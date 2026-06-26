import argparse
import hashlib
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

STATE = Path(".auth/zhenghe-state.json")
CREDS = Path(".auth/product-search-request.json")
OUT = Path("downloads")
PRODUCT_URL = "https://zhenghedata.com/product/search"
API = "https://tkapi-gl.zhenghedata.com"


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def safe_name(value):
    return re.sub(r"[^a-zA-Z0-9_.-]+", "-", str(value))[:120].strip("-") or "item"


def browser_page(headless=True):
    from playwright.sync_api import sync_playwright

    if not STATE.exists():
        raise SystemExit("缺少登录态，先运行 login")
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=headless)
    context = browser.new_context(storage_state=str(STATE), viewport={"width": 1440, "height": 1000})
    page = context.new_page()
    page.goto(PRODUCT_URL, wait_until="domcontentloaded", timeout=60_000)
    page.wait_for_timeout(3_000)
    return p, browser, context, page


def page_fetch_json(page, url, method="GET", headers=None, body=None):
    return page.evaluate(
        """async ({url, method, headers, body}) => {
            const response = await fetch(url, {
                method,
                headers: headers || {},
                body: body == null ? undefined : JSON.stringify(body),
                credentials: "include"
            });
            return await response.json();
        }""",
        {"url": url, "method": method, "headers": headers or {}, "body": body},
    )


def login(args):
    from playwright.sync_api import sync_playwright

    STATE.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(args.url, wait_until="domcontentloaded", timeout=60_000)
        input("登录完成后按 Enter 保存登录态...")
        context.storage_state(path=str(STATE))
        browser.close()
    print(f"登录态已保存：{STATE}")


def extract_visible_filters(text):
    labels = ["国家/地区：", "商品类目：", "店铺类型：", "筛选条件："]
    sections = {}
    for index, label in enumerate(labels):
        start = text.find(label)
        if start == -1:
            continue
        start += len(label)
        next_starts = [text.find(item, start) for item in labels[index + 1:]]
        next_starts = [item for item in next_starts if item != -1]
        date_start = text.find("2026-", start)
        if date_start != -1:
            next_starts.append(date_start)
        end = min(next_starts) if next_starts else len(text)
        sections[label.rstrip("：")] = [
            line.strip() for line in text[start:end].splitlines()
            if line.strip() and line.strip() != "NEW!"
        ]
    sections["country_codes"] = {
        "全球": "gl", "美国": "us", "印尼": "id", "英国": "gb", "菲律宾": "ph",
        "泰国": "th", "马来西亚": "my", "越南": "vn", "新加坡": "sg",
        "墨西哥": "mx", "西班牙": "es", "德国": "de", "意大利": "it",
        "法国": "fr", "巴西": "br", "日本": "jp",
    }
    sections["shop_type_params"] = {"全部": None, "本土店": 1, "跨境店": 2}
    return sections


def summarize_product_fields(product_json):
    records = product_json.get("extData", {}).get("records", [])
    fields = {}
    for record in records:
        for key, value in record.items():
            item = fields.setdefault(key, {"types": set(), "example": None})
            item["types"].add(type(value).__name__)
            if item["example"] is None and value is not None:
                item["example"] = value[:1] if isinstance(value, list) else value
    return {key: {"types": sorted(value["types"]), "example": value["example"]} for key, value in sorted(fields.items())}


def inspect(args):
    seen = set()
    captures = []
    product_json = None
    category_headers = None
    category_t = None
    network_dir = OUT / "inspect" / "network"

    from playwright.sync_api import sync_playwright

    if not STATE.exists():
        raise SystemExit("缺少登录态，先运行 login")

    def on_response(response):
        nonlocal product_json, category_headers, category_t
        url = response.url
        if "tkapi-gl.zhenghedata.com" not in url or "json" not in response.headers.get("content-type", ""):
            return
        request = response.request
        key = hashlib.sha1((url + request.method + (request.post_data or "")).encode()).hexdigest()[:12]
        if key in seen:
            return
        seen.add(key)
        item = {
            "url": url,
            "method": request.method,
            "headers": request.headers,
            "post_data": request.post_data,
            "status": response.status,
        }
        try:
            item["json"] = response.json()
        except Exception:
            item["text"] = response.text()[:2000]
        write_json(network_dir / f"{len(seen):03d}-{safe_name(url)}.json", item)
        captures.append({"url": url, "status": response.status})
        if "/product/search/v2" in url:
            product_json = item["json"]
            write_json(CREDS, item)
        if "/category/getCategory" in url and "categoryId=0" in url:
            category_headers = {k: v for k, v in request.headers.items() if k.lower() in {"accept", "referer", "user-agent", "x-token", "x-sign"}}
            match = re.search(r"[?&]t=(\d+)", url)
            category_t = match.group(1) if match else int(time.time() * 1000)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not args.headed)
        context = browser.new_context(storage_state=str(STATE), viewport={"width": 1440, "height": 1000})
        page = context.new_page()
        page.on("response", on_response)
        page.goto(PRODUCT_URL, wait_until="domcontentloaded", timeout=60_000)
        page.wait_for_timeout(args.seconds * 1000)
        visible = page.locator("body").inner_text(timeout=10_000)
        (OUT / "inspect" / "visible.txt").parent.mkdir(parents=True, exist_ok=True)
        (OUT / "inspect" / "visible.txt").write_text(visible, encoding="utf-8")
        context.storage_state(path=str(STATE))
        browser.close()

    write_json(OUT / "inspect" / "summary.json", captures)
    write_json(OUT / "product-search-filters.json", extract_visible_filters(visible))
    if product_json:
        write_json(OUT / "product-fields.json", summarize_product_fields(product_json))
    if category_headers:
        flat = []

        def category_children(category_id):
            url = f"{API}/category/getCategory?language=zh&fzRate=cn&t={category_t}&appKey=v1&categoryId={category_id}"
            request = urllib.request.Request(url, headers=category_headers)
            with urllib.request.urlopen(request, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8"))
            if data.get("status") != 0:
                raise RuntimeError(data)
            return data.get("extData") or []

        def walk(category_id=0):
            nodes = []
            for item in category_children(category_id):
                node = {key: item.get(key) for key in ["id", "name", "fullName", "level", "parentId", "topId"]}
                flat.append(node)
                if item.get("level", 0) < 3:
                    children = walk(item["id"])
                    if children:
                        node["children"] = children
                nodes.append(node)
                time.sleep(args.delay)
            return nodes

        write_json(OUT / "categories-tree.json", walk(0))
        write_json(OUT / "categories-flat.json", flat)

    print(f"接口响应：{network_dir}")
    print(f"筛选项：{OUT / 'product-search-filters.json'}")
    print(f"类目树：{OUT / 'categories-tree.json'}")


def products(args):
    p, browser, context, page = browser_page(headless=not args.headed)
    try:
        all_records = []
        for page_num in range(1, args.pages + 1):
            t_value = int(time.time() * 1000)
            body = {
                "language": "zh",
                "fzRate": "cn",
                "t": t_value,
                "appKey": "v1",
                "categoryId": args.category_id,
                "pageNum": page_num,
                "pageSize": args.page_size,
                "sort": args.sort,
                "startDate": args.start_date,
                "endDate": args.end_date,
                "searchType": 1,
            }
            if args.region:
                body["region"] = args.region
            if args.seller_type:
                body["sellerType"] = args.seller_type
            url = f"{API}/product/search/v2?language=zh&fzRate=cn&t={t_value}&appKey=v1"
            result = page_fetch_json(page, url, method="POST", headers={"content-type": "application/json"}, body=body)
            if result.get("status") != 0:
                raise SystemExit(result)
            records = result.get("extData", {}).get("records", [])
            all_records.extend(records)
            write_json(OUT / f"products-category-{args.category_id}-page-{page_num}.json", result)
            print(f"page {page_num}: {len(records)}")
        write_json(OUT / f"products-category-{args.category_id}.json", {"records": all_records})
    finally:
        context.storage_state(path=str(STATE))
        browser.close()
        p.stop()


def videos(args):
    detail_dir = OUT / f"product-detail-{args.product_id}"
    found_request = {}
    seen = set()

    from playwright.sync_api import sync_playwright

    if not STATE.exists():
        raise SystemExit("缺少登录态，先运行 login")

    def on_response(response):
        if "/product/video" not in response.url or "/overview" in response.url:
            return
        request = response.request
        key = hashlib.sha1((response.url + (request.post_data or "")).encode()).hexdigest()[:12]
        if key in seen:
            return
        seen.add(key)
        found_request.update({
            "url": response.url,
            "headers": {k: v for k, v in request.headers.items() if k.lower() in {"accept", "accept-language", "content-type", "origin", "referer", "user-agent", "x-token", "x-sign"}},
            "body": json.loads(request.post_data or "{}"),
            "json": response.json(),
        })

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not args.headed)
        context = browser.new_context(storage_state=str(STATE), viewport={"width": 1440, "height": 1000})
        page = context.new_page()
        page.on("response", on_response)
        page.goto(f"https://zhenghedata.com/product/search/detail?id={args.product_id}", wait_until="domcontentloaded", timeout=60_000)
        page.wait_for_timeout(8_000)
        if not found_request:
            raise SystemExit("未捕获到 /product/video")

        records = []
        for page_num in range(1, args.pages + 1):
            body = {**found_request["body"], "pageNum": page_num, "pageSize": args.page_size, "t": int(time.time() * 1000)}
            result = page_fetch_json(page, found_request["url"], method="POST", headers=found_request["headers"], body=body)
            if result.get("status") != 0:
                raise SystemExit(result)
            rows = result.get("extData", {}).get("records", [])
            records.extend(rows)
            print(f"page {page_num}: {len(rows)}")

        context.storage_state(path=str(STATE))
        browser.close()

    write_json(detail_dir / "benchmark-videos.json", {"records": records})
    write_json(detail_dir / "ai-videos.json", {"records": [item for item in records if item.get("isAi") == 1]})
    print(f"视频：{detail_dir / 'benchmark-videos.json'}")
    print(f"AI 视频：{detail_dir / 'ai-videos.json'}")


def download_videos(args):
    source = Path(args.source)
    if not source.exists():
        raise SystemExit(f"缺少文件：{source}")
    data = json.loads(source.read_text(encoding="utf-8"))
    records = data.get("records", data if isinstance(data, list) else [])
    p, browser, context, page = browser_page(headless=True)
    try:
        target = source.parent / "videos"
        target.mkdir(parents=True, exist_ok=True)
        downloaded = []
        for video in records[:args.limit]:
            video_id = str(video["videoId"])
            url = f"{API}/video/download?language=zh&fzRate=cn&t={int(time.time() * 1000)}&appKey=v1&videoId={urllib.parse.quote(video_id)}"
            result = page_fetch_json(page, url)
            if result.get("status") != 0 or not result.get("extData"):
                print(f"跳过 {video_id}: {result.get('message')}")
                continue
            file = target / f"{'AI-' if video.get('isAi') == 1 else ''}{video_id}-{safe_name(video.get('uniqueId', 'video'))}.mp4"
            with urllib.request.urlopen(result["extData"], timeout=90) as response:
                file.write_bytes(response.read())
            downloaded.append({"videoId": video_id, "file": str(file), "source": video.get("url")})
            print(f"已下载：{file}")
        write_json(source.parent / "downloaded-videos.json", downloaded)
    finally:
        browser.close()
        p.stop()


def self_test(_args=None):
    filters = extract_visible_filters("国家/地区：\n全球\n美国\n店铺类型：\n全部\n本土店\n2026-01-01")
    assert filters["店铺类型"] == ["全部", "本土店"]
    assert safe_name("https://a.com/x?b=1&c=2") == "https-a.com-x-b-1-c-2"
    print("self-test ok")


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("login")
    p.add_argument("--url", default=PRODUCT_URL)
    p.set_defaults(func=login)

    p = sub.add_parser("inspect")
    p.add_argument("--seconds", type=int, default=12)
    p.add_argument("--delay", type=float, default=0.03)
    p.add_argument("--headed", action="store_true")
    p.set_defaults(func=inspect)

    p = sub.add_parser("products")
    p.add_argument("--category-id", type=int, default=0)
    p.add_argument("--region")
    p.add_argument("--seller-type", type=int)
    p.add_argument("--start-date", required=True)
    p.add_argument("--end-date", required=True)
    p.add_argument("--pages", type=int, default=1)
    p.add_argument("--page-size", type=int, default=20)
    p.add_argument("--sort", type=int, default=0)
    p.add_argument("--headed", action="store_true")
    p.set_defaults(func=products)

    p = sub.add_parser("videos")
    p.add_argument("--product-id", required=True)
    p.add_argument("--pages", type=int, default=1)
    p.add_argument("--page-size", type=int, default=20)
    p.add_argument("--headed", action="store_true")
    p.set_defaults(func=videos)

    p = sub.add_parser("download-videos")
    p.add_argument("--source", required=True)
    p.add_argument("--limit", type=int, default=5)
    p.set_defaults(func=download_videos)

    p = sub.add_parser("self-test")
    p.set_defaults(func=self_test)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
