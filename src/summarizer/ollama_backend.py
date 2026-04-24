"""Ollama local summarizer backend (uses Ollama REST API, no extra dependencies)."""
from __future__ import annotations

import json
import urllib.error
import urllib.request

from .base import SummarizerBackend
from ..preprocess import clean_transcript


_SYSTEM_PROMPT_EN = """\
You are an expert meeting secretary.
Create structured meeting minutes from the transcript.
Output in Markdown with sections: Summary, Key Discussion Points, Action Items."""

_SYSTEM_PROMPT_JA = """\
あなたは優秀な会議秘書です。
書き起こしから構造化された議事録をMarkdown形式で作成してください。
セクション：概要、主な議論のポイント、アクションアイテム"""


class OllamaSummarizer(SummarizerBackend):
    """Summarizer using a locally running Ollama server."""

    def __init__(
        self,
        model: str = "gemma2:9b",
        base_url: str = "http://localhost:11434",
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")

    @property
    def name(self) -> str:
        return f"ollama/{self.model}"

    def summarize(self, transcript: str, language: str = "auto") -> str:
        from ..preprocess import truncate_transcript, count_tokens
        cleaned = clean_transcript(transcript)
        cleaned = truncate_transcript(cleaned, runtime="ollama", language=language)
        token_est = count_tokens(cleaned)
        print(f"[Summarizer] Estimated input tokens: ~{token_est:,}")
        system_prompt = _SYSTEM_PROMPT_JA if language == "ja" else _SYSTEM_PROMPT_EN

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Transcript:\n\n{cleaned}"},
            ],
            "stream": False,
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/api/chat",
            data=data,
            headers={"Content-Type": "application/json"},
        )

        print(f"[Summarizer] Sending to Ollama ({self.model}) at {self.base_url}…")
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                result = json.loads(resp.read())
                return result["message"]["content"]
        except urllib.error.URLError as e:
            raise RuntimeError(
                f"Cannot connect to Ollama at {self.base_url}.\n"
                "Make sure Ollama is running:  ollama serve\n"
                f"Pull the model if needed:    ollama pull {self.model}\n"
                f"Original error: {e}"
            ) from e
