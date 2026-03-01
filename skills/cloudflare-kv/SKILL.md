---
name: cloudflare-kv
description: Cloudflare Workers KV 键值对操作工具。支持读取、写入、列出、删除KV键值对。核心特性：脚本可自动从KV获取密钥，业务密钥存储在KV中无需修改openclaw.json、无需重启Gateway。适用于：需要与Cloudflare KV交互时、数据持久化到Cloudflare KV、配置管理、缓存场景、密钥集中管理。通过Python脚本提供基础KV操作能力，可重复使用。
---

# Cloudflare KV 操作工具

该skill提供了与Cloudflare Workers KV交互的基础功能，包括读取、写入、列出和删除键值对。

## ⚠️ 安全警告

**严禁将敏感密钥直接输出到对话中！**

### 正确做法
- ✅ 在脚本内部使用密钥（如API调用）
- ✅ 返回操作结果（成功/失败）
- ✅ 需要显示时使用部分遮掩（如：`BSAe...2f`）
- ✅ 使用 `[已配置]` 或 `[REDACTED]` 表示

### 错误做法（绝对禁止）
- ❌ 直接输出完整 API key
- ❌ 在对话中展示密钥字符串
- ❌ 将密钥写入日志文件

### 为什么重要？
- 对话历史会作为上下文发送到大模型
- 敏感信息会暴露到第三方服务器
- 违反安全最佳实践

## 快速开始

### 1. 环境配置

确保已安装Python依赖：

```bash
pip install requests
```

设置必要的环境变量（可在 `~/.bashrc` 或 `~/.zshrc` 中添加）：

```bash
export CLOUDFLARE_API_TOKEN="your-api-token"
export CLOUDFLARE_ACCOUNT_ID="your-account-id"
export CLOUDFLARE_NAMESPACE_ID="your-namespace-id"
```

### 2. 获取凭证

1. **API Token**：
   - 访问 https://dash.cloudflare.com/profile/api-tokens
   - 创建Token，权限选择：`Account - Cloudflare Workers KV Storage - Edit`

2. **Account ID**：
   - 访问 https://dash.cloudflare.com/
   - 在URL中找到：`dash.cloudflare.com/<account-id>/workers`

3. **Namespace ID**：
   - 访问 https://dash.cloudflare.com/<account-id>/workers/kv/namespaces
   - 创建或选择已有的KV Namespace，在URL中获取ID

## 🔑 自动获取密钥（推荐）

**核心优势：所有业务密钥存储在 KV，修改后无需重启 Gateway**

### 环境变量配置

只需要配置 KV 访问凭证（一次性配置，基本不改）：

```bash
# 在 openclaw.json 的 env 中配置
export CLOUDFLARE_API_TOKEN="your-api-token"
export CLOUDFLARE_ACCOUNT_ID="your-account-id"
export CLOUDFLARE_NAMESPACE_ID="your-namespace-id"
```

### 脚本自动从 KV 读取密钥

**场景1：脚本需要密钥**
```bash
# 方式A：直接读取单个密钥
BRAVE_KEY=$(python3 scripts/kv_get_env.py BRAVE_API_KEY)

# 方式B：导出为环境变量
eval $(python3 scripts/kv_get_env.py BRAVE_API_KEY GLM_API_KEY --export)

# 方式C：JSON 格式（用于 Python/Node.js 脚本）
KEYS=$(python3 scripts/kv_get_env.py BRAVE_API_KEY GLM_API_KEY --json)
```

**场景2：写入到本地 .env 文件**
```bash
# 追加模式（推荐）
python3 scripts/kv_get_env.py BRAVE_API_KEY GLM_API_KEY --write .env

# 覆盖模式
python3 scripts/kv_get_env.py BRAVE_API_KEY --write .env --overwrite
```

### 工作流程

```
1. 在 Cloudflare KV 中添加密钥
   ↓
2. 脚本调用 kv_get_env.py 自动获取
   ↓
3. 无需修改 openclaw.json
   ↓
4. 无需重启 Gateway
```

---

## 基础操作

### 读取键值

```bash
python3 scripts/kv_read.py <key>
```

示例：
```bash
python3 scripts/kv_read.py "user:123:config"
```

### 写入键值

```bash
python3 scripts/kv_write.py <key> <value>
```

示例：
```bash
python3 scripts/kv_write.py "user:123:config" '{"theme":"dark","lang":"zh"}'
```

### 列出所有键

```bash
python3 scripts/kv_list.py
```

带分页：
```bash
python3 scripts/kv_list.py --limit 50
python3 scripts/kv_list.py --cursor "abc123..."
```

### 删除键

```bash
python3 scripts/kv_delete.py <key>
```

示例：
```bash
python3 scripts/kv_delete.py "user:123:config"
```

## 高级用法

### 覆盖环境变量

所有脚本都支持命令行参数覆盖环境变量：

```bash
python3 scripts/kv_read.py "my-key" --account-id "xxx" --namespace-id "yyy"
```

### Python API 使用

所有脚本都导出主函数，可以直接在Python代码中调用：

```python
from scripts.kv_read import read_kv
from scripts.kv_write import write_kv
from scripts.kv_list import list_keys
from scripts.kv_delete import delete_kv

# 读取
value = read_kv("config")

# 写入
write_kv("config", '{"setting": "value"}')

# 列出
keys = list_keys(limit=10)

# 删除
delete_kv("config")
```

## 最佳实践

### 键命名规范

使用冒号分隔的层级结构，便于组织和管理：

```
user:<user-id>:profile
user:<user-id>:settings
app:config
cache:session:<session-id>
```

### 值格式建议

- **配置**：JSON字符串，便于解析
- **文本**：纯文本
- **二进制**：Base64编码

### 错误处理

脚本会在失败时返回非零退出码，错误信息输出到stderr：

```bash
python3 scripts/kv_read.py "nonexistent-key" 2>&1
```

## 常见问题

### Q: 如何批量操作KV？

使用 `kv_list.py` 获取键列表，然后循环处理：

```bash
for key in $(python3 scripts/kv_list.py --json | jq -r '.result[].name'); do
  python3 scripts/kv_read.py "$key"
done
```

### Q: KV读写延迟如何？

- 读取：全球边缘延迟（<100ms）
- 写入：通常在数秒内传播完成

### Q: KV的存储限制？

- 单个值：最大 25MB
- 命名空间：最多 1GB（免费版）

### Q: 如何设置过期时间？

KV API支持在写入时设置过期时间，如需此功能，可参考Cloudflare官方文档扩展脚本。

---

## 📝 实战示例：Brave Search 自动获取密钥

**场景**：脚本需要使用 BRAVE_API_KEY，但不想硬编码

```python
#!/usr/bin/env python3
import subprocess
import json

# 自动从 KV 获取密钥
result = subprocess.run(
    ["python3", "scripts/kv_get_env.py", "BRAVE_API_KEY", "--json"],
    capture_output=True,
    text=True,
    check=True
)

keys = json.loads(result.stdout)
api_key = keys["BRAVE_API_KEY"]

# 使用密钥调用 API
headers = {"X-API-Key": api_key}
# ... 调用 Brave Search API
```

**优势**：
- ✅ 密钥集中管理在 KV
- ✅ 修改密钥无需重启 Gateway
- ✅ 脚本自动获取最新密钥

