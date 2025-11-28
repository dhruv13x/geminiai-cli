#!/usr/bin/env python3
# src/geminiai_cli/cleanup.py

import os
import shutil
from .ui import cprint, console
from .config import NEON_GREEN, NEON_YELLOW, NEON_RED, NEON_CYAN, DEFAULT_GEMINI_HOME, RESET

def do_cleanup(args):
    target_dir = os.path.join(DEFAULT_GEMINI_HOME, "tmp")
    
    if not os.path.exists(target_dir):
        cprint(NEON_YELLOW, f"[INFO] Nothing to clean. Directory not found: {target_dir}")
        return

    # Get list of items to be removed (excluding 'bin')
    try:
        all_items = os.listdir(target_dir)
    except Exception as e:
        cprint(NEON_RED, f"[ERROR] Could not list directory {target_dir}: {e}")
        return

    items_to_remove = [item for item in all_items if item != "bin"]

    if not items_to_remove:
        cprint(NEON_GREEN, "[OK] Directory is already clean (only preserved items remain).")
        return

    cprint(NEON_CYAN, f"Found {len(items_to_remove)} items to clean in {target_dir}")
    
    if not args.force and not args.dry_run:
        console.print(f"[bold red]WARNING:[/] This will permanently delete {len(items_to_remove)} items from {target_dir}")
        choice = input(f"{NEON_YELLOW}Are you sure you want to proceed? (y/N): {RESET}").strip().lower()
        if choice != 'y':
            cprint(NEON_CYAN, "Cleanup cancelled.")
            return

    cprint(NEON_YELLOW, f"[INFO] Cleaning up...")
    
    cleaned_count = 0
    
    for item in items_to_remove:
        item_path = os.path.join(target_dir, item)
        
        if args.dry_run:
            cprint(NEON_YELLOW, f"[DRY-RUN] Would delete: {item}")
            cleaned_count += 1
            continue
        
        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)
                cleaned_count += 1
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
                cleaned_count += 1
        except Exception as e:
            cprint(NEON_RED, f"[ERROR] Failed to delete {item}: {e}")

    if args.dry_run:
        cprint(NEON_GREEN, f"[OK] Cleanup dry run finished. Would remove {cleaned_count} items.")
    else:
        cprint(NEON_GREEN, f"[OK] Cleanup finished. Removed {cleaned_count} items.")
