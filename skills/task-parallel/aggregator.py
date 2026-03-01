#!/usr/bin/env python3
"""
结果聚合器 - LLM 整合多个子代理结果
"""

import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class AggregatedResult:
    """聚合结果"""
    success: bool
    summary: str
    details: List[Dict[str, Any]]
    conflicts: List[Dict[str, Any]]
    recommendations: List[str]


class ResultAggregator:
    """结果聚合器 - 整合多个子代理结果"""
    
    AGGREGATE_PROMPT = """
你是一个专业的结果整合专家。请将以下多个子任务的执行结果整合为一份完整的报告。

## 原始任务
{original_task}

## 子任务执行结果
{subtask_results}

## 要求
1. **总结**：用 2-3 句话概括整体执行情况
2. **详细结果**：按顺序列出每个子任务的关键成果
3. **冲突检测**：识别结果之间的矛盾或不一致
4. **建议**：基于执行结果，给出后续行动建议

## 输出格式
```json
{{
  "success": true/false,
  "summary": "整体执行总结",
  "details": [
    {{"task_id": 1, "status": "completed", "key_result": "关键成果"}},
    ...
  ],
  "conflicts": [
    {{"description": "冲突描述", "severity": "low/medium/high"}}
  ],
  "recommendations": ["建议 1", "建议 2", ...]
}}
```
"""
    
    def __init__(self, enable_llm_aggregation: bool = True):
        self.enable_llm_aggregation = enable_llm_aggregation
    
    async def aggregate(
        self,
        original_task: str,
        subtasks: List[Dict],
        results: List[Dict]
    ) -> AggregatedResult:
        """
        聚合结果
        
        Args:
            original_task: 原始任务描述
            subtasks: 子任务列表
            results: 执行结果列表
        
        Returns:
            聚合结果
        """
        # 1. 合并结果
        merged = self._merge_results(subtasks, results)
        
        # 2. 检测冲突
        conflicts = self._detect_conflicts(merged)
        
        # 3. 生成总结
        if self.enable_llm_aggregation:
            summary = await self._llm_summarize(original_task, merged)
        else:
            summary = self._rule_based_summarize(original_task, merged)
        
        # 4. 生成建议
        recommendations = self._generate_recommendations(merged, conflicts)
        
        # 5. 判断整体成功
        completed_count = sum(1 for m in merged if m.get("status") == "completed")
        success = completed_count == len(merged) and len(conflicts) == 0
        
        return AggregatedResult(
            success=success,
            summary=summary,
            details=merged,
            conflicts=conflicts,
            recommendations=recommendations
        )
    
    def _merge_results(
        self,
        subtasks: List[Dict],
        results: List[Dict]
    ) -> List[Dict]:
        """合并子任务和结果"""
        result_map = {r["id"]: r for r in results}
        
        merged = []
        for st in subtasks:
            st_id = st["id"]
            result = result_map.get(st_id, {})
            
            merged.append({
                "task_id": st_id,
                "task": st.get("task", ""),
                "agent": st.get("agent", "main"),
                "status": result.get("status", "unknown"),
                "result": result.get("result", ""),
                "error": result.get("error"),
                "duration": result.get("duration", 0),
            })
        
        return merged
    
    def _detect_conflicts(self, merged: List[Dict]) -> List[Dict]:
        """检测冲突"""
        conflicts = []
        
        # 简化版：检查是否有矛盾的结果
        # TODO: 使用 LLM 检测语义冲突
        
        completed = [m for m in merged if m["status"] == "completed"]
        failed = [m for m in merged if m["status"] == "failed"]
        
        # 如果有失败的任务，可能有依赖冲突
        if failed and completed:
            conflicts.append({
                "description": f"{len(failed)} 个子任务失败，可能影响整体结果",
                "severity": "medium"
            })
        
        return conflicts
    
    async def _llm_summarize(self, original_task: str, merged: List[Dict]) -> str:
        """使用 LLM 生成总结"""
        # TODO: 集成 LLM 调用
        # 简化版：返回规则-based 总结
        return self._rule_based_summarize(original_task, merged)
    
    def _rule_based_summarize(self, original_task: str, merged: List[Dict]) -> str:
        """规则-based 总结"""
        completed = sum(1 for m in merged if m["status"] == "completed")
        failed = sum(1 for m in merged if m["status"] == "failed")
        total = len(merged)
        
        if completed == total:
            return f"✅ 所有 {total} 个子任务已完成，整体执行成功。"
        elif completed > 0:
            return f"⚠️ {completed}/{total} 个子任务完成，{failed} 个失败。"
        else:
            return f"❌ 所有 {total} 个子任务均失败。"
    
    def _generate_recommendations(
        self,
        merged: List[Dict],
        conflicts: List[Dict]
    ) -> List[str]:
        """生成建议"""
        recommendations = []
        
        # 根据执行情况生成建议
        failed_tasks = [m for m in merged if m["status"] == "failed"]
        
        if failed_tasks:
            recommendations.append("检查失败子任务的错误信息，修复后重新执行")
        
        if conflicts:
            recommendations.append("解决结果冲突，确保一致性")
        
        if len(merged) > 5:
            recommendations.append("考虑将大型任务进一步分解为更小的子任务")
        
        if not recommendations:
            recommendations.append("任务执行成功，可以交付结果")
        
        return recommendations
    
    def format_report(self, aggregated: AggregatedResult) -> str:
        """格式化报告"""
        lines = []
        
        # 标题
        lines.append("📊 **执行报告**")
        lines.append("")
        
        # 整体状态
        status_icon = "✅" if aggregated.success else "⚠️" if aggregated.conflicts else "❌"
        lines.append(f"{status_icon} **整体状态**: {'成功' if aggregated.success else '部分成功' if any(d['status'] == 'completed' for d in aggregated.details) else '失败'}")
        lines.append("")
        
        # 总结
        lines.append(f"📝 **总结**: {aggregated.summary}")
        lines.append("")
        
        # 详细结果
        lines.append("📋 **详细结果**:")
        for detail in aggregated.details:
            status_icon = "✅" if detail["status"] == "completed" else "❌"
            lines.append(f"  {status_icon} [{detail['task_id']}] {detail['task'][:50]}...")
            if detail.get("result"):
                lines.append(f"     > {detail['result'][:100]}")
        lines.append("")
        
        # 冲突
        if aggregated.conflicts:
            lines.append("⚠️ **冲突检测**:")
            for conflict in aggregated.conflicts:
                severity_icon = {"low": "🟡", "medium": "🟠", "high": "🔴"}.get(conflict["severity"], "⚪")
                lines.append(f"  {severity_icon} {conflict['description']}")
            lines.append("")
        
        # 建议
        lines.append("💡 **建议**:")
        for i, rec in enumerate(aggregated.recommendations, 1):
            lines.append(f"  {i}. {rec}")
        
        return "\n".join(lines)
