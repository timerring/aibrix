"""
Benchmark command for AIBrix CLI.

Integrates with the existing aibrix_benchmark entry point.
"""

import argparse
import sys
import subprocess
import os
from aibrix.gpu_optimizer.optimizer.profiling.benchmark import main as benchmark_main


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """Add arguments to the benchmark command parser."""
    parser.add_argument(
        "-m", "--model",
        type=str,
        required=True,
        help="Model name to benchmark"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        required=True,
        help="Output directory for benchmark results"
    )
    parser.add_argument(
        "--additional-args",
        type=str,
        help="Additional arguments to pass to benchmark script"
    )


def handle(args: argparse.ArgumentParser) -> int:
    """Handle the benchmark command."""
    try:
        # Set up sys.argv to match what the original benchmark expects
        original_argv = sys.argv.copy()
        
        # Build new argv for the benchmark
        new_argv = ["aibrix_benchmark", "-m", args.model, "-o", args.output]
        
        # Add additional arguments if provided
        if args.additional_args:
            new_argv.extend(args.additional_args.split())
        
        # Replace sys.argv temporarily
        sys.argv = new_argv
        
        try:
            # Call the original benchmark main function
            return benchmark_main()
        finally:
            # Restore original argv
            sys.argv = original_argv
            
    except Exception as e:
        print(f"Error running benchmark: {e}")
        return 1 