"""faster-whisper ASR backend."""
from __future__ import annotations

import time
from typing import Optional

from .base import ASRBackend, TranscriptionResult


class FasterWhisperBackend(ASRBackend):
    """ASR backend powered by faster-whisper (CTranslate2 quantized Whisper)."""

    def __init__(
        self,
        model_size: str = "large-v3-turbo",
        device: str = "",
        compute_type: str = "",
    ):
        self.model_size = model_size
        self._device = device or _auto_device()
        self._compute_type = compute_type or _auto_compute_type(self._device)

    @property
    def name(self) -> str:
        return f"faster-whisper/{self.model_size}"

    def transcribe(
        self, file_path: str, language: Optional[str] = None
    ) -> TranscriptionResult:
        from faster_whisper import WhisperModel

        print(
            f"[ASR] Loading faster-whisper: {self.model_size} "
            f"on {self._device} ({self._compute_type})"
        )
        model = WhisperModel(
            self.model_size, device=self._device, compute_type=self._compute_type
        )

        lang_arg = language if language and language != "auto" else None
        print(f"[ASR] Transcribing: {file_path}" + (f" (language={lang_arg})" if lang_arg else ""))
        start = time.perf_counter()

        segments, info = model.transcribe(
            file_path,
            language=lang_arg,
            beam_size=1,
            vad_filter=True,
        )

        lines: list[str] = []
        for seg in segments:
            text = seg.text.strip()
            if text:
                print(text)
                lines.append(text)

        elapsed = time.perf_counter() - start
        audio_duration = getattr(info, "duration", 0.0) or 0.0
        rtf = elapsed / audio_duration if audio_duration > 0 else 0.0

        print(
            f"[ASR] Detected language: {info.language} "
            f"(prob={info.language_probability:.2f})"
        )
        print(
            f"[ASR] RTF={rtf:.3f}  "
            f"(elapsed={elapsed:.1f}s / audio={audio_duration:.1f}s)"
        )

        del model
        return TranscriptionResult(
            text="\n".join(lines),
            language=info.language,
            language_probability=info.language_probability,
            duration=audio_duration,
            rtf=rtf,
        )


def _auto_device() -> str:
    try:
        import torch  # noqa: F401

        if torch.cuda.is_available():
            return "cuda"
    except ImportError:
        pass
    return "cpu"


def _auto_compute_type(device: str) -> str:
    return "float16" if device == "cuda" else "int8"
