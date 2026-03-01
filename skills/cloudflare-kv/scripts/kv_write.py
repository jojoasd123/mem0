#!/usr/bin/env python3
"""
Cloudflare KV 写入工具

依赖安装：
pip install requests cloudflare

环境变量：
- CLOUDFLARE_API_TOKEN: Cloudflare API Token
- CLOUDFLARE_ACCOUNT_ID: Cloudflare Account ID
- CLOUDFLARE_NAMESPACE_ID: KV Namespace ID（可选，默认使用命名空间）

使用方式：
python3 kv_write.py <key> <value> [--namespace-id <namespace_id>] [--account-id <account_id>]
"""

import os
import sys
import argparse
import requests


def write_kv(key: str, value: str, account_id: str = None, namespace_id: str = None) -> bool:
    """
    写入 Cloudflare KV 键值对

    Args:
        key: 键名
        value: 值
        account_id: Cloudflare Account ID（默认从环境变量读取）
        namespace_id: KV Namespace ID（默认从环境变量读取）

    Returns:
        True if successful

    Raises:
        ValueError: 缺少必要的配置
        requests.HTTPError: API请求失败
    """
    api_token = os.getenv("CLOUDFLARE_API_TOKEN")
    account_id = account_id or os.getenv("CLOUDFLARE_ACCOUNT_ID")
    namespace_id = namespace_id or os.getenv("CLOUDFLARE_NAMESPACE_ID")

    if not api_token:
        raise ValueError("CLOUDFLARE_API_TOKEN 环境变量未设置")
    if not account_id:
        raise ValueError("CLOUDFLARE_ACCOUNT_ID 环境变量未设置")
    if not namespace_id:
        raise ValueError("CLOUDFLARE_NAMESPACE_ID 环境变量未设置")

    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/storage/kv/namespaces/{namespace_id}/values/{key}"

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "text/plain"
    }

    response = requests.put(url, headers=headers, data=value)
    response.raise_for_status()

    return True


def main():
    parser = argparse.ArgumentParser(description="写入 Cloudflare KV 键值对")
    parser.add_argument("key", help="键名")
    parser.add_argument("value", help="值")
    parser.add_argument("--namespace-id", help="KV Namespace ID（覆盖环境变量）")
    parser.add_argument("--account-id", help="Cloudflare Account ID（覆盖环境变量）")

    args = parser.parse_args()

    try:
        write_kv(args.key, args.value, args.account_id, args.namespace_id)
        print(f"✅ 成功写入: {args.key}")
    except (ValueError, requests.HTTPError) as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
