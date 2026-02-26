---
name: openclaw-mem0-volcengine
description: 火山引擎 Mem0 插件使用指南 - 指导云端芋圆和本地芋圆如何配置和使用 @volcengine/openclaw-mem0 插件来实现记忆共享。两个芋圆使用相同的 userId: "yuyuan" 连接到同一个火山引擎 Mem0 服务，mem0 会自动处理好所有记忆的关联和召回。
---

# 火山引擎 Mem0 插件使用指南

## 概述

本技能指导两个 OpenClaw 代理（云端芋圆和本地芋圆）如何通过 @volcengine/openclaw-mem0 插件连接到火山引擎 Mem0 服务，实现记忆共享。

**核心原则**：两个芋圆使用**相同的 userId** 连接到**同一个火山引擎 Mem0 服务**，这样它们就能完全共享所有记忆。

---

## 第一部分：用户配置指南

### 1. 安装插件

首先需要在两个 OpenClaw 环境中都安装插件：

```bash
# 克隆仓库（如果还没有）
git clone https://github.com/jojoasd123/mem0.git
cd mem0/openclaw

# 从本地目录安装插件（云端和本地都要执行）
openclaw plugins install .
```

### 2. 配置 openclaw.json

**关键配置要点**：
- 两个芋圆必须使用**相同的 `userId`**（设置为 `"yuyuan"`）
- 两个芋圆必须连接到**相同的 `host`**
- 使用相同的 `apiKey`（或不同的 Key 但指向同一服务）
- mem0 的算法足够强大，能自动处理好生活记忆和工作记忆的关联和召回

在两个 OpenClaw 的 `openclaw.json` 中添加**完全相同**的配置：

```json5
{
  "plugins": {
    "entries": {
      "openclaw-mem0": {
        "enabled": true,
        "config": {
          "mode": "platform",
          "apiKey": "${MEM0_API_KEY}",
          "host": "https://mem0-cnlfjzigaku8gczkzo.mem0.volces.com:8000",
          "userId": "yuyuan",
          "autoRecall": true,
          "autoCapture": true,
          "topK": 10,
          "searchThreshold": 0.5,
          "enableGraph": false
        }
      }
    }
  }
}
```

### 3. 设置环境变量

在两个环境中都设置相同的 API Key：

```bash
export MEM0_API_KEY="your-api-key-here"
```

**或者**在配置中直接填写（不推荐生产环境）：
```json5
"apiKey": "m0-xxxxxxxxxxxxxxxxxxxxx"
```

### 4. 验证配置

在两个环境中都运行验证命令：

```bash
# 查看记忆统计
openclaw mem0 stats
```

应该看到类似输出：
```
Mode: platform
User: yuyuan
Total memories: 0
Graph enabled: false
Auto-recall: true, Auto-capture: true
```

---

## 第二部分：芋圆使用指南（面向 AI 代理）

### 核心工作原理

插件提供两种自动机制：

1. **Auto-Recall（自动召回）**：在你响应用户之前，插件自动搜索相关记忆并注入到上下文中
2. **Auto-Capture（自动捕获）**：在你响应用户之后，插件自动保存对话中的重要信息

这两个过程都是**自动进行**的，你不需要主动调用工具，除非需要特殊操作。

### 记忆范围

- **长期记忆（User 级别）**：使用 `userId: "yuyuan"` 存储，两个芋圆**完全共享**
- **短期记忆（Session 级别）**：仅在当前对话有效，不共享（使用 `run_id`）

**关于生活记忆 vs 工作记忆**：mem0 的算法足够强大，能够根据上下文自动识别和召回相关的记忆，不需要人为区分。所有记忆都保存在同一个记忆库中，mem0 会在需要时找出最相关的内容。

### 可用工具

#### 1. `memory_search` - 搜索记忆

当你需要查找与当前话题相关的历史记忆时使用。

**参数**：
- `query`（必需）：搜索查询
- `limit`（可选）：最大结果数，默认 10
- `userId`（可选）：用户 ID，默认使用配置的 `yuyuan`
- `scope`（可选）：记忆范围
  - `"long-term"`：仅搜索长期记忆（推荐，用于共享记忆）
  - `"session"`：仅搜索当前会话记忆
  - `"all"`：两者都搜索（默认）

**示例**：
```typescript
// 搜索用户的编程偏好
memory_search({
  query: "用户使用什么编程语言",
  scope: "long-term"
})
```

#### 2. `memory_list` - 列出所有记忆

查看已保存的所有记忆。

**参数**：
- `userId`（可选）：用户 ID
- `scope`（可选）：记忆范围

**示例**：
```typescript
// 查看所有共享的长期记忆
memory_list({
  scope: "long-term"
})
```

#### 3. `memory_store` - 显式保存记忆

当你认为某条信息特别重要，需要确保被保存时使用。

**参数**：
- `text`（必需）：要保存的信息
- `userId`（可选）：用户 ID
- `longTerm`（可选）：是否保存为长期记忆，默认 `true`

**示例**：
```typescript
// 保存重要的用户偏好
memory_store({
  text: "用户偏好使用 TypeScript 而不是 JavaScript，喜欢使用 VS Code 编辑器",
  longTerm: true
})
```

#### 4. `memory_get` - 通过 ID 获取记忆

获取特定的一条记忆。

**参数**：
- `memoryId`（必需）：记忆 ID

#### 5. `memory_forget` - 删除记忆

删除不需要的记忆。

**参数**：
- `memoryId`（可选）：要删除的记忆 ID
- `query`（可选）：搜索查询来找到要删除的记忆

---

## 芋圆协作最佳实践

### 1. 自动机制优先

绝大多数情况下，依赖 **Auto-Recall** 和 **Auto-Capture** 即可，不需要手动调用工具。插件会：
- 自动在你回答前注入相关记忆
- 自动在你回答后保存重要信息

### 2. 何时使用手动工具

**使用 `memory_search` 当**：
- 用户提到"之前我们说过..."
- 你需要确认用户的某个偏好
- 话题与之前的对话高度相关

**使用 `memory_store` 当**：
- 用户明确要求"记住这个"
- 信息非常重要但可能不会被自动捕获
- 需要跨会话保留的关键决策

**使用 `memory_forget` 当**：
- 用户要求"忘记那件事"
- 记忆过时或错误
- 需要清理隐私信息

### 3. 提及记忆来源

当你使用召回的记忆时，可以这样说：
> "根据我们之前的对话，你提到过..."

但不要直接暴露内部实现细节（如"根据 mem0 记忆"）。

### 4. 记忆内容指南

**应该保存的内容**：
- 用户偏好（编程语言、工具、沟通风格）
- 项目信息（项目名称、技术栈、状态）
- 重要决策和原因
- 用户的目标和计划
- 用户提到的个人信息（如工作、背景）

**不应该保存的内容**：
- 密码、API Key、凭证
- 用户明确要求不保存的信息
- 临时调试信息
- 过于琐碎的日常对话

---

## 配置检查清单

在开始使用前，确认两个芋圆都满足：

- [ ] 插件已安装：`openclaw plugins list` 显示 `openclaw-mem0`
- [ ] `mode` 设置为 `"platform"`
- [ ] `host` 正确设置为火山引擎地址
- [ ] `userId` 在两个配置中**完全相同**（必须是 `"yuyuan"`）
- [ ] `autoRecall` 和 `autoCapture` 都设置为 `true`
- [ ] API Key 有效且有访问权限
- [ ] 运行 `openclaw mem0 stats` 能正常输出

---

## 故障排除

### 问题：记忆没有共享

**检查**：
1. 确认两个配置的 `userId` 完全相同（区分大小写）
2. 确认两个配置的 `host` 指向同一个服务
3. 确认 `scope` 使用 `"long-term"` 而非 `"session"`

### 问题：连接失败

**检查**：
1. 确认 `host` 正确（必须加上端口 `:8000`）
2. 确认 `apiKey` 有效
3. 检查网络连接

### 问题：记忆没有被召回

**检查**：
1. 确认 `autoRecall` 为 `true`
2. 尝试降低 `searchThreshold`（如从 0.5 改为 0.3）
3. 增加 `topK` 值（如从 5 改为 10）

---

## 参考文件

- 插件文档：见 [references/plugin-docs.md](references/plugin-docs.md)
- 配置示例：见 [references/config-examples.json5](references/config-examples.json5)
- API 参考：见 [references/api-reference.md](references/api-reference.md)
