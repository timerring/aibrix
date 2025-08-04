# AIBrix Advanced CLI

A unified command-line interface for managing AIBrix workloads on Kubernetes, designed to simplify AI/ML workload management without requiring deep Kubernetes knowledge.

## Features

- **Unified Interface**: Single `aibrix` command for all operations
- **Kubernetes Abstraction**: Hide complex Kubernetes operations behind simple commands
- **Template System**: Deploy workloads using predefined templates
- **Legacy Integration**: Seamlessly integrates with existing AIBrix tools
- **Validation**: Built-in configuration validation
- **Monitoring**: Easy status checking and log retrieval

## Installation

The CLI is included with the AIBrix Python package:

```bash
pip install aibrix
```

## Quick Start

### 1. Install AIBrix Components

```bash
# Install latest version
aibrix install --version latest

# Install specific component
aibrix install --component stormservice
```

### 2. Deploy a Workload

```bash
# Deploy using built-in template
aibrix deploy --template deepseek-7b --name my-model

# Deploy using custom template
aibrix deploy --template my-template.yaml --params config.yaml
```

### 3. Manage Workloads

```bash
# List all workloads
aibrix list

# Check status
aibrix status --workload my-model

# Scale workload
aibrix scale --workload my-model --replicas 3

# View logs
aibrix logs --workload my-model --tail 100
```

## Commands

### Installation Commands

#### `aibrix install`
Install AIBrix components on the cluster.

```bash
# Install latest version
aibrix install --version latest

# Install specific component
aibrix install --component stormservice

# Install to specific namespace
aibrix install --namespace my-namespace

# Dry run to see what would be installed
aibrix install --dry-run
```

#### `aibrix uninstall`
Uninstall AIBrix components.

```bash
# Uninstall all components
aibrix uninstall --all

# Uninstall specific component
aibrix uninstall --component stormservice

# Force uninstall without confirmation
aibrix uninstall --all --force
```

### Deployment Commands

#### `aibrix deploy`
Deploy workloads using templates.

```bash
# Deploy using built-in template
aibrix deploy --template deepseek-7b --name my-model

# Deploy using custom template with parameters
aibrix deploy --template my-template.yaml --params config.yaml

# Deploy to specific namespace
aibrix deploy --template deepseek-7b --namespace my-namespace

# Dry run to see what would be deployed
aibrix deploy --template deepseek-7b --dry-run
```

#### `aibrix validate`
Validate configuration files.

```bash
# Validate template file
aibrix validate --file my-template.yaml

# Output validation results as JSON
aibrix validate --file my-template.yaml --output json
```

### Management Commands

#### `aibrix list`
List all AIBrix workloads.

```bash
# List workloads in default namespace
aibrix list

# List workloads in specific namespace
aibrix list --namespace my-namespace

# Show additional details
aibrix list --wide

# Output as YAML
aibrix list --output yaml
```

#### `aibrix scale`
Scale workloads.

```bash
# Scale workload to 3 replicas
aibrix scale --workload my-model --replicas 3

# Scale in specific namespace
aibrix scale --workload my-model --replicas 3 --namespace my-namespace

# Dry run to see what would be scaled
aibrix scale --workload my-model --replicas 3 --dry-run
```

#### `aibrix update`
Update workload configurations.

```bash
# Update workload with new configuration
aibrix update --workload my-model --file updated-config.yaml

# Force update without confirmation
aibrix update --workload my-model --file updated-config.yaml --force

# Dry run to see what would be updated
aibrix update --workload my-model --file updated-config.yaml --dry-run
```

#### `aibrix delete`
Delete workloads.

```bash
# Delete workload
aibrix delete my-model

# Delete from specific namespace
aibrix delete my-model --namespace my-namespace

# Force delete without confirmation
aibrix delete my-model --force
```

### Monitoring Commands

#### `aibrix status`
Check workload status.

```bash
# Check all workloads
aibrix status

# Check specific workload
aibrix status --workload my-model

# Show detailed status
aibrix status --workload my-model --output yaml
```

#### `aibrix logs`
View workload logs.

```bash
# View logs from workload
aibrix logs --workload my-model

# Follow logs in real-time
aibrix logs --workload my-model --follow

# Show last 100 lines
aibrix logs --workload my-model --tail 100

# View logs from specific container
aibrix logs --workload my-model --container aibrix-runtime
```

#### `aibrix port-forward`
Port forward to services.

```bash
# Port forward to service
aibrix port-forward --service envoy-gateway --port 8888:80

# Port forward to specific namespace
aibrix port-forward --service envoy-gateway --port 8888:80 --namespace my-namespace
```

### Legacy Integration Commands

#### `aibrix runtime`
Start the AIBrix runtime server.

```bash
# Start runtime server on default port
aibrix runtime

# Start on specific port
aibrix runtime --port 8080

# Start on specific host
aibrix runtime --host 0.0.0.0 --port 8080

# Enable FastAPI docs
aibrix runtime --enable-fastapi-docs
```

#### `aibrix download`
Download models.

```bash
# Download model from HuggingFace
aibrix download --model-uri deepseek-ai/deepseek-coder-6.7b-instruct

# Download to specific directory
aibrix download --model-uri deepseek-ai/deepseek-coder-6.7b-instruct --local-dir /models

# Download with progress bar
aibrix download --model-uri deepseek-ai/deepseek-coder-6.7b-instruct --enable-progress-bar
```

#### `aibrix benchmark`
Run benchmarks.

```bash
# Run benchmark for model
aibrix benchmark -m deepseek-coder-7b -o ./benchmark_results

# Run with additional arguments
aibrix benchmark -m deepseek-coder-7b -o ./benchmark_results --additional-args "--batch-size 4"
```

#### `aibrix gen-profile`
Generate profiles.

```bash
# Generate profile for deployment
aibrix gen-profile deepseek-coder-7b --cost 1.0 --tput 10.0

# Generate profile with specific SLO targets
aibrix gen-profile deepseek-coder-7b --cost 1.0 --e2e 100 --ttft 50

# Output to Redis
aibrix gen-profile deepseek-coder-7b --cost 1.0 -o "redis://localhost:6379/?model=deepseek-coder-7b"
```

## Configuration

### Kubernetes Configuration

The CLI uses standard Kubernetes configuration:

- **kubeconfig**: Default `~/.kube/config` or specify with `--kubeconfig`
- **Context**: Use `--context` to specify Kubernetes context
- **Namespace**: Default `default` namespace, override with `--namespace`

### Built-in Templates

The CLI includes several built-in templates:

- `deepseek-7b`: DeepSeek Coder 6.7B model
- `deepseek-7b-chat`: DeepSeek LLM 7B Chat model

### Custom Templates

Create custom templates in YAML format:

```yaml
apiVersion: orchestration.aibrix.ai/v1alpha1
kind: StormService
metadata:
  name: {{ model_name }}
  namespace: {{ namespace }}
spec:
  replicas: {{ replicas }}
  rolesets:
  - name: inference
    replicas: {{ inference_replicas }}
    template:
      spec:
        containers:
        - name: aibrix-runtime
          image: {{ image }}
          env:
          - name: MODEL_NAME
            value: {{ model_uri }}
          resources:
            requests:
              memory: {{ memory_request }}
              nvidia.com/gpu: {{ gpu_request }}
            limits:
              memory: {{ memory_limit }}
              nvidia.com/gpu: {{ gpu_limit }}
```

## Examples

### Complete Workflow

```bash
# 1. Install AIBrix
aibrix install --version latest

# 2. Deploy a model
aibrix deploy --template deepseek-7b --name my-coder-model

# 3. Check status
aibrix status --workload my-coder-model

# 4. Scale up for more load
aibrix scale --workload my-coder-model --replicas 3

# 5. View logs
aibrix logs --workload my-coder-model --tail 50

# 6. Port forward to access the service
aibrix port-forward --service my-coder-model --port 8888:80
```

### Development Workflow

```bash
# 1. Download model for local development
aibrix download --model-uri deepseek-ai/deepseek-coder-6.7b-instruct

# 2. Start runtime server
aibrix runtime --port 8080

# 3. Run benchmark
aibrix benchmark -m deepseek-coder-7b -o ./results

# 4. Generate profile
aibrix gen-profile deepseek-coder-7b --cost 1.0 --tput 10.0
```

## Troubleshooting

### Common Issues

1. **Kubernetes Connection**: Ensure `kubectl` is configured and can access your cluster
2. **Namespace Issues**: Check that the namespace exists and you have permissions
3. **Resource Limits**: Ensure your cluster has sufficient resources (GPU, memory)
4. **Image Pull**: Verify container images are accessible from your cluster

### Debug Commands

```bash
# Check cluster connectivity
kubectl cluster-info

# Check AIBrix components
aibrix list --namespace aibrix-system

# Validate configuration
aibrix validate --file my-config.yaml

# View detailed logs
aibrix logs --workload my-model --tail 100
```

## Contributing

The CLI is designed to be extensible. To add new commands:

1. Create a new command module in `aibrix/cli/commands/`
2. Implement `add_arguments()` and `handle()` functions
3. Register the command in `aibrix/cli/main.py`
4. Add tests and documentation

## License

Apache 2.0 License - see the main AIBrix repository for details. 