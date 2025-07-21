import os

import pandas as pd
import numpy as np
import pylab


def create_total_gflops_plot(
    benchmark_data,
    dst,
    show_legened=False,
    show_flops_rate=False
):
    tzero = benchmark_data['start_time']
    data_df = pd.DataFrame(benchmark_data['worker_stats'])
    data_df['est_flops'] = (
        benchmark_data['est_flops'] /
        benchmark_data['workers']
    )

    max_time = np.max(data_df.worker_end_tstamp) - tzero
    runtime_bins = np.linspace(
        0, int(max_time),
        int(max_time),
        endpoint=False
    )
    runtime_flops_hist = np.zeros((len(data_df), len(runtime_bins)))

    for i in range(len(data_df)):
        row = data_df.iloc[i]
        s = row.worker_func_start_tstamp - tzero
        e = row.worker_func_end_tstamp - tzero
        a, b = np.searchsorted(runtime_bins, [s, e])
        if b-a > 0:
            runtime_flops_hist[i, a:b] = row.est_flops / float(b-a)

    results_by_endtime = data_df.sort_values('worker_end_tstamp')
    results_by_endtime['job_endtime_zeroed'] = (
        data_df.worker_end_tstamp - tzero
    )
    results_by_endtime['flops_done'] = results_by_endtime.est_flops.cumsum()
    results_by_endtime['rolling_flops_rate'] = (
        results_by_endtime.flops_done /
        results_by_endtime.job_endtime_zeroed
    )

    fig = pylab.figure(figsize=(5, 2.5))
    ax = fig.add_subplot(1, 1, 1)

    ax.plot(
        runtime_flops_hist.sum(axis=0)/1e9,
        label='Peak',
        linewidth=3,
        color="#776bcd"  # pastel dark blue
    )
    ax.plot(
        results_by_endtime.job_endtime_zeroed,
        results_by_endtime.rolling_flops_rate/1e9,
        label='Effective',
        linewidth=3,
        color="#FCA714"  # pastel dark green
    )
    ax.set_xlabel('Execution Time (s)', fontsize=18)
    if show_flops_rate:
        ax.set_ylabel("GFLOPS", fontsize=18)
    else:
        ax.set_ylabel(None)

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

    ax.set_xticklabels(xticks, fontsize=16)
    ax.set_xticks(xticks)
    ax.set_xlim(0)
    ax.set_ylim(0)
    ax.set_yticklabels([f"{int(y)}" for y in ax.get_yticks()], fontsize=16)

    if show_legened:
        pylab.legend(loc='upper left', fontsize=16, handlelength=0.6)
    ax.grid(True)

    dst = os.path.expanduser(dst) if '~' in dst else dst

    fig.tight_layout()
    fig.savefig(dst)
