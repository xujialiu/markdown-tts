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
