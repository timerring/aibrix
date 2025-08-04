"""
Validate command for AIBrix CLI.

Handles validation of AIBrix configuration files.
"""

import argparse
import yaml
import os
from typing import Dict, Any, List


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """Add arguments to the validate command parser."""
    parser.add_argument(
        "--file",
        type=str,
        required=True,
        help="Path to template file to validate"
    )
    parser.add_argument(
        "--schema",
        type=str,
        help="Path to schema file (optional)"
    )
    parser.add_argument(
        "--output",
        type=str,
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )


def validate_stormservice_spec(spec: Dict[str, Any]) -> List[str]:
    """Validate StormService spec."""
    errors = []
    
    # Check required fields
    if "replicas" not in spec:
        errors.append("spec.replicas is required")
    elif not isinstance(spec["replicas"], int) or spec["replicas"] < 0:
        errors.append("spec.replicas must be a non-negative integer")
    
    if "rolesets" not in spec:
        errors.append("spec.rolesets is required")
    elif not isinstance(spec["rolesets"], list):
        errors.append("spec.rolesets must be a list")
    elif len(spec["rolesets"]) == 0:
        errors.append("spec.rolesets cannot be empty")
    else:
        # Validate each roleset
        for i, roleset in enumerate(spec["rolesets"]):
            if not isinstance(roleset, dict):
                errors.append(f"spec.rolesets[{i}] must be an object")
                continue
            
            if "name" not in roleset:
                errors.append(f"spec.rolesets[{i}].name is required")
            
            if "replicas" not in roleset:
                errors.append(f"spec.rolesets[{i}].replicas is required")
            elif not isinstance(roleset["replicas"], int) or roleset["replicas"] < 0:
                errors.append(f"spec.rolesets[{i}].replicas must be a non-negative integer")
            
            if "template" not in roleset:
                errors.append(f"spec.rolesets[{i}].template is required")
            elif not isinstance(roleset["template"], dict):
                errors.append(f"spec.rolesets[{i}].template must be an object")
            else:
                # Validate pod template
                template_errors = validate_pod_template(roleset["template"], f"spec.rolesets[{i}].template")
                errors.extend(template_errors)
    
    return errors


def validate_pod_template(template: Dict[str, Any], path: str) -> List[str]:
    """Validate pod template."""
    errors = []
    
    if "spec" not in template:
        errors.append(f"{path}.spec is required")
        return errors
    
    spec = template["spec"]
    if not isinstance(spec, dict):
        errors.append(f"{path}.spec must be an object")
        return errors
    
    if "containers" not in spec:
        errors.append(f"{path}.spec.containers is required")
    elif not isinstance(spec["containers"], list):
        errors.append(f"{path}.spec.containers must be a list")
    elif len(spec["containers"]) == 0:
        errors.append(f"{path}.spec.containers cannot be empty")
    else:
        # Validate each container
        for i, container in enumerate(spec["containers"]):
            if not isinstance(container, dict):
                errors.append(f"{path}.spec.containers[{i}] must be an object")
                continue
            
            if "name" not in container:
                errors.append(f"{path}.spec.containers[{i}].name is required")
            
            if "image" not in container:
                errors.append(f"{path}.spec.containers[{i}].image is required")
            
            # Validate resources if present
            if "resources" in container:
                resources = container["resources"]
                if not isinstance(resources, dict):
                    errors.append(f"{path}.spec.containers[{i}].resources must be an object")
                else:
                    if "requests" in resources:
                        requests = resources["requests"]
                        if not isinstance(requests, dict):
                            errors.append(f"{path}.spec.containers[{i}].resources.requests must be an object")
                    
                    if "limits" in resources:
                        limits = resources["limits"]
                        if not isinstance(limits, dict):
                            errors.append(f"{path}.spec.containers[{i}].resources.limits must be an object")
    
    return errors


def validate_metadata(metadata: Dict[str, Any]) -> List[str]:
    """Validate metadata."""
    errors = []
    
    if "name" not in metadata:
        errors.append("metadata.name is required")
    elif not isinstance(metadata["name"], str) or len(metadata["name"]) == 0:
        errors.append("metadata.name must be a non-empty string")
    
    if "namespace" in metadata and not isinstance(metadata["namespace"], str):
        errors.append("metadata.namespace must be a string")
    
    return errors


def validate_aibrix_resource(data: Dict[str, Any]) -> List[str]:
    """Validate AIBrix resource."""
    errors = []
    
    # Check required top-level fields
    if "apiVersion" not in data:
        errors.append("apiVersion is required")
    elif not data["apiVersion"].startswith("orchestration.aibrix.ai/"):
        errors.append("apiVersion must be from orchestration.aibrix.ai group")
    
    if "kind" not in data:
        errors.append("kind is required")
    elif data["kind"] != "StormService":
        errors.append("kind must be StormService")
    
    if "metadata" not in data:
        errors.append("metadata is required")
    elif not isinstance(data["metadata"], dict):
        errors.append("metadata must be an object")
    else:
        metadata_errors = validate_metadata(data["metadata"])
        errors.extend(metadata_errors)
    
    if "spec" not in data:
        errors.append("spec is required")
    elif not isinstance(data["spec"], dict):
        errors.append("spec must be an object")
    else:
        spec_errors = validate_stormservice_spec(data["spec"])
        errors.extend(spec_errors)
    
    return errors


def handle(args: argparse.ArgumentParser) -> int:
    """Handle the validate command."""
    try:
        # Check if file exists
        if not os.path.exists(args.file):
            print(f"Error: File '{args.file}' not found")
            return 1
        
        # Load and parse YAML
        try:
            with open(args.file, 'r') as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file: {e}")
            return 1
        
        # Validate the resource
        errors = validate_aibrix_resource(data)
        
        # Output results
        if args.output == "json":
            import json
            result = {
                "valid": len(errors) == 0,
                "errors": errors
            }
            print(json.dumps(result, indent=2))
        else:
            if len(errors) == 0:
                print(f"✓ Configuration file '{args.file}' is valid")
            else:
                print(f"✗ Configuration file '{args.file}' has {len(errors)} error(s):")
                for error in errors:
                    print(f"  - {error}")
        
        return 0 if len(errors) == 0 else 1
        
    except Exception as e:
        print(f"Error validating configuration: {e}")
        return 1 