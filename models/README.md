# models/ — ローカルモデル配置ディレクトリ

このディレクトリにローカルモデルを配置します。  
**モデルファイル自体は Git に含まれません**（`.gitignore` で除外済）。

---

## Gemma 4 E4B（推奨・デフォルト）

Gemma 4 E4B は Google の最新モデルで、`mlx-vlm` ランタイムを使います。  
ライセンス: Apache 2.0（商用利用可）

```bash
# ダウンロード（~3GB、初回のみ）
huggingface-cli download mlx-community/gemma-4-e4b-it-4bit \
    --local-dir models/gemma-4-e4b-it-4bit
```

`config.yaml` の設定（デフォルト値なので変更不要）：

```yaml
minutes:
  local:
    runtime: mlx-vlm
    model_path: mlx-community/gemma-4-e4b-it-4bit  # HuggingFace ID で自動ダウンロードも可
```

ローカルパスを使う場合：

```bash
uv run main.py input/meeting.mp4 \
    --minutes-backend local \
    --minutes-local-runtime mlx-vlm \
    --minutes-model models/gemma-4-e4b-it-4bit
```

---

## mlx-lm モデル（テキスト専用モデル向け）

テキスト専用モデルには `mlx-lm` ランタイムを使います。

```bash
# 例: Qwen2.5-7B をダウンロード
huggingface-cli download mlx-community/Qwen2.5-7B-Instruct-4bit \
    --local-dir models/Qwen2.5-7B-Instruct-4bit
```

`config.yaml` の設定：

```yaml
minutes:
  local:
    runtime: mlx-lm
    model_path: models/Qwen2.5-7B-Instruct-4bit
```

---

## Ollama モデルの配置方法

Ollama を使う場合はモデルファイルをここに置く必要はありません。  
Ollama サーバー経由でモデルを管理します：

```bash
# Ollama サーバーを起動
ollama serve

# モデルをプル（初回のみ）
ollama pull gemma2:9b

# 実行
uv run main.py input/meeting.mp4 --minutes-backend local --minutes-local-runtime ollama
```

---

## 推奨モデル一覧

| 用途 | モデル | サイズ目安 | ランタイム | ライセンス |
|------|--------|-----------|-----------|-----------|
| 議事録（デフォルト推奨） | `mlx-community/gemma-4-e4b-it-4bit` | ~3GB | mlx-vlm | Apache 2.0 |
| 議事録（テキスト専用） | `mlx-community/Qwen2.5-7B-Instruct-4bit` | ~4GB | mlx-lm | Apache 2.0 |
| 議事録（Ollama） | `gemma2:9b` | ~5.5GB | ollama | Gemma ToU |

各モデルのライセンスは `docs/model_licenses.md` を参照してください。
