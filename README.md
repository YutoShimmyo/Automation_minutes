# Meeting Minutes Automation

音声・動画ファイルから **文字起こし** と **議事録** を自動生成するツールです。  
日本語・英語どちらも対応しています。

---

## できること

| 機能 | 説明 |
|------|------|
| 🎙️ 音声認識 (STT) | Whisper / Parakeet による高精度文字起こし（日・英・自動検出） |
| 📝 議事録生成（API） | Gemini 2.5 Flash / Flash-Lite で高速・高品質な日本語議事録を生成 |
| 📝 議事録生成（ローカル） | Gemma 4 E4B (mlx-vlm) / Qwen2.5-7B / Ollama で完全オフライン動作 |
| ⚡ プリセット選択 | 高品質・標準・高速のプリセットをコマンド一つで切り替え |
| 🔧 設定ファイル | `config.yaml` で全設定を一元管理、CLI オプションで上書き可能 |
| 🌐 日本語出力デフォルト | 英語音声でも議事録は常に日本語で出力（`--minutes-language en` で変更可） |

---

## 最短実行手順

### 1. 前提インストール

```bash
# uv がなければインストール
curl -LsSf https://astral.sh/uv/install.sh | sh

# ffmpeg（音声変換に必要）
brew install ffmpeg       # macOS
# sudo apt install ffmpeg  # Ubuntu/Debian
```

### 2. 依存パッケージのインストール

```bash
git clone <このリポジトリのURL>
cd Automation_minutes
uv sync
```

### 3. 音声ファイルを変換するだけ

```bash
# 文字起こしのみ（最速）
uv run main.py input/your_meeting.mp4
```

出力: `output/transcripts/your_meeting.txt`

---

## CLIの使い方

```bash
uv run main.py <音声ファイル> [オプション]
```

### 基本例

```bash
# 文字起こしのみ
uv run main.py input/meeting.mp4

# 英語音声 + Gemini 議事録（日本語で出力、デフォルト）
uv run main.py input/meeting.mp4 --language en --minutes-backend api

# 高品質モデル指定
uv run main.py input/meeting.mp4 --language en --profile quality --minutes-backend api --minutes-model gemini-2.5-flash

# 軽量・高速モデル
uv run main.py input/meeting.mp4 --minutes-backend api --minutes-model gemini-2.5-flash-lite

# ローカル議事録（Gemma 4 E4B、デフォルト）
uv run main.py input/meeting.mp4 --minutes-backend local

# Ollama で議事録生成
uv run main.py input/meeting.mp4 --minutes-backend local --minutes-local-runtime ollama

# 特定モデルを指定
uv run main.py input/meeting.mp4 --asr-model large-v3

# カスタム設定ファイルを使う
uv run main.py input/meeting.mp4 --config my_config.yaml
```

### CLIオプション一覧

| オプション | 選択肢 | 説明 |
|-----------|--------|------|
| `--language` | `ja` / `en` / `auto` | 音声言語（デフォルト: auto） |
| `--profile` | `fast` / `standard` / `quality` | 品質プロファイル（デフォルト: standard） |
| `--asr-preset` | `A` / `B` / `C` / `D` | ASR プリセット（下記参照） |
| `--asr-backend` | `faster_whisper` / `parakeet` | ASR バックエンドを強制指定 |
| `--asr-model` | モデル名 | ASR モデルを強制指定（例: `large-v3`） |
| `--minutes-backend` | `none` / `api` / `local` | 議事録生成バックエンド（デフォルト: none） |
| `--minutes-language` | `ja` / `en` / `auto` | 議事録の出力言語（デフォルト: ja） |
| `--minutes-local-runtime` | `mlx-vlm` / `mlx-lm` / `ollama` | ローカル LLM ランタイム |
| `--minutes-model` | モデルパス/名前 | 議事録生成モデルを指定 |
| `--config` | ファイルパス | config.yaml のパスを指定 |

---

## ASR プリセットの選び方

| プリセット | 言語 | 品質 | モデル | 備考 |
|-----------|------|------|--------|------|
| **A** | 英語 | 高品質 | Parakeet TDT → Whisper large-v3 | Parakeet は英語専用 |
| **B** | 英語 | 標準 | Whisper large-v3-turbo | 速度と品質のバランス |
| **C** | 多言語 | 高品質 | Whisper large-v3 | 日本語にも最適 |
| **D** | 多言語 | 標準 | Whisper large-v3-turbo | デフォルト（推奨） |

### プロファイルとプリセットの自動対応

| `--profile` | `--language` | 選択されるプリセット |
|------------|-------------|------------------|
| quality | en | A |
| standard | en | B |
| quality | ja | C |
| standard | ja | D |
| * | auto | C (quality) / D (standard/fast) |

---

## config.yaml の使い方

```bash
cp config.yaml my_config.yaml
# my_config.yaml を編集
uv run main.py input/meeting.mp4 --config my_config.yaml
```

主要な設定項目:

```yaml
profile: standard         # fast / standard / quality
language: auto            # auto / ja / en（音声の言語）

asr:
  preset: auto            # auto / A / B / C / D
  backend: ""             # 空=自動 / faster_whisper / parakeet
  model: ""               # 空=自動 / large-v3 / medium / small など

minutes:
  backend: none           # none / api / local
  output_language: ja     # ja / en / auto（議事録の出力言語）

  api:
    provider: gemini
    # 利用可能: gemini-2.5-flash / gemini-2.5-flash-lite / gemini-2.0-flash
    model: gemini-2.5-flash

  local:
    runtime: mlx-vlm      # mlx-vlm / mlx-lm / ollama
    model_path: "mlx-community/gemma-4-e4b-it-4bit"
    ollama_model: "gemma2:9b"
    ollama_url: "http://localhost:11434"
```

---

## APIキーの設定方法

Gemini API を使う場合:

```bash
# テンプレートをコピー
cp .env.template .env

# .env を編集して APIキーを設定
# GEMINI_API_KEY=your_key_here
```

APIキーの取得: https://aistudio.google.com/app/apikey

---

## ローカルモデルの配置方法

### 議事録生成モデル（推奨: Gemma 4 E4B）

Gemma 4 E4B は `mlx-vlm` を使うマルチモーダルモデルです（テキスト専用として使用可能）：

```bash
# gemma-4-e4b-it-4bit をダウンロード（~3GB、初回のみ）
huggingface-cli download mlx-community/gemma-4-e4b-it-4bit \
    --local-dir models/gemma-4-e4b-it-4bit

# 実行（HuggingFace IDでも自動ダウンロード可）
uv run main.py input/meeting.mp4 \
    --minutes-backend local \
    --minutes-local-runtime mlx-vlm \
    --minutes-model mlx-community/gemma-4-e4b-it-4bit
```

### テキスト専用モデル（代替）

```bash
# Qwen2.5-7B（mlx-lm 用）
huggingface-cli download mlx-community/Qwen2.5-7B-Instruct-4bit \
    --local-dir models/Qwen2.5-7B-Instruct-4bit

uv run main.py input/meeting.mp4 \
    --minutes-backend local \
    --minutes-local-runtime mlx-lm \
    --minutes-model models/Qwen2.5-7B-Instruct-4bit
```

詳細は `models/README.md` を参照してください。

---

## 出力ファイル

| ファイル | 説明 |
|---------|------|
| `output/transcripts/<ファイル名>.txt` | 文字起こしテキスト |
| `output/minutes/<ファイル名>_minutes.md` | 構造化議事録（Markdown） |

---

## 対応フォーマット

音声/動画: `.m4a`, `.mp3`, `.mp4`, `.wav`, `.flac`, `.ogg`, `.webm` など ffmpeg が対応する形式すべて。

---

## よくあるエラー

### `Error: File not found`
→ ファイルパスを確認してください。`input/` ディレクトリに配置されているか確認。

### `GEMINI_API_KEY is not set`
→ `.env` ファイルに API キーが設定されているか確認してください。

### `Cannot connect to Ollama`
→ Ollama が起動しているか確認: `ollama serve`  
→ モデルがプルされているか確認: `ollama pull gemma2:9b`

### `nemo_toolkit not installed`（Parakeet 使用時）
→ NeMo が必要です: `pip install nemo_toolkit['asr']`  
→ または `--asr-backend faster_whisper` で代替バックエンドを使用してください。

### `mlx-lm requires Apple Silicon`
→ mlx-lm は Apple Silicon (M1/M2/M3/M4) 専用です。  
→ 他の環境では `--minutes-backend api` か `--minutes-local-runtime ollama` を使用してください。

### メモリ不足
→ より小さいモデルを使用してください: `--asr-model medium` または `--asr-model small`

### 議事録が途中で切れる / 警告が出る
→ 文字起こしが長すぎてモデルのコンテキスト上限に達しています。  
→ 各モデルで対応できるミーティング時間の目安（日本語）：

| バックエンド | 対応時間（日本語） | 対応時間（英語） |
|------------|--------------|--------------|
| Gemma 4 E4B (mlx-vlm) | 約 7 時間 | 約 13 時間 |
| Qwen2.5-7B (mlx-lm) | 約 7 時間 | 約 13 時間 |
| Gemini API | 実質無制限 | 実質無制限 |
| Ollama gemma2:9b（デフォルト） | **約 20 分 ⚠️** | 約 40 分 |

→ Ollama を長い会議に使う場合は `Modelfile` で `PARAMETER num_ctx 32768` に設定（→ 日本語 約1時間40分に延長）。  
→ 詳しくは `REPORT.md` の「コンテキスト長と対応可能なミーティング時間」を参照。

---

## ライセンスについて

このツール自体は MIT ライセンスです。  
**ただし、使用するモデルは各モデルのライセンスに従います。**  
商用利用の前に必ず `docs/model_licenses.md` を確認し、各モデルの公式ライセンスをご確認ください。

---

## ディレクトリ構成

```
Automation_minutes/
├── main.py               # メインエントリポイント
├── config.yaml           # デフォルト設定
├── .env.template         # 環境変数テンプレート
├── pyproject.toml        # 依存関係（uv管理）
├── src/
│   ├── config.py         # 設定ファイル読み込み
│   ├── preprocess.py     # テキスト前処理
│   ├── asr/              # 音声認識バックエンド
│   │   ├── base.py
│   │   ├── faster_whisper_backend.py
│   │   ├── parakeet_backend.py
│   │   └── factory.py
│   └── summarizer/       # 議事録生成バックエンド
│       ├── base.py
│       ├── gemini.py
│       ├── mlx_vlm_backend.py  # Gemma 4 E4B など (mlx-vlm)
│       ├── mlx_backend.py      # Qwen2.5 など (mlx-lm)
│       ├── ollama_backend.py
│       └── factory.py
├── models/               # ローカルモデル配置場所（Git除外）
│   └── README.md
├── docs/
│   └── model_licenses.md # モデルライセンス情報
├── input/                # 入力ファイル（Git除外）
├── output/               # 出力ファイル（Git除外）
└── scripts/
    └── run_slurm.sh      # Slurm クラスタ用
```
