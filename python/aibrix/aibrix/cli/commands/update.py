"""
Update command for AIBrix CLI.

Handles updating of AIBrix workload configurations.
"""

import argparse
import yaml
import os
from typing import Dict, Any
from aibrix.cli.k8s_client import AIBrixK8sClient


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """Add arguments to the update command parser."""
    parser.add_argument(
        "--workload",
        type=str,
        required=True,
        help="Workload name to update"
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Path to updated configuration file"
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
        help="Show what would be updated without actually updating"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force update without confirmation"
    )


def load_config_file(file_path: str) -> Dict[str, Any]:
    """Load configuration from file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Configuration file '{file_path}' not found")
    
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)


def merge_configs(current: Dict[str, Any], updated: Dict[str, Any]) -> Dict[str, Any]:
    """Merge updated configuration with current configuration."""
    # Deep copy current config
    result = yaml.safe_load(yaml.dump(current))
    
    # Update metadata
    if "metadata" in updated:
        if "metadata" not in result:
            result["metadata"] = {}
        result["metadata"].update(updated["metadata"])
    
    # Update spec
    if "spec" in updated:
        if "spec" not in result:
            result["spec"] = {}
        result["spec"].update(updated["spec"])
    
    return result


def handle(args: argparse.ArgumentParser) -> int:
    """Handle the update command."""
    try:
        # Initialize Kubernetes client
        k8s_client = AIBrixK8sClient(
            kubeconfig=args.kubeconfig,
            context=args.context
        )
        
        # Get current workload
        current_workload = k8s_client.get_stormservice(args.workload, args.namespace)
        if not current_workload:
            print(f"Error: Workload '{args.workload}' not found in namespace '{args.namespace}'")
            return 1
        
        # Load updated configuration if file is provided
        if args.file:
            updated_config = load_config_file(args.file)
            
            # Merge configurations
            merged_config = merge_configs(current_workload, updated_config)
        else:
            print("Error: Must provide --file with updated configuration")
            return 1
        
        if args.dry_run:
            print("=== DRY RUN - Updated workload configuration ===")
            print(yaml.dump(merged_config, default_flow_style=False))
            return 0
        
        # Confirm update unless --force is used
        if not args.force:
            print(f"Are you sure you want to update workload '{args.workload}' in namespace '{args.namespace}'? (y/N): ", end="")
            response = input().strip().lower()
            if response not in ['y', 'yes']:
                print("Update cancelled.")
                return 0
        
        # Update the workload
        print(f"Updating workload '{args.workload}' in namespace '{args.namespace}'...")
        
        result = k8s_client.update_stormservice(args.workload, merged_config, args.namespace)
        
        print(f"Successfully updated workload '{args.workload}'")
        return 0
        
    except Exception as e:
        print(f"Error updating workload: {e}")
        return 1 