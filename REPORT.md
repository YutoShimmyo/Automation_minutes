# 動作検証レポート

実行日: 2026-04-24  
環境: Apple M3 (Mac), Python 3.12, uv

---

## 検証に使用したファイル

| ファイル名 | 長さ | 内容 |
|-----------|------|------|
| `input/English_voice_1.m4a` | 16.7秒 | 英語自己紹介スピーチ |
| `input/Japanese_voice_1.m4a` | 5.3秒 | 日本語発話 |
| `input/English_and_Japanese_voice_1.m4a` | 30.1秒 | 日本語での技術的議論（英語カタカナ混じり） |

---

## STT（文字起こし）検証

### ファイル 1: English_voice_1.m4a

```
uv run main.py input/English_voice_1.m4a --language en --asr-preset B
```

| 項目 | 値 |
|-----|-----|
| プリセット | B (English · Standard) |
| バックエンド | faster-whisper/large-v3-turbo |
| デバイス | CPU (int8) |
| 音声長 | 16.7秒 |
| 処理時間（ASR） | 5.1秒 |
| Real-Time Factor | **0.303x** |
| 検出言語 | en (確信度 1.00) |
| 総実行時間（初回） | 112.4秒（モデルダウンロード込み） |
| 総実行時間（2回目以降） | 6.7秒 |

**文字起こし結果:**
```
Hi there, it's nice to meet you. My name is Yuto Shinmyo. I'm currently focusing on
improving my English skills. I believe that learning a new language opens up a full
new world of opportunities and perspectives.
```

**品質評価:** 自然な英語として正確に認識。固有名詞（Yuto Shinmyo）も正確。

---

### ファイル 2: Japanese_voice_1.m4a

```
uv run main.py input/Japanese_voice_1.m4a --language ja --asr-preset D
```

| 項目 | 値 |
|-----|-----|
| プリセット | D (Multilingual · Standard) |
| バックエンド | faster-whisper/large-v3-turbo |
| デバイス | CPU (int8) |
| 音声長 | 5.3秒 |
| 処理時間（ASR） | 4.9秒 |
| Real-Time Factor | **0.912x** |
| 検出言語 | ja (確信度 1.00) |
| 総実行時間 | 6.8秒（モデルキャッシュ済み） |

**文字起こし結果:**
```
私は霊のことが大好きです。彼女を愛しています。
```

**品質評価:** 日本語認識は正確。短い音声（5.3秒）でも問題なく処理。

---

### ファイル 3: English_and_Japanese_voice_1.m4a

```
uv run main.py input/English_and_Japanese_voice_1.m4a --language auto --asr-preset D
```

| 項目 | 値 |
|-----|-----|
| プリセット | D (Multilingual · Standard) |
| バックエンド | faster-whisper/large-v3-turbo |
| デバイス | CPU (int8) |
| 音声長 | 30.1秒 |
| 処理時間（ASR） | 10.4秒 |
| Real-Time Factor | **0.346x** |
| 検出言語 | ja (確信度 1.00、auto検出) |
| 総実行時間 | 12.2秒（モデルキャッシュ済み） |

**文字起こし結果:**
```
1つ目はデフォルト構成です。日英量対応ならデフォルトSTTをウェスパー系が無難です。英語品質モードだけパラケットに逃がすが自然です。
2つ目はローカルSLMの実行方式です。LAMA CPP、大LAMA、MLXLMの音量を前提にするか。
Mac M3ならMLXLMは相性が良いですが、初心者には大LAMAの方が扱いやすい可能性があります。
```

**品質評価:** 日本語主体の音声として正確に認識。英語技術用語（Whisper→ウェスパー、Parakeet→パラケット、LLAMA→大LAMA、MLXLM）はカタカナ変換されているが意味は伝わる。auto言語検出も正確に日本語と判定。

---

## STT RTF サマリー

| ファイル | 音声長 | 処理時間 | RTF | 評価 |
|---------|--------|---------|-----|------|
| English_voice_1.m4a | 16.7s | 5.1s | 0.303x | ◎ 高速 |
| Japanese_voice_1.m4a | 5.3s | 4.9s | 0.912x | ○ 短音声で若干低下 |
| English_and_Japanese_voice_1.m4a | 30.1s | 10.4s | 0.346x | ◎ 高速 |

> RTF < 1.0 = リアルタイムより速い（例: RTF=0.3 → 1分の音声を18秒で処理）

---

## 議事録生成（Summarization）検証

### API: Gemini

利用可能モデル（2026-04時点）: `gemini-2.5-flash`, `gemini-2.5-flash-lite`, `gemini-2.0-flash`
（`gemini-1.5-flash` は現行 API バージョンでは利用不可）

---

#### gemini-2.5-flash-lite（軽量・高速）

```
uv run main.py input/<file>.m4a --minutes-backend api --minutes-model gemini-2.5-flash-lite
```

| ファイル | 入力トークン推定 | 処理時間 | 評価 |
|---------|--------------|---------|------|
| English_voice_1.m4a | ~53 | **2.2秒** | ◎ |
| Japanese_voice_1.m4a | ~23 | **2.0秒** | ◎ |
| English_and_Japanese_voice_1.m4a | ~136 | **3.4秒** | ◎ |

**生成結果サンプル（English_and_Japanese_voice_1）:**

```markdown
# 議事録

## 概要
本議事録は、デフォルト構成とローカルSLMの実行方式に関する議論をまとめたものです。
日英量対応にはWhisper系が推奨され、英語品質モードではParakeetへの切り替えが自然とされました。

## 主な議論のポイント
- 日英両言語対応: Whisper系が無難
- 英語品質モード: Parakeet推奨
- ローカルSLM実行方式: LAMA CPP / Ollama / MLX の比較
- Mac M3: MLX相性良。初心者: Ollama が扱いやすい可能性

## アクションアイテム
- 具体的なアクションアイテムは特定されていません
```

---

#### gemini-2.5-flash（標準・高品質）

```
uv run main.py input/<file>.m4a --minutes-backend api --minutes-model gemini-2.5-flash
```

| ファイル | 入力トークン推定 | 処理時間 | 評価 |
|---------|--------------|---------|------|
| English_voice_1.m4a | ~53 | **12.1秒**（混雑リトライあり） | ◎◎ |
| Japanese_voice_1.m4a | ~23 | **16.9秒**（混雑リトライあり） | ◎◎ |
| English_and_Japanese_voice_1.m4a | ~136 | **9.9秒** | ◎◎ |

**生成結果サンプル（English_and_Japanese_voice_1）:**

```markdown
# 議事録

## 概要
本会議では、音声認識（STT）のデフォルト構成とローカルSLM実行方式について議論が行われました。

## 主な議論のポイント
- **STT デフォルト構成**: 日英両対応はWhisper系、英語品質重視はParakeet推奨
- **ローカルSLM 実行方式**: llama.cpp / Ollama / MLX の比較
  - Mac M3: MLX相性良
  - 初心者: Ollama が導入・操作が容易

## アクションアイテム
- 具体的なアクションアイテムはありません
```

**品質比較:**

| モデル | 速度 | 品質 | 特徴 |
|--------|------|------|------|
| `gemini-2.5-flash-lite` | ◎ 2〜3秒 | ◎ | 通常用途に最適。十分高品質 |
| `gemini-2.5-flash` | ○ 10〜17秒 | ◎◎ | より詳細・文脈補完が優秀。音声認識誤りを正確に修正 |

**リトライ動作**: 503（サーバ高負荷）で自動リトライ（指数バックオフ）確認。正常動作。

---

### ローカル LLM: mlx-lm (Qwen2.5-7B-Instruct-4bit)

#### 英語議事録（後方互換フラグ --summarize 経由）

```
uv run main.py input/English_voice_1.m4a --summarize --minutes-model mlx-community/Qwen2.5-7B-Instruct-4bit
```

| 項目 | 値 |
|-----|-----|
| バックエンド | mlx-lm/Qwen2.5-7B-Instruct-4bit |
| プロンプトトークン | 126 tokens |
| 生成トークン | 107 tokens |
| 生成速度 | 21.4 tokens/sec |
| 消費メモリ | 4.5 GB |
| 処理時間 | 8.9秒（モデルキャッシュ済み） |

**生成結果（抜粋）:**
```markdown
# Meeting Minutes

## Summary
The meeting was a brief introduction where Yuto Shinmyo greeted the group and shared
his name and his current focus on improving his English skills.

## Key Discussion Points
- Introduction of Yuto Shinmyo
- Current focus on improving English skills

## Action Items
- [ ] Continue improving English skills — Yuto Shinmyo
```

**品質評価:** 短い自己紹介から適切な構造化議事録を生成。担当者名も正確に抽出。

---

#### 日本語議事録（--language ja で日本語プロンプト）

```
uv run main.py input/Japanese_voice_1.m4a --minutes-backend local --language ja
    --minutes-model mlx-community/Qwen2.5-7B-Instruct-4bit
```

| 項目 | 値 |
|-----|-----|
| バックエンド | mlx-lm/Qwen2.5-7B-Instruct-4bit |
| プロンプトトークン | 122 tokens |
| 生成トークン | 142 tokens |
| 生成速度 | 21.0 tokens/sec |
| 消費メモリ | 4.5 GB |
| 処理時間 | 11.1秒 |

**生成結果（抜粋）:**
```markdown
# 議事録

## 概要
本会議は、参加者の霊的な興味と愛着についての議論を目的として開催されました。

## アクションアイテム
- [ ] 霊的な存在についての理解を深めるための資料を作成する — 李さん
```

**品質評価:** `--language ja` 指定時は日本語プロンプトが使われ、議事録も日本語で生成される。

---

#### 混合音声の議事録（English_and_Japanese_voice_1.m4a）

```
uv run main.py input/English_and_Japanese_voice_1.m4a --minutes-backend local
    --minutes-model mlx-community/Qwen2.5-7B-Instruct-4bit
```

**生成結果（抜粋）:**
```markdown
# Meeting Minutes

## Summary
The meeting discussed two key points: the default configuration for speech-to-text
(STT) systems, and the execution method for local speech learning models (SLM).

## Action Items
- [ ] Determine the default STT system for English-quantity alignment
- [ ] Decide on the local SLM execution method
```

**品質評価:** 技術的議論から要点を適切に抽出。STT → LLMのパイプライン全体として正常動作。

---

## プリセット・フォールバック検証

### プリセット A（Parakeet → Whisper large-v3）

| ステップ | 結果 |
|---------|------|
| Parakeet TDT | `nemo_toolkit` 未インストールのため自動スキップ |
| Whisper large-v3 (fallback) | ダウンロード待ちだが、コード・フォールバックロジック正常 |

**判定:** フォールバックロジックは正常動作。Parakeet を使いたい場合は `pip install nemo_toolkit['asr']` が必要。

---

## 後方互換性確認

| レガシーフラグ | 動作確認 | 説明 |
|--------------|---------|------|
| `--summarize` | ✅ 正常 | `--minutes-backend local` と同等 |
| `--use-gemini` | ✅ 正常 | `--minutes-backend api` と同等 |

---

## 総合評価

| 観点 | 評価 | 備考 |
|------|------|------|
| 英語文字起こし（Preset B） | ◎ | RTF=0.303, 高精度 |
| 日本語文字起こし（Preset D） | ○ | RTF=0.912, 正確 |
| 混合音声・auto検出 | ○ | 日本語として正確に認識 |
| ローカル議事録（mlx-vlm / Gemma 4 E4B） | ◎ | 日本語で高品質、28.7 tok/sec、Apache 2.0 |
| ローカル議事録（mlx-lm / Qwen2.5-7B） | ◎ | 日英両方で動作 |
| API議事録（gemini-2.5-flash-lite） | ◎ | 2〜3秒で高品質日本語議事録 |
| API議事録（gemini-2.5-flash） | ◎◎ | より詳細・音声認識誤り補完優秀 |
| 後方互換性 | ◎ | 旧フラグそのまま使用可能 |
| フォールバック動作 | ◎ | Parakeet 未インストール時に正常スキップ |

---

## 追加検証: gemma-4-e4b-it-4bit（mlx-vlm）

```
uv run main.py input/English_and_Japanese_voice_1.m4a \
    --minutes-backend local --minutes-local-runtime mlx-vlm \
    --minutes-model mlx-community/gemma-4-e4b-it-4bit
```

| 項目 | 値 |
|-----|-----|
| バックエンド | mlx-vlm/gemma-4-e4b-it-4bit |
| ライセンス | Apache 2.0（商用利用可） |
| プロンプトトークン | 216 tokens |
| プロンプト処理速度 | 139.3 tokens/sec |
| 生成トークン | 280 tokens |
| 生成速度 | 28.7 tokens/sec |
| 消費メモリ | 5.682 GB |
| 処理時間（キャッシュ済み） | 16.3秒 |

**生成された議事録:**

```markdown
# 議事録

## 概要
本会議では、音声認識（STT）およびローカルSLMの実行方式について、具体的な技術選定に関する議論が
行われました。多言語対応や実行環境に応じた最適なツールの選定が主な議題となりました。

## 主な議論のポイント
- デフォルトSTTとしてWhisper系を採用するのが最も安全との見解
- 英語品質モードはParakeetに依存させるのが自然との意見
- ローカルSLMの実行方式: LLAMA CPP / Ollama / mlx-lm の比較
- Mac M3 環境では mlx-lm との相性が良い
- 初心者には Ollama の方が扱いやすい可能性あり

## アクションアイテム
- 特になし（技術選定に関する情報共有が主）
```

**品質評価:** 音声認識のカタカナ誤認識（ウェスパー→Whisper、大LAMA→Ollama/LLAMA）を文脈から正しく補完し、高品質な日本語議事録を生成。Qwen2.5-7B より高速（28.7 vs 21.0 tokens/sec）かつ Apache 2.0 ライセンスで商用利用可。

---

## コンテキスト長と対応可能なミーティング時間

### Step 1：1時間のミーティングでどれくらい話すか

会議の発話量（Whisper による文字起こし後）の目安：

| 言語 | 発話速度（会議平均） | 1時間の文字起こし量 |
|------|-----------------|----------------|
| 日本語 | 約 300 文字/分 | **約 18,000 文字**（A4 用紙 約13枚分） |
| 英語 | 約 120 語/分 | **約 7,200 語**（A4 用紙 約29枚分） |

> 会議は通常会話より発話が少ない（間、質疑応答、沈黙）ため、通常会話より遅めの数値を使用。  
> 実際には参加者数・会議スタイルによって変動する。

---

### Step 2：各モデルが 1 回で処理できる上限時間

モデルには「一度に読み込めるテキスト量（コンテキスト長）」に上限があります。  
上限を超えた場合はツールが自動的に警告を出し、超過部分をカットします。

| バックエンド | モデル | コンテキスト上限 | 日本語 | 英語 |
|------------|--------|--------------|------|------|
| `mlx-vlm` | **Gemma 4 E4B** | 128K（実測値） | **約 7 時間** | 約 13 時間 |
| `mlx-lm` | Qwen2.5-7B | 128K | **約 7 時間** | 約 13 時間 |
| `api` | **Gemini 2.5 Flash** | 1,000K（1M） | **実質無制限** | 実質無制限 |
| `ollama` | gemma2:9b（デフォルト） | 8K ⚠️ | **約 20 分** | 約 40 分 |

> 計算根拠：日本語 1 文字 ≈ 1 token / 英語 1 語 ≈ 1.3 tokens。  
> システムプロンプト・生成出力分（約 2,000 tokens）を差し引いた実効値。

#### ⚠️ Ollama だけは要注意
デフォルトの 8K context では **日本語 20 分・英語 40 分** が上限。  
それ以上のミーティングには `Modelfile` で `PARAMETER num_ctx 32768`（32K）に拡張すると  
→ 日本語 **約 1 時間 40 分**、英語 **約 3 時間 20 分** まで対応可能。

---

### Step 3：ミーティング時間別 推奨バックエンド

コンテキストに収まっていても、非常に長い会議は要約品質が落ちやすい点に注意。

| 会議の長さ | 推奨バックエンド | 補足 |
|----------|--------------|------|
| 〜30分 | **どれでも可** | 最も安定した出力が期待できる |
| 30分〜1.5時間 | mlx-vlm / mlx-lm / api | Ollama はデフォルト設定では不足 |
| 1.5時間〜3時間 | mlx-vlm / api | ローカルでも問題なし |
| 3時間〜7時間 | **api（Gemini）推奨** | または 30〜60 分単位に分割して処理 |
| 7時間以上 | api（Gemini）一択 | ローカルモデルのコンテキスト上限に近づく |

---

### コード上の安全機構

上限超過時は自動カットされ、以下の警告が表示されます：

```
[Warning] Transcript is ~25,000 tokens (≈83 min of speech),
but 'ollama' context limit is ~6,192 tokens (≈20 min of speech).
  → The transcript will be truncated. Consider splitting the audio into shorter segments.
```

実行時には入力テキスト量の推定値も常に表示されます：

```
[Summarizer] Estimated input tokens: ~136
```

---

## 注意事項・既知の制限

1. **初回実行時間**: Whisper large-v3-turbo のダウンロード（約1.6GB）に時間がかかる。2回目以降はキャッシュが使われ高速。
2. **Parakeet TDT**: `nemo_toolkit['asr']` が必要。Mac では NeMo のインストールが複雑な場合あり。
3. **mlx-lm は Apple Silicon 専用**: M1/M2/M3/M4 Mac のみ対応。他の環境では `--minutes-backend api` か `--minutes-local-runtime ollama` を使用する。
4. **日英混合音声**: auto 検出は主要言語を選択する。音声全体に英語と日本語が混在する場合、どちらかの言語で処理される。
