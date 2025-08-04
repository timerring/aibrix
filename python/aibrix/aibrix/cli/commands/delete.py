"""
Delete command for AIBrix CLI.

Handles deletion of AIBrix workloads.
"""

import argparse
from aibrix.cli.k8s_client import AIBrixK8sClient


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """Add arguments to the delete command parser."""
    parser.add_argument(
        "workload",
        type=str,
        help="Workload name to delete"
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
        "--force",
        action="store_true",
        help="Force deletion without confirmation"
    )
    parser.add_argument(
        "--grace-period",
        type=int,
        default=30,
        help="Grace period in seconds (default: 30)"
    )


def handle(args: argparse.ArgumentParser) -> int:
    """Handle the delete command."""
    try:
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
        
        # Confirm deletion unless --force is used
        if not args.force:
            print(f"Are you sure you want to delete workload '{args.workload}' from namespace '{args.namespace}'? (y/N): ", end="")
            response = input().strip().lower()
            if response not in ['y', 'yes']:
                print("Deletion cancelled.")
                return 0
        
        # Delete the workload
        print(f"Deleting workload '{args.workload}' from namespace '{args.namespace}'...")
        
        success = k8s_client.delete_stormservice(args.workload, args.namespace)
        
        if success:
            print(f"Successfully deleted workload '{args.workload}'")
        else:
            print(f"Failed to delete workload '{args.workload}'")
            return 1
        
        return 0
        
    except Exception as e:
        print(f"Error deleting workload: {e}")
        return 1 