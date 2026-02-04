# Typora TTS App - Design Document

**Date:** 2026-02-04
**Status:** Approved

## Overview

A Markdown editor with text-to-speech capabilities, similar to Typora but with integrated Azure TTS for reading documents aloud with real-time word and sentence highlighting.

## Technology Stack

| Component | Technology |
|-----------|------------|
| GUI Framework | PySide6 |
| Markdown Rendering | markdown + Pygments |
| HTML Display | QWebEngineView |
| TTS | Azure Cognitive Services Speech |
| Config | OmegaConf (YAML) |
| File Tree | QFileSystemModel + QTreeView |
| Environment | Conda (ves_anno) |

## Project Structure

```
typora_tts_app/
├── main.py                 # Entry point
├── config.yaml             # Azure credentials & settings
├── requirements.txt        # Dependencies
│
├── src/
│   ├── __init__.py
│   ├── app.py              # QApplication setup, main window
│   ├── config.py           # OmegaConf loader/saver
│   │
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_window.py  # Main window with menu bar
│   │   ├── sidebar.py      # Folder tree view
│   │   ├── editor.py       # QPlainTextEdit for editing
│   │   ├── viewer.py       # QWebEngineView for rendering
│   │   └── toolbar.py      # TTS controls toolbar
│   │
│   ├── markdown/
│   │   ├── __init__.py
│   │   └── renderer.py     # Markdown → HTML conversion
│   │
│   └── tts/
│       ├── __init__.py
│       ├── engine.py       # Azure TTS wrapper
│       └── highlighter.py  # Sentence/word tracking & highlighting
│
└── resources/
    └── styles/
        └── markdown.css    # Styling for rendered markdown
```

## UI Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  File   Edit   View   Text-to-Speech   Help         [Menu Bar] │
├─────────────────────────────────────────────────────────────────┤
│  [▶] [⏸] [⏹]  |  Speed: [1.0x ▼]  |  Vol: [━━━●━]   [Toolbar]  │
├──────────────┬──────────────────────────────────────────────────┤
│              │                                                  │
│  📁 docs     │   # My Document                                  │
│  ├── api.md  │                                                  │
│  └── guide.md│   This is a paragraph with **bold** text.       │
│  📁 notes    │                                                  │
│  └── todo.md │   - Item one                                     │
│              │   - Item two                                     │
│   [Sidebar]  │                                     [Editor/Viewer]│
│              │                                                  │
└──────────────┴──────────────────────────────────────────────────┘
```

### Menu Structure

- **File:** Open File, Open Folder, Recent Files ▶, Save, Exit
- **Edit:** Undo, Redo, Cut, Copy, Paste (disabled in render mode)
- **View:** Toggle Sidebar, Toggle Toolbar
- **Text-to-Speech:** Play, Pause, Stop, separator, Voice ▶ (submenu), Speed ▶, Volume ▶
- **Help:** About

### Toolbar

- Play, Pause, Stop buttons
- Speed dropdown (0.5x - 2.0x)
- Volume slider
- Hidden by default, toggle via View menu

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+S | Save file to disk |
| Ctrl+I | Toggle between edit and render mode |
| Ctrl+P | Jump to current reading position & re-enable auto-scroll |

## Edit/Render Mode

**State machine:**
```
          Ctrl+I              Ctrl+I
  [EDIT] ────────▶ [RENDER] ────────▶ [EDIT]
     │                 │
     │                 ├── TTS can play
     │                 ├── Click sentence to jump
     │                 └── Read-only
     │
     ├── Text editable
     ├── TTS pauses (if playing)
     └── Plain text editing
```

**Implementation:**
- QStackedWidget containing EditorWidget and ViewerWidget
- On Ctrl+I (Edit → Render): Convert markdown to HTML, inject CSS/JS, load into viewer
- On Ctrl+I (Render → Edit): Pause TTS if playing, switch back to editor

## TTS Engine

### Azure Integration

- Initialize SpeechSynthesizer with config (key, region, voice)
- Methods: `play(text)`, `pause()`, `resume()`, `stop()`
- Signals: `word_boundary(start, end)`, `sentence_started(index)`, `playback_finished()`
- Voice listing: `get_available_voices()` → list of voice names

### Playback Controls

- **Speed:** Azure SSML `<prosody rate="1.2">` wrapper (range: 0.5x - 2.0x)
- **Volume:** Azure SSML `<prosody volume>` or local audio control

### Playback Flow

1. User clicks Play
2. Extract plain text from markdown (strip formatting)
3. Pass to Azure TTS
4. Azure streams audio + emits word boundaries
5. Highlighter receives boundaries → updates CSS classes via JavaScript
6. QWebEngineView executes JS to add/remove highlight classes

## Highlighting System

### CSS Classes (colors from config.yaml)

```css
.current-sentence {
    background-color: [config.highlight.sentence_color];
    opacity: [config.highlight.sentence_opacity];
}
.current-word {
    background-color: [config.highlight.word_color];
    opacity: [config.highlight.word_opacity];
}
```

### HTML Structure

- Each sentence wrapped in `<span data-sentence="0">`
- Each word wrapped in `<span data-word="42">` with character offset

### JavaScript Bridge

Embedded JavaScript (30-40 lines) handles:
- Highlight updates via `runJavaScript()` calls from Python
- Scroll detection to disable auto-scroll when user scrolls
- Click detection to capture sentence clicks and signal Python
- Smooth scrolling via `scrollIntoView()`

Communication via QWebChannel (PySide6's JS↔Python bridge).

## Auto-scroll Behavior

- `autoScrollEnabled = True` by default
- On user scroll event (detected via JS): set `autoScrollEnabled = False`
- On Ctrl+P: set `autoScrollEnabled = True`, scroll to current sentence
- Scroll uses `element.scrollIntoView({ behavior: 'smooth', block: 'center' })`

## Click-to-Jump

- Each sentence span has click handler
- Click → get `data-sentence` index → signal to Python
- Python stops current TTS, restarts synthesis from clicked sentence
- Note: Azure TTS doesn't support seeking mid-stream, so restart is required

## File Handling

### Open Methods

- File menu: Open File, Open Folder
- Drag-drop: Files and folders onto window
- Recent Files: Submenu with last 10 opened files

### Sidebar (QTreeView + QFileSystemModel)

- Shows folder structure with only `.md` and `.markdown` files
- Click file to open in editor
- System default folder/file icons

### Drag-Drop Support

```python
def dropEvent(self, event):
    for url in event.mimeData().urls():
        path = url.toLocalFile()
        if path.endswith('.md'):
            self.open_file(path)
        elif os.path.isdir(path):
            self.open_folder(path)
```

## Configuration (config.yaml)

```yaml
azure:
  speech_key: "your-key-here"
  speech_region: "eastus"
  default_voice: "en-US-JennyNeural"

playback:
  speed: 1.0          # 0.5 - 2.0
  volume: 100         # 0 - 100

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

### Config Handling

- Loaded at app start with defaults merged
- Saved on: app close, settings change, window resize
- Missing keys fall back to defaults (OmegaConf merge)
- Path: `./config.yaml` (same directory as main.py)

## Markdown Rendering

### Libraries

- **markdown (Python-Markdown):** Core conversion with extensions
- **Pygments:** Syntax highlighting for code blocks
- **Extensions:** tables, footnotes, codehilite, toc, nl2br, sane_lists

### Supported Elements

- Headings, bold, italic, strikethrough
- Lists (ordered, unordered, checkboxes)
- Links, images
- Code blocks with syntax highlighting
- Tables
- Blockquotes
- Horizontal rules
- Footnotes

## Error Handling

### Azure TTS Errors

- **Missing/invalid credentials:** Dialog on first Play: "Azure credentials not configured"
- **Network failure:** Status bar message, stop playback gracefully
- **Voice not found:** Fall back to first available voice

### File Operations

- **File not found (recent):** Remove from list silently
- **Permission denied:** Show dialog
- **Unsaved changes on close:** Prompt Save/Don't Save/Cancel

### Playback Edge Cases

- **Empty document:** Disable Play button
- **Switch to edit while playing:** Pause TTS, resume on return
- **Click sentence while paused:** Jump to sentence, remain paused

### Config Errors

- **Malformed YAML:** Use defaults, show warning
- **Missing config.yaml:** Create with defaults

## Dependencies

```
PySide6>=6.5.0
PySide6-WebEngine>=6.5.0
omegaconf>=2.3.0
azure-cognitiveservices-speech>=1.30.0
markdown>=3.5.0
Pygments>=2.17.0
```

## Setup

```bash
conda activate ves_anno
pip install -r requirements.txt
python main.py
```
