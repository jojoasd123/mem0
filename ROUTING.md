# 任务路由规则

## 自动路由逻辑

Main Agent 收到消息后，根据关键词自动分发给对应的 Agent：

### 🎯 路由判断规则

| 任务类型 | 关键词 | 执行 Agent | 模型 |
|---------|--------|-----------|------|
| **编程** | 代码/编程/Python/脚本/修复 bug/功能/接口/API/数据库/SQL/前端/后端/调试 | coder | glm-4.7 |
| **视频** | 视频/脚本/Remotion/画面/镜头/动画/渲染/剪辑/字幕/特效 | video | qwen3.5-plus |
| **日常** | 其他 | main | qwen3.5-plus |

### 📋 路由执行方式

Main 使用 `sessions_spawn` 创建子代理任务：

```javascript
sessions_spawn({
  agentId: "coder",  // 或 "video"
  runtime: "subagent",
  mode: "run",
  task: "具体任务描述"
})
```

### ⚠️ 注意事项

1. **用户无感知**：子代理执行过程用户看不到，只看到最终结果
2. **Session 隔离**：每个 Agent 有独立的 session 存储
3. **上下文传递**：Main 需要把完整上下文传递给子代理
4. **结果汇总**：子代理完成后自动汇报，Main 转发给用户

---

*最后更新：2026-03-01*
