"""
Scale command for AIBrix CLI.

Handles scaling of AIBrix workloads.
"""

import argparse
from aibrix.cli.k8s_client import AIBrixK8sClient


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """Add arguments to the scale command parser."""
    parser.add_argument(
        "--workload",
        type=str,
        required=True,
        help="Workload name to scale"
    )
    parser.add_argument(
        "--replicas",
        type=int,
        required=True,
        help="Number of replicas"
    )
    parser.add_argument(
        "--namespace",
        type=str,
        default="default",
        help="Kubernetes namespace (default: default)"
    )
    parser.add_argument(
        "--kubeconfig",
        type=str,
        help="Path to kubeconfig file"
    )
    parser.add_argument(
        "--context",
        type=str,
        help="Kubernetes context to use"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be scaled without actually scaling"
    )


def handle(args: argparse.Namespace) -> int:
    """Handle the scale command."""
    try:
        # Validate replicas
        if args.replicas < 0:
            print("Error: Replicas must be a non-negative integer")
            return 1
        
        # Initialize Kubernetes client
        k8s_client = AIBrixK8sClient(
            kubeconfig=args.kubeconfig,
            context=args.context
        )
        
        # Check if workload exists
        workload = k8s_client.get_stormservice(args.workload, args.namespace)
        if not workload:
            print(f"Error: Workload '{args.workload}' not found in namespace '{args.namespace}'")
            return 1
        
        current_replicas = workload.get("spec", {}).get("replicas", 0)
        
        if args.dry_run:
            print(f"=== DRY RUN - Scaling '{args.workload}' ===")
            print(f"Current replicas: {current_replicas}")
            print(f"Target replicas: {args.replicas}")
            return 0
        
        # Scale the workload
        print(f"Scaling '{args.workload}' from {current_replicas} to {args.replicas} replicas...")
        
        result = k8s_client.scale_stormservice(args.workload, args.replicas, args.namespace)
        
        print(f"Successfully scaled '{args.workload}' to {args.replicas} replicas")
        return 0
        
    except Exception as e:
        print(f"Error scaling workload: {e}")
        return 1 