---
name: zhenghe-data
description: Work with Zhenghe Data (郑和数据) for TikTok commerce research. Use when Codex needs to log in to zhenghedata.com, capture product-search filters/categories, fetch product lists, inspect product detail pages, collect benchmark/related videos, identify AI videos via isAi, or download Zhenghe-hosted TikTok video MP4 files.
---

# Zhenghe Data

Use the bundled script. Do not hand-roll curl calls unless debugging one request.

## Setup

From the user's project directory:

```bash
python3 -m venv .venv
.venv/bin/pip install -r skills/zhenghe-data/scripts/requirements.txt
.venv/bin/python -m playwright install chromium
```

## Commands

Use the script path directly:

```bash
.venv/bin/python skills/zhenghe-data/scripts/zhenghe_tool.py <command>
```

Core commands:

```bash
# Manual login; saves .auth/zhenghe-state.json in the current project.
.venv/bin/python skills/zhenghe-data/scripts/zhenghe_tool.py login

# Capture product-search page metadata, categories, filters, and current product request.
.venv/bin/python skills/zhenghe-data/scripts/zhenghe_tool.py inspect

# Fetch products inside the logged-in browser context.
.venv/bin/python skills/zhenghe-data/scripts/zhenghe_tool.py products --category-id 600001 --start-date 2026-06-25 --end-date 2026-06-25 --pages 1

# Fetch related/benchmark videos for a product detail page.
.venv/bin/python skills/zhenghe-data/scripts/zhenghe_tool.py videos --product-id 1733587410864539046 --pages 3

# Download videos from a benchmark-videos.json or ai-videos.json file.
.venv/bin/python skills/zhenghe-data/scripts/zhenghe_tool.py download-videos --source downloads/product-detail-1733587410864539046/ai-videos.json --limit 5
```

## Outputs

The script writes into the current project:

```text
.auth/zhenghe-state.json
.auth/product-search-request.json
downloads/product-search-filters.json
downloads/categories-tree.json
downloads/categories-flat.json
downloads/product-fields.json
downloads/products-*.json
downloads/product-detail-<productId>/benchmark-videos.json
downloads/product-detail-<productId>/ai-videos.json
downloads/product-detail-<productId>/videos/*.mp4
```

## Important Notes

- Use browser-context fetch for product and video APIs. Pure Python/urllib replay can return `查询权限超出` even with valid captured headers.
- `category/getCategory` is safe to recurse for category trees. Product search may consume quota.
- AI video detection comes from `/product/video` field `isAi`: `1` means AI, `0` means non-AI, `null` means unknown.
- Video download uses Zhenghe's `/video/download?videoId=<id>` endpoint to get a Zhenghe-hosted MP4 URL, then downloads the MP4.
- Do not store pasted cookies/tokens in code. Save login state with `login`.
