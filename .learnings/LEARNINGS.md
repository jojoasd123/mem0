
---

## [LRN-20260207-004] 修正：openclaw.json 修改后无需重启 Gateway

**Logged**: 2026-02-07T20:15:00+08:00
**Priority**: high
**Status**: active
**Area**: configuration, gateway

### 用户更正
用户指出：官方文档说明 Gateway 对 skill 配置或 openclaw.json 是**热加载**的，不需要手动重启。

### 我之前的行为
- 每次修改 openclaw.json 后都执行 `openclaw gateway restart`
- 这是不必要的操作

### 修正后的流程
```
1. 查看真理之书 (qmd search)
   ↓
2. 手动备份当前配置
   cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.backup.$(date +%Y%m%d_%H%M%S)
   ↓
3. 执行修改
   ↓
4. 验证 JSON 语法
   cat ~/.openclaw/openclaw.json | jq . > /dev/null
   ↓
5. ✅ 无需重启，配置热加载生效
```

### 验证
- self-improving-agent 已设置为 enabled: false
- 无需重启即可生效

### Suggested Action
- 更新 MEMORY.md 中的高风险操作规范
- 移除"重启 Gateway"步骤

### Metadata
- Source: user-correction
- Related Files: MEMORY.md, ~/.openclaw/openclaw.json
- Tags: correction, gateway, hot-reload, configuration
- See Also: MEMORY.md#高风险操作规范
