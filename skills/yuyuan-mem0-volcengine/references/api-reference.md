# API 参考 - 记忆工具

## memory_search

搜索记忆。

**参数**：
```typescript
{
  query: string;                    // 搜索查询（必需）
  limit?: number;                   // 最大结果数，默认 topK 配置值
  userId?: string;                  // 用户 ID，默认配置中的 userId
  scope?: "session" | "long-term" | "all";  // 记忆范围，默认 "all"
}
```

**返回**：
```typescript
{
  content: [
    {
      type: "text";
      text: string;  // 格式化的记忆列表
    }
  ];
  details: {
    count: number;
    memories: Array<{
      id: string;
      memory: string;
      score?: number;
      categories?: string[];
      created_at?: string;
    }>;
  };
}
```

**使用场景**：
- 用户问"之前我们说过..."
- 需要确认用户偏好
- 话题与历史对话相关

---

## memory_store

显式保存记忆。

**参数**：
```typescript
{
  text: string;                      // 要保存的信息（必需）
  userId?: string;                   // 用户 ID
  metadata?: Record<string, unknown>;  // 附加元数据
  longTerm?: boolean;                // 是否长期保存，默认 true
}
```

**返回**：
```typescript
{
  content: [
    {
      type: "text";
      text: string;  // 保存结果摘要
    }
  ];
  details: {
    action: "stored";
    results: Array<{
      id: string;
      memory: string;
      event: "ADD" | "UPDATE" | "DELETE" | "NOOP";
    }>;
  };
}
```

**使用场景**：
- 用户明确要求"记住这个"
- 重要决策或偏好
- 跨会话需要的关键信息

---

## memory_list

列出所有记忆。

**参数**：
```typescript
{
  userId?: string;                   // 用户 ID
  scope?: "session" | "long-term" | "all";  // 记忆范围，默认 "all"
}
```

**返回**：
```typescript
{
  content: [
    {
      type: "text";
      text: string;  // 记忆列表
    }
  ];
  details: {
    count: number;
    memories: Array<{
      id: string;
      memory: string;
      categories?: string[];
      created_at?: string;
    }>;
  };
}
```

---

## memory_get

通过 ID 获取特定记忆。

**参数**：
```typescript
{
  memoryId: string;  // 记忆 ID（必需）
}
```

**返回**：
```typescript
{
  content: [
    {
      type: "text";
      text: string;  // 记忆详情
    }
  ];
  details: {
    memory: {
      id: string;
      memory: string;
      user_id?: string;
      score?: number;
      categories?: string[];
      metadata?: Record<string, unknown>;
      created_at?: string;
      updated_at?: string;
    };
  };
}
```

---

## memory_forget

删除记忆。

**参数**：
```typescript
{
  query?: string;      // 搜索查询（二选一）
  memoryId?: string;   // 记忆 ID（二选一）
}
```

**返回**：
```typescript
{
  content: [
    {
      type: "text";
      text: string;  // 删除结果
    }
  ];
  details: {
    action?: "deleted" | "candidates";
    id?: string;
    found?: number;
    candidates?: Array<{
      id: string;
      memory: string;
      score?: number;
    }>;
    error?: string;
  };
}
```

**使用场景**：
- 用户要求"忘记那件事"
- 记忆过时或错误
- 清理隐私信息

---

## CLI 命令

### 搜索记忆

```bash
# 搜索所有记忆
openclaw mem0 search "查询内容"

# 指定范围
openclaw mem0 search "查询内容" --scope long-term
openclaw mem0 search "查询内容" --scope session

# 限制结果数
openclaw mem0 search "查询内容" --limit 20
```

### 查看统计

```bash
openclaw mem0 stats
```

输出示例：
```
Mode: platform
User: yuyuan
Total memories: 42
Graph enabled: false
Auto-recall: true, Auto-capture: true
```
