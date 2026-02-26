# OpenClaw Mem0 插件文档（火山引擎版）

## 插件功能特性

### 1. 自动召回 (Auto-Recall)

在代理响应前，自动搜索相关记忆并注入到上下文中。

**工作流程**：
1. 用户发送消息
2. 插件使用消息内容作为查询搜索 Mem0
3. 找到相关记忆（长期 + 会话）
4. 将记忆注入到 `<relevant-memories>` 标签中
5. 代理看到注入的记忆后生成响应

**配置**：`autoRecall: true`（默认）

### 2. 自动捕获 (Auto-Capture)

在代理响应后，自动保存对话中的重要信息。

**工作流程**：
1. 代理完成响应
2. 插件收集最近的对话（最多 10 条）
3. 发送到 Mem0 进行记忆提取
4. Mem0 分析对话并决定保存哪些内容

**配置**：`autoCapture: true`（默认）

### 3. 双记忆系统

**长期记忆（User 级别）**：
- 使用 `userId` 作为标识
- 持久化存储，跨所有会话共享
- 适合保存用户偏好、项目信息等

**短期记忆（Session 级别）**：
- 使用 `run_id` 作为标识
- 仅在当前对话有效
- 适合保存临时上下文

## 完整配置选项

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `mode` | string | - | 必须设置为 `"platform"` 来使用火山引擎 |
| `apiKey` | string | - | Mem0 API Key，必填 |
| `host` | string | - | 火山引擎服务地址（必须加上端口 :8000） |
| `userId` | string | `"default"` | 用户标识，两个芋圆必须相同 |
| `orgId` | string | - | 组织 ID（可选） |
| `projectId` | string | - | 项目 ID（可选） |
| `autoRecall` | boolean | `true` | 启用自动召回 |
| `autoCapture` | boolean | `true` | 启用自动捕获 |
| `topK` | number | `5` | 每次召回的记忆数量 |
| `searchThreshold` | number | `0.5` | 相似度阈值 (0-1) |
| `enableGraph` | boolean | `false` | 启用记忆图谱 |
