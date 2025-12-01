"""Unit tests for configuration dataclasses."""

import pytest
from pathlib import Path
import sys
import io

# Add parent directory to path to import loggrep
TESTS_DIR = Path(__file__).parent
LOGGREP_PATH = TESTS_DIR.parent
sys.path.insert(0, str(LOGGREP_PATH))

from loggrep import SearchConfig, OutputConfig, RuntimeConfig


class TestSearchConfig:
    """Tests for SearchConfig dataclass."""

    def test_default_values(self):
        """Test SearchConfig with default values."""
        config = SearchConfig(phrases=["error", "warning"])

        assert config.phrases == ["error", "warning"]
        assert config.case_sensitive is False
        assert config.match_all is True
        assert config.window_size == 1

    def test_custom_values(self):
        """Test SearchConfig with custom values."""
        config = SearchConfig(
            phrases=["ERROR"], case_sensitive=True, match_all=False, window_size=3
        )

        assert config.phrases == ["ERROR"]
        assert config.case_sensitive is True
        assert config.match_all is False
        assert config.window_size == 3

    def test_empty_phrases_list(self):
        """Test SearchConfig with empty phrases list."""
        config = SearchConfig(phrases=[])
        assert config.phrases == []

    def test_single_phrase(self):
        """Test SearchConfig with single phrase."""
        config = SearchConfig(phrases=["error"])
        assert config.phrases == ["error"]
        assert len(config.phrases) == 1

    def test_window_size_zero(self):
        """Test SearchConfig with window_size=0."""
        config = SearchConfig(phrases=["test"], window_size=0)
        assert config.window_size == 0

    def test_window_size_large(self):
        """Test SearchConfig with large window_size."""
        config = SearchConfig(phrases=["test"], window_size=100)
        assert config.window_size == 100


class TestOutputConfig:
    """Tests for OutputConfig dataclass."""

    def test_default_values(self):
        """Test OutputConfig with default values."""
        config = OutputConfig()

        assert config.output_file is None
        assert config.show_line_numbers is True
        assert config.print_results is True
        assert config.count_only is False
        assert config.files_only is False

    def test_custom_values(self):
        """Test OutputConfig with custom values."""
        output_file = io.StringIO()
        config = OutputConfig(
            output_file=output_file,
            show_line_numbers=False,
            print_results=False,
            count_only=True,
            files_only=False,
        )

        assert config.output_file == output_file
        assert config.show_line_numbers is False
        assert config.print_results is False
        assert config.count_only is True
        assert config.files_only is False

    def test_files_only_mode(self):
        """Test OutputConfig for files-only mode (like grep -l)."""
        config = OutputConfig(files_only=True)
        assert config.files_only is True
        assert config.count_only is False

    def test_count_only_mode(self):
        """Test OutputConfig for count-only mode (like grep -c)."""
        config = OutputConfig(count_only=True)
        assert config.count_only is True
        assert config.files_only is False

    def test_mutually_exclusive_modes(self):
        """Test that count_only and files_only can both be set (caller's responsibility)."""
        # Note: It's the caller's responsibility to ensure these are mutually exclusive
        config = OutputConfig(count_only=True, files_only=True)
        assert config.count_only is True
        assert config.files_only is True


class TestRuntimeConfig:
    """Tests for RuntimeConfig dataclass."""

    def test_default_values(self):
        """Test RuntimeConfig with default values."""
        config = RuntimeConfig()

        assert config.verbose is False
        assert config.recursive is False
        assert config.include_patterns is None

    def test_custom_values(self):
        """Test RuntimeConfig with custom values."""
        config = RuntimeConfig(
            verbose=True, recursive=True, include_patterns=["*.log", "*.txt"]
        )

        assert config.verbose is True
        assert config.recursive is True
        assert config.include_patterns == ["*.log", "*.txt"]

    def test_single_include_pattern(self):
        """Test RuntimeConfig with single include pattern."""
        config = RuntimeConfig(include_patterns=["*.xml"])
        assert config.include_patterns == ["*.xml"]
        assert len(config.include_patterns) == 1

    def test_empty_include_patterns(self):
        """Test RuntimeConfig with empty include patterns list."""
        config = RuntimeConfig(include_patterns=[])
        assert config.include_patterns == []

    def test_recursive_without_patterns(self):
        """Test RuntimeConfig with recursive but no patterns."""
        config = RuntimeConfig(recursive=True, include_patterns=None)
        assert config.recursive is True
        assert config.include_patterns is None


class TestConfigIntegration:
    """Integration tests for using configs together."""

    def test_typical_search_scenario(self):
        """Test creating all configs for a typical search."""
        search_config = SearchConfig(
            phrases=["error", "warning"],
            case_sensitive=False,
            match_all=False,
            window_size=1,
        )
        output_config = OutputConfig(show_line_numbers=True, print_results=True)
        runtime_config = RuntimeConfig(
            verbose=True, recursive=True, include_patterns=["*.log"]
        )

        assert search_config.phrases == ["error", "warning"]
        assert output_config.show_line_numbers is True
        assert runtime_config.recursive is True

    def test_window_search_scenario(self):
        """Test creating configs for window search."""
        search_config = SearchConfig(
            phrases=["database", "connection", "failed"], match_all=True, window_size=3
        )
        output_config = OutputConfig(show_line_numbers=True)
        runtime_config = RuntimeConfig(verbose=False)

        assert search_config.window_size == 3
        assert search_config.match_all is True
        assert len(search_config.phrases) == 3

    def test_count_only_scenario(self):
        """Test creating configs for count-only mode."""
        search_config = SearchConfig(phrases=["ERROR"])
        output_config = OutputConfig(count_only=True, print_results=False)
        runtime_config = RuntimeConfig()

        assert output_config.count_only is True
        assert output_config.print_results is False
