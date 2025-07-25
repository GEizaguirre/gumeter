import os
import json

from gumeter.metrics import get_execution_time
import numpy as np


if __name__ == "__main__":

    benchmark = "terasort"
    num_replicas = 3
    backends = ["aws_lambda", "gcp_cloudrun", "aws_lambda_redis"]
    elasticity_metrics = {}

    for bch_i, backend in enumerate(backends):
        elasticity_metrics[backend] = []
        results_dir = "benchmark_results"
        matching_files = [
            f for f in os.listdir(results_dir)
            if f.startswith(f"{benchmark}_{backend}")
        ]
        for file_name in matching_files:
            num_replica = int(file_name.split("_")[-1].split(".")[0].split("a")[1])
            if num_replica < num_replicas:
                log_file = os.path.join(results_dir, file_name)
                if os.path.isfile(log_file):
                    backend_data = json.load(open(log_file, "r"))
                    exec_time = get_execution_time(backend_data)
                    elasticity_metrics[backend].append(exec_time)

    import matplotlib.pyplot as plt

    # Prepare data for plotting
    backend_colors = ["#F4BF2C", "#D44A4A", "#61E4B4"]  # Pastel blue, pastel pink, pastel green
    backend_str = ["AWS Lambda\n(S3)", "GCP Cloud Run\n(Cloud Storage)", "AWS Lambda\n(Redis)"]

    means = []
    stds = []

    for backend in backends:
        values = elasticity_metrics.get(backend, [])
        means.append(np.mean(values) if values else 0)
        stds.append(np.std(values) if values else 0)

    means = np.array(means)
    stds = np.array(stds)

    fig, ax = plt.subplots(figsize=(8, 4))
    x = np.arange(len(backends))
    bars = ax.bar(
        x,
        means,
        yerr=stds,
        color=backend_colors,
        capsize=8,
        alpha=0.85,
        edgecolor='black'
    )

    ax.set_xticks(x)
    ax.set_yticks([0.0, 20.0, 40.0, 60.0, 80.0])
    ax.set_xticklabels(backend_str, fontsize=17)
    ax.set_yticklabels(ax.get_yticks(), fontsize=17)
    ax.set_ylabel("Execution Time (s)", fontsize=19)
    ax.grid(axis='y', linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig("plots/exchange_comparison/execution_time_bars.pdf")
