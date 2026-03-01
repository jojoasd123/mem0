#!/bin/bash
# 修复 WSL2 DNS 问题
# 问题：WSL2 默认使用 Windows DNS，可能导致解析失败

echo "🔧 修复 WSL2 DNS 配置..."

# 备份原配置
sudo cp /etc/resolv.conf /etc/resolv.conf.backup.$(date +%Y%m%d_%H%M%S)

# 使用公共 DNS（Google DNS）
sudo tee /etc/resolv.conf > /dev/null <<EOF
nameserver 8.8.8.8
nameserver 8.8.4.4
nameserver 114.114.114.114
EOF

# 防止 WSL2 自动覆盖 /etc/resolv.conf
if [ -f /etc/wsl.conf ]; then
    sudo cp /etc/wsl.conf /etc/wsl.conf.backup.$(date +%Y%m%d_%H%M%S)
fi

sudo tee /etc/wsl.conf > /dev/null <<EOF
[network]
generateResolvConf = false
EOF

echo "✅ DNS 配置已更新"
echo ""
echo "📝 需要重启 WSL2 才能生效："
echo "   在 Windows PowerShell（管理员）中运行："
echo "   wsl --shutdown"
echo "   然后重新打开 WSL2"
echo ""
echo "🔍 当前 DNS 配置："
cat /etc/resolv.conf
