#!/usr/bin/env python3
"""
Unit tests for _format_match_output function.
"""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from loggrep import _format_match_output


class TestFormatMatchOutput:
    """Tests for _format_match_output function."""

    def test_format_with_line_numbers(self):
        """Should include line numbers when show_line_numbers=True."""
        result = _format_match_output(
            "/path/to/file.log", 42, "ERROR: something failed", show_line_numbers=True
        )

        assert result == "/path/to/file.log:42: ERROR: something failed"

    def test_format_without_line_numbers(self):
        """Should omit line numbers when show_line_numbers=False."""
        result = _format_match_output(
            "/path/to/file.log", 42, "ERROR: something failed", show_line_numbers=False
        )

        assert result == "/path/to/file.log: ERROR: something failed"

    def test_format_preserves_content(self):
        """Should preserve original line content including whitespace."""
        content = "  ERROR: indented content\t"
        result = _format_match_output("file.log", 1, content, show_line_numbers=True)

        assert content in result
        assert result == f"file.log:1: {content}"

    def test_format_with_special_characters(self):
        """Should handle special characters in content."""
        content = 'ERROR: JSON {"key": "value"}'
        result = _format_match_output("file.log", 10, content, show_line_numbers=True)

        assert result == f"file.log:10: {content}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
