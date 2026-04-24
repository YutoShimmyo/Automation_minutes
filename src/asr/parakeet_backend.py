"""NVIDIA Parakeet ASR backend (requires nemo_toolkit[asr]).

Installation:
    pip install nemo_toolkit['asr']

Note: Parakeet is English-only. For multilingual audio, use faster-whisper.
"""
from __future__ import annotations

import subprocess
import time
from typing import Optional

from .base import ASRBackend, TranscriptionResult


class ParakeetBackend(ASRBackend):
    """ASR backend using NVIDIA NeMo Parakeet TDT models (English only)."""

    DEFAULT_MODEL = "nvidia/parakeet-tdt-0.6b-v2"

    def __init__(self, model_name: str = ""):
        self.model_name = model_name or self.DEFAULT_MODEL

    @property
    def name(self) -> str:
        return f"parakeet/{self.model_name}"

    def transcribe(
        self, file_path: str, language: Optional[str] = None
    ) -> TranscriptionResult:
        try:
            import nemo.collections.asr as nemo_asr  # noqa: F401
        except ImportError as exc:
            raise RuntimeError(
                "NeMo toolkit is not installed.\n"
                "Install with:  pip install nemo_toolkit['asr']\n"
                "Or use a different ASR backend (e.g. faster_whisper)."
            ) from exc

        print(f"[ASR] Loading Parakeet model: {self.model_name}")
        model = nemo_asr.models.ASRModel.from_pretrained(model_name=self.model_name)
        model.eval()

        print(f"[ASR] Transcribing: {file_path}")
        start = time.perf_counter()
        transcriptions = model.transcribe([file_path])
        elapsed = time.perf_counter() - start

        text = transcriptions[0] if transcriptions else ""
        print(text)

        audio_duration = _get_audio_duration(file_path)
        rtf = elapsed / audio_duration if audio_duration > 0 else 0.0
        print(
            f"[ASR] RTF={rtf:.3f}  "
            f"(elapsed={elapsed:.1f}s / audio={audio_duration:.1f}s)"
        )

        del model
        return TranscriptionResult(
            text=text,
            language="en",
            language_probability=1.0,
            duration=audio_duration,
            rtf=rtf,
        )


def _get_audio_duration(file_path: str) -> float:
    """Return audio duration in seconds via ffprobe."""
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                file_path,
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return float(result.stdout.strip())
    except Exception:
        return 0.0
