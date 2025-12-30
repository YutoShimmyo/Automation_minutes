# Meeting Minutes Automation

This tool automates the transcription and summarization of meeting audio/video files using AI. It supports fast local execution on Mac (Apple Silicon) and remote execution on a GPU cluster (Slurm).

## Features
- **Transcription**: Uses `faster-whisper` (`small` model) with optimized settings (greedy search, VAD) for high speed.
- **Summarization**: Uses `mlx-lm` (Qwen2.5-7B) to generate structured minutes (Optional).
- **Format Support**: Supports `.m4a`, `.mp3`, `.mp4` (video), etc.
- **Dual Mode**:
    - **Local**: Runs entirely on your Mac.
    - **Remote**: Offloads processing to a GPU server (e.g., NAIST cc21) via Slurm.

## Prerequisites
- **uv**: For Python dependency management.
- **ffmpeg**: For audio processing.
- **SSH Access** (for Remote Mode): Password-less SSH access to the remote server.

## Installation

Initialize the environment and install dependencies:

```bash
uv sync
```

### 1. Local Execution (Mac)
**Transcription Only (Fastest):**
```bash
uv run main.py input/your_file.mp4
```
*Generates `output/transcripts/your_file.txt`.*

### 2. Gemini Automation (Recommended)
Automatically transcribe and summarize using Gemini 1.5 Flash (Free Tier).

1.  Copy `.env.template` to `.env` and set your `GEMINI_API_KEY`.
2.  Run:
    ```bash
    uv run main.py input/your_file.mp4 --use-gemini
    ```
*Generates `output/minutes/your_file_minutes.md`.*

### 2. Remote Execution (Slurm)
Best for large files or batch processing on a GPU server.

```bash
python deploy.py input/your_file.mp4 <user>@cc21dev0
```
*(Replace `<user>` with your username)*

**What this does:**
1.  Archives your project code.
2.  Transfers code and input file to the server.
3.  Submits a Slurm job (`gpu_short` partition).
4.  Logs and results will be stored in `/work/<user>/Automation_minutes_Job/` on the server.

## Output
- `output/filename.txt`: Raw transcription text.
- `output/filename_minutes.md`: Structured meeting minutes (if summarization is enabled).
