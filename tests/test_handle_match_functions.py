"""Tests for _handle_files_only_match and _handle_normal_match functions."""

import sys
from pathlib import Path
from io import StringIO

sys.path.insert(0, str(Path(__file__).parent.parent))

from loggrep import (
    _handle_files_only_match,
    _handle_normal_match,
    OutputConfig,
    RuntimeConfig,
    VerboseLogger,
)


class TestHandleFilesOnlyMatch:
    """Test cases for _handle_files_only_match function."""

    def test_prints_filename_once(self, capsys):
        """Test that function prints filename when print_results is True."""
        output_config = OutputConfig(files_only=True, print_results=True)
        runtime_config = RuntimeConfig(logger=VerboseLogger())

        _handle_files_only_match("test.log", output_config, runtime_config)

        captured = capsys.readouterr()
        assert "test.log" in captured.out

    def test_no_print_when_disabled(self, capsys):
        """Test that function doesn't print when print_results is False."""
        output_config = OutputConfig(files_only=True, print_results=False)
        runtime_config = RuntimeConfig(logger=VerboseLogger())

        _handle_files_only_match("test.log", output_config, runtime_config)

        captured = capsys.readouterr()
        assert captured.out == ""


class TestHandleNormalMatch:
    """Test cases for _handle_normal_match function."""

    def test_prints_with_line_numbers(self, capsys):
        """Test printing match with line numbers."""
        output_config = OutputConfig(
            show_line_numbers=True, print_results=True, output_file=None
        )
        runtime_config = RuntimeConfig(logger=VerboseLogger())

        _handle_normal_match(
            file_path="test.log",
            line_num=42,
            line_content="ERROR: something failed",
            output_config=output_config,
            runtime_config=runtime_config,
        )

        captured = capsys.readouterr()
        assert "test.log:42: ERROR: something failed" in captured.out

    def test_prints_without_line_numbers(self, capsys):
        """Test printing match without line numbers."""
        output_config = OutputConfig(
            show_line_numbers=False, print_results=True, output_file=None
        )
        runtime_config = RuntimeConfig(logger=VerboseLogger())

        _handle_normal_match(
            file_path="test.log",
            line_num=42,
            line_content="ERROR: something failed",
            output_config=output_config,
            runtime_config=runtime_config,
        )

        captured = capsys.readouterr()
        assert "test.log: ERROR: something failed" in captured.out
        assert ":42:" not in captured.out

    def test_no_print_when_disabled(self, capsys):
        """Test that function doesn't print when print_results is False."""
        output_config = OutputConfig(show_line_numbers=True, print_results=False)
        runtime_config = RuntimeConfig(logger=VerboseLogger())

        _handle_normal_match(
            file_path="test.log",
            line_num=42,
            line_content="ERROR: something failed",
            output_config=output_config,
            runtime_config=runtime_config,
        )

        captured = capsys.readouterr()
        assert captured.out == ""

    def test_writes_to_output_file(self, tmp_path):
        """Test writing match to output file."""
        output_file_path = tmp_path / "output.txt"
        with open(output_file_path, "w") as f:
            output_config = OutputConfig(
                show_line_numbers=True, print_results=False, output_file=f
            )
            runtime_config = RuntimeConfig(logger=VerboseLogger())

            _handle_normal_match(
                file_path="test.log",
                line_num=10,
                line_content="WARNING: disk space low",
                output_config=output_config,
                runtime_config=runtime_config,
            )

        with open(output_file_path, "r") as f:
            content = f.read()
        assert "test.log:10: WARNING: disk space low" in content

    def test_handles_special_characters(self, capsys):
        """Test handling lines with special characters."""
        output_config = OutputConfig(show_line_numbers=True, print_results=True)
        runtime_config = RuntimeConfig(logger=VerboseLogger())

        _handle_normal_match(
            file_path="test.log",
            line_num=1,
            line_content="Tab\there and 'quotes' and \"double\"",
            output_config=output_config,
            runtime_config=runtime_config,
        )

        captured = capsys.readouterr()
        assert "Tab\there" in captured.out
        assert "'quotes'" in captured.out
        assert '"double"' in captured.out
