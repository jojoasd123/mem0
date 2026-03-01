#!/bin/bash
# detect-yuyuan-env.sh - 自动检测芋圆环境

IS_WSL=false
IS_CLOUD=false
YUYUAN_ENV="unknown"

if grep -q "WSL2" /proc/version 2>/dev/null; then
    IS_WSL=true
    YUYUAN_ENV="local"
fi

if [ -n "$WSL_DISTRO_NAME" ] || [ -n "$WSL_INTEROP" ]; then
    IS_WSL=true
    YUYUAN_ENV="local"
fi

HOSTNAME=$(hostname)
if [ "$HOSTNAME" = "VM-0-12-ubuntu" ]; then
    IS_CLOUD=true
    YUYUAN_ENV="cloud"
fi

export YUYUAN_ENV
export IS_WSL
export IS_CLOUD

if [ "$YUYUAN_ENV" = "cloud" ]; then
    export YUYUAN_GIT_BRANCH="main"
    export YUYUAN_NAME="云端芋圆"
elif [ "$YUYUAN_ENV" = "local" ]; then
    export YUYUAN_GIT_BRANCH="local"
    export YUYUAN_NAME="本地芋圆"
else
    export YUYUAN_GIT_BRANCH="main"
    export YUYUAN_NAME="未知芋圆"
fi

if [ "${1:-}" = "--verbose" ]; then
    echo "🍡 芋圆环境检测"
    echo "================"
    echo "环境: $YUYUAN_ENV"
    echo "名称: $YUYUAN_NAME"
    echo "Git分支: $YUYUAN_GIT_BRANCH"
    echo "Hostname: $HOSTNAME"
fi
