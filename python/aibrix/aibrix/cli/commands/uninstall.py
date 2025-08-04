"""
Uninstall command for AIBrix CLI.

Handles uninstallation of AIBrix components.
"""

import argparse
import subprocess
import sys


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """Add arguments to the uninstall command parser."""
    parser.add_argument(
        "--all",
        action="store_true",
        help="Uninstall all AIBrix components"
    )
    parser.add_argument(
        "--component",
        type=str,
        help="Specific component to uninstall"
    )
    parser.add_argument(
        "--namespace",
        type=str,
        default="aibrix-system",
        help="Namespace to uninstall from (default: aibrix-system)"
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
        help="Force uninstallation without confirmation"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be uninstalled without actually uninstalling"
    )


def run_kubectl_delete(resource_type: str, resource_name: str, namespace: str, kubeconfig: str = None, context: str = None, dry_run: bool = False) -> int:
    """Run kubectl delete command."""
    cmd = ["kubectl", "delete"]
    
    if kubeconfig:
        cmd.extend(["--kubeconfig", kubeconfig])
    
    if context:
        cmd.extend(["--context", context])
    
    if dry_run:
        cmd.append("--dry-run=client")
    
    cmd.extend([resource_type, resource_name, "-n", namespace])
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            print(f"Error deleting {resource_type} {resource_name}: {stderr}")
            return process.returncode
        
        print(stdout)
        return 0
        
    except Exception as e:
        print(f"Error running kubectl delete: {e}")
        return 1


def handle(args: argparse.ArgumentParser) -> int:
    """Handle the uninstall command."""
    try:
        if not args.all and not args.component:
            print("Error: Must specify either --all or --component")
            return 1
        
        if args.all:
            print(f"Uninstalling all AIBrix components from namespace '{args.namespace}'...")
            
            # Confirm uninstallation unless --force is used
            if not args.force and not args.dry_run:
                print(f"Are you sure you want to uninstall all AIBrix components from namespace '{args.namespace}'? (y/N): ", end="")
                response = input().strip().lower()
                if response not in ['y', 'yes']:
                    print("Uninstallation cancelled.")
                    return 0
            
            # Delete namespace (this will cascade delete all resources)
            if args.dry_run:
                print(f"Would delete namespace '{args.namespace}'")
            else:
                result = run_kubectl_delete(
                    resource_type="namespace",
                    resource_name=args.namespace,
                    namespace="default",  # Use default namespace for namespace deletion
                    kubeconfig=args.kubeconfig,
                    context=args.context,
                    dry_run=args.dry_run
                )
                
                if result == 0:
                    print(f"Successfully uninstalled all AIBrix components from namespace '{args.namespace}'")
                else:
                    print(f"Failed to uninstall AIBrix components from namespace '{args.namespace}'")
                    return result
        
        elif args.component:
            print(f"Uninstalling component '{args.component}' from namespace '{args.namespace}'...")
            
            # Confirm uninstallation unless --force is used
            if not args.force and not args.dry_run:
                print(f"Are you sure you want to uninstall component '{args.component}' from namespace '{args.namespace}'? (y/N): ", end="")
                response = input().strip().lower()
                if response not in ['y', 'yes']:
                    print("Uninstallation cancelled.")
                    return 0
            
            # Delete specific component
            if args.dry_run:
                print(f"Would delete component '{args.component}' from namespace '{args.namespace}'")
            else:
                # This is a simplified implementation - in practice, you would need to
                # know the specific resource types and names for each component
                result = run_kubectl_delete(
                    resource_type="deployment",
                    resource_name=f"aibrix-{args.component}",
                    namespace=args.namespace,
                    kubeconfig=args.kubeconfig,
                    context=args.context,
                    dry_run=args.dry_run
                )
                
                if result == 0:
                    print(f"Successfully uninstalled component '{args.component}' from namespace '{args.namespace}'")
                else:
                    print(f"Failed to uninstall component '{args.component}' from namespace '{args.namespace}'")
                    return result
        
        return 0
        
    except Exception as e:
        print(f"Error uninstalling AIBrix: {e}")
        return 1 