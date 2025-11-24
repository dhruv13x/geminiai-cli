#!/usr/bin/env python3
"""
check_b2.py

Verifies Backblaze B2 credentials and bucket access.
"""
import os
import sys
import argparse
from .ui import cprint, NEON_GREEN, NEON_RED
from .b2 import B2Manager
from .settings import get_setting

def main():
    parser = argparse.ArgumentParser(description="Verify Backblaze B2 credentials and bucket access.")
    parser.add_argument("--b2-id", help="B2 Key ID (or set env GEMINI_B2_KEY_ID)")
    parser.add_argument("--b2-key", help="B2 App Key (or set env GEMINI_B2_APP_KEY)")
    parser.add_argument("--bucket", help="B2 Bucket Name (or set env GEMINI_B2_BUCKET)")
    args = parser.parse_args()

    # Resolve credentials (CLI arg > Env Var > Config)
    key_id = args.b2_id or os.environ.get("GEMINI_B2_KEY_ID") or get_setting("b2_id")
    app_key = args.b2_key or os.environ.get("GEMINI_B2_APP_KEY") or get_setting("b2_key")
    bucket = args.bucket or os.environ.get("GEMINI_B2_BUCKET") or get_setting("bucket")

    if not (key_id and app_key and bucket):
        cprint(NEON_RED, "[ERROR] B2 credentials or bucket name missing.")
        cprint(NEON_RED, "Provide --b2-id, --b2-key, --bucket OR set environment variables OR use 'geminiai config set ...'")
        cprint(NEON_RED, "  - GEMINI_B2_KEY_ID")
        cprint(NEON_RED, "  - GEMINI_B2_APP_KEY")
        cprint(NEON_RED, "  - GEMINI_B2_BUCKET")
        sys.exit(1)

    try:
        B2Manager(key_id, app_key, bucket)
        cprint(NEON_GREEN, "[OK] Backblaze B2 credentials and bucket access are correctly configured.")
    except SystemExit as e:
        # B2Manager calls sys.exit on failure, so we catch it to prevent a traceback
        # The error message is already printed by B2Manager's __init__
        sys.exit(e.code)
    except Exception as e:
        # Catch any other unexpected exceptions
        cprint(NEON_RED, f"[ERROR] An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
