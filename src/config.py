"""Configuration management using OmegaConf."""
from pathlib import Path
from omegaconf import OmegaConf, DictConfig

CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"

DEFAULTS = {
    "azure": {
        "speech_key": "",
        "speech_region": "eastus",
        "default_voice": "en-US-JennyNeural",
    },
    "playback": {
        "speed": 1.0,
        "volume": 100,
    },
    "highlight": {
        "sentence_color": "#fff3cd",
        "sentence_opacity": 1.0,
        "word_color": "#ffc107",
        "word_opacity": 1.0,
    },
    "ui": {
        "toolbar_visible": False,
        "sidebar_visible": True,
        "window_width": 1200,
        "window_height": 800,
        "sidebar_width": 250,
    },
    "recent": {
        "files": [],
        "last_folder": "",
    },
}


def load_config(config_path: Path = CONFIG_PATH) -> DictConfig:
    """Load configuration from file, merging with defaults."""
    defaults = OmegaConf.create(DEFAULTS)
    if config_path.exists():
        try:
            user_config = OmegaConf.load(config_path)
            return OmegaConf.merge(defaults, user_config)
        except Exception:
            return defaults
    return defaults


def save_config(cfg: DictConfig, config_path: Path = CONFIG_PATH) -> None:
    """Save configuration to file."""
    OmegaConf.save(cfg, config_path)
