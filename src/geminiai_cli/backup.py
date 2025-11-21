#!/usr/bin/env python3
"""
backup.py - automatic Gemini CLI backup that names backups with timestamp + email

Example result:
  /root/2025-10-22_042211-bose13x@gmail.com.gemini
Archive:
  /root/backups/2025-10-22_042211-bose13x@gmail.com.gemini.tar.gz
Stable "latest" symlink:
  /root/bose13x@gmail.com.gemini -> /root/2025-10-22_042211-bose13x@gmail.com.gemini

Usage:
  ./backup.py
  ./backup.py --dry-run
  ./backup.py --src ~/.gemini --archive-dir /root/backups --dest-dir-parent /root
"""

from __future__ import annotations
import argparse
import fcntl
import json
import os
import shutil
import subprocess
import sys
import time
import tempfile
from typing import Optional

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
    import shlex
    return shlex.quote(s)

def read_active_email(gemini_dir: str) -> Optional[str]:
    path = os.path.join(gemini_dir, "google_accounts.json")
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        active = data.get("active")
        if not active:
            return None
        active = str(active).strip()
        # Basic sanitization: remove path separators and spaces
        active = active.replace(os.path.sep, "_").replace(" ", "_")
        return active
    except Exception:
        return None

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def make_timestamp() -> str:
    # Format: YYYY-MM-DD_HHMMSS  -> example: 2025-10-22_042211
    return time.strftime("%Y-%m-%d_%H%M%S")

def atomic_symlink(target: str, link_name: str):
    """
    Create an atomic symlink: create tmp symlink and replace existing link atomically.
    """
    tmp = f"{link_name}.tmp-{int(time.time() * 1000)}"
    try:
        if os.path.lexists(tmp):
            try:
                os.unlink(tmp)
            except Exception:
                pass
        os.symlink(target, tmp)
        # os.replace will atomically rename the tmp symlink over the old link_name
        os.replace(tmp, link_name)
    finally:
        if os.path.lexists(tmp):
            try:
                os.unlink(tmp)
            except Exception:
                pass

def main():
    p = argparse.ArgumentParser(description="Safe timestamped backup for ~/.gemini (name: YYYY-MM-DD_HHMMSS-email.gemini)")
    p.add_argument("--src", default="~/.gemini", help="Source gemini dir (default ~/.gemini)")
    p.add_argument("--archive-dir", default="/root/backups", help="Directory to store tar.gz archives")
    p.add_argument("--dest-dir-parent", default="/root", help="Parent directory where timestamped backups are stored")
    p.add_argument("--dry-run", action="store_true", help="Do not perform destructive actions")
    args = p.parse_args()

    src = os.path.abspath(os.path.expanduser(args.src))
    archive_dir = os.path.abspath(os.path.expanduser(args.archive_dir))
    dest_parent = os.path.abspath(os.path.expanduser(args.dest_dir_parent))
    ts = make_timestamp()

    if not os.path.exists(src):
        print(f"Source does not exist: {src}")
        sys.exit(1)

    active_email = read_active_email(src)
    if active_email:
        # Example: 2025-10-22_042211-bose13x@gmail.com.gemini
        dest_basename = f"{ts}-{active_email}.gemini"
    else:
        dest_basename = f"{ts}-gemini-backup.gemini"
        print("Warning: could not read active email from google_accounts.json; using fallback name:", dest_basename)

    dest = os.path.join(dest_parent, dest_basename)
    archive_path = os.path.join(archive_dir, f"{dest_basename}.tar.gz")
    latest_symlink = os.path.join(dest_parent, f"{active_email}.gemini") if active_email else None

    lockfd = acquire_lock()
    try:
        # 1) Create archive (tar gz) of the source
        print(f"[1/4] Creating archive: {archive_path}")
        if not args.dry_run:
            ensure_dir(archive_dir)
            tar_cmd = f"tar -C {shlex_quote(src)} -czf {shlex_quote(archive_path)} ."
            run(tar_cmd)
        else:
            print("DRY RUN: would run tar -C ...")

        # 2) Copy to temporary location (sibling of dest)
        tmp_parent = os.path.dirname(dest) or "/tmp"
        tmp_dest = os.path.join(tmp_parent, f".{os.path.basename(dest)}.tmp-{ts}")
        print(f"[2/4] Copying to temporary location: {tmp_dest}")
        if not args.dry_run:
            if os.path.exists(tmp_dest):
                shutil.rmtree(tmp_dest)
            cp_cmd = f"cp -a {shlex_quote(src)} {shlex_quote(tmp_dest)}"
            run(cp_cmd)
        else:
            print("DRY RUN: would cp -a ...")

        # 3) Verify copy with diff -r
        print("[3/4] Verifying copy with diff -r")
        if not args.dry_run:
            diff_proc = run(f"diff -r {shlex_quote(src)} {shlex_quote(tmp_dest)}", check=False, capture=True)
            if diff_proc.returncode != 0:
                print("Verification FAILED: diff reported differences.")
                if diff_proc.stdout:
                    print(diff_proc.stdout)
                shutil.rmtree(tmp_dest, ignore_errors=True)
                print("Temporary copy removed. Aborting.")
                sys.exit(3)
            else:
                print("Verification OK (no differences).")
        else:
            print("DRY RUN: would run diff -r ...")

        # 4) Move temporary backup into final timestamped destination
        print(f"[4/4] Installing directory backup: {dest}")
        if not args.dry_run:
            ensure_dir(os.path.dirname(dest))
            # tmp_dest is full copy of src; move it to dest (atomic rename)
            os.replace(tmp_dest, dest)
            print("Directory backup created at:", dest)
            print("Archive saved at:", archive_path)

            # Update stable symlink /root/<email>.gemini -> timestamped dir
            if latest_symlink:
                try:
                    print(f"Updating latest symlink: {latest_symlink} -> {dest}")
                    atomic_symlink(dest, latest_symlink)
                except Exception as e:
                    print("Failed to update latest symlink:", e)
            else:
                print("No active email available; skipping latest symlink.")
        else:
            print("DRY RUN: would os.replace(tmp_dest, dest) and update symlink if available")

        print("Backup complete.")
    finally:
        try:
            fcntl.flock(lockfd, fcntl.LOCK_UN)
            lockfd.close()
        except Exception:
            pass

if __name__ == "__main__":
    main()