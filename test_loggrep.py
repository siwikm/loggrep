#!/usr/bin/env python3
"""
Test file for loggrep functionality.
Tests against files in the /tests directory.
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path

# Assume loggrep.py is in the same directory as this test file
SCRIPT_DIR = Path(__file__).parent
LOGGREP_PATH = SCRIPT_DIR / "loggrep.py"
TESTS_DIR = SCRIPT_DIR / "tests"


def run_loggrep(args, capture_output=True):
    """Run loggrep.py with given arguments and return result."""
    cmd = [sys.executable, str(LOGGREP_PATH)] + args
    if capture_output:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    else:
        result = subprocess.run(cmd)
        return result.returncode, "", ""


def test_basic_search():
    """Test basic search functionality."""
    print("Test 1: Basic search in t2.log for 'ERROR'")

    returncode, stdout, stderr = run_loggrep([str(TESTS_DIR / "t2.log"), "ERROR"])

    if returncode == 0:
        lines = stdout.strip().split("\n")
        # Filter out summary lines
        matching_lines = [line for line in lines if ":" in line and "ERROR" in line]
        print(f"  ✓ Found {len(matching_lines)} lines with ERROR")
        if matching_lines:
            print(f"  Example: {matching_lines[0][:200]}...")
    else:
        print(f"  ✗ Failed with code {returncode}")
        print(f"  stderr: {stderr}")
    print()


def test_multiple_phrases_all():
    """Test search with multiple phrases (ALL mode)."""
    print("Test 2: Search for lines containing both 'task_runner' AND 'Starting'")

    returncode, stdout, stderr = run_loggrep(
        [str(TESTS_DIR / "t2.log"), "task_runner", "Starting"]
    )

    if returncode == 0:
        lines = stdout.strip().split("\n")
        matching_lines = [
            line for line in lines if "task_runner" in line and "Starting" in line
        ]
        print(f"  ✓ Found {len(matching_lines)} lines with both phrases")
        if matching_lines:
            print(f"  Example: {matching_lines[0][:80]}...")
    else:
        print(f"  ✗ Failed with code {returncode}")
    print()


def test_multiple_phrases_any():
    """Test search with multiple phrases (ANY mode)."""
    print("Test 3: Search for lines containing 'ERROR' OR 'BadRequest' (--any)")

    returncode, stdout, stderr = run_loggrep(
        [str(TESTS_DIR / "t2.log"), "ERROR", "BadRequest", "--any"]
    )

    if returncode == 0:
        lines = stdout.strip().split("\n")
        matching_lines = [
            line
            for line in lines
            if ":" in line and ("ERROR" in line or "BadRequest" in line)
        ]
        print(f"  ✓ Found {len(matching_lines)} lines with either phrase")
        if matching_lines:
            print(f"  Example: {matching_lines[0][:80]}...")
    else:
        print(f"  ✗ Failed with code {returncode}")
    print()


def test_case_insensitive():
    """Test case-insensitive search."""
    print("Test 4: Case-insensitive search for 'error' (--ignore-case)")

    returncode, stdout, stderr = run_loggrep(
        [str(TESTS_DIR / "t2.log"), "error", "--ignore-case"]
    )

    if returncode == 0:
        lines = stdout.strip().split("\n")
        matching_lines = [
            line for line in lines if ":" in line and "error" in line.lower()
        ]
        print(f"  ✓ Found {len(matching_lines)} lines with 'error' (case-insensitive)")
        if matching_lines:
            print(f"  Example: {matching_lines[0][:80]}...")
    else:
        print(f"  ✗ Failed with code {returncode}")
    print()


def test_json_search():
    """Test search in JSON file."""
    print("Test 5: Search in JSON file for 'cardStatus'")

    returncode, stdout, stderr = run_loggrep([str(TESTS_DIR / "t1.json"), "cardStatus"])

    if returncode == 0:
        lines = stdout.strip().split("\n")
        matching_lines = [
            line for line in lines if ":" in line and "cardStatus" in line
        ]
        print(f"  ✓ Found {len(matching_lines)} lines with 'cardStatus'")
        if matching_lines:
            print(f"  Example: {matching_lines[0][:80]}...")
    else:
        print(f"  ✗ Failed with code {returncode}")
    print()


def test_directory_search():
    """Test directory search."""
    print("Test 6: Search entire tests directory for 'ERROR'")

    returncode, stdout, stderr = run_loggrep([str(TESTS_DIR), "ERROR"])

    if returncode == 0:
        lines = stdout.strip().split("\n")
        matching_lines = [line for line in lines if ":" in line and "ERROR" in line]
        print(f"  ✓ Found {len(matching_lines)} lines with 'ERROR' across directory")
        # Count files mentioned
        files = set()
        for line in matching_lines:
            if ":" in line:
                file_part = line.split(":")[0]
                files.add(file_part)
        print(f"  Files with matches: {len(files)}")
    else:
        print(f"  ✗ Failed with code {returncode}")
    print()


def test_count_mode():
    """Test count-only mode."""
    print("Test 7: Count mode (-c) for 'INFO' in t2.log")

    returncode, stdout, stderr = run_loggrep([str(TESTS_DIR / "t2.log"), "INFO", "-c"])

    if returncode == 0:
        print(f"  ✓ Count mode output:")
        for line in stdout.strip().split("\n"):
            if line.strip():
                print(f"    {line}")
    else:
        print(f"  ✗ Failed with code {returncode}")
    print()


def test_files_only_mode():
    """Test files-only mode."""
    print("Test 8: Files-only mode (-l) for 'cardType' in tests directory")

    returncode, stdout, stderr = run_loggrep([str(TESTS_DIR), "cardType", "-l"])

    if returncode == 0:
        files = [line.strip() for line in stdout.strip().split("\n") if line.strip()]
        print(f"  ✓ Files containing 'cardType': {len(files)}")
        for f in files:
            print(f"    {f}")
    else:
        print(f"  ✗ Failed with code {returncode}")
    print()


def test_output_to_file():
    """Test output to file."""
    print("Test 9: Output to file (-o) functionality")

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as tmp:
        tmp_path = tmp.name

    try:
        returncode, stdout, stderr = run_loggrep(
            [str(TESTS_DIR / "t2.log"), "SUCCESS", "-o", tmp_path]
        )

        if returncode == 0:
            if os.path.exists(tmp_path):
                with open(tmp_path, "r") as f:
                    content = f.read()
                lines = [line for line in content.strip().split("\n") if line.strip()]
                print(f"  ✓ Successfully wrote {len(lines)} lines to output file")
                if lines:
                    print(f"  Example from file: {lines[0][:80]}...")
            else:
                print("  ✗ Output file was not created")
        else:
            print(f"  ✗ Failed with code {returncode}")
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
    print()


def test_no_line_numbers():
    """Test --no-line-numbers option."""
    print("Test 10: No line numbers (--no-line-numbers)")

    returncode, stdout, stderr = run_loggrep(
        [str(TESTS_DIR / "t2.log"), "ERROR", "--no-line-numbers"]
    )

    if returncode == 0:
        lines = stdout.strip().split("\n")
        matching_lines = [
            line for line in lines if "ERROR" in line and not line.startswith("Found")
        ]

        # Check if line numbers are absent (format should be file: content, not file:line: content)
        has_line_numbers = any(
            ":" in line and line.split(":")[1].strip().isdigit()
            for line in matching_lines
        )

        if not has_line_numbers:
            print(
                f"  ✓ Successfully removed line numbers from {len(matching_lines)} matching lines"
            )
        else:
            print(f"  ⚠ Line numbers still present in output")

        if matching_lines:
            print(f"  Example: {matching_lines[0][:80]}...")
    else:
        print(f"  ✗ Failed with code {returncode}")
    print()


def test_verbose_mode():
    """Test verbose mode."""
    print("Test 11: Verbose mode (-v)")

    returncode, stdout, stderr = run_loggrep([str(TESTS_DIR / "t2.log"), "ERROR", "-v"])

    if returncode == 0:
        verbose_indicators = [
            "Starting search",
            "Searching file:",
            "Search completed",
            "SUMMARY:",
        ]

        found_verbose = sum(
            1 for indicator in verbose_indicators if indicator in stdout
        )
        print(f"  ✓ Found {found_verbose}/{len(verbose_indicators)} verbose indicators")

        if found_verbose >= 2:
            print("  ✓ Verbose mode appears to be working")
        else:
            print("  ⚠ Verbose mode may not be fully working")
    else:
        print(f"  ✗ Failed with code {returncode}")
    print()


def main():
    """Run all tests."""
    print("Running loggrep tests...")
    print("=" * 60)

    # Check if loggrep.py exists
    if not LOGGREP_PATH.exists():
        print(f"Error: {LOGGREP_PATH} not found!")
        return 1

    # Check if tests directory exists
    if not TESTS_DIR.exists():
        print(f"Error: {TESTS_DIR} not found!")
        return 1

    print(f"Using loggrep: {LOGGREP_PATH}")
    print(f"Test data dir: {TESTS_DIR}")
    print()

    # Run all tests
    test_basic_search()
    test_multiple_phrases_all()
    test_multiple_phrases_any()
    test_case_insensitive()
    test_json_search()
    test_directory_search()
    test_count_mode()
    test_files_only_mode()
    test_output_to_file()
    test_no_line_numbers()
    test_verbose_mode()

    print("=" * 60)
    print("All tests completed!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
