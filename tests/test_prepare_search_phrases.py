#!/usr/bin/env python3
"""
Unit tests for _prepare_search_phrases function.
"""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from loggrep import _prepare_search_phrases


class TestPrepareSearchPhrases:
    """Tests for _prepare_search_phrases function."""

    def test_case_sensitive_returns_original(self):
        """Case-sensitive mode should return phrases unchanged."""
        phrases = ["ERROR", "Warning", "Info"]
        result = _prepare_search_phrases(phrases, case_sensitive=True)

        assert result == phrases
        assert result is phrases  # Should be same object

    def test_case_insensitive_casefolding(self):
        """Case-insensitive mode should casefold all phrases."""
        phrases = ["ERROR", "Warning", "Info"]
        result = _prepare_search_phrases(phrases, case_sensitive=False)

        assert result == ["error", "warning", "info"]

    def test_case_insensitive_unicode(self):
        """Should handle Unicode properly with casefold."""
        phrases = ["ĄĆĘŁŃÓŚŹŻ", "Straße"]  # Polish chars, German ß
        result = _prepare_search_phrases(phrases, case_sensitive=False)

        # casefold() handles Unicode better than lower()
        assert result[0] == "ąćęłńóśźż"
        assert result[1] == "strasse"  # ß becomes ss

    def test_empty_phrases(self):
        """Should handle empty phrase list."""
        result = _prepare_search_phrases([], case_sensitive=False)
        assert result == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
