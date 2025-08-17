# loggrep — Usage Examples

This document contains additional CLI usage examples and common workflows for the `loggrep` tool.

## Common workflows

1) Search for multiple phrases (ALL match):

```sh
# returns lines that contain both 'ERROR' and 'database'
loggrep /var/logs/app.log ERROR database
```

2) Search for multiple phrases (ANY match):

```sh
# returns lines that contain either 'ERROR' or 'WARNING'
loggrep /var/logs --any 'ERROR' 'WARNING'
```

3) Recursive search and save results to a file:

```sh
loggrep /var/logs 'timeout' --recursive -o timeouts.txt
```

4) Case-insensitive search across multiple files:

```sh
loggrep ./logs 'failed' 'exception' --ignore-case
```

5) Use in scripts (example):

```sh
#!/usr/bin/env bash
# find recent logs and search for failures
for f in $(find /var/log/myapp -name '*.log' -mtime -1); do
  loggrep "$f" 'ERROR' 'CRITICAL' --any >> failures_today.txt
done
```

## Notes
- When using the tool in scripts, prefer the `-o` option to write results to a single file instead of aggregating stdout in loops.
- For very large directories use `--recursive` cautiously — it will traverse all subdirectories.
