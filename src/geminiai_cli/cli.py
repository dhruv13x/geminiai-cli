#!/usr/bin/env python3

import argparse
import sys
from .ui import banner, cprint
from .login import do_login
from .logout import do_logout
from .update import do_update, do_check_update
from .reset_helpers import (
    do_next_reset,
    do_capture_reset,
    do_list_resets,
    remove_entry_by_id,
)
from .config import NEON_YELLOW, NEON_CYAN
from .backup import main as backup_main
from .restore import main as restore_main
from .integrity import main as integrity_main
from .list_backups import main as list_backups_main
from .check_b2 import main as check_b2_main

def main():
    parser = argparse.ArgumentParser(description="Gemini CLI Automation Script (Neon Theme)")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Keep existing top-level arguments and add backup/restore as commands
    parser.add_argument("--login", action="store_true", help="Login to Gemini CLI")
    parser.add_argument("--logout", action="store_true", help="Logout from Gemini CLI")
    parser.add_argument("--update", action="store_true", help="Reinstall / update Gemini CLI")
    parser.add_argument("--check-update", action="store_true", help="Check for updates")
    parser.add_argument(
        "--next",
        nargs="?",
        const=None,
        help="Show next usage time. Optionally pass email or id: --next alice@example.com"
    )
    parser.add_argument(
        "--add",
        nargs="?",
        const="",
        help='Add time manually. Example: --add "01:00 PM alice@example.com" (quotes needed for spaces) or --add 13:00 alice@example.com'
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List saved schedules"
    )
    parser.add_argument(
        "--remove",
        nargs=1,
        help="Remove saved entry by id or email. Example: --remove alice@example.com"
    )

    # Backup command
    backup_parser = subparsers.add_parser("backup", help="Backup Gemini configuration and chats.")
    backup_parser.add_argument("--src", default="~/.gemini", help="Source gemini dir (default ~/.gemini)")
    backup_parser.add_argument("--archive-dir", default="/root/geminiai_backups", help="Directory to store tar.gz archives (default /root/geminiai_backups)")
    backup_parser.add_argument("--dest-dir-parent", default="/root/geminiai_backups", help="Parent directory where timestamped backups are stored (default /root/geminiai_backups)")
    backup_parser.add_argument("--dry-run", action="store_true", help="Do not perform destructive actions")
    backup_parser.add_argument("--cloud", action="store_true", help="Upload backup to Cloud (B2)")
    backup_parser.add_argument("--bucket", help="B2 Bucket Name")
    backup_parser.add_argument("--b2-id", help="B2 Key ID (or set env B2_APPLICATION_KEY_ID)")
    backup_parser.add_argument("--b2-key", help="B2 App Key (or set env B2_APPLICATION_KEY)")

    # Restore command
    restore_parser = subparsers.add_parser("restore", help="Restore Gemini configuration from a backup.")
    restore_parser.add_argument("--from-dir", help="Directory backup to restore from (preferred)")
    restore_parser.add_argument("--from-archive", help="Tar.gz archive to restore from")
    restore_parser.add_argument("--search-dir", default="/root/geminiai_backups", help="Directory to search for timestamped backups when no --from-dir (default /root/geminiai_backups)")
    restore_parser.add_argument("--dest", default="~/.gemini", help="Destination (default ~/.gemini)")
    restore_parser.add_argument("--force", action="store_true", help="Allow destructive replace without keeping .bak")
    restore_parser.add_argument("--dry-run", action="store_true", help="Do a dry run without destructive actions")
    restore_parser.add_argument("--cloud", action="store_true", help="Restore from Cloud (B2)")
    restore_parser.add_argument("--bucket", help="B2 Bucket Name")
    restore_parser.add_argument("--b2-id", help="B2 Key ID")
    restore_parser.add_argument("--b2-key", help="B2 App Key")

    # Integrity check command
    integrity_parser = subparsers.add_parser("check-integrity", help="Check integrity of current configuration against the latest backup.")
    integrity_parser.add_argument("--src", default="~/.gemini", help="Source directory for integrity check (default: ~/.gemini)")
    integrity_parser.add_argument("--search-dir", default="/root/geminiai_backups", help="Backup directory for integrity check (default: /root/geminiai_backups)")

    # List backups command
    list_backups_parser = subparsers.add_parser("list-backups", help="List available backups.")
    list_backups_parser.add_argument("--search-dir", default="/root/geminiai_backups", help="Directory to search for backups (default /root/geminiai_backups)")

    # Check B2 command
    check_b2_parser = subparsers.add_parser("check-b2", help="Verify Backblaze B2 credentials.")
    check_b2_parser.add_argument("--b2-id", help="B2 Key ID (or set env B2_APPLICATION_KEY_ID)")
    check_b2_parser.add_argument("--b2-key", help="B2 App Key (or set env B2_APPLICATION_KEY)")
    check_b2_parser.add_argument("--bucket", help="B2 Bucket Name (or set env B2_BUCKET_NAME)")


    # To handle the case where the script is called with no arguments
    if len(sys.argv) == 1:
        banner()
        parser.print_help()
        sys.exit(0)
    
    args = parser.parse_args()

    if args.command == "backup":
        sys.argv = ["geminiai-backup"]
        if args.src:
            sys.argv.extend(["--src", args.src])
        if args.archive_dir:
            sys.argv.extend(["--archive-dir", args.archive_dir])
        if args.dest_dir_parent:
            sys.argv.extend(["--dest-dir-parent", args.dest_dir_parent])
        if args.dry_run:
            sys.argv.append("--dry-run")
        if args.cloud: sys.argv.append("--cloud")
        if args.bucket: sys.argv.extend(["--bucket", args.bucket])
        if args.b2_id: sys.argv.extend(["--b2-id", args.b2_id])
        if args.b2_key: sys.argv.extend(["--b2-key", args.b2_key])
        backup_main()
    elif args.command == "restore":
        sys.argv = ["geminiai-restore"]
        if args.from_dir:
            sys.argv.extend(["--from-dir", args.from_dir])
        if args.from_archive:
            sys.argv.extend(["--from-archive", args.from_archive])
        if args.search_dir:
            sys.argv.extend(["--search-dir", args.search_dir])
        if args.dest:
            sys.argv.extend(["--dest", args.dest])
        if args.force:
            sys.argv.append("--force")
        if args.dry_run:
            sys.argv.append("--dry-run")
        if args.cloud: sys.argv.append("--cloud")
        if args.bucket: sys.argv.extend(["--bucket", args.bucket])
        if args.b2_id: sys.argv.extend(["--b2-id", args.b2_id])
        if args.b2_key: sys.argv.extend(["--b2-key", args.b2_key])
        restore_main()
    elif args.command == "check-integrity":
        sys.argv = ["geminiai-check-integrity"]
        if args.src:
            sys.argv.extend(["--src", args.src])
        if args.search_dir:
            sys.argv.extend(["--search-dir", args.search_dir])
        integrity_main()
    elif args.command == "list-backups":
        sys.argv = ["geminiai-list-backups"]
        if args.search_dir:
            sys.argv.extend(["--search-dir", args.search_dir])
        list_backups_main()
    elif args.command == "check-b2":
        sys.argv = ["geminiai-check-b2"]
        if args.bucket: sys.argv.extend(["--bucket", args.bucket])
        if args.b2_id: sys.argv.extend(["--b2-id", args.b2_id])
        if args.b2_key: sys.argv.extend(["--b2-key", args.b2_key])
        check_b2_main()
    elif args.login:
        do_login()
    elif args.logout:
        do_logout()
    elif args.update:
        do_update()
    elif args.check_update:
        do_check_update()
    elif args.list:
        do_list_resets()
    elif args.remove is not None:
        key = args.remove[0]
        ok = remove_entry_by_id(key)
        if ok:
            cprint(NEON_CYAN, f"[OK] Removed entries matching: {key}")
        else:
            cprint(NEON_YELLOW, f"[WARN] No entries matched: {key}")
    elif args.next is not None:
        ident = args.next
        do_next_reset(ident)
    elif args.add is not None:
        do_capture_reset(args.add)
    else:
        banner()
        parser.print_help()


if __name__ == "__main__":
    main()