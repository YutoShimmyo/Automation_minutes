"""MLX-LM local summarizer backend (Apple Silicon only)."""
from __future__ import annotations

import gc

from .base import SummarizerBackend
from ..preprocess import clean_transcript


_SYSTEM_PROMPT_EN = """\
You are an expert meeting secretary.
Create structured meeting minutes from the transcript.

Output in Markdown:

# Meeting Minutes

## Summary
(2–3 sentence overview)

## Key Discussion Points
- (bullet points)

## Action Items
- [ ] (task) — (owner if mentioned)
"""

_SYSTEM_PROMPT_JA = """\
あなたは優秀な会議秘書です。
以下の書き起こしから構造化された議事録をMarkdown形式で作成してください。

# 議事録

## 概要
（2〜3文の要約）

## 主な議論のポイント
- （箇条書き）

## アクションアイテム
- [ ] （タスク）— （担当者）
"""


class MLXSummarizer(SummarizerBackend):
    """Summarizer using mlx-lm on Apple Silicon (M1/M2/M3/M4)."""

    DEFAULT_MODEL = "mlx-community/gemma-3-4b-it-4bit"

    def __init__(self, model_path: str = ""):
        self.model_path = model_path or self.DEFAULT_MODEL

    @property
    def name(self) -> str:
        return f"mlx-lm/{self.model_path}"

    def summarize(self, transcript: str, language: str = "auto") -> str:
        try:
            from mlx_lm import load, generate
        except ImportError as exc:
            raise RuntimeError(
                "mlx-lm is not installed.\n"
                "  Install:  uv add mlx-lm\n"
                "  Note: mlx-lm requires Apple Silicon (M1/M2/M3/M4).\n"
                "  On other hardware use --minutes-backend api or ollama."
            ) from exc

        from ..preprocess import truncate_transcript, count_tokens
        cleaned = clean_transcript(transcript)
        cleaned = truncate_transcript(cleaned, runtime="mlx-lm", language=language)
        token_est = count_tokens(cleaned)
        print(f"[Summarizer] Estimated input tokens: ~{token_est:,}")
        system_prompt = _SYSTEM_PROMPT_JA if language == "ja" else _SYSTEM_PROMPT_EN

        print(f"[Summarizer] Loading MLX model: {self.model_path}")
        model, tokenizer = load(self.model_path)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"以下が書き起こしです：\n\n{cleaned}"},
        ]
        prompt = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )

        print("[Summarizer] Generating summary…")
        response = generate(model, tokenizer, prompt=prompt, verbose=True, max_tokens=2048)

        del model, tokenizer
        gc.collect()
        return response
