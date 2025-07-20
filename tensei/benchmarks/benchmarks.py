import os

from tensei.config import (
    BACKEND_STORAGE,
    RESULTS_DIR
)
from tensei.benchmarks.flops.flops import run_flops
from tensei.benchmarks.terasort.terasort import run_terasort


def run_benchmark(
    benchmark_name: str,
    backend: str,
    out_dir: str = RESULTS_DIR,
    num_replicas: int = 1
):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    storage = BACKEND_STORAGE[backend]
    for _ in range(num_replicas):
        print("Replica %d of benchmark '%s' on backend '%s'" % (
            _ + 1, benchmark_name, backend
        ))
        if benchmark_name == "flops":
            run_flops(
                backend=backend,
                storage=storage,
                outdir=out_dir
            )
        elif benchmark_name == "terasort":
            run_terasort(   
                backend=backend,
                storage=storage,
                outdir=out_dir
            )


def run_all_benchmarks(
    backend: str,
    out_dir: str = RESULTS_DIR,
    num_replicas: int = 1
):
    run_benchmark(
        "flops",
        backend,
        out_dir,
        num_replicas
    )
    run_benchmark(
        "terasort",
        backend,
        out_dir,
        num_replicas
    )
