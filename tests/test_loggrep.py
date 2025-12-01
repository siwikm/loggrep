#!/usr/bin/env python3
"""
Pytest test suite for loggrep functionality.
Tests against files in the /tests directory.
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
import pytest

# Assume loggrep.py is in the parent directory
SCRIPT_DIR = Path(__file__).parent
LOGGREP_PATH = SCRIPT_DIR.parent / "loggrep.py"
TESTS_DIR = SCRIPT_DIR / "test_files"


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    tmp_dir = tempfile.mkdtemp()
    yield Path(tmp_dir)
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)


@pytest.fixture
def temp_file():
    """Create a temporary file for tests."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as tmp:
        tmp_path = tmp.name
    yield tmp_path
    if os.path.exists(tmp_path):
        os.unlink(tmp_path)


def run_loggrep(args, capture_output=True):
    """Run loggrep.py with given arguments and return result."""
    cmd = [sys.executable, str(LOGGREP_PATH)] + args
    if capture_output:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    else:
        result = subprocess.run(cmd)
        return result.returncode, "", ""


class TestBasicSearch:
    """Tests for basic search functionality."""

    def test_basic_search(self):
        """Test basic search functionality."""
        returncode, stdout, stderr = run_loggrep([str(TESTS_DIR / "t2.log"), "ERROR"])

        assert returncode == 0
        lines = stdout.strip().split("\n")
        matching_lines = [line for line in lines if ":" in line and "ERROR" in line]
        assert len(matching_lines) > 0, "Should find at least one line with ERROR"

    def test_multiple_phrases_all(self):
        """Test search with multiple phrases (ALL mode)."""
        returncode, stdout, stderr = run_loggrep(
            [str(TESTS_DIR / "t2.log"), "task_runner", "Starting"]
        )

        assert returncode == 0
        lines = stdout.strip().split("\n")
        matching_lines = [
            line for line in lines if "task_runner" in line and "Starting" in line
        ]
        assert len(matching_lines) > 0, "Should find lines with both phrases"

    def test_multiple_phrases_any(self):
        """Test search with multiple phrases (ANY mode)."""
        returncode, stdout, stderr = run_loggrep(
            [str(TESTS_DIR / "t2.log"), "ERROR", "BadRequest", "--any"]
        )

        assert returncode == 0
        lines = stdout.strip().split("\n")
        matching_lines = [
            line
            for line in lines
            if ":" in line and ("ERROR" in line or "BadRequest" in line)
        ]
        assert len(matching_lines) > 0, "Should find lines with either phrase"

    def test_case_insensitive(self):
        """Test case-insensitive search."""
        returncode, stdout, stderr = run_loggrep(
            [str(TESTS_DIR / "t2.log"), "error", "--ignore-case"]
        )

        assert returncode == 0
        lines = stdout.strip().split("\n")
        matching_lines = [
            line for line in lines if ":" in line and "error" in line.lower()
        ]
        assert len(matching_lines) > 0, (
            "Should find lines with 'error' (case-insensitive)"
        )

    def test_json_search(self):
        """Test search in JSON file."""
        returncode, stdout, stderr = run_loggrep(
            [str(TESTS_DIR / "t1.json"), "cardStatus"]
        )

        assert returncode == 0
        lines = stdout.strip().split("\n")
        matching_lines = [
            line for line in lines if ":" in line and "cardStatus" in line
        ]
        assert len(matching_lines) > 0, "Should find lines with 'cardStatus'"

    def test_directory_search(self):
        """Test directory search."""
        returncode, stdout, stderr = run_loggrep([str(TESTS_DIR), "ERROR"])

        assert returncode == 0
        lines = stdout.strip().split("\n")
        matching_lines = [line for line in lines if ":" in line and "ERROR" in line]
        assert len(matching_lines) > 0, (
            "Should find lines with 'ERROR' across directory"
        )

        # Count files mentioned
        files = set()
        for line in matching_lines:
            if ":" in line:
                file_part = line.split(":")[0]
                files.add(file_part)
        assert len(files) > 0, "Should find matches in at least one file"


class TestOutputModes:
    """Tests for different output modes."""

    def test_count_mode(self):
        """Test count-only mode."""
        returncode, stdout, stderr = run_loggrep(
            [str(TESTS_DIR / "t2.log"), "INFO", "-c"]
        )

        assert returncode == 0
        # Output should contain count information
        assert ":" in stdout, "Should show file:count format"

    def test_files_only_mode(self):
        """Test files-only mode."""
        returncode, stdout, stderr = run_loggrep([str(TESTS_DIR), "cardType", "-l"])

        assert returncode == 0
        files = [line.strip() for line in stdout.strip().split("\n") if line.strip()]
        assert len(files) > 0, "Should list files containing 'cardType'"

    def test_output_to_file(self, temp_file):
        """Test output to file."""
        returncode, stdout, stderr = run_loggrep(
            [str(TESTS_DIR / "t2.log"), "Success", "-o", temp_file]
        )

        assert returncode == 0
        assert os.path.exists(temp_file), "Output file should be created"

        with open(temp_file, "r") as f:
            content = f.read()
        lines = [line for line in content.strip().split("\n") if line.strip()]
        assert len(lines) > 0, "Output file should contain matches"

    def test_no_line_numbers(self):
        """Test --no-line-numbers option."""
        returncode, stdout, stderr = run_loggrep(
            [str(TESTS_DIR / "t2.log"), "ERROR", "--no-line-numbers"]
        )

        assert returncode == 0
        lines = stdout.strip().split("\n")
        matching_lines = [
            line for line in lines if "ERROR" in line and not line.startswith("Found")
        ]

        # Check if line numbers are absent
        has_line_numbers = any(
            ":" in line and line.split(":")[1].strip().isdigit()
            for line in matching_lines
        )
        assert not has_line_numbers, "Line numbers should be removed from output"

    def test_verbose_mode(self):
        """Test verbose mode."""
        returncode, stdout, stderr = run_loggrep(
            [str(TESTS_DIR / "t2.log"), "ERROR", "-v"]
        )

        assert returncode == 0
        verbose_indicators = [
            "Starting search",
            "Searching file:",
            "Search completed",
            "SUMMARY:",
        ]

        found_verbose = sum(
            1 for indicator in verbose_indicators if indicator in stdout
        )
        assert found_verbose >= 2, "Should show verbose output indicators"


class TestWindowSearch:
    """Tests for window search functionality."""

    def test_window_exact_size(self, temp_file):
        """Test --window with a file whose length equals the window size."""
        content = """[2025-01-06 10:00:01] INFO: Job started
[2025-01-06 10:00:02] ERROR: Connection lost
[2025-01-06 10:00:03] INFO: database reconnect scheduled
"""
        with open(temp_file, "w") as f:
            f.write(content)

        returncode, stdout, stderr = run_loggrep(
            [temp_file, "ERROR", "database", "--window", "3"]
        )

        assert returncode == 0
        assert "database reconnect scheduled" in stdout, (
            "Should find phrases across window"
        )

    def test_window_partial_tail(self, temp_file):
        """Test --window on a file shorter than the requested window."""
        content = """[2025-01-06 11:00:01] INFO: Starting cleanup
[2025-01-06 11:00:02] ERROR: Cleanup failed
[2025-01-06 11:00:03] INFO: timeout waiting for resource
"""
        with open(temp_file, "w") as f:
            f.write(content)

        returncode, stdout, stderr = run_loggrep(
            [temp_file, "ERROR", "timeout", "--window", "5"]
        )

        assert returncode == 0
        assert "timeout waiting for resource" in stdout, (
            "Should handle partial window at file end"
        )


class TestIncludePatterns:
    """Tests for file extension filtering with --include flag."""

    def test_single_pattern(self, temp_dir):
        """Test single pattern (*.log)."""
        # Create test files
        (temp_dir / "app.log").write_text("ERROR: database connection failed\n")
        (temp_dir / "server.log").write_text("ERROR: timeout occurred\n")
        (temp_dir / "data.txt").write_text("ERROR: file not found\n")
        (temp_dir / "readme.md").write_text("ERROR: this should not match\n")

        returncode, stdout, stderr = run_loggrep(
            [str(temp_dir), "ERROR", "-r", "-e", "*.log"]
        )

        assert returncode == 0
        assert "app.log" in stdout, "Should match app.log"
        assert "server.log" in stdout, "Should match server.log"
        assert "data.txt" not in stdout, "Should not match data.txt"
        assert "readme.md" not in stdout, "Should not match readme.md"

    def test_multiple_patterns(self, temp_dir):
        """Test multiple patterns (*.log and *.txt)."""
        # Create test files
        (temp_dir / "app.log").write_text("ERROR: database connection failed\n")
        (temp_dir / "server.log").write_text("ERROR: timeout occurred\n")
        (temp_dir / "data.txt").write_text("ERROR: file not found\n")
        (temp_dir / "readme.md").write_text("ERROR: this should not match\n")
        (temp_dir / "config.json").write_text('{"error": "ERROR: json error"}\n')

        returncode, stdout, stderr = run_loggrep(
            [str(temp_dir), "ERROR", "-r", "-e", "*.log", "-e", "*.txt"]
        )

        assert returncode == 0
        assert "app.log" in stdout, "Should match app.log"
        assert "server.log" in stdout, "Should match server.log"
        assert "data.txt" in stdout, "Should match data.txt"
        assert "readme.md" not in stdout, "Should not match readme.md"
        assert "config.json" not in stdout, "Should not match config.json"

    def test_no_matches_pattern(self, temp_dir):
        """Test pattern with no matches."""
        # Create test files
        (temp_dir / "app.log").write_text("ERROR: database connection failed\n")
        (temp_dir / "server.log").write_text("ERROR: timeout occurred\n")

        returncode, stdout, stderr = run_loggrep(
            [str(temp_dir), "ERROR", "-r", "-e", "*.xml"]
        )

        assert returncode == 0
        # When no files match the pattern, should indicate which patterns didn't match
        assert "No files found matching patterns: *.xml" in stdout, (
            "Should indicate which patterns didn't match any files"
        )


# Parametrized tests for edge cases
@pytest.mark.parametrize(
    "search_term,expected_found",
    [
        ("ERROR", True),
        ("NONEXISTENT_PHRASE_12345", False),
    ],
)
def test_search_term_presence(search_term, expected_found):
    """Test search with terms that should/shouldn't be found."""
    returncode, stdout, stderr = run_loggrep([str(TESTS_DIR / "t2.log"), search_term])

    assert returncode == 0
    if expected_found:
        assert search_term in stdout or "Found" in stdout
    else:
        assert "No matching lines found" in stdout


if __name__ == "__main__":
    # Run pytest with verbose output
    pytest.main([__file__, "-v"])
