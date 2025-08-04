"""
Logs command for AIBrix CLI.

Handles log retrieval from AIBrix workloads.
"""

import argparse
import time
from typing import List, Dict, Any
from aibrix.cli.k8s_client import AIBrixK8sClient


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """Add arguments to the logs command parser."""
    parser.add_argument(
        "--workload",
        type=str,
        required=True,
        help="Workload name to get logs from"
    )
    parser.add_argument(
        "--tail",
        type=int,
        help="Number of lines to show from the end of the logs"
    )
    parser.add_argument(
        "--follow",
        "-f",
        action="store_true",
        help="Follow log output"
    )
    parser.add_argument(
        "--container",
        type=str,
        help="Container name (if multi-container pod)"
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
        "--since",
        type=str,
        help="Show logs since timestamp (e.g., 2h, 1d)"
    )


def get_pods_for_workload(k8s_client: AIBrixK8sClient, workload_name: str, namespace: str) -> List[Dict[str, Any]]:
    """Get pods associated with a workload."""
    # Get the workload to understand its structure
    workload = k8s_client.get_stormservice(workload_name, namespace)
    if not workload:
        return []
    
    # Get pods with workload label
    label_selector = f"app={workload_name}"
    pods = k8s_client.list_pods(namespace, label_selector)
    
    # If no pods found with app label, try a broader search
    if not pods:
        # List all pods and filter by name pattern
        all_pods = k8s_client.list_pods(namespace)
        pods = [pod for pod in all_pods if workload_name in pod.get("metadata", {}).get("name", "")]
    
    return pods


def handle(args: argparse.Namespace) -> int:
    """Handle the logs command."""
    try:
        # Initialize Kubernetes client
        k8s_client = AIBrixK8sClient(
            kubeconfig=args.kubeconfig,
            context=args.context
        )
        
        # Get pods for the workload
        pods = get_pods_for_workload(k8s_client, args.workload, args.namespace)
        
        if not pods:
            print(f"No pods found for workload '{args.workload}' in namespace '{args.namespace}'")
            return 1
        
        # Get logs from each pod
        for pod in pods:
            pod_name = pod.get("metadata", {}).get("name", "unknown")
            pod_status = pod.get("status", {}).get("phase", "Unknown")
            
            print(f"=== Logs from pod {pod_name} (status: {pod_status}) ===")
            
            if pod_status == "Running":
                logs = k8s_client.get_pod_logs(
                    name=pod_name,
                    namespace=args.namespace,
                    container=args.container,
                    tail_lines=args.tail,
                    follow=args.follow
                )
                print(logs)
            else:
                print(f"Pod {pod_name} is not running (status: {pod_status})")
                print("Logs are not available for non-running pods.")
            
            print()  # Add separator between pods
        
        return 0
        
    except KeyboardInterrupt:
        print("\nLog following stopped by user")
        return 0
    except Exception as e:
        print(f"Error retrieving logs: {e}")
        return 1 