#!/usr/bin/env python3

import argparse
from .ui import banner, cprint
from .commands import do_login, do_logout, do_update, do_check_update
from .config import NEON_YELLOW, NEON_CYAN

def main():
    parser = argparse.ArgumentParser(description="Gemini CLI Automation Script (Neon Theme)")
    parser.add_argument("--login", action="store_true", help="Login to Gemini CLI")
    parser.add_argument("--logout", action="store_true", help="Logout from Gemini CLI")
    parser.add_argument("--update", action="store_true", help="Reinstall / update Gemini CLI")
    parser.add_argument("--check-update", action="store_true", help="Check for updates")
    args = parser.parse_args()

    if args.login:
        do_login()
    elif args.logout:
        do_logout()
    elif args.update:
        do_update()
    elif args.check_update:
        do_check_update()
    else:
        banner()
        cprint(NEON_YELLOW, "Usage:")
        cprint(NEON_CYAN, "  python sgemini.py --login")
        cprint(NEON_CYAN, "  python sgemini.py --logout")
        cprint(NEON_CYAN, "  python sgemini.py --update")
        cprint(NEON_CYAN, "  python sgemini.py --check-update")

if __name__ == "__main__":
    main()
