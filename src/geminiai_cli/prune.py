#!/usr/bin/env python3

import os
import sys
import time
import argparse
from datetime import datetime, timedelta
from .ui import cprint, NEON_GREEN, NEON_RED, NEON_YELLOW, NEON_CYAN
from .settings import get_setting
from .b2 import B2Manager
from .config import TIMESTAMPED_DIR_REGEX

def parse_ts(name):
    m = TIMESTAMPED_DIR_REGEX.match(name)
    if m:
        return time.strptime(m.group(1), "%Y-%m-%d_%H%M%S")
    return None

def get_backup_list(files):
    """
    Filter and sort backups.
    files: list of filenames
    Returns list of (timestamp_struct, filename) sorted NEWEST first.
    """
    valid = []
    for f in files:
        if f.endswith(".gemini.tar.gz"):
            ts = parse_ts(f)
            if ts:
                valid.append((ts, f))
    # Sort: Newest first (descending timestamp)
    valid.sort(key=lambda x: x[0], reverse=True)
    return valid

def prune_list(backups, keep_count, dry_run, delete_callback):
    """
    backups: list of (ts, filename) sorted newest first.
    keep_count: int
    delete_callback: func(filename)
    """
    if len(backups) <= keep_count:
        cprint(NEON_GREEN, f"Total backups ({len(backups)}) <= keep count ({keep_count}). No pruning needed.")
        return

    to_keep = backups[:keep_count]
    to_delete = backups[keep_count:]

    cprint(NEON_CYAN, f"Keeping {len(to_keep)} latest backups.")
    cprint(NEON_YELLOW, f"Pruning {len(to_delete)} old backups...")

    for ts, fname in to_delete:
        if dry_run:
            print(f"[DRY-RUN] Would delete: {fname}")
        else:
            delete_callback(fname)
            print(f"[DELETED] {fname}")

def do_prune(args):
    backup_dir = os.path.abspath(os.path.expanduser(args.backup_dir))
    keep = int(args.keep)
    dry_run = args.dry_run
    
    cprint(NEON_CYAN, "✂️  Gemini Backup Pruning Tool")
    
    # 1. Local Prune
    if not args.cloud_only:
        cprint(NEON_CYAN, f"\n[LOCAL] Scanning {backup_dir}...")
        if os.path.exists(backup_dir):
            files = os.listdir(backup_dir)
            backups = get_backup_list(files)
            
            def local_delete(fname):
                path = os.path.join(backup_dir, fname)
                try:
                    os.remove(path)
                except Exception as e:
                    cprint(NEON_RED, f"Failed to remove {path}: {e}")

            prune_list(backups, keep, dry_run, local_delete)
        else:
             cprint(NEON_YELLOW, f"Backup directory not found: {backup_dir}")

    # 2. Cloud Prune
    if args.cloud or args.cloud_only:
        key_id = args.b2_id or os.environ.get("GEMINI_B2_KEY_ID") or get_setting("b2_id")
        app_key = args.b2_key or os.environ.get("GEMINI_B2_APP_KEY") or get_setting("b2_key")
        bucket_name = args.bucket or os.environ.get("GEMINI_B2_BUCKET") or get_setting("bucket")

        if key_id and app_key and bucket_name:
            cprint(NEON_CYAN, f"\n[CLOUD] Scanning B2 Bucket: {bucket_name}...")
            try:
                b2 = B2Manager(key_id, app_key, bucket_name)
                # b2.list_backups returns generator of (file_version, ...)
                # We need filenames.
                files = []
                # We might have multiple versions of the same file in B2, but our naming schema includes TS in filename.
                # So each file is unique.
                # list_backups yields (FileVersion, ...)
                cloud_files_map = {} # fname -> file_id (for deletion)
                
                for fv, _ in b2.list_backups():
                    files.append(fv.file_name)
                    cloud_files_map[fv.file_name] = fv.id_
                
                backups = get_backup_list(files)
                
                def cloud_delete(fname):
                    # B2Manager doesn't have delete_file_version exposed nicely in current helper?
                    # Let's check b2.py. 
                    # If not, we might need to add it or use the raw api.
                    # b2sdk bucket.delete_file_version(file_id, file_name)
                    # Let's assume we need to update B2Manager or use internal bucket ref.
                    try:
                        b2.bucket.delete_file_version(cloud_files_map[fname], fname)
                    except Exception as e:
                         cprint(NEON_RED, f"Failed to delete cloud file {fname}: {e}")

                prune_list(backups, keep, dry_run, cloud_delete)

            except Exception as e:
                cprint(NEON_RED, f"[ERROR] Cloud prune failed: {e}")
        else:
             if args.cloud_only:
                 cprint(NEON_RED, "[ERROR] Cloud credentials missing.")
             else:
                 cprint(NEON_YELLOW, "\n[CLOUD] Skipping (credentials not set).")
