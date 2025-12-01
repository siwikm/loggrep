#!/usr/bin/env python3
"""
Unit tests for _validate_file_exists function.
"""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from loggrep import _validate_file_exists


class TestValidateFileExists:
    """Tests for _validate_file_exists function."""

    def test_validates_existing_file(self, tmp_path):
        """Should return True for existing file."""
        test_file = tmp_path / "test.log"
        test_file.write_text("content")

        assert _validate_file_exists(str(test_file)) is True

    def test_rejects_nonexistent_file(self, tmp_path):
        """Should return False for non-existent file."""
        nonexistent = tmp_path / "does_not_exist.log"

        assert _validate_file_exists(str(nonexistent)) is False

    def test_rejects_directory(self, tmp_path):
        """Should return False for directory."""
        directory = tmp_path / "testdir"
        directory.mkdir()

        assert _validate_file_exists(str(directory)) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
