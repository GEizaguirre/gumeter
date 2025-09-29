import json
import os

from gumeter.config import BENCHMARK_BACKENDS
from gumeter.plot.flops import create_total_gflops_plot

if __name__ == "__main__":

    create_total_gflops_plot(f"plots/paper/flops_one.pdf")
