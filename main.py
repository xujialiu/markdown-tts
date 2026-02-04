"""Typora TTS App - Markdown editor with text-to-speech."""
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel


def main():
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Typora TTS")
    window.setCentralWidget(QLabel("Hello, Typora TTS!"))
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
