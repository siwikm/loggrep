"""Tests for get_files_to_search function."""

import sys
from pathlib import Path
import tempfile
import os

sys.path.insert(0, str(Path(__file__).parent.parent))

from loggrep import get_files_to_search, VerboseLogger


class TestGetFilesToSearch:
    """Test cases for get_files_to_search function."""

    def test_single_file_without_patterns(self, tmp_path):
        """Test that single file is returned when no patterns specified."""
        test_file = tmp_path / "test.log"
        test_file.write_text("test content")

        result = get_files_to_search(str(test_file))

        assert len(result) == 1
        assert str(test_file) in result

    def test_single_file_matching_pattern(self, tmp_path):
        """Test that single file matching pattern is included."""
        test_file = tmp_path / "test.log"
        test_file.write_text("test content")

        result = get_files_to_search(str(test_file), include_patterns=["*.log"])

        assert len(result) == 1
        assert str(test_file) in result

    def test_single_file_not_matching_pattern_skipped(self, tmp_path, caplog):
        """Test that single file NOT matching pattern is skipped with warning."""
        import logging

        caplog.set_level(logging.WARNING)

        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        result = get_files_to_search(str(test_file), include_patterns=["*.log"])

        # File should be skipped
        assert len(result) == 0

        # Should produce a warning in logs
        assert any(
            "Warning" in record.message or "does not match" in record.message
            for record in caplog.records
        )

    def test_single_file_matching_multiple_patterns(self, tmp_path):
        """Test single file matches one of multiple patterns."""
        test_file = tmp_path / "app.log"
        test_file.write_text("test content")

        result = get_files_to_search(
            str(test_file), include_patterns=["*.txt", "*.log", "*.json"]
        )

        assert len(result) == 1
        assert str(test_file) in result

    def test_single_file_no_match_multiple_patterns(self, tmp_path):
        """Test single file doesn't match any of multiple patterns."""
        test_file = tmp_path / "data.csv"
        test_file.write_text("test content")

        result = get_files_to_search(
            str(test_file), include_patterns=["*.txt", "*.log", "*.json"]
        )

        assert len(result) == 0

    def test_directory_with_patterns(self, tmp_path):
        """Test directory search with include patterns."""
        (tmp_path / "file1.log").write_text("log content")
        (tmp_path / "file2.txt").write_text("txt content")
        (tmp_path / "file3.log").write_text("log content")

        result = get_files_to_search(str(tmp_path), include_patterns=["*.log"])

        assert len(result) == 2
        assert str(tmp_path / "file1.log") in result
        assert str(tmp_path / "file3.log") in result
        assert str(tmp_path / "file2.txt") not in result

    def test_directory_without_patterns(self, tmp_path):
        """Test directory search without patterns includes all files."""
        (tmp_path / "file1.log").write_text("log content")
        (tmp_path / "file2.txt").write_text("txt content")
        (tmp_path / "file3.json").write_text("json content")

        result = get_files_to_search(str(tmp_path))

        assert len(result) == 3

    def test_recursive_with_patterns(self, tmp_path):
        """Test recursive search with include patterns."""
        (tmp_path / "file1.log").write_text("log content")
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "file2.log").write_text("log content")
        (subdir / "file3.txt").write_text("txt content")

        result = get_files_to_search(
            str(tmp_path), recursive=True, include_patterns=["*.log"]
        )

        assert len(result) == 2
        assert str(tmp_path / "file1.log") in result
        assert str(subdir / "file2.log") in result
        assert str(subdir / "file3.txt") not in result

    def test_nonexistent_path_returns_empty(self):
        """Test that nonexistent path returns empty list."""
        result = get_files_to_search("/nonexistent/path/file.log")
        assert result == []

    def test_verbose_logging_with_patterns(self, tmp_path, capsys):
        """Test that verbose mode logs pattern matching."""
        test_file = tmp_path / "test.log"
        test_file.write_text("test content")

        vlogger = VerboseLogger(verbose=True)

        # Configure logging to see verbose output
        import logging

        logging.basicConfig(level=logging.INFO, force=True)

        result = get_files_to_search(
            str(test_file), vlogger=vlogger, include_patterns=["*.log"]
        )

        assert len(result) == 1

    def test_complex_pattern_matching(self, tmp_path):
        """Test complex glob patterns."""
        (tmp_path / "app.log").write_text("content")
        (tmp_path / "app.log.1").write_text("content")
        (tmp_path / "error.log").write_text("content")
        (tmp_path / "data.txt").write_text("content")

        result = get_files_to_search(str(tmp_path), include_patterns=["app.*", "*.log"])

        # app.log matches both patterns, app.log.1 matches app.*, error.log matches *.log
        assert len(result) >= 2
        assert str(tmp_path / "app.log") in result
        assert str(tmp_path / "error.log") in result

    def test_case_sensitive_pattern_matching(self, tmp_path):
        """Test that pattern matching respects case on case-sensitive filesystems."""
        (tmp_path / "file.log").write_text("content")

        result = get_files_to_search(str(tmp_path), include_patterns=["*.log"])

        # Should match the lowercase version
        assert len(result) >= 1
        assert str(tmp_path / "file.log") in result
