from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed

from .analyzer import analyze_app
from .crawler import fetch_url
from .extractor import extract_chat_decoder, extract_endpoints
from .model import DiscoveryResult
from .parser import parse_html


class DiscoveryBot:
    def __init__(self, timeout: int = 10, max_workers: int = 6, max_bytes: int = 2_000_000) -> None:
        self.timeout = timeout
        self.max_workers = max_workers
        self.max_bytes = max_bytes

    def discover(self, urls: list[str]) -> list[DiscoveryResult]:
        results: list[DiscoveryResult] = []
        if not urls:
            return results

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_map = {
                executor.submit(self._process_url, url): url for url in urls
            }
            for future in as_completed(future_map):
                result = future.result()
                results.append(result)
        return results

    def _process_url(self, url: str) -> DiscoveryResult:
        result = DiscoveryResult(url=url)
        fetch = fetch_url(url, timeout=self.timeout, max_bytes=self.max_bytes)
        result.final_url = fetch.final_url
        result.status_code = fetch.status_code
        if fetch.error:
            result.errors.append(fetch.error)
            return result

        metadata = parse_html(fetch.content)
        result.metadata = metadata

        is_ai_app, confidence, categories, chat_capability = analyze_app(metadata)
        result.is_ai_app = is_ai_app
        result.confidence = confidence
        result.categories = categories
        result.chat_capability = chat_capability

        result.endpoints = extract_endpoints(fetch.content)
        result.chat_decoder = extract_chat_decoder(fetch.content)

        if not result.chat_capability:
            if any("/chat" in endpoint for endpoint in result.endpoints):
                result.chat_capability = True
        return result
