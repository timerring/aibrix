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

"""Template management commands for AIBrix CLI."""

import argparse
import asyncio
import json
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional

from ...logger import init_logger

logger = init_logger(__name__)


class TemplateManager:
    """Manages AIBrix workload templates."""
    
    # Built-in templates
    TEMPLATES = {
        "quickstart": {
            "description": "Quick start template for LLM deployment",
            "parameters": {
                "model_name": {
                    "description": "Model name (e.g., deepseek-r1-distill-llama-8b)",
                    "required": True
                },
                "model_path": {
                    "description": "HuggingFace model path",
                    "default": "deepseek-ai/DeepSeek-R1-Distill-Llama-8B"
                },
                "replicas": {
                    "description": "Number of replicas",
                    "default": "1"
                },
                "gpu_count": {
                    "description": "Number of GPUs per replica",
                    "default": "1"
                },
                "max_model_len": {
                    "description": "Maximum model length",
                    "default": "12288"
                }
            }
        },
        "autoscaling": {
            "description": "Template with autoscaling enabled",
            "parameters": {
                "model_name": {
                    "description": "Model name",
                    "required": True
                },
                "model_path": {
                    "description": "HuggingFace model path",
                    "required": True
                },
                "min_replicas": {
                    "description": "Minimum number of replicas",
                    "default": "1"
                },
                "max_replicas": {
                    "description": "Maximum number of replicas", 
                    "default": "10"
                },
                "target_cpu": {
                    "description": "Target CPU utilization for scaling",
                    "default": "70"
                }
            }
        },
        "kvcache": {
            "description": "Template with KV cache disaggregation",
            "parameters": {
                "model_name": {
                    "description": "Model name",
                    "required": True
                },
                "model_path": {
                    "description": "HuggingFace model path",
                    "required": True
                },
                "cache_type": {
                    "description": "Cache type (l1cache, infinistore, vineyard)",
                    "default": "l1cache"
                },
                "cache_size": {
                    "description": "Cache size",
                    "default": "10Gi"
                }
            }
        }
    }
    
    def __init__(self):
        """Initialize the template manager."""
        pass
    
    def list_templates(self) -> Dict[str, Dict[str, Any]]:
        """List available templates.
        
        Returns:
            Dictionary of template names and their information
        """
        return self.TEMPLATES
    
    def get_template_info(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific template.
        
        Args:
            template_name: Name of the template
            
        Returns:
            Template information or None if not found
        """
        return self.TEMPLATES.get(template_name)
    
    def generate_manifest(self, template_name: str, parameters: Dict[str, str]) -> str:
        """Generate manifest from template and parameters.
        
        Args:
            template_name: Name of the template
            parameters: Template parameters
            
        Returns:
            Generated YAML manifest as string
        """
        if template_name not in self.TEMPLATES:
            raise ValueError(f"Unknown template: {template_name}")
        
        template_info = self.TEMPLATES[template_name]
        
        # Validate required parameters
        for param_name, param_info in template_info["parameters"].items():
            if param_info.get("required", False) and param_name not in parameters:
                raise ValueError(f"Required parameter missing: {param_name}")
        
        # Set default values for missing parameters
        for param_name, param_info in template_info["parameters"].items():
            if param_name not in parameters and "default" in param_info:
                parameters[param_name] = param_info["default"]
        
        # Generate manifest based on template
        if template_name == "quickstart":
            return self._generate_quickstart_manifest(parameters)
        elif template_name == "autoscaling":
            return self._generate_autoscaling_manifest(parameters)
        elif template_name == "kvcache":
            return self._generate_kvcache_manifest(parameters)
        else:
            raise ValueError(f"Template generation not implemented: {template_name}")
    
    def _generate_quickstart_manifest(self, params: Dict[str, str]) -> str:
        """Generate quickstart template manifest."""
        manifest = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "labels": {
                    "model.aibrix.ai/name": params["model_name"],
                    "model.aibrix.ai/port": "8000"
                },
                "name": params["model_name"],
                "namespace": "default"
            },
            "spec": {
                "replicas": int(params["replicas"]),
                "selector": {
                    "matchLabels": {
                        "model.aibrix.ai/name": params["model_name"]
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "model.aibrix.ai/name": params["model_name"]
                        }
                    },
                    "spec": {
                        "containers": [
                            {
                                "command": [
                                    "python3",
                                    "-m",
                                    "vllm.entrypoints.openai.api_server",
                                    "--host", "0.0.0.0",
                                    "--port", "8000",
                                    "--uvicorn-log-level", "warning",
                                    "--model", params["model_path"],
                                    "--served-model-name", params["model_name"],
                                    "--max-model-len", params["max_model_len"]
                                ],
                                "image": "vllm/vllm-openai:v0.7.1",
                                "imagePullPolicy": "IfNotPresent",
                                "name": "vllm-openai",
                                "ports": [
                                    {
                                        "containerPort": 8000,
                                        "protocol": "TCP"
                                    }
                                ],
                                "resources": {
                                    "limits": {
                                        "nvidia.com/gpu": params["gpu_count"]
                                    },
                                    "requests": {
                                        "nvidia.com/gpu": params["gpu_count"]
                                    }
                                },
                                "livenessProbe": {
                                    "httpGet": {
                                        "path": "/health",
                                        "port": 8000,
                                        "scheme": "HTTP"
                                    },
                                    "failureThreshold": 3,
                                    "periodSeconds": 5,
                                    "successThreshold": 1,
                                    "timeoutSeconds": 1
                                },
                                "readinessProbe": {
                                    "httpGet": {
                                        "path": "/health",
                                        "port": 8000,
                                        "scheme": "HTTP"
                                    },
                                    "failureThreshold": 5,
                                    "periodSeconds": 5,
                                    "successThreshold": 1,
                                    "timeoutSeconds": 1
                                }
                            }
                        ]
                    }
                }
            }
        }
        
        service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "labels": {
                    "model.aibrix.ai/name": params["model_name"],
                    "prometheus-discovery": "true"
                },
                "annotations": {
                    "prometheus.io/scrape": "true",
                    "prometheus.io/port": "8080"
                },
                "name": params["model_name"],
                "namespace": "default"
            },
            "spec": {
                "ports": [
                    {
                        "name": "serve",
                        "port": 8000,
                        "protocol": "TCP",
                        "targetPort": 8000
                    }
                ],
                "selector": {
                    "model.aibrix.ai/name": params["model_name"]
                },
                "type": "ClusterIP"
            }
        }
        
        # Combine deployment and service
        documents = [manifest, service]
        return yaml.dump_all(documents, default_flow_style=False)
    
    def _generate_autoscaling_manifest(self, params: Dict[str, str]) -> str:
        """Generate autoscaling template manifest."""
        # Start with quickstart manifest
        quickstart_yaml = self._generate_quickstart_manifest(params)
        documents = list(yaml.safe_load_all(quickstart_yaml))
        
        # Add PodAutoscaler
        autoscaler = {
            "apiVersion": "autoscaling.aibrix.ai/v1alpha1",
            "kind": "PodAutoscaler",
            "metadata": {
                "name": f"{params['model_name']}-autoscaler",
                "namespace": "default"
            },
            "spec": {
                "scaleTargetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": params["model_name"]
                },
                "minReplicas": int(params["min_replicas"]),
                "maxReplicas": int(params["max_replicas"]),
                "targetMetric": "CPU",
                "targetValue": params["target_cpu"],
                "scalingStrategy": "HPA"
            }
        }
        
        documents.append(autoscaler)
        return yaml.dump_all(documents, default_flow_style=False)
    
    def _generate_kvcache_manifest(self, params: Dict[str, str]) -> str:
        """Generate KV cache template manifest."""
        # Start with quickstart manifest
        quickstart_yaml = self._generate_quickstart_manifest(params)
        documents = list(yaml.safe_load_all(quickstart_yaml))
        
        # Add KVCache resource
        kvcache = {
            "apiVersion": "orchestration.aibrix.ai/v1alpha1",
            "kind": "KVCache",
            "metadata": {
                "name": f"{params['model_name']}-kvcache",
                "namespace": "default"
            },
            "spec": {
                "cacheType": params["cache_type"],
                "cacheSize": params["cache_size"],
                "targetDeployment": params["model_name"]
            }
        }
        
        documents.append(kvcache)
        return yaml.dump_all(documents, default_flow_style=False)
    
    def validate_parameters(self, template_name: str, parameters: Dict[str, str]) -> List[str]:
        """Validate template parameters.
        
        Args:
            template_name: Name of the template
            parameters: Parameters to validate
            
        Returns:
            List of validation error messages
        """
        errors = []
        
        if template_name not in self.TEMPLATES:
            errors.append(f"Unknown template: {template_name}")
            return errors
        
        template_info = self.TEMPLATES[template_name]
        template_params = template_info["parameters"]
        
        # Check for required parameters
        for param_name, param_info in template_params.items():
            if param_info.get("required", False) and param_name not in parameters:
                errors.append(f"Required parameter missing: {param_name}")
        
        # Validate parameter values
        for param_name, value in parameters.items():
            if param_name not in template_params:
                errors.append(f"Unknown parameter: {param_name}")
                continue
            
            # Basic validation for numeric parameters
            if param_name in ["replicas", "min_replicas", "max_replicas", "gpu_count"]:
                try:
                    int_value = int(value)
                    if int_value < 1:
                        errors.append(f"Parameter {param_name} must be positive integer")
                except ValueError:
                    errors.append(f"Parameter {param_name} must be integer")
        
        return errors


async def handle_list_templates(args: argparse.Namespace) -> int:
    """Handle list templates command."""
    try:
        manager = TemplateManager()
        templates = manager.list_templates()
        
        print(f"{'Template':<15} {'Description'}")
        print("-" * 60)
        
        for name, info in templates.items():
            description = info.get("description", "")
            print(f"{name:<15} {description}")
        
        return 0
        
    except Exception as e:
        logger.error(f"List templates command failed: {e}")
        return 1


async def handle_template_info(args: argparse.Namespace) -> int:
    """Handle template info command."""
    try:
        manager = TemplateManager()
        template_info = manager.get_template_info(args.template)
        
        if not template_info:
            logger.error(f"Template not found: {args.template}")
            return 1
        
        print(f"Template: {args.template}")
        print(f"Description: {template_info.get('description', 'N/A')}")
        print("\\nParameters:")
        
        for param_name, param_info in template_info["parameters"].items():
            required = " (required)" if param_info.get("required", False) else ""
            default = f" [default: {param_info.get('default')}]" if "default" in param_info else ""
            description = param_info.get("description", "")
            
            print(f"  {param_name}{required}{default}")
            if description:
                print(f"    {description}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Template info command failed: {e}")
        return 1


async def handle_generate_template(args: argparse.Namespace) -> int:
    """Handle generate template command."""
    try:
        manager = TemplateManager()
        
        # Parse parameters from command line
        parameters = {}
        if args.params:
            for param in args.params:
                if "=" in param:
                    key, value = param.split("=", 1)
                    parameters[key] = value
                else:
                    logger.error(f"Invalid parameter format: {param} (use key=value)")
                    return 1
        
        # Validate parameters
        errors = manager.validate_parameters(args.template, parameters)
        if errors:
            logger.error("Parameter validation failed:")
            for error in errors:
                logger.error(f"  {error}")
            return 1
        
        # Generate manifest
        manifest = manager.generate_manifest(args.template, parameters)
        
        if args.output:
            # Write to file
            output_path = Path(args.output)
            with open(output_path, 'w') as f:
                f.write(manifest)
            logger.info(f"Manifest written to: {args.output}")
        else:
            # Print to stdout
            print(manifest)
        
        return 0
        
    except Exception as e:
        logger.error(f"Generate template command failed: {e}")
        return 1


def add_subparser(subparsers) -> None:
    """Add template subcommands to the main parser."""
    
    # Templates command group
    templates_parser = subparsers.add_parser(
        "templates",
        help="Manage templates",
        description="Manage AIBrix workload templates"
    )
    
    templates_subparsers = templates_parser.add_subparsers(dest="templates_command")
    
    # List templates command
    list_parser = templates_subparsers.add_parser(
        "list",
        help="List available templates",
        description="List all available AIBrix templates"
    )
    list_parser.set_defaults(func=lambda args: asyncio.run(handle_list_templates(args)))
    
    # Template info command
    info_parser = templates_subparsers.add_parser(
        "info",
        help="Show template information",
        description="Show detailed information about a template"
    )
    info_parser.add_argument(
        "template",
        help="Template name"
    )
    info_parser.set_defaults(func=lambda args: asyncio.run(handle_template_info(args)))
    
    # Generate template command
    generate_parser = templates_subparsers.add_parser(
        "generate",
        help="Generate manifest from template", 
        description="Generate YAML manifest from template"
    )
    generate_parser.add_argument(
        "template",
        help="Template name"
    )
    generate_parser.add_argument(
        "--params",
        nargs="*",
        help="Template parameters in key=value format"
    )
    generate_parser.add_argument(
        "--output", "-o",
        help="Output file path (if not specified, prints to stdout)"
    )
    generate_parser.set_defaults(func=lambda args: asyncio.run(handle_generate_template(args)))
