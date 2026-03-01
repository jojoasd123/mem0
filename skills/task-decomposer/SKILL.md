# 任务拆解器 (Task Decomposer)

自动将复杂任务拆解为可并行执行的子任务，并协调执行。

## 使用方式

### 1. 作为技能使用

```python
from task_decomposer import decompose_and_execute

# 简单用法
result = decompose_and_execute("创建一个待办事项应用，包括前端、后端和数据库")

# 高级用法
result = decompose_and_execute(
    task="创建一个待办事项应用",
    max_subtasks=5,
    agent_id="coder",
    timeout=300
)
```

### 2. 作为 CLI 工具

```bash
python workspace/skills/task-decomposer/decompose.py "创建一个待办事项应用"
```

## 核心功能

1. **任务拆解**：用 LLM 将大任务拆成独立的子任务
2. **并行执行**：同时启动多个子代理执行子任务
3. **结果汇总**：收集所有子代理结果，整合回复

## 配置

在 `openclaw.json` 中添加：

```json
{
  "skills": {
    "entries": {
      "task-decomposer": {
        "enabled": true,
        "config": {
          "defaultAgent": "coder",
          "maxSubtasks": 5,
          "timeout": 300
        }
      }
    }
  }
}
```

---

*最后更新：2026-03-01*
