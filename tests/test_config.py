"""Tests for configuration module."""
import pytest
from pathlib import Path
from omegaconf import OmegaConf


def test_load_config_returns_omegaconf():
    from src.config import load_config
    cfg = load_config()
    assert isinstance(cfg, OmegaConf.__class__.__bases__[0])


def test_config_has_azure_section():
    from src.config import load_config
    cfg = load_config()
    assert "azure" in cfg
    assert "speech_key" in cfg.azure
    assert "speech_region" in cfg.azure
    assert "default_voice" in cfg.azure


def test_config_has_playback_section():
    from src.config import load_config
    cfg = load_config()
    assert "playback" in cfg
    assert "speed" in cfg.playback
    assert "volume" in cfg.playback


def test_config_has_highlight_section():
    from src.config import load_config
    cfg = load_config()
    assert "highlight" in cfg
    assert "sentence_color" in cfg.highlight
    assert "word_color" in cfg.highlight


def test_config_has_ui_section():
    from src.config import load_config
    cfg = load_config()
    assert "ui" in cfg
    assert "toolbar_visible" in cfg.ui
    assert "sidebar_visible" in cfg.ui


def test_config_has_recent_section():
    from src.config import load_config
    cfg = load_config()
    assert "recent" in cfg
    assert "files" in cfg.recent
