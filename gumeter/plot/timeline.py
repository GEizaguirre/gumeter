import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
import numpy as np
from mpl_toolkits.axes_grid1.inset_locator import inset_axes


def plot_worker_activity(backend_data_dict, dst, elasticity_values, show_legend=False):
    all_end_times = []
    for backend_name, data in backend_data_dict.items():
        all_end_times.append(datetime.fromtimestamp(data["end_time"]))

    if not all_end_times:
        print("No backend data provided.")
        return

    max_overall_duration = 0
    for backend_name, data in backend_data_dict.items():
        start_time_dt = datetime.fromtimestamp(data["start_time"])
        end_time_dt = datetime.fromtimestamp(data["end_time"])
        duration = (end_time_dt - start_time_dt).total_seconds()
        if duration > max_overall_duration:
            max_overall_duration = duration

    fig, ax = plt.subplots(figsize=(4, 1.4))

    pastel_colors = [
        "#FF8C42",
        "#C44B4B",
        "#1976D2",
    ]  # Darker pastel orange, green, blue
    color_cycle = iter(pastel_colors)

    for backend_name, data in backend_data_dict.items():
        start_time_dt = datetime.fromtimestamp(data["start_time"])
        end_time_dt = datetime.fromtimestamp(data["end_time"])

        events = []
        for key, stage_workers in data.items():
            if key.startswith("stage") and isinstance(stage_workers, list):
                for worker_stat in stage_workers:
                    worker_start_dt = datetime.fromtimestamp(
                        worker_stat["worker_start_tstamp"]
                    )
                    worker_end_dt = datetime.fromtimestamp(
                        worker_stat["worker_end_tstamp"]
                    )
                    events.append(
                        ((worker_start_dt - start_time_dt).total_seconds(), 1)
                    )
                    events.append(((worker_end_dt - start_time_dt).total_seconds(), -1))

        events.sort(key=lambda x: x[0])

        time_points = [0]
        active_workers = [0]
        current_workers = 0

        for time, change in events:
            if not time_points or time_points[-1] < time:
                time_points.append(time)
                active_workers.append(current_workers)
            current_workers += change
            time_points.append(time)
            active_workers.append(current_workers)

        backend_duration = (end_time_dt - start_time_dt).total_seconds()
        if time_points[-1] < backend_duration:
            time_points.append(backend_duration)
            active_workers.append(active_workers[-1])
        elif time_points[-1] > backend_duration:
            idx_to_clip = next(
                (i for i, t in enumerate(time_points) if t > backend_duration),
                len(time_points),
            )
            time_points = time_points[:idx_to_clip]
            active_workers = active_workers[:idx_to_clip]
            time_points.append(backend_duration)
            active_workers.append(current_workers)

        plt.plot(
            time_points,
            active_workers,
            label=backend_name,
            linestyle="-",
            linewidth=2,
            color=next(color_cycle),
        )

    plt.xlim(0, max_overall_duration * 1.05)
    plt.ylim(bottom=0)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.grid(True, linestyle="--", alpha=0.7)
    if show_legend:
        plt.legend(loc="upper right", fontsize=10)

    means = []
    stds = []
    means_row = []
    stds_row = []
    for backend in elasticity_values.keys():
        values = elasticity_values.get(backend, [])
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

    ax_inset = inset_axes(ax, width="15%", height="60%", loc="upper right")

    ax_inset.set_axisbelow(True)
    ax_inset.set_xlim(-0.5, 2.5)
    ax_inset.set_ylim(0, 1.05)
    ax_inset.set_xticks([])
    ax_inset.set_yticks([0, 1])
    ax_inset.yaxis.grid(True, which="minor", linestyle=":", alpha=0.5)
    ax_inset.yaxis.set_minor_locator(plt.MultipleLocator(0.25))

    bars = ax_inset.bar(
        [0, 1, 2], means[0], yerr=stds[0], capsize=2, color=pastel_colors
    )

    plt.subplots_adjust(left=0.1, right=0.99, top=0.95, bottom=0.17)
    plt.savefig(dst)
    plt.close()
