#!/usr/bin/env python3
"""
restore.py - Safe restore that picks the oldest timestamped backup by default.

Naming convention expected for automatic discovery (produced by backup.py):
  YYYY-MM-DD_HHMMSS-<email>.gemini
Examples:
  2025-10-22_042211-bose13x@gmail.com.gemini
  2025-10-21_020211-kingchess@gmail.com.gemini

Behavior:
 - If --from-dir or --from-archive is passed, those are used.
 - If nothing is passed, script scans --search-dir (default /root) for
   directories matching the timestamp pattern and picks the oldest (earliest)
   timestamp to restore.
 - Safety: lockfile, temp copy, diff verification, .bak move of existing ~/.gemini,
   atomic replace, dry-run and --force supported.
"""
from __future__ import annotations
import argparse
import fcntl
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Optional, Tuple

from .config import TIMESTAMPED_DIR_REGEX
...
LOCKFILE = "/var/lock/gemini-backup.lock"

def acquire_lock(path: str = LOCKFILE):
    fd = open(path, "w+")
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print("Another backup/restore is running. Exiting.")
        sys.exit(2)
    return fd

def run(cmd: str, check: bool = True, capture: bool = False):
    if capture:
        return subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return subprocess.run(cmd, shell=True, check=check)

def shlex_quote(s: str) -> str:
    return shlex.quote(s)

def parse_timestamp_from_name(name: str) -> Optional[time.struct_time]:
    """
    Parse timestamp prefix like '2025-10-22_042211' into struct_time.
    Return None if it doesn't match.
    """
    m = TIMESTAMPED_DIR_REGEX.match(name)
    if not m:
        return None
    ts_str = m.group(1)  # 'YYYY-MM-DD_HHMMSS'
    try:
        return time.strptime(ts_str, "%Y-%m-%d_%H%M%S")
    except Exception:
        return None

def find_oldest_archive_backup(search_dir: str) -> Optional[str]:
    """
    Search search_dir for backup archives (*.gemini.tar.gz) matching the
    timestamp pattern and return the full path of the oldest backup (earliest
    timestamp). If none found, return None.
    """
    candidates: list[Tuple[time.struct_time, str]] = []
    try:
        for entry in os.listdir(search_dir):
            full_path = os.path.join(search_dir, entry)
            # We are now looking for archive files, not directories
            if not (os.path.isfile(full_path) and entry.endswith(".gemini.tar.gz")):
                continue

            # The name for parsing is the filename itself
            ts = parse_timestamp_from_name(entry)
            if ts:
                candidates.append((ts, full_path))
    except FileNotFoundError:
        return None

    if not candidates:
        return None

    # Sort by timestamp struct_time ascending (earliest first)
    candidates.sort(key=lambda x: time.mktime(x[0]))
    return candidates[0][1]


def extract_archive(archive_path: str, extract_to: str):
    os.makedirs(extract_to, exist_ok=True)
    cmd = f"tar -C {shlex_quote(extract_to)} -xzf {shlex_quote(archive_path)}"
    run(cmd)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--from-dir", help="Directory backup to restore from (legacy, archive is preferred)")
    p.add_argument("--from-archive", help="Tar.gz archive to restore from")
    p.add_argument("--search-dir", default="/root/geminiai_backups", help="Directory to search for timestamped backups when no source is specified (default: /root/geminiai_backups)")
    p.add_argument("--dest", default="~/.gemini", help="Destination (default ~/.gemini)")
    p.add_argument("--force", action="store_true", help="Allow destructive replace without keeping .bak")
    p.add_argument("--dry-run", action="store_true", help="Do a dry run without destructive actions")
    args = p.parse_args()

    dest = os.path.abspath(os.path.expanduser(args.dest))
    ts_now = time.strftime("%Y%m%d-%H%M%S")

    chosen_src: Optional[str] = None
    from_archive: Optional[str] = None

    if args.from_dir:
        chosen_src = os.path.abspath(os.path.expanduser(args.from_dir))
        if not os.path.exists(chosen_src):
            print(f"Specified --from-dir not found: {chosen_src}")
            sys.exit(1)
    elif args.from_archive:
        from_archive = os.path.abspath(os.path.expanduser(args.from_archive))
        if not os.path.exists(from_archive):
            print(f"Specified --from-archive not found: {from_archive}")
            sys.exit(1)
    else:
        # Auto-discover oldest timestamped *archive* in search_dir
        sd = os.path.abspath(os.path.expanduser(args.search_dir))
        print(f"Searching for oldest backup archive in: {sd}")
        oldest_archive = find_oldest_archive_backup(sd)
        if not oldest_archive:
            print(f"No timestamped backup archives (*.gemini.tar.gz) found in {sd}")
            sys.exit(1)
        
        from_archive = oldest_archive
        print(f"Auto-selected oldest backup archive: {from_archive}")

    lockfd = acquire_lock()
    try:
        work_tmp = tempfile.mkdtemp(prefix="gemini-restore-")
        try:
            if from_archive:
                print(f"Extracting archive {from_archive} -> {work_tmp}")
                if not args.dry_run:
                    extract_archive(from_archive, work_tmp)
                else:
                    print("DRY RUN: would extract archive.")
                src_for_copy = work_tmp
            else:
                # chosen_src is set (either provided or auto-selected)
                src_for_copy = os.path.abspath(chosen_src)
                print("Source to restore from:", src_for_copy)

            # Copy into temporary dest - to prepare verification
            tmp_dest = f"{dest}.tmp-{ts_now}"
            print(f"Copying {src_for_copy} -> {tmp_dest}")
            if not args.dry_run:
                if os.path.exists(tmp_dest):
                    shutil.rmtree(tmp_dest)
                cp_cmd = f"cp -a {shlex_quote(src_for_copy)} {shlex_quote(tmp_dest)}"
                run(cp_cmd)
            else:
                print("DRY RUN: would cp -a ...")

            # Verify copy with diff -r
            print("Verifying copy with diff -r")
            if not args.dry_run:
                diff_proc = run(f"diff -r {shlex_quote(tmp_dest)} {shlex_quote(src_for_copy)}", capture=True, check=False)
                if diff_proc.returncode != 0:
                    print("Verification FAILED (diff shows differences):")
                    if diff_proc.stdout:
                        print(diff_proc.stdout)
                    shutil.rmtree(tmp_dest, ignore_errors=True)
                    sys.exit(3)
                else:
                    print("Verification OK.")
            else:
                print("DRY RUN: would run diff -r ...")

            # Prepare swap: move existing dest to .bak-<ts> unless --force
            bakname = None
            if os.path.exists(dest):
                bakname = f"{dest}.bak-{ts_now}"
                print(f"Preparing to move existing {dest} -> {bakname}")
                if not args.dry_run:
                    if args.force:
                        print("--force: removing existing dest")
                        shutil.rmtree(dest)
                    else:
                        # atomic rename (replace if necessary fallback)
                        try:
                            os.replace(dest, bakname)
                        except Exception:
                            shutil.move(dest, bakname)
                else:
                    print("DRY RUN: would move existing dest to bak or remove with --force")

            # Install new .gemini (atomic replace)
            print(f"Installing new .gemini from {tmp_dest} -> {dest}")
            if not args.dry_run:
                os.replace(tmp_dest, dest)
            else:
                print("DRY RUN: would os.replace(tmp_dest, dest)")

            # Post-restore verification
            if not args.dry_run:
                print("Post-restore verification: diff -r between restored dest and source")
                diff2 = run(f"diff -r {shlex_quote(dest)} {shlex_quote(src_for_copy)}", capture=True, check=False)
                if diff2.returncode != 0:
                    print("Post-restore verification FAILED:")
                    if diff2.stdout:
                        print(diff2.stdout)
                    print("Attempting rollback (if possible).")
                    if not args.force and bakname and os.path.exists(bakname):
                        try:
                            os.replace(bakname, dest)
                            print("Rollback to previous copy succeeded.")
                        except Exception as e:
                            print("Rollback failed:", e)
                    sys.exit(4)
                else:
                    print("Post-restore verification OK.")
            else:
                print("DRY RUN: would run post-restore diff")

            print("Restore complete.")
            if bakname and os.path.exists(bakname):
                print("Previous .gemini moved to:", bakname)
        finally:
            # cleanup temp extraction dir if still present
            if os.path.exists(work_tmp):
                try:
                    shutil.rmtree(work_tmp)
                except Exception:
                    pass
    finally:
        try:
            fcntl.flock(lockfd, fcntl.LOCK_UN)
            lockfd.close()
        except Exception:
            pass

if __name__ == "__main__":
    main()