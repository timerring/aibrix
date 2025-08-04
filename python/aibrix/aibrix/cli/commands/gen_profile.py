"""
Gen-profile command for AIBrix CLI.

Integrates with the existing aibrix_gen_profile entry point.
"""

import argparse
import sys
from aibrix.gpu_optimizer.optimizer.profiling.gen_profile import main as gen_profile_main


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """Add arguments to the gen-profile command parser."""
    parser.add_argument(
        "deployment",
        type=str,
        help="Target deployment name"
    )
    parser.add_argument(
        "--benchmark",
        type=str,
        help="Benchmark result file"
    )
    parser.add_argument(
        "--tput",
        type=float,
        default=0.0,
        help="Throughput SLO target as RPS"
    )
    parser.add_argument(
        "--tt",
        type=float,
        default=0.0,
        help="Token Throughput SLO target"
    )
    parser.add_argument(
        "--e2e",
        type=float,
        default=float('inf'),
        help="E2E latency SLO target"
    )
    parser.add_argument(
        "--ttft",
        type=float,
        default=float('inf'),
        help="Time To First Token SLO target"
    )
    parser.add_argument(
        "--tpat",
        type=float,
        default=float('inf'),
        help="Time Per All Token SLO target"
    )
    parser.add_argument(
        "--tpot",
        type=float,
        default=float('inf'),
        help="Time Per Output Token SLO target"
    )
    parser.add_argument(
        "--percentile",
        type=int,
        default=0,
        choices=[0, 50, 90, 99],
        help="Percentile to use for SLO calculation (default: 0, ignore percentile and use mean)"
    )
    parser.add_argument(
        "--cost",
        type=float,
        default=1.0,
        help="Cost of the GPU"
    )
    parser.add_argument(
        "-o",
        type=str,
        help="Output file name. Support redis as: redis://[username:password@]hostname:port[/db_name]?model=[model_name]"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print more information for understanding the generated profile"
    )


def handle(args: argparse.ArgumentParser) -> int:
    """Handle the gen-profile command."""
    try:
        # Set up sys.argv to match what the original gen_profile expects
        original_argv = sys.argv.copy()
        
        # Build new argv for the gen_profile
        new_argv = ["aibrix_gen_profile", args.deployment]
        
        if args.benchmark:
            new_argv.extend(["--benchmark", args.benchmark])
        
        if args.tput != 0.0:
            new_argv.extend(["--tput", str(args.tput)])
        
        if args.tt != 0.0:
            new_argv.extend(["--tt", str(args.tt)])
        
        if args.e2e != float('inf'):
            new_argv.extend(["--e2e", str(args.e2e)])
        
        if args.ttft != float('inf'):
            new_argv.extend(["--ttft", str(args.ttft)])
        
        if args.tpat != float('inf'):
            new_argv.extend(["--tpat", str(args.tpat)])
        
        if args.tpot != float('inf'):
            new_argv.extend(["--tpot", str(args.tpot)])
        
        if args.percentile != 0:
            new_argv.extend(["--percentile", str(args.percentile)])
        
        if args.cost != 1.0:
            new_argv.extend(["--cost", str(args.cost)])
        
        if args.o:
            new_argv.extend(["-o", args.o])
        
        if args.verbose:
            new_argv.append("--verbose")
        
        # Replace sys.argv temporarily
        sys.argv = new_argv
        
        try:
            # Call the original gen_profile main function
            return gen_profile_main()
        finally:
            # Restore original argv
            sys.argv = original_argv
            
    except Exception as e:
        print(f"Error generating profile: {e}")
        return 1 