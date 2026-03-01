#!/usr/bin/env python3
"""
YuYuan Orchestrator - 任务编排系统核心

基于 Kimi K2.5 架构设计的简化版任务编排系统。
"""

import json
import time
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict


# ============================================================================
# 数据模型
# ============================================================================

@dataclass
class SubTask:
    """子任务"""
    id: int
    task: str
    agent: str = "main"
    dependencies: List[int] = field(default_factory=list)
    status: str = "pending"  # pending, running, completed, failed
    result: Optional[str] = None
    error: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    duration: Optional[float] = None
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TaskAnalysis:
    """任务分析结果"""
    intent: str  # development, research, writing, etc.
    complexity: str  # low, medium, high
    estimated_subtasks: int
    required_agents: List[str]
    confidence: float  # 0-1
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ExecutionMetrics:
    """执行指标"""
    task_id: str
    original_task: str
    start_time: float
    end_time: Optional[float] = None
    subtask_count: int = 0
    parallel_count: int = 0
    completion_rate: float = 0.0
    duration_seconds: float = 0.0
    agent_usage: Dict[str, int] = field(default_factory=dict)
    parallel_efficiency: float = 0.0
    avg_duration: float = 0.0
    failure_rate: float = 0.0
    
    def to_dict(self) -> dict:
        return asdict(self)


# ============================================================================
# 任务分析器
# ============================================================================

class TaskAnalyzer:
    """任务分析器 - 意图识别 + 复杂度评估"""
    
    INTENT_KEYWORDS = {
        "development": ["代码", "编程", "功能", "开发", "实现", "bug", "修复", "接口", "API", "数据库", "Python", "脚本", "CSV", "应用", "计算器", "系统", "网站"],
        "research": ["研究", "调研", "分析", "调查", "搜索", "查找", "信息", "资料"],
        "writing": ["写", "文档", "报告", "文章", "邮件", "内容", "文案", "总结"],
        "video": ["视频", "渲染", "剪辑", "动画", "镜头", "画面", "字幕", "影视"],
        "design": ["设计", "UI", "UX", "界面", "原型", "视觉"],
    }
    
    COMPLEXITY_INDICATORS = {
        "high": ["应用", "系统", "平台", "完整", "全面", "复杂", "多个", "包括"],
        "medium": ["功能", "模块", "部分", "一些", "几个"],
        "low": ["简单", "快速", "小", "单个", "一下"],
    }
    
    def analyze(self, task: str) -> TaskAnalysis:
        """分析任务"""
        intent = self._detect_intent(task)
        complexity = self._assess_complexity(task)
        estimated_count = self._estimate_subtasks(complexity, intent)
        required_agents = self._determine_agents(intent)
        confidence = 0.8  # 简化版，固定置信度
        
        return TaskAnalysis(
            intent=intent,
            complexity=complexity,
            estimated_subtasks=estimated_count,
            required_agents=required_agents,
            confidence=confidence
        )
    
    def _detect_intent(self, task: str) -> str:
        """检测意图"""
        scores = {}
        for intent, keywords in self.INTENT_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in task.lower())
            scores[intent] = score
        
        if max(scores.values()) == 0:
            return "general"
        
        return max(scores, key=scores.get)
    
    def _assess_complexity(self, task: str) -> str:
        """评估复杂度"""
        scores = {"high": 0, "medium": 0, "low": 0}
        
        for level, indicators in self.COMPLEXITY_INDICATORS.items():
            for indicator in indicators:
                if indicator in task.lower():
                    scores[level] += 1
        
        if scores["high"] > 0:
            return "high"
        elif scores["medium"] > 0:
            return "medium"
        else:
            return "low"
    
    def _estimate_subtasks(self, complexity: str, intent: str) -> int:
        """估计子任务数量"""
        base_counts = {"low": 1, "medium": 2, "high": 4}
        return base_counts.get(complexity, 2)
    
    def _determine_agents(self, intent: str) -> List[str]:
        """确定需要的 Agent"""
        agent_map = {
            "development": ["coder"],
            "research": ["main"],
            "writing": ["main"],
            "video": ["video"],
            "design": ["coder"],
            "general": ["main"],
        }
        return agent_map.get(intent, ["main"])


# ============================================================================
# 任务分解器
# ============================================================================

class TaskDecomposer:
    """任务分解器 - LLM 驱动的任务拆解"""
    
    DECOMPOSE_PROMPT = """
你是一个专业的任务规划师。请将以下任务拆解成可执行的子任务。

## 任务信息
- **原始任务**: {task}
- **意图**: {intent}
- **复杂度**: {complexity}
- **预计子任务数**: {estimated_count} 个左右

## 要求
1. 每个子任务必须独立、具体、可执行
2. 识别子任务之间的依赖关系
3. 为每个子任务分配合适的 Agent（coder/video/main）
4. 输出严格的 JSON 格式

## Agent 分配规则
- coder: 编程、开发、代码、功能实现
- video: 视频、脚本、渲染、剪辑
- main: 日常对话、信息查询、写作、研究

## 输出格式
```json
{{
  "subtasks": [
    {{
      "id": 1,
      "task": "子任务 1 描述",
      "agent": "coder",
      "dependencies": []
    }},
    {{
      "id": 2,
      "task": "子任务 2 描述",
      "agent": "coder",
      "dependencies": [1]
    }}
  ],
  "should_decompose": true,
  "reason": "拆解原因"
}}
```

## 任务：
{task}
"""
    
    def decompose(self, task: str, analysis: TaskAnalysis) -> List[SubTask]:
        """分解任务"""
        # 简化版：使用规则-based 分解
        # TODO: 集成 LLM 调用
        subtasks_data = self._rule_based_decompose(task, analysis)
        
        subtasks = []
        for i, data in enumerate(subtasks_data, 1):
            subtask = SubTask(
                id=i,
                task=data["task"],
                agent=data.get("agent", "main"),
                dependencies=data.get("dependencies", [])
            )
            subtasks.append(subtask)
        
        return subtasks
    
    def _rule_based_decompose(self, task: str, analysis: TaskAnalysis) -> List[dict]:
        """基于规则的分解（简化版）"""
        intent = analysis.intent
        complexity = analysis.complexity
        
        if intent == "development":
            return self._decompose_development(task, complexity)
        elif intent == "research":
            return self._decompose_research(task, complexity)
        elif intent == "writing":
            return self._decompose_writing(task, complexity)
        elif intent == "video":
            return self._decompose_video(task, complexity)
        else:
            return [{"task": task, "agent": "main", "dependencies": []}]
    
    def _decompose_development(self, task: str, complexity: str) -> List[dict]:
        """开发任务分解"""
        if complexity == "high":
            return [
                {"task": "设计数据库 schema 和数据模型", "agent": "coder", "dependencies": []},
                {"task": "实现后端 API 和业务逻辑", "agent": "coder", "dependencies": [1]},
                {"task": "创建前端界面和交互", "agent": "coder", "dependencies": [2]},
                {"task": "测试和调试", "agent": "coder", "dependencies": [3]},
            ]
        elif complexity == "medium":
            return [
                {"task": "实现核心功能", "agent": "coder", "dependencies": []},
                {"task": "编写测试用例", "agent": "coder", "dependencies": [1]},
            ]
        else:
            return [{"task": task, "agent": "coder", "dependencies": []}]
    
    def _decompose_research(self, task: str, complexity: str) -> List[dict]:
        """研究任务分解"""
        if complexity == "high":
            return [
                {"task": "搜索和收集相关资料", "agent": "main", "dependencies": []},
                {"task": "整理和分析信息", "agent": "main", "dependencies": [1]},
                {"task": "撰写研究报告", "agent": "main", "dependencies": [2]},
            ]
        else:
            return [{"task": task, "agent": "main", "dependencies": []}]
    
    def _decompose_writing(self, task: str, complexity: str) -> List[dict]:
        """写作任务分解"""
        if complexity == "high":
            return [
                {"task": "收集素材和大纲", "agent": "main", "dependencies": []},
                {"task": "撰写初稿", "agent": "main", "dependencies": [1]},
                {"task": "修改和润色", "agent": "main", "dependencies": [2]},
            ]
        else:
            return [{"task": task, "agent": "main", "dependencies": []}]
    
    def _decompose_video(self, task: str, complexity: str) -> List[dict]:
        """视频任务分解"""
        if complexity == "high":
            return [
                {"task": "编写视频脚本", "agent": "video", "dependencies": []},
                {"task": "准备素材和画面", "agent": "video", "dependencies": [1]},
                {"task": "剪辑和后期制作", "agent": "video", "dependencies": [2]},
            ]
        else:
            return [{"task": task, "agent": "video", "dependencies": []}]


# ============================================================================
# DAG 构建器
# ============================================================================

class DAGBuilder:
    """DAG 构建器 - 依赖识别 + 关键路径"""
    
    def build(self, subtasks: List[SubTask]) -> Dict[str, Any]:
        """构建 DAG"""
        # 构建邻接表
        graph = {st.id: st.dependencies for st in subtasks}
        
        # 拓扑排序，确定执行顺序
        sorted_ids = self._topological_sort(graph)
        
        # 识别并行组（无依赖的子任务可以同时执行）
        parallel_groups = self._identify_parallel_groups(subtasks, graph)
        
        # 计算关键路径
        critical_path = self._find_critical_path(subtasks, graph)
        
        return {
            "subtasks": {st.id: st for st in subtasks},
            "graph": graph,
            "sorted_ids": sorted_ids,
            "parallel_groups": parallel_groups,
            "critical_path": critical_path,
        }
    
    def _topological_sort(self, graph: Dict[int, List[int]]) -> List[int]:
        """拓扑排序"""
        in_degree = {node: len(deps) for node, deps in graph.items()}
        queue = [node for node, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            
            for other_node, deps in graph.items():
                if node in deps:
                    in_degree[other_node] -= 1
                    if in_degree[other_node] == 0:
                        queue.append(other_node)
        
        return result
    
    def _identify_parallel_groups(self, subtasks: List[SubTask], graph: Dict[int, List[int]]) -> List[List[int]]:
        """识别并行组"""
        levels = {}
        
        for st in subtasks:
            if not st.dependencies:
                levels[st.id] = 0
            else:
                levels[st.id] = max(levels.get(dep, 0) for dep in st.dependencies) + 1
        
        # 按层级分组
        groups = {}
        for st_id, level in levels.items():
            if level not in groups:
                groups[level] = []
            groups[level].append(st_id)
        
        return [groups[level] for level in sorted(groups.keys())]
    
    def _find_critical_path(self, subtasks: List[SubTask], graph: Dict[int, List[int]]) -> List[int]:
        """查找关键路径（简化版：返回最长依赖链）"""
        # 简化实现：返回第一个并行组
        if not subtasks:
            return []
        
        # TODO: 实现完整的 critical path 算法
        return [subtasks[0].id]


# ============================================================================
# 性能监控器
# ============================================================================

class PerformanceMonitor:
    """性能监控器 - 指标收集 + 日志记录"""
    
    def __init__(self, metrics_path: str = "/home/ubuntu/.openclaw/workspace/orchestrator/metrics"):
        self.metrics_path = Path(metrics_path)
        self.metrics_path.mkdir(parents=True, exist_ok=True)
    
    def record_metrics(self, metrics: ExecutionMetrics):
        """记录指标"""
        timestamp = datetime.fromtimestamp(metrics.start_time).strftime("%Y%m%d_%H%M%S")
        filename = f"metrics_{timestamp}_{metrics.task_id}.json"
        filepath = self.metrics_path / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(metrics.to_dict(), f, ensure_ascii=False, indent=2)
    
    def get_historical_metrics(self, limit: int = 100) -> List[ExecutionMetrics]:
        """获取历史指标"""
        files = sorted(self.metrics_path.glob("metrics_*.json"), reverse=True)[:limit]
        
        metrics_list = []
        for filepath in files:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    metrics = ExecutionMetrics(**data)
                    metrics_list.append(metrics)
            except Exception as e:
                print(f"读取指标失败 {filepath}: {e}")
        
        return metrics_list
    
    def generate_report(self) -> Dict[str, Any]:
        """生成性能报告"""
        metrics_list = self.get_historical_metrics()
        
        if not metrics_list:
            return {"message": "暂无历史数据"}
        
        total_tasks = len(metrics_list)
        avg_duration = sum(m.duration_seconds for m in metrics_list) / total_tasks
        avg_completion_rate = sum(m.completion_rate for m in metrics_list) / total_tasks
        avg_parallel_efficiency = sum(m.parallel_efficiency for m in metrics_list) / total_tasks
        
        return {
            "total_tasks": total_tasks,
            "avg_duration_seconds": round(avg_duration, 2),
            "avg_completion_rate": round(avg_completion_rate * 100, 2),
            "avg_parallel_efficiency": round(avg_parallel_efficiency * 100, 2),
        }


# ============================================================================
# 主编排器
# ============================================================================

class YuYuanOrchestrator:
    """YuYuan Orchestrator - 任务编排系统"""
    
    def __init__(
        self,
        max_parallel: int = 10,
        timeout_per_task: int = 300,
        enable_monitoring: bool = True
    ):
        self.max_parallel = max_parallel
        self.timeout_per_task = timeout_per_task
        self.enable_monitoring = enable_monitoring
        
        self.analyzer = TaskAnalyzer()
        self.decomposer = TaskDecomposer()
        self.dag_builder = DAGBuilder()
        self.monitor = PerformanceMonitor() if enable_monitoring else None
    
    async def execute(self, task: str) -> Dict[str, Any]:
        """执行任务编排"""
        task_id = f"task_{int(time.time())}"
        start_time = time.time()
        
        # 1. 任务分析
        print(f"🔍 正在分析任务...")
        analysis = self.analyzer.analyze(task)
        print(f"📊 意图：{analysis.intent}, 复杂度：{analysis.complexity}")
        
        # 2. 任务分解
        print(f"📋 正在分解任务...")
        subtasks = self.decomposer.decompose(task, analysis)
        print(f"✅ 分解为 {len(subtasks)} 个子任务")
        
        # 3. DAG 构建
        print(f"🔗 构建依赖图...")
        dag = self.dag_builder.build(subtasks)
        print(f"✅ 并行组数：{len(dag['parallel_groups'])}")
        
        # 4. 并行执行（简化版：直接执行，不等待 sessions_spawn）
        print(f"🚀 开始执行...")
        results = await self._execute_subtasks(subtasks, dag)
        
        # 5. 结果汇总
        end_time = time.time()
        duration = end_time - start_time
        
        # 计算指标
        completed = sum(1 for st in subtasks if st.status == "completed")
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
            parallel_efficiency=0.85,  # 简化版：固定值
            avg_duration=round(duration / len(subtasks), 2) if subtasks else 0,
            failure_rate=1 - (completed / len(subtasks)) if subtasks else 0,
        )
        
        # 记录指标
        if self.monitor:
            self.monitor.record_metrics(metrics)
        
        # 6. 返回结果
        return {
            "success": True,
            "task_id": task_id,
            "original_task": task,
            "analysis": analysis.to_dict(),
            "subtasks": [st.to_dict() for st in subtasks],
            "results": results,
            "metrics": metrics.to_dict(),
            "duration_seconds": round(duration, 2),
        }
    
    async def _execute_subtasks(self, subtasks: List[SubTask], dag: Dict) -> List[Dict]:
        """执行子任务（简化版：模拟执行）"""
        results = []
        
        for group in dag["parallel_groups"]:
            print(f"\n📦 执行并行组（{len(group)} 个子任务）...")
            
            for st_id in group:
                subtask = next(st for st in subtasks if st.id == st_id)
                print(f"  [{st_id}] {subtask.agent.upper()}: {subtask.task[:50]}...")
                
                # 模拟执行
                subtask.status = "completed"
                subtask.result = f"子任务 {st_id} 执行完成（模拟结果）"
                subtask.start_time = time.time()
                subtask.end_time = time.time()
                subtask.duration = 0.1
                
                results.append({
                    "id": st_id,
                    "task": subtask.task,
                    "status": "completed",
                    "result": subtask.result,
                })
        
        return results
    
    def _count_agent_usage(self, subtasks: List[SubTask]) -> Dict[str, int]:
        """统计 Agent 使用情况"""
        usage = {}
        for st in subtasks:
            agent = st.agent
            usage[agent] = usage.get(agent, 0) + 1
        return usage


# ============================================================================
# CLI 入口
# ============================================================================

async def main():
    """CLI 入口"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法：python orchestrator.py <任务描述>")
        print("示例：python orchestrator.py '创建一个待办事项应用'")
        sys.exit(1)
    
    task = " ".join(sys.argv[1:])
    
    orchestrator = YuYuanOrchestrator(
        max_parallel=10,
        timeout_per_task=300,
        enable_monitoring=True
    )
    
    result = await orchestrator.execute(task)
    
    print("\n" + "="*60)
    print("📊 执行结果汇总")
    print("="*60)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
