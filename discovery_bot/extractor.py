from __future__ import annotations

import re

from .model import ChatDecoderInfo


_URL_RE = re.compile(r"https?://[^\s'\"<>]+", re.IGNORECASE)
_API_PATH_RE = re.compile(r"['\"](/(?:api|v1|v2)/[^'\"<>]+)['\"]")
_CHAT_HINT_RE = re.compile(
    r"(chat/completions|/chat|conversation|messages|event-stream|eventsource|websocket)",
    re.IGNORECASE,
)


def extract_endpoints(content: str, limit: int = 40) -> list[str]:
    if not content:
        return []
    endpoints: list[str] = []
    seen: set[str] = set()

    for match in _URL_RE.findall(content):
        cleaned = _clean_endpoint(match)
        if cleaned not in seen:
            seen.add(cleaned)
            endpoints.append(cleaned)
        if len(endpoints) >= limit:
            return endpoints

    for match in _API_PATH_RE.findall(content):
        cleaned = _clean_endpoint(match)
        if cleaned not in seen:
            seen.add(cleaned)
            endpoints.append(cleaned)
        if len(endpoints) >= limit:
            return endpoints

    return endpoints


def extract_chat_decoder(content: str) -> ChatDecoderInfo:
    if not content:
        return ChatDecoderInfo()
    lower = content.lower()
    evidence: list[str] = []
    kind = "unknown"

    if "eventsource" in lower or "text/event-stream" in lower or "event-stream" in lower:
        kind = "sse"
        evidence.append("event-stream")

    if "websocket" in lower or "wss://" in content or "ws://" in content:
        if kind == "unknown":
            kind = "websocket"
        evidence.append("websocket")

    if "polling" in lower or "long polling" in lower or "setinterval" in lower:
        if kind == "unknown":
            kind = "polling"
        evidence.append("polling")

    chat_hints = _CHAT_HINT_RE.findall(content)
    for hint in chat_hints[:5]:
        if hint.lower() not in evidence:
            evidence.append(hint.lower())

    return ChatDecoderInfo(kind=kind, evidence=evidence)


def _clean_endpoint(endpoint: str) -> str:
    return endpoint.rstrip(").,;\"'")
