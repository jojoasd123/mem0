
# 火山引擎 Mem0 兼容更新指南

## 概述

本次更新使 openclaw-mem0 插件能够兼容火山引擎部署的 Mem0 服务。

## 修改内容

### 1. TypeScript SDK 修改 (`mem0-ts/src/client/mem0.ts`)

#### 1.1 修复 `ping()` 方法

**问题**: 火山引擎的 `/v1/ping/` 接口返回格式与官方 mem0 不同，没有 `status: "ok"` 字段。

**修改前**:
```typescript
if (response.status !== "ok") {
  throw new APIError(response.message || "API Key is invalid");
}
```

**修改后**:
```typescript
// 兼容火山引擎的返回格式 - 火山引擎不返回 status: "ok"
// 只要有 project_id 或 org_id 就认为成功
const hasProjectOrOrg = response.project_id || response.org_id;
const hasStatusOk = response.status === "ok";

if (!hasStatusOk && !hasProjectOrOrg) {
  throw new APIError(response.message || "API Key is invalid");
}
```

#### 1.2 修改 `add()` 方法默认启用 `async_mode`

**问题**: 火山引擎只支持异步模式，同步模式会返回错误：
`"Sync mode is disabled. please set async_mode to True."`

**修改**: 在 `add()` 方法中添加：
```typescript
// 火山引擎只支持异步模式，默认启用 async_mode
if (options.async_mode === undefined) {
  options.async_mode = true;
}
```

### 2. 文档更新 (`openclaw/README.md`)

**问题**: 用户可能忘记在 host 中添加端口 `:8000`。

**修改**: 在所有示例和配置说明中，明确指出 host 需要包含端口：
- `https://mem0-cnlfjzigaku8gczkzo.mem0.volces.com:8000`

## 配置示例

### openclaw.json 配置

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
          "userId": "default"
        }
      }
    }
  }
}
```

### 环境变量

```bash
export MEM0_API_KEY="7814ca22-d815-5db8-bea1-8a688d6dd366"
```

## 重新构建和安装

### 1. 构建 TypeScript SDK

```bash
cd mem0-ts
npm install
npm run build
```

### 2. 安装插件到 openclaw

```bash
cd ../openclaw
openclaw plugins install .
```

## 验证安装

安装完成后，可以通过以下方式验证：

1. 启动 openclaw
2. 检查插件是否成功加载，没有 "Failed to ping server: fetch failed" 错误
3. 测试记忆功能是否正常工作

## 向后兼容

这些修改保持了对官方 mem0 服务的完全向后兼容：
- 官方 mem0 仍然可以通过 `status: "ok"` 正常验证
- `async_mode` 可以被显式覆盖为 `false`（如果官方服务支持）

## 故障排查

### 问题: 仍然提示 "Failed to ping server"

**检查清单**:
1. 确认 host 包含 `:8000` 端口
2. 确认 API Key 正确
3. 确认网络可以访问火山引擎服务

### 问题: 添加记忆失败

**检查清单**:
1. 确认使用的是最新构建的版本
2. 检查是否有 `"Sync mode is disabled"` 错误

