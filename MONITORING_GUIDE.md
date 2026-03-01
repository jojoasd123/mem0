# 卡顿排查方案 - 已部署监控

## ✅ 已完成的操作

### 1. WSL2 监控（已启动）
- **脚本位置**: `~/.openclaw/workspace/scripts/monitor-resources.sh`
- **进程ID**: 1202
- **日志位置**: `~/.openclaw/logs/monitor/resource-*.log`
- **监控频率**: 每5秒记录一次

**监控内容**:
- Top 10 CPU 进程
- Top 10 Memory 进程
- 运行中的 systemd 服务
- Load Average（系统负载）

### 2. Windows 监控（需要手动启动）
**PowerShell 脚本位置**: `~/.openclaw/workspace/scripts/monitor-windows.ps1`
可通过WSL访问: `explorer.exe ~/.openclaw/workspace/scripts/`

---

## 🔍 下一步操作

### 方案1：等待卡顿发生（推荐）
1. **继续正常使用电脑**
2. 等待卡顿发生后，告诉我"卡了！"
3. 我会立即分析日志，找出罪魁祸首

### 方案2：同时启用 Windows 监控
在 Windows PowerShell（管理员）中运行：

```powershell
# 1. 复制脚本到桌面
cp /home/ubuntu/.openclaw/workspace/scripts/monitor-windows.ps1 $env:USERPROFILE\Desktop\

# 2. 在后台运行（PowerShell中）
Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File $env:USERPROFILE\Desktop\monitor-windows.ps1" -WindowStyle Hidden
```

---

## 📊 查看监控结果

### 查看 WSL2 日志
```bash
# 查看最新日志
~/.openclaw/workspace/scripts/analyze-monitor.sh

# 或直接查看原始日志
tail -100 ~/.openclaw/logs/monitor/resource-*.log
```

### 查看 Windows 日志
日志文件位于: `C:\Users\你的用户名\Desktop\monitor-logs\win-resource-*.log`

---

## 🎯 常见问题排查

### 如果卡顿时日志显示：
1. **openclaw-gateway CPU 飙高** → 可能是某个AI任务在运行
2. **v2ray CPU 飙高** → 代理服务可能在处理大量流量
3. **tailscaled CPU 飙高** → Tailscale 网络连接问题
4. **snapd 相关进程** → Snap 包管理系统在后台工作
5. **WSL2 进程** → 可能是 Windows 资源分配问题

### 快速停止监控
```bash
# 停止 WSL2 监控
kill 1202

# 停止 Windows 监控（在任务管理器中结束 PowerShell 进程）
```

---

## 💡 分析建议

告诉我以下信息，我可以更精准地定位问题：
1. 卡顿发生的大致时间
2. 卡顿持续多久（几秒、几十秒？）
3. 卡顿时是否在做特定操作（打开软件、游戏、复制文件等）

我会根据日志找出那个时间点哪个进程在捣乱！
