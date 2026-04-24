"""Configuration management: loads config.yaml and merges CLI overrides."""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml


DEFAULT_CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"


@dataclass
class ASRConfig:
    preset: str = "auto"
    backend: str = ""
    model: str = ""
    device: str = ""


@dataclass
class MinutesAPIConfig:
    provider: str = "gemini"
    model: str = "gemini-2.5-flash"


@dataclass
class MinutesLocalConfig:
    runtime: str = "mlx-lm"
    model_path: str = "mlx-community/gemma-3-4b-it-4bit"
    ollama_model: str = "gemma2:9b"
    ollama_url: str = "http://localhost:11434"


@dataclass
class MinutesConfig:
    backend: str = "none"
    # Output language for the generated minutes (independent of audio language).
    # "ja" = always Japanese, "en" = always English, "auto" = follow audio language.
    output_language: str = "ja"
    api: MinutesAPIConfig = field(default_factory=MinutesAPIConfig)
    local: MinutesLocalConfig = field(default_factory=MinutesLocalConfig)


@dataclass
class AppConfig:
    profile: str = "standard"
    language: str = "auto"
    asr: ASRConfig = field(default_factory=ASRConfig)
    minutes: MinutesConfig = field(default_factory=MinutesConfig)


def load_config(config_path: Optional[str] = None) -> AppConfig:
    """Load configuration from a YAML file, falling back to defaults."""
    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH

    if not path.exists():
        if config_path:
            raise FileNotFoundError(f"Config file not found: {config_path}")
        return AppConfig()

    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    cfg = AppConfig()
    cfg.profile = raw.get("profile", cfg.profile)
    cfg.language = raw.get("language", cfg.language)

    asr_raw = raw.get("asr", {})
    cfg.asr.preset = asr_raw.get("preset", cfg.asr.preset)
    cfg.asr.backend = asr_raw.get("backend", cfg.asr.backend) or ""
    cfg.asr.model = asr_raw.get("model", cfg.asr.model) or ""
    cfg.asr.device = asr_raw.get("device", cfg.asr.device) or ""

    min_raw = raw.get("minutes", {})
    cfg.minutes.backend = min_raw.get("backend", cfg.minutes.backend)
    cfg.minutes.output_language = min_raw.get("output_language", cfg.minutes.output_language)

    api_raw = min_raw.get("api", {})
    cfg.minutes.api.provider = api_raw.get("provider", cfg.minutes.api.provider)
    cfg.minutes.api.model = api_raw.get("model", cfg.minutes.api.model)

    local_raw = min_raw.get("local", {})
    cfg.minutes.local.runtime = local_raw.get("runtime", cfg.minutes.local.runtime)
    cfg.minutes.local.model_path = local_raw.get("model_path", cfg.minutes.local.model_path) or ""
    cfg.minutes.local.ollama_model = local_raw.get("ollama_model", cfg.minutes.local.ollama_model)
    cfg.minutes.local.ollama_url = local_raw.get("ollama_url", cfg.minutes.local.ollama_url)

    return cfg


def apply_cli_overrides(cfg: AppConfig, args: argparse.Namespace) -> AppConfig:
    """Apply CLI argument overrides on top of the loaded config."""
    if getattr(args, "language", None):
        cfg.language = args.language
    if getattr(args, "profile", None):
        cfg.profile = args.profile
    if getattr(args, "asr_preset", None):
        cfg.asr.preset = args.asr_preset
    if getattr(args, "asr_backend", None):
        cfg.asr.backend = args.asr_backend
    if getattr(args, "asr_model", None):
        cfg.asr.model = args.asr_model
    if getattr(args, "minutes_backend", None):
        cfg.minutes.backend = args.minutes_backend
    if getattr(args, "minutes_language", None):
        cfg.minutes.output_language = args.minutes_language
    if getattr(args, "minutes_local_runtime", None):
        cfg.minutes.local.runtime = args.minutes_local_runtime
    if getattr(args, "minutes_model", None):
        if cfg.minutes.backend == "api":
            cfg.minutes.api.model = args.minutes_model
        elif cfg.minutes.local.runtime == "ollama":
            cfg.minutes.local.ollama_model = args.minutes_model
        else:
            cfg.minutes.local.model_path = args.minutes_model
    return cfg
