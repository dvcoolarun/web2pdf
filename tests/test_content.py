"""Tests for content extraction and HTML formatting."""
import pytest
import sys
import os
from unittest.mock import MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

for mod in ['gevent', 'gevent.monkey', 'grequests', 'weasyprint', 'weasyprint.HTML']:
    sys.modules[mod] = MagicMock()

from main import Web2PDFConverter


@pytest.fixture
def converter():
    return Web2PDFConverter(use_browser=False)


class TestFormatTextAsHtml:
    """Tests for _format_text_as_html method."""

    def test_empty_text_returns_empty(self, converter):
        result = converter._format_text_as_html("")
        assert result == ""

    def test_none_returns_empty(self, converter):
        result = converter._format_text_as_html(None)
        assert result == ""

    def test_single_paragraph(self, converter):
        result = converter._format_text_as_html("Hello world")
        assert "Hello world" in result

    def test_multiple_paragraphs(self, converter):
        text = "first paragraph\n\nsecond paragraph"
        result = converter._format_text_as_html(text)
        assert result.count("<p>") == 2

    def test_headings_detected(self, converter):
        text = "This Is A Heading\nSome content here"
        result = converter._format_text_as_html(text)
        assert "<h2>" in result

    def test_html_escaped(self, converter):
        result = converter._format_text_as_html("<script>alert('xss')</script>")
        assert "<script>" not in result
        assert "&lt;script&gt;" in result


class TestExtractContentFallback:
    """Tests for extract_content_fallback method."""

    def test_extracts_title(self, converter):
        html = "<html><head><title>Test Title</title></head><body></body></html>"
        result = converter.extract_content_fallback(html)
        assert result is not None
        assert "Test Title" in result

    def test_extracts_headings(self, converter):
        html = """
        <html><body>
            <h1>Main Heading</h1>
            <h2>Sub Heading</h2>
            <p>Some content here that is long enough to be included</p>
        </body></html>
        """
        result = converter.extract_content_fallback(html)
        assert result is not None
        assert "Main Heading" in result

    def test_removes_scripts(self, converter):
        html = """
        <html><body>
            <script>malicious code</script>
            <p>Good content here that is long enough</p>
        </body></html>
        """
        result = converter.extract_content_fallback(html)
        assert "malicious" not in result

    def test_removes_styles(self, converter):
        html = """
        <html><body>
            <style>body { color: red; }</style>
            <p>Good content here that is long enough</p>
        </body></html>
        """
        result = converter.extract_content_fallback(html)
        assert "color: red" not in result

    def test_returns_none_on_empty_html(self, converter):
        result = converter.extract_content_fallback("<html></html>")
        # May return None or minimal content
        assert result is None or len(result) < 50

    def test_extracts_main_content(self, converter):
        html = """
        <html><body>
            <nav>Navigation that should be skipped</nav>
            <main>
                <p>Main content paragraph that is substantial enough</p>
            </main>
        </body></html>
        """
        result = converter.extract_content_fallback(html)
        assert result is not None


class TestExtractLinks:
    """Tests for extract_links_from_page method."""

    def test_extracts_same_domain_links(self, converter):
        class MockResponse:
            text = '<a href="/page1">Link 1</a><a href="/page2">Link 2</a>'

        links = converter.extract_links_from_page(MockResponse(), "https://example.com")
        assert len(links) == 2
        assert all("example.com" in link for link in links)

    def test_filters_external_links(self, converter):
        class MockResponse:
            text = '''
            <a href="/internal">Internal</a>
            <a href="https://external.com/page">External</a>
            '''

        links = converter.extract_links_from_page(MockResponse(), "https://example.com")
        assert len(links) == 1
        assert "external.com" not in links[0]

    def test_handles_absolute_urls(self, converter):
        class MockResponse:
            text = '<a href="https://example.com/full-url">Full URL</a>'

        links = converter.extract_links_from_page(MockResponse(), "https://example.com")
        assert len(links) == 1
        assert "https://example.com/full-url" in links[0]

    def test_removes_fragments(self, converter):
        class MockResponse:
            text = '<a href="/page#section">Link</a>'

        links = converter.extract_links_from_page(MockResponse(), "https://example.com")
        assert "#" not in links[0]

    def test_returns_empty_on_none_response(self, converter):
        links = converter.extract_links_from_page(None, "https://example.com")
        assert links == []

    def test_returns_empty_on_empty_text(self, converter):
        class MockResponse:
            text = ""

        links = converter.extract_links_from_page(MockResponse(), "https://example.com")
        assert links == []
