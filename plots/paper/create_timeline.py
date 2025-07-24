import json
import os

from gumeter.config import (
    BACKEND_STRING,
    BENCHMARK_BACKENDS
)
from gumeter.plot.timeline import plot_worker_activity

if __name__ == "__main__":

    replica_num = 3
    results_dir = "benchmark_results"

    benchmarks = [
        "montecarlo_stock",
        "montecarlo_pi",
        "terasort",
        "mandelbrot"
    ]

    for bch_i, benchmark in enumerate(benchmarks):
        backend_dict = {}
        for b_i, backend in enumerate(BENCHMARK_BACKENDS):
            backend_name = backend.value
            if backend_name != "aws_batch":
                print(backend_name)
                log_file = os.path.join(
                    results_dir,
                    f"{benchmark}_{backend_name}_replica{replica_num}.json"
                )
                benchmark_data = json.load(open(log_file, 'r'))
                backend_str = BACKEND_STRING[backend_name]
                backend_dict[backend_str] = benchmark_data

        dst = f"plots/paper/worker_activity_{benchmark}.pdf"
        plot_worker_activity(
            backend_dict,
            dst,
            show_legend=(bch_i == 0)
        )

                
