import json
import os

from gumeter.config import BACKEND_STRING, BENCHMARK_BACKENDS
from gumeter.plot.timeline import plot_worker_activity
from gumeter.metrics import measure_elasticity

if __name__ == "__main__":

    replica_num = 3
    results_dir = "benchmark_results"

    benchmarks = ["montecarlo_stock", "montecarlo_pi", "terasort", "mandelbrot"]

    elasticity_metrics = {}
    for bch_i, benchmark in enumerate(benchmarks):
        backend_dict = {}
        elasticity_metrics[benchmark] = {}
        for b_i, backend in enumerate(BENCHMARK_BACKENDS):
            backend_name = backend.value
            if backend_name != "aws_batch":
                log_file = os.path.join(
                    results_dir, f"{benchmark}_{backend_name}_replica{replica_num}.json"
                )
                benchmark_data = json.load(open(log_file, "r"))
                backend_str = BACKEND_STRING[backend_name]
                backend_dict[backend_str] = benchmark_data

                elasticity_metrics[benchmark][backend_name] = []
                results_dir = "benchmark_results"
                matching_files = [
                    f
                    for f in os.listdir(results_dir)
                    if f.startswith(f"{benchmark}_{backend_name}")
                ]
                for file_name in matching_files:
                    log_file = os.path.join(results_dir, file_name)
                    if os.path.isfile(log_file):
                        backend_data = json.load(open(log_file, "r"))
                        elasticity = measure_elasticity(backend_data)
                        elasticity_metrics[benchmark][backend_name].append(elasticity)

        dst = f"plots/paper/worker_activity_{benchmark}.pdf"
        plot_worker_activity(
            backend_dict, dst, elasticity_metrics[benchmark], show_legend=False
        )
