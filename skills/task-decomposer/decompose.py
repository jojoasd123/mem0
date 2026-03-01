#!/usr/bin/env python3
"""
任务拆解器 - Task Decomposer

自动将复杂任务拆解为可并行执行的子任务，并协调执行。
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional


# 任务拆解提示词模板
DECOMPOSE_PROMPT = """
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


def decompose_task(task: str, max_subtasks: int = 5) -> Dict[str, Any]:
    """
    使用 LLM 拆解任务
    
    Args:
        task: 原始任务描述
        max_subtasks: 最大子任务数量
    
    Returns:
        包含子任务列表的字典
    """
    prompt = DECOMPOSE_PROMPT.format(
        task=task,
        max_subtasks=max_subtasks
    )
    
    # 调用 LLM（使用 qwen3.5-plus）
    result = subprocess.run(
        [
            "python3", "-c",
            f"""
import json
from openai import OpenAI

client = OpenAI(
    base_url="https://coding.dashscope.aliyuncs.com/compatible-mode/v1",
    api_key="sk-sp-678c06c67fe64d4ab3716fee844d18e8"
)

response = client.chat.completions.create(
    model="qwen3.5-plus",
    messages=[
        {{"role": "system", "content": "你是一个专业的任务规划师，擅长将复杂任务拆解为可并行执行的子任务。输出严格的 JSON 格式。"}},
        {{"role": "user", "content": {json.dumps(prompt)}}}
    ],
    temperature=0.3,
    max_tokens=2000
)

content = response.choices[0].message.content
# 提取 JSON
import re
json_match = re.search(r'```json\\n(.+?)\\n```', content, re.DOTALL)
if json_match:
    print(json_match.group(1))
else:
    # 尝试直接解析
    try:
        data = json.loads(content)
        print(content)
    except:
        print('{{"subtasks": [], "should_decompose": false, "reason": "解析失败"}}')
"""
        ],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.returncode != 0:
        print(f"⚠️  LLM 调用失败：{result.stderr}", file=sys.stderr)
        # 降级：不拆解，直接执行
        return {
            "subtasks": [{"task": task, "agent_hint": "main"}],
            "should_decompose": False,
            "reason": f"LLM 调用失败：{result.stderr}"
        }
    
    try:
        output = result.stdout.strip()
        data = json.loads(output)
        return data
    except json.JSONDecodeError as e:
        print(f"⚠️  JSON 解析失败：{e}", file=sys.stderr)
        return {
            "subtasks": [{"task": task, "agent_hint": "main"}],
            "should_decompose": False,
            "reason": f"JSON 解析失败：{e}"
        }


def get_agent_for_task(agent_hint: str) -> str:
    """根据提示选择 Agent"""
    agent_map = {
        "coder": "coder",
        "video": "video",
        "main": "main"
    }
    return agent_map.get(agent_hint.lower(), "main")


def execute_subtask(task: str, agent_id: str = "main", timeout: int = 300) -> Dict[str, Any]:
    """
    执行单个子任务（通过 sessions_spawn）
    
    注意：这个函数需要在 OpenClaw 环境中调用，使用 sessions_spawn 工具
    """
    # 这个函数在实际使用时会被 OpenClaw 的 Python 环境替换
    # 这里提供一个模拟实现用于测试
    return {
        "task": task,
        "agent_id": agent_id,
        "status": "pending",
        "result": None
    }


def decompose_and_execute(
    task: str,
    max_subtasks: int = 5,
    default_agent: str = "main",
    timeout: int = 300
) -> Dict[str, Any]:
    """
    拆解任务并并行执行
    
    Args:
        task: 原始任务
        max_subtasks: 最大子任务数
        default_agent: 默认 Agent ID
        timeout: 子任务超时时间（秒）
    
    Returns:
        执行结果汇总
    """
    # 1. 拆解任务
    print(f"🔍 正在拆解任务：{task}")
    decomposition = decompose_task(task, max_subtasks)
    
    should_decompose = decomposition.get("should_decompose", False)
    subtasks = decomposition.get("subtasks", [])
    reason = decomposition.get("reason", "")
    
    print(f"📋 拆解结果：{reason}")
    
    if not subtasks:
        return {
            "success": False,
            "message": "任务拆解失败",
            "reason": reason
        }
    
    # 2. 执行子任务
    print(f"🚀 准备执行 {len(subtasks)} 个子任务...")
    
    results = []
    for i, subtask in enumerate(subtasks, 1):
        task_desc = subtask.get("task", "")
        agent_hint = subtask.get("agent_hint", default_agent)
        agent_id = get_agent_for_task(agent_hint)
        
        print(f"  [{i}/{len(subtasks)}] {task_desc[:50]}... → {agent_id}")
        
        # 在实际 OpenClaw 环境中，这里会调用 sessions_spawn
        # 这里提供一个模拟实现
        result = {
            "index": i,
            "task": task_desc,
            "agent_id": agent_id,
            "status": "completed",
            "result": f"子任务 {i} 执行结果（模拟）"
        }
        results.append(result)
    
    # 3. 汇总结果
    return {
        "success": True,
        "original_task": task,
        "should_decompose": should_decompose,
        "subtask_count": len(subtasks),
        "subtasks": subtasks,
        "results": results,
        "summary": f"完成 {len(results)}/{len(subtasks)} 个子任务"
    }


def main():
    """CLI 入口"""
    if len(sys.argv) < 2:
        print("用法：python decompose.py <任务描述>")
        print("示例：python decompose.py '创建一个待办事项应用'")
        sys.exit(1)
    
    task = " ".join(sys.argv[1:])
    result = decompose_and_execute(task)
    
    print("\n" + "="*60)
    print("📊 执行结果汇总")
    print("="*60)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
