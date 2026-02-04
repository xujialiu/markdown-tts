"""Sidebar widget with file tree for folder navigation."""
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTreeView,
    QLabel,
    QHeaderView,
    QFileSystemModel,
)
from PySide6.QtCore import Signal, QDir, QModelIndex


class SidebarWidget(QWidget):
    """Sidebar with file tree for navigating markdown files."""

    file_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_folder: Path | None = None
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Set up the sidebar UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header label showing folder name
        self.header_label = QLabel("No folder open")
        self.header_label.setStyleSheet(
            "QLabel { padding: 8px; background-color: #f0f0f0; "
            "font-weight: bold; border-bottom: 1px solid #ccc; }"
        )
        layout.addWidget(self.header_label)

        # File system model
        self.model = QFileSystemModel()
        self.model.setReadOnly(True)
        # Filter to show only .md and .markdown files
        self.model.setNameFilters(["*.md", "*.markdown"])
        self.model.setNameFilterDisables(False)  # Hide non-matching files

        # Tree view
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.model)
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setAnimated(True)
        self.tree_view.setIndentation(20)

        # Hide all columns except name
        self.tree_view.setColumnHidden(1, True)  # Size
        self.tree_view.setColumnHidden(2, True)  # Type
        self.tree_view.setColumnHidden(3, True)  # Date Modified

        # Configure header
        header = self.tree_view.header()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.tree_view)

    def _connect_signals(self):
        """Connect internal signals."""
        self.tree_view.doubleClicked.connect(self._on_item_double_clicked)
        self.tree_view.clicked.connect(self._on_item_clicked)

    def _on_item_clicked(self, index: QModelIndex):
        """Handle single click on tree item."""
        file_path = self.model.filePath(index)
        if file_path and not self.model.isDir(index):
            # Emit file_selected for single click
            self.file_selected.emit(file_path)

    def _on_item_double_clicked(self, index: QModelIndex):
        """Handle double click on tree item."""
        file_path = self.model.filePath(index)
        if file_path and not self.model.isDir(index):
            self.file_selected.emit(file_path)

    def set_folder(self, folder_path: str | Path) -> None:
        """Set the root directory for the file tree.

        Args:
            folder_path: Path to the folder to display.
        """
        folder_path = Path(folder_path)
        if not folder_path.exists() or not folder_path.is_dir():
            return

        self._current_folder = folder_path
        self.header_label.setText(folder_path.name)

        # Set root path for the model
        root_index = self.model.setRootPath(str(folder_path))
        self.tree_view.setRootIndex(root_index)

    def get_current_folder(self) -> Path | None:
        """Get the currently displayed folder.

        Returns:
            Path to current folder or None if no folder is set.
        """
        return self._current_folder

    def clear(self):
        """Clear the file tree and reset to initial state."""
        self._current_folder = None
        self.header_label.setText("No folder open")
        # Reset to empty root
        self.model.setRootPath("")
        self.tree_view.setRootIndex(QModelIndex())
