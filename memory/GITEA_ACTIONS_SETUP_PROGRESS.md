# Gitea Actions 自动部署 - 进度记录

> **开始时间**: 2026-02-17 19:00  
> **目标**: 实现管理员面板代码 push 后自动部署

---

## ✅ 已完成

### 1. Gitea 环境检查
- ✅ Gitea 版本：1.25.4（支持 Actions）
- ✅ Actions 已启用：`ENABLED = true`
- ✅ Gitea 地址：https://tea.runleestore.top/
- ✅ 部署服务器：43.156.77.48
- ✅ SSH 密钥：~/.ssh/gitea_yuyuan.pem

### 2. 基础准备
- ✅ 下载了 Gitea Runner 镜像：`gitea/act_runner:latest`
- ✅ 创建了部署脚本模板
- ✅ 确认了 Gitea 仓库列表

---

## ❓ 待确认信息（关键！）

需要用户提供：

1. **管理员面板前端的 Gitea 仓库名**
   - 示例：`yuyuan/admin-frontend`

2. **管理员面板后端的 Gitea 仓库名**
   - 示例：`yuyuan/admin-backend`

3. **这两个项目在部署服务器上的目录路径**
   - 示例：`/home/ubuntu/admin-frontend`
   - 示例：`/home/ubuntu/admin-backend`

---

## 📝 待完成任务

### 下一步（等用户提供信息后）
- [ ] 完成 Gitea Runner 注册
- [ ] 在 admin-frontend 仓库创建 `.gitea/workflows/deploy.yaml`
- [ ] 在 admin-backend 仓库创建 `.gitea/workflows/deploy.yaml`
- [ ] 配置 SSH 私钥到 Gitea Secrets
- [ ] 测试 push 触发自动部署

---

## ⚠️ 可能遇到的问题清单

| 问题 | 可能原因 | 解决方案 |
|------|---------|---------|
| Runner 注册失败 | Token 不对、网络问题 | 检查 Gitea Runner Token |
| SSH 连接失败 | 密钥不对、权限问题 | 确认 SSH 密钥和权限 |
| Actions 不触发 | 仓库没启用 Actions | 在仓库设置里启用 |
| Docker 命令失败 | 权限、路径问题 | 检查 Docker 和目录 |

---

## 📂 相关文件

- 部署脚本模板：`scripts/gitea-webhook-deploy.sh`
- Webhook 服务器：`scripts/webhook-server.py`
- 本进度文件：`memory/GITEA_ACTIONS_SETUP_PROGRESS.md`

---

## 🎯 方案回顾

### 推荐方案：Gitea Actions
- 精确控制：只有 admin-frontend/admin-backend 有 push 时才部署
- 官方支持，稳定可靠
- 和 GitHub Actions 兼容，以后好扩展

### 备选方案：Webhook + 脚本
- 简单、可靠、易维护
- 不用配置 Runner
- 适合快速上线

---

**最后更新**: 2026-02-17 20:03  
**状态**: ⏸️ 暂停，等待用户提供项目信息
