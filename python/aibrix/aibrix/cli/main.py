# Copyright 2024 The Aibrix Team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# 	http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Main CLI entry point for AIBrix advanced command-line interface."""

import argparse
import sys
from typing import List, Optional

from ..logger import init_logger
from .commands import (
    install,
    management,
    monitoring,
    templates,
)
from .completion import add_completion_parser

logger = init_logger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog="aibrix",
        description="AIBrix - Advanced CLI for AI/ML workload management on Kubernetes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  aibrix install --version latest                    # Install AIBrix components
  aibrix deploy --template quickstart                # Deploy using quickstart template
  aibrix list workloads                              # List all workloads
  aibrix scale --workload my-model --replicas 3      # Scale workload
  aibrix logs --workload my-model --tail 100         # View logs
  aibrix workload-status --workload my-model         # Check workload status

For more information, visit: https://github.com/vllm-project/aibrix
        """
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.3.0"  # TODO: Get from __version__.py
    )
    
    parser.add_argument(
        "--kubeconfig",
        type=str,
        help="Path to kubeconfig file (default: ~/.kube/config)"
    )
    
    parser.add_argument(
        "--namespace",
        "-n",
        type=str,
        default="default",
        help="Kubernetes namespace (default: default)"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output"
    )

    # Create subparsers for different command groups
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Installation commands
    install.add_subparser(subparsers)
    
    # Management commands  
    management.add_subparser(subparsers)
    
    # Monitoring commands
    monitoring.add_subparser(subparsers)
    
    # Template commands
    templates.add_subparser(subparsers)
    
    # Completion commands
    add_completion_parser(subparsers)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entry point."""
    if argv is None:
        argv = sys.argv[1:]
    
    parser = create_parser()
    args = parser.parse_args(argv)
    
    # Configure logging level
    if args.verbose:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Handle case where no command is provided
    if args.command is None:
        parser.print_help()
        return 1
    
    try:
        # Dispatch to appropriate command handler
        if hasattr(args, "func"):
            return args.func(args)
        else:
            logger.error(f"No handler found for command: {args.command}")
            return 1
            
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        return 130
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
