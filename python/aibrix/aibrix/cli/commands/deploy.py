"""
Deploy command for AIBrix CLI.

Handles deployment of AIBrix workloads using templates.
"""

import argparse
import yaml
import os
from typing import Dict, Any
from aibrix.cli.k8s_client import AIBrixK8sClient


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """Add arguments to the deploy command parser."""
    parser.add_argument(
        "--template",
        type=str,
        required=True,
        help="Template name or path to template file"
    )
    parser.add_argument(
        "--params",
        type=str,
        help="Path to parameters file (YAML)"
    )
    parser.add_argument(
        "--namespace",
        type=str,
        default="default",
        help="Kubernetes namespace (default: default)"
    )
    parser.add_argument(
        "--name",
        type=str,
        help="Workload name (overrides template name)"
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
        help="Show what would be deployed without actually deploying"
    )


def load_template(template_path: str) -> Dict[str, Any]:
    """Load a template from file or built-in templates."""
    if os.path.exists(template_path):
        # Load from file
        with open(template_path, 'r') as f:
            return yaml.safe_load(f)
    else:
        # Try to load from built-in templates
        return load_builtin_template(template_path)


def load_builtin_template(template_name: str) -> Dict[str, Any]:
    """Load a built-in template by name."""
    templates = {
        "deepseek-7b": {
            "apiVersion": "orchestration.aibrix.ai/v1alpha1",
            "kind": "StormService",
            "metadata": {
                "name": "deepseek-7b",
                "namespace": "default"
            },
            "spec": {
                "replicas": 1,
                "rolesets": [
                    {
                        "name": "inference",
                        "replicas": 1,
                        "template": {
                            "spec": {
                                "containers": [
                                    {
                                        "name": "aibrix-runtime",
                                        "image": "aibrix/aibrix-runtime:latest",
                                        "env": [
                                            {
                                                "name": "MODEL_NAME",
                                                "value": "deepseek-ai/deepseek-coder-6.7b-instruct"
                                            }
                                        ],
                                        "resources": {
                                            "requests": {
                                                "memory": "16Gi",
                                                "nvidia.com/gpu": "1"
                                            },
                                            "limits": {
                                                "memory": "16Gi",
                                                "nvidia.com/gpu": "1"
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    }
                ]
            }
        },
        "deepseek-7b-chat": {
            "apiVersion": "orchestration.aibrix.ai/v1alpha1",
            "kind": "StormService",
            "metadata": {
                "name": "deepseek-7b-chat",
                "namespace": "default"
            },
            "spec": {
                "replicas": 1,
                "rolesets": [
                    {
                        "name": "inference",
                        "replicas": 1,
                        "template": {
                            "spec": {
                                "containers": [
                                    {
                                        "name": "aibrix-runtime",
                                        "image": "aibrix/aibrix-runtime:latest",
                                        "env": [
                                            {
                                                "name": "MODEL_NAME",
                                                "value": "deepseek-ai/deepseek-llm-7b-chat"
                                            }
                                        ],
                                        "resources": {
                                            "requests": {
                                                "memory": "16Gi",
                                                "nvidia.com/gpu": "1"
                                            },
                                            "limits": {
                                                "memory": "16Gi",
                                                "nvidia.com/gpu": "1"
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    }
                ]
            }
        }
    }
    
    if template_name not in templates:
        raise ValueError(f"Unknown template: {template_name}. Available templates: {list(templates.keys())}")
    
    return templates[template_name]


def load_params(params_path: str) -> Dict[str, Any]:
    """Load parameters from YAML file."""
    if not params_path or not os.path.exists(params_path):
        return {}
    
    with open(params_path, 'r') as f:
        return yaml.safe_load(f)


def apply_params(template: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
    """Apply parameters to template."""
    # Deep copy the template
    result = yaml.safe_load(yaml.dump(template))
    
    # Apply parameter substitutions
    def replace_values(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                obj[key] = replace_values(value)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                obj[i] = replace_values(item)
        elif isinstance(obj, str) and obj.startswith("{{") and obj.endswith("}}"):
            param_name = obj[2:-2].strip()
            if param_name in params:
                return params[param_name]
            else:
                print(f"Warning: Parameter {param_name} not found in params file")
                return obj
        return obj
    
    return replace_values(result)


def handle(args: argparse.Namespace) -> int:
    """Handle the deploy command."""
    try:
        # Load template
        template = load_template(args.template)
        
        # Load parameters
        params = load_params(args.params)
        
        # Apply parameters
        workload = apply_params(template, params)
        
        # Override name if specified
        if args.name:
            workload["metadata"]["name"] = args.name
        
        # Override namespace
        workload["metadata"]["namespace"] = args.namespace
        
        if args.dry_run:
            print("=== DRY RUN - Workload that would be deployed ===")
            print(yaml.dump(workload, default_flow_style=False))
            return 0
        
        # Initialize Kubernetes client
        k8s_client = AIBrixK8sClient(
            kubeconfig=args.kubeconfig,
            context=args.context
        )
        
        # Check if namespace exists, create if not
        if not k8s_client.check_namespace_exists(args.namespace):
            print(f"Creating namespace {args.namespace}...")
            if not k8s_client.create_namespace(args.namespace):
                print(f"Failed to create namespace {args.namespace}")
                return 1
        
        # Deploy the workload
        workload_name = workload["metadata"]["name"]
        print(f"Deploying {workload['kind']} '{workload_name}' to namespace '{args.namespace}'...")
        
        if workload["kind"] == "StormService":
            result = k8s_client.create_stormservice(workload, args.namespace)
            print(f"Successfully deployed StormService '{workload_name}'")
        else:
            print(f"Unsupported workload kind: {workload['kind']}")
            return 1
        
        return 0
        
    except Exception as e:
        print(f"Error deploying workload: {e}")
        return 1 