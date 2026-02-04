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
