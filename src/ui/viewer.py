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
