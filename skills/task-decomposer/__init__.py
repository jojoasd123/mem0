# 任务拆解器 - OpenClaw Skill 入口

"""
任务拆解器技能 - 自动拆解复杂任务并并行执行

使用方式：
1. 自动触发：当检测到复杂任务时
2. 手动触发：用户说"拆解任务：xxx"或"并行执行：xxx"
"""

from typing import Dict, Any, Optional
import json


async def handle_task_decomposition(
    task: str,
    context: Dict[str, Any]
) -> str:
    """
    处理任务拆解请求
    
    Args:
        task: 用户任务描述
        context: 上下文信息（包含 sessions_spawn 等工具）
    
    Returns:
        执行结果文本
    """
    max_subtasks = 5
    default_agent = "main"
    
    # 1. 拆解任务
    decomposition = await decompose_task_llm(task, max_subtasks, context)
    
    should_decompose = decomposition.get("should_decompose", False)
    subtasks = decomposition.get("subtasks", [])
    reason = decomposition.get("reason", "")
    
    if not subtasks:
        return f"❌ 任务拆解失败：{reason}"
    
    # 2. 构建回复
    reply = []
    reply.append(f"🔍 **任务拆解完成**（{reason}）")
    reply.append("")
    
    if should_decompose and len(subtasks) > 1:
        reply.append(f"📋 拆解为 {len(subtasks)} 个并行子任务：")
        reply.append("")
        
        for i, subtask in enumerate(subtasks, 1):
            task_desc = subtask.get("task", "")
            agent_hint = subtask.get("agent_hint", default_agent)
            reply.append(f"{i}. **{agent_hint.upper()}**: {task_desc}")
        
        reply.append("")
        reply.append("🚀 开始并行执行...")
        reply.append("")
        
        # 3. 并行执行子任务
        results = await execute_subtasks_parallel(subtasks, default_agent, context)
        
        # 4. 汇总结果
        reply.append("📊 **执行结果汇总**")
        reply.append("")
        
        for result in results:
            status_icon = "✅" if result.get("status") == "completed" else "❌"
            reply.append(f"{status_icon} **子任务 {result['index']}**: {result['task'][:50]}...")
            if result.get("result"):
                reply.append(f"   > {result['result'][:100]}")
        
        reply.append("")
        reply.append(f"✨ 完成 {sum(1 for r in results if r['status'] == 'completed')}/{len(results)} 个子任务")
    else:
        # 不需要拆解，直接执行
        reply.append("💡 任务较简单，直接执行...")
        reply.append("")
        result = await execute_single_task(subtasks[0]["task"], default_agent, context)
        reply.append(f"✅ **执行完成**")
        reply.append("")
        reply.append(result)
    
    return "\n".join(reply)


async def decompose_task_llm(
    task: str,
    max_subtasks: int,
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """调用 LLM 拆解任务"""
    
    prompt = f"""
你是一个专业的任务规划师。请将以下复杂任务拆解成可**并行执行**的独立子任务。

## 要求：
1. 每个子任务必须独立，不依赖其他子任务的结果
2. 子任务数量：{max_subtasks} 个以内
3. 每个子任务描述清晰、具体、可执行
4. 如果任务本身很简单（一句话能完成），不要拆解，直接返回原任务

## 任务：
{task}

## 输出格式（严格 JSON）：
```json
{{
  "subtasks": [
    {{"task": "子任务 1 描述", "agent_hint": "coder|video|main"}},
    {{"task": "子任务 2 描述", "agent_hint": "coder|video|main"}}
  ],
  "should_decompose": true/false,
  "reason": "拆解/不拆解的原因"
}}
```

## Agent 提示：
- coder: 编程相关（代码、功能开发、bug 修复）
- video: 视频相关（脚本、渲染、剪辑）
- main: 日常对话、信息查询、简单任务
"""
    
    # 使用 OpenClaw 的 LLM 工具调用
    # 这里假设有一个 call_llm 工具可用
    try:
        # 实际实现需要调用 OpenClaw 的 LLM 接口
        # 这里提供一个伪代码实现
        llm_response = await context.get("call_llm", lambda x: {"content": ""})(prompt)
        
        content = llm_response.get("content", "")
        
        # 提取 JSON
        import re
        json_match = re.search(r'```json\n(.+?)\n```', content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
        else:
            return json.loads(content)
    except Exception as e:
        return {
            "subtasks": [{"task": task, "agent_hint": "main"}],
            "should_decompose": False,
            "reason": f"LLM 调用失败：{str(e)}"
        }


async def execute_subtasks_parallel(
    subtasks: list,
    default_agent: str,
    context: Dict[str, Any]
) -> list:
    """并行执行多个子任务"""
    
    results = []
    
    for i, subtask in enumerate(subtasks, 1):
        task_desc = subtask.get("task", "")
        agent_hint = subtask.get("agent_hint", default_agent)
        
        # 映射 agent_hint 到实际 agent_id
        agent_map = {"coder": "coder", "video": "video", "main": "main"}
        agent_id = agent_map.get(agent_hint.lower(), default_agent)
        
        # 使用 sessions_spawn 执行
        # 注意：实际实现需要调用 OpenClaw 的 sessions_spawn 工具
        result = {
            "index": i,
            "task": task_desc,
            "agent_id": agent_id,
            "status": "completed",
            "result": "子任务执行结果（需要在 OpenClaw 环境中实现）"
        }
        results.append(result)
    
    return results


async def execute_single_task(
    task: str,
    agent_id: str,
    context: Dict[str, Any]
) -> str:
    """执行单个任务"""
    # 实际实现需要调用 OpenClaw 的执行工具
    return f"任务 '{task}' 执行完成（需要在 OpenClaw 环境中实现）"


# Skill 元数据
SKILL_METADATA = {
    "name": "task-decomposer",
    "version": "1.0.0",
    "description": "自动拆解复杂任务并并行执行",
    "triggers": [
        "拆解任务",
        "并行执行",
        "多任务处理",
        "分解任务"
    ]
}
