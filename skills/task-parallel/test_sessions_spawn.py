#!/usr/bin/env python3
"""
测试真实的 sessions_spawn 集成

这个脚本演示如何在 OpenClaw 技能中使用 sessions_spawn 执行真正的并行任务。
"""

import asyncio
import time
from typing import Callable, Any, Dict


# 模拟 sessions_spawn 工具（实际由 OpenClaw 提供）
async def mock_sessions_spawn(
    task: str,
    agentId: str = "main",
    runtime: str = "subagent",
    mode: str = "run",
    timeoutSeconds: int = 300,
    label: str = ""
) -> Dict[str, Any]:
    """
    模拟 sessions_spawn 工具
    
    在真实 OpenClaw 环境中，这会创建一个独立的子代理会话
    """
    print(f"  🚀 [sessions_spawn] 启动子代理：{agentId}")
    print(f"     任务：{task[:60]}...")
    print(f"     标签：{label}")
    
    # 模拟执行延迟
    await asyncio.sleep(2.0)
    
    # 模拟返回结果
    return {
        "sessionKey": f"session_{agentId}_{int(time.time())}",
        "message": f"子代理 {agentId} 执行完成",
        "status": "completed"
    }


async def test_orchestrator_with_sessions_spawn():
    """测试编排器与 sessions_spawn 集成"""
    
    # 导入编排器
    from orchestrator_v2 import YuYuanOrchestratorV2
    
    # 创建编排器
    orchestrator = YuYuanOrchestratorV2(
        max_parallel=10,
        timeout_per_task=300,
        retry_attempts=2,
        enable_monitoring=True,
        enable_critical_path=True,
        enable_llm_aggregation=False
    )
    
    # 注入 sessions_spawn 工具
    orchestrator.set_sessions_spawn(mock_sessions_spawn)
    
    # 执行测试任务
    test_task = "开发一个简单的博客系统，包括用户认证和文章管理"
    
    print("="*60)
    print("🧪 测试：真实的 sessions_spawn 集成")
    print("="*60)
    print(f"\n📌 测试任务：{test_task}\n")
    
    # 执行
    result = await orchestrator.execute(test_task)
    
    # 输出结果
    print("\n" + "="*60)
    print("📊 测试结果")
    print("="*60)
    print(result["aggregated_report"])
    
    print("\n" + "="*60)
    print("📈 性能指标")
    print("="*60)
    metrics = result["metrics"]
    print(f"任务 ID: {metrics['task_id']}")
    print(f"总耗时：{metrics['duration_seconds']}秒")
    print(f"子任务数：{metrics['subtask_count']}")
    print(f"并行组数：{metrics['parallel_count']}")
    print(f"完成率：{metrics['completion_rate']*100:.0f}%")
    print(f"并行效率：{metrics['parallel_efficiency']*100:.0f}%")
    print(f"Agent 使用：{metrics['agent_usage']}")
    
    return result


async def test_parallel_execution():
    """测试真正的并行执行"""
    
    print("="*60)
    print("🧪 测试：并行执行效率")
    print("="*60)
    
    # 导入编排器
    from orchestrator_v2 import YuYuanOrchestratorV2
    
    # 创建编排器
    orchestrator = YuYuanOrchestratorV2(
        max_parallel=5,
        timeout_per_task=60,
        retry_attempts=1,
        enable_monitoring=True,
        enable_critical_path=False,
        enable_llm_aggregation=False
    )
    
    # 注入 sessions_spawn
    orchestrator.set_sessions_spawn(mock_sessions_spawn)
    
    # 测试任务：5 个独立子任务（可以完全并行）
    test_task = "研究 5 个不同的 AI 框架并对比它们的优缺点"
    
    print(f"\n📌 测试任务：{test_task}")
    print(f"📊 预期：5 个子任务并行执行\n")
    
    result = await orchestrator.execute(test_task)
    
    # 分析并行效率
    metrics = result["metrics"]
    
    print("\n" + "="*60)
    print("📊 并行效率分析")
    print("="*60)
    
    # 如果是真正的并行，总耗时应该接近单个任务的耗时
    # 如果是串行，总耗时 = 单个任务耗时 × 任务数
    expected_serial_time = 5 * 2.0  # 5 个任务 × 2 秒/任务 = 10 秒
    actual_time = metrics['duration_seconds']
    efficiency = expected_serial_time / actual_time if actual_time > 0 else 0
    
    print(f"预期串行时间：{expected_serial_time:.1f}秒")
    print(f"实际耗时：{actual_time:.1f}秒")
    print(f"并行加速比：{efficiency:.2f}x")
    
    if efficiency > 3:
        print("✅ 并行效果良好！")
    else:
        print("⚠️  并行效率不高，可能需要优化")
    
    return result


if __name__ == "__main__":
    async def main():
        # 测试 1：基本集成
        await test_orchestrator_with_sessions_spawn()
        
        print("\n\n")
        
        # 测试 2：并行效率
        await test_parallel_execution()
    
    asyncio.run(main())
