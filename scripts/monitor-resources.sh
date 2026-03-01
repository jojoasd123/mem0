#!/bin/bash
# 资源监控脚本 - 记录导致卡顿的进程
# 每5秒记录一次，自动轮转日志文件

LOG_DIR="$HOME/.openclaw/logs/monitor"
mkdir -p "$LOG_DIR"

# 日志文件（带时间戳）
LOG_FILE="$LOG_DIR/resource-$(date +%Y%m%d-%H%M%S).log"
MAX_LOG_SIZE=$((10 * 1024 * 1024))  # 10MB

# 头部信息
echo "=== 资源监控启动: $(date) ===" | tee -a "$LOG_FILE"
echo "监控间隔: 5秒" | tee -a "$LOG_FILE"
echo "日志文件: $LOG_FILE" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

# 轮换旧日志（保留最近3个）
ls -t "$LOG_DIR"/resource-*.log 2>/dev/null | tail -n +4 | xargs rm -f 2>/dev/null

# 监控循环
while true; do
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    
    # 检查日志文件大小，超过则轮换
    if [ -f "$LOG_FILE" ] && [ $(stat -c%s "$LOG_FILE" 2>/dev/null || echo 0) -gt $MAX_LOG_SIZE ]; then
        LOG_FILE="$LOG_DIR/resource-$(date +%Y%m%d-%H%M%S).log"
        echo "=== 日志轮换: $(date) ===" | tee -a "$LOG_FILE"
    fi
    
    echo "" >> "$LOG_FILE"
    echo "[$TIMESTAMP] --- Top 10 CPU ---" >> "$LOG_FILE"
    ps aux --sort=-%cpu | head -11 >> "$LOG_FILE"
    
    echo "" >> "$LOG_FILE"
    echo "[$TIMESTAMP] --- Top 10 Memory ---" >> "$LOG_FILE"
    ps aux --sort=-%mem | head -11 >> "$LOG_FILE"
    
    echo "" >> "$LOG_FILE"
    echo "[$TIMESTAMP] --- Running Services ---" >> "$LOG_FILE"
    systemctl --user list-units --type=service --state=running >> "$LOG_FILE"
    
    echo "" >> "$LOG_FILE"
    echo "[$TIMESTAMP] --- Load Average ---" >> "$LOG_FILE"
    cat /proc/loadavg >> "$LOG_FILE"
    
    echo "========================================" >> "$LOG_FILE"
    
    sleep 5
done
