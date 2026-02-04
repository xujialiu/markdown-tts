"""TTS Highlighter for sentence and word tracking during playback."""
import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Sentence:
    """Represents a sentence with position information."""

    text: str
    start: int  # Start character offset in the original text
    end: int    # End character offset in the original text
    index: int  # Sentence index (0-based)


class TTSHighlighter:
    """Tracks sentence and word positions for TTS highlighting.

    This class splits text into sentences and provides methods to
    map character offsets to sentences and track word positions.
    """

    # Sentence-ending punctuation pattern
    SENTENCE_END_PATTERN = re.compile(r'[.!?]+')

    def __init__(self, text: str):
        """Initialize the highlighter with text content.

        Args:
            text: The text content to track for highlighting.
        """
        self._text = text
        self._sentences: List[Sentence] = []
        self._current_position: int = 0
        self._split_sentences()

    def _split_sentences(self) -> None:
        """Split the text into sentences based on . ! ? punctuation.

        Creates Sentence objects with text, start/end offsets, and index.
        """
        if not self._text:
            return

        sentences = []
        current_start = 0
        text = self._text

        # Find all sentence-ending punctuation
        for match in self.SENTENCE_END_PATTERN.finditer(text):
            end_pos = match.end()

            # Extract sentence text (including the punctuation)
            sentence_text = text[current_start:end_pos].strip()

            if sentence_text:
                # Find the actual start position (skip leading whitespace)
                actual_start = current_start
                while actual_start < len(text) and text[actual_start].isspace():
                    actual_start += 1

                sentences.append(Sentence(
                    text=sentence_text,
                    start=actual_start,
                    end=end_pos,
                    index=len(sentences)
                ))

            current_start = end_pos

        # Handle any remaining text after the last sentence-ending punctuation
        remaining = text[current_start:].strip()
        if remaining:
            actual_start = current_start
            while actual_start < len(text) and text[actual_start].isspace():
                actual_start += 1

            sentences.append(Sentence(
                text=remaining,
                start=actual_start,
                end=len(text),
                index=len(sentences)
            ))

        self._sentences = sentences

    def get_sentence_for_offset(self, char_offset: int) -> int:
        """Get the sentence index containing the given character offset.

        Args:
            char_offset: Character position in the original text.

        Returns:
            The index of the sentence containing the offset,
            or -1 if not found or no sentences exist.
        """
        if not self._sentences:
            return -1

        for sentence in self._sentences:
            if sentence.start <= char_offset < sentence.end:
                return sentence.index

        # If offset is at or beyond the end of the text,
        # return the last sentence
        if char_offset >= len(self._text) and self._sentences:
            return self._sentences[-1].index

        return -1

    def get_word_offset(self, start: int, end: int) -> int:
        """Calculate the cumulative word offset for a position range.

        Counts the number of words from the beginning of the text
        up to the start position.

        Args:
            start: Start character offset.
            end: End character offset (unused, kept for API consistency).

        Returns:
            Number of words before the start position.
        """
        if start <= 0:
            return 0

        # Extract text up to the start position
        text_before = self._text[:start]

        # Count words (split on whitespace)
        words = text_before.split()
        return len(words)

    def get_sentence_by_index(self, idx: int) -> Optional[Sentence]:
        """Get a sentence by its index.

        Args:
            idx: The sentence index (0-based).

        Returns:
            The Sentence object, or None if index is out of range.
        """
        if 0 <= idx < len(self._sentences):
            return self._sentences[idx]
        return None

    def get_text_from_sentence(self, sentence_idx: int) -> str:
        """Get the text from a given sentence to the end of the content.

        Args:
            sentence_idx: The starting sentence index (0-based).

        Returns:
            Text from the start of the specified sentence to the end,
            or empty string if index is invalid.
        """
        sentence = self.get_sentence_by_index(sentence_idx)
        if sentence is None:
            return ""

        return self._text[sentence.start:]

    def update_position(self, char_offset: int) -> None:
        """Update the current tracking position.

        Args:
            char_offset: The new character position.
        """
        self._current_position = max(0, char_offset)

    @property
    def text(self) -> str:
        """Get the original text content."""
        return self._text

    @property
    def sentences(self) -> List[Sentence]:
        """Get the list of all sentences."""
        return self._sentences.copy()

    @property
    def sentence_count(self) -> int:
        """Get the total number of sentences."""
        return len(self._sentences)

    @property
    def current_position(self) -> int:
        """Get the current tracking position."""
        return self._current_position
