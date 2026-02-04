"""TTS (Text-to-Speech) module using Azure Cognitive Services."""
from .engine import TTSEngine, TTSWorker
from .highlighter import TTSHighlighter

__all__ = ["TTSEngine", "TTSWorker", "TTSHighlighter"]
