"""MLX-VLM local summarizer backend (Apple Silicon only).

Required for multimodal models like Gemma 4 E4B.
Install: uv add mlx-vlm
"""
from __future__ import annotations

import gc

from .base import SummarizerBackend
from ..preprocess import clean_transcript


_SYSTEM_PROMPT_JA = """\
あなたは優秀な会議秘書です。
以下の書き起こしから構造化された議事録を日本語で作成してください。
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

_SYSTEM_PROMPT_EN = """\
You are an expert meeting secretary.
Create structured meeting minutes in English from the transcript below.
The transcript may contain speech-to-text errors; use context to interpret them.

Output in Markdown:

# Meeting Minutes

## Summary
(2–3 sentence overview)

## Key Discussion Points
- (bullet points)

## Action Items
- [ ] (task) — (owner if mentioned)
"""


class MLXVLMSummarizer(SummarizerBackend):
    """Summarizer using mlx-vlm on Apple Silicon (supports multimodal models like Gemma 4)."""

    DEFAULT_MODEL = "mlx-community/gemma-4-e4b-it-4bit"

    def __init__(self, model_path: str = ""):
        self.model_path = model_path or self.DEFAULT_MODEL

    @property
    def name(self) -> str:
        return f"mlx-vlm/{self.model_path}"

    def summarize(self, transcript: str, language: str = "ja") -> str:
        try:
            from mlx_vlm import load, generate
            from mlx_vlm.prompt_utils import apply_chat_template
            from mlx_vlm.utils import load_config as vlm_load_config
        except ImportError as exc:
            raise RuntimeError(
                "mlx-vlm is not installed.\n"
                "  Install:  uv add mlx-vlm\n"
                "  Note: mlx-vlm requires Apple Silicon (M1/M2/M3/M4).\n"
                "  On other hardware use --minutes-backend api or ollama."
            ) from exc

        from ..preprocess import truncate_transcript, count_tokens
        cleaned = clean_transcript(transcript)
        cleaned = truncate_transcript(cleaned, runtime="mlx-vlm", language=language)
        token_est = count_tokens(cleaned)
        print(f"[Summarizer] Estimated input tokens: ~{token_est:,}")
        system_prompt = _SYSTEM_PROMPT_JA if language == "ja" else _SYSTEM_PROMPT_EN
        user_message = f"{system_prompt}\n\n以下が書き起こしです：\n\n{cleaned}"

        print(f"[Summarizer] Loading MLX-VLM model: {self.model_path}")
        model, processor = load(self.model_path)
        config = vlm_load_config(self.model_path)

        # apply_chat_template formats the prompt for the specific model
        # num_images=0 for text-only inference
        prompt = apply_chat_template(
            processor, config, user_message, num_images=0
        )

        print("[Summarizer] Generating summary…")
        result = generate(
            model,
            processor,
            prompt=prompt,
            image=None,
            max_tokens=2048,
            verbose=True,
        )

        del model, processor
        gc.collect()

        # mlx-vlm returns a GenerationResult object; extract text if needed
        if isinstance(result, str):
            return result
        return str(result.text) if hasattr(result, "text") else str(result)
