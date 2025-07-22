import os
import json

from gumeter.config import DISTRIBUTED_BACKENDS
from gumeter.metrics import get_cost, get_execution_time
import numpy as np


if __name__ == "__main__":

    benchmarks = [ "montecarlo_stock", "montecarlo_pi", "terasort", "mandelbrot" ]
    elasticity_metrics = {}

    for bch_i, benchmark in enumerate(benchmarks):
        elasticity_metrics[benchmark] = {}
        for b_i, backend in enumerate(DISTRIBUTED_BACKENDS):
            backend_name = backend.value
            if backend_name != "aws_batch":
                elasticity_metrics[benchmark][backend_name] = []
                results_dir = "benchmark_results"
                matching_files = [
                    f for f in os.listdir(results_dir)
                    if f.startswith(f"{benchmark}_{backend_name}")
                ]
                for file_name in matching_files:
                    log_file = os.path.join(results_dir, file_name)
                    if os.path.isfile(log_file):
                        backend_data = json.load(open(log_file, "r"))
                        elasticity = 1 / ( 
                            get_cost(backend_data, backend_name) * get_execution_time(backend_data)
                        )
                        elasticity_metrics[benchmark][backend_name].append(elasticity)

    import matplotlib.pyplot as plt

    # Prepare data for plotting
    backend_colors = ['#FF8C42', "#C44B4B", '#1976D2']  # Darker pastel orange, green, blue

    benchmarks_list = benchmarks
    backends_list = [backend.value for backend in DISTRIBUTED_BACKENDS if backend.value != "aws_batch"]

    means = []
    stds = []

    for benchmark in benchmarks_list:
        means_row = []
        stds_row = []
        for backend in backends_list:
            values = elasticity_metrics[benchmark].get(backend, [])
            if values:
                means_row.append(np.mean(values))
                stds_row.append(np.std(values))
            else:
                means_row.append(0)
                stds_row.append(0)
        means.append(means_row)
        stds.append(stds_row)

    means = np.array(means)
    stds = np.array(stds)

    x = np.arange(len(benchmarks_list))
    width = 0.15

    fig, ax = plt.subplots(figsize=(10, 4))

    backend_names = ["AWS Lambda", "GCP Cloud Run", "IBM Code Engine"]
    for i, backend in enumerate(backends_list):
        ax.bar(x + i * width, means[:, i], width, yerr=stds[:, i], label=backend_names[i], capsize=5, color=backend_colors[i])

    ax.set_ylabel('Cost Efficiency\n($1/\\$s$, mean ± std)', fontsize=17)
    ax.set_xticks(x + width * (len(backends_list) - 1) / 2)
    ax.set_xticklabels(["Monte Carlo Stock", "Monte Carlo Pi", "Terasort", "Mandelbrot"], fontsize=16)
    ax.set_yscale('log')
    ax.legend(fontsize=15)
    ax.tick_params(axis='y', labelsize=16)
    ax.set_axisbelow(True)
    ax.grid(True, axis='y', linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.savefig("cost_efficiency_bars.pdf")

