"""Main application window."""
from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow,
    QMenuBar,
    QStatusBar,
    QStackedWidget,
    QFileDialog,
    QMessageBox,
)
from PySide6.QtGui import QAction, QKeySequence, QDragEnterEvent, QDropEvent
from PySide6.QtCore import Qt

from src.config import load_config, save_config
from src.ui.editor import EditorWidget
from src.ui.viewer import ViewerWidget
from src.markdown.renderer import MarkdownRenderer


class MainWindow(QMainWindow):
    """Main application window with menu bar and status bar."""

    # Mode constants
    MODE_EDIT = 0
    MODE_VIEW = 1

    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.current_file: Path | None = None
        self.is_modified = False
        self._setup_window()
        self._setup_renderer()
        self._setup_central_widget()
        self._setup_menu_bar()
        self._setup_status_bar()
        self._connect_signals()

    def _setup_window(self):
        """Configure window properties."""
        self.setWindowTitle("Typora TTS")
        self.resize(
            self.config.ui.window_width,
            self.config.ui.window_height,
        )
        # Enable drag-drop
        self.setAcceptDrops(True)

    def _setup_renderer(self):
        """Initialize the markdown renderer."""
        self.renderer = MarkdownRenderer(self.config.highlight)

    def _setup_central_widget(self):
        """Set up QStackedWidget with editor and viewer."""
        self.stack = QStackedWidget()

        # Create editor widget (index 0)
        self.editor = EditorWidget()
        self.stack.addWidget(self.editor)

        # Create viewer widget (index 1)
        self.viewer = ViewerWidget()
        self.stack.addWidget(self.viewer)

        # Start in edit mode
        self.stack.setCurrentIndex(self.MODE_EDIT)
        self.setCentralWidget(self.stack)

    def _setup_menu_bar(self):
        """Create menu bar with all menus."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        self.open_file_action = QAction("&Open File...", self)
        self.open_file_action.setShortcut(QKeySequence.Open)
        file_menu.addAction(self.open_file_action)

        open_folder_action = QAction("Open &Folder...", self)
        file_menu.addAction(open_folder_action)

        self.recent_menu = file_menu.addMenu("&Recent Files")

        file_menu.addSeparator()

        self.save_action = QAction("&Save", self)
        self.save_action.setShortcut(QKeySequence.Save)
        file_menu.addAction(self.save_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")

        undo_action = QAction("&Undo", self)
        undo_action.setShortcut(QKeySequence.Undo)
        undo_action.triggered.connect(self.editor.undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction("&Redo", self)
        redo_action.setShortcut(QKeySequence.Redo)
        redo_action.triggered.connect(self.editor.redo)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        cut_action = QAction("Cu&t", self)
        cut_action.setShortcut(QKeySequence.Cut)
        cut_action.triggered.connect(self.editor.cut)
        edit_menu.addAction(cut_action)

        copy_action = QAction("&Copy", self)
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.triggered.connect(self.editor.copy)
        edit_menu.addAction(copy_action)

        paste_action = QAction("&Paste", self)
        paste_action.setShortcut(QKeySequence.Paste)
        paste_action.triggered.connect(self.editor.paste)
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

        self.toggle_mode_action = QAction("Toggle &Edit/Render Mode", self)
        self.toggle_mode_action.setShortcut("Ctrl+I")
        view_menu.addAction(self.toggle_mode_action)

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
        self._update_status_bar()

    def _connect_signals(self):
        """Connect signals to handlers."""
        # Menu actions
        self.open_file_action.triggered.connect(self.open_file_dialog)
        self.save_action.triggered.connect(self.save_file)
        self.toggle_mode_action.triggered.connect(self.toggle_mode)

        # Editor modifications
        self.editor.text_modified.connect(self._on_text_modified)

    def _on_text_modified(self):
        """Handle editor text modifications."""
        self.is_modified = True
        self._update_window_title()

    def _update_window_title(self):
        """Update window title with file name and modified indicator."""
        title = "Typora TTS"
        if self.current_file:
            title = f"{self.current_file.name} - {title}"
        if self.is_modified:
            title = f"*{title}"
        self.setWindowTitle(title)

    def _update_status_bar(self):
        """Update status bar with current mode."""
        current_mode = self.stack.currentIndex()
        if current_mode == self.MODE_EDIT:
            mode_text = "Edit Mode"
        else:
            mode_text = "Render Mode"
        self.status_bar.showMessage(f"{mode_text} | Press Ctrl+I to toggle")

    def toggle_mode(self):
        """Toggle between edit and render mode."""
        current_mode = self.stack.currentIndex()

        if current_mode == self.MODE_EDIT:
            # Switch to view mode - render the markdown
            markdown_text = self.editor.get_text()
            html = self.renderer.render(markdown_text)
            self.viewer.set_html(html)
            self.stack.setCurrentIndex(self.MODE_VIEW)
        else:
            # Switch back to edit mode
            self.stack.setCurrentIndex(self.MODE_EDIT)
            self.editor.setFocus()

        self._update_status_bar()

    def open_file(self, file_path: Path) -> bool:
        """Open a file and load its content.

        Args:
            file_path: Path to the file to open.

        Returns:
            True if file was opened successfully, False otherwise.
        """
        try:
            content = file_path.read_text(encoding="utf-8")
            self.editor.set_text(content)
            self.current_file = file_path
            self.is_modified = False
            self._update_window_title()

            # Switch to edit mode
            self.stack.setCurrentIndex(self.MODE_EDIT)
            self._update_status_bar()

            self.status_bar.showMessage(f"Opened: {file_path}", 3000)
            return True
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Opening File",
                f"Could not open file:\n{file_path}\n\nError: {e}",
            )
            return False

    def save_file(self) -> bool:
        """Save the current file.

        Returns:
            True if file was saved successfully, False otherwise.
        """
        if not self.current_file:
            return self._save_file_as()

        try:
            content = self.editor.get_text()
            self.current_file.write_text(content, encoding="utf-8")
            self.is_modified = False
            self._update_window_title()
            self.status_bar.showMessage(f"Saved: {self.current_file}", 3000)
            return True
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Saving File",
                f"Could not save file:\n{self.current_file}\n\nError: {e}",
            )
            return False

    def _save_file_as(self) -> bool:
        """Show save dialog and save file.

        Returns:
            True if file was saved successfully, False otherwise.
        """
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File",
            str(self.config.recent.last_folder or Path.home()),
            "Markdown Files (*.md *.markdown);;All Files (*)",
        )

        if not file_path:
            return False

        self.current_file = Path(file_path)
        return self.save_file()

    def open_file_dialog(self):
        """Show open file dialog and open selected file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            str(self.config.recent.last_folder or Path.home()),
            "Markdown Files (*.md *.markdown);;All Files (*)",
        )

        if file_path:
            path = Path(file_path)
            self.config.recent.last_folder = str(path.parent)
            self.open_file(path)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event for file drops."""
        if event.mimeData().hasUrls():
            # Accept if any URL is a markdown file
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    path = Path(url.toLocalFile())
                    if path.suffix.lower() in (".md", ".markdown", ".txt"):
                        event.acceptProposedAction()
                        return
        event.ignore()

    def dropEvent(self, event: QDropEvent):
        """Handle drop event for file drops."""
        for url in event.mimeData().urls():
            if url.isLocalFile():
                path = Path(url.toLocalFile())
                if path.suffix.lower() in (".md", ".markdown", ".txt"):
                    self.open_file(path)
                    event.acceptProposedAction()
                    return
        event.ignore()

    def closeEvent(self, event):
        """Save config on close, with unsaved changes prompt."""
        if self.is_modified:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save before exiting?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save,
            )

            if reply == QMessageBox.Save:
                if not self.save_file():
                    event.ignore()
                    return
            elif reply == QMessageBox.Cancel:
                event.ignore()
                return

        # Save window size
        self.config.ui.window_width = self.width()
        self.config.ui.window_height = self.height()
        save_config(self.config)
        event.accept()
