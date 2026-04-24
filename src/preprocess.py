import re

def clean_transcript(text: str) -> str:
    """
    Cleans transcript text by removing multiple newlines and merging lines.
    
    Strategy:
    1. Replace sequence of 2 or more newlines with a special marker (DOUBLE_NEWLINE).
    2. Replace single newlines with a space.
    3. Restore the special marker to a single newline (paragraph break).
    4. Collapse multiple spaces.
    """
    if not text:
        return ""

    if not text:
        return ""

    # Normalize multiple newlines to max 2 (paragraph break)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Trim whitespace from lines
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    
    return text.strip()

def count_tokens(text: str) -> int:
    """
    Rough estimate of tokens.
    - CJK characters (Japanese/Chinese) ≈ 1 token/character
    - Latin characters ≈ 1 token / 4 characters
    Uses a heuristic based on character type ratio.
    """
    if not text:
        return 0
    cjk_count = sum(1 for ch in text if "\u3000" <= ch <= "\u9FFF" or "\uF900" <= ch <= "\uFAFF")
    latin_count = len(text) - cjk_count
    return cjk_count + (latin_count // 4)


# Context window limits per runtime (input tokens available for transcript)
# Subtract ~300 for system prompt and ~1500 for generated output.
_CONTEXT_LIMITS: dict[str, int] = {
    "mlx-vlm":  131072 - 2000,   # Gemma 4 E4B: 128K
    "mlx-lm":   131072 - 2000,   # Qwen2.5-7B etc.: 128K
    "ollama":   8192   - 2000,   # gemma2:9b default: 8K
    "api":      999999,          # Gemini 1.5 Flash: 1M tokens
}

# Meeting speech density estimates (tokens per minute)
# Japanese: ~300 tokens/min,  English: ~150 tokens/min
_TOKENS_PER_MINUTE = {"ja": 300, "en": 150, "auto": 300}


def check_transcript_length(
    text: str, runtime: str, language: str = "auto"
) -> tuple[int, bool, str]:
    """
    Estimate token count and check if transcript fits in the model's context window.

    Returns:
        (token_count, is_within_limit, warning_message)
    """
    tokens = count_tokens(text)
    limit = _CONTEXT_LIMITS.get(runtime, 128000)
    tpm = _TOKENS_PER_MINUTE.get(language, 300)

    if tokens <= limit:
        return tokens, True, ""

    # Over limit: estimate safe meeting duration
    safe_minutes = limit // tpm
    actual_minutes = tokens // tpm
    msg = (
        f"[Warning] Transcript is ~{tokens:,} tokens "
        f"(≈{actual_minutes} min of speech), "
        f"but {runtime!r} context limit is ~{limit:,} tokens "
        f"(≈{safe_minutes} min of speech).\n"
        f"  → The transcript will be truncated. "
        "Consider splitting the audio into shorter segments."
    )
    return tokens, False, msg


def truncate_transcript(text: str, runtime: str, language: str = "auto") -> str:
    """Truncate transcript to fit within the model's context window if needed."""
    tokens, within_limit, warning = check_transcript_length(text, runtime, language)
    if within_limit:
        return text
    print(warning)

    limit = _CONTEXT_LIMITS.get(runtime, 128000)
    # Estimate character count to keep (rough inverse of count_tokens)
    cjk_ratio = sum(
        1 for ch in text if "\u3000" <= ch <= "\u9FFF" or "\uF900" <= ch <= "\uFAFF"
    ) / max(len(text), 1)
    chars_per_token = 1.0 if cjk_ratio > 0.5 else 4.0
    max_chars = int(limit * chars_per_token)
    return text[:max_chars] + "\n\n[... 文字起こしが長すぎるため以降は省略されました ...]"
