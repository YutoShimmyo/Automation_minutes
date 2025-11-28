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
    segments, info = model.transcribe(file_path, beam_size=5)

    print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

    transcript_parts = []
    for segment in segments:
        # Format: Text only (no timestamps)
        line = segment.text
        print(line)
        transcript_parts.append(line)
    
    full_transcript = "\n".join(transcript_parts)
    
    # Explicitly delete model to free up RAM
    del model
    
    return full_transcript
