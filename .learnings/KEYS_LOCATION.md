# 密钥清单（仅位置，无内容）

> ⚠️ 安全提示：本文件只记录密钥位置，绝不包含密钥内容！

## SSH 密钥

| 密钥文件 | 用途 | 权限 |
|---------|------|------|
| `~/.ssh/GitHub` | GitHub 推送认证 | 600 |
| `~/.ssh/yuyuan12.top.key` | 服务器 SSH 连接 | 600 |
| `~/.ssh/.backup-passwd` | 备份加密密码 | 600 |

## API Token / 密钥

| 位置 | 用途 | 加载方式 |
|------|------|---------|
| `~/.ssh/.env` | 各种 API Token（GLM、R2、Telegram 等）| 脚本自动 source |
| `~/.openclaw/openclaw.json` | Gateway Token、Bot Token | OpenClaw 自动读取 |

## 配置详情

### SSH Config
- 文件：`~/.ssh/config`
- 内容：GitHub 使用 `~/.ssh/GitHub` 密钥

### 环境变量文件
- 文件：`~/.ssh/.env`
- 权限：600
- 内容：包含 GLM_API_KEY、CF_API_TOKEN、TELEGRAM_BOT_TOKEN 等

## 自动化状态

- ✅ SSH 配置已写入 `~/.ssh/config`
- ✅ 密钥权限已设置为 600
- ⚠️ ssh-agent 需要每次会话启动（或配置自动启动）

## 提醒

- 永远不要将密钥内容写入任何 .md 文件
- 永远不要将密钥暴露在对话中
- 敏感文件已通过 .gitignore 排除

---

*本文件只记录位置，方便查找，不包含任何密钥内容*
