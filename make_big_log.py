#!/usr/bin/env python3
"""
Generate a large text log file (default 5 GiB) for testing.
Usage:
    python3 make_big_log.py --size 5G --output big.log
"""

import argparse
import os
import random
import time
from datetime import datetime, timedelta

LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
SAMPLE_MESSAGES = [
    "User login successful",
    "Database connection failed",
    "Payment processing succeeded",
    "Payment processing failed for user",
    "Timeout while calling external API",
    "File not found",
    "Cache miss for key",
    "Background job started",
    "Background job finished",
    "High memory usage detected",
]


def parse_size(s: str) -> int:
    s = s.strip().upper()
    mult = 1
    if s.endswith("K"):
        mult = 1024
        s = s[:-1]
    elif s.endswith("M"):
        mult = 1024**2
        s = s[:-1]
    elif s.endswith("G"):
        mult = 1024**3
        s = s[:-1]
    elif s.endswith("T"):
        mult = 1024**4
        s = s[:-1]
    return int(float(s) * mult)


def generate_block(start_time: datetime, lines: int, filler: str) -> (str, datetime):
    parts = []
    t = start_time
    for i in range(lines):
        t += timedelta(seconds=1)
        level = random.choice(LEVELS)
        msg = random.choice(SAMPLE_MESSAGES)
        # add a variable id and filler to make lines larger and less repetitive
        entry = f"[{t.strftime('%Y-%m-%d %H:%M:%S')}] {level}: {msg} id={random.randint(0, 999999)} {filler}"
        parts.append(entry)
    block = "\n".join(parts) + "\n"
    return block, t


def main():
    parser = argparse.ArgumentParser(
        description="Generate a large log file for testing."
    )
    parser.add_argument("--output", "-o", default="big.log", help="Output filename")
    parser.add_argument(
        "--size", "-s", default="5G", help="Target size (e.g. 5G, 500M)"
    )
    parser.add_argument(
        "--block-lines", type=int, default=2000, help="Number of lines per write block"
    )
    parser.add_argument(
        "--filler-size", type=int, default=200, help="Bytes of filler text per line"
    )
    parser.add_argument("--seed", type=int, default=None, help="Random seed (optional)")
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    target = parse_size(args.size)
    out_path = args.output

    # Prepare filler string to reach approx line size
    filler = "x" * max(0, args.filler_size)

    written = 0
    current_time = datetime.now() - timedelta(days=1)

    print(
        f"Generating ~{target} bytes into {out_path} (block {args.block_lines} lines)..."
    )

    start = time.time()
    last_report = time.time()
    report_interval = 5.0  # seconds

    with open(out_path, "w", encoding="utf-8", errors="replace") as f:
        while written < target:
            block, current_time = generate_block(current_time, args.block_lines, filler)
            encoded = block.encode("utf-8")
            # If writing whole block would exceed target, trim the block
            if written + len(encoded) > target:
                # compute remaining bytes
                remaining = target - written
                # we need to cut encoded to remaining bytes safely at a utf-8 boundary
                trimmed = encoded[:remaining]
                try:
                    text = trimmed.decode("utf-8")
                except Exception:
                    # fallback: drop last few bytes until valid
                    for cut in range(1, 5):
                        try:
                            text = encoded[: remaining - cut].decode("utf-8")
                            break
                        except Exception:
                            continue
                    else:
                        # as last resort, stop without writing
                        break
                f.write(text)
                written += len(text.encode("utf-8"))
                break

            f.write(block)
            written += len(encoded)

            now = time.time()
            if now - last_report >= report_interval:
                elapsed = now - start
                mb = written / (1024 * 1024)
                speed = mb / elapsed if elapsed > 0 else 0
                pct = written / target * 100
                print(
                    f"Written: {written} bytes ({mb:.2f} MB) — {pct:.2f}% — {speed:.2f} MB/s"
                )
                last_report = now

    total_time = time.time() - start
    print(f"Done. Wrote {written} bytes to {out_path} in {total_time:.1f}s")


if __name__ == "__main__":
    main()
