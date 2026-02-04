# Typora TTS App - Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Markdown editor with Azure TTS integration for reading documents aloud with real-time highlighting.

**Architecture:** PySide6 GUI with QStackedWidget for edit/render modes, QWebEngineView for rendered markdown display, Azure Speech SDK for TTS with word boundary events driving JavaScript-based highlighting.

**Tech Stack:** PySide6, PySide6-WebEngine, OmegaConf, azure-cognitiveservices-speech, markdown, Pygments

---

## Task 1: Project Setup

**Files:**
- Create: `requirements.txt`
- Create: `main.py`
- Create: `src/__init__.py`

**Step 1: Create requirements.txt**

```txt
PySide6>=6.5.0
PySide6-WebEngine>=6.5.0
omegaconf>=2.3.0
azure-cognitiveservices-speech>=1.30.0
markdown>=3.5.0
Pygments>=2.17.0
```

**Step 2: Create minimal main.py**

```python
"""Typora TTS App - Markdown editor with text-to-speech."""
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel


def main():
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Typora TTS")
    window.setCentralWidget(QLabel("Hello, Typora TTS!"))
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

**Step 3: Create src/__init__.py**

```python
"""Typora TTS App source package."""
```

**Step 4: Install dependencies and verify**

Run:
```bash
conda activate ves_anno
pip install -r requirements.txt
python main.py
```
Expected: Window appears with "Hello, Typora TTS!" label

**Step 5: Commit**

```bash
git add requirements.txt main.py src/__init__.py
git commit -m "feat: initial project setup with PySide6"
```

---

## Task 2: Configuration Module

**Files:**
- Create: `src/config.py`
- Create: `config.yaml`
- Create: `tests/__init__.py`
- Create: `tests/test_config.py`

**Step 1: Create tests/__init__.py**

```python
"""Test package."""
```

**Step 2: Write failing test for config loading**

Create `tests/test_config.py`:
```python
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
```

**Step 3: Run test to verify it fails**

Run: `pytest tests/test_config.py -v`
Expected: FAIL with "ModuleNotFoundError" or "cannot import name 'load_config'"

**Step 4: Implement config module**

Create `src/config.py`:
```python
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
```

**Step 5: Create default config.yaml**

```yaml
# Typora TTS Configuration
azure:
  speech_key: "your-key-here"
  speech_region: "eastus"
  default_voice: "en-US-JennyNeural"

playback:
  speed: 1.0
  volume: 100

highlight:
  sentence_color: "#fff3cd"
  sentence_opacity: 1.0
  word_color: "#ffc107"
  word_opacity: 1.0

ui:
  toolbar_visible: false
  sidebar_visible: true
  window_width: 1200
  window_height: 800
  sidebar_width: 250

recent:
  files: []
  last_folder: ""
```

**Step 6: Run tests to verify they pass**

Run: `pytest tests/test_config.py -v`
Expected: All tests PASS

**Step 7: Commit**

```bash
git add src/config.py config.yaml tests/
git commit -m "feat: add configuration module with OmegaConf"
```

---

## Task 3: Main Window Shell

**Files:**
- Create: `src/ui/__init__.py`
- Create: `src/ui/main_window.py`
- Modify: `main.py`

**Step 1: Create src/ui/__init__.py**

```python
"""UI components package."""
from src.ui.main_window import MainWindow

__all__ = ["MainWindow"]
```

**Step 2: Create main window with menu bar skeleton**

Create `src/ui/main_window.py`:
```python
"""Main application window."""
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QMenuBar,
    QStatusBar,
)
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtCore import Qt

from src.config import load_config, save_config


class MainWindow(QMainWindow):
    """Main application window with menu bar and status bar."""

    def __init__(self):
        super().__init__()
        self.config = load_config()
        self._setup_window()
        self._setup_menu_bar()
        self._setup_status_bar()
        self._setup_central_widget()

    def _setup_window(self):
        """Configure window properties."""
        self.setWindowTitle("Typora TTS")
        self.resize(
            self.config.ui.window_width,
            self.config.ui.window_height,
        )

    def _setup_menu_bar(self):
        """Create menu bar with all menus."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        open_file_action = QAction("&Open File...", self)
        open_file_action.setShortcut(QKeySequence.Open)
        file_menu.addAction(open_file_action)

        open_folder_action = QAction("Open &Folder...", self)
        file_menu.addAction(open_folder_action)

        self.recent_menu = file_menu.addMenu("&Recent Files")

        file_menu.addSeparator()

        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence.Save)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")

        undo_action = QAction("&Undo", self)
        undo_action.setShortcut(QKeySequence.Undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction("&Redo", self)
        redo_action.setShortcut(QKeySequence.Redo)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        cut_action = QAction("Cu&t", self)
        cut_action.setShortcut(QKeySequence.Cut)
        edit_menu.addAction(cut_action)

        copy_action = QAction("&Copy", self)
        copy_action.setShortcut(QKeySequence.Copy)
        edit_menu.addAction(copy_action)

        paste_action = QAction("&Paste", self)
        paste_action.setShortcut(QKeySequence.Paste)
        edit_menu.addAction(paste_action)

        # View menu
        view_menu = menubar.addMenu("&View")

        self.toggle_sidebar_action = QAction("Toggle &Sidebar", self)
        self.toggle_sidebar_action.setCheckable(True)
        self.toggle_sidebar_action.setChecked(self.config.ui.sidebar_visible)
        view_menu.addAction(self.toggle_sidebar_action)

        self.toggle_toolbar_action = QAction("Toggle &Toolbar", self)
        self.toggle_toolbar_action.setCheckable(True)
        self.toggle_toolbar_action.setChecked(self.config.ui.toolbar_visible)
        view_menu.addAction(self.toggle_toolbar_action)

        view_menu.addSeparator()

        toggle_mode_action = QAction("Toggle &Edit/Render Mode", self)
        toggle_mode_action.setShortcut("Ctrl+I")
        view_menu.addAction(toggle_mode_action)

        # Text-to-Speech menu
        tts_menu = menubar.addMenu("&Text-to-Speech")

        play_action = QAction("&Play", self)
        tts_menu.addAction(play_action)

        pause_action = QAction("P&ause", self)
        tts_menu.addAction(pause_action)

        stop_action = QAction("&Stop", self)
        tts_menu.addAction(stop_action)

        tts_menu.addSeparator()

        self.voice_menu = tts_menu.addMenu("&Voice")
        self.speed_menu = tts_menu.addMenu("S&peed")
        self.volume_menu = tts_menu.addMenu("Volu&me")

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        help_menu.addAction(about_action)

    def _setup_status_bar(self):
        """Create status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def _setup_central_widget(self):
        """Set up placeholder central widget."""
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addWidget(QLabel("Content area - to be replaced"))
        self.setCentralWidget(central)

    def closeEvent(self, event):
        """Save config on close."""
        self.config.ui.window_width = self.width()
        self.config.ui.window_height = self.height()
        save_config(self.config)
        event.accept()
```

**Step 3: Update main.py to use MainWindow**

```python
"""Typora TTS App - Markdown editor with text-to-speech."""
import sys
from PySide6.QtWidgets import QApplication

from src.ui import MainWindow


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

**Step 4: Run and verify**

Run: `python main.py`
Expected: Window with full menu bar (File, Edit, View, Text-to-Speech, Help), status bar shows "Ready"

**Step 5: Commit**

```bash
git add src/ui/ main.py
git commit -m "feat: add main window with menu bar structure"
```

---

## Task 4: Editor Widget

**Files:**
- Create: `src/ui/editor.py`
- Create: `tests/test_editor.py`

**Step 1: Write failing test**

Create `tests/test_editor.py`:
```python
"""Tests for editor widget."""
import pytest
from PySide6.QtWidgets import QApplication

# Ensure QApplication exists for widget tests
@pytest.fixture(scope="module")
def app():
    app = QApplication.instance() or QApplication([])
    yield app


def test_editor_widget_exists(app):
    from src.ui.editor import EditorWidget
    editor = EditorWidget()
    assert editor is not None


def test_editor_can_set_and_get_text(app):
    from src.ui.editor import EditorWidget
    editor = EditorWidget()
    editor.set_text("# Hello World")
    assert editor.get_text() == "# Hello World"


def test_editor_emits_modified_signal(app, qtbot):
    from src.ui.editor import EditorWidget
    editor = EditorWidget()

    with qtbot.waitSignal(editor.text_modified, timeout=1000):
        editor.set_text("New content")
        # Simulate typing
        editor.insertPlainText("x")
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_editor.py -v`
Expected: FAIL with "cannot import name 'EditorWidget'"

**Step 3: Implement editor widget**

Create `src/ui/editor.py`:
```python
"""Markdown editor widget using QPlainTextEdit."""
from PySide6.QtWidgets import QPlainTextEdit
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont


class EditorWidget(QPlainTextEdit):
    """Plain text editor for markdown editing."""

    text_modified = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_editor()
        self.textChanged.connect(self._on_text_changed)

    def _setup_editor(self):
        """Configure editor appearance and behavior."""
        font = QFont("Consolas", 11)
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)
        self.setLineWrapMode(QPlainTextEdit.WidgetWidth)
        self.setTabStopDistance(40)

    def _on_text_changed(self):
        """Emit modified signal when text changes."""
        self.text_modified.emit()

    def set_text(self, text: str) -> None:
        """Set editor content."""
        self.setPlainText(text)

    def get_text(self) -> str:
        """Get editor content."""
        return self.toPlainText()
```

**Step 4: Update src/ui/__init__.py**

```python
"""UI components package."""
from src.ui.main_window import MainWindow
from src.ui.editor import EditorWidget

__all__ = ["MainWindow", "EditorWidget"]
```

**Step 5: Run tests to verify they pass**

Run: `pytest tests/test_editor.py -v`
Expected: All tests PASS (note: qtbot fixture requires pytest-qt, install if needed)

**Step 6: Commit**

```bash
git add src/ui/editor.py src/ui/__init__.py tests/test_editor.py
git commit -m "feat: add editor widget with plain text editing"
```

---

## Task 5: Markdown Renderer

**Files:**
- Create: `src/markdown/__init__.py`
- Create: `src/markdown/renderer.py`
- Create: `resources/styles/markdown.css`
- Create: `tests/test_renderer.py`

**Step 1: Create directories**

```bash
mkdir -p src/markdown resources/styles
```

**Step 2: Write failing test**

Create `tests/test_renderer.py`:
```python
"""Tests for markdown renderer."""
import pytest


def test_renderer_converts_heading():
    from src.markdown.renderer import MarkdownRenderer
    renderer = MarkdownRenderer()
    html = renderer.render("# Hello")
    assert "<h1>" in html
    assert "Hello" in html


def test_renderer_converts_bold():
    from src.markdown.renderer import MarkdownRenderer
    renderer = MarkdownRenderer()
    html = renderer.render("**bold text**")
    assert "<strong>" in html or "<b>" in html


def test_renderer_includes_sentence_spans():
    from src.markdown.renderer import MarkdownRenderer
    renderer = MarkdownRenderer()
    html = renderer.render("First sentence. Second sentence.")
    assert 'data-sentence="0"' in html
    assert 'data-sentence="1"' in html


def test_renderer_includes_word_spans():
    from src.markdown.renderer import MarkdownRenderer
    renderer = MarkdownRenderer()
    html = renderer.render("Hello world")
    assert 'data-word=' in html


def test_renderer_applies_highlight_colors():
    from src.markdown.renderer import MarkdownRenderer
    config = {
        "highlight": {
            "sentence_color": "#ff0000",
            "sentence_opacity": 0.8,
            "word_color": "#00ff00",
            "word_opacity": 0.9,
        }
    }
    renderer = MarkdownRenderer(highlight_config=config["highlight"])
    html = renderer.render("Test")
    assert "#ff0000" in html
    assert "#00ff00" in html


def test_renderer_syntax_highlights_code():
    from src.markdown.renderer import MarkdownRenderer
    renderer = MarkdownRenderer()
    html = renderer.render("```python\nprint('hello')\n```")
    assert "highlight" in html or "codehilite" in html
```

**Step 3: Run test to verify it fails**

Run: `pytest tests/test_renderer.py -v`
Expected: FAIL with "cannot import name 'MarkdownRenderer'"

**Step 4: Implement markdown renderer**

Create `src/markdown/__init__.py`:
```python
"""Markdown processing package."""
from src.markdown.renderer import MarkdownRenderer

__all__ = ["MarkdownRenderer"]
```

Create `src/markdown/renderer.py`:
```python
"""Markdown to HTML renderer with TTS support."""
import re
import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.tables import TableExtension
from markdown.extensions.footnotes import FootnoteExtension
from markdown.extensions.toc import TocExtension
from markdown.extensions.nl2br import Nl2BrExtension
from markdown.extensions.sane_lists import SaneListExtension


class MarkdownRenderer:
    """Renders markdown to HTML with sentence/word spans for TTS highlighting."""

    def __init__(self, highlight_config=None):
        """Initialize renderer with optional highlight configuration."""
        self.highlight_config = highlight_config or {
            "sentence_color": "#fff3cd",
            "sentence_opacity": 1.0,
            "word_color": "#ffc107",
            "word_opacity": 1.0,
        }
        self.md = markdown.Markdown(
            extensions=[
                CodeHiliteExtension(css_class="highlight", guess_lang=True),
                TableExtension(),
                FootnoteExtension(),
                TocExtension(),
                Nl2BrExtension(),
                SaneListExtension(),
                "md_in_html",
            ]
        )

    def render(self, text: str) -> str:
        """Convert markdown to HTML with sentence/word spans."""
        # Reset markdown instance for fresh conversion
        self.md.reset()

        # Convert markdown to HTML
        html_content = self.md.convert(text)

        # Wrap sentences and words with spans
        html_content = self._add_tts_spans(html_content)

        # Build full HTML document
        return self._build_document(html_content)

    def _add_tts_spans(self, html: str) -> str:
        """Add sentence and word spans for TTS highlighting."""
        # Split into sentences (simple approach: split on . ! ?)
        # This works on the text content, preserving HTML tags

        sentence_idx = 0
        word_offset = 0
        result = []

        # Process text nodes while preserving HTML structure
        # Split by HTML tags
        parts = re.split(r'(<[^>]+>)', html)

        for part in parts:
            if part.startswith('<'):
                # HTML tag - keep as-is
                result.append(part)
            else:
                # Text content - wrap sentences and words
                processed = self._process_text_node(part, sentence_idx, word_offset)
                result.append(processed["html"])
                sentence_idx = processed["next_sentence_idx"]
                word_offset = processed["next_word_offset"]

        return ''.join(result)

    def _process_text_node(self, text: str, sentence_idx: int, word_offset: int) -> dict:
        """Process a text node, adding sentence and word spans."""
        if not text.strip():
            return {"html": text, "next_sentence_idx": sentence_idx, "next_word_offset": word_offset}

        result = []
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)

        for i, sentence in enumerate(sentences):
            if not sentence.strip():
                result.append(sentence)
                continue

            words = sentence.split()
            word_spans = []

            for word in words:
                word_span = f'<span class="tts-word" data-word="{word_offset}">{word}</span>'
                word_spans.append(word_span)
                word_offset += len(word) + 1  # +1 for space

            sentence_html = ' '.join(word_spans)
            result.append(f'<span class="tts-sentence" data-sentence="{sentence_idx}">{sentence_html}</span>')
            sentence_idx += 1

            # Add space between sentences if not last
            if i < len(sentences) - 1:
                result.append(' ')

        return {
            "html": ''.join(result),
            "next_sentence_idx": sentence_idx,
            "next_word_offset": word_offset,
        }

    def _build_document(self, content: str) -> str:
        """Build complete HTML document with CSS and JavaScript."""
        css = self._generate_css()
        js = self._generate_js()

        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>{css}</style>
</head>
<body>
    <div class="markdown-body">{content}</div>
    <script>{js}</script>
</body>
</html>"""

    def _generate_css(self) -> str:
        """Generate CSS with highlight colors from config."""
        return f"""
body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    font-size: 16px;
    line-height: 1.6;
    padding: 20px;
    max-width: 900px;
    margin: 0 auto;
    color: #333;
}}

.markdown-body h1, .markdown-body h2, .markdown-body h3 {{
    margin-top: 24px;
    margin-bottom: 16px;
    font-weight: 600;
}}

.markdown-body h1 {{ font-size: 2em; border-bottom: 1px solid #eee; padding-bottom: 0.3em; }}
.markdown-body h2 {{ font-size: 1.5em; border-bottom: 1px solid #eee; padding-bottom: 0.3em; }}
.markdown-body h3 {{ font-size: 1.25em; }}

.markdown-body p {{ margin-bottom: 16px; }}

.markdown-body code {{
    background-color: #f6f8fa;
    padding: 0.2em 0.4em;
    border-radius: 3px;
    font-family: "Consolas", "Monaco", monospace;
    font-size: 85%;
}}

.markdown-body pre {{
    background-color: #f6f8fa;
    padding: 16px;
    overflow: auto;
    border-radius: 6px;
}}

.markdown-body pre code {{
    background: none;
    padding: 0;
}}

.markdown-body blockquote {{
    border-left: 4px solid #dfe2e5;
    padding-left: 16px;
    color: #6a737d;
    margin: 0 0 16px 0;
}}

.markdown-body table {{
    border-collapse: collapse;
    width: 100%;
    margin-bottom: 16px;
}}

.markdown-body th, .markdown-body td {{
    border: 1px solid #dfe2e5;
    padding: 8px 12px;
}}

.markdown-body th {{
    background-color: #f6f8fa;
    font-weight: 600;
}}

.markdown-body ul, .markdown-body ol {{
    padding-left: 2em;
    margin-bottom: 16px;
}}

.markdown-body a {{
    color: #0366d6;
    text-decoration: none;
}}

.markdown-body a:hover {{
    text-decoration: underline;
}}

.markdown-body img {{
    max-width: 100%;
}}

.markdown-body hr {{
    border: none;
    border-top: 1px solid #eee;
    margin: 24px 0;
}}

/* TTS Highlighting */
.current-sentence {{
    background-color: {self.highlight_config['sentence_color']};
    opacity: {self.highlight_config['sentence_opacity']};
}}

.current-word {{
    background-color: {self.highlight_config['word_color']};
    opacity: {self.highlight_config['word_opacity']};
    border-radius: 2px;
}}

/* Pygments syntax highlighting */
.highlight pre {{ line-height: 1.4; }}
.highlight .hll {{ background-color: #ffffcc }}
.highlight .c {{ color: #6a737d }} /* Comment */
.highlight .k {{ color: #d73a49 }} /* Keyword */
.highlight .o {{ color: #d73a49 }} /* Operator */
.highlight .n {{ color: #24292e }} /* Name */
.highlight .s {{ color: #032f62 }} /* String */
.highlight .m {{ color: #005cc5 }} /* Number */
.highlight .p {{ color: #24292e }} /* Punctuation */
"""

    def _generate_js(self) -> str:
        """Generate JavaScript for TTS interaction."""
        return """
var autoScrollEnabled = true;

function clearHighlights() {
    document.querySelectorAll('.current-sentence').forEach(el => {
        el.classList.remove('current-sentence');
    });
    document.querySelectorAll('.current-word').forEach(el => {
        el.classList.remove('current-word');
    });
}

function highlightSentence(sentenceIdx) {
    clearHighlights();
    var el = document.querySelector('[data-sentence="' + sentenceIdx + '"]');
    if (el) {
        el.classList.add('current-sentence');
        if (autoScrollEnabled) {
            el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }
}

function highlightWord(wordOffset) {
    document.querySelectorAll('.current-word').forEach(el => {
        el.classList.remove('current-word');
    });
    var el = document.querySelector('[data-word="' + wordOffset + '"]');
    if (el) {
        el.classList.add('current-word');
    }
}

function scrollToSentence(sentenceIdx) {
    autoScrollEnabled = true;
    var el = document.querySelector('[data-sentence="' + sentenceIdx + '"]');
    if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

function disableAutoScroll() {
    autoScrollEnabled = false;
}

function enableAutoScroll() {
    autoScrollEnabled = true;
}

// Detect user scroll to disable auto-scroll
var scrollTimeout;
window.addEventListener('scroll', function() {
    clearTimeout(scrollTimeout);
    scrollTimeout = setTimeout(function() {
        // User initiated scroll
    }, 100);
});

window.addEventListener('wheel', function() {
    autoScrollEnabled = false;
});

// Click-to-jump handler
document.addEventListener('click', function(e) {
    var sentence = e.target.closest('.tts-sentence');
    if (sentence) {
        var idx = sentence.getAttribute('data-sentence');
        if (window.qt && window.qt.webChannelTransport) {
            // Signal to Python via QWebChannel
            window.bridge.sentenceClicked(parseInt(idx));
        }
    }
});
"""


def extract_plain_text(markdown_text: str) -> str:
    """Extract plain text from markdown for TTS."""
    # Remove code blocks
    text = re.sub(r'```[\s\S]*?```', '', markdown_text)
    text = re.sub(r'`[^`]+`', '', text)

    # Remove images
    text = re.sub(r'!\[[^\]]*\]\([^)]+\)', '', text)

    # Convert links to just text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)

    # Remove headers markers
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)

    # Remove bold/italic markers
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'__([^_]+)__', r'\1', text)
    text = re.sub(r'_([^_]+)_', r'\1', text)

    # Remove horizontal rules
    text = re.sub(r'^[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)

    # Clean up whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()

    return text
```

**Step 5: Create base markdown.css**

Create `resources/styles/markdown.css`:
```css
/* Base markdown styles - colors injected dynamically */
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    font-size: 16px;
    line-height: 1.6;
    padding: 20px;
    max-width: 900px;
    margin: 0 auto;
}
```

**Step 6: Run tests to verify they pass**

Run: `pytest tests/test_renderer.py -v`
Expected: All tests PASS

**Step 7: Commit**

```bash
git add src/markdown/ resources/ tests/test_renderer.py
git commit -m "feat: add markdown renderer with TTS spans and highlighting"
```

---

## Task 6: Viewer Widget

**Files:**
- Create: `src/ui/viewer.py`
- Create: `tests/test_viewer.py`

**Step 1: Write failing test**

Create `tests/test_viewer.py`:
```python
"""Tests for viewer widget."""
import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="module")
def app():
    app = QApplication.instance() or QApplication([])
    yield app


def test_viewer_widget_exists(app):
    from src.ui.viewer import ViewerWidget
    viewer = ViewerWidget()
    assert viewer is not None


def test_viewer_can_load_html(app):
    from src.ui.viewer import ViewerWidget
    viewer = ViewerWidget()
    viewer.set_html("<h1>Test</h1>")
    # Widget should not crash


def test_viewer_can_run_javascript(app):
    from src.ui.viewer import ViewerWidget
    viewer = ViewerWidget()
    viewer.set_html("<div id='test'>Hello</div>")
    # Should be able to call JS without error
    viewer.run_js("console.log('test')")
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_viewer.py -v`
Expected: FAIL with "cannot import name 'ViewerWidget'"

**Step 3: Implement viewer widget**

Create `src/ui/viewer.py`:
```python
"""Markdown viewer widget using QWebEngineView."""
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtCore import QObject, Signal, Slot


class WebBridge(QObject):
    """Bridge for JavaScript to Python communication."""

    sentence_clicked = Signal(int)

    @Slot(int)
    def sentenceClicked(self, sentence_idx: int):
        """Called from JavaScript when a sentence is clicked."""
        self.sentence_clicked.emit(sentence_idx)


class ViewerWidget(QWebEngineView):
    """Web view for displaying rendered markdown."""

    sentence_clicked = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_web_channel()

    def _setup_web_channel(self):
        """Set up QWebChannel for JS-Python communication."""
        self.channel = QWebChannel()
        self.bridge = WebBridge()
        self.channel.registerObject("bridge", self.bridge)
        self.page().setWebChannel(self.channel)

        # Forward bridge signals
        self.bridge.sentence_clicked.connect(self.sentence_clicked.emit)

    def set_html(self, html: str) -> None:
        """Load HTML content into the viewer."""
        # Inject QWebChannel setup
        channel_js = """
        <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                new QWebChannel(qt.webChannelTransport, function(channel) {
                    window.bridge = channel.objects.bridge;
                });
            });
        </script>
        """
        # Insert before </head>
        if "</head>" in html:
            html = html.replace("</head>", channel_js + "</head>")
        else:
            html = channel_js + html

        self.setHtml(html)

    def run_js(self, script: str, callback=None) -> None:
        """Execute JavaScript in the viewer."""
        if callback:
            self.page().runJavaScript(script, callback)
        else:
            self.page().runJavaScript(script)

    def highlight_sentence(self, sentence_idx: int) -> None:
        """Highlight a sentence by index."""
        self.run_js(f"highlightSentence({sentence_idx})")

    def highlight_word(self, word_offset: int) -> None:
        """Highlight a word by offset."""
        self.run_js(f"highlightWord({word_offset})")

    def clear_highlights(self) -> None:
        """Clear all highlights."""
        self.run_js("clearHighlights()")

    def scroll_to_sentence(self, sentence_idx: int) -> None:
        """Scroll to a sentence and enable auto-scroll."""
        self.run_js(f"scrollToSentence({sentence_idx})")

    def enable_auto_scroll(self) -> None:
        """Enable auto-scrolling."""
        self.run_js("enableAutoScroll()")

    def disable_auto_scroll(self) -> None:
        """Disable auto-scrolling."""
        self.run_js("disableAutoScroll()")
```

**Step 4: Update src/ui/__init__.py**

```python
"""UI components package."""
from src.ui.main_window import MainWindow
from src.ui.editor import EditorWidget
from src.ui.viewer import ViewerWidget

__all__ = ["MainWindow", "EditorWidget", "ViewerWidget"]
```

**Step 5: Run tests to verify they pass**

Run: `pytest tests/test_viewer.py -v`
Expected: All tests PASS

**Step 6: Commit**

```bash
git add src/ui/viewer.py src/ui/__init__.py tests/test_viewer.py
git commit -m "feat: add viewer widget with QWebChannel bridge"
```

---

## Task 7: Edit/Render Toggle

**Files:**
- Modify: `src/ui/main_window.py`

**Step 1: Update main_window.py with stacked widget**

Replace the `_setup_central_widget` method and add mode toggle:

```python
"""Main application window."""
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QSplitter,
    QStackedWidget,
    QMenuBar,
    QStatusBar,
    QFileDialog,
    QMessageBox,
)
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtCore import Qt

from src.config import load_config, save_config
from src.ui.editor import EditorWidget
from src.ui.viewer import ViewerWidget
from src.markdown.renderer import MarkdownRenderer


class MainWindow(QMainWindow):
    """Main application window with menu bar and status bar."""

    # Edit mode = 0, Render mode = 1
    EDIT_MODE = 0
    RENDER_MODE = 1

    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.current_file = None
        self.is_modified = False
        self.current_mode = self.EDIT_MODE

        self._setup_window()
        self._setup_components()
        self._setup_menu_bar()
        self._setup_status_bar()
        self._setup_central_widget()
        self._connect_signals()

    def _setup_window(self):
        """Configure window properties."""
        self.setWindowTitle("Typora TTS")
        self.resize(
            self.config.ui.window_width,
            self.config.ui.window_height,
        )
        self.setAcceptDrops(True)

    def _setup_components(self):
        """Initialize main components."""
        self.editor = EditorWidget()
        self.viewer = ViewerWidget()
        self.renderer = MarkdownRenderer(
            highlight_config=dict(self.config.highlight)
        )

    def _setup_menu_bar(self):
        """Create menu bar with all menus."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        self.open_file_action = QAction("&Open File...", self)
        self.open_file_action.setShortcut(QKeySequence.Open)
        self.open_file_action.triggered.connect(self.open_file_dialog)
        file_menu.addAction(self.open_file_action)

        self.open_folder_action = QAction("Open &Folder...", self)
        self.open_folder_action.triggered.connect(self.open_folder_dialog)
        file_menu.addAction(self.open_folder_action)

        self.recent_menu = file_menu.addMenu("&Recent Files")
        self._update_recent_menu()

        file_menu.addSeparator()

        self.save_action = QAction("&Save", self)
        self.save_action.setShortcut(QKeySequence.Save)
        self.save_action.triggered.connect(self.save_file)
        file_menu.addAction(self.save_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")

        self.undo_action = QAction("&Undo", self)
        self.undo_action.setShortcut(QKeySequence.Undo)
        self.undo_action.triggered.connect(self.editor.undo)
        edit_menu.addAction(self.undo_action)

        self.redo_action = QAction("&Redo", self)
        self.redo_action.setShortcut(QKeySequence.Redo)
        self.redo_action.triggered.connect(self.editor.redo)
        edit_menu.addAction(self.redo_action)

        edit_menu.addSeparator()

        self.cut_action = QAction("Cu&t", self)
        self.cut_action.setShortcut(QKeySequence.Cut)
        self.cut_action.triggered.connect(self.editor.cut)
        edit_menu.addAction(self.cut_action)

        self.copy_action = QAction("&Copy", self)
        self.copy_action.setShortcut(QKeySequence.Copy)
        self.copy_action.triggered.connect(self.editor.copy)
        edit_menu.addAction(self.copy_action)

        self.paste_action = QAction("&Paste", self)
        self.paste_action.setShortcut(QKeySequence.Paste)
        self.paste_action.triggered.connect(self.editor.paste)
        edit_menu.addAction(self.paste_action)

        # View menu
        view_menu = menubar.addMenu("&View")

        self.toggle_sidebar_action = QAction("Toggle &Sidebar", self)
        self.toggle_sidebar_action.setCheckable(True)
        self.toggle_sidebar_action.setChecked(self.config.ui.sidebar_visible)
        view_menu.addAction(self.toggle_sidebar_action)

        self.toggle_toolbar_action = QAction("Toggle &Toolbar", self)
        self.toggle_toolbar_action.setCheckable(True)
        self.toggle_toolbar_action.setChecked(self.config.ui.toolbar_visible)
        view_menu.addAction(self.toggle_toolbar_action)

        view_menu.addSeparator()

        self.toggle_mode_action = QAction("Toggle &Edit/Render Mode", self)
        self.toggle_mode_action.setShortcut("Ctrl+I")
        self.toggle_mode_action.triggered.connect(self.toggle_mode)
        view_menu.addAction(self.toggle_mode_action)

        # Text-to-Speech menu
        tts_menu = menubar.addMenu("&Text-to-Speech")

        self.play_action = QAction("&Play", self)
        tts_menu.addAction(self.play_action)

        self.pause_action = QAction("P&ause", self)
        tts_menu.addAction(self.pause_action)

        self.stop_action = QAction("&Stop", self)
        tts_menu.addAction(self.stop_action)

        tts_menu.addSeparator()

        self.voice_menu = tts_menu.addMenu("&Voice")
        self.speed_menu = tts_menu.addMenu("S&peed")
        self.volume_menu = tts_menu.addMenu("Volu&me")

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def _setup_status_bar(self):
        """Create status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self._update_status()

    def _setup_central_widget(self):
        """Set up central widget with splitter and stacked widget."""
        # Main splitter for sidebar and content
        self.main_splitter = QSplitter(Qt.Horizontal)

        # Stacked widget for editor/viewer
        self.content_stack = QStackedWidget()
        self.content_stack.addWidget(self.editor)  # Index 0 = Edit mode
        self.content_stack.addWidget(self.viewer)  # Index 1 = Render mode

        # For now, just add content stack (sidebar will be added later)
        self.main_splitter.addWidget(self.content_stack)

        self.setCentralWidget(self.main_splitter)

    def _connect_signals(self):
        """Connect widget signals."""
        self.editor.text_modified.connect(self._on_text_modified)
        self.viewer.sentence_clicked.connect(self._on_sentence_clicked)

    def _on_text_modified(self):
        """Handle text modification."""
        self.is_modified = True
        self._update_title()

    def _on_sentence_clicked(self, sentence_idx: int):
        """Handle sentence click in viewer."""
        # Will be connected to TTS later
        self.status_bar.showMessage(f"Sentence {sentence_idx} clicked")

    def _update_title(self):
        """Update window title with file name and modified indicator."""
        title = "Typora TTS"
        if self.current_file:
            title = f"{Path(self.current_file).name} - {title}"
        if self.is_modified:
            title = f"*{title}"
        self.setWindowTitle(title)

    def _update_status(self):
        """Update status bar."""
        mode = "Edit" if self.current_mode == self.EDIT_MODE else "Render"
        self.status_bar.showMessage(f"Mode: {mode}")

    def _update_recent_menu(self):
        """Update recent files menu."""
        self.recent_menu.clear()
        for file_path in self.config.recent.files[:10]:
            action = QAction(file_path, self)
            action.triggered.connect(lambda checked, p=file_path: self.open_file(p))
            self.recent_menu.addAction(action)

    def _add_to_recent(self, file_path: str):
        """Add file to recent files list."""
        files = list(self.config.recent.files)
        if file_path in files:
            files.remove(file_path)
        files.insert(0, file_path)
        self.config.recent.files = files[:10]
        self._update_recent_menu()
        save_config(self.config)

    def toggle_mode(self):
        """Toggle between edit and render mode."""
        if self.current_mode == self.EDIT_MODE:
            # Switch to render mode
            html = self.renderer.render(self.editor.get_text())
            self.viewer.set_html(html)
            self.content_stack.setCurrentIndex(self.RENDER_MODE)
            self.current_mode = self.RENDER_MODE
            self._set_edit_actions_enabled(False)
        else:
            # Switch to edit mode
            self.content_stack.setCurrentIndex(self.EDIT_MODE)
            self.current_mode = self.EDIT_MODE
            self._set_edit_actions_enabled(True)

        self._update_status()

    def _set_edit_actions_enabled(self, enabled: bool):
        """Enable/disable edit actions based on mode."""
        self.undo_action.setEnabled(enabled)
        self.redo_action.setEnabled(enabled)
        self.cut_action.setEnabled(enabled)
        self.paste_action.setEnabled(enabled)

    def open_file_dialog(self):
        """Show open file dialog."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Markdown File",
            self.config.recent.last_folder or "",
            "Markdown Files (*.md *.markdown);;All Files (*)",
        )
        if file_path:
            self.open_file(file_path)

    def open_folder_dialog(self):
        """Show open folder dialog."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Open Folder",
            self.config.recent.last_folder or "",
        )
        if folder:
            self.open_folder(folder)

    def open_file(self, file_path: str):
        """Open a markdown file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.editor.set_text(content)
            self.current_file = file_path
            self.is_modified = False
            self._update_title()
            self._add_to_recent(file_path)
            self.config.recent.last_folder = str(Path(file_path).parent)

            # Switch to edit mode when opening file
            if self.current_mode == self.RENDER_MODE:
                self.toggle_mode()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open file:\n{e}")

    def open_folder(self, folder: str):
        """Open a folder in sidebar."""
        self.config.recent.last_folder = folder
        save_config(self.config)
        # Sidebar will be implemented in next task
        self.status_bar.showMessage(f"Opened folder: {folder}")

    def save_file(self):
        """Save current file."""
        if not self.current_file:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Markdown File",
                self.config.recent.last_folder or "",
                "Markdown Files (*.md);;All Files (*)",
            )
            if not file_path:
                return
            self.current_file = file_path

        try:
            with open(self.current_file, "w", encoding="utf-8") as f:
                f.write(self.editor.get_text())
            self.is_modified = False
            self._update_title()
            self._add_to_recent(self.current_file)
            self.status_bar.showMessage("File saved", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save file:\n{e}")

    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Typora TTS",
            "Typora TTS\n\nA Markdown editor with text-to-speech.\n\nVersion 0.1.0",
        )

    def dragEnterEvent(self, event):
        """Handle drag enter."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        """Handle file/folder drop."""
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.endswith(('.md', '.markdown')):
                self.open_file(path)
            elif Path(path).is_dir():
                self.open_folder(path)

    def closeEvent(self, event):
        """Handle close with unsaved changes check."""
        if self.is_modified:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "Save changes before closing?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            )
            if reply == QMessageBox.Save:
                self.save_file()
            elif reply == QMessageBox.Cancel:
                event.ignore()
                return

        # Save window state
        self.config.ui.window_width = self.width()
        self.config.ui.window_height = self.height()
        save_config(self.config)
        event.accept()
```

**Step 2: Run and verify**

Run: `python main.py`
Expected:
- Window opens with editor
- Ctrl+I switches to render mode (shows rendered markdown)
- Ctrl+I again switches back to edit mode
- Status bar shows current mode

**Step 3: Commit**

```bash
git add src/ui/main_window.py
git commit -m "feat: add edit/render mode toggle with Ctrl+I"
```

---

## Task 8: Sidebar File Tree

**Files:**
- Create: `src/ui/sidebar.py`
- Modify: `src/ui/main_window.py`

**Step 1: Create sidebar widget**

Create `src/ui/sidebar.py`:
```python
"""Sidebar file tree widget."""
from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTreeView, QLabel
from PySide6.QtCore import Signal, QDir
from PySide6.QtGui import QFileSystemModel


class SidebarWidget(QWidget):
    """File tree sidebar for folder navigation."""

    file_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Set up the sidebar UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header label
        self.header = QLabel("No folder open")
        layout.addWidget(self.header)

        # File system model
        self.model = QFileSystemModel()
        self.model.setNameFilters(["*.md", "*.markdown"])
        self.model.setNameFilterDisables(False)  # Hide non-matching

        # Tree view
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setHeaderHidden(True)

        # Hide size, type, date columns
        self.tree.hideColumn(1)
        self.tree.hideColumn(2)
        self.tree.hideColumn(3)

        self.tree.clicked.connect(self._on_item_clicked)
        self.tree.doubleClicked.connect(self._on_item_double_clicked)

        layout.addWidget(self.tree)

    def set_folder(self, folder_path: str):
        """Set the root folder for the tree."""
        path = Path(folder_path)
        if path.exists() and path.is_dir():
            self.model.setRootPath(folder_path)
            self.tree.setRootIndex(self.model.index(folder_path))
            self.header.setText(path.name)

    def _on_item_clicked(self, index):
        """Handle single click on item."""
        pass  # Reserved for future use

    def _on_item_double_clicked(self, index):
        """Handle double click to open file."""
        file_path = self.model.filePath(index)
        if Path(file_path).is_file():
            self.file_selected.emit(file_path)
```

**Step 2: Update main_window.py to include sidebar**

Add to imports:
```python
from src.ui.sidebar import SidebarWidget
```

Update `_setup_components`:
```python
def _setup_components(self):
    """Initialize main components."""
    self.sidebar = SidebarWidget()
    self.editor = EditorWidget()
    self.viewer = ViewerWidget()
    self.renderer = MarkdownRenderer(
        highlight_config=dict(self.config.highlight)
    )
```

Update `_setup_central_widget`:
```python
def _setup_central_widget(self):
    """Set up central widget with splitter and stacked widget."""
    # Main splitter for sidebar and content
    self.main_splitter = QSplitter(Qt.Horizontal)

    # Add sidebar
    self.main_splitter.addWidget(self.sidebar)

    # Stacked widget for editor/viewer
    self.content_stack = QStackedWidget()
    self.content_stack.addWidget(self.editor)  # Index 0 = Edit mode
    self.content_stack.addWidget(self.viewer)  # Index 1 = Render mode

    self.main_splitter.addWidget(self.content_stack)

    # Set initial sizes
    self.main_splitter.setSizes([
        self.config.ui.sidebar_width,
        self.config.ui.window_width - self.config.ui.sidebar_width,
    ])

    # Sidebar visibility
    self.sidebar.setVisible(self.config.ui.sidebar_visible)

    self.setCentralWidget(self.main_splitter)
```

Update `_connect_signals`:
```python
def _connect_signals(self):
    """Connect widget signals."""
    self.editor.text_modified.connect(self._on_text_modified)
    self.viewer.sentence_clicked.connect(self._on_sentence_clicked)
    self.sidebar.file_selected.connect(self.open_file)
    self.toggle_sidebar_action.triggered.connect(self._toggle_sidebar)
```

Add toggle method:
```python
def _toggle_sidebar(self):
    """Toggle sidebar visibility."""
    visible = not self.sidebar.isVisible()
    self.sidebar.setVisible(visible)
    self.toggle_sidebar_action.setChecked(visible)
    self.config.ui.sidebar_visible = visible
```

Update `open_folder`:
```python
def open_folder(self, folder: str):
    """Open a folder in sidebar."""
    self.sidebar.set_folder(folder)
    self.config.recent.last_folder = folder
    save_config(self.config)
    self.status_bar.showMessage(f"Opened folder: {folder}")
```

Update `closeEvent` to save sidebar width:
```python
def closeEvent(self, event):
    """Handle close with unsaved changes check."""
    if self.is_modified:
        reply = QMessageBox.question(
            self,
            "Unsaved Changes",
            "Save changes before closing?",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
        )
        if reply == QMessageBox.Save:
            self.save_file()
        elif reply == QMessageBox.Cancel:
            event.ignore()
            return

    # Save window state
    self.config.ui.window_width = self.width()
    self.config.ui.window_height = self.height()
    self.config.ui.sidebar_width = self.main_splitter.sizes()[0]
    self.config.ui.sidebar_visible = self.sidebar.isVisible()
    save_config(self.config)
    event.accept()
```

**Step 3: Update src/ui/__init__.py**

```python
"""UI components package."""
from src.ui.main_window import MainWindow
from src.ui.editor import EditorWidget
from src.ui.viewer import ViewerWidget
from src.ui.sidebar import SidebarWidget

__all__ = ["MainWindow", "EditorWidget", "ViewerWidget", "SidebarWidget"]
```

**Step 4: Run and verify**

Run: `python main.py`
Expected:
- Sidebar visible on left
- File > Open Folder populates sidebar
- Double-clicking .md file opens it in editor
- View > Toggle Sidebar hides/shows sidebar

**Step 5: Commit**

```bash
git add src/ui/sidebar.py src/ui/main_window.py src/ui/__init__.py
git commit -m "feat: add sidebar file tree with folder navigation"
```

---

## Task 9: TTS Engine

**Files:**
- Create: `src/tts/__init__.py`
- Create: `src/tts/engine.py`
- Create: `tests/test_tts_engine.py`

**Step 1: Create tests/test_tts_engine.py**

```python
"""Tests for TTS engine."""
import pytest


def test_tts_engine_exists():
    from src.tts.engine import TTSEngine
    assert TTSEngine is not None


def test_tts_engine_init_without_credentials():
    from src.tts.engine import TTSEngine
    engine = TTSEngine(speech_key="", speech_region="eastus")
    assert engine.is_configured() == False


def test_tts_engine_build_ssml():
    from src.tts.engine import TTSEngine
    engine = TTSEngine(speech_key="test", speech_region="eastus")
    ssml = engine._build_ssml("Hello world", voice="en-US-JennyNeural", rate=1.0, volume=100)
    assert "<speak" in ssml
    assert "Hello world" in ssml
    assert "en-US-JennyNeural" in ssml


def test_tts_engine_build_ssml_with_rate():
    from src.tts.engine import TTSEngine
    engine = TTSEngine(speech_key="test", speech_region="eastus")
    ssml = engine._build_ssml("Test", voice="en-US-JennyNeural", rate=1.5, volume=100)
    assert 'rate="1.5"' in ssml or 'rate="150%"' in ssml
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_tts_engine.py -v`
Expected: FAIL with "cannot import name 'TTSEngine'"

**Step 3: Implement TTS engine**

Create `src/tts/__init__.py`:
```python
"""Text-to-speech package."""
from src.tts.engine import TTSEngine

__all__ = ["TTSEngine"]
```

Create `src/tts/engine.py`:
```python
"""Azure Text-to-Speech engine."""
from typing import Optional, List, Callable
from PySide6.QtCore import QObject, Signal, QThread

try:
    import azure.cognitiveservices.speech as speechsdk
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    speechsdk = None


class TTSWorker(QThread):
    """Worker thread for TTS synthesis."""

    word_boundary = Signal(int, int)  # start, end offsets
    synthesis_completed = Signal()
    synthesis_error = Signal(str)

    def __init__(self, synthesizer, ssml: str):
        super().__init__()
        self.synthesizer = synthesizer
        self.ssml = ssml
        self._stop_requested = False

    def run(self):
        """Run synthesis in background thread."""
        try:
            result = self.synthesizer.speak_ssml_async(self.ssml).get()
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                self.synthesis_completed.emit()
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation = result.cancellation_details
                if cancellation.reason == speechsdk.CancellationReason.Error:
                    self.synthesis_error.emit(cancellation.error_details)
        except Exception as e:
            self.synthesis_error.emit(str(e))

    def stop(self):
        """Request stop."""
        self._stop_requested = True
        if self.synthesizer:
            self.synthesizer.stop_speaking_async()


class TTSEngine(QObject):
    """Azure TTS engine with word boundary events."""

    # Signals
    word_boundary = Signal(int, int)  # start, end character offsets
    playback_started = Signal()
    playback_paused = Signal()
    playback_resumed = Signal()
    playback_stopped = Signal()
    playback_finished = Signal()
    error_occurred = Signal(str)
    voices_loaded = Signal(list)

    def __init__(self, speech_key: str, speech_region: str, parent=None):
        super().__init__(parent)
        self.speech_key = speech_key
        self.speech_region = speech_region
        self.synthesizer = None
        self.worker = None
        self.current_voice = "en-US-JennyNeural"
        self.current_rate = 1.0
        self.current_volume = 100
        self._is_playing = False
        self._is_paused = False

        if self.is_configured():
            self._init_synthesizer()

    def is_configured(self) -> bool:
        """Check if Azure credentials are configured."""
        return bool(self.speech_key and self.speech_region and AZURE_AVAILABLE)

    def _init_synthesizer(self):
        """Initialize the speech synthesizer."""
        if not AZURE_AVAILABLE:
            return

        speech_config = speechsdk.SpeechConfig(
            subscription=self.speech_key,
            region=self.speech_region,
        )
        speech_config.set_speech_synthesis_output_format(
            speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
        )

        audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

        self.synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config,
            audio_config=audio_config,
        )

        # Connect word boundary event
        self.synthesizer.synthesis_word_boundary.connect(self._on_word_boundary)

    def _on_word_boundary(self, evt):
        """Handle word boundary event from Azure."""
        self.word_boundary.emit(evt.text_offset, evt.text_offset + evt.word_length)

    def _build_ssml(self, text: str, voice: str, rate: float, volume: int) -> str:
        """Build SSML for synthesis."""
        # Convert rate to percentage (1.0 = 100%)
        rate_percent = f"{int(rate * 100)}%"
        # Volume as percentage
        volume_str = f"{volume}%"

        return f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
    <voice name="{voice}">
        <prosody rate="{rate_percent}" volume="{volume_str}">
            {text}
        </prosody>
    </voice>
</speak>"""

    def play(self, text: str):
        """Start TTS playback."""
        if not self.is_configured():
            self.error_occurred.emit("Azure TTS not configured. Please check config.yaml")
            return

        if self._is_playing:
            self.stop()

        ssml = self._build_ssml(text, self.current_voice, self.current_rate, self.current_volume)

        self.worker = TTSWorker(self.synthesizer, ssml)
        self.worker.word_boundary.connect(self.word_boundary.emit)
        self.worker.synthesis_completed.connect(self._on_synthesis_completed)
        self.worker.synthesis_error.connect(self._on_synthesis_error)
        self.worker.start()

        self._is_playing = True
        self._is_paused = False
        self.playback_started.emit()

    def pause(self):
        """Pause playback."""
        # Note: Azure SDK doesn't have native pause, we'll stop and track position
        if self._is_playing and not self._is_paused:
            self._is_paused = True
            self.playback_paused.emit()

    def resume(self):
        """Resume playback."""
        if self._is_paused:
            self._is_paused = False
            self.playback_resumed.emit()

    def stop(self):
        """Stop playback."""
        if self.worker:
            self.worker.stop()
            self.worker.wait()
            self.worker = None

        self._is_playing = False
        self._is_paused = False
        self.playback_stopped.emit()

    def _on_synthesis_completed(self):
        """Handle synthesis completion."""
        self._is_playing = False
        self._is_paused = False
        self.playback_finished.emit()

    def _on_synthesis_error(self, error: str):
        """Handle synthesis error."""
        self._is_playing = False
        self._is_paused = False
        self.error_occurred.emit(error)

    def set_voice(self, voice: str):
        """Set the TTS voice."""
        self.current_voice = voice

    def set_rate(self, rate: float):
        """Set playback rate (0.5 - 2.0)."""
        self.current_rate = max(0.5, min(2.0, rate))

    def set_volume(self, volume: int):
        """Set volume (0 - 100)."""
        self.current_volume = max(0, min(100, volume))

    def get_available_voices(self) -> List[str]:
        """Get list of available voices."""
        if not self.is_configured():
            return []

        # Common neural voices
        return [
            "en-US-JennyNeural",
            "en-US-GuyNeural",
            "en-US-AriaNeural",
            "en-US-DavisNeural",
            "en-US-AmberNeural",
            "en-US-AnaNeural",
            "en-US-ChristopherNeural",
            "en-US-EricNeural",
            "en-GB-SoniaNeural",
            "en-GB-RyanNeural",
            "en-AU-NatashaNeural",
            "en-AU-WilliamNeural",
        ]

    @property
    def is_playing(self) -> bool:
        """Check if currently playing."""
        return self._is_playing

    @property
    def is_paused(self) -> bool:
        """Check if paused."""
        return self._is_paused
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_tts_engine.py -v`
Expected: All tests PASS

**Step 5: Commit**

```bash
git add src/tts/ tests/test_tts_engine.py
git commit -m "feat: add Azure TTS engine with word boundary events"
```

---

## Task 10: TTS Highlighter

**Files:**
- Create: `src/tts/highlighter.py`
- Create: `tests/test_highlighter.py`

**Step 1: Write failing test**

Create `tests/test_highlighter.py`:
```python
"""Tests for TTS highlighter."""
import pytest


def test_highlighter_maps_offset_to_sentence():
    from src.tts.highlighter import TTSHighlighter
    text = "First sentence. Second sentence. Third sentence."
    highlighter = TTSHighlighter(text)

    # Offset in first sentence
    assert highlighter.get_sentence_for_offset(5) == 0
    # Offset in second sentence
    assert highlighter.get_sentence_for_offset(20) == 1
    # Offset in third sentence
    assert highlighter.get_sentence_for_offset(40) == 2


def test_highlighter_splits_sentences():
    from src.tts.highlighter import TTSHighlighter
    text = "Hello! How are you? I am fine."
    highlighter = TTSHighlighter(text)

    assert len(highlighter.sentences) == 3


def test_highlighter_tracks_word_offsets():
    from src.tts.highlighter import TTSHighlighter
    text = "Hello world"
    highlighter = TTSHighlighter(text)

    # First word starts at 0
    assert highlighter.get_word_offset(0, 5) == 0
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_highlighter.py -v`
Expected: FAIL

**Step 3: Implement highlighter**

Create `src/tts/highlighter.py`:
```python
"""TTS highlighting manager."""
import re
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class Sentence:
    """A sentence with its character offsets."""
    text: str
    start: int
    end: int
    index: int


class TTSHighlighter:
    """Manages sentence and word highlighting for TTS."""

    def __init__(self, text: str):
        """Initialize with text content."""
        self.text = text
        self.sentences = self._split_sentences(text)
        self.current_sentence_idx = 0
        self.current_word_offset = 0

    def _split_sentences(self, text: str) -> List[Sentence]:
        """Split text into sentences with offset tracking."""
        sentences = []
        # Split on sentence-ending punctuation followed by space or end
        pattern = r'([.!?]+)\s*'

        pos = 0
        idx = 0

        for match in re.finditer(pattern, text):
            end = match.end()
            sentence_text = text[pos:end].strip()
            if sentence_text:
                sentences.append(Sentence(
                    text=sentence_text,
                    start=pos,
                    end=end,
                    index=idx,
                ))
                idx += 1
            pos = end

        # Handle remaining text (no ending punctuation)
        if pos < len(text):
            remaining = text[pos:].strip()
            if remaining:
                sentences.append(Sentence(
                    text=remaining,
                    start=pos,
                    end=len(text),
                    index=idx,
                ))

        return sentences

    def get_sentence_for_offset(self, char_offset: int) -> int:
        """Get sentence index for a character offset."""
        for sentence in self.sentences:
            if sentence.start <= char_offset < sentence.end:
                return sentence.index
        return len(self.sentences) - 1 if self.sentences else 0

    def get_word_offset(self, start: int, end: int) -> int:
        """Get cumulative word offset for highlighting."""
        # Count characters up to this point (for data-word attribute matching)
        return start

    def get_sentence_by_index(self, idx: int) -> Sentence:
        """Get sentence by index."""
        if 0 <= idx < len(self.sentences):
            return self.sentences[idx]
        return None

    def get_text_from_sentence(self, sentence_idx: int) -> str:
        """Get text from a sentence index to end."""
        if sentence_idx >= len(self.sentences):
            return ""

        return ' '.join(s.text for s in self.sentences[sentence_idx:])

    def update_position(self, char_offset: int):
        """Update current position based on character offset."""
        self.current_sentence_idx = self.get_sentence_for_offset(char_offset)
        self.current_word_offset = char_offset
```

Update `src/tts/__init__.py`:
```python
"""Text-to-speech package."""
from src.tts.engine import TTSEngine
from src.tts.highlighter import TTSHighlighter

__all__ = ["TTSEngine", "TTSHighlighter"]
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_highlighter.py -v`
Expected: All tests PASS

**Step 5: Commit**

```bash
git add src/tts/highlighter.py src/tts/__init__.py tests/test_highlighter.py
git commit -m "feat: add TTS highlighter for sentence/word tracking"
```

---

## Task 11: TTS Toolbar

**Files:**
- Create: `src/ui/toolbar.py`
- Modify: `src/ui/main_window.py`

**Step 1: Create toolbar widget**

Create `src/ui/toolbar.py`:
```python
"""TTS control toolbar."""
from PySide6.QtWidgets import (
    QToolBar,
    QPushButton,
    QComboBox,
    QSlider,
    QLabel,
    QWidget,
    QHBoxLayout,
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QIcon


class TTSToolbar(QToolBar):
    """Toolbar with TTS playback controls."""

    play_clicked = Signal()
    pause_clicked = Signal()
    stop_clicked = Signal()
    speed_changed = Signal(float)
    volume_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__("TTS Controls", parent)
        self._setup_ui()

    def _setup_ui(self):
        """Set up toolbar UI."""
        # Play button
        self.play_btn = QPushButton("Play")
        self.play_btn.clicked.connect(self.play_clicked.emit)
        self.addWidget(self.play_btn)

        # Pause button
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.clicked.connect(self.pause_clicked.emit)
        self.addWidget(self.pause_btn)

        # Stop button
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_clicked.emit)
        self.addWidget(self.stop_btn)

        self.addSeparator()

        # Speed control
        self.addWidget(QLabel("Speed:"))
        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["0.5x", "0.75x", "1.0x", "1.25x", "1.5x", "1.75x", "2.0x"])
        self.speed_combo.setCurrentText("1.0x")
        self.speed_combo.currentTextChanged.connect(self._on_speed_changed)
        self.addWidget(self.speed_combo)

        self.addSeparator()

        # Volume control
        self.addWidget(QLabel("Volume:"))
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(100)
        self.volume_slider.setFixedWidth(100)
        self.volume_slider.valueChanged.connect(self._on_volume_changed)
        self.addWidget(self.volume_slider)

        self.volume_label = QLabel("100%")
        self.volume_label.setFixedWidth(40)
        self.addWidget(self.volume_label)

    def _on_speed_changed(self, text: str):
        """Handle speed change."""
        speed = float(text.replace('x', ''))
        self.speed_changed.emit(speed)

    def _on_volume_changed(self, value: int):
        """Handle volume change."""
        self.volume_label.setText(f"{value}%")
        self.volume_changed.emit(value)

    def set_playing(self, is_playing: bool):
        """Update UI for playing state."""
        self.play_btn.setEnabled(not is_playing)
        self.pause_btn.setEnabled(is_playing)
        self.stop_btn.setEnabled(is_playing)

    def set_speed(self, speed: float):
        """Set speed combo box."""
        self.speed_combo.setCurrentText(f"{speed}x")

    def set_volume(self, volume: int):
        """Set volume slider."""
        self.volume_slider.setValue(volume)
```

**Step 2: Update main_window.py to integrate TTS**

Add imports:
```python
from src.ui.toolbar import TTSToolbar
from src.tts import TTSEngine, TTSHighlighter
from src.markdown.renderer import MarkdownRenderer, extract_plain_text
```

Update `_setup_components`:
```python
def _setup_components(self):
    """Initialize main components."""
    self.sidebar = SidebarWidget()
    self.editor = EditorWidget()
    self.viewer = ViewerWidget()
    self.toolbar = TTSToolbar()
    self.renderer = MarkdownRenderer(
        highlight_config=dict(self.config.highlight)
    )
    self.tts_engine = TTSEngine(
        speech_key=self.config.azure.speech_key,
        speech_region=self.config.azure.speech_region,
    )
    self.tts_engine.set_voice(self.config.azure.default_voice)
    self.tts_engine.set_rate(self.config.playback.speed)
    self.tts_engine.set_volume(self.config.playback.volume)
    self.highlighter = None
    self.plain_text = ""
```

Add toolbar setup after menu bar:
```python
def _setup_toolbar(self):
    """Set up TTS toolbar."""
    self.addToolBar(self.toolbar)
    self.toolbar.setVisible(self.config.ui.toolbar_visible)
    self.toolbar.set_speed(self.config.playback.speed)
    self.toolbar.set_volume(self.config.playback.volume)
```

Call `_setup_toolbar()` in `__init__` after `_setup_menu_bar()`.

Update `_connect_signals`:
```python
def _connect_signals(self):
    """Connect widget signals."""
    self.editor.text_modified.connect(self._on_text_modified)
    self.viewer.sentence_clicked.connect(self._on_sentence_clicked)
    self.sidebar.file_selected.connect(self.open_file)
    self.toggle_sidebar_action.triggered.connect(self._toggle_sidebar)
    self.toggle_toolbar_action.triggered.connect(self._toggle_toolbar)

    # TTS toolbar signals
    self.toolbar.play_clicked.connect(self._tts_play)
    self.toolbar.pause_clicked.connect(self._tts_pause)
    self.toolbar.stop_clicked.connect(self._tts_stop)
    self.toolbar.speed_changed.connect(self._tts_set_speed)
    self.toolbar.volume_changed.connect(self._tts_set_volume)

    # TTS engine signals
    self.tts_engine.word_boundary.connect(self._on_word_boundary)
    self.tts_engine.playback_finished.connect(self._on_playback_finished)
    self.tts_engine.error_occurred.connect(self._on_tts_error)

    # Menu TTS actions
    self.play_action.triggered.connect(self._tts_play)
    self.pause_action.triggered.connect(self._tts_pause)
    self.stop_action.triggered.connect(self._tts_stop)
```

Add TTS methods:
```python
def _toggle_toolbar(self):
    """Toggle toolbar visibility."""
    visible = not self.toolbar.isVisible()
    self.toolbar.setVisible(visible)
    self.toggle_toolbar_action.setChecked(visible)
    self.config.ui.toolbar_visible = visible

def _tts_play(self):
    """Start TTS playback."""
    if self.current_mode == self.EDIT_MODE:
        self.toggle_mode()  # Switch to render mode

    self.plain_text = extract_plain_text(self.editor.get_text())
    if not self.plain_text.strip():
        self.status_bar.showMessage("No content to read")
        return

    self.highlighter = TTSHighlighter(self.plain_text)
    self.tts_engine.play(self.plain_text)
    self.toolbar.set_playing(True)

def _tts_pause(self):
    """Pause TTS playback."""
    self.tts_engine.pause()
    self.toolbar.set_playing(False)

def _tts_stop(self):
    """Stop TTS playback."""
    self.tts_engine.stop()
    self.toolbar.set_playing(False)
    self.viewer.clear_highlights()

def _tts_set_speed(self, speed: float):
    """Set TTS playback speed."""
    self.tts_engine.set_rate(speed)
    self.config.playback.speed = speed

def _tts_set_volume(self, volume: int):
    """Set TTS volume."""
    self.tts_engine.set_volume(volume)
    self.config.playback.volume = volume

def _on_word_boundary(self, start: int, end: int):
    """Handle word boundary event from TTS."""
    if self.highlighter:
        sentence_idx = self.highlighter.get_sentence_for_offset(start)
        self.viewer.highlight_sentence(sentence_idx)
        self.viewer.highlight_word(start)

def _on_playback_finished(self):
    """Handle TTS playback finished."""
    self.toolbar.set_playing(False)
    self.viewer.clear_highlights()
    self.status_bar.showMessage("Playback finished")

def _on_tts_error(self, error: str):
    """Handle TTS error."""
    self.toolbar.set_playing(False)
    QMessageBox.warning(self, "TTS Error", error)

def _on_sentence_clicked(self, sentence_idx: int):
    """Handle sentence click in viewer - jump TTS to that sentence."""
    if self.highlighter and self.tts_engine.is_playing:
        text_from_sentence = self.highlighter.get_text_from_sentence(sentence_idx)
        self.tts_engine.stop()
        self.highlighter = TTSHighlighter(text_from_sentence)
        self.tts_engine.play(text_from_sentence)
        self.toolbar.set_playing(True)
```

Add Ctrl+P shortcut for jump-to-position:
```python
# In _setup_menu_bar, after toggle_mode_action:
self.jump_to_position_action = QAction("&Jump to Reading Position", self)
self.jump_to_position_action.setShortcut("Ctrl+P")
self.jump_to_position_action.triggered.connect(self._jump_to_reading_position)
view_menu.addAction(self.jump_to_position_action)

# Add method:
def _jump_to_reading_position(self):
    """Jump to current reading position and enable auto-scroll."""
    if self.highlighter:
        self.viewer.scroll_to_sentence(self.highlighter.current_sentence_idx)
```

**Step 3: Update src/ui/__init__.py**

```python
"""UI components package."""
from src.ui.main_window import MainWindow
from src.ui.editor import EditorWidget
from src.ui.viewer import ViewerWidget
from src.ui.sidebar import SidebarWidget
from src.ui.toolbar import TTSToolbar

__all__ = ["MainWindow", "EditorWidget", "ViewerWidget", "SidebarWidget", "TTSToolbar"]
```

**Step 4: Run and verify**

Run: `python main.py`
Expected:
- Toolbar hidden by default (toggle via View menu)
- Play/Pause/Stop buttons work
- Speed dropdown changes rate
- Volume slider adjusts volume
- TTS highlights current sentence/word during playback

**Step 5: Commit**

```bash
git add src/ui/toolbar.py src/ui/main_window.py src/ui/__init__.py
git commit -m "feat: add TTS toolbar with playback controls"
```

---

## Task 12: Voice Selection Menu

**Files:**
- Modify: `src/ui/main_window.py`

**Step 1: Add voice menu population**

In `_setup_menu_bar`, after creating `self.voice_menu`:

```python
# Populate voice menu
self._populate_voice_menu()
self._populate_speed_menu()
self._populate_volume_menu()
```

Add methods:
```python
def _populate_voice_menu(self):
    """Populate voice selection menu."""
    voices = self.tts_engine.get_available_voices()
    for voice in voices:
        action = QAction(voice, self)
        action.setCheckable(True)
        action.setChecked(voice == self.config.azure.default_voice)
        action.triggered.connect(lambda checked, v=voice: self._set_voice(v))
        self.voice_menu.addAction(action)

def _populate_speed_menu(self):
    """Populate speed menu."""
    speeds = [0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
    for speed in speeds:
        action = QAction(f"{speed}x", self)
        action.setCheckable(True)
        action.setChecked(speed == self.config.playback.speed)
        action.triggered.connect(lambda checked, s=speed: self._menu_set_speed(s))
        self.speed_menu.addAction(action)

def _populate_volume_menu(self):
    """Populate volume menu."""
    volumes = [0, 25, 50, 75, 100]
    for vol in volumes:
        action = QAction(f"{vol}%", self)
        action.setCheckable(True)
        action.setChecked(vol == self.config.playback.volume)
        action.triggered.connect(lambda checked, v=vol: self._menu_set_volume(v))
        self.volume_menu.addAction(action)

def _set_voice(self, voice: str):
    """Set TTS voice."""
    self.tts_engine.set_voice(voice)
    self.config.azure.default_voice = voice
    # Update checkmarks
    for action in self.voice_menu.actions():
        action.setChecked(action.text() == voice)

def _menu_set_speed(self, speed: float):
    """Set speed from menu."""
    self._tts_set_speed(speed)
    self.toolbar.set_speed(speed)
    # Update checkmarks
    for action in self.speed_menu.actions():
        action.setChecked(action.text() == f"{speed}x")

def _menu_set_volume(self, volume: int):
    """Set volume from menu."""
    self._tts_set_volume(volume)
    self.toolbar.set_volume(volume)
    # Update checkmarks
    for action in self.volume_menu.actions():
        action.setChecked(action.text() == f"{volume}%")
```

**Step 2: Run and verify**

Run: `python main.py`
Expected:
- Text-to-Speech > Voice shows list of voices with checkmark on current
- Text-to-Speech > Speed shows speed options
- Text-to-Speech > Volume shows volume options

**Step 3: Commit**

```bash
git add src/ui/main_window.py
git commit -m "feat: add voice/speed/volume selection menus"
```

---

## Task 13: Final Polish

**Files:**
- Modify: `src/ui/main_window.py`
- Update: `config.yaml` if needed

**Step 1: Add empty document handling**

Update `_tts_play`:
```python
def _tts_play(self):
    """Start TTS playback."""
    if self.current_mode == self.EDIT_MODE:
        self.toggle_mode()  # Switch to render mode

    self.plain_text = extract_plain_text(self.editor.get_text())
    if not self.plain_text.strip():
        self.status_bar.showMessage("No content to read")
        QMessageBox.information(self, "TTS", "No content to read")
        return

    if not self.tts_engine.is_configured():
        QMessageBox.warning(
            self,
            "TTS Not Configured",
            "Azure TTS is not configured.\nPlease add your speech_key to config.yaml"
        )
        return

    self.highlighter = TTSHighlighter(self.plain_text)
    self.tts_engine.play(self.plain_text)
    self.toolbar.set_playing(True)
```

**Step 2: Handle mode switch during playback**

Update `toggle_mode`:
```python
def toggle_mode(self):
    """Toggle between edit and render mode."""
    if self.current_mode == self.EDIT_MODE:
        # Switch to render mode
        html = self.renderer.render(self.editor.get_text())
        self.viewer.set_html(html)
        self.content_stack.setCurrentIndex(self.RENDER_MODE)
        self.current_mode = self.RENDER_MODE
        self._set_edit_actions_enabled(False)
    else:
        # Switch to edit mode - pause TTS if playing
        if self.tts_engine.is_playing:
            self._tts_pause()
        self.content_stack.setCurrentIndex(self.EDIT_MODE)
        self.current_mode = self.EDIT_MODE
        self._set_edit_actions_enabled(True)

    self._update_status()
```

**Step 3: Add pytest-qt to requirements**

Update `requirements.txt`:
```txt
PySide6>=6.5.0
PySide6-WebEngine>=6.5.0
omegaconf>=2.3.0
azure-cognitiveservices-speech>=1.30.0
markdown>=3.5.0
Pygments>=2.17.0
pytest>=7.0.0
pytest-qt>=4.2.0
```

**Step 4: Run all tests**

Run: `pytest tests/ -v`
Expected: All tests PASS

**Step 5: Run application and verify all features**

Run: `python main.py`

Verify:
- [ ] Window opens with correct size from config
- [ ] Sidebar shows folder tree when folder opened
- [ ] Ctrl+I toggles edit/render mode
- [ ] Ctrl+S saves file
- [ ] Ctrl+P jumps to reading position
- [ ] TTS Play/Pause/Stop work
- [ ] Word and sentence highlighting during TTS
- [ ] Click sentence to jump TTS
- [ ] Drag-drop files/folders
- [ ] Recent files menu
- [ ] Voice/Speed/Volume menus

**Step 6: Commit**

```bash
git add .
git commit -m "feat: complete Typora TTS app with all features"
```

---

## Summary

| Task | Description | Files |
|------|-------------|-------|
| 1 | Project Setup | main.py, requirements.txt, src/__init__.py |
| 2 | Configuration | src/config.py, config.yaml, tests/test_config.py |
| 3 | Main Window Shell | src/ui/main_window.py |
| 4 | Editor Widget | src/ui/editor.py |
| 5 | Markdown Renderer | src/markdown/renderer.py |
| 6 | Viewer Widget | src/ui/viewer.py |
| 7 | Edit/Render Toggle | src/ui/main_window.py |
| 8 | Sidebar File Tree | src/ui/sidebar.py |
| 9 | TTS Engine | src/tts/engine.py |
| 10 | TTS Highlighter | src/tts/highlighter.py |
| 11 | TTS Toolbar | src/ui/toolbar.py |
| 12 | Voice Selection | src/ui/main_window.py |
| 13 | Final Polish | various |

Total: ~13 tasks, each with 5-6 steps following TDD principles.
