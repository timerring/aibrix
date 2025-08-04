"""
Status command for AIBrix CLI.

Handles status checking of AIBrix workloads.
"""

import argparse
from typing import Dict, Any, Optional
from aibrix.cli.k8s_client import AIBrixK8sClient


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """Add arguments to the status command parser."""
    parser.add_argument(
        "--workload",
        type=str,
        help="Specific workload name to check (if not specified, shows all)"
    )
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
        "--watch",
        action="store_true",
        help="Watch status changes (not implemented yet)"
    )


def get_workload_status(workload: Dict[str, Any]) -> Dict[str, Any]:
    """Extract status information from a workload."""
    metadata = workload.get("metadata", {})
    spec = workload.get("spec", {})
    status = workload.get("status", {})
    
    # Basic info
    status_info = {
        "name": metadata.get("name", "unknown"),
        "kind": workload.get("kind", "unknown"),
        "namespace": metadata.get("namespace", "default"),
        "replicas": spec.get("replicas", 0),
        "ready_replicas": status.get("readyReplicas", 0),
        "available_replicas": status.get("availableReplicas", 0),
        "updated_replicas": status.get("updatedReplicas", 0),
    }
    
    # Conditions
    conditions = status.get("conditions", [])
    status_info["conditions"] = []
    
    for condition in conditions:
        status_info["conditions"].append({
            "type": condition.get("type", "Unknown"),
            "status": condition.get("status", "Unknown"),
            "reason": condition.get("reason", ""),
            "message": condition.get("message", ""),
            "last_transition_time": condition.get("lastTransitionTime", ""),
        })
    
    # Overall status
    if conditions:
        ready_condition = next(
            (c for c in conditions if c.get("type") == "Ready"),
            None
        )
        if ready_condition:
            status_info["overall_status"] = "Ready" if ready_condition.get("status") == "True" else "NotReady"
        else:
            status_info["overall_status"] = "Unknown"
    else:
        status_info["overall_status"] = "Unknown"
    
    return status_info


def format_status_table(statuses: list, wide: bool = False) -> str:
    """Format status information as a table."""
    if not statuses:
        return "No workloads found."
    
    # Define headers
    if wide:
        headers = ["NAME", "KIND", "REPLICAS", "READY", "AVAILABLE", "UPDATED", "STATUS", "CONDITIONS"]
    else:
        headers = ["NAME", "REPLICAS", "READY", "STATUS"]
    
    # Calculate column widths
    col_widths = [len(h) for h in headers]
    
    # Process each status
    rows = []
    for status in statuses:
        if wide:
            # Format conditions for wide output
            conditions_str = "; ".join([
                f"{c['type']}={c['status']}" for c in status.get("conditions", [])
            ])
            if len(conditions_str) > 50:
                conditions_str = conditions_str[:47] + "..."
            
            row = [
                status["name"],
                status["kind"],
                str(status["replicas"]),
                str(status["ready_replicas"]),
                str(status["available_replicas"]),
                str(status["updated_replicas"]),
                status["overall_status"],
                conditions_str
            ]
        else:
            row = [
                status["name"],
                str(status["replicas"]),
                str(status["ready_replicas"]),
                status["overall_status"]
            ]
        
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


def format_status_yaml(statuses: list) -> str:
    """Format status information as YAML."""
    import yaml
    return yaml.dump(statuses, default_flow_style=False)


def format_status_json(statuses: list) -> str:
    """Format status information as JSON."""
    import json
    return json.dumps(statuses, indent=2)


def handle(args: argparse.Namespace) -> int:
    """Handle the status command."""
    try:
        # Initialize Kubernetes client
        k8s_client = AIBrixK8sClient(
            kubeconfig=args.kubeconfig,
            context=args.context
        )
        
        statuses = []
        
        if args.workload:
            # Check specific workload
            workload = k8s_client.get_stormservice(args.workload, args.namespace)
            if not workload:
                print(f"Error: Workload '{args.workload}' not found in namespace '{args.namespace}'")
                return 1
            
            status_info = get_workload_status(workload)
            statuses.append(status_info)
        else:
            # Check all workloads
            print(f"Checking status of AIBrix workloads in namespace '{args.namespace}'...")
            stormservices = k8s_client.list_stormservices(args.namespace)
            
            for workload in stormservices:
                status_info = get_workload_status(workload)
                statuses.append(status_info)
        
        if not statuses:
            print("No workloads found.")
            return 0
        
        # Format output
        if args.output == "table":
            output = format_status_table(statuses, wide=True)
        elif args.output == "yaml":
            output = format_status_yaml(statuses)
        elif args.output == "json":
            output = format_status_json(statuses)
        else:
            print(f"Unknown output format: {args.output}")
            return 1
        
        print(output)
        return 0
        
    except Exception as e:
        print(f"Error checking workload status: {e}")
        return 1 