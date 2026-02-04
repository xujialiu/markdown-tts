"""Tests for TTS engine module."""
import pytest
from xml.etree import ElementTree


def test_tts_engine_class_exists():
    """Test that TTSEngine class can be imported."""
    from src.tts.engine import TTSEngine
    assert TTSEngine is not None


def test_tts_worker_class_exists():
    """Test that TTSWorker class can be imported."""
    from src.tts.engine import TTSWorker
    assert TTSWorker is not None


def test_is_configured_returns_false_without_credentials():
    """Test that is_configured returns False without valid credentials."""
    from src.tts.engine import TTSEngine

    engine = TTSEngine()
    assert engine.is_configured() is False


def test_is_configured_returns_false_with_empty_key():
    """Test that is_configured returns False with empty speech key."""
    from src.tts.engine import TTSEngine

    engine = TTSEngine(speech_key="", speech_region="eastus")
    assert engine.is_configured() is False


def test_engine_default_values():
    """Test that engine initializes with correct default values."""
    from src.tts.engine import TTSEngine

    engine = TTSEngine()
    assert engine.voice == "en-US-JennyNeural"
    assert engine.rate == 1.0
    assert engine.volume == 100
    assert engine.is_playing is False
    assert engine.is_paused is False


def test_set_voice():
    """Test setting voice."""
    from src.tts.engine import TTSEngine

    engine = TTSEngine()
    engine.set_voice("en-US-GuyNeural")
    assert engine.voice == "en-US-GuyNeural"


def test_set_rate():
    """Test setting speech rate."""
    from src.tts.engine import TTSEngine

    engine = TTSEngine()
    engine.set_rate(1.5)
    assert engine.rate == 1.5


def test_set_rate_clamps_minimum():
    """Test that rate is clamped to minimum 0.5."""
    from src.tts.engine import TTSEngine

    engine = TTSEngine()
    engine.set_rate(0.1)
    assert engine.rate == 0.5


def test_set_rate_clamps_maximum():
    """Test that rate is clamped to maximum 2.0."""
    from src.tts.engine import TTSEngine

    engine = TTSEngine()
    engine.set_rate(3.0)
    assert engine.rate == 2.0


def test_set_volume():
    """Test setting volume."""
    from src.tts.engine import TTSEngine

    engine = TTSEngine()
    engine.set_volume(75)
    assert engine.volume == 75


def test_set_volume_clamps_minimum():
    """Test that volume is clamped to minimum 0."""
    from src.tts.engine import TTSEngine

    engine = TTSEngine()
    engine.set_volume(-10)
    assert engine.volume == 0


def test_set_volume_clamps_maximum():
    """Test that volume is clamped to maximum 100."""
    from src.tts.engine import TTSEngine

    engine = TTSEngine()
    engine.set_volume(150)
    assert engine.volume == 100


def test_build_ssml_generates_valid_xml():
    """Test that _build_ssml generates valid SSML XML."""
    from src.tts.engine import TTSEngine

    engine = TTSEngine()
    ssml = engine._build_ssml("Hello, world!")

    # Parse the SSML as XML to verify it's valid
    root = ElementTree.fromstring(ssml)
    assert root.tag == "{http://www.w3.org/2001/10/synthesis}speak"


def test_build_ssml_contains_voice_element():
    """Test that SSML contains voice element with correct name."""
    from src.tts.engine import TTSEngine

    engine = TTSEngine()
    engine.set_voice("en-US-AriaNeural")
    ssml = engine._build_ssml("Test")

    assert 'name="en-US-AriaNeural"' in ssml


def test_build_ssml_contains_prosody_with_rate():
    """Test that SSML contains prosody element with rate."""
    from src.tts.engine import TTSEngine

    engine = TTSEngine()
    engine.set_rate(1.5)
    ssml = engine._build_ssml("Test")

    assert 'rate="150%"' in ssml


def test_build_ssml_contains_prosody_with_volume():
    """Test that SSML contains prosody element with volume."""
    from src.tts.engine import TTSEngine

    engine = TTSEngine()
    engine.set_volume(80)
    ssml = engine._build_ssml("Test")

    assert 'volume="80%"' in ssml


def test_build_ssml_escapes_special_characters():
    """Test that SSML properly escapes special XML characters."""
    from src.tts.engine import TTSEngine

    engine = TTSEngine()
    ssml = engine._build_ssml("Test <tag> & 'quote' \"doublequote\"")

    # Verify special characters are escaped
    assert "&lt;tag&gt;" in ssml
    assert "&amp;" in ssml


def test_build_ssml_contains_text():
    """Test that SSML contains the original text."""
    from src.tts.engine import TTSEngine

    engine = TTSEngine()
    ssml = engine._build_ssml("Hello, this is a test message.")

    assert "Hello, this is a test message." in ssml


def test_get_available_voices_returns_empty_without_config():
    """Test that get_available_voices returns empty list when not configured."""
    from src.tts.engine import TTSEngine

    engine = TTSEngine()
    voices = engine.get_available_voices()
    assert voices == []


def test_play_returns_false_without_config():
    """Test that play returns False when engine is not configured."""
    from src.tts.engine import TTSEngine

    engine = TTSEngine()
    result = engine.play("Hello")
    assert result is False


def test_engine_has_required_signals():
    """Test that engine has all required Qt signals."""
    from src.tts.engine import TTSEngine
    from PySide6.QtCore import Signal

    engine = TTSEngine()

    # Verify signals exist (they're class attributes)
    assert hasattr(TTSEngine, 'word_boundary')
    assert hasattr(TTSEngine, 'playback_started')
    assert hasattr(TTSEngine, 'playback_paused')
    assert hasattr(TTSEngine, 'playback_stopped')
    assert hasattr(TTSEngine, 'playback_finished')
    assert hasattr(TTSEngine, 'error_occurred')


def test_worker_has_required_signals():
    """Test that worker has all required Qt signals."""
    from src.tts.engine import TTSWorker

    # Verify signals exist (they're class attributes)
    assert hasattr(TTSWorker, 'word_boundary')
    assert hasattr(TTSWorker, 'playback_started')
    assert hasattr(TTSWorker, 'playback_finished')
    assert hasattr(TTSWorker, 'error_occurred')


def test_module_exports():
    """Test that module exports correct classes."""
    from src.tts import TTSEngine, TTSWorker

    assert TTSEngine is not None
    assert TTSWorker is not None
