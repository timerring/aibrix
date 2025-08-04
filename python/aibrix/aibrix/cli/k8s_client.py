"""
Kubernetes Client Wrapper for AIBrix CLI

Provides a simplified interface for Kubernetes operations.
"""

import logging
from typing import Dict, List, Optional, Any
from kubernetes import client, config
from kubernetes.client.rest import ApiException

logger = logging.getLogger(__name__)


class AIBrixK8sClient:
    """Kubernetes client wrapper for AIBrix operations."""
    
    def __init__(self, kubeconfig: Optional[str] = None, context: Optional[str] = None):
        """Initialize the Kubernetes client.
        
        Args:
            kubeconfig: Path to kubeconfig file
            context: Kubernetes context to use
        """
        try:
            if kubeconfig:
                config.load_kube_config(config_file=kubeconfig, context=context)
            else:
                config.load_kube_config(context=context)
            
            self.core_v1 = client.CoreV1Api()
            self.apps_v1 = client.AppsV1Api()
            self.custom_objects = client.CustomObjectsApi()
            
            # AIBrix CRD API groups
            self.orchestration_group = "orchestration.aibrix.ai"
            self.model_group = "model.aibrix.ai"
            self.autoscaling_group = "autoscaling.aibrix.ai"
            
        except Exception as e:
            logger.error(f"Failed to initialize Kubernetes client: {e}")
            raise
    
    def list_stormservices(self, namespace: str = "default") -> List[Dict[str, Any]]:
        """List all StormService resources.
        
        Args:
            namespace: Kubernetes namespace
            
        Returns:
            List of StormService resources
        """
        try:
            response = self.custom_objects.list_namespaced_custom_object(
                group=self.orchestration_group,
                version="v1alpha1",
                namespace=namespace,
                plural="stormservices"
            )
            return response.get("items", [])
        except ApiException as e:
            logger.error(f"Failed to list StormServices: {e}")
            return []
    
    def get_stormservice(self, name: str, namespace: str = "default") -> Optional[Dict[str, Any]]:
        """Get a specific StormService resource.
        
        Args:
            name: StormService name
            namespace: Kubernetes namespace
            
        Returns:
            StormService resource or None if not found
        """
        try:
            return self.custom_objects.get_namespaced_custom_object(
                group=self.orchestration_group,
                version="v1alpha1",
                namespace=namespace,
                plural="stormservices",
                name=name
            )
        except ApiException as e:
            if e.status == 404:
                return None
            logger.error(f"Failed to get StormService {name}: {e}")
            return None
    
    def create_stormservice(self, body: Dict[str, Any], namespace: str = "default") -> Dict[str, Any]:
        """Create a new StormService resource.
        
        Args:
            body: StormService resource definition
            namespace: Kubernetes namespace
            
        Returns:
            Created StormService resource
        """
        try:
            return self.custom_objects.create_namespaced_custom_object(
                group=self.orchestration_group,
                version="v1alpha1",
                namespace=namespace,
                plural="stormservices",
                body=body
            )
        except ApiException as e:
            logger.error(f"Failed to create StormService: {e}")
            raise
    
    def update_stormservice(self, name: str, body: Dict[str, Any], namespace: str = "default") -> Dict[str, Any]:
        """Update an existing StormService resource.
        
        Args:
            name: StormService name
            body: Updated StormService resource definition
            namespace: Kubernetes namespace
            
        Returns:
            Updated StormService resource
        """
        try:
            return self.custom_objects.replace_namespaced_custom_object(
                group=self.orchestration_group,
                version="v1alpha1",
                namespace=namespace,
                plural="stormservices",
                name=name,
                body=body
            )
        except ApiException as e:
            logger.error(f"Failed to update StormService {name}: {e}")
            raise
    
    def delete_stormservice(self, name: str, namespace: str = "default") -> bool:
        """Delete a StormService resource.
        
        Args:
            name: StormService name
            namespace: Kubernetes namespace
            
        Returns:
            True if deleted successfully
        """
        try:
            self.custom_objects.delete_namespaced_custom_object(
                group=self.orchestration_group,
                version="v1alpha1",
                namespace=namespace,
                plural="stormservices",
                name=name
            )
            return True
        except ApiException as e:
            logger.error(f"Failed to delete StormService {name}: {e}")
            return False
    
    def scale_stormservice(self, name: str, replicas: int, namespace: str = "default") -> Dict[str, Any]:
        """Scale a StormService resource.
        
        Args:
            name: StormService name
            replicas: Number of replicas
            namespace: Kubernetes namespace
            
        Returns:
            Updated StormService resource
        """
        try:
            # Get current resource
            current = self.get_stormservice(name, namespace)
            if not current:
                raise ValueError(f"StormService {name} not found")
            
            # Update replicas
            current["spec"]["replicas"] = replicas
            
            return self.update_stormservice(name, current, namespace)
        except Exception as e:
            logger.error(f"Failed to scale StormService {name}: {e}")
            raise
    
    def list_pods(self, namespace: str = "default", label_selector: Optional[str] = None) -> List[Dict[str, Any]]:
        """List pods in a namespace.
        
        Args:
            namespace: Kubernetes namespace
            label_selector: Label selector for filtering
            
        Returns:
            List of pod resources
        """
        try:
            response = self.core_v1.list_namespaced_pod(
                namespace=namespace,
                label_selector=label_selector
            )
            return [pod.to_dict() for pod in response.items]
        except ApiException as e:
            logger.error(f"Failed to list pods: {e}")
            return []
    
    def get_pod_logs(self, name: str, namespace: str = "default", container: Optional[str] = None, 
                    tail_lines: Optional[int] = None, follow: bool = False) -> str:
        """Get logs from a pod.
        
        Args:
            name: Pod name
            namespace: Kubernetes namespace
            container: Container name (if multi-container pod)
            tail_lines: Number of lines to return
            follow: Whether to follow logs
            
        Returns:
            Pod logs
        """
        try:
            return self.core_v1.read_namespaced_pod_log(
                name=name,
                namespace=namespace,
                container=container,
                tail_lines=tail_lines,
                follow=follow
            )
        except ApiException as e:
            logger.error(f"Failed to get logs for pod {name}: {e}")
            return ""
    
    def port_forward(self, name: str, ports: List[str], namespace: str = "default") -> None:
        """Port forward to a pod or service.
        
        Args:
            name: Pod or service name
            ports: List of port mappings (e.g., ["8888:80"])
            namespace: Kubernetes namespace
        """
        # This would require implementing port forwarding logic
        # For now, we'll provide guidance on using kubectl
        port_mappings = " ".join([f"--address=0.0.0.0 {port}" for port in ports])
        print(f"To port forward, run: kubectl port-forward {name} {port_mappings} -n {namespace}")
    
    def get_service_endpoints(self, name: str, namespace: str = "default") -> List[Dict[str, Any]]:
        """Get endpoints for a service.
        
        Args:
            name: Service name
            namespace: Kubernetes namespace
            
        Returns:
            List of endpoint resources
        """
        try:
            response = self.core_v1.list_namespaced_endpoints(
                namespace=namespace,
                field_selector=f"metadata.name={name}"
            )
            return [endpoint.to_dict() for endpoint in response.items]
        except ApiException as e:
            logger.error(f"Failed to get endpoints for service {name}: {e}")
            return []
    
    def check_namespace_exists(self, namespace: str) -> bool:
        """Check if a namespace exists.
        
        Args:
            namespace: Namespace name
            
        Returns:
            True if namespace exists
        """
        try:
            self.core_v1.read_namespace(name=namespace)
            return True
        except ApiException as e:
            if e.status == 404:
                return False
            logger.error(f"Failed to check namespace {namespace}: {e}")
            return False
    
    def create_namespace(self, name: str) -> bool:
        """Create a namespace.
        
        Args:
            name: Namespace name
            
        Returns:
            True if created successfully
        """
        try:
            namespace = client.V1Namespace(
                metadata=client.V1ObjectMeta(name=name)
            )
            self.core_v1.create_namespace(namespace)
            return True
        except ApiException as e:
            logger.error(f"Failed to create namespace {name}: {e}")
            return False 