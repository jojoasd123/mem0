#!/usr/bin/env python3
"""
执行引擎 - 集成 sessions_spawn 实现真正的并行执行
"""

import asyncio
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass

try:
    from .orchestrator import SubTask, ExecutionMetrics
except ImportError:
    from orchestrator import SubTask, ExecutionMetrics


@dataclass
class SubAgentResult:
    """子代理执行结果"""
    task_id: int
    status: str  # completed, failed, timeout
    result: Optional[str] = None
    error: Optional[str] = None
    duration: float = 0.0
    session_key: Optional[str] = None


class ExecutionEngine:
    """执行引擎 - 并行执行子任务"""
    
    def __init__(
        self,
        max_parallel: int = 10,
        timeout_per_task: int = 300,
        retry_attempts: int = 2
    ):
        self.max_parallel = max_parallel
        self.timeout_per_task = timeout_per_task
        self.retry_attempts = retry_attempts
        
        # sessions_spawn 工具函数（由 OpenClaw 注入）
        self.sessions_spawn_func: Optional[Callable] = None
    
    def set_sessions_spawn(self, func: Callable):
        """设置 sessions_spawn 工具函数"""
        self.sessions_spawn_func = func
    
    async def execute_parallel(
        self,
        subtasks: List[SubTask],
        dag: Dict[str, Any]
    ) -> List[SubAgentResult]:
        """
        并行执行子任务
        
        Args:
            subtasks: 子任务列表
            dag: DAG 结构（包含 parallel_groups）
        
        Returns:
            子代理执行结果列表
        """
        all_results = []
        parallel_groups = dag.get("parallel_groups", [])
        
        print(f"\n🚀 开始并行执行（最大并发：{self.max_parallel}）...")
        
        # 按并行组顺序执行
        for group_idx, group in enumerate(parallel_groups, 1):
            print(f"\n📦 执行第 {group_idx}/{len(parallel_groups)} 组（{len(group)} 个子任务）...")
            
            # 获取该组的子任务
            group_subtasks = [st for st in subtasks if st.id in group]
            
            # 检查依赖是否都完成
            for st in group_subtasks:
                if not self._check_dependencies(st, all_results):
                    print(f"  ⚠️  [{st.id}] 依赖未完成，跳过")
                    continue
            
            # 并行执行该组子任务
            tasks = []
            for st in group_subtasks:
                task = asyncio.create_task(self._execute_with_retry(st))
                tasks.append(task)
            
            # 等待该组所有任务完成
            group_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 处理结果
            for i, result in enumerate(group_results):
                st = group_subtasks[i]
                if isinstance(result, Exception):
                    print(f"  ❌ [{st.id}] 执行失败：{str(result)}")
                    all_results.append(SubAgentResult(
                        task_id=st.id,
                        status="failed",
                        error=str(result)
                    ))
                else:
                    sub_result: SubAgentResult = result
                    status_icon = "✅" if sub_result.status == "completed" else "❌"
                    print(f"  {status_icon} [{st.id}] {sub_result.status}: {st.task[:40]}...")
                    all_results.append(sub_result)
        
        return all_results
    
    def _check_dependencies(
        self,
        subtask: SubTask,
        completed_results: List[SubAgentResult]
    ) -> bool:
        """检查依赖是否都完成"""
        if not subtask.dependencies:
            return True
        
        completed_ids = {r.task_id for r in completed_results if r.status == "completed"}
        return all(dep_id in completed_ids for dep_id in subtask.dependencies)
    
    async def _execute_with_retry(self, subtask: SubTask) -> SubAgentResult:
        """带重试的执行"""
        last_error = None
        
        for attempt in range(1, self.retry_attempts + 1):
            try:
                result = await self._execute_single(subtask, attempt)
                if result.status == "completed":
                    return result
                last_error = result.error
            except Exception as e:
                last_error = str(e)
            
            if attempt < self.retry_attempts:
                print(f"    ↻ 重试 {attempt}/{self.retry_attempts}...")
                await asyncio.sleep(1.0 * attempt)  # 指数退避
        
        # 所有重试都失败
        return SubAgentResult(
            task_id=subtask.id,
            status="failed",
            error=f"重试 {self.retry_attempts} 次后仍失败：{last_error}"
        )
    
    async def _execute_single(
        self,
        subtask: SubTask,
        attempt: int = 1
    ) -> SubAgentResult:
        """执行单个子任务"""
        start_time = time.time()
        
        print(f"    → 启动子代理：{subtask.agent} - {subtask.task[:40]}...")
        
        # 如果没有 sessions_spawn 工具，使用模拟执行
        if not self.sessions_spawn_func:
            print(f"    ⚠️  未提供 sessions_spawn 工具，使用模拟执行")
            await asyncio.sleep(0.5)  # 模拟延迟
            
            return SubAgentResult(
                task_id=subtask.id,
                status="completed",
                result=f"子任务 {subtask.id} 执行完成（模拟结果，尝试 {attempt}）",
                duration=time.time() - start_time
            )
        
        # 使用 sessions_spawn 执行
        try:
            # 构建任务描述
            task_description = self._build_task_description(subtask)
            
            # 调用 sessions_spawn
            session_result = await self.sessions_spawn_func(
                task=task_description,
                agentId=subtask.agent,
                runtime="subagent",
                mode="run",
                timeoutSeconds=self.timeout_per_task,
                label=f"orchestrator_task_{subtask.id}"
            )
            
            duration = time.time() - start_time
            
            return SubAgentResult(
                task_id=subtask.id,
                status="completed",
                result=session_result.get("message", "执行完成"),
                duration=duration,
                session_key=session_result.get("sessionKey")
            )
        
        except asyncio.TimeoutError:
            return SubAgentResult(
                task_id=subtask.id,
                status="timeout",
                error=f"执行超时（>{self.timeout_per_task}秒）",
                duration=time.time() - start_time
            )
        
        except Exception as e:
            return SubAgentResult(
                task_id=subtask.id,
                status="failed",
                error=str(e),
                duration=time.time() - start_time
            )
    
    def _build_task_description(self, subtask: SubTask) -> str:
        """构建任务描述"""
        return f"""
你是 {subtask.agent} Agent。请执行以下任务：

**任务**: {subtask.task}

**要求**:
- 专注完成这个具体任务
- 输出清晰、结构化的结果
- 如果遇到问题，清晰说明原因

**上下文**: 这是大型任务的子任务 #{subtask.id}
"""


class CriticalPathScheduler:
    """关键路径调度器 - 优先执行耗时长的任务"""
    
    def __init__(self):
        self.task_duration_history: Dict[str, float] = {}  # 任务模式 -> 平均耗时
    
    def schedule_by_critical_path(
        self,
        subtasks: List[SubTask],
        dag: Dict[str, Any]
    ) -> List[List[int]]:
        """
        按关键路径重新排序并行组
        
        策略：
        1. 估算每个子任务的耗时
        2. 在并行组内，按耗时降序排列（长的先执行）
        3. 返回优化后的并行组顺序
        """
        parallel_groups = dag.get("parallel_groups", [])
        optimized_groups = []
        
        for group in parallel_groups:
            # 估算组内每个任务的耗时
            task_estimates = []
            for task_id in group:
                subtask = next((st for st in subtasks if st.id == task_id), None)
                if subtask:
                    estimated_duration = self._estimate_duration(subtask)
                    task_estimates.append((task_id, estimated_duration))
            
            # 按耗时降序排列（关键任务优先）
            task_estimates.sort(key=lambda x: x[1], reverse=True)
            optimized_order = [t[0] for t in task_estimates]
            optimized_groups.append(optimized_order)
            
            print(f"  📊 并行组优化：{group} → {optimized_order}")
        
        return optimized_groups
    
    def _estimate_duration(self, subtask: SubTask) -> float:
        """估算任务耗时"""
        # 简化版：根据任务描述长度和 Agent 类型估算
        base_duration = 10.0  # 基础 10 秒
        
        # 任务描述越长，估计耗时越长
        length_factor = len(subtask.task) / 50.0
        
        # 不同 Agent 的基础速度不同
        agent_factor = {
            "coder": 2.0,    # 编码任务通常更慢
            "video": 3.0,    # 视频任务最慢
            "main": 1.0,     # 日常任务较快
        }.get(subtask.agent, 1.0)
        
        # 历史数据修正
        history_factor = self.task_duration_history.get(
            f"{subtask.agent}_{subtask.task[:20]}",
            1.0
        )
        
        estimated = base_duration * length_factor * agent_factor * history_factor
        return estimated
    
    def update_history(self, task_pattern: str, actual_duration: float):
        """更新历史耗时数据"""
        # 指数移动平均
        old_avg = self.task_duration_history.get(task_pattern, actual_duration)
        new_avg = 0.7 * old_avg + 0.3 * actual_duration
        self.task_duration_history[task_pattern] = new_avg
