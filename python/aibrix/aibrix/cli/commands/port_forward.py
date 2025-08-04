"""
Port-forward command for AIBrix CLI.

Handles port forwarding to AIBrix services.
"""

import argparse
import subprocess
import sys
import signal
import time
from aibrix.cli.k8s_client import AIBrixK8sClient


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """Add arguments to the port-forward command parser."""
    parser.add_argument(
        "--service",
        type=str,
        required=True,
        help="Service name to port forward to"
    )
    parser.add_argument(
        "--port",
        type=str,
        required=True,
        help="Port mapping (e.g., 8888:80)"
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
        "--address",
        type=str,
        default="127.0.0.1",
        help="Address to bind to (default: 127.0.0.1)"
    )


def run_kubectl_port_forward(service: str, port: str, namespace: str, address: str, context: str = None) -> int:
    """Run kubectl port-forward command."""
    cmd = ["kubectl", "port-forward"]
    
    if context:
        cmd.extend(["--context", context])
    
    cmd.extend([
        f"service/{service}",
        f"--address={address}",
        port,
        "-n", namespace
    ])
    
    print(f"Running: {' '.join(cmd)}")
    print(f"Port forwarding {service}:{port} -> {address}:{port.split(':')[0]}")
    print("Press Ctrl+C to stop")
    
    try:
        # Run the kubectl command
        process = subprocess.Popen(cmd)
        
        # Wait for the process to complete
        return process.wait()
        
    except KeyboardInterrupt:
        print("\nStopping port forward...")
        if process:
            process.terminate()
            process.wait()
        return 0
    except Exception as e:
        print(f"Error running port forward: {e}")
        return 1


def handle(args: argparse.ArgumentParser) -> int:
    """Handle the port-forward command."""
    try:
        # Validate port format
        if ":" not in args.port:
            print("Error: Port must be in format 'local_port:remote_port' (e.g., 8888:80)")
            return 1
        
        # Initialize Kubernetes client to check if service exists
        k8s_client = AIBrixK8sClient(
            kubeconfig=args.kubeconfig,
            context=args.context
        )
        
        # Check if service exists (basic check)
        endpoints = k8s_client.get_service_endpoints(args.service, args.namespace)
        if not endpoints:
            print(f"Warning: Service '{args.service}' not found in namespace '{args.namespace}'")
            print("Port forwarding will still be attempted...")
        
        # Run port forward
        return run_kubectl_port_forward(
            service=args.service,
            port=args.port,
            namespace=args.namespace,
            address=args.address,
            context=args.context
        )
        
    except Exception as e:
        print(f"Error setting up port forward: {e}")
        return 1 