#!/usr/bin/env python3
# src/geminiai_cli/cli.py

import sys
from .ui import cprint
from .banner import print_logo
from .login import do_login
from .logout import do_logout
from .session import do_session
from .cooldown import do_cooldown_list, do_remove_account
from .settings_cli import do_config
from .doctor import do_doctor
from .prune import do_prune
from .update import do_update, do_check_update
from .cleanup import do_cleanup
from .recommend import do_recommend
from .stats import do_stats
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
from .sync import cloud_sync, local_sync
from .args import build_main_parser, print_rich_help

def main():
    print_logo()
    # Handle main help manually to use Rich if no args or explicit help on main
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] in ["-h", "--help"]):
        print_rich_help()

    parser, resets_parser = build_main_parser()
    
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
        if args.auto: sys.argv.append("--auto")
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
        if args.cloud: sys.argv.append("--cloud")
        if args.bucket: sys.argv.extend(["--bucket", args.bucket])
        if args.b2_id: sys.argv.extend(["--b2-id", args.b2_id])
        if args.b2_key: sys.argv.extend(["--b2-key", args.b2_key])
        list_backups_main()
    elif args.command == "check-b2":
        sys.argv = ["geminiai-check-b2"]
        if args.bucket: sys.argv.extend(["--bucket", args.bucket])
        if args.b2_id: sys.argv.extend(["--b2-id", args.b2_id])
        if args.b2_key: sys.argv.extend(["--b2-key", args.b2_key])
        check_b2_main()
    elif args.command == "cloud-sync":
        cloud_sync(args)
    elif args.command == "local-sync":
        local_sync(args)
    elif args.command == "config":
        do_config(args)
    elif args.command == "doctor":
        do_doctor()
    elif args.command == "prune":
        do_prune(args)
    elif args.command == "cleanup":
        do_cleanup(args)
    elif args.command == "cooldown":
        if args.remove:
            do_remove_account(args.remove[0], args)
        else:
            do_cooldown_list(args)
    elif args.command == "recommend" or args.command == "next":
        do_recommend(args)
    elif args.command == "stats" or args.command == "usage":
        do_stats(args)
    elif args.command == "resets":
        if args.list:
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
            if ident == "*ALL*":
                ident = None
            do_next_reset(ident)
        elif args.add is not None:
            do_capture_reset(args.add)
        else:
            resets_parser.print_help()
    elif args.login:
        do_login()
    elif args.logout:
        do_logout()
    elif args.session:
        do_session()
    elif args.update:
        do_update()
    elif args.check_update:
        do_check_update()
    else:
        print_rich_help()


if __name__ == "__main__":
    main()
