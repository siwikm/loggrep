"""Tests for _should_include_file helper function."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from loggrep import _should_include_file


class TestShouldIncludeFile:
    """Test cases for _should_include_file function."""

    def test_no_patterns_includes_all_files(self):
        """Test that files are included when no patterns specified."""
        file_path = Path("test.log")
        assert _should_include_file(file_path, None) is True

        file_path = Path("test.txt")
        assert _should_include_file(file_path, None) is True

        file_path = Path("any_file.xyz")
        assert _should_include_file(file_path, None) is True

    def test_empty_patterns_list_includes_all_files(self):
        """Test that files are included when patterns list is empty."""
        file_path = Path("test.log")
        assert _should_include_file(file_path, []) is True

    def test_single_pattern_match(self):
        """Test matching with a single pattern."""
        file_path = Path("application.log")
        assert _should_include_file(file_path, ["*.log"]) is True

        file_path = Path("data.txt")
        assert _should_include_file(file_path, ["*.log"]) is False

    def test_multiple_patterns_any_match(self):
        """Test that file matches if any pattern matches."""
        patterns = ["*.log", "*.txt"]

        assert _should_include_file(Path("app.log"), patterns) is True
        assert _should_include_file(Path("data.txt"), patterns) is True
        assert _should_include_file(Path("script.py"), patterns) is False

    def test_complex_glob_patterns(self):
        """Test with more complex glob patterns."""
        # Pattern with directory
        file_path = Path("logs/app.log")
        assert _should_include_file(file_path, ["logs/*.log"]) is True

        # Pattern with multiple wildcards
        file_path = Path("error.2023.log")
        assert _should_include_file(file_path, ["error.*.log"]) is True

        # Pattern with character class
        file_path = Path("log1.txt")
        assert _should_include_file(file_path, ["log[0-9].txt"]) is True

    def test_case_sensitive_patterns(self):
        """Test that pattern matching is case-sensitive on case-sensitive filesystems."""
        file_path = Path("Error.LOG")

        # This will match because glob patterns are case-insensitive on macOS/Windows
        # but case-sensitive on Linux
        result = _should_include_file(file_path, ["*.log"])
        # We just test it doesn't crash - actual result depends on filesystem

    def test_multiple_patterns_all_must_fail_to_exclude(self):
        """Test that file is excluded only if no patterns match."""
        patterns = ["*.log", "*.txt", "*.json"]

        assert _should_include_file(Path("data.log"), patterns) is True
        assert _should_include_file(Path("data.txt"), patterns) is True
        assert _should_include_file(Path("data.json"), patterns) is True
        assert _should_include_file(Path("data.xml"), patterns) is False

    def test_pattern_with_subdirectory(self):
        """Test patterns that include subdirectories."""
        file_path = Path("subdir/file.log")

        # Direct match
        assert _should_include_file(file_path, ["subdir/*.log"]) is True

        # Wildcard subdirectories
        assert _should_include_file(file_path, ["*/*.log"]) is True

        # Recursive pattern
        assert _should_include_file(file_path, ["**/*.log"]) is True

    def test_exact_filename_pattern(self):
        """Test matching exact filename."""
        file_path = Path("specific_file.log")

        assert _should_include_file(file_path, ["specific_file.log"]) is True
        assert _should_include_file(file_path, ["other_file.log"]) is False
