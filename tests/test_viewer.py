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
