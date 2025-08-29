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

"""Kubernetes client wrapper for AIBrix CRD operations."""

import os
import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass

try:
    from kubernetes import client, config
    from kubernetes.client.rest import ApiException
    from kubernetes.client.exceptions import ApiException as ClientApiException
except ImportError:
    raise ImportError(
        "kubernetes package is required for CLI operations. "
        "Install it with: pip install kubernetes"
    )

from ..logger import init_logger

logger = init_logger(__name__)


@dataclass
class KubernetesResource:
    """Represents a Kubernetes resource with metadata."""
    api_version: str
    kind: str
    metadata: Dict[str, Any]
    spec: Dict[str, Any]
    status: Optional[Dict[str, Any]] = None


class AIBrixK8sClient:
    """Kubernetes client wrapper for AIBrix operations."""
    
    # AIBrix CRD mappings
    CRD_MAPPINGS = {
        "autoscaling": {
            "group": "autoscaling.aibrix.ai",
            "version": "v1alpha1",
            "kinds": ["PodAutoscaler"]
        },
        "model": {
            "group": "model.aibrix.ai", 
            "version": "v1alpha1",
            "kinds": ["ModelAdapter"]
        },
        "orchestration": {
            "group": "orchestration.aibrix.ai",
            "version": "v1alpha1",
            "kinds": ["StormService", "KVCache", "RayClusterFleet", "RayClusterReplicaSet", "RoleSet"]
        }
    }
    
    def __init__(self, kubeconfig_path: Optional[str] = None, namespace: str = "default"):
        """Initialize the Kubernetes client.
        
        Args:
            kubeconfig_path: Path to kubeconfig file. If None, uses default location.
            namespace: Default namespace for operations.
        """
        self.namespace = namespace
        self._api_client = None
        self._core_v1 = None
        self._apps_v1 = None
        self._custom_objects_api = None
        self._configure_client(kubeconfig_path)
    
    def _configure_client(self, kubeconfig_path: Optional[str]) -> None:
        """Configure the Kubernetes client with authentication."""
        try:
            # Try to load from cluster first (in-cluster config)
            if os.getenv("KUBERNETES_SERVICE_HOST"):
                config.load_incluster_config()
                logger.debug("Loaded in-cluster Kubernetes config")
            else:
                # Load from kubeconfig file
                if kubeconfig_path:
                    config.load_kube_config(config_file=kubeconfig_path)
                else:
                    config.load_kube_config()
                logger.debug("Loaded Kubernetes config from kubeconfig file")
            
            # Initialize API clients
            self._api_client = client.ApiClient()
            self._core_v1 = client.CoreV1Api()
            self._apps_v1 = client.AppsV1Api()
            self._custom_objects_api = client.CustomObjectsApi()
            
        except Exception as e:
            raise RuntimeError(f"Failed to configure Kubernetes client: {e}")
    
    async def test_connection(self) -> bool:
        """Test the connection to Kubernetes cluster.
        
        Returns:
            True if connection is successful, False otherwise.
        """
        try:
            # Test connection by listing namespaces (simple API call)
            await asyncio.to_thread(self._core_v1.list_namespace)
            logger.debug("Kubernetes connection test successful")
            return True
        except Exception as e:
            logger.error(f"Kubernetes connection test failed: {e}")
            return False
    
    async def list_namespaces(self) -> List[str]:
        """List all available namespaces.
        
        Returns:
            List of namespace names.
        """
        try:
            response = await asyncio.to_thread(self._core_v1.list_namespace)
            return [ns.metadata.name for ns in response.items]
        except ApiException as e:
            logger.error(f"Failed to list namespaces: {e}")
            raise
    
    async def create_custom_resource(
        self,
        group: str,
        version: str,
        plural: str,
        body: Dict[str, Any],
        namespace: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a custom resource.
        
        Args:
            group: API group of the custom resource
            version: API version
            plural: Plural name of the resource
            body: Resource specification
            namespace: Namespace to create in (uses default if None)
            
        Returns:
            Created resource object
        """
        ns = namespace or self.namespace
        try:
            response = await asyncio.to_thread(
                self._custom_objects_api.create_namespaced_custom_object,
                group=group,
                version=version,
                namespace=ns,
                plural=plural,
                body=body
            )
            logger.debug(f"Created {group}/{version}/{plural}: {body.get('metadata', {}).get('name', 'unknown')}")
            return response
        except ApiException as e:
            logger.error(f"Failed to create custom resource: {e}")
            raise
    
    async def get_custom_resource(
        self,
        group: str,
        version: str,
        plural: str,
        name: str,
        namespace: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get a custom resource by name.
        
        Args:
            group: API group of the custom resource
            version: API version
            plural: Plural name of the resource
            name: Resource name
            namespace: Namespace to search in (uses default if None)
            
        Returns:
            Resource object
        """
        ns = namespace or self.namespace
        try:
            response = await asyncio.to_thread(
                self._custom_objects_api.get_namespaced_custom_object,
                group=group,
                version=version,
                namespace=ns,
                plural=plural,
                name=name
            )
            return response
        except ApiException as e:
            if e.status == 404:
                logger.warning(f"Custom resource not found: {name}")
                return None
            logger.error(f"Failed to get custom resource: {e}")
            raise
    
    async def list_custom_resources(
        self,
        group: str,
        version: str,
        plural: str,
        namespace: Optional[str] = None,
        label_selector: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List custom resources.
        
        Args:
            group: API group of the custom resource
            version: API version
            plural: Plural name of the resource
            namespace: Namespace to search in (uses default if None)
            label_selector: Label selector for filtering
            
        Returns:
            List of resource objects
        """
        ns = namespace or self.namespace
        try:
            kwargs = {
                "group": group,
                "version": version,
                "namespace": ns,
                "plural": plural
            }
            if label_selector:
                kwargs["label_selector"] = label_selector
                
            response = await asyncio.to_thread(
                self._custom_objects_api.list_namespaced_custom_object,
                **kwargs
            )
            return response.get("items", [])
        except ApiException as e:
            logger.error(f"Failed to list custom resources: {e}")
            raise
    
    async def update_custom_resource(
        self,
        group: str,
        version: str,
        plural: str,
        name: str,
        body: Dict[str, Any],
        namespace: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update a custom resource.
        
        Args:
            group: API group of the custom resource
            version: API version
            plural: Plural name of the resource
            name: Resource name
            body: Updated resource specification
            namespace: Namespace (uses default if None)
            
        Returns:
            Updated resource object
        """
        ns = namespace or self.namespace
        try:
            response = await asyncio.to_thread(
                self._custom_objects_api.patch_namespaced_custom_object,
                group=group,
                version=version,
                namespace=ns,
                plural=plural,
                name=name,
                body=body
            )
            logger.debug(f"Updated {group}/{version}/{plural}: {name}")
            return response
        except ApiException as e:
            logger.error(f"Failed to update custom resource: {e}")
            raise
    
    async def delete_custom_resource(
        self,
        group: str,
        version: str,
        plural: str,
        name: str,
        namespace: Optional[str] = None
    ) -> bool:
        """Delete a custom resource.
        
        Args:
            group: API group of the custom resource
            version: API version
            plural: Plural name of the resource
            name: Resource name
            namespace: Namespace (uses default if None)
            
        Returns:
            True if deleted successfully
        """
        ns = namespace or self.namespace
        try:
            await asyncio.to_thread(
                self._custom_objects_api.delete_namespaced_custom_object,
                group=group,
                version=version,
                namespace=ns,
                plural=plural,
                name=name
            )
            logger.debug(f"Deleted {group}/{version}/{plural}: {name}")
            return True
        except ApiException as e:
            if e.status == 404:
                logger.warning(f"Custom resource not found for deletion: {name}")
                return False
            logger.error(f"Failed to delete custom resource: {e}")
            raise
    
    async def list_deployments(
        self,
        namespace: Optional[str] = None,
        label_selector: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List deployments in namespace.
        
        Args:
            namespace: Namespace to search in (uses default if None)
            label_selector: Label selector for filtering
            
        Returns:
            List of deployment objects
        """
        ns = namespace or self.namespace
        try:
            kwargs = {"namespace": ns}
            if label_selector:
                kwargs["label_selector"] = label_selector
                
            response = await asyncio.to_thread(
                self._apps_v1.list_namespaced_deployment,
                **kwargs
            )
            return [self._deployment_to_dict(dep) for dep in response.items]
        except ApiException as e:
            logger.error(f"Failed to list deployments: {e}")
            raise
    
    async def get_deployment(self, name: str, namespace: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get deployment by name.
        
        Args:
            name: Deployment name
            namespace: Namespace (uses default if None)
            
        Returns:
            Deployment object or None if not found
        """
        ns = namespace or self.namespace
        try:
            response = await asyncio.to_thread(
                self._apps_v1.read_namespaced_deployment,
                name=name,
                namespace=ns
            )
            return self._deployment_to_dict(response)
        except ApiException as e:
            if e.status == 404:
                return None
            logger.error(f"Failed to get deployment: {e}")
            raise
    
    async def scale_deployment(
        self,
        name: str,
        replicas: int,
        namespace: Optional[str] = None
    ) -> Dict[str, Any]:
        """Scale a deployment.
        
        Args:
            name: Deployment name
            replicas: Target number of replicas
            namespace: Namespace (uses default if None)
            
        Returns:
            Updated deployment object
        """
        ns = namespace or self.namespace
        try:
            # Get current deployment
            deployment = await asyncio.to_thread(
                self._apps_v1.read_namespaced_deployment,
                name=name,
                namespace=ns
            )
            
            # Update replicas
            deployment.spec.replicas = replicas
            
            # Apply the update
            response = await asyncio.to_thread(
                self._apps_v1.patch_namespaced_deployment,
                name=name,
                namespace=ns,
                body=deployment
            )
            
            logger.info(f"Scaled deployment {name} to {replicas} replicas")
            return self._deployment_to_dict(response)
            
        except ApiException as e:
            logger.error(f"Failed to scale deployment: {e}")
            raise
    
    async def get_pod_logs(
        self,
        pod_name: str,
        namespace: Optional[str] = None,
        container: Optional[str] = None,
        tail_lines: Optional[int] = None,
        follow: bool = False
    ) -> str:
        """Get logs from a pod.
        
        Args:
            pod_name: Pod name
            namespace: Namespace (uses default if None)
            container: Container name (if pod has multiple containers)
            tail_lines: Number of lines to tail
            follow: Whether to follow/stream logs
            
        Returns:
            Log content as string
        """
        ns = namespace or self.namespace
        try:
            kwargs = {
                "name": pod_name,
                "namespace": ns,
                "follow": follow
            }
            if container:
                kwargs["container"] = container
            if tail_lines:
                kwargs["tail_lines"] = tail_lines
                
            response = await asyncio.to_thread(
                self._core_v1.read_namespaced_pod_log,
                **kwargs
            )
            return response
        except ApiException as e:
            logger.error(f"Failed to get pod logs: {e}")
            raise
    
    def _deployment_to_dict(self, deployment) -> Dict[str, Any]:
        """Convert deployment object to dictionary."""
        return {
            "apiVersion": deployment.api_version,
            "kind": deployment.kind,
            "metadata": {
                "name": deployment.metadata.name,
                "namespace": deployment.metadata.namespace,
                "labels": deployment.metadata.labels or {},
                "creationTimestamp": deployment.metadata.creation_timestamp.isoformat() if deployment.metadata.creation_timestamp else None
            },
            "spec": {
                "replicas": deployment.spec.replicas,
                "selector": deployment.spec.selector.match_labels if deployment.spec.selector else {}
            },
            "status": {
                "readyReplicas": deployment.status.ready_replicas or 0,
                "replicas": deployment.status.replicas or 0,
                "unavailableReplicas": deployment.status.unavailable_replicas or 0
            }
        }
    
    def close(self) -> None:
        """Close the API client connection."""
        if self._api_client:
            self._api_client.close()
