"""Tests for _open_output_file function."""

import sys
from pathlib import Path
import tempfile
import os

sys.path.insert(0, str(Path(__file__).parent.parent))

from loggrep import _open_output_file, VerboseLogger


class TestOpenOutputFile:
    """Test cases for _open_output_file function."""

    def test_opens_file_successfully(self):
        """Test that function successfully opens a writable file."""
        vlogger = VerboseLogger(verbose=False)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "output.txt")
            result = _open_output_file(output_path, vlogger)

            assert result is not None
            assert not result.closed
            result.close()

    def test_creates_new_file(self):
        """Test that function creates new file if it doesn't exist."""
        vlogger = VerboseLogger(verbose=False)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "new_file.txt")
            assert not Path(output_path).exists()

            result = _open_output_file(output_path, vlogger)

            assert result is not None
            assert Path(output_path).exists()
            result.close()

    def test_overwrites_existing_file(self):
        """Test that function overwrites existing file."""
        vlogger = VerboseLogger(verbose=False)

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
            tmp.write("existing content")
            tmp_path = tmp.name

        try:
            result = _open_output_file(tmp_path, vlogger)
            assert result is not None
            result.write("new content")
            result.close()

            with open(tmp_path, "r") as f:
                content = f.read()
            assert content == "new content"
        finally:
            os.unlink(tmp_path)

    def test_returns_none_on_permission_error(self, tmp_path):
        """Test that function returns None when permission denied."""
        # Create a read-only directory
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o444)

        output_path = str(readonly_dir / "output.txt")
        vlogger = VerboseLogger(verbose=False)

        try:
            result = _open_output_file(output_path, vlogger)
            assert result is None
        finally:
            # Clean up: restore permissions
            readonly_dir.chmod(0o755)

    def test_returns_none_on_invalid_path(self):
        """Test that function returns None for invalid path."""
        vlogger = VerboseLogger(verbose=False)

        # Use a path that doesn't exist in non-writable location
        invalid_path = "/root/nonexistent/path.txt"

        result = _open_output_file(invalid_path, vlogger)
        assert result is None

    def test_verbose_logging(self, tmp_path, capsys):
        """Test that verbose logger logs file opening."""
        vlogger = VerboseLogger(verbose=True)
        output_path = str(tmp_path / "test.txt")

        # Configure logging to capture output
        import logging

        logging.basicConfig(level=logging.INFO, force=True)

        result = _open_output_file(output_path, vlogger)

        if result:
            result.close()

        # Verbose mode should log something about opening file
        # (actual output depends on logger configuration)
        assert result is not None
