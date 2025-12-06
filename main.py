import argparse
import os
import sys
import time
from src.transcribe import transcribe_audio
from src.summarize import summarize_text

def main():
    parser = argparse.ArgumentParser(description="Automate meeting minutes from audio.")
    parser.add_argument("audio_file", help="Path to the input file (m4a, mp3, mp4, etc.)")
    parser.add_argument("--summarize", action="store_true", help="Enable summarization (requires downloading LLM)")
    args = parser.parse_args()

    audio_path = args.audio_file
    if not os.path.exists(audio_path):
        print(f"Error: File not found: {audio_path}")
        sys.exit(1)

    base_name = os.path.splitext(os.path.basename(audio_path))[0]
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    transcript_file = os.path.join(output_dir, f"{base_name}.txt")
    minutes_file = os.path.join(output_dir, f"{base_name}_minutes.md")

    start_time = time.time()

    # Step 1: Transcription
    print("=== Step 1: Transcription ===")
    if os.path.exists(transcript_file):
        print(f"Transcript already exists at {transcript_file}. Skipping transcription.")
        with open(transcript_file, "r", encoding="utf-8") as f:
            transcript = f.read()
    else:
        transcript = transcribe_audio(audio_path, model_size="small")
        with open(transcript_file, "w", encoding="utf-8") as f:
            f.write(transcript)
        print(f"Transcript saved to {transcript_file}")

    # Step 2: Summarization
    if args.summarize:
        print("\n=== Step 2: Summarization ===")
        # Note: transcribe_audio explicitly deletes the Whisper model to free RAM.
        # We can proceed to load the LLM.
        
        summary = summarize_text(transcript)
        
        with open(minutes_file, "w", encoding="utf-8") as f:
            f.write(summary)
        print(f"Minutes saved to {minutes_file}")
    else:
        print("\n=== Step 2: Summarization (Skipped) ===")
        print("Use --summarize flag to enable summarization.")
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n=== Done! ===")
    print(f"Total time: {duration:.2f} seconds")
    print(f"Minutes saved to {minutes_file}")

if __name__ == "__main__":
    main()
