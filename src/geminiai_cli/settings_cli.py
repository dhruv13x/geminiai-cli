#!/usr/bin/env python3
# src/geminiai_cli/settings_cli.py


import argparse
from .settings import set_setting, get_setting, list_settings, remove_setting
from .ui import cprint
from .config import NEON_CYAN, NEON_GREEN, NEON_YELLOW, NEON_RED, RESET

def do_config(args):
    """
    Handle config command.
    args.config_action: 'set', 'get', 'list', 'unset'
    args.key: key (optional for list)
    args.value: value (optional for get/list/unset)
    """
    action = args.config_action
    
    if action == "list":
        s = list_settings()
        if not s:
            cprint(NEON_YELLOW, "No settings configured.")
        else:
            cprint(NEON_CYAN, "Current Configuration:")
            for k, v in s.items():
                # Mask sensitive keys in output
                display_val = v
                if "key" in k.lower() or "secret" in k.lower() or "password" in k.lower():
                    if isinstance(v, str) and len(v) > 4:
                        display_val = v[:2] + "*" * (len(v)-4) + v[-2:]
                    else:
                        display_val = "*****"
                print(f"  {NEON_GREEN}{k}{RESET}: {display_val}")
        return

    if not args.key:
        cprint(NEON_RED, "[ERROR] Key required for set/get/unset.")
        return

    if action == "set":
        if not args.value:
            cprint(NEON_RED, "[ERROR] Value required for set.")
            return
        # Store value. If user passed multiple words, they might be in a list, but argparse nargs='?' handles one.
        # If we wanted multi-word values without quotes, we'd use nargs='+' and join.
        # For now assume single string or quoted string.
        set_setting(args.key, args.value)
        cprint(NEON_GREEN, f"[OK] Set {args.key} = {args.value}")

    elif action == "get":
        val = get_setting(args.key)
        if val is not None:
            cprint(NEON_GREEN, f"{val}")
        else:
            cprint(NEON_YELLOW, f"(not set)")

    elif action == "unset":
        if remove_setting(args.key):
            cprint(NEON_GREEN, f"[OK] Removed {args.key}")
        else:
            cprint(NEON_YELLOW, f"[WARN] Key {args.key} not found.")
