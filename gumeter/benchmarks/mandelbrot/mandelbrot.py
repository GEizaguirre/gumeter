from math import sqrt
import time
import json

import numpy as np
from lithops import FunctionExecutor

from gumeter.backend.code_engine import get_docker_username_from_config
from gumeter.config import (
    BACKEND_MEMORY,
    DOCKER_BACKENDS,
    RESULTS_DIR,
    RUNTIME_NAMES,
    TAGS
)
from gumeter.utils import get_fname_w_replica_num


WIDTH = HEIGHT = 768
MAXITER = 300
XTARGET = -0.7436438870
YTARGET = 0.1318259042


def parallel_mandelbrot(
    backend,
    storage,
    runtime_memory,
    log_level,
    runtime,
    xmin,
    xmax,
    ymin,
    ymax,
    width,
    height,
    maxiter,
    concurrency
):

    blocks_per_row = sqrt(concurrency)
    assert blocks_per_row == int(blocks_per_row), "concurrency must be square"
    blocks_per_row = int(blocks_per_row)
    y_step = (ymax - ymin) / blocks_per_row
    x_step = (xmax - xmin) / blocks_per_row
    mat_block_sz = int(width / blocks_per_row)

    limits = []
    indexes = []
    for i in range(blocks_per_row):
        for j in range(blocks_per_row):
            limits.append((
                xmin + i*x_step, xmin + (i + 1)*x_step,
                ymin + j*y_step, ymin + (j + 1)*y_step
            ))
            indexes.append((i*mat_block_sz, (i + 1)*mat_block_sz,
                            j*mat_block_sz, (j + 1)*mat_block_sz))

    def mandelbrot_chunk_fn(limit, maxiter):
        rx = np.linspace(limit[0], limit[1], mat_block_sz)
        ry = np.linspace(limit[2], limit[3], mat_block_sz)
        c = rx + ry[:, None]*1j
        output = np.zeros((mat_block_sz, mat_block_sz))
        z = np.zeros((mat_block_sz, mat_block_sz), np.complex64)

        for it in range(maxiter+1):
            notdone = np.less(z.real*z.real + z.imag*z.imag, 4.0)
            output[notdone] = it
            z[notdone] = z[notdone]**2 + c[notdone]

        return output.T

    iterdata = [
        {
            "limit": limit,
            "maxiter": maxiter
        } for limit in limits
    ]

    executor = FunctionExecutor(
        backend=backend,
        storage=storage,
        runtime_memory=runtime_memory,
        log_level=log_level,
        runtime=runtime
    )
    futures = executor.map(
        mandelbrot_chunk_fn,
        iterdata
    )
    results = executor.get_result(futures)
    worker_stats = [f.stats for f in futures if not f.error]

    mat = np.zeros((width, height))
    for i, mat_chunk in enumerate(results):
        idx = indexes[i]
        mat[idx[0]:idx[1], idx[2]:idx[3]] = mat_chunk

    return worker_stats


def run_mandelbrot(
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

    results = {}
    results["start_time"] = time.time()

    # Initial rectangle position
    delta = 1
    xmin = XTARGET - delta
    xmax = XTARGET + delta
    ymin = YTARGET - delta
    ymax = YTARGET + delta
    maxiter = MAXITER
    concurrency = 3**2
    worker_stats = parallel_mandelbrot(
        backend,
        storage,
        memory,
        log_level,
        runtime,
        xmin,
        xmax,
        ymin,
        ymax,
        WIDTH,
        HEIGHT,
        maxiter,
        concurrency
    )
    results["stage0"] = worker_stats
    results["stage0_time"] = time.time()

    # 1st zoom
    delta = 0.4
    xmin = XTARGET - delta
    xmax = XTARGET + delta
    ymin = YTARGET - delta
    ymax = YTARGET + delta
    concurrency = 5**2
    worker_stats = parallel_mandelbrot(
        backend,
        storage,
        memory,
        log_level,
        runtime,
        xmin,
        xmax,
        ymin,
        ymax,
        WIDTH,
        HEIGHT,
        maxiter,
        concurrency
    )
    results["stage1"] = worker_stats
    results["stage1_time"] = time.time()

    # 2nd zoom
    delta *= 0.4
    xmin = XTARGET - delta
    xmax = XTARGET + delta
    ymin = YTARGET - delta
    ymax = YTARGET + delta
    maxiter += 30
    concurrency = 7**2
    worker_stats = parallel_mandelbrot(
        backend,
        storage,
        memory,
        log_level,
        runtime,
        xmin,
        xmax,
        ymin,
        ymax,
        WIDTH,
        HEIGHT,
        maxiter,
        concurrency
    )
    results["stage2"] = worker_stats
    results["stage2_time"] = time.time()

    # 3rd zoom
    delta *= 0.4
    xmin = XTARGET - delta
    xmax = XTARGET + delta
    ymin = YTARGET - delta
    ymax = YTARGET + delta
    maxiter += 30
    concurrency = 9**2
    worker_stats = parallel_mandelbrot(
        backend,
        storage,
        memory,
        log_level,
        runtime,
        xmin,
        xmax,
        ymin,
        ymax,
        WIDTH,
        HEIGHT,
        maxiter,
        concurrency
    )
    results["stage3"] = worker_stats
    results["stage3_time"] = time.time()

    # 4th zoom
    delta *= 0.4
    xmin = XTARGET - delta
    xmax = XTARGET + delta
    ymin = YTARGET - delta
    ymax = YTARGET + delta
    maxiter += 40
    concurrency = 10**2
    worker_stats = parallel_mandelbrot(
        backend,
        storage,
        memory,
        log_level,
        runtime,
        xmin,
        xmax,
        ymin,
        ymax,
        WIDTH,
        HEIGHT,
        maxiter,
        concurrency
    )
    results["stage4"] = worker_stats
    results["stage4_time"] = time.time()

    # 5th zoom
    delta *= 0.4
    xmin = XTARGET - delta
    xmax = XTARGET + delta
    ymin = YTARGET - delta
    ymax = YTARGET + delta
    maxiter += 40
    concurrency = 12**2
    worker_stats = parallel_mandelbrot(
        backend,
        storage,
        memory,
        log_level,
        runtime,
        xmin,
        xmax,
        ymin,
        ymax,
        WIDTH,
        HEIGHT,
        maxiter,
        concurrency
    )
    results["stage5"] = worker_stats
    results["stage5_time"] = time.time()

    # 6th zoom
    delta *= 0.4
    xmin = XTARGET - delta
    xmax = XTARGET + delta
    ymin = YTARGET - delta
    ymax = YTARGET + delta
    maxiter = 500
    concurrency = 14**2
    worker_stats = parallel_mandelbrot(
        backend,
        storage,
        memory,
        log_level,
        runtime,
        xmin,
        xmax,
        ymin,
        ymax,
        WIDTH,
        HEIGHT,
        maxiter,
        concurrency
    )
    results["stage6"] = worker_stats
    results["stage6_time"] = time.time()

    results["end_time"] = time.time()

    fname = f"mandelbrot_{backend}.json"
    fdir = f"{outdir}/{fname}"
    fdir = get_fname_w_replica_num(
        fname=fdir
    )
    json.dump(
        results,
        open(fdir, "w")
    )
