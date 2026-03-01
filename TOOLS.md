

---

### Telegram Bots

**主 Bot - 芋圆 (@yuyuan688bot)**
- Token: `8572...vQZ8`
- 配置: `~/.openclaw/openclaw.json`
- Gateway: port 18789

**救援 Bot - 小救 (@yuyuan_rescure_bot)**
- Token: `8450...O8Gw`
- 容器: `emergency-yuyuan`
- Gateway: `http://localhost:19001`
- Token: `rescue-token-19001`
- 工作目录: `/home/ubuntu/emergency-yuyuan/workspace`

**群聊配置注意事项：**
- 群ID升级问题：普通群 `-5118951374` → 超级群 `-1003881866207`
- 需要在 `allowFrom` 中同时保留两个ID
- 踩坑记录: `.learnings/TELEGRAM_PITFALLS.md`

<!-- antfarm:workflows -->
# Antfarm Workflows

Antfarm CLI (always use full path to avoid PATH issues):
`node ~/.openclaw/workspace/antfarm/dist/cli/cli.js`

Commands:
- Install: `node ~/.openclaw/workspace/antfarm/dist/cli/cli.js workflow install <name>`
- Run: `node ~/.openclaw/workspace/antfarm/dist/cli/cli.js workflow run <workflow-id> "<task>"`
- Status: `node ~/.openclaw/workspace/antfarm/dist/cli/cli.js workflow status "<task title>"`
- Logs: `node ~/.openclaw/workspace/antfarm/dist/cli/cli.js logs`

Workflows are self-advancing via per-agent cron jobs. No manual orchestration needed.
<!-- /antfarm:workflows -->

