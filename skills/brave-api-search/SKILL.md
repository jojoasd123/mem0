---
name: brave-api-search
description: Web search via Brave Search API (Official API, requires BRAVE_API_KEY). Automatically loads API key from Cloudflare KV. No manual configuration needed if key is in KV.
---

# Brave API Search

Web search using Brave Search official API.

## 🔑 Configuration

**Recommended: Store API key in Cloudflare KV (auto-loaded)**

### Option 1: Cloudflare KV (Recommended)

1. Add `BRAVE_API_KEY` to your Cloudflare KV namespace
2. Configure KV access in `openclaw.json`:

```json
{
  "env": {
    "CLOUDFLARE_API_TOKEN": "your-kv-token",
    "CLOUDFLARE_ACCOUNT_ID": "your-account-id",
    "CLOUDFLARE_NAMESPACE_ID": "your-namespace-id"
  }
}
```

3. That's it! The script automatically fetches the key from KV.

### Option 2: Environment Variable

```bash
export BRAVE_API_KEY='your-api-key-here'
```

### Option 3: openclaw.json

Add to `~/.openclaw/openclaw.json`:

```json
{
  "env": {
    "BRAVE_API_KEY": "your-api-key-here"
  }
}
```

**Note:** Option 1 (Cloudflare KV) is recommended because:
- ✅ No Gateway restart needed when updating keys
- ✅ Centralized key management
- ✅ Scripts auto-fetch latest keys

## Usage

```bash
# Basic search (5 results)
node search.js "query"

# More results
node search.js "query" -n 10

# Examples
node search.js "javascript async await"
node search.js "rust programming" -n 10
node search.js "climate change" -n 3
```

## Output Format

```
--- Result 1 ---
Title: Page Title
Link: https://example.com/page
Snippet: Description from search results...

--- Result 2 ---
...
```

## When to Use

- Searching for documentation or API references
- Looking up facts or current information
- Any task requiring web search
- When you have a valid BRAVE_API_KEY

## API Reference

- **Endpoint**: `https://api.search.brave.com/res/v1/web/search`
- **Method**: GET
- **Headers**:
  - `X-Subscription-Token`: Your API key
  - `Accept`: `application/json`
- **Parameters**:
  - `q`: Search query (required)
  - `count`: Number of results (default: 5, max: 20)

## Rate Limits

Free tier: 2,000 requests per month
Check your usage at: https://api.search.brave.com/app/keys

## Notes

- Uses official Brave Search API
- More reliable than scraping
- No browser required
- Auto-loads API key from Cloudflare KV (recommended)
