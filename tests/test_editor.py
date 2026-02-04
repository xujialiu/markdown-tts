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
