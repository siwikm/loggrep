"""Tests for process_window function."""

import sys
from pathlib import Path
from io import StringIO

sys.path.insert(0, str(Path(__file__).parent.parent))

from loggrep import (
    process_window,
    SearchConfig,
    OutputConfig,
    RuntimeConfig,
    VerboseLogger,
)


class TestProcessWindow:
    """Test cases for process_window function."""

    def test_empty_buffer_returns_no_match(self):
        """Test that empty buffer returns no match."""
        search_config = SearchConfig(phrases=["ERROR"], case_sensitive=False)
        output_config = OutputConfig()
        runtime_config = RuntimeConfig(logger=VerboseLogger())

        match_found, should_stop = process_window(
            buffer_lines=[],
            buffer_numbers=[],
            file_path="test.log",
            search_phrases=["error"],
            search_config=search_config,
            output_config=output_config,
            runtime_config=runtime_config,
        )

        assert match_found is False
        assert should_stop is False

    def test_match_all_phrases_present(self):
        """Test window matching when all phrases are present."""
        search_config = SearchConfig(
            phrases=["ERROR", "database"], case_sensitive=False, match_all=True
        )
        output_config = OutputConfig(print_results=False)
        runtime_config = RuntimeConfig(logger=VerboseLogger())

        match_found, should_stop = process_window(
            buffer_lines=["ERROR connecting to database"],
            buffer_numbers=[1],
            file_path="test.log",
            search_phrases=["error", "database"],
            search_config=search_config,
            output_config=output_config,
            runtime_config=runtime_config,
        )

        assert match_found is True
        assert should_stop is False

    def test_match_all_missing_phrase(self):
        """Test window not matching when a phrase is missing in match_all mode."""
        search_config = SearchConfig(
            phrases=["ERROR", "database"], case_sensitive=False, match_all=True
        )
        output_config = OutputConfig()
        runtime_config = RuntimeConfig(logger=VerboseLogger())

        match_found, should_stop = process_window(
            buffer_lines=["ERROR occurred"],
            buffer_numbers=[1],
            file_path="test.log",
            search_phrases=["error", "database"],
            search_config=search_config,
            output_config=output_config,
            runtime_config=runtime_config,
        )

        assert match_found is False
        assert should_stop is False

    def test_match_any_with_one_phrase(self):
        """Test window matching with any phrase when one is present."""
        search_config = SearchConfig(
            phrases=["ERROR", "WARNING"], case_sensitive=False, match_all=False
        )
        output_config = OutputConfig(print_results=False)
        runtime_config = RuntimeConfig(logger=VerboseLogger())

        match_found, should_stop = process_window(
            buffer_lines=["Something WARNING here"],
            buffer_numbers=[1],
            file_path="test.log",
            search_phrases=["error", "warning"],
            search_config=search_config,
            output_config=output_config,
            runtime_config=runtime_config,
        )

        assert match_found is True
        assert should_stop is False

    def test_files_only_stops_after_match(self):
        """Test that files_only mode stops after first match."""
        search_config = SearchConfig(phrases=["ERROR"], case_sensitive=False)
        output_config = OutputConfig(files_only=True, print_results=False)
        runtime_config = RuntimeConfig(logger=VerboseLogger())

        match_found, should_stop = process_window(
            buffer_lines=["ERROR occurred"],
            buffer_numbers=[1],
            file_path="test.log",
            search_phrases=["error"],
            search_config=search_config,
            output_config=output_config,
            runtime_config=runtime_config,
        )

        assert match_found is True
        assert should_stop is True

    def test_count_only_continues_after_match(self):
        """Test that count_only mode continues after match."""
        search_config = SearchConfig(phrases=["ERROR"], case_sensitive=False)
        output_config = OutputConfig(count_only=True)
        runtime_config = RuntimeConfig(logger=VerboseLogger())

        match_found, should_stop = process_window(
            buffer_lines=["ERROR occurred"],
            buffer_numbers=[1],
            file_path="test.log",
            search_phrases=["error"],
            search_config=search_config,
            output_config=output_config,
            runtime_config=runtime_config,
        )

        assert match_found is True
        assert should_stop is False

    def test_case_sensitive_matching(self):
        """Test case-sensitive matching in window."""
        search_config = SearchConfig(phrases=["ERROR"], case_sensitive=True)
        output_config = OutputConfig(print_results=False)
        runtime_config = RuntimeConfig(logger=VerboseLogger())

        # Should match
        match_found, _ = process_window(
            buffer_lines=["ERROR occurred"],
            buffer_numbers=[1],
            file_path="test.log",
            search_phrases=["ERROR"],
            search_config=search_config,
            output_config=output_config,
            runtime_config=runtime_config,
        )
        assert match_found is True

        # Should not match
        match_found, _ = process_window(
            buffer_lines=["error occurred"],
            buffer_numbers=[1],
            file_path="test.log",
            search_phrases=["ERROR"],
            search_config=search_config,
            output_config=output_config,
            runtime_config=runtime_config,
        )
        assert match_found is False

    def test_multiline_window_match(self):
        """Test matching across multiple lines in window."""
        search_config = SearchConfig(
            phrases=["ERROR", "timeout"], case_sensitive=False, match_all=True
        )
        output_config = OutputConfig(print_results=False)
        runtime_config = RuntimeConfig(logger=VerboseLogger())

        match_found, should_stop = process_window(
            buffer_lines=["First line ERROR", "Second line timeout"],
            buffer_numbers=[10, 11],
            file_path="test.log",
            search_phrases=["error", "timeout"],
            search_config=search_config,
            output_config=output_config,
            runtime_config=runtime_config,
        )

        assert match_found is True
        assert should_stop is False
