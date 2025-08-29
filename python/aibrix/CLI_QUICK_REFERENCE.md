# AIBrix CLI

## 安装

```bash
pip install aibrix
```

## 第一次使用

### 1. 验证安装
```bash
aibrix --version
aibrix --help
```

### 2. 检查集群连接
```bash
aibrix status
```

### 3. 查看可用模板
```bash
aibrix templates list
```

## 核心功能

### 🚀 快速部署模型

#### 基础部署
```bash
aibrix deploy --template quickstart \
  --params model_name=我的模型 \
           model_path=meta-llama/Llama-2-7b-chat-hf
```

#### 带自动扩展的部署
```bash
aibrix deploy --template autoscaling \
  --params model_name=可扩展模型 \
           model_path=meta-llama/Llama-2-7b-hf \
           min_replicas=1 \
           max_replicas=5
```

#### 带缓存优化的部署
```bash
aibrix deploy --template kvcache \
  --params model_name=缓存模型 \
           model_path=meta-llama/Llama-2-13b-hf \
           cache_type=l1cache \
           cache_size=10Gi
```

### 📊 管理工作负载

```bash
# 查看所有部署
aibrix list deployments

# 扩展副本数
aibrix scale --workload 我的模型 --replicas 3

# 查看详细状态
aibrix workload-status --workload 我的模型

# 更新部署
aibrix update 我的模型 --file 新配置.yaml

# 删除部署
aibrix delete 我的模型
```

### 🔍 监控和调试

```bash
# 查看实时日志
aibrix logs --workload 我的模型 --follow

# 查看最近100行日志
aibrix logs --workload 我的模型 --tail 100

# 端口转发到本地
aibrix port-forward --service 我的模型 --port 8080:8000

# 检查详细状态和事件
aibrix workload-status --workload 我的模型 --events
```

### ✅ 验证配置

```bash
# 验证YAML文件
aibrix validate --file 部署配置.yaml

# 生成模板到文件
aibrix templates generate quickstart \
  --params model_name=测试模型 model_path=gpt2 \
  --output 测试部署.yaml
```

## 实用技巧

### 使用标签过滤
```bash
aibrix list deployments --selector model.aibrix.ai/name=我的模型
```

### 指定命名空间
```bash
aibrix --namespace 生产环境 list deployments
```

### 启用详细输出
```bash
aibrix --verbose deploy --template quickstart \
  --params model_name=调试模型 model_path=gpt2
```

### 自动补全设置
```bash
# Bash用户
aibrix completion --install --shell bash
echo 'source ~/.bash_completion.d/aibrix' >> ~/.bashrc

# Zsh用户  
aibrix completion --install --shell zsh
echo 'fpath=(~/.zsh/completions $fpath)' >> ~/.zshrc
```

## 常见使用场景

### 开发测试
```bash
# 快速部署用于开发测试
aibrix deploy --template quickstart \
  --params model_name=开发测试 model_path=gpt2 replicas=1

# 实时查看日志
aibrix logs --workload 开发测试 --follow

# 本地访问测试
aibrix port-forward --service 开发测试 --port 8000
```

### 生产部署
```bash
# 部署生产环境（带自动扩展）
aibrix deploy --template autoscaling \
  --params model_name=生产服务 \
           model_path=meta-llama/Llama-2-7b-hf \
           min_replicas=2 \
           max_replicas=10 \
           target_cpu=70

# 监控扩展状态
aibrix workload-status --workload 生产服务 --events
```

### 大模型优化
```bash
# 使用KV缓存优化大模型
aibrix deploy --template kvcache \
  --params model_name=大模型服务 \
           model_path=meta-llama/Llama-2-70b-hf \
           cache_type=infinistore \
           cache_size=100Gi

# 监控缓存效果
aibrix logs --workload 大模型服务 | grep cache
```

## 故障排除

### 连接问题
```bash
# 检查集群状态
kubectl cluster-info
aibrix status

# 使用特定配置文件
aibrix --kubeconfig /路径/配置文件 status
```

### 部署问题
```bash
# 检查模板参数
aibrix templates info quickstart

# 验证配置文件
aibrix validate --file 配置.yaml

# 查看详细错误
aibrix --verbose deploy --template quickstart \
  --params model_name=测试 model_path=gpt2
```

### 运行时问题
```bash
# 查看Pod状态
aibrix workload-status --workload 模型名 --events

# 查看详细日志
aibrix logs --workload 模型名 --tail 200

# 检查资源使用
kubectl top pods -l model.aibrix.ai/name=模型名
```

## 进阶用法

### 批处理操作
```bash
#!/bin/bash
# 批量检查模型状态
for model in 模型1 模型2 模型3; do
  echo "=== $model ==="
  aibrix workload-status --workload $model
done
```

### 配置备份
```bash
# 导出当前配置
kubectl get deployment 我的模型 -o yaml > 备份-我的模型.yaml

# 从备份恢复
aibrix deploy --file 备份-我的模型.yaml
```

### 环境变量配置
```bash
export KUBECONFIG=/路径/配置文件
export AIBRIX_NAMESPACE=我的命名空间
export AIBRIX_VERBOSE=true
```

## 常用命令速查

| 功能 | 命令 |
|------|------|
| 快速部署 | `aibrix deploy --template quickstart --params model_name=名称 model_path=路径` |
| 列出部署 | `aibrix list deployments` |
| 查看状态 | `aibrix workload-status --workload 名称` |
| 扩展副本 | `aibrix scale --workload 名称 --replicas 数量` |
| 查看日志 | `aibrix logs --workload 名称 --tail 100` |
| 端口转发 | `aibrix port-forward --service 名称 --port 8080:8000` |
| 验证配置 | `aibrix validate --file 文件.yaml` |
| 删除部署 | `aibrix delete 名称` |

## 获取帮助

```bash
# 查看总体帮助
aibrix --help

# 查看特定命令帮助
aibrix deploy --help
aibrix templates --help

# 查看模板信息
aibrix templates info quickstart
```
