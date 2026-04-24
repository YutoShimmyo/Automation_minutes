"""Meeting Minutes Automation — main entry point.

Usage:
    uv run main.py input/meeting.mp4
    uv run main.py input/meeting.mp4 --language en --profile quality
    uv run main.py input/meeting.mp4 --minutes-backend api
    uv run main.py input/meeting.mp4 --minutes-backend local --minutes-local-runtime ollama
    uv run main.py input/meeting.mp4 --config my_config.yaml
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

from src.config import load_config, apply_cli_overrides
from src.asr import create_backend
from src.summarizer import create_summarizer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="minutes",
        description="Transcribe audio/video meetings and generate structured minutes.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  # Transcription only (fastest)
  uv run main.py input/meeting.mp4

  # English high-quality transcription + Gemini minutes
  uv run main.py input/meeting.mp4 --language en --profile quality --minutes-backend api

  # Japanese high-quality + local mlx-lm minutes
  uv run main.py input/meeting.mp4 --language ja --profile quality --minutes-backend local

  # Use Ollama for minutes
  uv run main.py input/meeting.mp4 --minutes-backend local --minutes-local-runtime ollama

  # Force a specific model
  uv run main.py input/meeting.mp4 --asr-model large-v3

  # Use a custom config file
  uv run main.py input/meeting.mp4 --config my_config.yaml
""",
    )

    parser.add_argument(
        "audio_file",
        help="Path to the audio/video file (m4a, mp3, mp4, wav, …)",
    )

    parser.add_argument(
        "--config",
        metavar="PATH",
        help="Path to config.yaml (default: config.yaml in project root)",
    )

    # General
    parser.add_argument(
        "--language",
        choices=["ja", "en", "auto"],
        help="Audio language. 'auto' lets Whisper detect it (default: auto)",
    )
    parser.add_argument(
        "--profile",
        choices=["fast", "standard", "quality"],
        help="Quality profile; affects ASR preset auto-selection (default: standard)",
    )

    # ASR
    asr = parser.add_argument_group("ASR options")
    asr.add_argument(
        "--asr-preset",
        choices=["A", "B", "C", "D"],
        metavar="PRESET",
        help=(
            "ASR preset: "
            "A=English·HQ, B=English·Standard, "
            "C=Multilingual·HQ, D=Multilingual·Standard"
        ),
    )
    asr.add_argument(
        "--asr-backend",
        choices=["faster_whisper", "parakeet"],
        help="Override ASR backend regardless of preset",
    )
    asr.add_argument(
        "--asr-model",
        metavar="MODEL",
        help="Override ASR model (e.g. 'large-v3', 'medium', 'small')",
    )

    # Minutes
    mins = parser.add_argument_group("Minutes options")
    mins.add_argument(
        "--minutes-backend",
        choices=["none", "api", "local"],
        help="Minutes generation backend (default: none — transcription only)",
    )
    mins.add_argument(
        "--minutes-language",
        choices=["ja", "en", "auto"],
        help=(
            "Output language for the minutes (default: ja). "
            "'auto' follows the detected audio language."
        ),
    )
    mins.add_argument(
        "--minutes-local-runtime",
        choices=["mlx-lm", "mlx-vlm", "ollama"],
        help=(
            "Local LLM runtime when --minutes-backend=local (default: mlx-vlm). "
            "Use mlx-vlm for multimodal models like Gemma 4 E4B."
        ),
    )
    mins.add_argument(
        "--minutes-model",
        metavar="MODEL",
        help="Model path/name for minutes generation (HuggingFace ID or local path)",
    )

    # Legacy flags kept for backward compatibility
    legacy = parser.add_argument_group("Legacy options (backward compatibility)")
    legacy.add_argument(
        "--summarize",
        action="store_true",
        help="[Legacy] Enable local mlx-lm summarization (same as --minutes-backend local)",
    )
    legacy.add_argument(
        "--use-gemini",
        action="store_true",
        help="[Legacy] Enable Gemini API summarization (same as --minutes-backend api)",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # ── Load config ──────────────────────────────────────────────────────────
    cfg = load_config(args.config)
    cfg = apply_cli_overrides(cfg, args)

    # Handle legacy flags
    if getattr(args, "use_gemini", False) and cfg.minutes.backend == "none":
        cfg.minutes.backend = "api"
    if getattr(args, "summarize", False) and cfg.minutes.backend == "none":
        cfg.minutes.backend = "local"

    # ── Validate input file ───────────────────────────────────────────────────
    audio_path = args.audio_file
    if not os.path.exists(audio_path):
        print(f"Error: File not found: {audio_path}", file=sys.stderr)
        sys.exit(1)

    base_name = Path(audio_path).stem
    transcript_dir = Path("output/transcripts")
    minutes_dir = Path("output/minutes")
    transcript_dir.mkdir(parents=True, exist_ok=True)
    minutes_dir.mkdir(parents=True, exist_ok=True)

    transcript_file = transcript_dir / f"{base_name}.txt"
    minutes_file = minutes_dir / f"{base_name}_minutes.md"

    total_start = time.perf_counter()

    # ── Step 1: Transcription ─────────────────────────────────────────────────
    _section("Step 1: Transcription")

    if transcript_file.exists():
        print(f"Transcript already exists at {transcript_file} — skipping.")
        transcript = transcript_file.read_text(encoding="utf-8")
    else:
        asr = create_backend(
            preset=cfg.asr.preset,
            backend_override=cfg.asr.backend,
            model_override=cfg.asr.model,
            device=cfg.asr.device,
            profile=cfg.profile,
            language=cfg.language,
        )
        print(f"[ASR] Backend: {asr.name}")
        result = asr.transcribe(
            audio_path,
            language=cfg.language if cfg.language != "auto" else None,
        )
        transcript = result.text
        transcript_file.write_text(transcript, encoding="utf-8")
        print(f"\n[ASR] Transcript saved: {transcript_file}")

    # ── Step 2: Minutes Generation ────────────────────────────────────────────
    _section("Step 2: Minutes Generation")

    if cfg.minutes.backend == "none":
        print(
            "Skipped. Use one of the following to enable:\n"
            "  --minutes-backend api    (requires GEMINI_API_KEY in .env)\n"
            "  --minutes-backend local  (requires mlx-lm or Ollama)"
        )
    else:
        summarizer = create_summarizer(
            backend=cfg.minutes.backend,
            api_provider=cfg.minutes.api.provider,
            api_model=cfg.minutes.api.model,
            local_runtime=cfg.minutes.local.runtime,
            model_path=cfg.minutes.local.model_path,
            ollama_model=cfg.minutes.local.ollama_model,
            ollama_url=cfg.minutes.local.ollama_url,
        )
        if summarizer:
            print(f"[Summarizer] Backend: {summarizer.name}")
            # Resolve output language: "auto" follows the detected audio language
            minutes_lang = cfg.minutes.output_language
            if minutes_lang == "auto":
                minutes_lang = cfg.language  # may still be "auto" if no detection ran
            minutes = summarizer.summarize(transcript, language=minutes_lang)
            minutes_file.write_text(minutes, encoding="utf-8")
            print(f"[Summarizer] Minutes saved: {minutes_file}")

    # ── Summary ───────────────────────────────────────────────────────────────
    total_elapsed = time.perf_counter() - total_start
    _section(f"Done!  Total time: {total_elapsed:.1f}s")
    print(f"  Transcript : {transcript_file}")
    if cfg.minutes.backend != "none" and minutes_file.exists():
        print(f"  Minutes    : {minutes_file}")


def _section(title: str) -> None:
    bar = "=" * 50
    print(f"\n{bar}\n{title}\n{bar}")


if __name__ == "__main__":
    main()
