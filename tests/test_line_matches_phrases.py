#!/usr/bin/env python3
"""
Unit tests for _line_matches_phrases function.
"""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from loggrep import _line_matches_phrases, _prepare_search_phrases


class TestLineMatchesPhrases:
    """Tests for _line_matches_phrases function."""

    def test_match_all_with_all_phrases_present(self):
        """Should return True when all phrases are in line (match_all=True)."""
        line = "ERROR: database connection failed"
        phrases = ["error", "database"]

        assert (
            _line_matches_phrases(line, phrases, case_sensitive=False, match_all=True)
            is True
        )

    def test_match_all_with_missing_phrase(self):
        """Should return False when any phrase is missing (match_all=True)."""
        line = "ERROR: database connection failed"
        phrases = ["error", "timeout"]

        assert (
            _line_matches_phrases(line, phrases, case_sensitive=False, match_all=True)
            is False
        )

    def test_match_any_with_one_phrase_present(self):
        """Should return True when any phrase is present (match_all=False)."""
        line = "ERROR: database connection failed"
        phrases = ["warning", "error", "timeout"]

        assert (
            _line_matches_phrases(line, phrases, case_sensitive=False, match_all=False)
            is True
        )

    def test_match_any_with_no_phrases_present(self):
        """Should return False when no phrases are present (match_all=False)."""
        line = "INFO: operation successful"
        phrases = ["error", "warning", "timeout"]

        assert (
            _line_matches_phrases(line, phrases, case_sensitive=False, match_all=False)
            is False
        )

    def test_case_sensitive_exact_match(self):
        """Case-sensitive should require exact case match."""
        line = "ERROR: something happened"
        phrases = ["ERROR"]

        assert (
            _line_matches_phrases(line, phrases, case_sensitive=True, match_all=True)
            is True
        )

    def test_case_sensitive_wrong_case(self):
        """Case-sensitive should reject different case."""
        line = "ERROR: something happened"
        phrases = ["error"]  # lowercase

        assert (
            _line_matches_phrases(line, phrases, case_sensitive=True, match_all=True)
            is False
        )

    def test_case_insensitive_matching(self):
        """Case-insensitive should match regardless of case."""
        line = "ERROR: something happened"
        phrases = ["error"]  # already casefolded

        assert (
            _line_matches_phrases(line, phrases, case_sensitive=False, match_all=True)
            is True
        )

    def test_partial_word_matching(self):
        """Should match substrings, not just whole words."""
        line = "database connection established"
        phrases = ["data", "base", "connect"]

        assert (
            _line_matches_phrases(line, phrases, case_sensitive=False, match_all=True)
            is True
        )

    def test_empty_phrases_list(self):
        """Empty phrases list should return True for match_all, False for match_any."""
        line = "some content"

        # all([]) returns True in Python
        assert (
            _line_matches_phrases(line, [], case_sensitive=False, match_all=True)
            is True
        )
        # any([]) returns False in Python
        assert (
            _line_matches_phrases(line, [], case_sensitive=False, match_all=False)
            is False
        )


# Parametrized tests for edge cases
@pytest.mark.parametrize(
    "line,phrases,case_sensitive,match_all,expected",
    [
        # Basic cases
        ("ERROR: failed", ["error"], False, True, True),
        ("ERROR: failed", ["ERROR"], True, True, True),
        ("ERROR: failed", ["error"], True, True, False),
        # Multiple phrases
        ("ERROR: database timeout", ["error", "database"], False, True, True),
        ("ERROR: database timeout", ["error", "missing"], False, True, False),
        ("ERROR: database timeout", ["error", "missing"], False, False, True),
        # Empty and edge cases
        ("", ["error"], False, True, False),
        ("content", [], False, True, True),  # all([]) is True
        ("content", [], False, False, False),  # any([]) is False
        # Unicode
        ("Błąd: połączenie", ["błąd"], False, True, True),
        ("BŁĄD: połączenie", ["błąd"], True, True, False),
    ],
)
def test_line_matching_parametrized(line, phrases, case_sensitive, match_all, expected):
    """Parametrized tests for various line matching scenarios."""
    search_phrases = _prepare_search_phrases(phrases, case_sensitive)
    result = _line_matches_phrases(line, search_phrases, case_sensitive, match_all)
    assert result == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
