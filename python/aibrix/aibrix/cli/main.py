#!/usr/bin/env python3
"""
AIBrix Advanced CLI - Main Entry Point

Unified command-line interface for AIBrix workload management.
"""

import argparse
import sys
from typing import Optional

from aibrix.cli.commands import (
    install,
    uninstall,
    deploy,
    validate,
    list_workloads,
    delete,
    update,
    scale,
    port_forward,
    status,
    logs,
    runtime,
    download,
    benchmark,
    gen_profile,
)


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser for the AIBrix CLI."""
    parser = argparse.ArgumentParser(
        description="AIBrix Advanced CLI - Manage AI workloads on Kubernetes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Install AIBrix components
  aibrix install --version latest
  
  # Deploy a workload using template
  aibrix deploy --template deepseek-7b --params config.yaml
  
  # List all workloads
  aibrix list
  
  # Scale a workload
  aibrix scale --workload my-model --replicas 3
  
  # Get workload status
  aibrix status --workload my-model
  
  # View logs
  aibrix logs --workload my-model --tail 100
  
  # Port forward to service
  aibrix port-forward --service envoy-gateway --port 8888
  
  # Run runtime server
  aibrix runtime --port 8080
  
  # Download model
  aibrix download --model-uri deepseek-ai/deepseek-coder-6.7b-instruct
  
  # Run benchmark
  aibrix benchmark -m deepseek-coder-7b -o ./benchmark_results
  
  # Generate profile
  aibrix gen-profile deepseek-coder-7b --cost 1.0 --tput 10.0
        """,
    )
    
    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
        metavar="COMMAND",
    )
    
    # Installation commands
    install_parser = subparsers.add_parser(
        "install",
        help="Install AIBrix components",
        description="Install AIBrix components on the cluster",
    )
    install.add_arguments(install_parser)
    
    uninstall_parser = subparsers.add_parser(
        "uninstall",
        help="Uninstall AIBrix components",
        description="Uninstall AIBrix components from the cluster",
    )
    uninstall.add_arguments(uninstall_parser)
    
    # Deployment commands
    deploy_parser = subparsers.add_parser(
        "deploy",
        help="Deploy workloads",
        description="Deploy AIBrix workloads using templates",
    )
    deploy.add_arguments(deploy_parser)
    
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate configuration",
        description="Validate workload configuration files",
    )
    validate.add_arguments(validate_parser)
    
    # Management commands
    list_parser = subparsers.add_parser(
        "list",
        help="List workloads",
        description="List all AIBrix workloads",
    )
    list_workloads.add_arguments(list_parser)
    
    delete_parser = subparsers.add_parser(
        "delete",
        help="Delete workloads",
        description="Delete AIBrix workloads",
    )
    delete.add_arguments(delete_parser)
    
    update_parser = subparsers.add_parser(
        "update",
        help="Update workloads",
        description="Update AIBrix workload configurations",
    )
    update.add_arguments(update_parser)
    
    scale_parser = subparsers.add_parser(
        "scale",
        help="Scale workloads",
        description="Scale AIBrix workloads",
    )
    scale.add_arguments(scale_parser)
    
    # Monitoring commands
    status_parser = subparsers.add_parser(
        "status",
        help="Check workload status",
        description="Check the status of AIBrix workloads",
    )
    status.add_arguments(status_parser)
    
    logs_parser = subparsers.add_parser(
        "logs",
        help="View workload logs",
        description="View logs from AIBrix workloads",
    )
    logs.add_arguments(logs_parser)
    
    port_forward_parser = subparsers.add_parser(
        "port-forward",
        help="Port forward to services",
        description="Port forward to AIBrix services",
    )
    port_forward.add_arguments(port_forward_parser)
    
    # Legacy command integrations
    runtime_parser = subparsers.add_parser(
        "runtime",
        help="Run AIBrix runtime server",
        description="Start the AIBrix runtime server",
    )
    runtime.add_arguments(runtime_parser)
    
    download_parser = subparsers.add_parser(
        "download",
        help="Download models",
        description="Download models from various sources",
    )
    download.add_arguments(download_parser)
    
    benchmark_parser = subparsers.add_parser(
        "benchmark",
        help="Run benchmarks",
        description="Run AIBrix benchmarks",
    )
    benchmark.add_arguments(benchmark_parser)
    
    gen_profile_parser = subparsers.add_parser(
        "gen-profile",
        help="Generate profiles",
        description="Generate AIBrix profiles",
    )
    gen_profile.add_arguments(gen_profile_parser)
    
    return parser


def main(args: Optional[list] = None) -> int:
    """Main entry point for the AIBrix CLI."""
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    
    if not parsed_args.command:
        parser.print_help()
        return 1
    
    try:
        # Route to appropriate command handler
        command_handlers = {
            "install": install.handle,
            "uninstall": uninstall.handle,
            "deploy": deploy.handle,
            "validate": validate.handle,
            "list": list_workloads.handle,
            "delete": delete.handle,
            "update": update.handle,
            "scale": scale.handle,
            "status": status.handle,
            "logs": logs.handle,
            "port-forward": port_forward.handle,
            "runtime": runtime.handle,
            "download": download.handle,
            "benchmark": benchmark.handle,
            "gen-profile": gen_profile.handle,
        }
        
        handler = command_handlers.get(parsed_args.command)
        if handler:
            return handler(parsed_args)
        else:
            print(f"Unknown command: {parsed_args.command}")
            return 1
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 130
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 