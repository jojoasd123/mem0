# Task Parallel Skill - OpenClaw 技能入口

"""
Task Parallel - 任务并行执行系统

触发方式：
- "并行处理：xxx"
- "拆解执行：xxx"
- "多任务：xxx"
- "task-parallel: xxx"
"""

import asyncio
from typing import Dict, Any
from .orchestrator_v2 import TaskParallel


async def handle_task_parallel_request(
    task: str,
    context: Dict[str, Any]
) -> str:
    """
    处理任务并行请求
    
    Args:
        task: 用户任务描述
        context: 上下文信息（包含 sessions_spawn 等工具）
    
    Returns:
        执行结果文本
    """
    # 创建任务并行执行器
    parallel = TaskParallel(
        max_parallel=10,
        timeout_per_task=300,
        retry_attempts=2,
        enable_monitoring=True,
        enable_critical_path=True,
        enable_llm_aggregation=False  # 暂不启用 LLM 聚合
    )
    
    # 注入 sessions_spawn 工具（如果可用）
    if "sessions_spawn" in context:
        parallel.set_sessions_spawn(context["sessions_spawn"])
    
    # 执行任务并行处理
    result = await parallel.execute(task)
    
    # 返回聚合报告
    return result["aggregated_report"]


def build_reply(result: Dict[str, Any]) -> str:
    """构建回复文本"""
    lines = []
    
    # 标题
    lines.append("🎛️ **任务编排器**")
    lines.append("")
    
    # 任务分析
    analysis = result.get("analysis", {})
    lines.append("📊 **任务分析**")
    lines.append(f"├─ 意图：{analysis.get('intent', 'unknown')}")
    lines.append(f"├─ 复杂度：{analysis.get('complexity', 'unknown')}")
    lines.append(f"└─ 预计子任务：{analysis.get('estimated_subtasks', 0)} 个")
    lines.append("")
    
    # 任务分解
    subtasks = result.get("subtasks", [])
    lines.append("📋 **任务分解**")
    for st in subtasks:
        deps = f"（依赖：{st['dependencies']}）" if st['dependencies'] else "（无依赖）"
        lines.append(f"├─ [{st['id']}] {st['agent'].upper()}: {st['task']}{deps}")
    lines.append("")
    
    # 执行结果
    lines.append("🚀 **执行结果**")
    results = result.get("results", [])
    for r in results:
        status_icon = "✅" if r['status'] == 'completed' else "❌"
        lines.append(f"{status_icon} [{r['id']}] {r['task'][:50]}...")
        if r.get('result'):
            lines.append(f"   > {r['result'][:100]}")
    lines.append("")
    
    # 性能指标
    metrics = result.get("metrics", {})
    lines.append("📊 **性能指标**")
    lines.append(f"├─ 总耗时：{metrics.get('duration_seconds', 0):.2f} 秒")
    lines.append(f"├─ 并行效率：{metrics.get('parallel_efficiency', 0)*100:.0f}%")
    lines.append(f"├─ 完成率：{metrics.get('completion_rate', 0)*100:.0f}%")
    lines.append(f"└─ Agent 使用：{metrics.get('agent_usage', {})}")
    lines.append("")
    
    # 任务 ID
    lines.append(f"ℹ️ 任务 ID: {result.get('task_id', 'unknown')}")
    
    return "\n".join(lines)


# Skill 元数据
SKILL_METADATA = {
    "name": "task-parallel",
    "version": "1.0.0",
    "description": "Task Parallel - 基于 Kimi K2.5 架构的任务并行执行系统",
    "triggers": [
        "并行处理",
        "拆解执行",
        "多任务",
        "task-parallel"
    ],
    "author": "本地芋圆 🍡",
    "based_on": "Kimi K2.5 Agent Swarm 架构"
}
