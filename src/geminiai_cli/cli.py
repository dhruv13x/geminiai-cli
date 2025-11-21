#!/usr/bin/env python3

import argparse
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

def main():
    parser = argparse.ArgumentParser(description="Gemini CLI Automation Script (Neon Theme)")
    parser.add_argument("--login", action="store_true", help="Login to Gemini CLI")
    parser.add_argument("--logout", action="store_true", help="Logout from Gemini CLI")
    parser.add_argument("--update", action="store_true", help="Reinstall / update Gemini CLI")
    parser.add_argument("--check-update", action="store_true", help="Check for updates")

    # next-reset optionally accepts an identifier (email or id)
    parser.add_argument(
        "--next",
        nargs="?",
        const=None,
        help="Show next usage time. Optionally pass email or id: --next alice@example.com"
    )

    # capture-reset accepts optional text (or reads stdin/prompt)
    parser.add_argument(
        "--add",
        nargs="?",
        const="",
        help='Add time manually. Example: --add "01:00 PM alice@example.com" (quotes needed for spaces) or --add 13:00 alice@example.com'
    )

    # list and remove helpers for multi-account management
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

    args = parser.parse_args()

    if args.login:
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
        # args.remove is a list with 1 element due to nargs=1
        key = args.remove[0]
        ok = remove_entry_by_id(key)
        if ok:
            cprint(NEON_CYAN, f"[OK] Removed entries matching: {key}")
        else:
            cprint(NEON_YELLOW, f"[WARN] No entries matched: {key}")

    elif args.next is not None:
        # args.next is None when flag passed with no argument (const=None)
        # or a string when a value was provided
        ident = args.next  # could be None or "email" or "id"
        do_next_reset(ident)

    elif args.add is not None:
        # args.add == "" when flag passed without value (const=""),
        # or a string when provided
        do_capture_reset(args.add)

    else:
        banner()
        cprint(NEON_YELLOW, "Usage:")
        cprint(NEON_CYAN, "  geminiai --login")
        cprint(NEON_CYAN, "  geminiai --logout")
        cprint(NEON_CYAN, "  geminiai --update")
        cprint(NEON_CYAN, "  geminiai --check-update")
        cprint(NEON_CYAN, "  geminiai --list")
        cprint(NEON_CYAN, "  geminiai --next [email|id]")
        cprint(NEON_CYAN, "  geminiai --add \"01:00 PM alice@example.com\"")
        cprint(NEON_CYAN, "  geminiai --remove alice@example.com")

if __name__ == "__main__":
    main()