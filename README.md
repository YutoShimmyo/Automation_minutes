# Meeting Minutes Automation

This tool automates the transcription and summarization of meeting audio files (m4a, mp3, etc.) using local AI models on your Mac.

## Features
- **Transcription**: Uses `faster-whisper` (`small` model) for fast, local speech-to-text.
- **Summarization**: Uses `mlx-lm` (Qwen2.5-7B) for generating meeting minutes (Optional).
- **Privacy**: Runs entirely on your Mac (Apple Silicon optimized).

## Prerequisites
- **uv**: For Python dependency management.
- **ffmpeg**: For audio processing.

## Installation

Initialize the environment and install dependencies:

```bash
uv sync
```

## Usage

1. **Prepare Audio**: Place your audio files (e.g., `.m4a`) in the `input/` directory.

2. **Run Transcription** (Fast, Text Only):
   ```bash
   uv run main.py input/your_audio.m4a
   ```
   This will generate a raw transcript in `output/your_audio.txt`.

3. **Run with Summarization** (Optional):
   ```bash
   uv run main.py input/your_audio.m4a --summarize
   ```
   *Note: This requires downloading a large LLM (~4-5GB) on the first run and requires sufficient RAM/Disk space.*

## Output
- `output/filename.txt`: Raw transcription text.
- `output/filename_minutes.md`: Structured meeting minutes (Action Items, Key Points).
