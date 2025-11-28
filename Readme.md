# loggrep

A simple Python CLI tool to search log files (single file or directory).
No external dependencies — requires Python 3.8+.

## Requirements

- Python 3.8 or newer

## Installation (global)

On macOS, Debian, Ubuntu — copy the script to a system binary directory and make it executable:

```sh
# while in the project directory
wget https://raw.githubusercontent.com/siwikm/loggrep/main/loggrep.py
sudo cp loggrep.py /usr/local/bin/loggrep
sudo chmod +x /usr/local/bin/loggrep
```

After this you can run the tool using the `loggrep` command.

Alternative: run without installation:

```sh
python3 loggrep.py <path> <phrase1> [phrase2 ...] [options]
```

## Syntax (CLI)

```sh
loggrep <path_to_file_or_directory> <phrase1> [phrase2 ...] [options]
```

Output: each matched line is printed in the format `path:line: content`.

## Options

- `-i`, `--ignore-case` — ignore letter case
- `-a`, `--any` — show lines containing ANY phrase (default: ALL phrases)
- `-r`, `--recursive` — search directories recursively (only when the provided path is a directory)
- `-v`, `--verbose` — display detailed operation logs
- `-o`, `--output <file>` — save results to a file
- `-w`, `--window <N>` — search phrases within a window of N adjacent lines (default: 1 line)
- `--no-line-numbers` — omit line numbers from the output
- `-c`, `--count` — print only the number of matches per file
- `-l`, `--files-only` — print only filenames that contain matches (like `grep -l`)

## Examples

1. Search for lines that contain both `ERROR` and `database` in a file:

```sh
loggrep tests/t2.log ERROR database
```

2. Search for lines that contain `ERROR` OR `WARNING` (any mode):

```sh
loggrep /var/logs 'ERROR' 'WARNING' --any
```

3. Recursive search in a directory:

```sh
loggrep /var/logs 'ERROR' --recursive
```

4. Ignore case:

```sh
loggrep app.log 'error' 'failed' --ignore-case
```

5. Save results to a file:

```sh
loggrep app.log 'payment_intent' 'succeeded' -o results.txt
```

6. Verbose mode (diagnostics):

```sh
loggrep /var/logs 'ERROR' --recursive --verbose
```

7. Search for phrases across a window of adjacent lines (e.g., 3-line window):

```sh
loggrep app.log 'ERROR' 'database' --window 3
```

8. Show only filenames or match counts:

```sh
loggrep tests 'cardType' --files-only
loggrep tests/t2.log 'INFO' --count
```

---

- "No files found to search." — check that the provided path exists and you have permissions.
- UnicodeDecodeError — the file may be binary or use an encoding other than UTF-8.
- To run without installing globally, use `python3 loggrep.py`.

---