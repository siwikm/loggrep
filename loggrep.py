#!/usr/bin/env python3
# filepath: /usr/local/bin/loggrep

import sys
import argparse
from pathlib import Path
from typing import List, Optional, TextIO, Tuple
from dataclasses import dataclass
import logging


# Verbose Logger Class
class VerboseLogger:
    """Logger that handles verbosity checks internally."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self._logger = logging.getLogger(__name__)

    def info(self, msg: str):
        """Only logs if verbose mode is enabled."""
        if self.verbose:
            self._logger.info(msg)

    def error(self, msg: str):
        """Always logs errors."""
        self._logger.error(msg)

    def warning(self, msg: str):
        """Always logs warnings."""
        self._logger.warning(msg)


# Default logger instance (will be replaced in main with verbose setting)
logger = VerboseLogger()


# Configuration Objects
@dataclass
class SearchConfig:
    """Configuration for search operations."""

    phrases: List[str]
    case_sensitive: bool = False
    match_all: bool = True
    window_size: int = 1


@dataclass
class OutputConfig:
    """Configuration for output formatting."""

    output_file: Optional[TextIO] = None
    show_line_numbers: bool = True
    print_results: bool = True
    count_only: bool = False
    files_only: bool = False


@dataclass
class RuntimeConfig:
    """Runtime configuration."""

    logger: VerboseLogger
    recursive: bool = False
    include_patterns: Optional[List[str]] = None


def process_window(
    buffer_lines: List[str],
    buffer_numbers: List[int],
    file_path: str,
    search_phrases: List[str],
    search_config: SearchConfig,
    output_config: OutputConfig,
    runtime_config: RuntimeConfig,
) -> Tuple[bool, bool]:
    """Process a window of lines and return (match_found, should_stop)."""

    if not buffer_lines:
        return False, False

    combined_text = " ".join(buffer_lines)
    search_text = (
        combined_text if search_config.case_sensitive else combined_text.casefold()
    )

    if search_config.match_all:
        found = all(phrase in search_text for phrase in search_phrases)
    else:
        found = any(phrase in search_text for phrase in search_phrases)

    if not found:
        return False, False

    if output_config.files_only:
        _handle_files_only_match(file_path, output_config, runtime_config)
        return True, True

    if output_config.count_only:
        return True, False

    start_line = buffer_numbers[0]
    end_line = buffer_numbers[-1]
    if output_config.show_line_numbers:
        out = f"{file_path}:{start_line}-{end_line}:\n"
        for i, (ln, content) in enumerate(zip(buffer_numbers, buffer_lines)):
            prefix = "  " if i > 0 else ""
            out += f"{prefix}{ln}: {content}\n"
        out = out.rstrip("\n")
    else:
        out = f"{file_path}:\n" + "\n".join(f"  {line}" for line in buffer_lines)

    if output_config.print_results:
        print(out)
    _write_to_output_file(
        output_config.output_file, out, file_path, runtime_config.logger
    )

    return True, False


def _validate_file_exists(file_path: str) -> bool:
    """Check if file exists and is accessible. Returns True if valid."""
    path_obj = Path(file_path)
    if not path_obj.exists():
        logger.error(f"Error: File {file_path} not found.")
        return False
    if not path_obj.is_file():
        logger.error(f"Error: {file_path} is not a file.")
        return False
    return True


def _prepare_search_phrases(phrases: List[str], case_sensitive: bool) -> List[str]:
    """Prepare phrases for searching (case-folding if needed)."""
    if case_sensitive:
        return phrases
    else:
        # use casefold for better Unicode case-insensitive matching
        return [p.casefold() for p in phrases]


def _line_matches_phrases(
    line: str, search_phrases: List[str], case_sensitive: bool, match_all: bool
) -> bool:
    """Check if a line matches the search criteria."""
    search_line = line if case_sensitive else line.casefold()

    if match_all:
        return all(phrase in search_line for phrase in search_phrases)
    else:
        return any(phrase in search_line for phrase in search_phrases)


def _format_match_output(
    file_path: str, line_num: int, line_content: str, show_line_numbers: bool
) -> str:
    """Format a matching line for output."""
    if show_line_numbers:
        return f"{file_path}:{line_num}: {line_content}"
    else:
        return f"{file_path}: {line_content}"


def _write_to_output_file(
    output_file: Optional[TextIO],
    content: str,
    file_path: str,
    vlogger: VerboseLogger,
) -> None:
    """Write content to output file with error handling."""
    if output_file:
        try:
            output_file.write(content + "\n")
        except Exception:
            vlogger.error(
                f"  ERROR: Failed to write to output file while processing {file_path}"
            )


def _handle_files_only_match(
    file_path: str,
    output_config: OutputConfig,
    runtime_config: RuntimeConfig,
) -> None:
    """Handle output when files_only mode finds a match."""
    if output_config.print_results:
        print(file_path)
    _write_to_output_file(
        output_config.output_file, file_path, file_path, runtime_config.logger
    )


def _handle_normal_match(
    file_path: str,
    line_num: int,
    line_content: str,
    output_config: OutputConfig,
    runtime_config: RuntimeConfig,
) -> None:
    """Handle output for a normal (non-count, non-files-only) match."""
    output = _format_match_output(
        file_path, line_num, line_content, output_config.show_line_numbers
    )
    if output_config.print_results:
        print(output)
    _write_to_output_file(
        output_config.output_file, output, file_path, runtime_config.logger
    )


def _search_line_by_line(
    file: TextIO,
    file_path: str,
    search_phrases: List[str],
    search_config: SearchConfig,
    output_config: OutputConfig,
    runtime_config: RuntimeConfig,
) -> int:
    """Search file line by line (window_size=1). Returns number of matches."""
    matches = 0

    for line_num, line in enumerate(file, 1):
        # Keep original line content but strip only newline characters
        line_content = line.rstrip("\n").rstrip("\r")

        # Check if line matches search criteria
        if _line_matches_phrases(
            line_content,
            search_phrases,
            search_config.case_sensitive,
            search_config.match_all,
        ):
            matches += 1

            # files_only: print filename once and stop scanning this file
            if output_config.files_only:
                _handle_files_only_match(file_path, output_config, runtime_config)
                return matches

            # count_only: do not print matching lines, continue to count
            if output_config.count_only:
                continue

            # normal: print/write matching line
            _handle_normal_match(
                file_path, line_num, line_content, output_config, runtime_config
            )

    return matches


def _search_with_window(
    file: TextIO,
    file_path: str,
    search_phrases: List[str],
    search_config: SearchConfig,
    output_config: OutputConfig,
    runtime_config: RuntimeConfig,
) -> int:
    """Search file with window of adjacent lines. Returns number of matches."""
    matches = 0
    lines_buffer = []  # Buffer to hold current window
    line_numbers_buffer = []  # Track line numbers for current window

    for line_num, line in enumerate(file, 1):
        line_content = line.rstrip("\n").rstrip("\r")

        # Add current line to window
        lines_buffer.append(line_content)
        line_numbers_buffer.append(line_num)

        # Keep only last window_size lines
        if len(lines_buffer) > search_config.window_size:
            lines_buffer.pop(0)
            line_numbers_buffer.pop(0)

        # Only search when we have a full window
        if len(lines_buffer) == search_config.window_size:
            match_found, should_stop = process_window(
                lines_buffer,
                line_numbers_buffer,
                file_path,
                search_phrases,
                search_config,
                output_config,
                runtime_config,
            )
            if match_found:
                matches += 1
            if should_stop:
                return matches

    # Handle partial window at end of file (file shorter than window_size)
    if lines_buffer and len(lines_buffer) < search_config.window_size:
        match_found, should_stop = process_window(
            lines_buffer,
            line_numbers_buffer,
            file_path,
            search_phrases,
            search_config,
            output_config,
            runtime_config,
        )
        if match_found:
            matches += 1
        if should_stop:
            return matches

    return matches


def search_phrases_in_file(
    file_path: str,
    search_config: SearchConfig,
    output_config: OutputConfig,
    runtime_config: RuntimeConfig,
) -> int:
    """
    Searches for lines containing specified phrases in a file.

    This streaming version does NOT accumulate results in memory.
    It prints matches immediately and optionally writes them to output_file.

    Args:
        file_path: Path to the file to search
        search_config: Search configuration (phrases, case sensitivity, match mode, window size)
        output_config: Output configuration (formatting, output file, modes)
        runtime_config: Runtime configuration (verbose, recursive, include patterns)

    Returns: number of matching lines found
    """
    runtime_config.logger.info(
        f"Searching file: {file_path} (window size: {search_config.window_size})"
    )

    # Early validation - fail fast
    if not _validate_file_exists(file_path):
        return 0

    # Prepare phrases once (avoid doing this per-line)
    search_phrases = _prepare_search_phrases(
        search_config.phrases, search_config.case_sensitive
    )

    try:
        # errors='replace' prevents crashes on bad encoding while keeping streaming
        with open(file_path, "r", encoding="utf-8", errors="replace") as file:
            runtime_config.logger.info("  File loading completed successfully")

            # Delegate to appropriate search method
            if search_config.window_size == 1:
                matches = _search_line_by_line(
                    file,
                    file_path,
                    search_phrases,
                    search_config,
                    output_config,
                    runtime_config,
                )
            else:
                matches = _search_with_window(
                    file,
                    file_path,
                    search_phrases,
                    search_config,
                    output_config,
                    runtime_config,
                )

    except PermissionError:
        logger.error(f"Error: Permission denied accessing {file_path}")
        return 0
    except Exception as e:
        logger.error(f"ERROR: Unexpected error reading file {file_path}: {e}")
        return 0

    runtime_config.logger.info(f"  Search completed, found {matches} matches")

    return matches


def get_files_to_search(
    path: str,
    recursive: bool = False,
    vlogger: Optional[VerboseLogger] = None,
    include_patterns: Optional[List[str]] = None,
) -> List[str]:
    """
    Gets the list of files to search.

    Args:
        path: Path to file or directory
        recursive: Whether to search recursively in subdirectories
        vlogger: VerboseLogger instance for detailed logs
        include_patterns: List of glob patterns (e.g., ['*.log', '*.txt']) to filter files.
                         If None, all files are included.

    Returns:
        List of file paths
    """
    if vlogger is None:
        vlogger = VerboseLogger()

    vlogger.info(f"Checking path: {path}")
    if include_patterns:
        vlogger.info(f"  Filtering by patterns: {include_patterns}")

    path_obj = Path(path)
    files_to_search = []

    if path_obj.is_file():
        vlogger.info(f"  This is a file: {path}")
        return [str(path_obj)]

    elif path_obj.is_dir():
        vlogger.info(f"  This is a directory: {path}")
        if recursive:
            vlogger.info("  Using recursive mode")

        if recursive:
            # Recursively search all files
            for file_path in path_obj.rglob("*"):
                if file_path.is_file():
                    # Apply include patterns if specified
                    if include_patterns:
                        if any(
                            file_path.match(pattern) for pattern in include_patterns
                        ):
                            files_to_search.append(str(file_path))
                    else:
                        files_to_search.append(str(file_path))
        else:
            # Search only files in the main directory
            for file_path in path_obj.iterdir():
                if file_path.is_file():
                    # Apply include patterns if specified
                    if include_patterns:
                        if any(
                            file_path.match(pattern) for pattern in include_patterns
                        ):
                            files_to_search.append(str(file_path))
                    else:
                        files_to_search.append(str(file_path))
    else:
        logger.error(
            f"Error: Path {path} does not exist or is not a file or directory."
        )
        return []

    vlogger.info(f"  Found {len(files_to_search)} files")

    return sorted(files_to_search)


def search_phrases_in_text(
    text: str, phrases: List[str], case_sensitive: bool = False, match_all: bool = True
) -> List[str]:
    """
    Searches for lines containing specified phrases in text.
    """
    matching_lines = []
    lines = text.split("\n")

    for line_num, line in enumerate(lines, 1):
        line_content = line.strip()

        # Prepare line for comparison
        search_line = line_content if case_sensitive else line_content.lower()

        # Prepare phrases for comparison
        search_phrases = (
            phrases if case_sensitive else [phrase.lower() for phrase in phrases]
        )

        # Check if phrases are in the line
        if match_all:
            # All phrases must be in the line
            if all(phrase in search_line for phrase in search_phrases):
                matching_lines.append(f"{line_num}: {line_content}")
        else:
            # Any phrase is enough
            if any(phrase in search_line for phrase in search_phrases):
                matching_lines.append(f"{line_num}: {line_content}")

    return matching_lines


def main():
    parser = argparse.ArgumentParser(
        description="Searches log files for lines containing specified phrases."
    )
    parser.add_argument("path", help="Path to log file or directory")
    parser.add_argument("phrases", nargs="+", help="List of phrases to search for")
    parser.add_argument("-i", "--ignore-case", action="store_true", help="Ignore case")
    parser.add_argument(
        "-a",
        "--any",
        action="store_true",
        help="Show lines containing ANY phrase (default: ALL phrases)",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Search recursively in all subdirectories (only when path is a directory)",
    )
    parser.add_argument(
        "-e",
        "--include",
        action="append",
        dest="include_patterns",
        help="Include only files matching glob pattern (e.g., '*.log', '*.txt'). Can be used multiple times.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Display detailed operation logs",
    )
    parser.add_argument("-o", "--output", help="Save results to file")
    parser.add_argument(
        "--no-line-numbers",
        action="store_true",
        help="Do not include line numbers in output",
    )
    parser.add_argument(
        "-c",
        "--count",
        action="store_true",
        help="Only print number of matches per file (do not print matching lines)",
    )
    parser.add_argument(
        "-l",
        "--files-only",
        action="store_true",
        help="Only print names of files that contain matches (like grep -l)",
    )
    parser.add_argument(
        "-w",
        "--window",
        type=int,
        default=1,
        help="Search phrases within a window of N adjacent lines (default: 1)",
    )

    args = parser.parse_args()

    # Create verbose logger
    vlogger = VerboseLogger(verbose=args.verbose)

    # Get list of files to search
    files_to_search = get_files_to_search(
        args.path, args.recursive, vlogger, args.include_patterns
    )

    if not files_to_search:
        if args.include_patterns:
            patterns_str = ", ".join(args.include_patterns)
            print(f"No files found matching patterns: {patterns_str}")
        else:
            print("No files found to search.")
        return

    if args.verbose:
        logging.basicConfig(
            level=logging.INFO,
            format="%(levelname)s: %(message)s",
            handlers=[logging.StreamHandler(sys.stdout)],
        )
        vlogger.info(f"Starting search of {len(files_to_search)} files...")
    else:
        # For non-verbose: only show warnings/errors
        logging.basicConfig(
            level=logging.WARNING,
            format="%(message)s",
            handlers=[logging.StreamHandler(sys.stdout)],
        )

    if args.verbose:
        if args.recursive:
            print("Mode: recursive")
        print(f"Search phrases: {args.phrases}")
        print(f"Match mode: {'all phrases' if not args.any else 'any phrase'}")
        print(
            f"Case sensitivity: {'considered' if not args.ignore_case else 'ignored'}"
        )
        print(
            f"Print options: line_numbers={'no' if args.no_line_numbers else 'yes'}, count={args.count}, files_only={args.files_only}, window={args.window}"
        )
        print("-" * 60)
    else:
        print(f"Searching {len(files_to_search)} files...")
        if args.recursive:
            print("(with recursive option)")
        print("-" * 50)

    total_matches = 0
    output_handle: Optional[TextIO] = None

    try:
        if args.output:
            vlogger.info(f"Opening output file: {args.output}")
            output_handle = open(args.output, "w", encoding="utf-8")

        # Create config objects from args
        search_config = SearchConfig(
            phrases=args.phrases,
            case_sensitive=not args.ignore_case,
            match_all=not args.any,
            window_size=args.window,
        )

        output_config = OutputConfig(
            output_file=output_handle,
            show_line_numbers=not args.no_line_numbers,
            print_results=not args.count and not args.files_only,
            count_only=args.count,
            files_only=args.files_only,
        )

        runtime_config = RuntimeConfig(
            logger=vlogger,
            recursive=args.recursive,
            include_patterns=args.include_patterns,
        )

        # Search each file (streaming; results printed/written immediately)
        for file_path in files_to_search:
            matches = search_phrases_in_file(
                file_path=file_path,
                search_config=search_config,
                output_config=output_config,
                runtime_config=runtime_config,
            )
            total_matches += matches

            # If count mode, print per-file counts
            if args.count and not args.files_only:
                # print and optionally write per-file count
                if args.verbose:
                    print(f"{file_path}: {matches} matches")
                else:
                    print(f"{file_path}: {matches}")
                if output_handle:
                    try:
                        output_handle.write(f"{file_path}: {matches}\n")
                    except Exception:
                        vlogger.error(
                            f"  ERROR: Failed to write count for {file_path} to output file"
                        )

        # Summary
        if total_matches:
            if args.verbose:
                print("-" * 60)
                print(
                    f"SUMMARY: Found {total_matches} lines in {len(files_to_search)} files:"
                )
            else:
                print(f"Found {total_matches} lines:")
            print("-" * 50)
        else:
            if args.verbose:
                print("-" * 60)
                print("SUMMARY: No matching lines found.")
            else:
                print("No matching lines found.")

        if args.output:
            print(f"\nResults saved to: {args.output}")
            vlogger.info(f"Saved {total_matches} lines to file")

    except Exception as e:
        logger.error(f"ERROR during search: {e}")

    finally:
        if output_handle:
            try:
                output_handle.close()
            except Exception as close_error:
                logger.warning(f"Failed to close output file: {close_error}")


# Usage examples
if __name__ == "__main__":
    # If run without arguments, show examples
    if len(sys.argv) == 1:
        print("Usage examples:")
        print("=" * 50)
        print("1. Search for lines containing ALL phrases in a file:")
        print("   python3 loggrep.py app.log 'ERROR' 'database'")
        print()
        print("2. Search in entire directory:")
        print("   python3 loggrep.py /var/logs/ 'ERROR' 'WARNING'")
        print()
        print("3. Search recursively in subdirectories:")
        print("   python3 loggrep.py /var/logs/ 'ERROR' --recursive")
        print()
        print("4. Search for lines containing ANY phrase:")
        print("   python3 loggrep.py app.log 'ERROR' 'WARNING' --any")
        print()
        print("5. Ignore case:")
        print("   python3 loggrep.py app.log 'error' 'failed' --ignore-case")
        print()
        print("6. Save results to file:")
        print(
            "   python3 loggrep.py app.log 'payment_intent' 'succeeded' -o results.txt"
        )
        print()
        print("7. Detailed operation logs:")
        print("   python3 loggrep.py /var/logs/ 'ERROR' --recursive --verbose")
        print()
        print("8. Search within adjacent lines (window):")
        print("   python3 loggrep.py app.log 'ERROR' 'database' --window 3")
        print()
        print("9. Programmatic usage:")
        print()

        # Programmatic example
        print("sample.log content:\n")
        sample_log = """
[2025-01-06 10:00:01] INFO: User login successful
[2025-01-06 10:00:02] ERROR: Database connection failed
[2025-01-06 10:00:03] WARNING: High memory usage detected
[2025-01-06 10:00:04] ERROR: Payment processing failed for user 123
[2025-01-06 10:00:05] INFO: Backup completed successfully
        """
        print(sample_log.strip())
        print()
        print("loggrep.py programmatic example result:\n")

        print("   # Search for lines with 'ERROR' and 'failed':")
        results = search_phrases_in_text(
            sample_log, ["ERROR", "failed"], match_all=True
        )
        for result in results:
            print(f"   {result}")

        sys.exit(0)

    main()
