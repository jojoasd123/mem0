#!/usr/bin/env node

import { execSync } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const args = process.argv.slice(2);

let numResults = 5;
const nIndex = args.indexOf("-n");
if (nIndex !== -1 && args[nIndex + 1]) {
	numResults = parseInt(args[nIndex + 1], 10);
	args.splice(nIndex, 2);
}

const query = args.join(" ");

if (!query) {
	console.log("Usage: search.js <query> [-n <num>]");
	console.log("\nOptions:");
	console.log("  -n <num>    Number of results (default: 5)");
	console.log("\nExamples:");
	console.log('  search.js "javascript async await"');
	console.log('  search.js "rust programming" -n 10');
	console.log('  search.js "climate change" -n 3');
	process.exit(1);
}

// Auto-load BRAVE_API_KEY from Cloudflare KV
function loadApiKeyFromKV() {
	try {
		const kvScriptPath = path.resolve(__dirname, '../cloudflare-kv/scripts/kv_get_env.py');
		const result = execSync(
			`python3 ${kvScriptPath} BRAVE_API_KEY --json`,
			{ encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'] }
		);
		const keys = JSON.parse(result);
		if (keys.BRAVE_API_KEY) {
			return keys.BRAVE_API_KEY;
		}
	} catch (error) {
		// KV 读取失败，继续检查环境变量
	}

	// Fall back to environment variable
	return process.env.BRAVE_API_KEY;
}

const apiKey = loadApiKeyFromKV();

if (!apiKey) {
	console.error("❌ Error: BRAVE_API_KEY not found in Cloudflare KV or environment.");
	console.error("\nOptions:");
	console.error("1. Add BRAVE_API_KEY to Cloudflare KV (recommended)");
	console.error("2. Set environment variable: export BRAVE_API_KEY='your-api-key'");
	console.error("3. Add it to ~/.openclaw/openclaw.json env section.");
	process.exit(1);
}

async function searchBrave(query, numResults) {
	const url = `https://api.search.brave.com/res/v1/web/search?q=${encodeURIComponent(query)}&count=${numResults}`;

	const response = await fetch(url, {
		headers: {
			"Accept": "application/json",
			"Accept-Encoding": "gzip",
			"X-Subscription-Token": apiKey
		}
	});

	if (!response.ok) {
		const errorText = await response.text();
		throw new Error(`HTTP ${response.status}: ${response.statusText}\n${errorText}`);
	}

	const data = await response.json();
	return data.web?.results || [];
}

// Main
try {
	const results = await searchBrave(query, numResults);

	if (results.length === 0) {
		console.error("No results found.");
		process.exit(0);
	}

	for (let i = 0; i < results.length; i++) {
		const r = results[i];
		console.log(`--- Result ${i + 1} ---`);
		console.log(`Title: ${r.title}`);
		console.log(`Link: ${r.url}`);
		console.log(`Snippet: ${r.description || 'No description'}`);
		console.log("");
	}
} catch (e) {
	console.error(`Error: ${e.message}`);
	process.exit(1);
}
