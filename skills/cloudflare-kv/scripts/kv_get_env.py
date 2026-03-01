#!/usr/bin/env python3
"""
Cloudflare KV 环境变量获取器

从 KV 自动读取密钥并导出为环境变量，用于脚本使用。

用法：
1. 直接输出值（用于脚本变量）：
   BRAVE_KEY=$(python3 kv_get_env.py BRAVE_API_KEY)

2. 导出为 shell 环境变量：
   eval $(python3 kv_get_env.py BRAVE_API_KEY GLM_API_KEY --export)

3. 写入 .env 文件：
   python3 kv_get_env.py BRAVE_API_KEY GLM_API_KEY --write .env
"""

import os
import sys
import argparse
import json
from pathlib import Path

# 导入 KV 读取功能
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kv_read import read_kv


def get_kv_key(key: str) -> str:
    """
    从 KV 读取指定 key

    Args:
        key: KV 键名

    Returns:
        键的值

    Raises:
        ValueError: 读取失败
    """
    try:
        return read_kv(key)
    except Exception as e:
        print(f"⚠️  无法读取 KV 键 '{key}': {e}", file=sys.stderr)
        return None


def export_as_env_vars(keys: list) -> str:
    """
    导出为 shell 环境变量格式

    Args:
        keys: 键名列表

    Returns:
        shell export 语句
    """
    exports = []
    for key in keys:
        value = get_kv_key(key)
        if value is not None:
            # 转义特殊字符
            escaped_value = value.replace('"', '\\"').replace('$', '\\$')
            exports.append(f'export {key}="{escaped_value}"')
    return '\n'.join(exports)


def write_to_env_file(keys: list, output_path: str, mode: str = 'append') -> None:
    """
    写入到 .env 文件

    Args:
        keys: 键名列表
        output_path: 输出文件路径
        mode: 模式（'append' 或 'overwrite'）
    """
    if mode == 'overwrite' and os.path.exists(output_path):
        os.remove(output_path)

    with open(output_path, 'a') as f:
        f.write(f"# Auto-generated from Cloudflare KV\n")
        for key in keys:
            value = get_kv_key(key)
            if value is not None:
                # 转义特殊字符
                escaped_value = value.replace('"', '\\"')
                f.write(f'{key}="{escaped_value}"\n')

    print(f"✅ 已写入到: {output_path}")


def output_json(keys: list) -> str:
    """
    输出 JSON 格式（用于程序读取）

    Args:
        keys: 键名列表

    Returns:
        JSON 字符串
    """
    result = {}
    for key in keys:
        value = get_kv_key(key)
        if value is not None:
            result[key] = value
    return json.dumps(result, indent=2)


def main():
    parser = argparse.ArgumentParser(description="从 Cloudflare KV 获取密钥")
    parser.add_argument("keys", nargs='+', help="KV 键名（支持多个）")
    parser.add_argument("--export", action="store_true", help="导出为 shell 环境变量")
    parser.add_argument("--write", metavar="FILE", help="写入到 .env 文件")
    parser.add_argument("--overwrite", action="store_true", help="覆盖而非追加到 .env 文件")
    parser.add_argument("--json", action="store_true", help="以 JSON 格式输出")

    args = parser.parse_args()

    if args.export:
        # 导出为环境变量
        print(export_as_env_vars(args.keys))
    elif args.write:
        # 写入到文件
        write_to_env_file(args.keys, args.write, mode='overwrite' if args.overwrite else 'append')
    elif args.json:
        # JSON 格式
        print(output_json(args.keys))
    else:
        # 直接输出值（用于变量捕获）
        for i, key in enumerate(args.keys):
            value = get_kv_key(key)
            if value is not None:
                if i > 0:
                    print(' ', end='')  # 多个值用空格分隔
                print(value, end='')
        print()  # 换行


if __name__ == "__main__":
    main()
