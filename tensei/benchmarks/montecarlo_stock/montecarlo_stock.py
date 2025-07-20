import os
import time
import json

from lithops import (
    FunctionExecutor,
    Storage
)
import cloudpickle as pickle
import numpy as np
import scipy.stats as scpy

from tensei.backend.code_engine import get_docker_username_from_config
from tensei.config import (
    BACKEND_MEMORY,
    DOCKER_BACKENDS,
    INPUT_BUCKET,
    RESULTS_DIR,
    RUNTIME_NAMES,
    TAGS
)
from tensei.utils import (
    get_fname_w_replica_num,
    remove_objects
)


MAP_INSTANCES = 10
PARTITION_PREFIX = "intermediate_montecarlo_stock/"


class StockData:
    forecasts_per_map = 100
    days2predict = 730

    def __init__(self, title, drift, std_dev, last_value):
        self.title = title
        self.last_value = last_value
        self.std_dev = std_dev
        self.drift = drift

    def single_forecast_generator(self):
        predicts_est = [self.last_value]
        for predict in range(1, self.days2predict + 1):
            rand = np.random.rand()
            pow_r = scpy.norm.ppf(rand)
            predicts_est.append(predicts_est[predict - 1] * np.exp(self.drift + (self.std_dev * pow_r)))
        return predicts_est


def parallel_montecarlo_stock(
    executor: FunctionExecutor,
    current_stock: StockData,
    bucket: str
):

    def process_forecasts(
        func_i: int
    ):
        storage = Storage()
        end = current_stock.days2predict
        mid = int(end / 2)
        hist_end = list()
        hist_mid = list()
        for i in range(StockData.forecasts_per_map):
            frc = current_stock.single_forecast_generator()
            hist_end.append(frc[end])
            hist_mid.append(frc[mid])
        result = (hist_mid, hist_end)
        key = os.path.join(
            PARTITION_PREFIX,
            str(func_i)
        )
        storage.put_object(
            bucket=bucket,
            key=key,
            body=pickle.dumps(result)
        )
        return key

    def combine_forecasts(
        result_keys: list[str]
    ):
        storage = Storage()
        results = [
            pickle.loads(
                storage.get_object(
                    bucket=bucket,
                    key=key
                )
            )
            for key in result_keys
        ]
        hist_end = list()
        hist_mid = list()
        for single_map_result in results:
            hist_end.extend(single_map_result[1])
            hist_mid.extend(single_map_result[0])
        return (hist_mid, hist_end)

    results = {}
    results["start_time"] = time.time()

    # execute the code
    map_futures = executor.map(
        process_forecasts,
        list(range(MAP_INSTANCES))
    )
    map_results = executor.get_result(map_futures)
    map_stats = [f.stats for f in map_futures if not f.error]
    results["stage0"] = map_stats
    results["stage0_time"] = time.time()

    reduce_futures = executor.map(
        combine_forecasts,
        [map_results]
    )
    forecast_result = executor.get_result(reduce_futures)[0]
    reduce_stats = [f.stats for f in reduce_futures if not f.error]
    results["stage1"] = reduce_stats

    results["end_time"] = time.time()

    return results


def run_montecarlo_stock(
    backend,
    storage,
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
    bucket = INPUT_BUCKET.get(backend, "tensei-data")

    fexec = FunctionExecutor(
        backend=backend,
        storage=storage,
        runtime_memory=memory,
        log_level=log_level,
        runtime=runtime
    )

    stock_data = StockData(
        title="Example 2014, 2015, 2016",
        drift=-0.00022513546014255100,
        std_dev=0.0121678341323272,
        last_value=159.44
    )
    results = parallel_montecarlo_stock(
        executor=fexec,
        current_stock=stock_data,
        bucket=bucket
    )

    fname = f"montecarlo_stock_{backend}.json"
    fdir = f"{outdir}/{fname}"
    fdir = get_fname_w_replica_num(
        fname=fdir
    )
    json.dump(
        results,
        open(fdir, "w")
    )

    remove_objects(
        storage=fexec.storage,
        bucket=bucket,
        prefix=PARTITION_PREFIX
    )
