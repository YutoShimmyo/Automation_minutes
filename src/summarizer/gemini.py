"""Google Gemini API summarizer backend."""
from __future__ import annotations

import os
import time
from typing import Optional

from dotenv import load_dotenv

from .base import SummarizerBackend
from ..preprocess import clean_transcript


_SYSTEM_PROMPT_EN = """\
You are an expert meeting secretary.
Create structured meeting minutes from the transcript below.
The transcript may contain speech-to-text errors; use context to interpret them.

Output in Markdown:

# Meeting Minutes

## Summary
(2–3 sentence overview of the meeting)

## Key Discussion Points
- (bullet points)

## Action Items
- [ ] (task) — (owner if mentioned)
"""

_SYSTEM_PROMPT_JA = """\
あなたは優秀な会議秘書です。
以下の書き起こしから構造化された議事録を作成してください。
テキストは音声認識によるものでエラーを含む可能性があります。文脈から補完してください。

Markdown形式で出力してください：

# 議事録

## 概要
（2〜3文の要約）

## 主な議論のポイント
- （箇条書き）

## アクションアイテム
- [ ] （タスク）— （担当者、わかれば）
"""


class GeminiSummarizer(SummarizerBackend):
    """Summarizer using Google Gemini API."""

    def __init__(self, model: str = "gemini-1.5-flash", api_key: Optional[str] = None):
        load_dotenv()
        self.model = model
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY is not set.\n"
                "  1. Copy template:  cp .env.template .env\n"
                "  2. Edit .env and set GEMINI_API_KEY=<your_key>\n"
                "  Get a key at: https://aistudio.google.com/app/apikey"
            )

    @property
    def name(self) -> str:
        return f"gemini/{self.model}"

    def summarize(self, transcript: str, language: str = "auto") -> str:
        from google import genai

        from ..preprocess import truncate_transcript, count_tokens
        cleaned = clean_transcript(transcript)
        cleaned = truncate_transcript(cleaned, runtime="api", language=language)
        token_est = count_tokens(cleaned)
        print(f"[Summarizer] Estimated input tokens: ~{token_est:,}")
        system_prompt = _SYSTEM_PROMPT_JA if language == "ja" else _SYSTEM_PROMPT_EN
        prompt = f"{system_prompt}\n\nTranscript:\n{cleaned}"

        client = genai.Client(api_key=self.api_key)

        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                )
                return response.text
            except Exception as e:
                print(f"[Summarizer] Attempt {attempt + 1} failed: {e}")
                if attempt < 2:
                    wait = 2.0 * (2**attempt)
                    print(f"[Summarizer] Retrying in {wait:.0f}s...")
                    time.sleep(wait)
                else:
                    raise RuntimeError(
                        f"Gemini summarization failed after 3 attempts: {e}"
                    ) from e
        return ""
