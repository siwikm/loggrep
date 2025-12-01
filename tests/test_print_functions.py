"""Tests for _print_summary and _print_search_info functions."""

import sys
from pathlib import Path
import argparse

sys.path.insert(0, str(Path(__file__).parent.parent))

from loggrep import _print_summary, _print_search_info


class TestPrintSummary:
    """Test cases for _print_summary function."""

    def test_summary_with_matches_verbose(self, capsys):
        """Test summary output when matches found in verbose mode."""
        args = argparse.Namespace(verbose=True)
        _print_summary(total_matches=25, file_count=3, args=args)

        captured = capsys.readouterr()
        assert "SUMMARY:" in captured.out
        assert "25" in captured.out
        assert "3" in captured.out

    def test_summary_with_matches_non_verbose(self, capsys):
        """Test summary output when matches found in non-verbose mode."""
        args = argparse.Namespace(verbose=False)
        _print_summary(total_matches=10, file_count=2, args=args)

        captured = capsys.readouterr()
        assert "Found 10 lines" in captured.out
        assert "SUMMARY:" not in captured.out

    def test_summary_no_matches_verbose(self, capsys):
        """Test summary output when no matches in verbose mode."""
        args = argparse.Namespace(verbose=True)
        _print_summary(total_matches=0, file_count=5, args=args)

        captured = capsys.readouterr()
        assert "SUMMARY:" in captured.out
        assert "No matching lines found" in captured.out

    def test_summary_no_matches_non_verbose(self, capsys):
        """Test summary output when no matches in non-verbose mode."""
        args = argparse.Namespace(verbose=False)
        _print_summary(total_matches=0, file_count=5, args=args)

        captured = capsys.readouterr()
        assert "No matching lines found" in captured.out
        assert "SUMMARY:" not in captured.out


class TestPrintSearchInfo:
    """Test cases for _print_search_info function."""

    def test_verbose_mode_shows_all_info(self, capsys):
        """Test that verbose mode shows detailed search info."""
        args = argparse.Namespace(
            verbose=True,
            recursive=True,
            phrases=["ERROR", "WARNING"],
            any=False,
            ignore_case=True,
            no_line_numbers=False,
            count=False,
            files_only=False,
            window=1,
        )
        _print_search_info(args, file_count=5)

        captured = capsys.readouterr()
        assert "Mode: recursive" in captured.out
        assert "Search phrases:" in captured.out
        assert "ERROR" in captured.out
        assert "WARNING" in captured.out
        assert "Match mode:" in captured.out
        assert "Case sensitivity:" in captured.out
        assert "Print options:" in captured.out

    def test_verbose_mode_without_recursive(self, capsys):
        """Test verbose mode without recursive flag."""
        args = argparse.Namespace(
            verbose=True,
            recursive=False,
            phrases=["ERROR"],
            any=False,
            ignore_case=False,
            no_line_numbers=False,
            count=False,
            files_only=False,
            window=1,
        )
        _print_search_info(args, file_count=1)

        captured = capsys.readouterr()
        assert "Mode: recursive" not in captured.out
        assert "Search phrases:" in captured.out

    def test_non_verbose_mode_shows_basic_info(self, capsys):
        """Test that non-verbose mode shows minimal info."""
        args = argparse.Namespace(verbose=False, recursive=False)
        _print_search_info(args, file_count=10)

        captured = capsys.readouterr()
        assert "Searching 10 files" in captured.out
        assert "Search phrases:" not in captured.out
        assert "(with recursive option)" not in captured.out

    def test_non_verbose_with_recursive(self, capsys):
        """Test non-verbose mode with recursive flag."""
        args = argparse.Namespace(verbose=False, recursive=True)
        _print_search_info(args, file_count=20)

        captured = capsys.readouterr()
        assert "Searching 20 files" in captured.out
        assert "(with recursive option)" in captured.out

    def test_match_mode_any_phrase(self, capsys):
        """Test output shows 'any phrase' mode correctly."""
        args = argparse.Namespace(
            verbose=True,
            recursive=False,
            phrases=["ERROR", "WARNING"],
            any=True,
            ignore_case=False,
            no_line_numbers=False,
            count=False,
            files_only=False,
            window=1,
        )
        _print_search_info(args, file_count=3)

        captured = capsys.readouterr()
        assert "any phrase" in captured.out

    def test_match_mode_all_phrases(self, capsys):
        """Test output shows 'all phrases' mode correctly."""
        args = argparse.Namespace(
            verbose=True,
            recursive=False,
            phrases=["ERROR", "database"],
            any=False,
            ignore_case=False,
            no_line_numbers=False,
            count=False,
            files_only=False,
            window=1,
        )
        _print_search_info(args, file_count=3)

        captured = capsys.readouterr()
        assert "all phrases" in captured.out

    def test_case_sensitivity_considered(self, capsys):
        """Test output shows case sensitivity status."""
        args = argparse.Namespace(
            verbose=True,
            recursive=False,
            phrases=["ERROR"],
            any=False,
            ignore_case=False,
            no_line_numbers=False,
            count=False,
            files_only=False,
            window=1,
        )
        _print_search_info(args, file_count=1)

        captured = capsys.readouterr()
        assert "considered" in captured.out

    def test_case_sensitivity_ignored(self, capsys):
        """Test output shows case insensitive mode."""
        args = argparse.Namespace(
            verbose=True,
            recursive=False,
            phrases=["ERROR"],
            any=False,
            ignore_case=True,
            no_line_numbers=False,
            count=False,
            files_only=False,
            window=1,
        )
        _print_search_info(args, file_count=1)

        captured = capsys.readouterr()
        assert "ignored" in captured.out
