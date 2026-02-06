from __future__ import annotations

import html
from html.parser import HTMLParser

from .model import PageMetadata


class _MetadataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title_parts: list[str] = []
        self.text_parts: list[str] = []
        self.meta: dict[str, str] = {}
        self.language: str = ""
        self._in_title = False
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {key.lower(): value for key, value in attrs if key}
        if tag == "html" and not self.language:
            lang = attrs_dict.get("lang")
            if lang:
                self.language = lang
        if tag == "title":
            self._in_title = True
        if tag in {"script", "style", "noscript"}:
            self._skip_depth += 1
        if tag == "meta":
            name = (attrs_dict.get("name") or attrs_dict.get("property") or "").lower()
            content = attrs_dict.get("content") or ""
            if name and content:
                self.meta[name] = content

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        if tag in {"script", "style", "noscript"} and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if not data.strip():
            return
        if self._in_title:
            self.title_parts.append(data.strip())
            return
        if self._skip_depth == 0:
            self.text_parts.append(data.strip())


def parse_html(content: str) -> PageMetadata:
    parser = _MetadataParser()
    try:
        parser.feed(content)
    except Exception:
        pass
    title = html.unescape(" ".join(parser.title_parts)).strip()
    description = parser.meta.get("description", "").strip()
    og_title = parser.meta.get("og:title", "").strip()
    og_description = parser.meta.get("og:description", "").strip()
    text = _normalize_text(" ".join(parser.text_parts))
    if not description:
        description = text[:300].strip()
    text_sample = text[:600].strip()
    return PageMetadata(
        title=title,
        description=description,
        og_title=og_title,
        og_description=og_description,
        language=parser.language,
        text_sample=text_sample,
    )


def _normalize_text(text: str) -> str:
    return " ".join(text.split())
