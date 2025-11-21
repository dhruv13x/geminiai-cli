#!/usr/bin/env python3
"""
list_backups.py

Lists all available backups from the backup directory.
"""
import os
import argparse
from .ui import cprint, NEON_CYAN, NEON_YELLOW

def main():
    parser = argparse.ArgumentParser(description="List available Gemini backups.")
    parser.add_argument("--search-dir", default="/root/geminiai_backups", help="Directory to search for backups (default /root/geminiai_backups)")
    args = parser.parse_args()

    backup_dir = os.path.expanduser(args.search_dir)

    if not os.path.isdir(backup_dir):
        cprint(NEON_YELLOW, f"Backup directory not found: {backup_dir}")
        return

    try:
        backups = [f for f in os.listdir(backup_dir) if os.path.isfile(os.path.join(backup_dir, f)) and f.endswith(('.gemini.tar.gz', '.gemini'))]
        if not backups:
            cprint(NEON_YELLOW, f"No backups found in {backup_dir}")
            return

        cprint(NEON_CYAN, f"Available backups in {backup_dir}:")
        for backup in sorted(backups):
            print(f"  {backup}")

    except OSError as e:
        cprint(NEON_RED, f"Error reading backup directory: {e}")

if __name__ == "__main__":
    main()
