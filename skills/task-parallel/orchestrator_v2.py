#!/usr/bin/env python3
"""
YuYuan Orchestrator V2 - 集成真正的并行执行

Phase 2 新增：
- 执行引擎（sessions_spawn 集成）
- 关键路径调度
- 结果聚合器
"""

import json
import time
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable

# 导入 Phase 1 组件
try:
    from .orchestrator import (
        SubTask, TaskAnalysis, ExecutionMetrics,
        TaskAnalyzer, TaskDecomposer, DAGBuilder, PerformanceMonitor
    )
except ImportError:
    from orchestrator import (
        SubTask, TaskAnalysis, ExecutionMetrics,
        TaskAnalyzer, TaskDecomposer, DAGBuilder, PerformanceMonitor
    )

# 导入 Phase 2 组件
try:
    from .executor import ExecutionEngine, CriticalPathScheduler, SubAgentResult
    from .aggregator import ResultAggregator, AggregatedResult
except ImportError:
    from executor import ExecutionEngine, CriticalPathScheduler, SubAgentResult
    from aggregator import ResultAggregator, AggregatedResult


class TaskParallel:
    """Task Parallel - 任务并行执行系统"""
    
    def __init__(
        self,
        max_parallel: int = 10,
        timeout_per_task: int = 300,
        retry_attempts: int = 2,
        enable_monitoring: bool = True,
        enable_critical_path: bool = True,
        enable_llm_aggregation: bool = True
    ):
        self.max_parallel = max_parallel
        self.timeout_per_task = timeout_per_task
        self.retry_attempts = retry_attempts
        self.enable_monitoring = enable_monitoring
        self.enable_critical_path = enable_critical_path
        self.enable_llm_aggregation = enable_llm_aggregation
        
        # Phase 1 组件
        self.analyzer = TaskAnalyzer()
        self.decomposer = TaskDecomposer()
        self.dag_builder = DAGBuilder()
        self.monitor = PerformanceMonitor() if enable_monitoring else None
        
        # Phase 2 组件
        self.executor = ExecutionEngine(
            max_parallel=max_parallel,
            timeout_per_task=timeout_per_task,
            retry_attempts=retry_attempts
        )
        self.scheduler = CriticalPathScheduler() if enable_critical_path else None
        self.aggregator = ResultAggregator(enable_llm_aggregation)
        
        # sessions_spawn 工具（由 OpenClaw 注入）
        self.sessions_spawn_func: Optional[Callable] = None
    
    def set_sessions_spawn(self, func: Callable):
        """设置 sessions_spawn 工具函数"""
        self.sessions_spawn_func = func
        self.executor.set_sessions_spawn(func)
    
    async def execute(self, task: str) -> Dict[str, Any]:
        """执行任务编排"""
        task_id = f"task_{int(time.time())}"
        start_time = time.time()
        
        print("="*60)
        print("🚀 Task Parallel - 任务并行执行")
        print("="*60)
        
        # 1. 任务分析
        print(f"\n🔍 正在分析任务...")
        analysis = self.analyzer.analyze(task)
        print(f"📊 意图：{analysis.intent}, 复杂度：{analysis.complexity}")
        
        # 2. 任务分解
        print(f"\n📋 正在分解任务...")
        subtasks = self.decomposer.decompose(task, analysis)
        print(f"✅ 分解为 {len(subtasks)} 个子任务")
        
        # 打印子任务
        for st in subtasks:
            deps = f"（依赖：{st.dependencies}）" if st.dependencies else "（无依赖）"
            print(f"  [{st.id}] {st.agent.upper()}: {st.task}{deps}")
        
        # 3. DAG 构建
        print(f"\n🔗 构建依赖图...")
        dag = self.dag_builder.build(subtasks)
        print(f"✅ 并行组数：{len(dag['parallel_groups'])}")
        
        # 4. 关键路径优化（Phase 2 新增）
        if self.enable_critical_path and self.scheduler:
            print(f"\n⚡ 关键路径优化...")
            optimized_groups = self.scheduler.schedule_by_critical_path(subtasks, dag)
            dag["parallel_groups"] = optimized_groups
        
        # 5. 并行执行（Phase 2 新增 - 真正的执行）
        print(f"\n🚀 开始并行执行...")
        results = await self.executor.execute_parallel(subtasks, dag)
        
        # 6. 结果聚合（Phase 2 新增）
        print(f"\n📊 正在聚合结果...")
        subtasks_dict = [st.to_dict() for st in subtasks]
        results_dict = [
            {
                "id": r.task_id,
                "status": r.status,
                "result": r.result,
                "error": r.error,
                "duration": r.duration,
            }
            for r in results
        ]
        
        aggregated = await self.aggregator.aggregate(task, subtasks_dict, results_dict)
        aggregated_report = self.aggregator.format_report(aggregated)
        
        # 7. 计算指标
        end_time = time.time()
        duration = end_time - start_time
        
        completed = sum(1 for r in results if r.status == "completed")
        metrics = ExecutionMetrics(
            task_id=task_id,
            original_task=task,
            start_time=start_time,
            end_time=end_time,
            subtask_count=len(subtasks),
            parallel_count=len(dag["parallel_groups"]),
            completion_rate=completed / len(subtasks) if subtasks else 0,
            duration_seconds=round(duration, 2),
            agent_usage=self._count_agent_usage(subtasks),
            parallel_efficiency=self._calculate_parallel_efficiency(results, duration),
            avg_duration=round(sum(r.duration for r in results) / len(results), 2) if results else 0,
            failure_rate=1 - (completed / len(subtasks)) if subtasks else 0,
        )
        
        # 8. 记录指标
        if self.monitor:
            self.monitor.record_metrics(metrics)
        
        # 9. 返回完整结果
        return {
            "success": aggregated.success,
            "task_id": task_id,
            "original_task": task,
            "analysis": analysis.to_dict(),
            "subtasks": subtasks_dict,
            "execution_results": results_dict,
            "aggregated_report": aggregated_report,
            "metrics": metrics.to_dict(),
            "duration_seconds": round(duration, 2),
        }
    
    def _count_agent_usage(self, subtasks: List[SubTask]) -> Dict[str, int]:
        """统计 Agent 使用情况"""
        usage = {}
        for st in subtasks:
            agent = st.agent
            usage[agent] = usage.get(agent, 0) + 1
        return usage
    
    def _calculate_parallel_efficiency(
        self,
        results: List[SubAgentResult],
        total_duration: float
    ) -> float:
        """计算并行效率"""
        if not results or total_duration == 0:
            return 0.0
        
        # 串行时间（所有任务耗时之和）
        serial_time = sum(r.duration for r in results)
        
        # 并行效率 = 串行时间 / 实际时间
        efficiency = serial_time / total_duration
        
        # 限制在 0-1 之间
        return min(1.0, max(0.0, efficiency))


# ============================================================================
# CLI 入口
# ============================================================================

async def main():
    """CLI 入口"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法：python orchestrator_v2.py <任务描述>")
        print("示例：python orchestrator_v2.py '创建一个待办事项应用'")
        sys.exit(1)
    
    task = " ".join(sys.argv[1:])
    
    # 创建任务并行执行器
    parallel = TaskParallel(
        max_parallel=10,
        timeout_per_task=300,
        retry_attempts=2,
        enable_monitoring=True,
        enable_critical_path=True,
        enable_llm_aggregation=False  # CLI 模式暂不启用 LLM 聚合
    )
    
    result = await parallel.execute(task)
    
    print("\n" + "="*60)
    print("📊 最终报告")
    print("="*60)
    print(result["aggregated_report"])
    
    print("\n" + "="*60)
    print("📈 性能指标")
    print("="*60)
    metrics = result["metrics"]
    print(f"总耗时：{metrics['duration_seconds']}秒")
    print(f"并行效率：{metrics['parallel_efficiency']*100:.0f}%")
    print(f"完成率：{metrics['completion_rate']*100:.0f}%")
    print(f"失败率：{metrics['failure_rate']*100:.0f}%")
    print(f"Agent 使用：{metrics['agent_usage']}")


if __name__ == "__main__":
    asyncio.run(main())
