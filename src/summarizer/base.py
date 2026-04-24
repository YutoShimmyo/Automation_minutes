"""Abstract base class for summarization backends."""
from abc import ABC, abstractmethod


class SummarizerBackend(ABC):
    """Abstract base for all meeting-minutes generation backends."""

    @abstractmethod
    def summarize(self, transcript: str, language: str = "auto") -> str:
        """Generate structured meeting minutes from the given transcript."""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of this backend."""
        ...
