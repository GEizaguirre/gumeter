import argparse
from tensei.benchmarks.benchmarks import run_benchmark, run_all_benchmarks
from tensei.plotting.plotting import generate_plots


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
        choices=["aws_lambda", "azure_functions", "google_cloud_functions"],
        help="Backend to use for the benchmark.",
    )

    # --- Run all benchmarks ---
    run_all_parser = subparsers.add_parser(
        "run-all", help="Run all available benchmarks."
    )
    run_all_parser.add_argument(
        "--backend",
        type=str,
        default="aws_lambda",
        choices=["aws_lambda", "azure_functions", "google_cloud_functions"],
        help="Backend to use for the benchmark."
    )

    # --- Get plots ---
    plot_parser = subparsers.add_parser(
        "plot", help="Generate plots from benchmark results."
    )
    plot_parser.add_argument(
        "--results-dir",
        type=str,
        default="benchmark_results",
        help="Path to the directory containing benchmark results.",
    )
    plot_parser.add_argument(
        "--output-dir",
        type=str,
        default="plots",
        help="Directory to save the generated plots.",
    )

    args = parser.parse_args()

    if args.command == "run":
        results = run_benchmark(args.benchmark_name, args.backend)
        print("Benchmark results:", results)
        # You might want to save these results to a file
    elif args.command == "run-all":
        all_results = run_all_benchmarks(args.backend)
        print("All benchmark results:", all_results)
        # Save all results to a file for plotting later
    elif args.command == "plot":
        print(f"Generating plots from '{args.results_file}'...")
        generate_plots(args.results_file, args.output_dir)
        print(f"Plots saved to '{args.output_dir}'")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
