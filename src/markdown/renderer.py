"""Markdown renderer with TTS spans and highlighting support."""
import re
from typing import Optional

import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.tables import TableExtension
from markdown.extensions.footnotes import FootnoteExtension
from markdown.extensions.toc import TocExtension
from markdown.extensions.nl2br import Nl2BrExtension
from markdown.extensions.sane_lists import SaneListExtension
from markdown.extensions.md_in_html import MarkdownInHtmlExtension
from omegaconf import DictConfig


class MarkdownRenderer:
    """Renders markdown to HTML with TTS sentence/word spans."""

    def __init__(self, highlight_config: Optional[DictConfig] = None):
        """Initialize renderer with highlight configuration.

        Args:
            highlight_config: Configuration for highlight colors and opacity.
                Expected keys: sentence_color, sentence_opacity,
                              word_color, word_opacity
        """
        self.highlight_config = highlight_config or {}
        self._md = markdown.Markdown(
            extensions=[
                CodeHiliteExtension(css_class="codehilite", guess_lang=False),
                TableExtension(),
                FootnoteExtension(),
                TocExtension(permalink=True),
                Nl2BrExtension(),
                SaneListExtension(),
                MarkdownInHtmlExtension(),
                "fenced_code",
            ]
        )

    def render(self, markdown_text: str) -> str:
        """Convert markdown to full HTML document with TTS spans.

        Args:
            markdown_text: The markdown content to render.

        Returns:
            Full HTML document string with embedded CSS and JavaScript.
        """
        # Reset the markdown instance for clean conversion
        self._md.reset()

        # Convert markdown to HTML
        html_content = self._md.convert(markdown_text)

        # Add TTS spans for sentences and words
        html_with_spans = self._add_tts_spans(html_content)

        # Build complete HTML document
        return self._build_document(html_with_spans)

    def _add_tts_spans(self, html: str) -> str:
        """Add TTS sentence and word spans to HTML content.

        Args:
            html: The HTML content to process.

        Returns:
            HTML with added TTS spans.
        """
        # Process text nodes within HTML to add spans
        # We need to avoid processing content inside tags
        result = []
        sentence_index = 0
        word_offset = 0

        # Pattern to match HTML tags
        tag_pattern = re.compile(r'(<[^>]+>)')
        parts = tag_pattern.split(html)

        for part in parts:
            if part.startswith('<'):
                # This is an HTML tag, keep as is
                result.append(part)
            else:
                # This is text content, process it
                processed, sentence_index, word_offset = self._process_text_node(
                    part, sentence_index, word_offset
                )
                result.append(processed)

        return ''.join(result)

    def _process_text_node(
        self, text: str, sentence_index: int, word_offset: int
    ) -> tuple[str, int, int]:
        """Process a text node to add sentence and word spans.

        Args:
            text: The text content to process.
            sentence_index: Current sentence index.
            word_offset: Current character offset for words.

        Returns:
            Tuple of (processed_html, new_sentence_index, new_word_offset).
        """
        if not text.strip():
            return text, sentence_index, word_offset

        # Split into sentences (simple split on . ! ?)
        sentence_pattern = re.compile(r'([^.!?]*[.!?]+\s*)')
        sentences = sentence_pattern.findall(text)

        # Handle any remaining text that doesn't end with punctuation
        remaining = sentence_pattern.sub('', text)
        if remaining.strip():
            sentences.append(remaining)

        if not sentences:
            sentences = [text]

        result = []

        for sentence in sentences:
            if not sentence.strip():
                result.append(sentence)
                continue

            # Process words within the sentence
            word_spans = []
            words = re.findall(r'(\S+)(\s*)', sentence)

            for word, space in words:
                word_span = (
                    f'<span class="tts-word" data-word="{word_offset}">'
                    f'{word}</span>{space}'
                )
                word_spans.append(word_span)
                word_offset += len(word) + len(space)

            sentence_content = ''.join(word_spans)

            # Wrap in sentence span
            sentence_span = (
                f'<span class="tts-sentence" data-sentence="{sentence_index}">'
                f'{sentence_content}</span>'
            )
            result.append(sentence_span)
            sentence_index += 1

        return ''.join(result), sentence_index, word_offset

    def _build_document(self, content: str) -> str:
        """Build a complete HTML document with CSS and JavaScript.

        Args:
            content: The HTML content to embed.

        Returns:
            Complete HTML document string.
        """
        css = self._generate_css()
        js = self._generate_js()

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Markdown Preview</title>
    <style>
{css}
    </style>
</head>
<body>
    <div class="markdown-body">
{content}
    </div>
    <script>
{js}
    </script>
</body>
</html>"""

    def _generate_css(self) -> str:
        """Generate CSS with highlight colors from configuration.

        Returns:
            CSS string with highlight styles.
        """
        # Get colors from config with defaults
        sentence_color = getattr(
            self.highlight_config, 'sentence_color', '#fff3cd'
        )
        sentence_opacity = getattr(
            self.highlight_config, 'sentence_opacity', 1.0
        )
        word_color = getattr(
            self.highlight_config, 'word_color', '#ffc107'
        )
        word_opacity = getattr(
            self.highlight_config, 'word_opacity', 1.0
        )

        return f"""
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            line-height: 1.6;
            padding: 20px;
            max-width: 900px;
            margin: 0 auto;
            color: #333;
        }}

        .markdown-body {{
            padding: 20px;
        }}

        h1, h2, h3, h4, h5, h6 {{
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
            line-height: 1.25;
        }}

        h1 {{ font-size: 2em; border-bottom: 1px solid #eee; padding-bottom: 0.3em; }}
        h2 {{ font-size: 1.5em; border-bottom: 1px solid #eee; padding-bottom: 0.3em; }}
        h3 {{ font-size: 1.25em; }}

        p {{
            margin-bottom: 16px;
        }}

        code {{
            background-color: #f6f8fa;
            padding: 0.2em 0.4em;
            border-radius: 3px;
            font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
            font-size: 85%;
        }}

        pre {{
            background-color: #f6f8fa;
            padding: 16px;
            overflow: auto;
            border-radius: 6px;
            line-height: 1.45;
        }}

        pre code {{
            background-color: transparent;
            padding: 0;
        }}

        .codehilite {{
            background-color: #f6f8fa;
            padding: 16px;
            border-radius: 6px;
            overflow: auto;
        }}

        blockquote {{
            margin: 0;
            padding: 0 1em;
            color: #6a737d;
            border-left: 0.25em solid #dfe2e5;
        }}

        table {{
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 16px;
        }}

        table th, table td {{
            border: 1px solid #dfe2e5;
            padding: 6px 13px;
        }}

        table tr:nth-child(2n) {{
            background-color: #f6f8fa;
        }}

        a {{
            color: #0366d6;
            text-decoration: none;
        }}

        a:hover {{
            text-decoration: underline;
        }}

        img {{
            max-width: 100%;
            height: auto;
        }}

        .tts-sentence {{
            transition: background-color 0.2s ease;
        }}

        .tts-word {{
            transition: background-color 0.15s ease;
        }}

        .current-sentence {{
            background-color: {sentence_color};
            opacity: {sentence_opacity};
        }}

        .current-word {{
            background-color: {word_color};
            opacity: {word_opacity};
        }}

        /* Footnotes */
        .footnote {{
            font-size: 0.9em;
        }}

        /* Table of contents */
        .toc {{
            background-color: #f6f8fa;
            padding: 10px 20px;
            border-radius: 6px;
            margin-bottom: 20px;
        }}

        .toc ul {{
            list-style-type: none;
            padding-left: 20px;
        }}

        .toc > ul {{
            padding-left: 0;
        }}
"""

    def _generate_js(self) -> str:
        """Generate JavaScript for TTS highlighting and scrolling.

        Returns:
            JavaScript string with highlight/scroll functions.
        """
        return """
        // Auto-scroll state
        let autoScrollEnabled = true;

        // Clear all highlights
        function clearHighlights() {
            document.querySelectorAll('.current-sentence').forEach(el => {
                el.classList.remove('current-sentence');
            });
            document.querySelectorAll('.current-word').forEach(el => {
                el.classList.remove('current-word');
            });
        }

        // Highlight a specific sentence
        function highlightSentence(index) {
            // Clear previous sentence highlights
            document.querySelectorAll('.current-sentence').forEach(el => {
                el.classList.remove('current-sentence');
            });

            // Highlight new sentence
            const sentence = document.querySelector(`[data-sentence="${index}"]`);
            if (sentence) {
                sentence.classList.add('current-sentence');
            }
        }

        // Highlight a specific word
        function highlightWord(offset) {
            // Clear previous word highlights
            document.querySelectorAll('.current-word').forEach(el => {
                el.classList.remove('current-word');
            });

            // Highlight new word
            const word = document.querySelector(`[data-word="${offset}"]`);
            if (word) {
                word.classList.add('current-word');
            }
        }

        // Scroll to a specific sentence
        function scrollToSentence(index) {
            if (!autoScrollEnabled) return;

            const sentence = document.querySelector(`[data-sentence="${index}"]`);
            if (sentence) {
                sentence.scrollIntoView({
                    behavior: 'smooth',
                    block: 'center'
                });
            }
        }

        // Enable auto-scroll
        function enableAutoScroll() {
            autoScrollEnabled = true;
        }

        // Disable auto-scroll
        function disableAutoScroll() {
            autoScrollEnabled = false;
        }

        // Detect manual scroll to disable auto-scroll
        document.addEventListener('wheel', function(e) {
            disableAutoScroll();
        });

        // Click handler for sentences - signals to Python via QWebChannel
        document.addEventListener('click', function(e) {
            const sentence = e.target.closest('.tts-sentence');
            if (sentence) {
                const index = parseInt(sentence.dataset.sentence, 10);
                // If QWebChannel is available, signal to Python
                if (typeof qt !== 'undefined' && qt.webChannelTransport) {
                    new QWebChannel(qt.webChannelTransport, function(channel) {
                        if (channel.objects.bridge) {
                            channel.objects.bridge.onSentenceClicked(index);
                        }
                    });
                }
                // Also emit a custom event for non-Qt environments
                window.dispatchEvent(new CustomEvent('sentenceClicked', {
                    detail: { index: index }
                }));
            }
        });
"""


def extract_plain_text(markdown_text: str) -> str:
    """Extract plain text from markdown for TTS processing.

    Strips all markdown formatting, code blocks, and links,
    returning only the readable text content.

    Args:
        markdown_text: The markdown content to process.

    Returns:
        Plain text string suitable for TTS.
    """
    text = markdown_text

    # Remove code blocks
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'`[^`]+`', '', text)

    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Remove images
    text = re.sub(r'!\[[^\]]*\]\([^)]+\)', '', text)

    # Convert links to just text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)

    # Remove headers formatting
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)

    # Remove bold/italic
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'__([^_]+)__', r'\1', text)
    text = re.sub(r'_([^_]+)_', r'\1', text)

    # Remove strikethrough
    text = re.sub(r'~~([^~]+)~~', r'\1', text)

    # Remove blockquote markers
    text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)

    # Remove horizontal rules
    text = re.sub(r'^[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)

    # Remove list markers
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)

    # Clean up extra whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()

    return text
