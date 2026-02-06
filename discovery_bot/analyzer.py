from __future__ import annotations

from .model import PageMetadata


AI_KEYWORDS = [
    "ai",
    "artificial intelligence",
    "machine learning",
    "ml",
    "llm",
    "gpt",
    "generative",
    "neural",
    "language model",
]

CATEGORY_KEYWORDS = {
    "chat": ["chat", "assistant", "conversation", "dialog", "messages"],
    "image": ["image", "photo", "diffusion", "generate images", "visual"],
    "audio": ["audio", "speech", "voice", "tts", "transcribe", "podcast"],
    "video": ["video", "animate", "clip", "movie", "caption"],
    "code": ["code", "developer", "programming", "copilot", "IDE"],
    "search": ["search", "retrieve", "ranking", "knowledge base", "semantic"],
    "productivity": ["productivity", "workflow", "automation", "ops", "task"],
    "data": ["data", "analytics", "insights", "dashboard", "report"],
    "agent": ["agent", "autonomous", "multi-agent", "tool calling"],
    "design": ["design", "ui", "ux", "mockup", "prototype"],
}


def analyze_app(metadata: PageMetadata) -> tuple[bool, float, list[str], bool]:
    text = _build_text(metadata)
    ai_hits = _count_hits(text, AI_KEYWORDS)
    is_ai_app = ai_hits > 0
    confidence = min(1.0, ai_hits / 4.0)

    category_scores: dict[str, int] = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        hits = _count_hits(text, keywords)
        if hits:
            category_scores[category] = hits

    categories = [
        item[0]
        for item in sorted(category_scores.items(), key=lambda x: (-x[1], x[0]))
    ]

    chat_capability = "chat" in categories or _count_hits(text, CATEGORY_KEYWORDS["chat"]) > 0
    return is_ai_app, confidence, categories, chat_capability


def _build_text(metadata: PageMetadata) -> str:
    parts = [
        metadata.title,
        metadata.description,
        metadata.og_title,
        metadata.og_description,
        metadata.text_sample,
    ]
    return " ".join(part for part in parts if part).lower()


def _count_hits(text: str, keywords: list[str]) -> int:
    hits = 0
    for keyword in keywords:
        if keyword.lower() in text:
            hits += 1
    return hits
