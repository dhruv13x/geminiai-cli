#!/usr/bin/env python3
# src/geminiai_cli/integrity.py

"""
integrity.py - Check integrity of current configuration against the latest backup.
"""
from __future__ import annotations
import argparse
import os
import sys
import time
from typing import Optional, Tuple

from .config import TIMESTAMPED_DIR_REGEX, DEFAULT_BACKUP_DIR
import subprocess

from .config import TIMESTAMPED_DIR_REGEX

def run(cmd: str, check: bool = True, capture: bool = False):
    if capture:
        return subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return subprocess.run(cmd, shell=True, check=check)

def parse_timestamp_from_name(name: str) -> Optional[time.struct_time]:
    """
    Parse timestamp prefix like '2025-10-22_042211' into struct_time.
    Return None if it doesn't match.
    """
    m = TIMESTAMPED_DIR_REGEX.match(name)
    if not m:
        return None
    ts_str = m.group(1)  # 'YYYY-MM-DD_HHMMSS'
    try:
        return time.strptime(ts_str, "%Y-%m-%d_%H%M%S")
    except Exception:
        return None

def find_latest_backup(search_dir: str) -> Optional[str]:
    """
    Search search_dir for directories matching timestamp pattern and return
    full path of the latest backup (newest timestamp). If none found, return None.
    """
    candidates: list[Tuple[time.struct_time, str]] = []
    try:
        for entry in os.listdir(search_dir):
            full = os.path.join(search_dir, entry)
            if not os.path.isdir(full):
                continue
            ts = parse_timestamp_from_name(entry)
            if ts:
                candidates.append((ts, full))
    except FileNotFoundError:
        return None

    if not candidates:
        return None

    # sort by timestamp struct_time descending (newest first)
    candidates.sort(key=lambda x: time.mktime(x[0]), reverse=True)
    return candidates[0][1]

def perform_integrity_check(args: argparse.Namespace):
    # Fallback if args missing or None
    if not hasattr(args, 'src') or args.src is None:
        args.src = "~/.gemini"
    if not hasattr(args, 'search_dir') or args.search_dir is None:
        args.search_dir = DEFAULT_BACKUP_DIR

    src = os.path.abspath(os.path.expanduser(args.src))
    search_dir = os.path.abspath(os.path.expanduser(args.search_dir))

    if not os.path.exists(src):
        print(f"Source directory does not exist: {src}")
        sys.exit(1)

    latest_backup = find_latest_backup(search_dir)

    if not latest_backup:
        print(f"No backups found in {search_dir}")
        sys.exit(1)

    print(f"Found latest backup: {latest_backup}")
    print(f"Comparing {src} with {latest_backup}")

    diff_proc = run(f"diff -r {src} {latest_backup}", check=False, capture=True)

    if diff_proc.returncode == 0:
        print("Integrity check passed: No differences found.")
    else:
        print("Integrity check failed: Differences found.")
        if diff_proc.stdout:
            print(diff_proc.stdout)
        if diff_proc.stderr:
            print(diff_proc.stderr)

def main():
    p = argparse.ArgumentParser(description="Check integrity of current configuration against the latest backup.")
    p.add_argument("--src", default="~/.gemini", help="Source gemini dir (default ~/.gemini)")
    p.add_argument("--search-dir", default=DEFAULT_BACKUP_DIR, help="Directory to search for timestamped backups (default ~/geminiai_backups)")
    args = p.parse_args()
    perform_integrity_check(args)

if __name__ == "__main__":
    main()
