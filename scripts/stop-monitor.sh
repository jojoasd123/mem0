#!/bin/bash
# 停止所有监控进程

echo "🛑 停止监控进程..."

# 停止 WSL2 资源监控
if ps aux | grep -v grep | grep -q "monitor-resources.sh"; then
    pkill -f monitor-resources.sh
    echo "✅ 已停止 WSL2 资源监控"
fi

# 停止 Windows 进程监控
if ps aux | grep -v grep | grep -q "monitor-windows.sh"; then
    pkill -f monitor-windows.sh
    echo "✅ 已停止 Windows 进程监控"
fi

echo ""
echo "📊 监控日志位置:"
echo "  - WSL2: ~/.openclaw/logs/monitor/"
echo "  - Windows: ~/Desktop/monitor-logs/"
echo ""
echo "查看日志:"
echo "  ~/.openclaw/workspace/scripts/analyze-monitor.sh"
