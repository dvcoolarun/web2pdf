"""Tests for URL to filename generation."""
import pytest
import sys
import os
from unittest.mock import MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock all heavy dependencies before importing main
for mod in ['gevent', 'gevent.monkey', 'grequests', 'weasyprint', 'weasyprint.HTML']:
    sys.modules[mod] = MagicMock()

from main import Web2PDFConverter


@pytest.fixture
def converter():
    return Web2PDFConverter(use_browser=False)


class TestGenerateFilename:
    """Tests for generate_filename_from_url method."""

    def test_root_url_uses_domain(self, converter):
        filename = converter.generate_filename_from_url("https://example.com")
        assert "example_com" in filename

    def test_root_url_strips_www(self, converter):
        filename = converter.generate_filename_from_url("https://www.example.com")
        assert "www" not in filename
        assert "example_com" in filename

    def test_path_uses_last_segment(self, converter):
        filename = converter.generate_filename_from_url("https://example.com/blog/my-post")
        assert "my-post" in filename

    def test_trailing_slash_handled(self, converter):
        filename = converter.generate_filename_from_url("https://example.com/blog/my-post/")
        assert "my-post" in filename

    def test_special_chars_replaced(self, converter):
        filename = converter.generate_filename_from_url("https://example.com/path?query=value&other=123")
        # Should not contain ? or &
        assert "?" not in filename
        assert "&" not in filename

    def test_long_path_truncated(self, converter):
        long_path = "a" * 100
        filename = converter.generate_filename_from_url(f"https://example.com/{long_path}")
        assert len(filename) <= 50

    def test_empty_path_uses_domain(self, converter):
        filename = converter.generate_filename_from_url("https://example.com/")
        assert "example_com" in filename

    def test_nested_path_uses_last_segment(self, converter):
        filename = converter.generate_filename_from_url("https://docs.python.org/3/library/os.html")
        assert "os" in filename

    def test_multiple_underscores_collapsed(self, converter):
        filename = converter.generate_filename_from_url("https://example.com/a___b___c")
        assert "___" not in filename
