import os

import pandas as pd
import numpy as np
import pylab
import json
from gumeter.config import BENCHMARK_BACKENDS
import matplotlib.pyplot as plt


def create_total_gflops_plot(dst):

    all_benchmark_data = {}
    replica_num = 3
    results_dir = "benchmark_results"
    for b_i, backend in enumerate(BENCHMARK_BACKENDS):
        backend_name = backend.value
        if backend_name != "aws_batch":
            print(backend_name)
            log_file = os.path.join(
                results_dir, f"flops_{backend_name}_replica{replica_num}.json"
            )
            all_benchmark_data[backend_name] = json.load(open(log_file, "r"))

    fig = pylab.figure(figsize=(4.4, 1.7))
    ax = fig.add_subplot(1, 1, 1)

    colors = ["#FF8C42", "#C44B4B", "#1976D2"]  # Darker pastel orange, green, blue

    for b_i, backend in enumerate(BENCHMARK_BACKENDS):
        backend_name = backend.value
        benchmark_data = all_benchmark_data[backend_name]
        tzero = benchmark_data["start_time"]
        data_df = pd.DataFrame(benchmark_data["worker_stats"])
        data_df["est_flops"] = benchmark_data["est_flops"] / benchmark_data["workers"]

        max_time = np.max(data_df.worker_end_tstamp) - tzero
        runtime_bins = np.linspace(0, int(max_time), int(max_time), endpoint=False)
        runtime_flops_hist = np.zeros((len(data_df), len(runtime_bins)))

        for i in range(len(data_df)):
            row = data_df.iloc[i]
            s = row.worker_func_start_tstamp - tzero
            e = row.worker_func_end_tstamp - tzero
            a, b = np.searchsorted(runtime_bins, [s, e])
            if b - a > 0:
                runtime_flops_hist[i, a:b] = row.est_flops / float(b - a)

        results_by_endtime = data_df.sort_values("worker_end_tstamp")
        results_by_endtime["job_endtime_zeroed"] = data_df.worker_end_tstamp - tzero
        results_by_endtime["flops_done"] = results_by_endtime.est_flops.cumsum()
        results_by_endtime["rolling_flops_rate"] = (
            results_by_endtime.flops_done / results_by_endtime.job_endtime_zeroed
        )

        ax.plot(
            runtime_flops_hist.sum(axis=0) / 1e9,
            label="Peak",
            linewidth=2,
            linestyle="dotted",
            color=colors[b_i % len(colors)],
            zorder=b_i,
        )
        ax.fill_between(
            results_by_endtime.job_endtime_zeroed,
            results_by_endtime.rolling_flops_rate / 1e9,
            alpha=0.8,
            color=colors[b_i % len(colors)],
            label="Effective",
            zorder=b_i + 1,
            hatch="////",
            facecolor=colors[b_i % len(colors)],
        )

    ax.set_xlabel("Execution Time (s)", fontsize=10)
    ax.set_ylabel(None)

    max_time = 50

    max_x = int(np.ceil(max_time))
    print(f"Max time: {max_x} seconds")
    if max_x <= 10:
        step = 2
    elif max_x <= 25:
        step = 5
    else:
        step = 10
    xticks = np.arange(0, max_x, step)
    if len(xticks) > 5:
        xticks = np.linspace(0, max_x, 5, dtype=int)
    elif len(xticks) < 5:
        xticks = np.append(xticks, max(xticks) + step)

    ax.set_xticklabels(xticks, fontsize=10)
    ax.set_xticks(xticks)
    ax.set_xlim(0)
    ax.set_ylim(0)
    ax.set_yticklabels([f"{int(y)}" for y in ax.get_yticks()], fontsize=10)

    ax.grid(True)

    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch

    legend1 = ax.legend(
        handles=[
            Line2D([0], [0], linestyle="dotted", color="black", label="Peak"),
            Patch(facecolor="gray", alpha=0.3, label="Effective", hatch="////"),
        ],
        title="Type",
        bbox_to_anchor=(0.26, 1),
        fontsize=9,
    )

    legend2 = ax.legend(
        handles=[
            Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                label="AWS Lambda",
                markerfacecolor=colors[0],
                markersize=8,
            ),
            Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                label="Google Cloud Run",
                markerfacecolor=colors[1],
                markersize=8,
            ),
            Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                label="IBM Code Engine",
                markerfacecolor=colors[2],
                markersize=8,
            ),
        ],
        loc="upper right",
        title="Provider",
        fontsize=9,
    )

    ax.add_artist(legend1)

    dst = os.path.expanduser(dst) if "~" in dst else dst

    plt.subplots_adjust(left=0.15, right=0.99, top=0.99, bottom=0.24)
    fig.savefig(dst)
