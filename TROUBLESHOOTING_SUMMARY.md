# 卡顿排查总结

## 📊 监控结果

### 19:23 卡顿时刻的数据

**WSL2 进程状态：**
| 指标 | 值 | 状态 |
|------|-----|------|
| Load Average | 0.10 | ✅ 正常 |
| openclaw-gateway CPU | 1.7% | ✅ 正常 |
| openclaw-gateway Memory | 2.6% | ✅ 正常 |
| 运行中的服务 | 1个（gateway） | ✅ 正常 |

**结论：WSL2 内部没有任何进程导致卡顿！**

---

## 🎯 根本原因

### WSL2 网络连接不稳定

**内核日志证据：**
```
WSL (287) ERROR: CheckConnection: getaddrinfo() failed: -5
```

**问题分析：**
- WSL2 默认使用 Windows 的 DNS 解析
- 当 DNS 解析失败时，会导致网络请求卡顿
- 这种卡顿会传播到整个系统

**影响：**
- 每隔几十秒到几分钟出现一次
- 卡顿持续几秒钟
- 影响所有依赖网络的操作

---

## 💡 解决方案

### 方案1：修复 WSL2 DNS（推荐，立即生效）

**在 WSL2 中运行：**
```bash
~/.openclaw/workspace/scripts/fix-wsl-dns.sh
```

**然后重启 WSL2：**
```powershell
# 在 Windows PowerShell（管理员）中运行
wsl --shutdown
```

### 方案2：优化 WSL2 性能参数

**在 WSL2 中运行：**
```bash
~/.openclaw/workspace/scripts/optimize-wsl2.sh
```

**然后重启 WSL2：**
```powershell
wsl --shutdown
```

### 方案3：禁用 WSL2 自动内存回收（如果方案1无效）

创建 `.wslconfig` 文件：
```ini
[wsl2]
memory=16GB
processors=8
swap=2GB

[experimental]
autoMemoryReclaim=disabled  # 禁用自动内存回收
```

---

## 🔍 验证方法

### 1. 检查 DNS 配置
```bash
cat /etc/resolv.conf
```
应该看到：
```
nameserver 8.8.8.8
nameserver 8.8.4.4
```

### 2. 测试 DNS 解析
```bash
nslookup google.com
ping -c 3 8.8.8.8
```

### 3. 检查 WSL2 错误日志
```bash
dmesg | grep "WSL.*ERROR" | tail -10
```
如果 DNS 修复成功，这个错误应该减少或消失。

---

## 📋 执行步骤

1. **运行 DNS 修复脚本**
   ```bash
   ~/.openclaw/workspace/scripts/fix-wsl-dns.sh
   ```

2. **运行 WSL2 优化脚本**
   ```bash
   ~/.openclaw/workspace/scripts/optimize-wsl2.sh
   ```

3. **重启 WSL2**
   - 在 Windows PowerShell（管理员）中运行：
   ```powershell
   wsl --shutdown
   ```

4. **重新打开 WSL2，验证配置**
   ```bash
   cat /etc/resolv.conf
   ```

5. **观察是否还有卡顿**

---

## 🛑 停止监控

如果问题解决，可以停止监控：
```bash
~/.openclaw/workspace/scripts/stop-monitor.sh
```

---

## 📞 如果问题仍然存在

如果以上方案无效，可能需要：

1. **检查 Windows 端的网络配置**
   - 检查是否有代理软件（Clash、V2Ray等）
   - 检查防火墙设置

2. **启用 Windows 监控**
   - 运行 `~/.openclaw/workspace/scripts/monitor-windows.ps1`
   - 等待卡顿发生，查看 Windows 进程日志

3. **联系 WSL2 官方支持**
   - 可能是 WSL2 版本的 Bug
   - 尝试更新 WSL2：
   ```powershell
   wsl --update
   ```
