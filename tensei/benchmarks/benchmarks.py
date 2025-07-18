from tensei.benchmarks.flops.flops import run_flops
from tensei.config import BACKEND_STORAGE, RESULTS_DIR
import os


def run_benchmark(
    benchmark_name: str,
    backend: str,
    out_dir: str = RESULTS_DIR
):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    storage = BACKEND_STORAGE[backend]
    if benchmark_name == "flops":
        run_flops(
            backend=backend,
            storage=storage,
            outdir=out_dir
        )


def run_all_benchmarks(
    backend: str,
    out_dir: str = RESULTS_DIR
):
    run_benchmark(
        "flops",
        backend,
        out_dir
    )
