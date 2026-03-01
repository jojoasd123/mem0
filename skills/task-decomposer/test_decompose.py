#!/usr/bin/env python3
"""
任务拆解器 - 快速测试脚本

用法：
    python test_decompose.py "创建一个待办事项应用"
"""

import sys
import json

# 模拟 LLM 拆解结果（实际应该调用 LLM）
def mock_decompose(task: str) -> dict:
    """模拟任务拆解"""
    
    # 简单关键词匹配来演示
    if "应用" in task or "网站" in task:
        return {
            "subtasks": [
                {"task": "设计数据库 schema", "agent_hint": "coder"},
                {"task": "实现后端 API", "agent_hint": "coder"},
                {"task": "创建前端界面", "agent_hint": "coder"}
            ],
            "should_decompose": True,
            "reason": "任务复杂，包含多个独立模块"
        }
    elif "bug" in task or "修复" in task:
        return {
            "subtasks": [
                {"task": "定位问题根因", "agent_hint": "coder"},
                {"task": "编写修复代码", "agent_hint": "coder"},
                {"task": "添加回归测试", "agent_hint": "coder"}
            ],
            "should_decompose": True,
            "reason": "Bug 修复需要多步骤验证"
        }
    else:
        return {
            "subtasks": [{"task": task, "agent_hint": "main"}],
            "should_decompose": False,
            "reason": "任务较简单，无需拆解"
        }


def main():
    if len(sys.argv) < 2:
        print("用法：python test_decompose.py <任务描述>")
        print("示例：python test_decompose.py '创建一个待办事项应用'")
        sys.exit(1)
    
    task = " ".join(sys.argv[1:])
    
    print("="*60)
    print("🔍 任务拆解器 - 测试模式")
    print("="*60)
    print(f"\n📌 原始任务：{task}\n")
    
    # 拆解任务
    result = mock_decompose(task)
    
    should_decompose = result["should_decompose"]
    subtasks = result["subtasks"]
    reason = result["reason"]
    
    print(f"📋 拆解结果：{reason}")
    print(f"   子任务数：{len(subtasks)}")
    print()
    
    if should_decompose:
        print("🚀 并行子任务：")
        for i, subtask in enumerate(subtasks, 1):
            agent = subtask.get("agent_hint", "main").upper()
            desc = subtask.get("task", "")
            print(f"   [{i}] {agent}: {desc}")
    else:
        print("💡 直接执行：")
        print(f"   → {subtasks[0]['task']}")
    
    print()
    print("="*60)
    print("✅ 完整 JSON 输出：")
    print("="*60)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
