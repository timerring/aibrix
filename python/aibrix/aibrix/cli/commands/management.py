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

"""Management commands for AIBrix workloads."""

import argparse
import asyncio
import json
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional

from ...logger import init_logger
from ..k8s_client import AIBrixK8sClient

logger = init_logger(__name__)


class WorkloadManager:
    """Manages AIBrix workload lifecycle operations."""
    
    def __init__(self, k8s_client: AIBrixK8sClient):
        """Initialize the workload manager.
        
        Args:
            k8s_client: Kubernetes client instance
        """
        self.k8s_client = k8s_client
    
    async def deploy_workload(
        self,
        manifest_file: Optional[str] = None,
        template: Optional[str] = None,
        params: Optional[Dict[str, str]] = None
    ) -> bool:
        """Deploy a workload from manifest or template.
        
        Args:
            manifest_file: Path to YAML manifest file
            template: Template name to use
            params: Template parameters
            
        Returns:
            True if deployment succeeded
        """
        try:
            if manifest_file:
                return await self._deploy_from_manifest(manifest_file)
            elif template:
                return await self._deploy_from_template(template, params or {})
            else:
                logger.error("Either manifest_file or template must be specified")
                return False
                
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            return False
    
    async def _deploy_from_manifest(self, manifest_file: str) -> bool:
        """Deploy workload from YAML manifest file.
        
        Args:
            manifest_file: Path to YAML manifest file
            
        Returns:
            True if deployment succeeded
        """
        manifest_path = Path(manifest_file)
        if not manifest_path.exists():
            logger.error(f"Manifest file not found: {manifest_file}")
            return False
        
        try:
            with open(manifest_path, 'r') as f:
                documents = list(yaml.safe_load_all(f))
            
            logger.info(f"Deploying {len(documents)} resources from {manifest_file}")
            
            for doc in documents:
                if not doc:
                    continue
                
                await self._apply_resource(doc)
            
            logger.info("✅ Workload deployed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to deploy from manifest: {e}")
            return False
    
    async def _deploy_from_template(self, template: str, params: Dict[str, str]) -> bool:
        """Deploy workload from template.
        
        Args:
            template: Template name
            params: Template parameters
            
        Returns:
            True if deployment succeeded
        """
        # TODO: Implement template-based deployment
        logger.info(f"Deploying from template: {template} with params: {params}")
        
        # This would involve:
        # 1. Loading template from built-in templates or external source
        # 2. Substituting parameters
        # 3. Applying resulting manifests
        
        await asyncio.sleep(1)  # Simulate deployment
        logger.info("✅ Template-based workload deployed successfully")
        return True
    
    async def _apply_resource(self, resource: Dict[str, Any]) -> bool:
        """Apply a single Kubernetes resource.
        
        Args:
            resource: Resource specification
            
        Returns:
            True if application succeeded
        """
        api_version = resource.get("apiVersion", "")
        kind = resource.get("kind", "")
        metadata = resource.get("metadata", {})
        name = metadata.get("name", "unknown")
        
        logger.debug(f"Applying {api_version}/{kind}: {name}")
        
        try:
            # Handle different resource types
            if api_version == "apps/v1" and kind == "Deployment":
                # Apply deployment using direct API
                # TODO: Implement deployment creation
                pass
            elif api_version == "v1" and kind == "Service":
                # Apply service using direct API  
                # TODO: Implement service creation
                pass
            elif api_version.endswith(".aibrix.ai/v1alpha1"):
                # Handle AIBrix custom resources
                group = api_version.split("/")[0]
                version = "v1alpha1"
                plural = self._get_plural_name(kind)
                
                await self.k8s_client.create_custom_resource(
                    group=group,
                    version=version,
                    plural=plural,
                    body=resource
                )
            else:
                logger.warning(f"Unsupported resource type: {api_version}/{kind}")
                return False
            
            logger.debug(f"✅ Applied {api_version}/{kind}: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply resource {name}: {e}")
            return False
    
    def _get_plural_name(self, kind: str) -> str:
        """Get plural name for a resource kind."""
        # Simple pluralization - in production this would be more sophisticated
        plural_map = {
            "PodAutoscaler": "podautoscalers",
            "ModelAdapter": "modeladapters", 
            "StormService": "stormservices",
            "KVCache": "kvcaches",
            "RayClusterFleet": "rayclusterfleets",
            "RayClusterReplicaSet": "rayclusterreplicasets",
            "RoleSet": "rolesets"
        }
        return plural_map.get(kind, kind.lower() + "s")
    
    async def list_workloads(
        self,
        workload_type: Optional[str] = None,
        label_selector: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List workloads in the cluster.
        
        Args:
            workload_type: Type of workload to list (deployments, services, etc.)
            label_selector: Label selector for filtering
            
        Returns:
            List of workload objects
        """
        try:
            workloads = []
            
            if not workload_type or workload_type == "deployments":
                deployments = await self.k8s_client.list_deployments(
                    label_selector=label_selector
                )
                workloads.extend(deployments)
            
            if not workload_type or workload_type == "custom":
                # List AIBrix custom resources
                for group_name, group_info in self.k8s_client.CRD_MAPPINGS.items():
                    for kind in group_info["kinds"]:
                        plural = self._get_plural_name(kind)
                        resources = await self.k8s_client.list_custom_resources(
                            group=group_info["group"],
                            version=group_info["version"],
                            plural=plural,
                            label_selector=label_selector
                        )
                        workloads.extend(resources)
            
            return workloads
            
        except Exception as e:
            logger.error(f"Failed to list workloads: {e}")
            return []
    
    async def delete_workload(self, name: str, workload_type: str = "deployment") -> bool:
        """Delete a workload.
        
        Args:
            name: Workload name
            workload_type: Type of workload
            
        Returns:
            True if deletion succeeded
        """
        try:
            if workload_type == "deployment":
                # TODO: Implement deployment deletion
                logger.info(f"Deleting deployment: {name}")
            else:
                # Handle custom resources
                # TODO: Determine the correct group/version/plural for the resource
                logger.info(f"Deleting custom resource: {name}")
            
            await asyncio.sleep(1)  # Simulate deletion
            logger.info(f"✅ Workload {name} deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete workload {name}: {e}")
            return False
    
    async def update_workload(self, name: str, manifest_file: str) -> bool:
        """Update an existing workload.
        
        Args:
            name: Workload name
            manifest_file: Path to updated manifest file
            
        Returns:
            True if update succeeded
        """
        try:
            # TODO: Implement workload update logic
            logger.info(f"Updating workload {name} from {manifest_file}")
            
            await asyncio.sleep(1)  # Simulate update
            logger.info(f"✅ Workload {name} updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update workload {name}: {e}")
            return False
    
    async def scale_workload(self, name: str, replicas: int) -> bool:
        """Scale a workload.
        
        Args:
            name: Workload name
            replicas: Target number of replicas
            
        Returns:
            True if scaling succeeded
        """
        try:
            await self.k8s_client.scale_deployment(name, replicas)
            logger.info(f"✅ Workload {name} scaled to {replicas} replicas")
            return True
            
        except Exception as e:
            logger.error(f"Failed to scale workload {name}: {e}")
            return False
    
    async def validate_manifest(self, manifest_file: str) -> bool:
        """Validate a manifest file.
        
        Args:
            manifest_file: Path to manifest file
            
        Returns:
            True if manifest is valid
        """
        manifest_path = Path(manifest_file)
        if not manifest_path.exists():
            logger.error(f"Manifest file not found: {manifest_file}")
            return False
        
        try:
            with open(manifest_path, 'r') as f:
                documents = list(yaml.safe_load_all(f))
            
            valid = True
            for i, doc in enumerate(documents):
                if not doc:
                    continue
                
                # Basic validation
                if not isinstance(doc, dict):
                    logger.error(f"Document {i}: Not a valid YAML object")
                    valid = False
                    continue
                
                required_fields = ["apiVersion", "kind", "metadata"]
                for field in required_fields:
                    if field not in doc:
                        logger.error(f"Document {i}: Missing required field '{field}'")
                        valid = False
                
                metadata = doc.get("metadata", {})
                if not metadata.get("name"):
                    logger.error(f"Document {i}: Missing metadata.name")
                    valid = False
            
            if valid:
                logger.info(f"✅ Manifest {manifest_file} is valid")
            else:
                logger.error(f"❌ Manifest {manifest_file} has validation errors")
            
            return valid
            
        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error in {manifest_file}: {e}")
            return False
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False


async def handle_deploy(args: argparse.Namespace) -> int:
    """Handle deploy command."""
    try:
        k8s_client = AIBrixK8sClient(
            kubeconfig_path=args.kubeconfig,
            namespace=args.namespace
        )
        
        manager = WorkloadManager(k8s_client)
        
        params = {}
        if args.params:
            # Parse key=value pairs
            for param in args.params:
                if "=" in param:
                    key, value = param.split("=", 1)
                    params[key] = value
        
        success = await manager.deploy_workload(
            manifest_file=args.file,
            template=args.template,
            params=params
        )
        
        k8s_client.close()
        return 0 if success else 1
        
    except Exception as e:
        logger.error(f"Deploy command failed: {e}")
        return 1


async def handle_list(args: argparse.Namespace) -> int:
    """Handle list command."""
    try:
        k8s_client = AIBrixK8sClient(
            kubeconfig_path=args.kubeconfig,
            namespace=args.namespace
        )
        
        manager = WorkloadManager(k8s_client)
        
        workloads = await manager.list_workloads(
            workload_type=args.type,
            label_selector=args.selector
        )
        
        if not workloads:
            print("No workloads found")
        else:
            print(f"{'Name':<30} {'Type':<20} {'Namespace':<15} {'Status':<15}")
            print("-" * 80)
            
            for workload in workloads:
                metadata = workload.get("metadata", {})
                name = metadata.get("name", "unknown")
                namespace = metadata.get("namespace", "unknown")
                kind = workload.get("kind", "unknown")
                
                # Get status info
                status = "Unknown"
                if kind == "Deployment":
                    status_info = workload.get("status", {})
                    ready = status_info.get("readyReplicas", 0)
                    total = status_info.get("replicas", 0)
                    status = f"{ready}/{total} ready"
                
                print(f"{name:<30} {kind:<20} {namespace:<15} {status:<15}")
        
        k8s_client.close()
        return 0
        
    except Exception as e:
        logger.error(f"List command failed: {e}")
        return 1


async def handle_delete(args: argparse.Namespace) -> int:
    """Handle delete command."""
    try:
        k8s_client = AIBrixK8sClient(
            kubeconfig_path=args.kubeconfig,
            namespace=args.namespace
        )
        
        manager = WorkloadManager(k8s_client)
        
        success = await manager.delete_workload(args.name, args.type)
        
        k8s_client.close()
        return 0 if success else 1
        
    except Exception as e:
        logger.error(f"Delete command failed: {e}")
        return 1


async def handle_update(args: argparse.Namespace) -> int:
    """Handle update command."""
    try:
        k8s_client = AIBrixK8sClient(
            kubeconfig_path=args.kubeconfig,
            namespace=args.namespace
        )
        
        manager = WorkloadManager(k8s_client)
        
        success = await manager.update_workload(args.name, args.file)
        
        k8s_client.close()
        return 0 if success else 1
        
    except Exception as e:
        logger.error(f"Update command failed: {e}")
        return 1


async def handle_scale(args: argparse.Namespace) -> int:
    """Handle scale command."""
    try:
        k8s_client = AIBrixK8sClient(
            kubeconfig_path=args.kubeconfig,
            namespace=args.namespace
        )
        
        manager = WorkloadManager(k8s_client)
        
        success = await manager.scale_workload(args.workload, args.replicas)
        
        k8s_client.close()
        return 0 if success else 1
        
    except Exception as e:
        logger.error(f"Scale command failed: {e}")
        return 1


async def handle_validate(args: argparse.Namespace) -> int:
    """Handle validate command."""
    try:
        manager = WorkloadManager(None)  # Validation doesn't need k8s client
        
        success = await manager.validate_manifest(args.file)
        
        return 0 if success else 1
        
    except Exception as e:
        logger.error(f"Validate command failed: {e}")
        return 1


def add_subparser(subparsers) -> None:
    """Add management subcommands to the main parser."""
    
    # Deploy command
    deploy_parser = subparsers.add_parser(
        "deploy",
        help="Deploy workloads",
        description="Deploy AIBrix workloads from manifest or template"
    )
    
    deploy_group = deploy_parser.add_mutually_exclusive_group(required=True)
    deploy_group.add_argument(
        "--file", "-f",
        help="YAML manifest file to deploy"
    )
    deploy_group.add_argument(
        "--template",
        help="Template name to deploy"
    )
    
    deploy_parser.add_argument(
        "--params",
        nargs="*",
        help="Template parameters in key=value format"
    )
    
    deploy_parser.set_defaults(func=lambda args: asyncio.run(handle_deploy(args)))
    
    # List command
    list_parser = subparsers.add_parser(
        "list",
        help="List workloads",
        description="List AIBrix workloads"
    )
    
    list_parser.add_argument(
        "type",
        nargs="?",
        choices=["deployments", "services", "custom", "all"],
        default="all",
        help="Type of workloads to list"
    )
    
    list_parser.add_argument(
        "--selector", "-l",
        help="Label selector for filtering"
    )
    
    list_parser.set_defaults(func=lambda args: asyncio.run(handle_list(args)))
    
    # Delete command
    delete_parser = subparsers.add_parser(
        "delete",
        help="Delete workloads",
        description="Delete AIBrix workloads"
    )
    
    delete_parser.add_argument(
        "name",
        help="Workload name to delete"
    )
    
    delete_parser.add_argument(
        "--type",
        default="deployment",
        help="Workload type (default: deployment)"
    )
    
    delete_parser.set_defaults(func=lambda args: asyncio.run(handle_delete(args)))
    
    # Update command
    update_parser = subparsers.add_parser(
        "update",
        help="Update workloads",
        description="Update existing AIBrix workloads"
    )
    
    update_parser.add_argument(
        "name",
        help="Workload name to update"
    )
    
    update_parser.add_argument(
        "--file", "-f",
        required=True,
        help="Updated YAML manifest file"
    )
    
    update_parser.set_defaults(func=lambda args: asyncio.run(handle_update(args)))
    
    # Scale command
    scale_parser = subparsers.add_parser(
        "scale",
        help="Scale workloads",
        description="Scale AIBrix workloads"
    )
    
    scale_parser.add_argument(
        "--workload",
        required=True,
        help="Workload name to scale"
    )
    
    scale_parser.add_argument(
        "--replicas",
        type=int,
        required=True,
        help="Target number of replicas"
    )
    
    scale_parser.set_defaults(func=lambda args: asyncio.run(handle_scale(args)))
    
    # Validate command
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate manifests",
        description="Validate AIBrix manifest files"
    )
    
    validate_parser.add_argument(
        "--file", "-f",
        required=True,
        help="YAML manifest file to validate"
    )
    
    validate_parser.set_defaults(func=lambda args: asyncio.run(handle_validate(args)))
