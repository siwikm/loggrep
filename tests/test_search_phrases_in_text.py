"""Tests for search_phrases_in_text function."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from loggrep import search_phrases_in_text


class TestSearchPhrasesInText:
    """Test cases for search_phrases_in_text function."""

    def test_basic_search_returns_matches(self):
        """Test basic search returns matching lines."""
        text = "Line 1\nERROR occurred\nLine 3\nERROR again"
        result = search_phrases_in_text(text, ["ERROR"])
        assert len(result) == 2
        assert "ERROR occurred" in result[0]
        assert "ERROR again" in result[1]

    def test_empty_text_returns_empty_list(self):
        """Test that empty text returns empty list."""
        result = search_phrases_in_text("", ["ERROR"])
        assert result == []

    def test_no_matches_returns_empty_list(self):
        """Test that no matches returns empty list."""
        text = "Line 1\nLine 2\nLine 3"
        result = search_phrases_in_text(text, ["ERROR"])
        assert result == []

    def test_case_insensitive_by_default(self):
        """Test that search is case-insensitive by default."""
        text = "error occurred\nERROR again\nError here"
        result = search_phrases_in_text(text, ["ERROR"])
        assert len(result) == 3

    def test_case_sensitive_when_specified(self):
        """Test case-sensitive search when case_sensitive=True."""
        text = "error occurred\nERROR again\nError here"
        result = search_phrases_in_text(text, ["ERROR"], case_sensitive=True)
        assert len(result) == 1
        assert "ERROR again" in result[0]

    def test_match_all_phrases(self):
        """Test that all phrases must be present."""
        text = "Line with ERROR and database\nLine with only ERROR"
        result = search_phrases_in_text(text, ["ERROR", "database"], match_all=True)
        assert len(result) == 1
        assert "ERROR and database" in result[0]

    def test_match_any_phrase(self):
        """Test that any phrase can match."""
        text = "Line with ERROR\nLine with WARNING\nLine with nothing"
        result = search_phrases_in_text(text, ["ERROR", "WARNING"], match_all=False)
        assert len(result) == 2

    def test_multiple_phrases_in_one_line(self):
        """Test line matching multiple phrases."""
        text = "ERROR: database connection failed"
        result = search_phrases_in_text(text, ["ERROR", "database", "failed"])
        assert len(result) == 1
        assert "ERROR: database connection failed" in result[0]

    def test_preserves_line_content(self):
        """Test that line content is in output (note: whitespace is stripped)."""
        text = "  Line with spaces  \nTab\there"
        result = search_phrases_in_text(text, ["Line"])
        # Function strips whitespace and adds line numbers
        assert "Line with spaces" in result[0]
        assert "1:" in result[0]

    def test_empty_phrases_returns_empty_list(self):
        """Test that empty phrases list returns empty list."""
        text = "Line 1\nLine 2"
        result = search_phrases_in_text(text, [])
        # With empty phrases, match_all returns [] (no phrases to match)
        assert result == []

    def test_multiline_text_with_windows_line_endings(self):
        """Test handling text with Windows-style line endings."""
        text = "Line 1\r\nERROR here\r\nLine 3"
        result = search_phrases_in_text(text, ["ERROR"])
        assert len(result) == 1
        assert "ERROR here" in result[0]

    def test_unicode_content(self):
        """Test search with Unicode content."""
        text = "Błąd połączenia\n错误信息\nエラー"
        result = search_phrases_in_text(text, ["Błąd"])
        assert len(result) == 1
        assert "Błąd połączenia" in result[0]

    def test_special_characters_in_phrases(self):
        """Test search with special characters."""
        text = "Error: file.txt not found\nWarning: [CRITICAL]"
        result = search_phrases_in_text(text, ["file.txt"])
        assert len(result) == 1
        assert "file.txt not found" in result[0]
