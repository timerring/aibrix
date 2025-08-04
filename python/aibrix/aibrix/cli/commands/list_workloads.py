"""
List command for AIBrix CLI.

Handles listing of AIBrix workloads.
"""

import argparse
from typing import List, Dict, Any
from aibrix.cli.k8s_client import AIBrixK8sClient


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """Add arguments to the list command parser."""
    parser.add_argument(
        "--namespace",
        type=str,
        default="default",
        help="Kubernetes namespace (default: default)"
    )
    parser.add_argument(
        "--output",
        type=str,
        choices=["table", "yaml", "json"],
        default="table",
        help="Output format (default: table)"
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
        "--wide",
        action="store_true",
        help="Show additional details in table output"
    )


def format_table(workloads: List[Dict[str, Any]], wide: bool = False) -> str:
    """Format workloads as a table."""
    if not workloads:
        return "No workloads found."
    
    # Define headers
    if wide:
        headers = ["NAME", "KIND", "NAMESPACE", "REPLICAS", "STATUS", "AGE", "IMAGE"]
    else:
        headers = ["NAME", "KIND", "REPLICAS", "STATUS", "AGE"]
    
    # Calculate column widths
    col_widths = [len(h) for h in headers]
    
    # Process each workload
    rows = []
    for workload in workloads:
        metadata = workload.get("metadata", {})
        spec = workload.get("spec", {})
        status = workload.get("status", {})
        
        name = metadata.get("name", "unknown")
        kind = workload.get("kind", "unknown")
        namespace = metadata.get("namespace", "default")
        replicas = spec.get("replicas", 0)
        
        # Determine status
        if status.get("conditions"):
            # Look for ready condition
            ready_condition = next(
                (c for c in status["conditions"] if c.get("type") == "Ready"),
                None
            )
            if ready_condition:
                status_str = "Ready" if ready_condition.get("status") == "True" else "NotReady"
            else:
                status_str = "Unknown"
        else:
            status_str = "Unknown"
        
        # Calculate age (simplified)
        creation_timestamp = metadata.get("creationTimestamp")
        if creation_timestamp:
            # This is a simplified age calculation
            age = "1d"  # Placeholder
        else:
            age = "Unknown"
        
        # Get image info for wide output
        image = "N/A"
        if wide and "rolesets" in spec:
            for roleset in spec["rolesets"]:
                template = roleset.get("template", {})
                containers = template.get("spec", {}).get("containers", [])
                if containers:
                    image = containers[0].get("image", "N/A")
                    break
        
        if wide:
            row = [name, kind, namespace, str(replicas), status_str, age, image]
        else:
            row = [name, kind, str(replicas), status_str, age]
        
        # Update column widths
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
        
        rows.append(row)
    
    # Build the table
    table = []
    
    # Header
    header_row = "  ".join(h.ljust(w) for h, w in zip(headers, col_widths))
    table.append(header_row)
    table.append("-" * len(header_row))
    
    # Data rows
    for row in rows:
        table.append("  ".join(str(cell).ljust(w) for cell, w in zip(row, col_widths)))
    
    return "\n".join(table)


def format_yaml(workloads: List[Dict[str, Any]]) -> str:
    """Format workloads as YAML."""
    import yaml
    return yaml.dump(workloads, default_flow_style=False)


def format_json(workloads: List[Dict[str, Any]]) -> str:
    """Format workloads as JSON."""
    import json
    return json.dumps(workloads, indent=2)


def handle(args: argparse.Namespace) -> int:
    """Handle the list command."""
    try:
        # Initialize Kubernetes client
        k8s_client = AIBrixK8sClient(
            kubeconfig=args.kubeconfig,
            context=args.context
        )
        
        # List StormServices
        print(f"Listing AIBrix workloads in namespace '{args.namespace}'...")
        stormservices = k8s_client.list_stormservices(args.namespace)
        
        # List other AIBrix resources (placeholder for future expansion)
        # kvcaches = k8s_client.list_kvcaches(args.namespace)
        # modeladapters = k8s_client.list_modeladapters(args.namespace)
        
        all_workloads = stormservices  # + kvcaches + modeladapters
        
        if not all_workloads:
            print("No AIBrix workloads found.")
            return 0
        
        # Format output
        if args.output == "table":
            output = format_table(all_workloads, args.wide)
        elif args.output == "yaml":
            output = format_yaml(all_workloads)
        elif args.output == "json":
            output = format_json(all_workloads)
        else:
            print(f"Unknown output format: {args.output}")
            return 1
        
        print(output)
        return 0
        
    except Exception as e:
        print(f"Error listing workloads: {e}")
        return 1 