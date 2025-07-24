import json
import os

from gumeter.config import BENCHMARK_BACKENDS
from gumeter.plot.flops import create_total_gflops_plot

if __name__ == "__main__":

    replica_num = 3
    results_dir = "benchmark_results"

    for b_i, backend in enumerate(BENCHMARK_BACKENDS):
        backend_name = backend.value
        if backend_name != "aws_batch":
            print(backend_name)
            log_file = os.path.join(
                results_dir,
                f"flops_{backend_name}_replica{replica_num}.json"
            )
            benchmark_data = json.load(open(log_file, 'r'))

            create_total_gflops_plot(
                benchmark_data,
                f"plots/paper/flops_{backend_name}.pdf",
                show_legened=(b_i == 0),
                show_flops_rate=(b_i == 0)
            )
