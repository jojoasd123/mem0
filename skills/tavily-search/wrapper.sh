#!/bin/bash
#
# Tavily Search 包装脚本
# 功能：每次调用时重新加载 .env，确保读取最新密钥
# 创建时间: 2026-02-07
# 约定：以后所有技能脚本都使用此格式
#

set -e

# 加载系统 .env（确保最新）
if [ -f ~/.openclaw/.env ]; then
  # 使用 source 加载（正确处理包含 = 的值）
  set -a  # 自动导出所有变量
  source ~/.openclaw/.env
  set +a  # 关闭自动导出
fi

# 执行真实脚本
exec node "$(dirname "$0")/scripts/search.mjs" "$@"
