#!/usr/bin/env python3
"""Client for the Apifox-documented async image generation API."""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_SIZE = "1024x1536"


def load_env_file() -> None:
    candidates = []
    explicit = os.environ.get("STORYBOARD_IMAGE_ENV_FILE")
    if explicit:
        candidates.append(Path(explicit))
    candidates.extend([Path(".env.storyboard-image"), Path(".env")])

    for path in candidates:
        if not path.exists():
            continue
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)


def env(name: str, default: str | None = None, required: bool = False) -> str:
    value = os.environ.get(name, default)
    if required and not value:
        raise SystemExit(f"Missing required env var: {name}")
    return value or ""


def base_url() -> str:
    return env("STORYBOARD_IMAGE_BASE_URL", required=True).rstrip("/")


def api_key() -> str:
    return env("STORYBOARD_IMAGE_API_KEY", required=True)


def model() -> str:
    return env("STORYBOARD_IMAGE_MODEL", required=True)


def request_json(method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
    url = base_url() + path
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {api_key()}",
        "Accept": "application/json, image/*, */*",
        "User-Agent": "Mozilla/5.0 storyboard-image-generator/1.0",
    }
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read()
            ctype = resp.headers.get("content-type", "")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        raise SystemExit(f"HTTP {exc.code} {exc.reason}: {detail}") from exc
    if "application/json" in ctype:
        return json.loads(body.decode("utf-8"))
    return body


def read_prompt(args: argparse.Namespace) -> str:
    if args.prompt_file:
        return Path(args.prompt_file).read_text(encoding="utf-8").strip()
    if args.prompt:
        return args.prompt.strip()
    if not sys.stdin.isatty():
        return sys.stdin.read().strip()
    raise SystemExit("Provide --prompt, --prompt-file, or stdin.")


def normalize_image(value: str) -> str:
    if value.startswith(("http://", "https://", "data:")):
        return value
    path = Path(value)
    if not path.exists():
        raise SystemExit(f"Reference image not found: {value}")
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def find_task_id(response: Any) -> str:
    if isinstance(response, dict):
        for key in ("id", "task_id", "taskId"):
            if response.get(key):
                return str(response[key])
        data = response.get("data")
        if isinstance(data, dict):
            for key in ("id", "task_id", "taskId"):
                if data.get(key):
                    return str(data[key])
    raise SystemExit(f"Could not find task id in response: {json.dumps(response, ensure_ascii=False)[:1000]}")


def is_completed(response: Any) -> bool:
    if not isinstance(response, dict):
        return False
    status = str(response.get("status") or response.get("state") or "").lower()
    if status in {"completed", "succeeded", "success", "done"}:
        return True
    data = response.get("data")
    if isinstance(data, dict):
        nested = str(data.get("status") or data.get("state") or "").lower()
        return nested in {"completed", "succeeded", "success", "done"}
    if isinstance(data, list) and data and isinstance(data[0], dict):
        return bool(data[0].get("url"))
    return False


def submit(args: argparse.Namespace) -> None:
    payload: dict[str, Any] = {
        "model": model(),
        "prompt": read_prompt(args),
        "response_format": args.response_format,
        "size": args.size or env("STORYBOARD_IMAGE_SIZE", DEFAULT_SIZE),
    }
    if args.image:
        payload["image"] = [normalize_image(item) for item in args.image]
    if args.extra_json:
        payload.update(json.loads(args.extra_json))

    response = request_json("POST", "/v1/images/generations?async=true", payload)
    print(json.dumps(response, ensure_ascii=False, indent=2))
    task_id = find_task_id(response)
    if args.wait:
        query_args = argparse.Namespace(task_id=task_id, interval=args.interval, timeout=args.timeout, json=True)
        final = wait_for_completion(query_args)
        if args.download:
            download(argparse.Namespace(task_id=task_id, output_dir=args.output_dir, output=args.output))
        else:
            print(json.dumps(final, ensure_ascii=False, indent=2))


def wait_for_completion(args: argparse.Namespace) -> Any:
    deadline = time.time() + args.timeout
    while True:
        response = request_json("GET", f"/v1/images/{urllib.parse.quote(args.task_id)}")
        if is_completed(response):
            return response
        if time.time() >= deadline:
            raise SystemExit(f"Timed out waiting for task: {args.task_id}")
        time.sleep(args.interval)


def query(args: argparse.Namespace) -> None:
    response = wait_for_completion(args) if args.wait else request_json("GET", f"/v1/images/{urllib.parse.quote(args.task_id)}")
    print(json.dumps(response, ensure_ascii=False, indent=2))


def download(args: argparse.Namespace) -> None:
    body = request_json("GET", f"/v1/images/{urllib.parse.quote(args.task_id)}/content")
    if isinstance(body, (dict, list)):
        print(json.dumps(body, ensure_ascii=False, indent=2))
        return
    output = Path(args.output) if args.output else Path(args.output_dir) / f"{args.task_id}.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(body)
    print(str(output))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    submit_p = sub.add_parser("submit", help="submit an async image generation task")
    submit_p.add_argument("--prompt")
    submit_p.add_argument("--prompt-file")
    submit_p.add_argument("--image", action="append", help="reference image URL, data URL, or local file")
    submit_p.add_argument("--size", default=None)
    submit_p.add_argument("--response-format", default="url")
    submit_p.add_argument("--extra-json", help="JSON object merged into the request body")
    submit_p.add_argument("--wait", action="store_true")
    submit_p.add_argument("--download", action="store_true")
    submit_p.add_argument("--interval", type=float, default=5)
    submit_p.add_argument("--timeout", type=float, default=300)
    submit_p.add_argument("--output-dir", default=env("STORYBOARD_IMAGE_OUTPUT_DIR", "downloads/storyboard-images"))
    submit_p.add_argument("--output")
    submit_p.set_defaults(func=submit)

    query_p = sub.add_parser("query", help="query a task")
    query_p.add_argument("--task-id", required=True)
    query_p.add_argument("--wait", action="store_true")
    query_p.add_argument("--interval", type=float, default=5)
    query_p.add_argument("--timeout", type=float, default=300)
    query_p.set_defaults(func=query)

    download_p = sub.add_parser("download", help="download completed task content")
    download_p.add_argument("--task-id", required=True)
    download_p.add_argument("--output-dir", default=env("STORYBOARD_IMAGE_OUTPUT_DIR", "downloads/storyboard-images"))
    download_p.add_argument("--output")
    download_p.set_defaults(func=download)

    return parser


def main() -> None:
    load_env_file()
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
