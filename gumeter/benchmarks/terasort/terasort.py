import time
from typing import (
    Dict,
    List,
    Tuple
)

from lithops import FunctionExecutor, Storage
import pandas as pd
import numpy as np
import pickle
import json

from gumeter.backend.code_engine import get_docker_username_from_config
from gumeter.config import (
    BACKEND_MEMORY,
    DOCKER_BACKENDS,
    INPUT_BUCKET,
    RESULTS_DIR,
    RUNTIME_NAMES,
    TAGS
)
from gumeter.utils import (
    get_fname_w_replica_num,
    remove_objects
)


MIN_CHAR_ASCII = 32
MAX_CHAR_ASCII = 126
range_per_char = MAX_CHAR_ASCII - MIN_CHAR_ASCII
base = range_per_char + 1
FILE_NAME = "terasort-5g"
PARTITION_PREFIX = "intermediate_terasort/"
OUTPUT_PREFIX = "out_terasort/"
NUM_TASKS = 100


def get_read_range(
    data_size: int,
    partition_id: int,
    num_partitions: int
) -> Tuple[int, int]:

    total_registers = data_size / 100

    registers_per_worker = total_registers // num_partitions

    lower_bound = partition_id * registers_per_worker * 100

    if partition_id == (num_partitions - 1):
        upper_bound = data_size - 1
    else:
        upper_bound = lower_bound + registers_per_worker * 100 - 1

    return int(lower_bound), int(upper_bound)


def read_input(
    storage: Storage,
    bucket: str,
    key: str,
    lower_bound: int,
    upper_bound: int
) -> bytes:

    data = storage.get_object(
        bucket,
        key,
        extra_get_args={
            "Range": ''.join(
                ['bytes=', str(lower_bound), '-', str(upper_bound)]
            )
        }
    )

    return data


def parse_input(
    data: bytes
) -> pd.DataFrame:

    lines = data.split(b'\n')
    result = {}
    for line in lines:
        if len(line) >= 98:
            key = line[:10].decode('utf-8', errors='ignore')
            value = line[12:98].decode('utf-8', errors='ignore')
            result[key] = value
    df = pd.DataFrame(list(result.items()), columns=["0", "1"])
    result = df
    return result


def get_partition(line: str, num_partitions: int) -> int:

    numerical_value = 0
    max_numerical_value = 0
    for i in range(8):
        if i < len(line):
            normalized_char_val = ord(line[i]) - MIN_CHAR_ASCII
            numerical_value = numerical_value * base + normalized_char_val
        else:
            normalized_char_val = 0
            numerical_value = numerical_value * base + normalized_char_val

    for i in range(8):
        max_numerical_value = max_numerical_value * base + range_per_char

    if max_numerical_value == 0:
        return 0

    normalized_value = numerical_value / max_numerical_value
    partition = int(normalized_value * num_partitions)

    if partition >= num_partitions:
        partition = num_partitions - 1

    return partition


def partition_data(
    data: pd.DataFrame,
    num_partitions: int
) -> Dict[int, pd.DataFrame]:

    partitions = {i: None for i in range(num_partitions)}
    partition_indices = np.empty(len(data), dtype=np.int32)

    for idx, key in enumerate(data["0"]):
        partition_indices[idx] = get_partition(key, num_partitions)

    for i in range(num_partitions):
        indices = np.where(partition_indices == i)[0]
        if indices.size > 0:
            partitions[i] = data.iloc[indices].reset_index(drop=True)
        else:
            partitions[i] = pd.DataFrame(columns=data.columns)

    return partitions


def write_partitions(
    storage: Storage,
    bucket: str,
    partition_prefix: str,
    partitions: Dict[int, pd.DataFrame]
):
    for partition_id, df in partitions.items():
        pickle_bytes = pickle.dumps(df)

        # This is a placeholder for actual S3/MinIO read operation.
        partition_path = f"{partition_prefix}_part_{partition_id}.pkl"

        storage.put_object(
            bucket=bucket,
            key=partition_path,
            body=pickle_bytes
        )


def mapper(
    bucket: str,
    key: str,
    data_size: int,
    mapper_id: int,
    num_mappers: int,
    num_reducers: int,
    partition_prefix: str = "part_"
):
    storage = Storage()

    lower_bound, upper_bound = get_read_range(
        data_size=data_size,
        partition_id=mapper_id,
        num_partitions=num_mappers
    )

    chunk = read_input(
        storage=storage,
        bucket=bucket,
        key=key,
        lower_bound=lower_bound,
        upper_bound=upper_bound
    )

    parsed_data = parse_input(chunk)

    partitioned_data = partition_data(
        data=parsed_data,
        num_partitions=num_reducers
    )

    write_partitions(
        storage=storage,
        bucket=bucket,
        partition_prefix=f"{partition_prefix}_mapper_{mapper_id}",
        partitions=partitioned_data
    )


def read_partitions(
    storage: Storage,
    bucket: str,
    partition_prefix: str,
    num_mappers: int,
    reducer_id: int
) -> List[pd.DataFrame]:

    partition_list = []
    for mapper_id in range(num_mappers):
        key = f"{partition_prefix}_mapper_{mapper_id}_part_{reducer_id}.pkl"
        partition_data = storage.get_object(
            bucket=bucket,
            key=key
        )
        if partition_data:
            partition_df = pickle.loads(partition_data)
            partition_list.append(partition_df)
    return partition_list


def concat_partitions(
    partition_list: List[pd.DataFrame]
) -> pd.DataFrame:

    if not partition_list:
        return pd.DataFrame(columns=["0", "1"])

    return pd.concat(partition_list, ignore_index=True)


def sort_dataframe(
    df: pd.DataFrame
) -> pd.DataFrame:

    return df.sort_values(by=["0"]).reset_index(drop=True)


def write_output(
    storage: Storage,
    bucket: str,
    output_key: str,
    df: pd.DataFrame
):

    storage.put_object(
        bucket=bucket,
        key=output_key,
        body=pickle.dumps(df)
    )


def reducer(
    bucket: str,
    partition_prefix: str,
    num_mappers: int,
    reducer_id: int,
    out_prefix: str
):

    storage = Storage()

    partition_list = read_partitions(
        storage=storage,
        bucket=bucket,
        partition_prefix=partition_prefix,
        num_mappers=num_mappers,
        reducer_id=reducer_id
    )

    concatenated_data = concat_partitions(partition_list)

    sorted_data = sort_dataframe(concatenated_data)

    output_key = f"{out_prefix}_reducer_{reducer_id}.pkl"
    write_output(
        storage=storage,
        bucket=bucket,
        output_key=output_key,
        df=sorted_data
    )

    return output_key


def run_terasort(
    backend,
    storage,
    num_tasks: int = NUM_TASKS,
    outdir: str = RESULTS_DIR,
    log_level: str = "INFO"
):

    runtime = RUNTIME_NAMES.get(backend)
    tag = TAGS.get(backend)
    memory = BACKEND_MEMORY.get(backend)
    runtime = f"{runtime}:{tag}"
    if backend in DOCKER_BACKENDS:
        docker_username = get_docker_username_from_config()
        runtime = f"{docker_username}/{runtime}"
    bucket = INPUT_BUCKET.get(backend, "gumeter-data")

    fexec = FunctionExecutor(
        backend=backend,
        storage=storage,
        runtime_memory=memory,
        log_level=log_level,
        runtime=runtime
    )

    data_size = int(fexec.storage.head_object(
        bucket=bucket,
        key=FILE_NAME
    )['content-length'])

    mapper_args = [
        {
            "bucket": bucket,
            "key": FILE_NAME,
            "data_size": data_size,
            "mapper_id": mapper_id,
            "num_mappers": num_tasks,
            "num_reducers": num_tasks,
            "partition_prefix": PARTITION_PREFIX
        }
        for mapper_id in range(num_tasks // 2)
    ]
    reducer_args = [
        {
            "bucket": bucket,
            "partition_prefix": PARTITION_PREFIX,
            "num_mappers": num_tasks,
            "reducer_id": reducer_id,
            "out_prefix": OUTPUT_PREFIX
        }
        for reducer_id in range(num_tasks)
    ]

    results = {}
    results["start_time"] = time.time()

    mapper_futures = fexec.map(
        mapper,
        mapper_args
    )
    fexec.wait(mapper_futures)
    mapper_stats = [f.stats for f in mapper_futures if not f.error]
    results["stage0"] = mapper_stats
    results["stage0_time"] = time.time()

    print("Stage 0 completed, starting Stage 1...")

    reducer_futures = fexec.map(
        reducer,
        reducer_args
    )
    fexec.wait(reducer_futures)
    reducer_stats = [f.stats for f in reducer_futures if not f.error]
    results["stage1"] = reducer_stats

    results["end_time"] = time.time()

    fname = f"terasort_{backend}.json"
    fdir = f"{outdir}/{fname}"
    fdir = get_fname_w_replica_num(
        fname=fdir
    )
    json.dump(results, open(fdir, "w"))

    remove_objects(
        storage=fexec.storage,
        bucket=bucket,
        prefix=PARTITION_PREFIX
    )
    remove_objects(
        storage=fexec.storage,
        bucket=bucket,
        prefix=OUTPUT_PREFIX
    )
