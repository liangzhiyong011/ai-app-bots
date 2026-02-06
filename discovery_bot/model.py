from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class PageMetadata:
    title: str = ""
    description: str = ""
    og_title: str = ""
    og_description: str = ""
    language: str = ""
    text_sample: str = ""


@dataclass
class FetchResult:
    url: str
    final_url: str
    status_code: int
    headers: Dict[str, str]
    content: str
    error: str = ""


@dataclass
class ChatDecoderInfo:
    kind: str = "unknown"
    evidence: List[str] = field(default_factory=list)


@dataclass
class DiscoveryResult:
    url: str
    final_url: str = ""
    status_code: int = 0
    metadata: PageMetadata = field(default_factory=PageMetadata)
    is_ai_app: bool = False
    confidence: float = 0.0
    categories: List[str] = field(default_factory=list)
    chat_capability: bool = False
    chat_decoder: ChatDecoderInfo = field(default_factory=ChatDecoderInfo)
    endpoints: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
