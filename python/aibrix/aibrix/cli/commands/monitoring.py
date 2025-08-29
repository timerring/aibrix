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

"""Monitoring commands for AIBrix workloads."""

import argparse
import asyncio
import signal
import subprocess
import sys
from typing import Any, Dict, List, Optional

from ...logger import init_logger
from ..k8s_client import AIBrixK8sClient

logger = init_logger(__name__)


class WorkloadMonitor:
    """Handles monitoring and observability for AIBrix workloads."""
    
    def __init__(self, k8s_client: AIBrixK8sClient):
        """Initialize the workload monitor.
        
        Args:
            k8s_client: Kubernetes client instance
        """
        self.k8s_client = k8s_client
    
    async def get_workload_status(self, name: str, workload_type: str = "deployment") -> Dict[str, Any]:
        """Get detailed status of a workload.
        
        Args:
            name: Workload name
            workload_type: Type of workload
            
        Returns:
            Dictionary with workload status information
        """
        try:
            if workload_type == "deployment":
                deployment = await self.k8s_client.get_deployment(name)
                if not deployment:
                    return {"status": "Not Found", "error": f"Deployment {name} not found"}
                
                return self._format_deployment_status(deployment)
            else:
                # Handle custom resources
                # TODO: Implement custom resource status retrieval
                return {"status": "Unknown", "type": workload_type}
                
        except Exception as e:
            logger.error(f"Failed to get workload status: {e}")
            return {"status": "Error", "error": str(e)}
    
    def _format_deployment_status(self, deployment: Dict[str, Any]) -> Dict[str, Any]:
        """Format deployment status information.
        
        Args:
            deployment: Deployment object
            
        Returns:
            Formatted status dictionary
        """
        metadata = deployment.get("metadata", {})
        spec = deployment.get("spec", {})
        status = deployment.get("status", {})
        
        ready_replicas = status.get("readyReplicas", 0)
        replicas = status.get("replicas", 0)
        target_replicas = spec.get("replicas", 0)
        unavailable_replicas = status.get("unavailableReplicas", 0)
        
        # Determine overall status
        if ready_replicas == target_replicas and unavailable_replicas == 0:
            overall_status = "Ready"
        elif ready_replicas > 0:
            overall_status = "Partially Ready"
        else:
            overall_status = "Not Ready"
        
        return {
            "name": metadata.get("name"),
            "namespace": metadata.get("namespace"),
            "status": overall_status,
            "replicas": {
                "ready": ready_replicas,
                "total": replicas,
                "target": target_replicas,
                "unavailable": unavailable_replicas
            },
            "labels": metadata.get("labels", {}),
            "creationTimestamp": metadata.get("creationTimestamp")
        }
    
    async def get_workload_logs(
        self,
        name: str,
        container: Optional[str] = None,
        tail_lines: Optional[int] = None,
        follow: bool = False,
        previous: bool = False
    ) -> Optional[str]:
        """Get logs from a workload.
        
        Args:
            name: Workload name
            container: Container name (if multiple containers)
            tail_lines: Number of lines to tail
            follow: Whether to follow logs
            previous: Get logs from previous container instance
            
        Returns:
            Log content as string, or None if failed
        """
        try:
            # First, find pods for the workload
            pods = await self._get_pods_for_workload(name)
            
            if not pods:
                logger.error(f"No pods found for workload: {name}")
                return None
            
            # Use the first available pod
            pod_name = pods[0]["metadata"]["name"]
            
            return await self.k8s_client.get_pod_logs(
                pod_name=pod_name,
                container=container,
                tail_lines=tail_lines,
                follow=follow
            )
            
        except Exception as e:
            logger.error(f"Failed to get logs: {e}")
            return None
    
    async def _get_pods_for_workload(self, workload_name: str) -> List[Dict[str, Any]]:
        """Get pods belonging to a workload.
        
        Args:
            workload_name: Name of the workload
            
        Returns:
            List of pod objects
        """
        try:
            # Use label selector to find pods
            label_selector = f"model.aibrix.ai/name={workload_name}"
            
            # TODO: Implement pod listing with label selector
            # For now, return mock data
            return [
                {
                    "metadata": {
                        "name": f"{workload_name}-pod-1",
                        "namespace": self.k8s_client.namespace
                    }
                }
            ]
            
        except Exception as e:
            logger.error(f"Failed to get pods for workload: {e}")
            return []
    
    async def port_forward(
        self,
        service: str,
        local_port: int,
        remote_port: int,
        namespace: Optional[str] = None
    ) -> bool:
        """Set up port forwarding to a service.
        
        Args:
            service: Service name
            local_port: Local port to forward to
            remote_port: Remote port to forward from
            namespace: Namespace (uses default if None)
            
        Returns:
            True if port forwarding started successfully
        """
        ns = namespace or self.k8s_client.namespace
        
        try:
            # Use kubectl port-forward for simplicity
            cmd = [
                "kubectl",
                "port-forward",
                f"service/{service}",
                f"{local_port}:{remote_port}",
                "-n", ns
            ]
            
            logger.info(f"Starting port forward: {service}:{remote_port} -> localhost:{local_port}")
            logger.info("Press Ctrl+C to stop port forwarding")
            
            # Run kubectl port-forward
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Set up signal handling for graceful shutdown
            def signal_handler(signum, frame):
                logger.info("Stopping port forward...")
                process.terminate()
                sys.exit(0)
            
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
            
            # Wait for process to complete
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                logger.info("Port forwarding completed")
                return True
            else:
                logger.error(f"Port forwarding failed: {stderr}")
                return False
                
        except FileNotFoundError:
            logger.error("kubectl not found. Please install kubectl to use port forwarding")
            return False
        except Exception as e:
            logger.error(f"Port forwarding failed: {e}")
            return False
    
    async def get_workload_events(self, name: str) -> List[Dict[str, Any]]:
        """Get events related to a workload.
        
        Args:
            name: Workload name
            
        Returns:
            List of event objects
        """
        try:
            # TODO: Implement event retrieval
            # This would involve listing events with field selectors
            
            # For now, return mock events
            return [
                {
                    "type": "Normal",
                    "reason": "Scheduled",
                    "message": f"Successfully assigned {name} to node",
                    "timestamp": "2024-01-01T00:00:00Z"
                }
            ]
            
        except Exception as e:
            logger.error(f"Failed to get events: {e}")
            return []


async def handle_status(args: argparse.Namespace) -> int:
    """Handle status command."""
    try:
        k8s_client = AIBrixK8sClient(
            kubeconfig_path=args.kubeconfig,
            namespace=args.namespace
        )
        
        monitor = WorkloadMonitor(k8s_client)
        
        status = await monitor.get_workload_status(args.workload, args.type)
        
        # Print status information
        print(f"Workload: {status.get('name', args.workload)}")
        print(f"Namespace: {status.get('namespace', args.namespace)}")
        print(f"Status: {status.get('status', 'Unknown')}")
        
        if "replicas" in status:
            replicas = status["replicas"]
            print(f"Replicas: {replicas['ready']}/{replicas['target']} ready")
            if replicas["unavailable"] > 0:
                print(f"Unavailable: {replicas['unavailable']}")
        
        if "labels" in status and status["labels"]:
            print("Labels:")
            for key, value in status["labels"].items():
                print(f"  {key}={value}")
        
        if "error" in status:
            print(f"Error: {status['error']}")
        
        # Get and display events if requested
        if args.events:
            events = await monitor.get_workload_events(args.workload)
            if events:
                print("\\nRecent Events:")
                for event in events[-5:]:  # Show last 5 events
                    print(f"  {event['timestamp']} {event['type']} {event['reason']}: {event['message']}")
        
        k8s_client.close()
        return 0
        
    except Exception as e:
        logger.error(f"Status command failed: {e}")
        return 1


async def handle_logs(args: argparse.Namespace) -> int:
    """Handle logs command."""
    try:
        k8s_client = AIBrixK8sClient(
            kubeconfig_path=args.kubeconfig,
            namespace=args.namespace
        )
        
        monitor = WorkloadMonitor(k8s_client)
        
        logs = await monitor.get_workload_logs(
            name=args.workload,
            container=args.container,
            tail_lines=args.tail,
            follow=args.follow,
            previous=args.previous
        )
        
        if logs:
            print(logs)
        else:
            logger.error("Failed to retrieve logs")
            return 1
        
        k8s_client.close()
        return 0
        
    except Exception as e:
        logger.error(f"Logs command failed: {e}")
        return 1


async def handle_port_forward(args: argparse.Namespace) -> int:
    """Handle port-forward command."""
    try:
        k8s_client = AIBrixK8sClient(
            kubeconfig_path=args.kubeconfig,
            namespace=args.namespace
        )
        
        monitor = WorkloadMonitor(k8s_client)
        
        # Parse port specification
        if ":" in args.port:
            local_port, remote_port = args.port.split(":", 1)
            local_port = int(local_port)
            remote_port = int(remote_port)
        else:
            local_port = remote_port = int(args.port)
        
        success = await monitor.port_forward(
            service=args.service,
            local_port=local_port,
            remote_port=remote_port,
            namespace=args.namespace
        )
        
        k8s_client.close()
        return 0 if success else 1
        
    except Exception as e:
        logger.error(f"Port-forward command failed: {e}")
        return 1


def add_subparser(subparsers) -> None:
    """Add monitoring subcommands to the main parser."""
    
    # Workload status command
    status_parser = subparsers.add_parser(
        "workload-status", 
        help="Show workload status",
        description="Show detailed status of AIBrix workloads"
    )
    
    status_parser.add_argument(
        "--workload",
        required=True,
        help="Workload name to check status"
    )
    
    status_parser.add_argument(
        "--type",
        default="deployment",
        help="Workload type (default: deployment)"
    )
    
    status_parser.add_argument(
        "--events",
        action="store_true",
        help="Include recent events in status output"
    )
    
    status_parser.set_defaults(func=lambda args: asyncio.run(handle_status(args)))
    
    # Logs command
    logs_parser = subparsers.add_parser(
        "logs",
        help="Show workload logs",
        description="Retrieve and display logs from AIBrix workloads"
    )
    
    logs_parser.add_argument(
        "--workload",
        required=True,
        help="Workload name to get logs from"
    )
    
    logs_parser.add_argument(
        "--container", "-c",
        help="Container name (if workload has multiple containers)"
    )
    
    logs_parser.add_argument(
        "--tail",
        type=int,
        help="Number of lines to tail from the end of logs"
    )
    
    logs_parser.add_argument(
        "--follow", "-f",
        action="store_true",
        help="Follow log output (stream logs)"
    )
    
    logs_parser.add_argument(
        "--previous", "-p",
        action="store_true",
        help="Get logs from previous container instance"
    )
    
    logs_parser.set_defaults(func=lambda args: asyncio.run(handle_logs(args)))
    
    # Port-forward command
    port_forward_parser = subparsers.add_parser(
        "port-forward",
        help="Forward local port to service",
        description="Set up port forwarding to AIBrix services"
    )
    
    port_forward_parser.add_argument(
        "--service",
        required=True,
        help="Service name to forward to"
    )
    
    port_forward_parser.add_argument(
        "--port",
        required=True,
        help="Port specification (local:remote or just port for same local/remote)"
    )
    
    port_forward_parser.set_defaults(func=lambda args: asyncio.run(handle_port_forward(args)))
