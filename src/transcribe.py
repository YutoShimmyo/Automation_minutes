import os
from faster_whisper import WhisperModel

def transcribe_audio(file_path, model_size="small", device="cpu", compute_type="int8"):
    """
    Transcribes audio file using faster-whisper.
    
    Args:
        file_path (str): Path to the audio file.
        model_size (str): Model size to use (default: small).
        device (str): Device to run on (default: cpu).
        compute_type (str): Quantization type (default: int8).
        
    Returns:
        str: Full transcription text.
    """
    print(f"Loading Whisper model: {model_size} on {device} with {compute_type}...")
    model = WhisperModel(model_size, device=device, compute_type=compute_type)

    print(f"Transcribing {file_path}...")
    # Optimization: beam_size=1 (greedy search) is faster. vad_filter=True skips silence.
    segments, info = model.transcribe(file_path, beam_size=1, vad_filter=True)

    print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

    full_transcript = ""

    for segment in segments:
        text = segment.text.strip()
        print(text)
        # Simply append with newline as requested for LLM input
        full_transcript += text + "\n"

    
    # Explicitly delete model to free up RAM
    del model
    
    return full_transcript
