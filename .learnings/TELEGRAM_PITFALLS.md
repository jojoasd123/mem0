# Telegram 踩坑记录

## 2026-02-05 多 Bot 群聊问题

### 问题1：群聊消息收不到
**现象：** 哥哥在群里发消息，我没收到，但私聊正常
**原因：** `allowFrom` 配置只包含旧群ID `-5118951374`，但会话使用的是 `-1003881866207`
**解决：** 将两个群ID都加入 `allowFrom` 列表

```json
"allowFrom": [
  "-5118951374",
  "-1003881866207"
]
```

### 问题2：为什么群ID会变？
**解释：** 
- Telegram 普通群升级为超级群后，群ID会从 `-xxx` 变成 `-100xxx`
- `-5118951374` 是原群ID
- `-1003881866207` 是升级后的超级群ID
- 两个ID都保留在配置中以防万一

### 问题3：两个 Bot 在群里如何协作？
**配置：**
- **芋圆**（@yuyuan688bot）：主 Bot，负责日常任务
- **小救**（@yuyuan_rescure_bot）：救援 Bot，在 Docker 中运行，端口 19001

**注意事项：**
1. 两个 Bot 需要分别配置群聊 `allowFrom`
2. 小救的消息要用 `message` 工具发到群里，不要用 `sessions_send` 私发
3. 群聊中 Bot 太多可能导致 webhook 冲突，建议使用轮询模式

### 问题4：Docker 内救援 Bot 配置错误
**现象：** `~/.openclaw-rescue/openclaw.json` 配置了 Feishu 但插件找不到
**原因：** Feishu 插件安装在主目录，救援配置指向错误路径
**解决：** 禁用救援配置的 Feishu 频道

```json
"feishu": {
  "enabled": false
}
```

## 最佳实践

1. **群ID变化时**：同时保留新旧ID在配置中，确保兼容性
2. **多Bot协作**：明确分工，避免重复回复
3. **Docker 内 Bot**：保持配置简洁，避免复杂插件依赖
4. **群聊策略**：Bot 被@时回复，平时保持沉默（NO_REPLY）

## 相关文件

- 主配置：`~/.openclaw/openclaw.json`
- 救援配置：`~/.openclaw-rescue/openclaw.json`
- 救援容器：`emergency-yuyuan` (port 19001)
- 救援 Token：`rescue-token-19001`
