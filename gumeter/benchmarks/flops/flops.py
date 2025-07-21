#
# Copyright Cloudlab URV 2020
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import time
import json
import numpy as np

from lithops import FunctionExecutor

from gumeter.config import (
    DOCKER_BACKENDS,
    BACKEND_MEMORY,
    MAX_TASKS,
    RESULTS_DIR,
    RUNTIME_NAMES,
    TAGS
)
from gumeter.backend.code_engine import get_docker_username_from_config
from gumeter.utils import get_fname_w_replica_num


def compute_flops(
    loopcount,
    mat_n
):

    A = np.arange(mat_n**2, dtype=np.float64).reshape(mat_n, mat_n)
    B = np.arange(mat_n**2, dtype=np.float64).reshape(mat_n, mat_n)

    start = time.time()
    for i in range(loopcount):
        _ = np.sum(np.dot(A, B))

    FLOPS = 2 * mat_n**3 * loopcount

    end = time.time()

    return {'flops': FLOPS / (end-start)}


def benchmark(
    backend: str,
    storage: str,
    workers: int = MAX_TASKS,
    loopcount: int = 10,
    matn: int = 1024,
    debug: bool = False
):
    iterable = [(loopcount, matn) for i in range(workers)]
    log_level = 'INFO' if not debug else 'DEBUG'
    runtime = RUNTIME_NAMES.get(backend)
    tag = TAGS.get(backend)
    memory = BACKEND_MEMORY.get(backend)
    runtime = f"{runtime}:{tag}"
    if backend in DOCKER_BACKENDS:
        docker_username = get_docker_username_from_config()
        runtime = f"{docker_username}/{runtime}"
    fexec = FunctionExecutor(
        backend=backend,
        storage=storage,
        runtime_memory=memory,
        log_level=log_level,
        runtime=runtime
    )
    start_time = time.time()
    worker_futures = fexec.map(
        compute_flops,
        iterable
    )
    results = fexec.get_result(throw_except=False)
    end_time = time.time()
    results = [flops for flops in results if flops is not None]
    worker_stats = [f.stats for f in worker_futures if not f.error]
    total_time = end_time-start_time

    print("Total time:", round(total_time, 3))
    toal_executed_tasks = len(worker_stats)
    est_flops = toal_executed_tasks * 2 * loopcount * matn ** 3
    print('Estimated GFLOPS:', round(est_flops / 1e9 / total_time, 4))

    res = {
        'start_time': start_time,
        'total_time': total_time,
        'est_flops': est_flops,
        'worker_stats': worker_stats,
        'results': results,
        'workers': toal_executed_tasks,
        'loopcount': loopcount,
        'MATN': matn
    }

    return res


def run_flops(
    backend,
    storage,
    tasks: int = MAX_TASKS,
    outdir: str = RESULTS_DIR,
):
    pass

    res = benchmark(
        backend,
        storage,
        tasks
    )
    fname = f"flops_{backend}.json"
    fdir = f"{outdir}/{fname}"
    fdir = get_fname_w_replica_num(
        fname=fdir
    )
    json.dump(
        res,
        open(fdir, "w")
    )
    print(f"Results saved to {fdir}")



if __name__ == "__main__":
    run_flops()
