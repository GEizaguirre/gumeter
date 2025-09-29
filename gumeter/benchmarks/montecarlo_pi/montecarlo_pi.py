import os
import time
import json
from random import random

from lithops import (
    FunctionExecutor,
    Storage
)
import cloudpickle as pickle

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


MAP_INSTANCES = 100
PARTITION_PREFIX = "intermediate_montecarlo_pi/"


class EstimatePI:
    randomize_per_map = 10000000

    def __init__(
        self,
        bucket: str
    ):
        self.total_randomize_points = MAP_INSTANCES * self.randomize_per_map
        self.bucket = bucket

    def __str__(self):
        return "Total Randomize Points: {:,}".format(
            self.randomize_per_map * MAP_INSTANCES
        )

    @staticmethod
    def predicate():
        x = random()
        y = random()
        return (x ** 2) + (y ** 2) <= 1

    def randomize_points(
        self,
        func_i: int
    ):
        storage = Storage()
        in_circle = 0
        for _ in range(self.randomize_per_map):
            in_circle += self.predicate()
        key = os.path.join(
            PARTITION_PREFIX,
            str(func_i)
        )
        result = float(in_circle / self.randomize_per_map)
        storage.put_object(
            bucket=self.bucket,
            key=key,
            body=pickle.dumps(result)
        )
        return key

    def process_in_circle_points(
        self,
        result_keys: list[str]
    ):
        storage = Storage()

        results = [
            pickle.loads(
                storage.get_object(
                    bucket=self.bucket,
                    key=result_key
                )
            ) for result_key in result_keys
        ]

        in_circle_percent = 0
        for map_result in results:
            in_circle_percent += map_result
        estimate_PI = float(4 * (in_circle_percent / MAP_INSTANCES))
        return estimate_PI


def parallel_montecarlo_pi(
    executor: FunctionExecutor,
    pi_estimator: EstimatePI
):

    results = {}
    results["start_time"] = time.time()

    # execute the code
    map_futures = executor.map(
        pi_estimator.randomize_points,
        list(range(MAP_INSTANCES))
    )
    map_results = executor.get_result(map_futures)
    map_stats = [f.stats for f in map_futures if not f.error]
    results["stage0"] = map_stats
    results["stage0_time"] = time.time()

    reduce_futures = executor.map(
        pi_estimator.process_in_circle_points,
        [map_results]
    )
    pi = executor.get_result(reduce_futures)[0]
    print(f"Estimated PI: {pi}")
    reduce_stats = [f.stats for f in reduce_futures if not f.error]
    results["stage1"] = reduce_stats

    results["end_time"] = time.time()

    return results


def run_montecarlo_pi(
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
    bucket = INPUT_BUCKET.get(backend)

    fexec = FunctionExecutor(
        backend=backend,
        storage=storage,
        runtime_memory=memory,
        log_level=log_level,
        runtime=runtime
    )

    pi_estimator = EstimatePI(bucket)
    results = parallel_montecarlo_pi(
        fexec,
        pi_estimator
    )

    fname = f"montecarlo_pi_{backend}.json"
    fdir = f"{outdir}/{fname}"
    fdir = get_fname_w_replica_num(
        fname=fdir
    )
    json.dump(
        results,
        open(fdir, "w")
    )
    print(f"Results saved to {fdir}")

    remove_objects(
        storage=fexec.storage,
        bucket=bucket,
        prefix=PARTITION_PREFIX
    )
