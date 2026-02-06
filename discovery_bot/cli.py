from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .bot import DiscoveryBot
from .model import DiscoveryResult


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AI application discovery bot")
    parser.add_argument("--input", help="input file with one URL per line")
    parser.add_argument(
        "--url",
        action="append",
        default=[],
        help="target URL (can be repeated)",
    )
    parser.add_argument(
        "--output",
        default="discovery_results.json",
        help="output file path, use '-' for stdout",
    )
    parser.add_argument(
        "--format",
        choices=["json", "jsonl"],
        default="json",
        help="output format",
    )
    parser.add_argument("--timeout", type=int, default=10, help="request timeout seconds")
    parser.add_argument("--max-workers", type=int, default=6, help="worker threads")
    parser.add_argument("--max-bytes", type=int, default=2_000_000, help="max bytes per page")
    parser.add_argument("--limit", type=int, default=0, help="limit number of URLs")
    args = parser.parse_args(argv)

    urls = _collect_urls(args.input, args.url)
    if args.limit and args.limit > 0:
        urls = urls[: args.limit]

    if not urls:
        parser.error("需要通过 --input 或 --url 提供至少一个 URL")

    bot = DiscoveryBot(
        timeout=args.timeout,
        max_workers=args.max_workers,
        max_bytes=args.max_bytes,
    )
    results = bot.discover(urls)
    output_payload = [_result_to_dict(result) for result in results]
    return _write_output(output_payload, args.output, args.format)


def _collect_urls(input_path: str | None, url_args: list[str]) -> list[str]:
    urls: list[str] = []
    if input_path:
        path = Path(input_path)
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                cleaned = _clean_url(line)
                if cleaned:
                    urls.append(cleaned)
        else:
            raise SystemExit(f"输入文件不存在: {input_path}")

    for url in url_args:
        cleaned = _clean_url(url)
        if cleaned:
            urls.append(cleaned)

    return urls


def _clean_url(value: str) -> str:
    text = value.strip()
    if not text or text.startswith("#"):
        return ""
    if text.startswith("http://") or text.startswith("https://"):
        return text
    return ""


def _result_to_dict(result: DiscoveryResult) -> dict:
    return {
        "url": result.url,
        "final_url": result.final_url,
        "status_code": result.status_code,
        "metadata": {
            "title": result.metadata.title,
            "description": result.metadata.description,
            "og_title": result.metadata.og_title,
            "og_description": result.metadata.og_description,
            "language": result.metadata.language,
            "text_sample": result.metadata.text_sample,
        },
        "is_ai_app": result.is_ai_app,
        "confidence": result.confidence,
        "categories": result.categories,
        "chat_capability": result.chat_capability,
        "chat_decoder": {
            "kind": result.chat_decoder.kind,
            "evidence": result.chat_decoder.evidence,
        },
        "endpoints": result.endpoints,
        "errors": result.errors,
    }


def _write_output(payload: list[dict], output_path: str, output_format: str) -> int:
    if output_path == "-":
        return _write_stream(payload, sys.stdout, output_format)

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        return _write_stream(payload, handle, output_format)


def _write_stream(payload: list[dict], handle, output_format: str) -> int:
    if output_format == "jsonl":
        for item in payload:
            handle.write(json.dumps(item, ensure_ascii=True))
            handle.write("\n")
    else:
        json.dump(payload, handle, indent=2, ensure_ascii=True)
        handle.write("\n")
    return 0
