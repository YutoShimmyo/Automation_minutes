"""Abstract base class for ASR backends."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class TranscriptionResult:
    text: str
    language: str
    language_probability: float
    duration: float   # audio duration in seconds
    rtf: float        # real-time factor (elapsed / duration)


class ASRBackend(ABC):
    """Abstract base for all speech-to-text backends."""

    @abstractmethod
    def transcribe(
        self,
        file_path: str,
        language: Optional[str] = None,
    ) -> TranscriptionResult:
        """Transcribe audio file and return a TranscriptionResult."""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of this backend."""
        ...
