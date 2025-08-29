# AIBrix Advanced CLI

A comprehensive command-line interface for managing AIBrix workloads on Kubernetes clusters. This CLI abstracts away Kubernetes complexity and provides intuitive commands for AI/ML practitioners to deploy, scale, and monitor their workloads.

## Features

- **Simplified Workload Management**: Deploy, scale, update, and delete AIBrix workloads without deep Kubernetes knowledge
- **Built-in Templates**: Quick-start templates for common deployment patterns
- **Integrated Monitoring**: View logs, check status, and monitor workload health
- **Auto-completion**: Shell completion support for bash and zsh
- **Validation**: Manifest validation with helpful error messages
- **No External Dependencies**: Minimal dependency footprint using only essential packages

## Installation

The AIBrix CLI is included with the AIBrix Python package:

```bash
pip install aibrix
```

After installation, the `aibrix` command will be available in your PATH.

## Quick Start

1. **Check your cluster connection**:
   ```bash
   aibrix status
   ```

2. **Deploy a model using a template**:
   ```bash
   aibrix deploy --template quickstart \
     --params model_name=my-llama model_path=meta-llama/Llama-2-7b-chat-hf
   ```

3. **List your workloads**:
   ```bash
   aibrix list deployments
   ```

4. **Scale your workload**:
   ```bash
   aibrix scale --workload my-llama --replicas 3
   ```

5. **Check workload status**:
   ```bash
   aibrix status --workload my-llama
   ```

6. **View logs**:
   ```bash
   aibrix logs --workload my-llama --tail 100
   ```

## Commands

### Installation Management

- `aibrix install` - Install AIBrix components
- `aibrix uninstall` - Uninstall AIBrix components  
- `aibrix status` - Show installation status

### Workload Management

- `aibrix deploy` - Deploy workloads from manifest or template
- `aibrix list` - List workloads
- `aibrix delete` - Delete workloads
- `aibrix update` - Update existing workloads
- `aibrix scale` - Scale workloads
- `aibrix validate` - Validate manifest files

### Monitoring

- `aibrix status --workload <name>` - Show workload status
- `aibrix logs --workload <name>` - Show workload logs
- `aibrix port-forward` - Forward local port to service

### Templates

- `aibrix templates list` - List available templates
- `aibrix templates info <template>` - Show template information
- `aibrix templates generate <template>` - Generate manifest from template

### Shell Completion

- `aibrix completion --install --shell bash` - Install bash completion
- `aibrix completion --generate --shell zsh` - Generate zsh completion

## Built-in Templates

### Quickstart Template

Basic deployment template for LLM inference:

```bash
aibrix deploy --template quickstart \
  --params model_name=my-model \
           model_path=meta-llama/Llama-2-7b-hf \
           replicas=2 \
           gpu_count=1
```

Parameters:
- `model_name` (required) - Deployment name
- `model_path` (required) - HuggingFace model path  
- `replicas` (default: 1) - Number of replicas
- `gpu_count` (default: 1) - GPUs per replica
- `max_model_len` (default: 12288) - Maximum sequence length

### Autoscaling Template

Deployment with horizontal pod autoscaler:

```bash
aibrix deploy --template autoscaling \
  --params model_name=my-model \
           model_path=meta-llama/Llama-2-7b-hf \
           min_replicas=1 \
           max_replicas=5 \
           target_cpu=70
```

### KV Cache Template

Deployment with KV cache disaggregation:

```bash
aibrix deploy --template kvcache \
  --params model_name=my-model \
           model_path=meta-llama/Llama-2-7b-hf \
           cache_type=l1cache \
           cache_size=10Gi
```

## Configuration

### Kubernetes Configuration

The CLI uses your default kubeconfig file (`~/.kube/config`). You can specify a different config file:

```bash
aibrix --kubeconfig /path/to/config <command>
```

### Namespace

Default namespace is `default`. Change it with:

```bash
aibrix --namespace my-namespace <command>
```

## Examples

### Deploy from Manifest File

```bash
# Deploy from YAML file
aibrix deploy --file my-deployment.yaml

# Validate before deploying
aibrix validate --file my-deployment.yaml
aibrix deploy --file my-deployment.yaml
```

### Template-based Deployment

```bash
# List available templates
aibrix templates list

# Get template information
aibrix templates info quickstart

# Generate manifest to file
aibrix templates generate quickstart \
  --params model_name=llama2 model_path=meta-llama/Llama-2-7b-hf \
  --output llama2-deployment.yaml

# Deploy the generated manifest
aibrix deploy --file llama2-deployment.yaml
```

### Workload Management

```bash
# List all workloads
aibrix list all

# List only deployments
aibrix list deployments

# List with label selector
aibrix list deployments --selector model.aibrix.ai/name=my-model

# Scale a workload
aibrix scale --workload my-model --replicas 5

# Update a workload
aibrix update my-model --file updated-deployment.yaml

# Delete a workload
aibrix delete my-model
```

### Monitoring and Debugging

```bash
# Check workload status
aibrix status --workload my-model --events

# View logs
aibrix logs --workload my-model
aibrix logs --workload my-model --tail 50
aibrix logs --workload my-model --follow
aibrix logs --workload my-model --container vllm-openai

# Port forwarding
aibrix port-forward --service my-model --port 8080:8000
```

### Installation Management

```bash
# Install all components
aibrix install --version latest

# Install specific component
aibrix install --component controller

# Check installation status
aibrix status

# Uninstall all components
aibrix uninstall --all
```

## Shell Completion

Enable auto-completion for better CLI experience:

### Bash

```bash
# Install completion
aibrix completion --install --shell bash

# Add to ~/.bashrc
echo 'source ~/.bash_completion.d/aibrix' >> ~/.bashrc
source ~/.bashrc
```

### Zsh

```bash
# Install completion
aibrix completion --install --shell zsh

# Add to ~/.zshrc
echo 'fpath=(~/.zsh/completions $fpath)' >> ~/.zshrc
echo 'autoload -U compinit && compinit' >> ~/.zshrc
source ~/.zshrc
```

## Error Handling

The CLI provides helpful error messages and suggestions:

```bash
# Invalid template parameter
$ aibrix deploy --template quickstart --params invalid=value
Error: Unknown parameter: invalid
Available parameters for quickstart: model_name, model_path, replicas, gpu_count, max_model_len

# Missing required parameter
$ aibrix deploy --template quickstart --params replicas=2
Error: Required parameter missing: model_name

# Manifest validation error
$ aibrix validate --file broken.yaml
Error: Document 0: Missing required field 'apiVersion'
```

## Troubleshooting

### Connection Issues

```bash
# Test cluster connectivity
aibrix status

# Use specific kubeconfig
aibrix --kubeconfig ~/.kube/my-config status

# Check kubectl access
kubectl cluster-info
```

### Workload Issues

```bash
# Check detailed status with events
aibrix status --workload my-model --events

# View logs for debugging
aibrix logs --workload my-model --tail 100

# Validate manifest syntax
aibrix validate --file my-deployment.yaml
```

### CLI Issues

```bash
# Enable verbose output
aibrix --verbose <command>

# Check CLI version
aibrix --version
```

## Integration with Existing Tools

The AIBrix CLI works alongside existing Kubernetes tools:

- Use `kubectl` for advanced Kubernetes operations
- Use `aibrix` for AIBrix-specific workload management
- Templates generate standard Kubernetes manifests
- All resources are standard Kubernetes objects

## Contributing

The CLI is part of the AIBrix project. See the main [CONTRIBUTING.md](https://github.com/vllm-project/aibrix/blob/main/CONTRIBUTING.md) for contribution guidelines.

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](https://github.com/vllm-project/aibrix/blob/main/LICENSE) for details.
