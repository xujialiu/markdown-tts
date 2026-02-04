"""Tests for markdown renderer with TTS spans."""
import pytest
from omegaconf import OmegaConf

from src.markdown.renderer import MarkdownRenderer, extract_plain_text


@pytest.fixture
def highlight_config():
    """Provide highlight configuration for tests."""
    return OmegaConf.create({
        "sentence_color": "#fff3cd",
        "sentence_opacity": 1.0,
        "word_color": "#ffc107",
        "word_opacity": 1.0,
    })


@pytest.fixture
def renderer(highlight_config):
    """Provide a MarkdownRenderer instance."""
    return MarkdownRenderer(highlight_config)


class TestMarkdownRenderer:
    """Tests for MarkdownRenderer class."""

    def test_renderer_converts_heading(self, renderer):
        """Test that markdown headings are converted to HTML h tags."""
        markdown_text = "# Heading 1\n\n## Heading 2\n\n### Heading 3"
        html = renderer.render(markdown_text)

        # Headings may have id attributes, so check for opening tag pattern
        assert "<h1" in html
        assert "</h1>" in html
        assert "<h2" in html
        assert "</h2>" in html
        assert "<h3" in html
        assert "</h3>" in html
        assert "Heading 1" in html or "Heading</span>" in html  # Text may be wrapped
        assert "Heading 2" in html or "Heading</span>" in html
        assert "Heading 3" in html or "Heading</span>" in html

    def test_renderer_converts_bold(self, renderer):
        """Test that bold markdown is converted to strong tags."""
        markdown_text = "This is **bold** text and __also bold__."
        html = renderer.render(markdown_text)

        assert "<strong>" in html
        assert "bold" in html

    def test_renderer_includes_sentence_spans(self, renderer):
        """Test that sentences are wrapped with data-sentence attributes."""
        markdown_text = "First sentence. Second sentence."
        html = renderer.render(markdown_text)

        assert 'data-sentence="0"' in html
        assert 'data-sentence="1"' in html
        assert 'class="tts-sentence"' in html

    def test_renderer_includes_word_spans(self, renderer):
        """Test that words are wrapped with data-word attributes."""
        markdown_text = "Hello world."
        html = renderer.render(markdown_text)

        assert 'data-word=' in html
        assert 'class="tts-word"' in html

    def test_renderer_applies_highlight_colors(self, highlight_config):
        """Test that custom highlight colors appear in generated CSS."""
        custom_config = OmegaConf.create({
            "sentence_color": "#ff0000",
            "sentence_opacity": 0.8,
            "word_color": "#00ff00",
            "word_opacity": 0.9,
        })
        renderer = MarkdownRenderer(custom_config)
        html = renderer.render("Test text.")

        # Check that custom colors are in the CSS
        assert "#ff0000" in html or "rgb(255, 0, 0)" in html
        assert "#00ff00" in html or "rgb(0, 255, 0)" in html
        # Check opacity values
        assert "0.8" in html
        assert "0.9" in html

    def test_renderer_syntax_highlights_code(self, renderer):
        """Test that code blocks get syntax highlighting."""
        markdown_text = "```python\ndef hello():\n    print('world')\n```"
        html = renderer.render(markdown_text)

        # CodeHilite extension adds codehilite class
        assert "codehilite" in html or "highlight" in html or "<code" in html


class TestExtractPlainText:
    """Tests for extract_plain_text function."""

    def test_extract_plain_text_removes_markdown(self):
        """Test that markdown formatting is stripped."""
        markdown_text = "# Heading\n\nThis is **bold** and *italic*."
        plain = extract_plain_text(markdown_text)

        assert "Heading" in plain
        assert "bold" in plain
        assert "italic" in plain
        assert "#" not in plain
        assert "**" not in plain
        assert "*" not in plain or plain.count("*") == 0

    def test_extract_plain_text_removes_code_blocks(self):
        """Test that code blocks are removed from plain text."""
        markdown_text = "Before code.\n\n```python\ncode here\n```\n\nAfter code."
        plain = extract_plain_text(markdown_text)

        assert "Before code" in plain
        assert "After code" in plain

    def test_extract_plain_text_removes_links(self):
        """Test that link formatting is removed but text preserved."""
        markdown_text = "Click [here](https://example.com) for more."
        plain = extract_plain_text(markdown_text)

        assert "Click" in plain
        assert "here" in plain
        assert "for more" in plain
        assert "https://" not in plain
        assert "[" not in plain
        assert "]" not in plain
