#!/bin/bash
# 快速分析监控日志 - 找出导致卡顿的罪魁祸首

LOG_DIR="$HOME/.openclaw/logs/monitor"

if [ -z "$1" ]; then
    LATEST_LOG=$(ls -t "$LOG_DIR"/resource-*.log 2>/dev/null | head -1)
else
    LATEST_LOG="$1"
fi

if [ ! -f "$LATEST_LOG" ]; then
    echo "❌ 找不到日志文件: $LATEST_LOG"
    exit 1
fi

echo "📊 分析日志: $LATEST_LOG"
echo "========================================"
echo ""

# 1. 统计CPU峰值
echo "🔥 CPU使用率 > 50% 的记录:"
grep -E "^\s+[a-z]+.*[5-9][0-9]\.[0-9]" "$LATEST_LOG" | head -20
echo ""

# 2. 统计内存峰值
echo "💾 内存使用率 > 50% 的记录:"
grep -E "^\s+[a-z]+.*[5-9][0-9]\.[0-9].*[0-9]" "$LATEST_LOG" | head -20
echo ""

# 3. Load Average 峰值
echo "⚡ Load Average 记录:"
grep "Load Average" "$LATEST_LOG" | tail -10
echo ""

# 4. 出现频率最高的进程
echo "🎯 高频进程（Top 10）:"
awk '/^ubuntu|^root/ {print $11}' "$LATEST_LOG" | sort | uniq -c | sort -rn | head -10
echo ""

# 5. 查看最近10分钟的记录
echo "⏰ 最近10分钟的记录（末尾）:"
tail -100 "$LATEST_LOG"
