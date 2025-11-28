import gc
from mlx_lm import load, generate

def summarize_text(transcript, model_path="mlx-community/Qwen2.5-7B-Instruct-4bit"):
    """
    Summarizes the transcript using a local LLM via MLX.
    
    Args:
        transcript (str): The full text of the meeting transcript.
        model_path (str): HuggingFace repo ID for the MLX model.
        
    Returns:
        str: Generated meeting minutes in Markdown format.
    """
    print(f"Loading LLM: {model_path}...")
    model, tokenizer = load(model_path)
    
    # Construct the prompt
    system_prompt = """
    あなたは優秀な研究室の秘書です。
    以下の会議の書き起こしテキストから、議事録を作成してください。
    
    出力フォーマットは以下のMarkdown形式を厳守してください：
    
    # 議事録
    
    ## 概要
    (会議の全体的な内容を簡潔に要約)
    
    ## 教授が詰めた点・質問した点
    (教授が指摘した問題点、質問、確認事項などを箇条書きで)
    
    ## やるべきこと (Action Items)
    (今後やるべきタスクを箇条書きで)
    """
    
    user_message = f"以下が書き起こしテキストです：\n\n{transcript}"
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
    
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    
    print("Generating summary (this may take a few minutes)...")
    response = generate(model, tokenizer, prompt=prompt, verbose=True, max_tokens=2048)
    
    # Clean up memory
    del model
    del tokenizer
    gc.collect()
    
    return response
