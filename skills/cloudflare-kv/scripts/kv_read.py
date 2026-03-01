#!/usr/bin/env python3
"""
Cloudflare KV 读取工具

依赖安装：
pip install requests cloudflare

环境变量：
- CLOUDFLARE_API_TOKEN: Cloudflare API Token
- CLOUDFLARE_ACCOUNT_ID: Cloudflare Account ID
- CLOUDFLARE_NAMESPACE_ID: KV Namespace ID（可选，默认使用命名空间）

使用方式：
python3 kv_read.py <key> [--namespace-id <namespace_id>] [--account-id <account_id>]
"""

import os
import sys
import argparse
import requests


def read_kv(key: str, account_id: str = None, namespace_id: str = None) -> str:
    """
    读取 Cloudflare KV 键值对

    Args:
        key: 要读取的键名
        account_id: Cloudflare Account ID（默认从环境变量读取）
        namespace_id: KV Namespace ID（默认从环境变量读取）

    Returns:
        键对应的值

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

    # Cloudflare KV API 端点
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/storage/kv/namespaces/{namespace_id}/values/{key}"

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.text


def main():
    parser = argparse.ArgumentParser(description="读取 Cloudflare KV 键值对")
    parser.add_argument("key", help="要读取的键名")
    parser.add_argument("--namespace-id", help="KV Namespace ID（覆盖环境变量）")
    parser.add_argument("--account-id", help="Cloudflare Account ID（覆盖环境变量）")

    args = parser.parse_args()

    try:
        value = read_kv(args.key, args.account_id, args.namespace_id)
        print(value)
    except (ValueError, requests.HTTPError) as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
