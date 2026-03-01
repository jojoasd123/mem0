#!/usr/bin/env python3
"""
Cloudflare KV 键列表工具

依赖安装：
pip install requests

环境变量：
- CLOUDFLARE_API_TOKEN: Cloudflare API Token
- CLOUDFLARE_ACCOUNT_ID: Cloudflare Account ID
- CLOUDFLARE_NAMESPACE_ID: KV Namespace ID

使用方式：
python3 kv_list.py [--limit 100] [--cursor <cursor>] [--namespace-id <namespace_id>] [--account-id <account_id>]
"""

import os
import sys
import argparse
import requests
import json


def list_keys(account_id: str = None, namespace_id: str = None, limit: int = 100, cursor: str = None) -> dict:
    """
    列出 Cloudflare KV 中的所有键

    Args:
        account_id: Cloudflare Account ID（默认从环境变量读取）
        namespace_id: KV Namespace ID（默认从环境变量读取）
        limit: 每页返回的键数量（1-1000）
        cursor: 分页游标

    Returns:
        包含键列表和分页信息的字典

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

    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/storage/kv/namespaces/{namespace_id}/keys"

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }

    params = {"limit": limit}
    if cursor:
        params["cursor"] = cursor

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    return response.json()


def main():
    parser = argparse.ArgumentParser(description="列出 Cloudflare KV 中的所有键")
    parser.add_argument("--limit", type=int, default=100, help="每页返回的键数量（默认100）")
    parser.add_argument("--cursor", help="分页游标")
    parser.add_argument("--namespace-id", help="KV Namespace ID（覆盖环境变量）")
    parser.add_argument("--account-id", help="Cloudflare Account ID（覆盖环境变量）")
    parser.add_argument("--json", action="store_true", help="以 JSON 格式输出")

    args = parser.parse_args()

    try:
        result = list_keys(args.account_id, args.namespace_id, args.limit, args.cursor)

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"📋 KV 键列表（共 {len(result.get('result', []))} 个键）：\n")
            for key_info in result.get("result", []):
                print(f"  • {key_info['name']}")
                print(f"    元数据: {json.dumps(key_info.get('metadata', {}), ensure_ascii=False)}")
                print(f"    过期时间: {key_info.get('expiration', 'N/A')}")
                print()

            if result.get("result_info", {}).get("cursor"):
                print(f"📄 下一页游标: {result['result_info']['cursor']}")

    except (ValueError, requests.HTTPError) as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
