#!/bin/bash
# 优化 WSL2 性能配置
# 通过 .wslconfig 文件调整 WSL2 资源分配

WSL_CONFIG="$env:USERPROFILE/.wslconfig"

echo "🔧 配置 WSL2 性能参数..."
echo ""

# 检查是否为 Windows 环境
if command -v powershell.exe &> /dev/null; then
    echo "✅ 检测到 WSL2 环境"

    # 创建 .wslconfig 文件
    powershell.exe -NoProfile -Command "
\$configPath = Join-Path \$env:USERPROFILE '.wslconfig'
\$configContent = @'
[wsl2]
memory=16GB
processors=8
swap=2GB
localhostForwarding=true

[experimental]
autoMemoryReclaim=gradual
sparseVhd=true
'@

Set-Content -Path \$configPath -Value \$configContent -Encoding UTF8
Write-Host '✅ .wslconfig 已创建'
Write-Host \"   位置: \$configPath\"
Write-Host ''
Write-Host '📝 配置内容：'
Get-Content \$configPath
Write-Host ''
Write-Host '⚠️  需要重启 WSL2 才能生效：'
Write-Host '   wsl --shutdown'
Write-Host '   然后重新打开 WSL2'
"
else
    echo "⚠️  此脚本需要在 WSL2 环境中运行"
    echo ""
    echo "📝 手动配置方法："
    echo "   在 Windows 用户目录创建 .wslconfig 文件："
    echo "   C:\\Users\\你的用户名\\.wslconfig"
    echo ""
    echo "   内容如下："
    echo ""
    echo "[wsl2]"
    echo "memory=16GB"
    echo "processors=8"
    echo "swap=2GB"
    echo "localhostForwarding=true"
    echo ""
    echo "[experimental]"
    echo "autoMemoryReclaim=gradual"
    echo "sparseVhd=true"
fi
