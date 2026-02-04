"""TTS Toolbar with playback controls."""
from PySide6.QtWidgets import (
    QToolBar,
    QToolButton,
    QComboBox,
    QSlider,
    QLabel,
    QWidget,
    QHBoxLayout,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QAction


class TTSToolbar(QToolBar):
    """Toolbar with TTS playback controls.

    Provides Play, Pause, Stop buttons along with speed and volume controls.
    """

    # Signals for playback control
    play_clicked = Signal()
    pause_clicked = Signal()
    stop_clicked = Signal()
    speed_changed = Signal(float)
    volume_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__("TTS Controls", parent)
        self.setObjectName("tts_toolbar")
        self._setup_ui()

    def _setup_ui(self):
        """Set up the toolbar UI components."""
        # Play button
        self.play_action = QAction("Play", self)
        self.play_action.setToolTip("Play TTS (Space)")
        self.play_action.triggered.connect(self.play_clicked.emit)
        self.addAction(self.play_action)

        # Pause button
        self.pause_action = QAction("Pause", self)
        self.pause_action.setToolTip("Pause TTS")
        self.pause_action.triggered.connect(self.pause_clicked.emit)
        self.pause_action.setEnabled(False)
        self.addAction(self.pause_action)

        # Stop button
        self.stop_action = QAction("Stop", self)
        self.stop_action.setToolTip("Stop TTS")
        self.stop_action.triggered.connect(self.stop_clicked.emit)
        self.stop_action.setEnabled(False)
        self.addAction(self.stop_action)

        self.addSeparator()

        # Speed label and dropdown
        speed_label = QLabel(" Speed: ")
        self.addWidget(speed_label)

        self.speed_combo = QComboBox()
        self.speed_combo.setToolTip("Playback speed")
        # Speed options from 0.5x to 2.0x
        self._speed_values = [0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]
        for speed in self._speed_values:
            self.speed_combo.addItem(f"{speed}x", speed)
        # Default to 1.0x (index 2)
        self.speed_combo.setCurrentIndex(2)
        self.speed_combo.currentIndexChanged.connect(self._on_speed_changed)
        self.addWidget(self.speed_combo)

        self.addSeparator()

        # Volume label and slider
        volume_label = QLabel(" Volume: ")
        self.addWidget(volume_label)

        # Create a container widget for the slider
        volume_widget = QWidget()
        volume_layout = QHBoxLayout(volume_widget)
        volume_layout.setContentsMargins(0, 0, 0, 0)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setToolTip("Volume level")
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(100)
        self.volume_slider.setFixedWidth(100)
        self.volume_slider.valueChanged.connect(self._on_volume_changed)
        volume_layout.addWidget(self.volume_slider)

        self.volume_label = QLabel("100%")
        self.volume_label.setFixedWidth(40)
        volume_layout.addWidget(self.volume_label)

        self.addWidget(volume_widget)

    def _on_speed_changed(self, index: int):
        """Handle speed combo box selection change."""
        speed = self._speed_values[index]
        self.speed_changed.emit(speed)

    def _on_volume_changed(self, value: int):
        """Handle volume slider value change."""
        self.volume_label.setText(f"{value}%")
        self.volume_changed.emit(value)

    def set_playing(self, is_playing: bool):
        """Update button states based on playback state.

        Args:
            is_playing: True if TTS is currently playing.
        """
        self.play_action.setEnabled(not is_playing)
        self.pause_action.setEnabled(is_playing)
        self.stop_action.setEnabled(is_playing)

    def set_speed(self, speed: float):
        """Set the speed dropdown to match the given value.

        Args:
            speed: Speed multiplier (0.5 to 2.0).
        """
        # Find the closest matching speed value
        closest_idx = 0
        min_diff = abs(self._speed_values[0] - speed)

        for i, val in enumerate(self._speed_values):
            diff = abs(val - speed)
            if diff < min_diff:
                min_diff = diff
                closest_idx = i

        # Block signals to prevent emitting speed_changed
        self.speed_combo.blockSignals(True)
        self.speed_combo.setCurrentIndex(closest_idx)
        self.speed_combo.blockSignals(False)

    def set_volume(self, volume: int):
        """Set the volume slider to match the given value.

        Args:
            volume: Volume level (0 to 100).
        """
        # Clamp volume to valid range
        volume = max(0, min(100, volume))

        # Block signals to prevent emitting volume_changed
        self.volume_slider.blockSignals(True)
        self.volume_slider.setValue(volume)
        self.volume_slider.blockSignals(False)

        self.volume_label.setText(f"{volume}%")
