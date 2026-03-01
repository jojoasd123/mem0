#!/bin/bash
# 监控 Windows 11 进程（通过 WSL2 获取）
# 需要配置 WSL2 访问 Windows 进程

LOG_DIR="$HOME/.openclaw/logs/monitor"
mkdir -p "$LOG_DIR"

LOG_FILE="$LOG_DIR/windows-processes-$(date +%Y%m%d-%H%M%S).log"
MAX_LOG_SIZE=$((10 * 1024 * 1024))  # 10MB

echo "=== Windows 进程监控启动: $(date) ===" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

# 监控循环
while true; do
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    
    # 检查日志文件大小，超过则轮换
    if [ -f "$LOG_FILE" ] && [ $(stat -c%s "$LOG_FILE" 2>/dev/null || echo 0) -gt $MAX_LOG_SIZE ]; then
        LOG_FILE="$LOG_DIR/windows-processes-$(date +%Y%m%d-%H%M%S).log"
        echo "=== 日志轮换: $(date) ===" | tee -a "$LOG_FILE"
    fi
    
    echo "" >> "$LOG_FILE"
    echo "[$TIMESTAMP] --- Windows Top 10 CPU ---" >> "$LOG_FILE"
    
    # 通过 WSL2 访问 Windows 任务管理器数据
    # 使用 PowerShell 从 WSL2 获取 Windows 进程
    powershell.exe -NoProfile -Command "Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 | Format-Table -AutoSize" 2>/dev/null >> "$LOG_FILE" || echo "无法获取 Windows 进程信息" >> "$LOG_FILE"
    
    echo "" >> "$LOG_FILE"
    echo "[$TIMESTAMP] --- Windows Top 10 Memory ---" >> "$LOG_FILE"
    powershell.exe -NoProfile -Command "Get-Process | Sort-Object WorkingSet -Descending | Select-Object -First 10 | Format-Table -AutoSize" 2>/dev/null >> "$LOG_FILE" || echo "无法获取 Windows 进程信息" >> "$LOG_FILE"
    
    echo "" >> "$LOG_FILE"
    echo "[$TIMESTAMP] --- Windows CPU Usage ---" >> "$LOG_FILE"
    powershell.exe -NoProfile -Command "Get-WmiObject win32_processor | Measure-Object -property LoadPercentage -Average | Select Average" 2>/dev/null >> "$LOG_FILE" || echo "无法获取 CPU 使用率" >> "$LOG_FILE"
    
    echo "========================================" >> "$LOG_FILE"
    
    sleep 10
done
