"""Tests for Web2PDFConverter initialization and core functionality."""
import pytest
import sys
import os
from unittest.mock import MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

for mod in ['gevent', 'gevent.monkey', 'grequests', 'weasyprint', 'weasyprint.HTML']:
    sys.modules[mod] = MagicMock()

from main import Web2PDFConverter


class TestConverterInit:
    """Tests for Web2PDFConverter initialization."""

    def test_default_init_no_browser(self):
        converter = Web2PDFConverter(use_browser=False)
        assert converter.use_browser is False
        assert hasattr(converter, 'visited_urls')
        assert hasattr(converter, 'all_urls')

    def test_init_with_empty_state(self):
        converter = Web2PDFConverter(use_browser=False)
        assert len(converter.visited_urls) == 0
        assert len(converter.all_urls) == 0

    def test_has_console(self):
        converter = Web2PDFConverter(use_browser=False)
        assert converter.console is not None


class TestCssStyles:
    """Tests for CSS styles constant."""

    def test_css_styles_defined(self):
        from main import css_styles
        assert css_styles is not None
        assert len(css_styles) > 100

    def test_css_has_page_size(self):
        from main import css_styles
        assert "A4" in css_styles

    def test_css_has_page_numbers(self):
        from main import css_styles
        assert "counter(page)" in css_styles

    def test_css_has_font_family(self):
        from main import css_styles
        assert "font-family" in css_styles

    def test_css_has_table_styles(self):
        from main import css_styles
        assert "table" in css_styles
        assert "td" in css_styles
