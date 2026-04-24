# モデルライセンス一覧

このツールは以下のモデルを利用できます。  
**モデルはユーザー自身がダウンロード・利用する責任を負います。**  
各モデルのライセンスを必ず確認した上でご利用ください。

---

## ASR (音声認識) モデル

### faster-whisper / Whisper

| モデル | プリセット | ライセンス | 配布元 |
|--------|-----------|-----------|--------|
| Whisper large-v3 | C (Multilingual HQ) | MIT | [openai/whisper-large-v3](https://huggingface.co/openai/whisper-large-v3) |
| Whisper large-v3-turbo | B/D (Standard) | MIT | [openai/whisper-large-v3-turbo](https://huggingface.co/openai/whisper-large-v3-turbo) |
| Whisper medium | B/D (fallback) | MIT | [openai/whisper-medium](https://huggingface.co/openai/whisper-medium) |
| Whisper small | B/D (fallback) | MIT | [openai/whisper-small](https://huggingface.co/openai/whisper-small) |

- ライセンス全文: https://github.com/openai/whisper/blob/main/LICENSE

faster-whisper は CTranslate2 を使って Whisper を高速化したラッパーです。  
- リポジトリ: https://github.com/SYSTRAN/faster-whisper  
- ライセンス: MIT

### NVIDIA Parakeet (プリセット A)

| モデル | ライセンス | 配布元 |
|--------|-----------|--------|
| parakeet-tdt-0.6b-v2 | CC-BY-4.0 | [nvidia/parakeet-tdt-0.6b-v2](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v2) |

**注意事項:**  
- Parakeet は **英語専用** です。日本語には対応していません。
- CC-BY-4.0 ライセンスにより、商用利用・改変が可能ですが帰属表示が必要です。
- 利用規約: https://huggingface.co/nvidia/parakeet-tdt-0.6b-v2

---

## 議事録生成 (LLM) モデル

### Google Gemini (API)

| モデル | ライセンス | 配布元 |
|--------|-----------|--------|
| gemini-2.5-flash | Google Terms of Service | [Google AI Studio](https://aistudio.google.com/) |
| gemini-2.5-flash-lite | Google Terms of Service | [Google AI Studio](https://aistudio.google.com/) |
| gemini-2.0-flash | Google Terms of Service | [Google AI Studio](https://aistudio.google.com/) |

**注意事項:**  
- 商用利用の可否は Google の利用規約に従います。
- 無料枠の制限に注意してください。
- `gemini-1.5-flash` は現行 API では利用不可（2026-04 時点）。
- 利用規約: https://ai.google.dev/gemini-api/terms

### Gemma 4 E4B (mlx-vlm) ← デフォルト推奨

| モデル | ライセンス | 配布元 |
|--------|-----------|--------|
| gemma-4-e4b-it (4bit) | **Apache 2.0** | [mlx-community/gemma-4-e4b-it-4bit](https://huggingface.co/mlx-community/gemma-4-e4b-it-4bit) |

**注意事項:**  
- Apache 2.0 ライセンスのため**商用利用・改変が可能**です。
- マルチモーダルモデルですが、このツールではテキスト専用で使用します。
- `mlx-vlm` ランタイムが必要（`mlx-lm` では動きません）。
- 元モデル: https://huggingface.co/google/gemma-4-e4b-it
- ライセンス全文: https://ai.google.dev/gemma/docs/gemma_4_license

### Gemma 3 (mlx-lm / ollama)

| モデル | ライセンス | 配布元 |
|--------|-----------|--------|
| gemma-3-4b-it (4bit) | Gemma Terms of Use | [mlx-community/gemma-3-4b-it-4bit](https://huggingface.co/mlx-community/gemma-3-4b-it-4bit) |

**注意事項:**  
- Google の Gemma Terms of Use に従います（商用利用には条件あり）。
- 利用規約: https://ai.google.dev/gemma/terms

### Qwen 2.5 (mlx-lm)

| モデル | ライセンス | 配布元 |
|--------|-----------|--------|
| Qwen2.5-7B-Instruct (4bit) | Apache 2.0 | [mlx-community/Qwen2.5-7B-Instruct-4bit](https://huggingface.co/mlx-community/Qwen2.5-7B-Instruct-4bit) |

**注意事項:**  
- Apache 2.0 ライセンスのため商用利用・改変が可能です。

### Gemma 2 (ollama)

| モデル | ライセンス | 配布元 |
|--------|-----------|--------|
| gemma2:9b | Gemma Terms of Use | [Ollama library](https://ollama.com/library/gemma2) |

---

## 免責事項

- このツールはモデル本体を同梱・配布しません。
- ユーザーは各モデルのライセンスを確認し、自己責任で利用してください。
- 商用利用の可否は必ず各モデルの公式ライセンスを参照してください。
