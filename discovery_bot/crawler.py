from __future__ import annotations

import codecs
import re
import urllib.error
import urllib.request
from typing import Dict, Tuple

from .model import FetchResult


_DEFAULT_HEADERS = {
    "User-Agent": "discovery-bot/1.0 (+https://aurascape.ai/resources/blog/aurascape-ai-application-discovery/)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

_CHARSET_RE = re.compile(r"charset=([a-zA-Z0-9_\-]+)")


def fetch_url(url: str, timeout: int = 10, max_bytes: int = 2_000_000) -> FetchResult:
    request = urllib.request.Request(url, headers=_DEFAULT_HEADERS)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status_code = getattr(response, "status", 0)
            final_url = response.geturl()
            headers = _headers_to_dict(response.headers.items())
            content_bytes = _read_response(response, max_bytes=max_bytes)
            content = _decode_content(content_bytes, headers)
            return FetchResult(
                url=url,
                final_url=final_url,
                status_code=status_code,
                headers=headers,
                content=content,
            )
    except urllib.error.HTTPError as exc:
        headers = _headers_to_dict(exc.headers.items()) if exc.headers else {}
        content_bytes = b""
        try:
            content_bytes = _read_response(exc, max_bytes=max_bytes)
        except Exception:
            content_bytes = b""
        content = _decode_content(content_bytes, headers) if content_bytes else ""
        return FetchResult(
            url=url,
            final_url=getattr(exc, "url", url),
            status_code=getattr(exc, "code", 0),
            headers=headers,
            content=content,
            error=str(exc),
        )
    except urllib.error.URLError as exc:
        return FetchResult(
            url=url,
            final_url=url,
            status_code=0,
            headers={},
            content="",
            error=str(exc),
        )


def _read_response(response: urllib.response.addinfourl, max_bytes: int) -> bytes:
    data = response.read(max_bytes + 1)
    if len(data) > max_bytes:
        return data[:max_bytes]
    return data


def _headers_to_dict(pairs: Tuple[str, str]) -> Dict[str, str]:
    return {key.lower(): value for key, value in pairs}


def _decode_content(content: bytes, headers: Dict[str, str]) -> str:
    if not content:
        return ""
    charset = _detect_charset(headers, content)
    try:
        return content.decode(charset, errors="replace")
    except LookupError:
        return content.decode("utf-8", errors="replace")


def _detect_charset(headers: Dict[str, str], content: bytes) -> str:
    content_type = headers.get("content-type", "")
    match = _CHARSET_RE.search(content_type)
    if match:
        return match.group(1)
    try:
        return codecs.lookup("utf-8").name
    except LookupError:
        return "utf-8"
