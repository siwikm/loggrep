"""Tests for _format_window_output function."""

import sys
from pathlib import Path

# Add parent directory to path to import loggrep
sys.path.insert(0, str(Path(__file__).parent.parent))

from loggrep import _format_window_output


class TestFormatWindowOutput:
    """Test cases for _format_window_output function."""

    def test_format_with_line_numbers_single_line(self):
        """Test formatting window with line numbers for single line."""
        result = _format_window_output(
            file_path="test.log",
            buffer_lines=["ERROR: something failed"],
            buffer_numbers=[42],
            show_line_numbers=True,
        )
        assert result == "test.log:42-42:\n42: ERROR: something failed"

    def test_format_with_line_numbers_multiple_lines(self):
        """Test formatting window with line numbers for multiple lines."""
        result = _format_window_output(
            file_path="app.log",
            buffer_lines=["Line 1 content", "Line 2 content", "Line 3 content"],
            buffer_numbers=[10, 11, 12],
            show_line_numbers=True,
        )
        expected = (
            "app.log:10-12:\n"
            "10: Line 1 content\n"
            "  11: Line 2 content\n"
            "  12: Line 3 content"
        )
        assert result == expected

    def test_format_without_line_numbers_single_line(self):
        """Test formatting window without line numbers for single line."""
        result = _format_window_output(
            file_path="test.log",
            buffer_lines=["ERROR: something failed"],
            buffer_numbers=[42],
            show_line_numbers=False,
        )
        assert result == "test.log:\n  ERROR: something failed"

    def test_format_without_line_numbers_multiple_lines(self):
        """Test formatting window without line numbers for multiple lines."""
        result = _format_window_output(
            file_path="app.log",
            buffer_lines=["Line 1", "Line 2", "Line 3"],
            buffer_numbers=[10, 11, 12],
            show_line_numbers=False,
        )
        expected = "app.log:\n  Line 1\n  Line 2\n  Line 3"
        assert result == expected

    def test_format_with_special_characters(self):
        """Test formatting preserves special characters."""
        result = _format_window_output(
            file_path="test.log",
            buffer_lines=["Tab\there", "Quote'test", 'Double"quote'],
            buffer_numbers=[1, 2, 3],
            show_line_numbers=True,
        )
        assert "Tab\there" in result
        assert "Quote'test" in result
        assert 'Double"quote' in result

    def test_format_with_unicode_content(self):
        """Test formatting with Unicode content."""
        result = _format_window_output(
            file_path="unicode.log",
            buffer_lines=["Błąd: połączenie", "错误信息", "エラー"],
            buffer_numbers=[5, 6, 7],
            show_line_numbers=True,
        )
        assert "Błąd: połączenie" in result
        assert "错误信息" in result
        assert "エラー" in result

    def test_format_preserves_whitespace(self):
        """Test that formatting preserves leading/trailing whitespace."""
        result = _format_window_output(
            file_path="test.log",
            buffer_lines=["  indented", "normal", "    more indent"],
            buffer_numbers=[1, 2, 3],
            show_line_numbers=False,
        )
        assert "  indented" in result
        assert "    more indent" in result
