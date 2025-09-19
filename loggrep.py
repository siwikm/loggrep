#!/usr/bin/env python3
# filepath: /usr/local/bin/loggrep

import sys
import argparse
from pathlib import Path
from typing import List, Optional, TextIO
import logging

logger = logging.getLogger(__name__)


def search_phrases_in_file(
    file_path: str,
    phrases: List[str],
    case_sensitive: bool = False,
    match_all: bool = True,
    verbose: bool = False,
    output_file: Optional[TextIO] = None,
    print_results: bool = True,
    show_line_numbers: bool = True,
    files_only: bool = False,
    count_only: bool = False,
) -> int:
    """
    Searches for lines containing specified phrases in a file.

    This streaming version does NOT accumulate results in memory.
    It prints matches immediately and optionally writes them to `output_file`.

    Options:
      show_line_numbers -- include line numbers in printed matches
      files_only -- print only file name when first match found (like grep -l)
      count_only -- do not print matching lines, only counts per file

    Returns: number of matching lines found
    """
    matches = 0

    if verbose:
        logger.info(f"Searching file: {file_path}")

    # Prepare phrases once (avoid doing this per-line)
    if case_sensitive:
        search_phrases = phrases
    else:
        # use casefold for better Unicode case-insensitive matching
        search_phrases = [p.casefold() for p in phrases]

    try:
        # errors='replace' prevents crashes on bad encoding while keeping streaming
        with open(file_path, "r", encoding="utf-8", errors="replace") as file:
            if verbose:
                logger.info("  File loading completed successfully")

            for line_num, line in enumerate(file, 1):
                # Keep original line content but strip only newline characters
                line_content = line.rstrip("\n").rstrip("\r")

                # Prepare line for comparison
                search_line = (
                    line_content if case_sensitive else line_content.casefold()
                )

                # Check if phrases are in the line
                if match_all:
                    ok = all(phrase in search_line for phrase in search_phrases)
                else:
                    ok = any(phrase in search_line for phrase in search_phrases)

                if ok:
                    matches += 1

                    # files_only: print filename once and stop scanning this file
                    if files_only:
                        if print_results:
                            print(file_path)
                        if output_file:
                            try:
                                output_file.write(file_path + "\n")
                            except Exception:
                                if verbose:
                                    logger.error(
                                        f"  ERROR: Failed to write filename to output while processing {file_path}"
                                    )
                        return matches

                    # count_only: do not print matching lines, continue to count
                    if count_only:
                        continue

                    # normal: print/write matching line, respect show_line_numbers
                    if show_line_numbers:
                        out = f"{file_path}:{line_num}: {line_content}"
                    else:
                        out = f"{file_path}: {line_content}"

                    if print_results:
                        print(out)
                    if output_file:
                        try:
                            output_file.write(out + "\n")
                        except Exception:
                            # avoid breaking the scan if writing fails
                            if verbose:
                                logger.error(
                                    f"  ERROR: Failed to write to output file while processing {file_path}"
                                )

    except FileNotFoundError:
        logger.error(f"Error: File {file_path} not found.")
    except Exception as e:
        logger.error(f"  ERROR: Unexpected error reading file {file_path}: {e}")

    # If count_only was requested and printing of per-file count is desired, caller will handle.
    if verbose:
        logger.info(f"  Search completed, found {matches} matches")

    return matches


def get_files_to_search(
    path: str, recursive: bool = False, verbose: bool = False
) -> List[str]:
    """
    Gets the list of files to search.

    Args:
        path: Path to file or directory
        recursive: Whether to search recursively in subdirectories
        verbose: Whether to display detailed logs

    Returns:
        List of file paths
    """
    if verbose:
        logger.info(f"Checking path: {path}")

    path_obj = Path(path)
    files_to_search = []

    if path_obj.is_file():
        if verbose:
            logger.info(f"  This is a file: {path}")
        return [str(path_obj)]

    elif path_obj.is_dir():
        if verbose:
            logger.info(f"  This is a directory: {path}")
            if recursive:
                logger.info("  Using recursive mode")

        if recursive:
            # Recursively search all files
            for file_path in path_obj.rglob("*"):
                if file_path.is_file():
                    files_to_search.append(str(file_path))
        else:
            # Search only files in the main directory
            for file_path in path_obj.iterdir():
                if file_path.is_file():
                    files_to_search.append(str(file_path))
    else:
        logger.error(
            f"Error: Path {path} does not exist or is not a file or directory."
        )
        return []

    if verbose:
        logger.info(f"  Found {len(files_to_search)} files")

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

    args = parser.parse_args()

    # Get list of files to search
    files_to_search = get_files_to_search(args.path, args.recursive, args.verbose)

    if not files_to_search:
        logger.info("No files found to search.")
        return

    if args.verbose:
        if args.verbose:
            logging.basicConfig(
                level=logging.INFO,
                format="%(levelname)s: %(message)s",
                handlers=[logging.StreamHandler(sys.stdout)],
            )
        else:
            # For non-verbose: only show warnings/errors, and matching lines as plain text
            logging.basicConfig(
                level=logging.WARNING,
                format="%(message)s",  # no level prefix for matching lines
                handlers=[logging.StreamHandler(sys.stdout)],
            )
        logger.info(f"Starting search of {len(files_to_search)} files...")
        if args.recursive:
            print("Mode: recursive")
        print(f"Search phrases: {args.phrases}")
        print(f"Match mode: {'all phrases' if not args.any else 'any phrase'}")
        print(
            f"Case sensitivity: {'considered' if not args.ignore_case else 'ignored'}"
        )
        print(
            f"Print options: line_numbers={'no' if args.no_line_numbers else 'yes'}, count={args.count}, files_only={args.files_only}"
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
            if args.verbose:
                logger.info(f"Opening output file: {args.output}")
            output_handle = open(args.output, "w", encoding="utf-8")

        # Search each file (streaming; results printed/written immediately)
        for file_path in files_to_search:
            matches = search_phrases_in_file(
                file_path=file_path,
                phrases=args.phrases,
                case_sensitive=not args.ignore_case,
                match_all=not args.any,
                verbose=args.verbose,
                output_file=output_handle,
                print_results=not args.count and not args.files_only,
                show_line_numbers=not args.no_line_numbers,
                files_only=args.files_only,
                count_only=args.count,
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
                        if args.verbose:
                            print(
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
            if args.verbose:
                print(f"Saved {total_matches} lines to file")

    except Exception as e:
        logger.error(f"ERROR during search: {e}")

    finally:
        if output_handle:
            try:
                output_handle.close()
            except Exception:
                pass


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
        print("8. Programmatic usage:")
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
