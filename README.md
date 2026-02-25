# OpenClaw Mem0 插件 - 火山引擎版

为 [OpenClaw](https://github.com/openclaw/openclaw) 代理提供长期记忆能力，由 [Mem0](https://mem0.ai) 驱动，支持火山引擎部署。

## 功能特性

- **自动召回 (Auto-Recall)** — 在代理响应前，自动搜索相关记忆并注入到上下文中
- **自动捕获 (Auto-Capture)** — 在代理响应后，自动保存对话中的重要信息
- **短期/长期双记忆系统** — 会话级（短期）和用户级（长期）记忆分离管理
- **火山引擎兼容** — 支持连接到火山引擎部署的 Mem0 服务

## 快速开始

### 1. 安装插件

```bash
openclaw plugins install @mem0/openclaw-mem0
```

### 2. 配置火山引擎

在你的 `openclaw.json` 配置文件中添加：

```json5
// plugins.entries
"openclaw-mem0": {
  "enabled": true,
  "config": {
    "mode": "platform",
    "apiKey": "${MEM0_API_KEY}",
    "host": "https://mem0-cnlfjzigaku8gczkzo.mem0.volces.com",
    "userId": "your-user-id"
  }
}
```

### 3. 设置环境变量

在你的环境变量中设置 Mem0 API Key：

```bash
export MEM0_API_KEY="your-api-key-here"
```

或者在配置中直接填写（不推荐生产环境使用）：

```json5
"apiKey": "m0-xxxxxxxxxxxxxxxxxxxxx"
```

## 配置详解

| 配置项 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `mode` | string | 是 | 固定为 `"platform"` |
| `apiKey` | string | 是 | Mem0 API Key，可使用 `${MEM0_API_KEY}` 引用环境变量 |
| `host` | string | 是 | 火山引擎 Mem0 服务地址：`https://mem0-cnlfjzigaku8gczkzo.mem0.volces.com` |
| `userId` | string | 否 | 用户标识，默认 `"default"` |
| `orgId` | string | 否 | 组织 ID（可选） |
| `projectId` | string | 否 | 项目 ID（可选） |
| `autoRecall` | boolean | 否 | 启用自动召回，默认 `true` |
| `autoCapture` | boolean | 否 | 启用自动捕获，默认 `true` |
| `topK` | number | 否 | 每次召回的记忆数量，默认 `5` |
| `searchThreshold` | number | 否 | 相似度阈值 (0-1)，默认 `0.5` |

### 完整配置示例

```json5
"openclaw-mem0": {
  "enabled": true,
  "config": {
    "mode": "platform",
    "apiKey": "${MEM0_API_KEY}",
    "host": "https://mem0-cnlfjzigaku8gczkzo.mem0.volces.com",
    "userId": "zhangsan",
    "autoRecall": true,
    "autoCapture": true,
    "topK": 10,
    "searchThreshold": 0.6,
    "enableGraph": false
  }
}
```

## 代理工具

插件为代理提供以下工具：

| 工具 | 描述 |
|------|------|
| `memory_search` | 通过自然语言搜索记忆 |
| `memory_list` | 列出用户的所有记忆 |
| `memory_store` | 显式保存某个事实 |
| `memory_get` | 通过 ID 获取特定记忆 |
| `memory_forget` | 通过 ID 或查询删除记忆 |

## CLI 命令

```bash
# 搜索所有记忆（长期 + 会话）
openclaw mem0 search "用户使用什么编程语言"

# 仅搜索长期记忆
openclaw mem0 search "用户使用什么编程语言" --scope long-term

# 仅搜索会话/短期记忆
openclaw mem0 search "用户使用什么编程语言" --scope session

# 查看统计信息
openclaw mem0 stats
```

## 工作原理

### 记忆范围

- **Session (短期记忆)** — 使用 `run_id` 与会话绑定，仅在当前对话中有效
- **User (长期记忆)** — 持久化存储，跨所有会话共享

### 工作流程

1. **Auto-Recall** — 代理响应前，插件搜索 Mem0 找到与当前消息相关的记忆并注入上下文
2. **Auto-Capture** — 代理响应后，插件将对话发送到 Mem0，Mem0 决定保存哪些内容
3. 两个过程都在后台静默运行，无需额外提示或配置

## 常见问题

### 如何获取 API Key？

请联系火山引擎 Mem0 服务管理员获取 API Key。

### 连接失败怎么办？

1. 确认 `host` 配置正确：`https://mem0-cnlfjzigaku8gczkzo.mem0.volces.com`
2. 确认 `apiKey` 有效且有访问权限
3. 检查网络连接是否可以访问火山引擎服务

### 记忆没有生效？

- 检查 `autoRecall` 和 `autoCapture` 是否为 `true`
- 调整 `searchThreshold` 阈值（降低可以召回更多记忆）
- 使用 `openclaw mem0 stats` 查看记忆统计
