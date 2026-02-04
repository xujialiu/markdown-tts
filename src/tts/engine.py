"""Azure TTS Engine with word boundary events."""
import html
from typing import Optional, List

from PySide6.QtCore import QObject, QThread, Signal, QMutex, QWaitCondition

try:
    import azure.cognitiveservices.speech as speechsdk
    AZURE_SDK_AVAILABLE = True
except ImportError:
    speechsdk = None
    AZURE_SDK_AVAILABLE = False


class TTSWorker(QThread):
    """Worker thread for background TTS synthesis."""

    # Signals emitted during synthesis
    word_boundary = Signal(int, int)  # start_offset, length
    playback_started = Signal()
    playback_finished = Signal()
    error_occurred = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._synthesizer: Optional[object] = None
        self._ssml: str = ""
        self._should_stop: bool = False
        self._is_paused: bool = False
        self._mutex = QMutex()
        self._pause_condition = QWaitCondition()

    def setup(self, synthesizer: object, ssml: str) -> None:
        """Configure the worker with synthesizer and SSML content."""
        self._synthesizer = synthesizer
        self._ssml = ssml
        self._should_stop = False
        self._is_paused = False

    def run(self) -> None:
        """Execute TTS synthesis in background thread."""
        if not AZURE_SDK_AVAILABLE or self._synthesizer is None:
            self.error_occurred.emit("Azure Speech SDK not available")
            return

        try:
            self.playback_started.emit()

            # Perform synthesis
            result = self._synthesizer.speak_ssml_async(self._ssml).get()

            if self._should_stop:
                return

            # Check result
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                self.playback_finished.emit()
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation = speechsdk.CancellationDetails(result)
                if cancellation.reason == speechsdk.CancellationReason.Error:
                    self.error_occurred.emit(
                        f"Speech synthesis canceled: {cancellation.error_details}"
                    )
                else:
                    # User-initiated cancellation
                    self.playback_finished.emit()

        except Exception as e:
            self.error_occurred.emit(f"TTS synthesis error: {str(e)}")

    def request_stop(self) -> None:
        """Request the worker to stop synthesis."""
        self._should_stop = True

    def pause(self) -> None:
        """Pause synthesis (note: Azure SDK doesn't support true pause)."""
        self._mutex.lock()
        self._is_paused = True
        self._mutex.unlock()

    def resume(self) -> None:
        """Resume synthesis."""
        self._mutex.lock()
        self._is_paused = False
        self._pause_condition.wakeAll()
        self._mutex.unlock()


class TTSEngine(QObject):
    """Azure Text-to-Speech engine with playback controls."""

    # Signals for playback state changes
    word_boundary = Signal(int, int)  # start_offset, length
    playback_started = Signal()
    playback_paused = Signal()
    playback_stopped = Signal()
    playback_finished = Signal()
    error_occurred = Signal(str)

    def __init__(
        self,
        speech_key: str = "",
        speech_region: str = "eastus",
        parent: Optional[QObject] = None
    ):
        super().__init__(parent)

        self._speech_key = speech_key
        self._speech_region = speech_region
        self._voice = "en-US-JennyNeural"
        self._rate = 1.0  # 0.5 to 2.0
        self._volume = 100  # 0 to 100

        self._speech_config: Optional[object] = None
        self._synthesizer: Optional[object] = None
        self._worker: Optional[TTSWorker] = None
        self._is_playing = False
        self._is_paused = False

        # Initialize if credentials provided
        if speech_key and AZURE_SDK_AVAILABLE:
            self._initialize_synthesizer()

    def _initialize_synthesizer(self) -> bool:
        """Initialize the Azure Speech synthesizer."""
        if not AZURE_SDK_AVAILABLE:
            return False

        try:
            self._speech_config = speechsdk.SpeechConfig(
                subscription=self._speech_key,
                region=self._speech_region
            )
            self._speech_config.speech_synthesis_voice_name = self._voice

            # Use default audio output (speakers)
            audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

            self._synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self._speech_config,
                audio_config=audio_config
            )

            # Connect word boundary event
            self._synthesizer.synthesis_word_boundary.connect(
                self._on_word_boundary
            )

            return True
        except Exception as e:
            self.error_occurred.emit(f"Failed to initialize TTS: {str(e)}")
            return False

    def _on_word_boundary(self, evt) -> None:
        """Handle word boundary event from Azure SDK."""
        # Azure provides text_offset and word_length
        self.word_boundary.emit(evt.text_offset, evt.word_length)

    def is_configured(self) -> bool:
        """Check if the engine has valid credentials configured."""
        if not AZURE_SDK_AVAILABLE:
            return False
        return bool(self._speech_key and self._speech_region and self._synthesizer)

    def configure(self, speech_key: str, speech_region: str) -> bool:
        """Configure or reconfigure the engine with new credentials."""
        self._speech_key = speech_key
        self._speech_region = speech_region
        return self._initialize_synthesizer()

    def _build_ssml(self, text: str) -> str:
        """Build SSML with prosody for rate and volume control.

        Args:
            text: Plain text to convert to speech.

        Returns:
            SSML string with prosody elements for rate/volume.
        """
        # Escape special XML characters in the text
        escaped_text = html.escape(text)

        # Convert rate (0.5-2.0) to percentage string
        # 1.0 = default, 0.5 = 50%, 2.0 = 200%
        rate_percent = int(self._rate * 100)
        rate_str = f"{rate_percent}%"

        # Convert volume (0-100) to percentage string
        volume_str = f"{self._volume}%"

        ssml = f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
    <voice name="{self._voice}">
        <prosody rate="{rate_str}" volume="{volume_str}">
            {escaped_text}
        </prosody>
    </voice>
</speak>'''
        return ssml

    def play(self, text: str) -> bool:
        """Start TTS synthesis for the given text.

        Args:
            text: Text to synthesize and play.

        Returns:
            True if synthesis started successfully, False otherwise.
        """
        if not self.is_configured():
            self.error_occurred.emit("TTS engine not configured")
            return False

        # Stop any existing playback
        if self._is_playing:
            self.stop()

        # Build SSML
        ssml = self._build_ssml(text)

        # Create and setup worker
        self._worker = TTSWorker(self)
        self._worker.setup(self._synthesizer, ssml)

        # Connect worker signals
        self._worker.word_boundary.connect(self.word_boundary.emit)
        self._worker.playback_started.connect(self._on_playback_started)
        self._worker.playback_finished.connect(self._on_playback_finished)
        self._worker.error_occurred.connect(self.error_occurred.emit)

        # Start synthesis
        self._worker.start()
        return True

    def _on_playback_started(self) -> None:
        """Handle playback started event."""
        self._is_playing = True
        self._is_paused = False
        self.playback_started.emit()

    def _on_playback_finished(self) -> None:
        """Handle playback finished event."""
        self._is_playing = False
        self._is_paused = False
        self.playback_finished.emit()

    def pause(self) -> None:
        """Pause current playback.

        Note: Azure Speech SDK doesn't support true pause/resume.
        This is a best-effort implementation.
        """
        if self._is_playing and not self._is_paused and self._worker:
            self._is_paused = True
            self._worker.pause()
            self.playback_paused.emit()

    def resume(self) -> None:
        """Resume paused playback."""
        if self._is_paused and self._worker:
            self._is_paused = False
            self._worker.resume()
            self.playback_started.emit()

    def stop(self) -> None:
        """Stop current playback."""
        if self._worker:
            self._worker.request_stop()
            if self._synthesizer and AZURE_SDK_AVAILABLE:
                try:
                    self._synthesizer.stop_speaking_async()
                except Exception:
                    pass  # Ignore errors during stop

            # Wait for worker to finish
            if self._worker.isRunning():
                self._worker.wait(1000)  # Wait up to 1 second

            self._worker = None

        if self._is_playing:
            self._is_playing = False
            self._is_paused = False
            self.playback_stopped.emit()

    def set_voice(self, voice: str) -> None:
        """Set the voice to use for synthesis.

        Args:
            voice: Voice name (e.g., "en-US-JennyNeural").
        """
        self._voice = voice
        if self._speech_config and AZURE_SDK_AVAILABLE:
            self._speech_config.speech_synthesis_voice_name = voice

    def set_rate(self, rate: float) -> None:
        """Set the speech rate.

        Args:
            rate: Speech rate multiplier (0.5 to 2.0, where 1.0 is normal).
        """
        self._rate = max(0.5, min(2.0, rate))

    def set_volume(self, volume: int) -> None:
        """Set the speech volume.

        Args:
            volume: Volume level (0 to 100).
        """
        self._volume = max(0, min(100, volume))

    def get_available_voices(self) -> List[str]:
        """Get list of available voice names.

        Returns:
            List of voice name strings, or empty list if not configured.
        """
        if not self.is_configured():
            return []

        try:
            result = self._synthesizer.get_voices_async().get()
            if result.reason == speechsdk.ResultReason.VoicesListRetrieved:
                return [voice.short_name for voice in result.voices]
            return []
        except Exception:
            return []

    @property
    def is_playing(self) -> bool:
        """Check if currently playing."""
        return self._is_playing

    @property
    def is_paused(self) -> bool:
        """Check if currently paused."""
        return self._is_paused

    @property
    def voice(self) -> str:
        """Get current voice name."""
        return self._voice

    @property
    def rate(self) -> float:
        """Get current speech rate."""
        return self._rate

    @property
    def volume(self) -> int:
        """Get current volume level."""
        return self._volume
