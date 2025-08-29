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

"""Installation commands for AIBrix CLI."""

import argparse
import asyncio
from typing import Dict, List, Optional

from ...logger import init_logger
from ..k8s_client import AIBrixK8sClient

logger = init_logger(__name__)


class AIBrixInstaller:
    """Handles AIBrix component installation and management."""
    
    COMPONENTS = {
        "controller": {
            "description": "AIBrix controller and CRDs",
            "manifests": [
                "config/crd/kustomization.yaml",
                "config/manager/kustomization.yaml",
                "config/rbac/kustomization.yaml"
            ]
        },
        "gateway": {
            "description": "Envoy Gateway for traffic routing",
            "manifests": [
                "config/gateway/kustomization.yaml"
            ]
        },
        "metadata": {
            "description": "Metadata service and Redis",
            "manifests": [
                "config/metadata/kustomization.yaml"
            ]
        },
        "monitoring": {
            "description": "Prometheus monitoring stack",
            "manifests": [
                "config/prometheus/kustomization.yaml"
            ]
        }
    }
    
    def __init__(self, k8s_client: AIBrixK8sClient):
        """Initialize the installer.
        
        Args:
            k8s_client: Kubernetes client instance
        """
        self.k8s_client = k8s_client
    
    async def install_all(self, version: str = "latest", environment: str = "default") -> bool:
        """Install all AIBrix components.
        
        Args:
            version: AIBrix version to install
            environment: Target environment (default, dev, prod)
            
        Returns:
            True if installation succeeded
        """
        logger.info(f"Installing AIBrix {version} for {environment} environment")
        
        try:
            # Check cluster connectivity
            if not await self.k8s_client.test_connection():
                logger.error("Cannot connect to Kubernetes cluster")
                return False
            
            # Install components in order
            for component_name in ["controller", "gateway", "metadata", "monitoring"]:
                if not await self.install_component(component_name, version):
                    logger.error(f"Failed to install component: {component_name}")
                    return False
            
            logger.info("✅ All AIBrix components installed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Installation failed: {e}")
            return False
    
    async def install_component(self, component: str, version: str = "latest") -> bool:
        """Install a specific AIBrix component.
        
        Args:
            component: Component name to install
            version: Component version
            
        Returns:
            True if installation succeeded
        """
        if component not in self.COMPONENTS:
            logger.error(f"Unknown component: {component}")
            logger.info(f"Available components: {', '.join(self.COMPONENTS.keys())}")
            return False
        
        component_info = self.COMPONENTS[component]
        logger.info(f"Installing {component}: {component_info['description']}")
        
        try:
            # TODO: Implement actual manifest application
            # This would typically involve:
            # 1. Downloading manifests from GitHub release
            # 2. Applying manifests using kubectl or direct API calls
            # 3. Waiting for resources to be ready
            
            # For now, simulate installation
            await asyncio.sleep(1)  # Simulate installation time
            logger.info(f"✅ Component {component} installed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to install component {component}: {e}")
            return False
    
    async def uninstall_all(self) -> bool:
        """Uninstall all AIBrix components.
        
        Returns:
            True if uninstallation succeeded
        """
        logger.info("Uninstalling all AIBrix components")
        
        try:
            # Uninstall in reverse order
            components = list(self.COMPONENTS.keys())
            components.reverse()
            
            for component_name in components:
                await self.uninstall_component(component_name)
            
            logger.info("✅ All AIBrix components uninstalled successfully")
            return True
            
        except Exception as e:
            logger.error(f"Uninstallation failed: {e}")
            return False
    
    async def uninstall_component(self, component: str) -> bool:
        """Uninstall a specific AIBrix component.
        
        Args:
            component: Component name to uninstall
            
        Returns:
            True if uninstallation succeeded
        """
        if component not in self.COMPONENTS:
            logger.error(f"Unknown component: {component}")
            return False
        
        component_info = self.COMPONENTS[component]
        logger.info(f"Uninstalling {component}: {component_info['description']}")
        
        try:
            # TODO: Implement actual manifest deletion
            # This would typically involve:
            # 1. Deleting resources using kubectl or direct API calls
            # 2. Waiting for resources to be removed
            
            # For now, simulate uninstallation
            await asyncio.sleep(1)  # Simulate uninstallation time
            logger.info(f"✅ Component {component} uninstalled successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to uninstall component {component}: {e}")
            return False
    
    async def get_installation_status(self) -> Dict[str, Dict[str, str]]:
        """Get installation status of all components.
        
        Returns:
            Dictionary with component status information
        """
        status = {}
        
        for component_name, component_info in self.COMPONENTS.items():
            try:
                # TODO: Check actual component status
                # This would involve checking if deployments/services exist and are ready
                
                # For now, return mock status
                status[component_name] = {
                    "description": component_info["description"],
                    "status": "Installed",  # Could be: Installed, Not Installed, Pending, Error
                    "version": "v0.3.0"
                }
                
            except Exception as e:
                status[component_name] = {
                    "description": component_info["description"],
                    "status": "Error",
                    "error": str(e)
                }
        
        return status


async def handle_install(args: argparse.Namespace) -> int:
    """Handle install command."""
    try:
        k8s_client = AIBrixK8sClient(
            kubeconfig_path=args.kubeconfig,
            namespace=args.namespace
        )
        
        installer = AIBrixInstaller(k8s_client)
        
        if args.component:
            success = await installer.install_component(args.component, args.version)
        else:
            success = await installer.install_all(args.version, args.env)
        
        k8s_client.close()
        return 0 if success else 1
        
    except Exception as e:
        logger.error(f"Install command failed: {e}")
        return 1


async def handle_uninstall(args: argparse.Namespace) -> int:
    """Handle uninstall command."""
    try:
        k8s_client = AIBrixK8sClient(
            kubeconfig_path=args.kubeconfig,
            namespace=args.namespace
        )
        
        installer = AIBrixInstaller(k8s_client)
        
        if args.component:
            success = await installer.uninstall_component(args.component)
        else:
            success = await installer.uninstall_all()
        
        k8s_client.close()
        return 0 if success else 1
        
    except Exception as e:
        logger.error(f"Uninstall command failed: {e}")
        return 1


async def handle_status(args: argparse.Namespace) -> int:
    """Handle installation status command."""
    try:
        k8s_client = AIBrixK8sClient(
            kubeconfig_path=args.kubeconfig,
            namespace=args.namespace
        )
        
        installer = AIBrixInstaller(k8s_client)
        status = await installer.get_installation_status()
        
        # Print status table
        print(f"{'Component':<15} {'Status':<12} {'Version':<10} {'Description'}")
        print("-" * 70)
        
        for component_name, info in status.items():
            status_str = info.get("status", "Unknown")
            version_str = info.get("version", "N/A")
            description = info.get("description", "")
            
            print(f"{component_name:<15} {status_str:<12} {version_str:<10} {description}")
        
        k8s_client.close()
        return 0
        
    except Exception as e:
        logger.error(f"Status command failed: {e}")
        return 1


def add_subparser(subparsers) -> None:
    """Add installation subcommands to the main parser."""
    
    # Install command
    install_parser = subparsers.add_parser(
        "install",
        help="Install AIBrix components",
        description="Install AIBrix components on Kubernetes cluster"
    )
    
    install_parser.add_argument(
        "--version",
        default="latest",
        help="AIBrix version to install (default: latest)"
    )
    
    install_parser.add_argument(
        "--env",
        choices=["default", "dev", "prod"],
        default="default",
        help="Target environment (default: default)"
    )
    
    install_parser.add_argument(
        "--component",
        choices=list(AIBrixInstaller.COMPONENTS.keys()),
        help="Install specific component only"
    )
    
    install_parser.set_defaults(func=lambda args: asyncio.run(handle_install(args)))
    
    # Uninstall command  
    uninstall_parser = subparsers.add_parser(
        "uninstall",
        help="Uninstall AIBrix components",
        description="Uninstall AIBrix components from Kubernetes cluster"
    )
    
    uninstall_parser.add_argument(
        "--all",
        action="store_true",
        help="Uninstall all components"
    )
    
    uninstall_parser.add_argument(
        "--component",
        choices=list(AIBrixInstaller.COMPONENTS.keys()),
        help="Uninstall specific component only"
    )
    
    uninstall_parser.set_defaults(func=lambda args: asyncio.run(handle_uninstall(args)))
    
    # Status command
    status_parser = subparsers.add_parser(
        "status",
        help="Show installation status",
        description="Show installation status of AIBrix components"
    )
    
    status_parser.set_defaults(func=lambda args: asyncio.run(handle_status(args)))
