import argparse

from tensei.benchmarks.benchmarks import (
    run_benchmark,
    run_all_benchmarks
)
from tensei.plotting.plotting import generate_plots
from tensei.config import (
    PLOTS_DIR,
    RESULTS_DIR,
    Backend
)
from tensei.runtime.runtime import deploy_runtime
from tensei.backend.set_config import set_config


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Tensei: A benchmarking suite for",
            "elastic serverless data analytics."
        )
    )

    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands"
    )

    # --- Run a single benchmark ---
    run_parser = subparsers.add_parser(
        "run", help="Run a specific benchmark."
    )
    run_parser.add_argument(
        "benchmark_name",
        type=str,
        help="Name of the benchmark to run (e.g., 'Mandelbrot')."
    )
    run_parser.add_argument(
        "--backend",
        type=str,
        default="aws_lambda",
        choices=[b.value for b in Backend],
        help="Backend to use for the benchmark.",
    )
    run_parser.add_argument(
        "--output-dir",
        type=str,
        default=RESULTS_DIR,
        help="Directory to save the generated plots.",
    )

    # --- Run all benchmarks ---
    run_all_parser = subparsers.add_parser(
        "run-all", help="Run all available benchmarks."
    )
    run_all_parser.add_argument(
        "--backend",
        type=str,
        default="aws_lambda",
        choices=[b.value for b in Backend],
        help="Backend to use for the benchmark.",
    )
    run_all_parser.add_argument(
        "--output-dir",
        type=str,
        default=RESULTS_DIR,
        help="Directory to save the generated plots.",
    )

    # --- Get plots ---
    plot_parser = subparsers.add_parser(
        "plot", help="Generate plots from benchmark results."
    )
    plot_parser.add_argument(
        "--results-dir",
        type=str,
        default=RESULTS_DIR,
        help="Path to the directory containing benchmark results.",
    )
    plot_parser.add_argument(
        "--output-dir",
        type=str,
        default=PLOTS_DIR,
        help="Directory to save the generated plots.",
    )
    plot_parser.add_argument(
        "--backend",
        type=str,
        default="AWS_LAMBDA",
        choices=[b.name for b in Backend],
        help="Backend to use for the benchmark.",
    )

    # --- Deploy a runtime ---
    deploy_parser = subparsers.add_parser(
        "deploy", help="Deploy a runtime for a specific backend."
    )
    deploy_parser.add_argument(
        "backend",
        type=str,
        choices=[b.value for b in Backend],
        help="Backend to deploy the runtime for.",
    )
    deploy_parser.add_argument(
        "--runtime-name",
        type=str,
        default=None,
        help="Optional name for the runtime.",
    )
    deploy_parser.add_argument(
        "--tag",
        type=str,
        default=None,
        help="Optional tag for the runtime.",
    )

    # --- Set backend config ---
    config_parser = subparsers.add_parser(
        "set-config", help="Set configuration for a backend."
    )
    config_parser.add_argument(
        "backend",
        type=str,
        choices=[b.value for b in Backend],
        help="Backend to configure.",
    )

    args = parser.parse_args()

    if args.command == "run":
        print(
            f"\033[95m\033[1mRunning benchmark '{args.benchmark_name}' "
            f"with backend '{args.backend}'...\033[0m"
        )
        run_benchmark(args.benchmark_name, args.backend)
        print(f"\033[1;32m\033[1mBenchmark finished\033[0m")
        # You might want to save these results to a file
    elif args.command == "run-all":
        print(
            "\033[95m\033[1mRunning all benchmarks with backend "
            f"'{args.backend}'...\033[0m"
        )
        all_results = run_all_benchmarks(args.backend)
        print(f"\033[1;32m\033[1mAll benchmark results: {all_results}\033[0m")
        # Save all results to a file for plotting later
    elif args.command == "plot":
        generate_plots(args.results_dir, args.output_dir)
        print(f"\033[1;32m\033[1mPlots saved to '{args.output_dir}'\033[0m")
    elif args.command == "deploy":
        deploy_runtime(
            backend=args.backend,
            runtime_name=args.runtime_name,
            tag=args.tag
        )
        print(
            f"\033[1;32m\033[1mRuntime for '{args.backend}' deployed.\033[0m"
        )
    elif args.command == "set-config":
        set_config(args.backend)
        print(
            f"\033[1;32m\033[1mConfiguration for '{args.backend}' set.\033[0m"
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
