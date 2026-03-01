# 🚀 Task Parallel - 任务并行执行系统

基于 Kimi K2.5 架构设计的简化版任务编排系统。

## 架构概览

```
┌──────────────────────────────────────────────────────────────────┐
│                      🎛️ Orchestrator (编排器)                    │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐            │
│  │ 任务分析器   │ → │ 任务分解器   │ → │ DAG 构建器     │            │
│  │ - 意图识别   │   │ - 子任务生成 │   │ - 依赖识别   │            │
│  │ - 复杂度评估 │   │ - Agent 分配 │   │ - 关键路径   │            │
│  └─────────────┘   └─────────────┘   └─────────────┘            │
│                            │                                     │
│                            ▼                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              📦 并行执行引擎 (Execution Engine)           │    │
│  │  最多 10 个并行子代理 (main/coder/video)                   │    │
│  └─────────────────────────────────────────────────────────┘    │
│                            │                                     │
│                            ▼                                     │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐            │
│  │ 结果收集器   │ → │ 冲突检测器   │ → │ 最终聚合器   │            │
│  │ - 状态监控   │   │ - 矛盾识别   │   │ - 报告生成   │            │
│  │ - 超时处理   │   │ - 自动修复   │   │ - 输出格式化 │            │
│  └─────────────┘   └─────────────┘   └─────────────┘            │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

## 核心特性

### ✅ 已实现（Phase 1）

- [x] 任务分析器（意图识别 + 复杂度评估）
- [x] 任务分解器（LLM 拆解 + Agent 分配）
- [x] DAG 构建器（依赖识别）
- [x] 并行执行引擎（sessions_spawn 集成）
- [x] 结果收集器
- [x] 性能监控（基础指标）

### ⏳ 待实现（Phase 2）

- [ ] 关键路径调度
- [ ] 失败重试机制
- [ ] 冲突检测器
- [ ] 最终聚合器（LLM 整合）

## 使用方式

### 1. 作为技能使用

```python
from task_parallel import TaskParallel

# 创建任务并行执行器
parallel = TaskParallel(
    max_parallel=10,
    timeout_per_task=300
)

# 执行任务
result = await parallel.execute("创建一个待办事项应用，包括前端、后端和数据库")
```

### 2. 自然语言触发

- "并行处理：创建一个待办事项应用"
- "拆解执行：修复 bug 并写文档和测试"
- "多任务：xxx"

## 配置

### openclaw.json

```json
{
  "skills": {
    "entries": {
      "orchestrator": {
        "enabled": true,
        "config": {
          "maxParallel": 10,
          "timeoutPerTask": 300,
          "defaultAgent": "main",
          "enableMonitoring": true,
          "monitoringPath": "/home/ubuntu/.openclaw/workspace/orchestrator/metrics"
        }
      }
    }
  }
}
```

### Agent 模板

```yaml
# orchestrator/agent_templates.yaml
agent_templates:
  main:
    model: bailian/qwen3.5-plus
    max_iterations: 50
    description: 日常对话、信息查询、简单任务
    
  coder:
    model: zai/glm-4.7
    max_iterations: 100
    tools: [file_editor, terminal]
    description: 编程任务（代码、功能开发、bug 修复）
    
  video:
    model: bailian/qwen3.5-plus
    max_iterations: 50
    description: 视频任务（脚本、渲染、剪辑）
```

## 性能指标

### 监控指标

| 指标 | 说明 | 单位 |
|------|------|------|
| `subtask_count` | 子任务数量 | 个 |
| `parallel_efficiency` | 并行效率（实际时间/串行时间） | % |
| `completion_rate` | 完成率（成功/总数） | % |
| `avg_duration` | 平均执行时间 | 秒 |
| `agent_utilization` | Agent 利用率 | % |
| `failure_rate` | 失败率 | % |

### 监控日志

```json
{
  "timestamp": "2026-03-01T16:00:00Z",
  "task_id": "task_001",
  "original_task": "创建一个待办事项应用",
  "subtask_count": 3,
  "parallel_count": 3,
  "duration_seconds": 45.2,
  "completion_rate": 1.0,
  "agent_usage": {
    "coder": 3
  },
  "metrics": {
    "parallel_efficiency": 0.85,
    "avg_duration": 15.1
  }
}
```

## 文件结构

```
skills/task-parallel/
├── SKILL.md              # 技能说明（本文件）
├── __init__.py           # 技能入口
├── orchestrator.py       # 核心编排逻辑
├── orchestrator_v2.py    # 完整版（含并行执行）
├── executor.py           # 并行执行引擎
├── aggregator.py         # 结果聚合器
└── tests/
    └── test_sessions_spawn.py
```

## 执行流程

### 1. 任务分析

```python
analysis = analyzer.analyze(task)
# 输出：
# {
#   "intent": "development",
#   "complexity": "high",
#   "estimated_subtasks": 3-5,
#   "required_agents": ["coder", "video"]
# }
```

### 2. 任务分解

```python
subtasks = decomposer.decompose(task, analysis)
# 输出：
# [
#   {"id": 1, "task": "设计数据库 schema", "agent": "coder", "dependencies": []},
#   {"id": 2, "task": "实现后端 API", "agent": "coder", "dependencies": [1]},
#   {"id": 3, "task": "创建前端界面", "agent": "coder", "dependencies": [2]}
# ]
```

### 3. DAG 构建

```python
dag = dag_builder.build(subtasks)
# 识别关键路径、并行组
```

### 4. 并行执行

```python
results = await executor.execute_parallel(dag)
# 启动 sessions_spawn，并行执行子任务
```

### 5. 结果聚合

```python
final_result = aggregator.aggregate(results)
# 整合所有子任务结果，生成最终报告
```

## 示例

### 输入

```
编排任务：创建一个待办事项应用，包括前端、后端和数据库
```

### 输出

```
🎛️ 任务编排器已启动

📊 任务分析
├─ 意图：应用开发
├─ 复杂度：高
└─ 预计子任务：3-5 个

📋 任务分解
├─ [1] CODER: 设计数据库 schema（无依赖）
├─ [2] CODER: 实现后端 API（依赖：1）
└─ [3] CODER: 创建前端界面（依赖：2）

🚀 开始执行（关键路径优先）
├─ [1/3] 执行中... 设计数据库 schema
├─ [2/3] 等待中... 实现后端 API（依赖 1）
└─ [3/3] 等待中... 创建前端界面（依赖 2）

[执行中...]

✅ 执行完成

📊 性能指标
├─ 总耗时：45.2 秒
├─ 并行效率：85%
├─ 完成率：100%
└─ Agent 使用：coder × 3

📝 最终报告
[整合所有子任务结果...]
```

---

*版本：1.0.0 | 作者：本地芋圆 🍡 | 基于 Kimi K2.5 Agent Swarm 架构设计*
