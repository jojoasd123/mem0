# 云端芋圆连接指南

> 故障时维修云端芋圆的 SSH 连接信息

---

## 连接信息

| 项目 | 值 |
|------|-----|
| **主机地址** | 43.156.232.91 |
| **端口** | 22 |
| **用户名** | ubuntu |
| **认证方式** | SSH 证书（免密码）|

## 证书位置

### WSL 路径（本地芋圆使用）
```
~/.ssh/openclaw.pem
```

### Windows 路径（参考）
```
C:\Users\eko\.ssh\openclaw.pem
```

## 连接命令

```bash
ssh -i ~/.ssh/openclaw.pem -o ConnectTimeout=5 -o StrictHostKeyChecking=no ubuntu@43.156.232.91
```

## 常用诊断命令

```bash
# 检查系统状态
ssh -i ~/.ssh/openclaw.pem ubuntu@43.156.232.91 "uptime && hostname"

# 检查 Gateway 状态
ssh -i ~/.ssh/openclaw.pem ubuntu@43.156.232.91 "systemctl --user status openclaw-gateway.service --no-pager"

# 查看 Gateway 日志
ssh -i ~/.ssh/openclaw.pem ubuntu@43.156.232.91 "tail -n 50 /tmp/openclaw/openclaw-\$(date +%Y-%m-%d).log"

# 重启 Gateway
ssh -i ~/.ssh/openclaw.pem ubuntu@43.156.232.91 "systemctl --user restart openclaw-gateway.service"

# 检查 Tailscale 状态
ssh -i ~/.ssh/openclaw.pem ubuntu@43.156.232.91 "tailscale status"
```

## 故障场景处理

### Gateway 崩溃
```bash
# 1. 检查日志定位错误
ssh -i ~/.ssh/openclaw.pem ubuntu@43.156.232.91 "journalctl --user -u openclaw-gateway.service --no-pager -n 50"

# 2. 运行 doctor 修复
ssh -i ~/.ssh/openclaw.pem ubuntu@43.156.232.91 "openclaw doctor --fix"

# 3. 重启服务
ssh -i ~/.ssh/openclaw.pem ubuntu@43.156.232.91 "systemctl --user restart openclaw-gateway.service"

# 4. 验证
ssh -i ~/.ssh/openclaw.pem ubuntu@43.156.232.91 "curl -s http://localhost:18789/status > /dev/null && echo '✅ Gateway正常' || echo '❌ Gateway异常'"
```

### 连接失败排查
1. 检查本地证书是否存在：`ls -la ~/.ssh/openclaw.pem`
2. 检查网络连通性：`ping 43.156.232.91`
3. 检查 SSH 服务：`ssh -v -i ~/.ssh/openclaw.pem ubuntu@43.156.232.91`
4. 检查云端防火墙/安全组

---

*记录时间: 2026-02-10*
*用途: 云端芋圆故障时的远程维修*
