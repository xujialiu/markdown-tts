"""Tests for sidebar widget."""
import pytest
import tempfile
from pathlib import Path
from PySide6.QtWidgets import QApplication


# Ensure QApplication exists for widget tests
@pytest.fixture(scope="module")
def app():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture
def temp_folder():
    """Create a temporary folder with markdown files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create some markdown files
        (Path(tmpdir) / "test1.md").write_text("# Test 1")
        (Path(tmpdir) / "test2.markdown").write_text("# Test 2")
        (Path(tmpdir) / "readme.txt").write_text("Not markdown")
        # Create a subdirectory with markdown
        subdir = Path(tmpdir) / "subdir"
        subdir.mkdir()
        (subdir / "nested.md").write_text("# Nested")
        yield tmpdir


def test_sidebar_widget_exists(app):
    from src.ui.sidebar import SidebarWidget
    sidebar = SidebarWidget()
    assert sidebar is not None


def test_sidebar_has_tree_view(app):
    from src.ui.sidebar import SidebarWidget
    sidebar = SidebarWidget()
    assert sidebar.tree_view is not None
    assert sidebar.model is not None


def test_sidebar_has_header_label(app):
    from src.ui.sidebar import SidebarWidget
    sidebar = SidebarWidget()
    assert sidebar.header_label is not None
    assert sidebar.header_label.text() == "No folder open"


def test_sidebar_set_folder(app, temp_folder):
    from src.ui.sidebar import SidebarWidget
    sidebar = SidebarWidget()
    sidebar.set_folder(temp_folder)

    folder_name = Path(temp_folder).name
    assert sidebar.header_label.text() == folder_name
    assert sidebar.get_current_folder() == Path(temp_folder)


def test_sidebar_set_folder_with_path_object(app, temp_folder):
    from src.ui.sidebar import SidebarWidget
    sidebar = SidebarWidget()
    sidebar.set_folder(Path(temp_folder))

    folder_name = Path(temp_folder).name
    assert sidebar.header_label.text() == folder_name


def test_sidebar_clear(app, temp_folder):
    from src.ui.sidebar import SidebarWidget
    sidebar = SidebarWidget()
    sidebar.set_folder(temp_folder)
    sidebar.clear()

    assert sidebar.header_label.text() == "No folder open"
    assert sidebar.get_current_folder() is None


def test_sidebar_emits_file_selected_signal(app, temp_folder):
    from src.ui.sidebar import SidebarWidget
    sidebar = SidebarWidget()
    sidebar.set_folder(temp_folder)

    # Test that the signal can be connected and emitted
    received_paths = []

    def on_file_selected(path):
        received_paths.append(path)

    sidebar.file_selected.connect(on_file_selected)
    test_path = str(Path(temp_folder) / "test1.md")
    sidebar.file_selected.emit(test_path)

    assert len(received_paths) == 1
    assert received_paths[0] == test_path


def test_sidebar_ignores_invalid_folder(app):
    from src.ui.sidebar import SidebarWidget
    sidebar = SidebarWidget()
    sidebar.set_folder("/nonexistent/path/that/does/not/exist")

    assert sidebar.header_label.text() == "No folder open"
    assert sidebar.get_current_folder() is None


def test_sidebar_model_filters_markdown(app, temp_folder):
    from src.ui.sidebar import SidebarWidget
    sidebar = SidebarWidget()

    # Check name filters are set correctly
    filters = sidebar.model.nameFilters()
    assert "*.md" in filters
    assert "*.markdown" in filters


def test_sidebar_exported_from_package(app):
    from src.ui import SidebarWidget
    sidebar = SidebarWidget()
    assert sidebar is not None
