#!/usr/bin/env python3
"""
list_backups.py

Lists all available backups from the backup directory.
"""
import os
import sys
import argparse
from .ui import cprint, NEON_CYAN, NEON_YELLOW, NEON_RED
from .b2 import B2Manager
from .settings import get_setting
from .config import DEFAULT_BACKUP_DIR

def main():
    parser = argparse.ArgumentParser(description="List available Gemini backups.")
    parser.add_argument("--search-dir", default=DEFAULT_BACKUP_DIR, help="Directory to search for backups (default ~/geminiai_backups)")
    parser.add_argument("--cloud", action="store_true", help="List backups from Cloud (B2)")
    parser.add_argument("--bucket", help="B2 Bucket Name")
    parser.add_argument("--b2-id", help="B2 Key ID (or set env GEMINI_B2_KEY_ID)")
    parser.add_argument("--b2-key", help="B2 App Key (or set env GEMINI_B2_APP_KEY)")
    args = parser.parse_args()

    if args.cloud:
        key_id = args.b2_id or os.environ.get("GEMINI_B2_KEY_ID") or get_setting("b2_id")
        app_key = args.b2_key or os.environ.get("GEMINI_B2_APP_KEY") or get_setting("b2_key")
        bucket_name = args.bucket or os.environ.get("GEMINI_B2_BUCKET") or get_setting("bucket")

        if not (key_id and app_key and bucket_name):
            cprint(NEON_RED, "[ERROR] Cloud listing requested but credentials or bucket name missing.")
            cprint(NEON_RED, "Provide --b2-id, --b2-key, --bucket OR set environment variables OR use 'geminiai config set ...'.")
            sys.exit(1)

        b2 = B2Manager(key_id, app_key, bucket_name)
        cprint(NEON_CYAN, f"Available backups in B2 bucket: {bucket_name}:")
        try:
            found_backups = False
            for file_version, _ in b2.list_backups():
                if file_version.file_name.endswith(".gemini.tar.gz"):
                    cprint(NEON_CYAN, f"  {file_version.file_name}")
                    found_backups = True
            if not found_backups:
                cprint(NEON_YELLOW, "No backups found in B2 bucket.")
        except Exception as e:
            cprint(NEON_RED, f"[CLOUD] Failed to list backups from B2: {e}")
            sys.exit(1)

    else: # List local backups
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
