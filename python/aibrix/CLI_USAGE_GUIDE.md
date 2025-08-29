# AIBrix CLI 详细使用文档

## 目录

1. [概述](#概述)
2. [安装与配置](#安装与配置)
3. [快速开始](#快速开始)
4. [命令详解](#命令详解)
5. [模板系统](#模板系统)
6. [监控与调试](#监控与调试)
7. [实践案例](#实践案例)
8. [故障排除](#故障排除)
9. [最佳实践](#最佳实践)

## 概述

AIBrix CLI 是一个专为 AI/ML 从业者设计的高级命令行工具，旨在简化 Kubernetes 上 AIBrix 工作负载的管理。它抽象了复杂的 Kubernetes 操作，提供直观的命令来部署、扩展和监控您的 AI 模型服务。

### 核心特性

- **简化工作负载管理**：无需深入了解 Kubernetes，即可部署、扩展、更新和删除 AIBrix 工作负载
- **内置模板系统**：提供常见部署模式的快速启动模板
- **集成监控**：查看日志、检查状态和监控工作负载健康状况
- **自动补全**：支持 bash 和 zsh 的 shell 补全
- **清单验证**：提供有用错误信息的清单验证
- **最小依赖**：仅使用必要的依赖包，保持轻量级

### 架构设计

AIBrix CLI 采用模块化架构：

```
aibrix/cli/
├── main.py              # 主要CLI入口点
├── k8s_client.py        # Kubernetes客户端包装器
├── completion.py        # 自动补全支持
└── commands/
    ├── install.py       # 安装管理命令
    ├── management.py    # 工作负载管理命令
    ├── monitoring.py    # 监控命令
    └── templates.py     # 模板系统
```

## 安装与配置

### 1. 安装 AIBrix CLI

AIBrix CLI 随 AIBrix Python 包一起提供：

```bash
# 安装 AIBrix
pip install aibrix

# 验证安装
aibrix --version
```

### 2. Kubernetes 配置

CLI 使用您的默认 kubeconfig 文件 (`~/.kube/config`)：

```bash
# 检查集群连接
kubectl cluster-info

# 验证 AIBrix CLI 连接
aibrix status
```

如需使用不同的配置文件：

```bash
# 指定 kubeconfig 文件
aibrix --kubeconfig /path/to/config status

# 指定命名空间
aibrix --namespace my-namespace status
```

### 3. 自动补全设置

#### Bash 补全

```bash
# 安装补全脚本
aibrix completion --install --shell bash

# 添加到 ~/.bashrc
echo 'source ~/.bash_completion.d/aibrix' >> ~/.bashrc
source ~/.bashrc
```

#### Zsh 补全

```bash
# 安装补全脚本
aibrix completion --install --shell zsh

# 添加到 ~/.zshrc
echo 'fpath=(~/.zsh/completions $fpath)' >> ~/.zshrc
echo 'autoload -U compinit && compinit' >> ~/.zshrc
source ~/.zshrc
```

## 快速开始

### 第一个部署

使用快速启动模板部署一个模型：

```bash
# 1. 检查模板列表
aibrix templates list

# 2. 查看模板信息
aibrix templates info quickstart

# 3. 部署模型
aibrix deploy --template quickstart \
  --params model_name=my-llama \
           model_path=meta-llama/Llama-2-7b-chat-hf \
           replicas=1

# 4. 检查部署状态
aibrix list deployments

# 5. 查看工作负载详细状态
aibrix workload-status --workload my-llama

# 6. 查看日志
aibrix logs --workload my-llama --tail 50
```

### 扩展和管理

```bash
# 扩展副本数
aibrix scale --workload my-llama --replicas 3

# 检查扩展状态
aibrix workload-status --workload my-llama --events

# 端口转发到本地
aibrix port-forward --service my-llama --port 8080:8000

# 清理资源
aibrix delete my-llama
```

## 命令详解

### 全局选项

所有命令都支持以下全局选项：

```bash
--kubeconfig KUBECONFIG    # kubeconfig 文件路径
--namespace NAMESPACE      # Kubernetes 命名空间 (默认: default)
--verbose                  # 启用详细输出
--help                     # 显示帮助信息
```

### 安装管理命令

#### 安装组件

```bash
# 安装所有 AIBrix 组件
aibrix install --version latest

# 安装特定组件
aibrix install --component controller
aibrix install --component gateway
aibrix install --component metadata
aibrix install --component monitoring

# 指定环境
aibrix install --env dev
aibrix install --env prod
```

#### 卸载组件

```bash
# 卸载所有组件
aibrix uninstall --all

# 卸载特定组件
aibrix uninstall --component controller
```

#### 查看安装状态

```bash
# 查看所有组件状态
aibrix status
```

输出示例：
```
Component       Status       Version    Description
--------------------------------------------------------------
controller      Installed    v0.3.0     AIBrix controller and CRDs
gateway         Installed    v0.3.0     Envoy Gateway for traffic routing
metadata        Installed    v0.3.0     Metadata service and Redis
monitoring      Installed    v0.3.0     Prometheus monitoring stack
```

### 工作负载管理命令

#### 部署工作负载

##### 从模板部署

```bash
# 基础部署
aibrix deploy --template quickstart \
  --params model_name=gpt-model \
           model_path=gpt2

# 带自动扩展的部署
aibrix deploy --template autoscaling \
  --params model_name=scalable-model \
           model_path=meta-llama/Llama-2-7b-hf \
           min_replicas=1 \
           max_replicas=5 \
           target_cpu=70

# 带 KV 缓存的部署
aibrix deploy --template kvcache \
  --params model_name=cached-model \
           model_path=meta-llama/Llama-2-13b-hf \
           cache_type=l1cache \
           cache_size=10Gi
```

##### 从清单文件部署

```bash
# 验证清单文件
aibrix validate --file deployment.yaml

# 部署清单文件
aibrix deploy --file deployment.yaml
```

#### 列出工作负载

```bash
# 列出所有工作负载
aibrix list all

# 列出特定类型
aibrix list deployments
aibrix list services
aibrix list custom

# 使用标签选择器过滤
aibrix list deployments --selector model.aibrix.ai/name=my-model
aibrix list all --selector environment=production
```

输出示例：
```
Name                           Type          Namespace      Status
--------------------------------------------------------------------------------
my-llama                       Deployment    default        2/2 ready
cached-model                   Deployment    default        1/1 ready
my-llama-autoscaler           PodAutoscaler  default        Active
```

#### 扩展工作负载

```bash
# 扩展到指定副本数
aibrix scale --workload my-model --replicas 5

# 扩展多个工作负载
aibrix scale --workload model-1 --replicas 3
aibrix scale --workload model-2 --replicas 2
```

#### 更新工作负载

```bash
# 从新的清单文件更新
aibrix update my-model --file updated-deployment.yaml
```

#### 删除工作负载

```bash
# 删除部署
aibrix delete my-model

# 删除特定类型的资源
aibrix delete my-autoscaler --type podautoscaler
```

#### 验证清单

```bash
# 验证单个文件
aibrix validate --file deployment.yaml

# 验证多个文件
aibrix validate --file deployment1.yaml
aibrix validate --file deployment2.yaml
```

### 监控命令

#### 查看工作负载状态

```bash
# 基本状态查看
aibrix workload-status --workload my-model

# 包含事件信息
aibrix workload-status --workload my-model --events
```

输出示例：
```
Workload: my-llama
Namespace: default
Status: Ready
Replicas: 2/2 ready
Labels:
  model.aibrix.ai/name=my-llama
  model.aibrix.ai/port=8000

Recent Events:
  2024-01-15T10:30:00Z Normal Scheduled: Successfully assigned pod to node
  2024-01-15T10:30:15Z Normal Pulled: Container image pulled successfully
  2024-01-15T10:30:20Z Normal Started: Container started successfully
```

#### 查看日志

```bash
# 查看最新日志
aibrix logs --workload my-model

# 指定行数
aibrix logs --workload my-model --tail 100

# 实时跟踪日志
aibrix logs --workload my-model --follow

# 查看特定容器日志
aibrix logs --workload my-model --container vllm-openai

# 查看之前容器实例日志
aibrix logs --workload my-model --previous
```

#### 端口转发

```bash
# 转发到相同端口
aibrix port-forward --service my-model --port 8000

# 转发到不同端口
aibrix port-forward --service my-model --port 8080:8000

# 指定命名空间
aibrix port-forward --service my-model --port 8080:8000 --namespace production
```

## 模板系统

### 内置模板

#### 1. Quickstart 模板

适用于基本的 LLM 推理部署：

```bash
# 查看模板信息
aibrix templates info quickstart

# 生成清单到文件
aibrix templates generate quickstart \
  --params model_name=my-model \
           model_path=meta-llama/Llama-2-7b-hf \
           replicas=2 \
           gpu_count=1 \
           max_model_len=12288 \
  --output my-deployment.yaml

# 直接部署
aibrix deploy --template quickstart \
  --params model_name=my-model \
           model_path=meta-llama/Llama-2-7b-hf
```

**参数说明：**
- `model_name` (必需)：部署名称
- `model_path` (必需)：HuggingFace 模型路径
- `replicas` (默认: 1)：副本数量
- `gpu_count` (默认: 1)：每个副本的 GPU 数量
- `max_model_len` (默认: 12288)：最大序列长度

#### 2. Autoscaling 模板

带有水平 Pod 自动扩展器的部署：

```bash
aibrix deploy --template autoscaling \
  --params model_name=scalable-model \
           model_path=meta-llama/Llama-2-7b-hf \
           min_replicas=1 \
           max_replicas=10 \
           target_cpu=70
```

**参数说明：**
- `model_name` (必需)：模型名称
- `model_path` (必需)：HuggingFace 模型路径
- `min_replicas` (默认: 1)：最小副本数
- `max_replicas` (默认: 10)：最大副本数
- `target_cpu` (默认: 70)：目标 CPU 利用率

#### 3. KVCache 模板

带有 KV 缓存分离的部署：

```bash
aibrix deploy --template kvcache \
  --params model_name=cached-model \
           model_path=meta-llama/Llama-2-13b-hf \
           cache_type=l1cache \
           cache_size=10Gi
```

**参数说明：**
- `model_name` (必需)：模型名称
- `model_path` (必需)：HuggingFace 模型路径
- `cache_type` (默认: l1cache)：缓存类型 (l1cache, infinistore, vineyard)
- `cache_size` (默认: 10Gi)：缓存大小

### 模板管理

```bash
# 列出所有可用模板
aibrix templates list

# 查看特定模板详细信息
aibrix templates info quickstart
aibrix templates info autoscaling
aibrix templates info kvcache

# 生成清单文件而不部署
aibrix templates generate quickstart \
  --params model_name=test-model model_path=gpt2 \
  --output test-deployment.yaml
```

## 监控与调试

### 检查工作负载健康状况

```bash
# 全面的状态检查
aibrix workload-status --workload my-model --events

# 检查所有部署状态
aibrix list deployments

# 查看自动扩展器状态
aibrix list custom --selector kind=PodAutoscaler
```

### 日志分析

```bash
# 查看启动日志
aibrix logs --workload my-model --tail 200

# 实时监控日志
aibrix logs --workload my-model --follow

# 检查错误模式
aibrix logs --workload my-model | grep -i error

# 查看多个容器日志
aibrix logs --workload my-model --container vllm-openai
aibrix logs --workload my-model --container aibrix-runtime
```

### 性能监控

```bash
# 设置端口转发访问 Prometheus 指标
aibrix port-forward --service my-model --port 8080:8080

# 访问健康检查端点
curl http://localhost:8080/healthz

# 访问指标端点
curl http://localhost:8080/metrics
```

### 调试部署问题

```bash
# 验证清单语法
aibrix validate --file problematic-deployment.yaml

# 检查资源状态和事件
aibrix workload-status --workload problematic-model --events

# 查看详细日志
aibrix logs --workload problematic-model --tail 500

# 检查集群资源
kubectl get nodes
kubectl describe node <node-name>
```

## 实践案例

### 案例 1：部署生产环境的 LLM 服务

```bash
# 1. 部署带自动扩展的生产服务
aibrix deploy --template autoscaling \
  --params model_name=production-llama \
           model_path=meta-llama/Llama-2-70b-chat-hf \
           min_replicas=2 \
           max_replicas=20 \
           target_cpu=80

# 2. 验证部署
aibrix workload-status --workload production-llama --events

# 3. 设置监控
aibrix port-forward --service production-llama --port 9090:8080 &

# 4. 负载测试期间监控
watch -n 5 'aibrix list deployments | grep production-llama'

# 5. 查看自动扩展行为
aibrix logs --workload production-llama-autoscaler --follow
```

### 案例 2：开发环境快速迭代

```bash
# 1. 快速部署开发版本
aibrix deploy --template quickstart \
  --params model_name=dev-model \
           model_path=gpt2 \
           replicas=1

# 2. 测试模型
aibrix port-forward --service dev-model --port 8000:8000 &
curl -X POST http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "dev-model", "prompt": "Hello", "max_tokens": 50}'

# 3. 查看日志调试
aibrix logs --workload dev-model --follow

# 4. 更新模型版本
# 编辑 deployment.yaml 修改镜像版本
aibrix update dev-model --file updated-deployment.yaml

# 5. 清理开发资源
aibrix delete dev-model
```

### 案例 3：大规模模型部署优化

```bash
# 1. 部署带 KV 缓存的大模型
aibrix deploy --template kvcache \
  --params model_name=large-model \
           model_path=meta-llama/Llama-2-70b-hf \
           cache_type=infinistore \
           cache_size=50Gi

# 2. 监控缓存效果
aibrix logs --workload large-model | grep cache

# 3. 根据负载动态扩展
aibrix scale --workload large-model --replicas 4

# 4. 监控资源使用情况
kubectl top pods -l model.aibrix.ai/name=large-model
```

### 案例 4：多模型并行部署

```bash
# 1. 部署多个不同规模的模型
aibrix deploy --template quickstart \
  --params model_name=small-model model_path=gpt2 replicas=3

aibrix deploy --template autoscaling \
  --params model_name=medium-model \
           model_path=meta-llama/Llama-2-7b-hf \
           min_replicas=1 max_replicas=5

aibrix deploy --template kvcache \
  --params model_name=large-model \
           model_path=meta-llama/Llama-2-13b-hf \
           cache_type=l1cache

# 2. 统一监控所有模型
aibrix list all --selector model.aibrix.ai/name

# 3. 批量状态检查
for model in small-model medium-model large-model; do
  echo "=== $model ==="
  aibrix workload-status --workload $model
  echo
done
```

## 故障排除

### 常见问题及解决方案

#### 1. 连接问题

**问题**：无法连接到 Kubernetes 集群
```bash
Error: Failed to configure Kubernetes client: Unable to load config
```

**解决方案**：
```bash
# 检查 kubeconfig 文件
ls -la ~/.kube/config

# 验证集群连接
kubectl cluster-info

# 使用特定配置文件
aibrix --kubeconfig /path/to/config status

# 检查集群权限
kubectl auth can-i create deployments
```

#### 2. 部署失败

**问题**：模板部署失败
```bash
Error: Required parameter missing: model_name
```

**解决方案**：
```bash
# 检查模板参数要求
aibrix templates info quickstart

# 验证参数格式
aibrix templates generate quickstart \
  --params model_name=test model_path=gpt2 \
  --output test.yaml

# 验证生成的清单
aibrix validate --file test.yaml
```

#### 3. 资源不足

**问题**：Pod 无法调度
```bash
Warning  FailedScheduling  pod/my-model-xxx  0/3 nodes are available: insufficient nvidia.com/gpu
```

**解决方案**：
```bash
# 检查节点资源
kubectl describe nodes

# 检查 GPU 可用性
kubectl get nodes -o custom-columns=NAME:.metadata.name,GPU:.status.allocatable.'nvidia\.com/gpu'

# 调整 GPU 需求
aibrix templates generate quickstart \
  --params model_name=my-model model_path=gpt2 gpu_count=1 \
  --output adjusted-deployment.yaml
```

#### 4. 镜像拉取失败

**问题**：容器镜像无法拉取
```bash
Failed to pull image "vllm/vllm-openai:v0.7.1": rpc error: code = Unknown
```

**解决方案**：
```bash
# 检查镜像是否存在
docker pull vllm/vllm-openai:v0.7.1

# 检查集群镜像拉取策略
kubectl describe pod my-model-xxx

# 使用本地可用镜像
# 编辑模板使用不同镜像版本
```

#### 5. 服务不可访问

**问题**：无法访问模型服务
```bash
curl: (7) Failed to connect to localhost:8000
```

**解决方案**：
```bash
# 检查服务状态
aibrix workload-status --workload my-model

# 验证端口转发
aibrix port-forward --service my-model --port 8000:8000

# 检查 pod 健康状况
kubectl get pods -l model.aibrix.ai/name=my-model

# 查看服务端点
kubectl get endpoints my-model
```

### 调试工具和技巧

#### 启用详细输出

```bash
# 使用详细模式获取更多信息
aibrix --verbose deploy --template quickstart \
  --params model_name=debug-model model_path=gpt2
```

#### 使用 kubectl 进行深度调试

```bash
# 检查 AIBrix 自定义资源
kubectl get podautoscalers
kubectl get stormservices
kubectl get kvcaches

# 查看资源详细信息
kubectl describe deployment my-model
kubectl describe pod my-model-xxx

# 检查事件
kubectl get events --sort-by='.lastTimestamp'
```

#### 日志聚合

```bash
# 收集所有相关日志
mkdir debug-logs
aibrix logs --workload my-model > debug-logs/model.log
kubectl logs deployment/my-model --all-containers > debug-logs/k8s.log
kubectl describe deployment my-model > debug-logs/describe.log
```

## 最佳实践

### 1. 命名约定

```bash
# 使用有意义的命名
aibrix deploy --template quickstart \
  --params model_name=chat-llama2-7b-v1 \
           model_path=meta-llama/Llama-2-7b-chat-hf

# 包含环境信息
aibrix deploy --template autoscaling \
  --params model_name=prod-gpt-service \
           model_path=gpt2
```

### 2. 资源管理

```bash
# 为不同环境使用不同命名空间
aibrix --namespace development deploy --template quickstart \
  --params model_name=dev-model model_path=gpt2

aibrix --namespace production deploy --template autoscaling \
  --params model_name=prod-model model_path=meta-llama/Llama-2-7b-hf
```

### 3. 监控策略

```bash
# 设置定期健康检查
#!/bin/bash
for model in $(aibrix list deployments | awk 'NR>1 {print $1}'); do
  status=$(aibrix workload-status --workload $model | grep "Status:" | awk '{print $2}')
  echo "Model: $model, Status: $status"
done
```

### 4. 备份和恢复

```bash
# 导出当前部署配置
aibrix list deployments | while read name _; do
  if [ "$name" != "Name" ]; then
    kubectl get deployment $name -o yaml > backup-${name}.yaml
  fi
done

# 从备份恢复
aibrix deploy --file backup-my-model.yaml
```

### 5. 版本管理

```bash
# 使用标签管理版本
kubectl label deployment my-model version=v1.0.0
kubectl label deployment my-model environment=production

# 查看版本信息
aibrix list deployments --selector version=v1.0.0
```

### 6. 安全考虑

```bash
# 使用专用命名空间
kubectl create namespace ai-models
aibrix --namespace ai-models deploy --template quickstart \
  --params model_name=secure-model model_path=gpt2

# 设置资源限制
# 在模板中包含适当的资源限制
```

### 7. 性能优化

```bash
# 使用 KV 缓存优化大模型
aibrix deploy --template kvcache \
  --params model_name=optimized-model \
           model_path=meta-llama/Llama-2-70b-hf \
           cache_type=infinistore \
           cache_size=100Gi

# 配置自动扩展
aibrix deploy --template autoscaling \
  --params model_name=elastic-model \
           model_path=meta-llama/Llama-2-7b-hf \
           min_replicas=2 \
           max_replicas=20 \
           target_cpu=60
```

---

## 附录

### A. 环境变量

AIBrix CLI 支持以下环境变量：

```bash
export KUBECONFIG=/path/to/kubeconfig      # 默认 kubeconfig 路径
export AIBRIX_NAMESPACE=my-namespace       # 默认命名空间
export AIBRIX_VERBOSE=true                 # 启用详细输出
```

### B. 配置文件

创建 `~/.aibrix/config.yaml` 来设置默认值：

```yaml
kubeconfig: /home/user/.kube/config
namespace: default
verbose: false
default_templates:
  development: quickstart
  production: autoscaling
```

### C. 集成示例

与 CI/CD 管道集成：

```yaml
# .github/workflows/deploy.yml
name: Deploy Model
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install AIBrix
        run: pip install aibrix
      - name: Deploy Model
        run: |
          aibrix deploy --template autoscaling \
            --params model_name=${{ github.sha }} \
                     model_path=my-org/my-model
```

### D. 故障排除检查清单

部署问题诊断清单：

- [ ] 集群连接正常 (`kubectl cluster-info`)
- [ ] 有足够的资源 (`kubectl describe nodes`)
- [ ] 镜像可访问 (`docker pull <image>`)
- [ ] 清单语法正确 (`aibrix validate --file <file>`)
- [ ] 参数完整 (`aibrix templates info <template>`)
- [ ] 网络策略允许访问
- [ ] RBAC 权限充足

