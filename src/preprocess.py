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
    Rough estimate of tokens (character count / 4).
    Gemini 1.5 Flash has a huge context window, so specific tokenizer isn't critical.
    """
    return len(text) // 4
