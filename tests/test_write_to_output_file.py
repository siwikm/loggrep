#!/usr/bin/env python3
"""
Unit tests for _write_to_output_file function.
"""

import pytest
from pathlib import Path
from io import StringIO
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from loggrep import _write_to_output_file, VerboseLogger


class TestWriteToOutputFile:
    """Tests for _write_to_output_file function."""

    def test_writes_to_file(self):
        """Should write content to output file."""
        output = StringIO()
        vlogger = VerboseLogger(verbose=False)
        _write_to_output_file(output, "test content", "/path/file.log", vlogger)

        assert output.getvalue() == "test content\n"

    def test_writes_multiple_lines(self):
        """Should write multiple calls to same file."""
        output = StringIO()
        vlogger = VerboseLogger(verbose=False)
        _write_to_output_file(output, "line 1", "/path/file.log", vlogger)
        _write_to_output_file(output, "line 2", "/path/file.log", vlogger)

        assert output.getvalue() == "line 1\nline 2\n"

    def test_does_nothing_when_no_file(self):
        """Should handle None output_file gracefully."""
        # Should not raise any exception
        vlogger = VerboseLogger(verbose=False)
        _write_to_output_file(None, "content", "/path/file.log", vlogger)

    def test_handles_write_errors(self):
        """Should handle write errors without crashing."""
        # Create a closed file to simulate write error
        output = StringIO()
        output.close()

        # Should not raise exception, just log error if verbose
        vlogger = VerboseLogger(verbose=False)
        _write_to_output_file(output, "content", "/path/file.log", vlogger)

    def test_writes_with_verbose(self):
        """Should still write when verbose=True."""
        output = StringIO()
        vlogger = VerboseLogger(verbose=True)
        _write_to_output_file(output, "test", "/path/file.log", vlogger)

        assert output.getvalue() == "test\n"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
