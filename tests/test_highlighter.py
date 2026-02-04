"""Tests for TTS highlighter module."""
import pytest

from src.tts.highlighter import TTSHighlighter, Sentence


class TestSentenceSplitting:
    """Tests for sentence splitting functionality."""

    def test_splits_on_period(self):
        """Test that sentences are split on period."""
        text = "First sentence. Second sentence."
        highlighter = TTSHighlighter(text)

        assert highlighter.sentence_count == 2
        assert highlighter.sentences[0].text == "First sentence."
        assert highlighter.sentences[1].text == "Second sentence."

    def test_splits_on_exclamation(self):
        """Test that sentences are split on exclamation mark."""
        text = "Hello world! How are you!"
        highlighter = TTSHighlighter(text)

        assert highlighter.sentence_count == 2
        assert highlighter.sentences[0].text == "Hello world!"
        assert highlighter.sentences[1].text == "How are you!"

    def test_splits_on_question_mark(self):
        """Test that sentences are split on question mark."""
        text = "Is this working? Yes it is?"
        highlighter = TTSHighlighter(text)

        assert highlighter.sentence_count == 2
        assert highlighter.sentences[0].text == "Is this working?"
        assert highlighter.sentences[1].text == "Yes it is?"

    def test_splits_on_mixed_punctuation(self):
        """Test splitting with mixed punctuation . ! ?"""
        text = "Statement here. Question here? Exclamation here!"
        highlighter = TTSHighlighter(text)

        assert highlighter.sentence_count == 3
        assert highlighter.sentences[0].text == "Statement here."
        assert highlighter.sentences[1].text == "Question here?"
        assert highlighter.sentences[2].text == "Exclamation here!"

    def test_handles_multiple_punctuation(self):
        """Test handling of multiple punctuation marks like ... or ?!"""
        text = "Wait... What?!"
        highlighter = TTSHighlighter(text)

        assert highlighter.sentence_count == 2

    def test_handles_text_without_ending_punctuation(self):
        """Test handling text that doesn't end with sentence punctuation."""
        text = "First sentence. This has no ending"
        highlighter = TTSHighlighter(text)

        assert highlighter.sentence_count == 2
        assert highlighter.sentences[1].text == "This has no ending"

    def test_handles_empty_text(self):
        """Test handling of empty text."""
        highlighter = TTSHighlighter("")

        assert highlighter.sentence_count == 0
        assert highlighter.sentences == []

    def test_handles_whitespace_only(self):
        """Test handling of whitespace-only text."""
        highlighter = TTSHighlighter("   \n\t  ")

        assert highlighter.sentence_count == 0

    def test_sentence_indices_are_sequential(self):
        """Test that sentence indices are sequential starting from 0."""
        text = "One. Two. Three."
        highlighter = TTSHighlighter(text)

        for i, sentence in enumerate(highlighter.sentences):
            assert sentence.index == i


class TestOffsetMapping:
    """Tests for mapping character offsets to sentences."""

    def test_maps_offset_to_first_sentence(self):
        """Test mapping offset within first sentence."""
        text = "First sentence. Second sentence."
        highlighter = TTSHighlighter(text)

        # Offset 0 should be in first sentence
        assert highlighter.get_sentence_for_offset(0) == 0
        # Offset 5 (within "First") should be in first sentence
        assert highlighter.get_sentence_for_offset(5) == 0

    def test_maps_offset_to_second_sentence(self):
        """Test mapping offset within second sentence."""
        text = "First sentence. Second sentence."
        highlighter = TTSHighlighter(text)

        # "Second" starts around position 16
        assert highlighter.get_sentence_for_offset(16) == 1
        assert highlighter.get_sentence_for_offset(20) == 1

    def test_maps_offset_at_sentence_boundary(self):
        """Test mapping offset at exact sentence boundary."""
        text = "Hi. Hello."
        highlighter = TTSHighlighter(text)

        # At position 3 (after "Hi.") should map correctly
        # Position 4 is the space, 5 is 'H' of "Hello"
        assert highlighter.get_sentence_for_offset(4) == 1

    def test_returns_negative_for_invalid_offset(self):
        """Test that invalid offsets return -1."""
        highlighter = TTSHighlighter("")

        assert highlighter.get_sentence_for_offset(0) == -1
        assert highlighter.get_sentence_for_offset(100) == -1

    def test_maps_offset_at_end_of_text(self):
        """Test mapping offset at/beyond end of text."""
        text = "Only sentence."
        highlighter = TTSHighlighter(text)

        # At or beyond the text length should return last sentence
        assert highlighter.get_sentence_for_offset(len(text)) == 0
        assert highlighter.get_sentence_for_offset(len(text) + 10) == 0


class TestWordOffsetTracking:
    """Tests for word offset tracking."""

    def test_word_offset_at_start(self):
        """Test word offset at the start of text."""
        text = "Hello world test"
        highlighter = TTSHighlighter(text)

        assert highlighter.get_word_offset(0, 5) == 0

    def test_word_offset_after_first_word(self):
        """Test word offset after first word."""
        text = "Hello world test"
        highlighter = TTSHighlighter(text)

        # After "Hello " (position 6)
        assert highlighter.get_word_offset(6, 11) == 1

    def test_word_offset_after_multiple_words(self):
        """Test word offset after multiple words."""
        text = "One two three four five"
        highlighter = TTSHighlighter(text)

        # After "One two three " (position 14)
        assert highlighter.get_word_offset(14, 18) == 3

    def test_word_offset_with_sentences(self):
        """Test word offset across sentence boundaries."""
        text = "First sentence. Second sentence."
        highlighter = TTSHighlighter(text)

        # At start of "Second" (around position 16)
        offset = highlighter.get_word_offset(16, 22)
        assert offset == 2  # "First" and "sentence." are before

    def test_word_offset_with_negative_start(self):
        """Test word offset with negative start returns 0."""
        text = "Hello world"
        highlighter = TTSHighlighter(text)

        assert highlighter.get_word_offset(-5, 0) == 0


class TestSentenceRetrieval:
    """Tests for sentence retrieval methods."""

    def test_get_sentence_by_valid_index(self):
        """Test getting sentence by valid index."""
        text = "First. Second. Third."
        highlighter = TTSHighlighter(text)

        sentence = highlighter.get_sentence_by_index(1)
        assert sentence is not None
        assert sentence.text == "Second."
        assert sentence.index == 1

    def test_get_sentence_by_invalid_index(self):
        """Test getting sentence by invalid index returns None."""
        text = "Only one."
        highlighter = TTSHighlighter(text)

        assert highlighter.get_sentence_by_index(-1) is None
        assert highlighter.get_sentence_by_index(5) is None

    def test_get_text_from_first_sentence(self):
        """Test getting text from first sentence to end."""
        text = "First. Second. Third."
        highlighter = TTSHighlighter(text)

        result = highlighter.get_text_from_sentence(0)
        assert result == text

    def test_get_text_from_middle_sentence(self):
        """Test getting text from middle sentence to end."""
        text = "First. Second. Third."
        highlighter = TTSHighlighter(text)

        result = highlighter.get_text_from_sentence(1)
        assert "Second." in result
        assert "Third." in result
        assert "First." not in result

    def test_get_text_from_last_sentence(self):
        """Test getting text from last sentence."""
        text = "First. Second. Third."
        highlighter = TTSHighlighter(text)

        result = highlighter.get_text_from_sentence(2)
        assert "Third." in result

    def test_get_text_from_invalid_sentence(self):
        """Test getting text from invalid sentence returns empty."""
        text = "Only one."
        highlighter = TTSHighlighter(text)

        assert highlighter.get_text_from_sentence(5) == ""
        assert highlighter.get_text_from_sentence(-1) == ""


class TestPositionTracking:
    """Tests for position tracking functionality."""

    def test_initial_position_is_zero(self):
        """Test that initial position is zero."""
        highlighter = TTSHighlighter("Some text.")

        assert highlighter.current_position == 0

    def test_update_position(self):
        """Test updating the current position."""
        highlighter = TTSHighlighter("Some text.")

        highlighter.update_position(5)
        assert highlighter.current_position == 5

        highlighter.update_position(10)
        assert highlighter.current_position == 10

    def test_update_position_clamps_negative(self):
        """Test that negative positions are clamped to 0."""
        highlighter = TTSHighlighter("Some text.")

        highlighter.update_position(-5)
        assert highlighter.current_position == 0


class TestSentenceDataclass:
    """Tests for Sentence dataclass."""

    def test_sentence_fields(self):
        """Test that Sentence has all required fields."""
        sentence = Sentence(text="Hello.", start=0, end=6, index=0)

        assert sentence.text == "Hello."
        assert sentence.start == 0
        assert sentence.end == 6
        assert sentence.index == 0

    def test_sentence_equality(self):
        """Test Sentence equality comparison."""
        s1 = Sentence(text="Hello.", start=0, end=6, index=0)
        s2 = Sentence(text="Hello.", start=0, end=6, index=0)

        assert s1 == s2


class TestHighlighterProperties:
    """Tests for highlighter properties."""

    def test_text_property(self):
        """Test that text property returns original text."""
        text = "Original text here."
        highlighter = TTSHighlighter(text)

        assert highlighter.text == text

    def test_sentences_property_returns_copy(self):
        """Test that sentences property returns a copy."""
        text = "First. Second."
        highlighter = TTSHighlighter(text)

        sentences = highlighter.sentences
        sentences.clear()

        # Original should not be affected
        assert highlighter.sentence_count == 2

    def test_sentence_count_property(self):
        """Test sentence_count property."""
        text = "One. Two. Three."
        highlighter = TTSHighlighter(text)

        assert highlighter.sentence_count == 3


class TestModuleExports:
    """Tests for module exports."""

    def test_highlighter_exported_from_tts_module(self):
        """Test that TTSHighlighter is exported from tts module."""
        from src.tts import TTSHighlighter

        assert TTSHighlighter is not None

    def test_sentence_can_be_imported(self):
        """Test that Sentence dataclass can be imported."""
        from src.tts.highlighter import Sentence

        assert Sentence is not None
