#!/usr/bin/env python3
"""
Integration tests combining multiple helper functions.
Tests the full pipeline of helper functions working together.
"""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from loggrep import (
    _prepare_search_phrases,
    _line_matches_phrases,
    _format_match_output,
)


class TestIntegrationScenarios:
    """Integration tests combining multiple helper functions."""

    def test_full_match_pipeline_case_insensitive(self):
        """Test full pipeline: prepare phrases -> check match -> format output."""
        # Prepare
        phrases = ["ERROR", "Database"]
        search_phrases = _prepare_search_phrases(phrases, case_sensitive=False)

        # Match
        line = "error: database connection failed"
        matches = _line_matches_phrases(
            line, search_phrases, case_sensitive=False, match_all=True
        )

        assert matches is True

        # Format
        output = _format_match_output(
            "/var/log/app.log", 123, line, show_line_numbers=True
        )
        assert output == "/var/log/app.log:123: error: database connection failed"

    def test_full_match_pipeline_case_sensitive(self):
        """Test full pipeline with case-sensitive matching."""
        # Prepare
        phrases = ["ERROR", "Database"]
        search_phrases = _prepare_search_phrases(phrases, case_sensitive=True)

        # Match - should fail due to case
        line = "error: database connection failed"
        matches = _line_matches_phrases(
            line, search_phrases, case_sensitive=True, match_all=True
        )

        assert matches is False

    def test_any_mode_with_one_match(self):
        """Test match_any mode where only one phrase matches."""
        phrases = ["timeout", "ERROR", "warning"]
        search_phrases = _prepare_search_phrases(phrases, case_sensitive=False)

        line = "INFO: operation completed successfully with ERROR in logs"
        matches = _line_matches_phrases(
            line, search_phrases, case_sensitive=False, match_all=False
        )

        assert matches is True

    def test_pipeline_no_match(self):
        """Test pipeline when no phrases match."""
        phrases = ["ERROR", "WARNING"]
        search_phrases = _prepare_search_phrases(phrases, case_sensitive=False)

        line = "INFO: everything is fine"
        matches = _line_matches_phrases(
            line, search_phrases, case_sensitive=False, match_all=True
        )

        assert matches is False

    def test_pipeline_with_unicode(self):
        """Test full pipeline with Unicode content."""
        phrases = ["BŁĄD", "Połączenie"]
        search_phrases = _prepare_search_phrases(phrases, case_sensitive=False)

        line = "błąd: połączenie zostało przerwane"
        matches = _line_matches_phrases(
            line, search_phrases, case_sensitive=False, match_all=True
        )

        assert matches is True

        output = _format_match_output("app.log", 42, line, show_line_numbers=True)
        assert output == "app.log:42: błąd: połączenie zostało przerwane"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
