"""Main application window."""
from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow,
    QMenuBar,
    QStatusBar,
    QStackedWidget,
    QFileDialog,
    QMessageBox,
    QSplitter,
)
from PySide6.QtGui import QAction, QActionGroup, QKeySequence, QDragEnterEvent, QDropEvent
from PySide6.QtCore import Qt

from src.config import load_config, save_config
from src.ui.editor import EditorWidget
from src.ui.viewer import ViewerWidget
from src.ui.sidebar import SidebarWidget
from src.ui.toolbar import TTSToolbar
from src.markdown.renderer import MarkdownRenderer, extract_plain_text
from src.tts import TTSEngine, TTSHighlighter


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
        self._setup_tts_engine()
        self._setup_central_widget()
        self._setup_toolbar()
        self._setup_menu_bar()
        self._populate_tts_menus()
        self._setup_status_bar()
        self._connect_signals()
        self._connect_tts_signals()

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

    def _setup_tts_engine(self):
        """Initialize the TTS engine and highlighter."""
        self.tts_engine = TTSEngine(
            speech_key=self.config.azure.speech_key,
            speech_region=self.config.azure.speech_region,
            parent=self,
        )
        self.tts_engine.set_voice(self.config.azure.default_voice)
        self.tts_engine.set_rate(self.config.playback.speed)
        self.tts_engine.set_volume(self.config.playback.volume)

        # Highlighter will be created when text is loaded
        self.tts_highlighter: TTSHighlighter | None = None
        self._tts_plain_text: str = ""

    def _setup_central_widget(self):
        """Set up splitter with sidebar and content stack."""
        # Main splitter to hold sidebar and content
        self.main_splitter = QSplitter(Qt.Horizontal)

        # Create sidebar
        self.sidebar = SidebarWidget()
        self.sidebar.setVisible(self.config.ui.sidebar_visible)
        self.main_splitter.addWidget(self.sidebar)

        # Content stack (editor and viewer)
        self.stack = QStackedWidget()

        # Create editor widget (index 0)
        self.editor = EditorWidget()
        self.stack.addWidget(self.editor)

        # Create viewer widget (index 1)
        self.viewer = ViewerWidget()
        self.stack.addWidget(self.viewer)

        # Start in edit mode
        self.stack.setCurrentIndex(self.MODE_EDIT)
        self.main_splitter.addWidget(self.stack)

        # Set initial splitter sizes
        sidebar_width = self.config.ui.sidebar_width
        content_width = self.config.ui.window_width - sidebar_width
        self.main_splitter.setSizes([sidebar_width, content_width])

        self.setCentralWidget(self.main_splitter)

    def _setup_toolbar(self):
        """Set up the TTS toolbar."""
        self.tts_toolbar = TTSToolbar(self)
        self.addToolBar(Qt.TopToolBarArea, self.tts_toolbar)

        # Set initial values from config
        self.tts_toolbar.set_speed(self.config.playback.speed)
        self.tts_toolbar.set_volume(self.config.playback.volume)

        # Set initial visibility from config
        self.tts_toolbar.setVisible(self.config.ui.toolbar_visible)

        # Connect toolbar signals
        self.tts_toolbar.play_clicked.connect(self._tts_play)
        self.tts_toolbar.pause_clicked.connect(self._tts_pause)
        self.tts_toolbar.stop_clicked.connect(self._tts_stop)
        self.tts_toolbar.speed_changed.connect(self._on_tts_speed_changed)
        self.tts_toolbar.volume_changed.connect(self._on_tts_volume_changed)

    def _setup_menu_bar(self):
        """Create menu bar with all menus."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        self.open_file_action = QAction("&Open File...", self)
        self.open_file_action.setShortcut(QKeySequence.Open)
        file_menu.addAction(self.open_file_action)

        self.open_folder_action = QAction("Open &Folder...", self)
        file_menu.addAction(self.open_folder_action)

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

        self.tts_play_action = QAction("&Play", self)
        self.tts_play_action.triggered.connect(self._tts_play)
        tts_menu.addAction(self.tts_play_action)

        self.tts_pause_action = QAction("P&ause", self)
        self.tts_pause_action.triggered.connect(self._tts_pause)
        tts_menu.addAction(self.tts_pause_action)

        self.tts_stop_action = QAction("&Stop", self)
        self.tts_stop_action.triggered.connect(self._tts_stop)
        tts_menu.addAction(self.tts_stop_action)

        tts_menu.addSeparator()

        self.jump_to_position_action = QAction("&Jump to Reading Position", self)
        self.jump_to_position_action.setShortcut("Ctrl+P")
        self.jump_to_position_action.triggered.connect(self.jump_to_reading_position)
        tts_menu.addAction(self.jump_to_position_action)

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
        self.open_folder_action.triggered.connect(self.open_folder_dialog)
        self.save_action.triggered.connect(self.save_file)
        self.toggle_mode_action.triggered.connect(self.toggle_mode)
        self.toggle_sidebar_action.triggered.connect(self.toggle_sidebar)
        self.toggle_toolbar_action.triggered.connect(self.toggle_toolbar)

        # Sidebar signals
        self.sidebar.file_selected.connect(self._on_sidebar_file_selected)

        # Editor modifications
        self.editor.text_modified.connect(self._on_text_modified)

    def _connect_tts_signals(self):
        """Connect TTS engine signals to handlers."""
        self.tts_engine.playback_started.connect(self._on_tts_started)
        self.tts_engine.playback_paused.connect(self._on_tts_paused)
        self.tts_engine.playback_stopped.connect(self._on_tts_stopped)
        self.tts_engine.playback_finished.connect(self._on_tts_finished)
        self.tts_engine.word_boundary.connect(self._on_tts_word_boundary)
        self.tts_engine.error_occurred.connect(self._on_tts_error)

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
            # Pause TTS when switching to edit mode if playing
            if self.tts_engine.is_playing and not self.tts_engine.is_paused:
                self.tts_engine.pause()
                self.status_bar.showMessage("TTS paused (switched to edit mode)", 3000)

            # Switch back to edit mode
            self.stack.setCurrentIndex(self.MODE_EDIT)
            self.editor.setFocus()

        self._update_status_bar()

    def toggle_sidebar(self):
        """Toggle sidebar visibility."""
        is_visible = self.sidebar.isVisible()
        self.sidebar.setVisible(not is_visible)
        self.toggle_sidebar_action.setChecked(not is_visible)

    def toggle_toolbar(self):
        """Toggle TTS toolbar visibility."""
        is_visible = self.tts_toolbar.isVisible()
        self.tts_toolbar.setVisible(not is_visible)
        self.toggle_toolbar_action.setChecked(not is_visible)

    # TTS Control Methods

    def _tts_play(self):
        """Start or resume TTS playback."""
        if self.tts_engine.is_paused:
            self.tts_engine.resume()
            return

        # Check if TTS is configured
        if not self.tts_engine.is_configured():
            QMessageBox.warning(
                self,
                "TTS Not Configured",
                "Text-to-Speech is not configured.\n\n"
                "Please set your Azure Speech Service credentials in config.yaml:\n"
                "- speech_key: Your Azure Speech Service key\n"
                "- speech_region: Your Azure region (e.g., eastus)",
            )
            return

        # Get the markdown text and convert to plain text for TTS
        markdown_text = self.editor.get_text()
        if not markdown_text.strip():
            self.status_bar.showMessage("No content to read", 3000)
            return

        # Extract plain text for TTS
        self._tts_plain_text = extract_plain_text(markdown_text)
        if not self._tts_plain_text.strip():
            self.status_bar.showMessage("No readable text found", 3000)
            return

        # Create highlighter for tracking
        self.tts_highlighter = TTSHighlighter(self._tts_plain_text)

        # Switch to view mode and render
        if self.stack.currentIndex() == self.MODE_EDIT:
            html = self.renderer.render(markdown_text)
            self.viewer.set_html(html)
            self.stack.setCurrentIndex(self.MODE_VIEW)
            self._update_status_bar()

        # Start playback
        if not self.tts_engine.play(self._tts_plain_text):
            self.status_bar.showMessage("Failed to start TTS playback", 3000)

    def _tts_pause(self):
        """Pause TTS playback."""
        self.tts_engine.pause()

    def _tts_stop(self):
        """Stop TTS playback."""
        self.tts_engine.stop()
        # Clear highlights in viewer
        self.viewer.clear_highlights()

    def _on_tts_speed_changed(self, speed: float):
        """Handle speed change from toolbar.

        Args:
            speed: New speed multiplier (0.5 to 2.0).
        """
        self.tts_engine.set_rate(speed)
        self.config.playback.speed = speed

    def _on_tts_volume_changed(self, volume: int):
        """Handle volume change from toolbar.

        Args:
            volume: New volume level (0 to 100).
        """
        self.tts_engine.set_volume(volume)
        self.config.playback.volume = volume

    def _on_tts_started(self):
        """Handle TTS playback started."""
        self.tts_toolbar.set_playing(True)
        self.status_bar.showMessage("TTS playing...")

    def _on_tts_paused(self):
        """Handle TTS playback paused."""
        self.tts_toolbar.set_playing(False)
        self.tts_toolbar.pause_action.setEnabled(False)
        self.tts_toolbar.play_action.setEnabled(True)
        self.tts_toolbar.stop_action.setEnabled(True)
        self.status_bar.showMessage("TTS paused")

    def _on_tts_stopped(self):
        """Handle TTS playback stopped."""
        self.tts_toolbar.set_playing(False)
        self.status_bar.showMessage("TTS stopped", 3000)

    def _on_tts_finished(self):
        """Handle TTS playback finished."""
        self.tts_toolbar.set_playing(False)
        self.viewer.clear_highlights()
        self.status_bar.showMessage("TTS finished", 3000)

    def _on_tts_word_boundary(self, start_offset: int, length: int):
        """Handle word boundary event from TTS engine.

        Args:
            start_offset: Character offset of the word start.
            length: Length of the word.
        """
        if not self.tts_highlighter:
            return

        # Update highlighter position
        self.tts_highlighter.update_position(start_offset)

        # Get sentence index for this word
        sentence_idx = self.tts_highlighter.get_sentence_for_offset(start_offset)

        # Get word offset for highlighting
        word_offset = self.tts_highlighter.get_word_offset(start_offset, start_offset + length)

        # Update viewer highlights
        if sentence_idx >= 0:
            self.viewer.highlight_sentence(sentence_idx)
            self.viewer.scroll_to_sentence(sentence_idx)

        self.viewer.highlight_word(word_offset)

    def _on_tts_error(self, error_msg: str):
        """Handle TTS error.

        Args:
            error_msg: Error message from TTS engine.
        """
        self.tts_toolbar.set_playing(False)
        self.status_bar.showMessage(f"TTS Error: {error_msg}", 5000)
        QMessageBox.warning(self, "TTS Error", error_msg)

    def jump_to_reading_position(self):
        """Jump to the current TTS reading position in the viewer."""
        if not self.tts_highlighter or not self.tts_engine.is_playing:
            return

        current_pos = self.tts_highlighter.current_position
        sentence_idx = self.tts_highlighter.get_sentence_for_offset(current_pos)

        if sentence_idx >= 0:
            self.viewer.scroll_to_sentence(sentence_idx)
            self.viewer.enable_auto_scroll()

    # TTS Menu Methods

    def _populate_tts_menus(self):
        """Populate all TTS-related menus."""
        self._populate_voice_menu()
        self._populate_speed_menu()
        self._populate_volume_menu()

    def _populate_voice_menu(self):
        """Populate Voice submenu with available voices from TTS engine."""
        self.voice_menu.clear()

        # Create action group for exclusive selection
        self._voice_action_group = QActionGroup(self)
        self._voice_action_group.setExclusive(True)

        # Get available voices from TTS engine
        voices = self.tts_engine.get_available_voices()

        if not voices:
            # If no voices available (not configured), show default voice option
            voices = [self.config.azure.default_voice]

        current_voice = self.tts_engine.voice

        for voice in voices:
            action = QAction(voice, self)
            action.setCheckable(True)
            action.setChecked(voice == current_voice)
            action.setData(voice)
            # Use default for checked to handle signal overload
            action.triggered.connect(lambda checked=False, v=voice: self._set_voice(v))
            self._voice_action_group.addAction(action)
            self.voice_menu.addAction(action)

    def _populate_speed_menu(self):
        """Populate Speed submenu with speed options."""
        self.speed_menu.clear()

        # Create action group for exclusive selection
        self._speed_action_group = QActionGroup(self)
        self._speed_action_group.setExclusive(True)

        # Speed options
        speed_options = [0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
        current_speed = self.config.playback.speed

        for speed in speed_options:
            label = f"{speed}x"
            action = QAction(label, self)
            action.setCheckable(True)
            # Use approximate comparison for floats
            action.setChecked(abs(speed - current_speed) < 0.01)
            action.setData(speed)
            # Use default for checked to handle signal overload
            action.triggered.connect(lambda checked=False, s=speed: self._menu_set_speed(s))
            self._speed_action_group.addAction(action)
            self.speed_menu.addAction(action)

    def _populate_volume_menu(self):
        """Populate Volume submenu with volume options."""
        self.volume_menu.clear()

        # Create action group for exclusive selection
        self._volume_action_group = QActionGroup(self)
        self._volume_action_group.setExclusive(True)

        # Volume options
        volume_options = [0, 25, 50, 75, 100]
        current_volume = self.config.playback.volume

        for volume in volume_options:
            label = f"{volume}%"
            action = QAction(label, self)
            action.setCheckable(True)
            action.setChecked(volume == current_volume)
            action.setData(volume)
            # Use default for checked to handle signal overload
            action.triggered.connect(lambda checked=False, v=volume: self._menu_set_volume(v))
            self._volume_action_group.addAction(action)
            self.volume_menu.addAction(action)

    def _set_voice(self, voice: str):
        """Set voice, update checkmarks, and update config.

        Args:
            voice: Voice name to set.
        """
        self.tts_engine.set_voice(voice)
        self.config.azure.default_voice = voice

        # Update checkmarks in voice menu
        for action in self._voice_action_group.actions():
            action.setChecked(action.data() == voice)

    def _menu_set_speed(self, speed: float):
        """Set speed from menu, sync with toolbar.

        Args:
            speed: Speed multiplier to set.
        """
        self.tts_engine.set_rate(speed)
        self.config.playback.speed = speed

        # Sync toolbar
        self.tts_toolbar.set_speed(speed)

        # Update checkmarks in speed menu
        for action in self._speed_action_group.actions():
            action.setChecked(abs(action.data() - speed) < 0.01)

    def _menu_set_volume(self, volume: int):
        """Set volume from menu, sync with toolbar.

        Args:
            volume: Volume level to set (0-100).
        """
        self.tts_engine.set_volume(volume)
        self.config.playback.volume = volume

        # Sync toolbar
        self.tts_toolbar.set_volume(volume)

        # Update checkmarks in volume menu
        for action in self._volume_action_group.actions():
            action.setChecked(action.data() == volume)

    def open_folder_dialog(self):
        """Show open folder dialog and set sidebar root."""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Open Folder",
            str(self.config.recent.last_folder or Path.home()),
        )

        if folder_path:
            self.config.recent.last_folder = folder_path
            self.sidebar.set_folder(folder_path)
            # Make sure sidebar is visible
            if not self.sidebar.isVisible():
                self.toggle_sidebar()

    def _on_sidebar_file_selected(self, file_path: str):
        """Handle file selection from sidebar.

        Args:
            file_path: Path to the selected file.
        """
        self.open_file(Path(file_path))

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
        # Stop any TTS playback
        if self.tts_engine.is_playing:
            self.tts_engine.stop()

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

        # Save sidebar state
        self.config.ui.sidebar_visible = self.sidebar.isVisible()
        if self.sidebar.isVisible():
            self.config.ui.sidebar_width = self.main_splitter.sizes()[0]

        # Save toolbar state
        self.config.ui.toolbar_visible = self.tts_toolbar.isVisible()

        save_config(self.config)
        event.accept()
