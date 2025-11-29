#!/usr/bin/env python3
# src/geminiai_cli/cooldown.py

import os
import json
import datetime
from typing import Dict, Optional

from .ui import cprint, NEON_CYAN, NEON_GREEN, NEON_YELLOW, NEON_RED, RESET
from .b2 import B2Manager
from .credentials import resolve_credentials


COOLDOWN_FILE_PATH = os.path.join(os.path.expanduser("~"), ".gemini-cooldown.json")
CLOUD_COOLDOWN_FILENAME = "gemini-cooldown.json"
COOLDOWN_HOURS = 24


def _sync_cooldown_file(direction: str, args):
    """
    Private helper to sync the cooldown file with B2 cloud storage.

    Args:
        direction: 'upload' or 'download'.
        args: Command-line arguments containing B2 credentials.
    """
    try:
        key_id, app_key, bucket_name = resolve_credentials(args)
        if not all([key_id, app_key, bucket_name]):
            cprint(NEON_YELLOW, "Warning: Cloud credentials not fully configured. Skipping cloud sync.")
            return

        b2 = B2Manager(key_id, app_key, bucket_name)
        local_path = os.path.expanduser(COOLDOWN_FILE_PATH)

        if direction == "download":
            cprint(NEON_CYAN, f"Downloading latest cooldown file from B2 bucket '{bucket_name}'...")
            try:
                b2.download(CLOUD_COOLDOWN_FILENAME, local_path)
                cprint(NEON_GREEN, "Cooldown file synced from cloud.")
            except Exception as e:
                # It's okay if the file doesn't exist yet in the cloud
                if "file_not_present" in str(e) or "No such file" in str(e):
                    cprint(NEON_YELLOW, "No cooldown file found in the cloud. Using local version.")
                else:
                    cprint(NEON_RED, f"Error downloading cooldown file: {e}")

        elif direction == "upload":
            if not os.path.exists(local_path):
                cprint(NEON_YELLOW, "Local cooldown file not found. Skipping upload.")
                return
            cprint(NEON_CYAN, f"Uploading cooldown file to B2 bucket '{bucket_name}'...")
            try:
                b2.upload(local_path, CLOUD_COOLDOWN_FILENAME)
                cprint(NEON_GREEN, "Cooldown file synced to cloud.")
            except Exception as e:
                cprint(NEON_RED, f"Error uploading cooldown file: {e}")

    except Exception as e:
        cprint(NEON_RED, f"An unexpected error occurred during cloud sync: {e}")


def get_cooldown_data() -> Dict[str, str]:
    """
    Reads the cooldown data from the JSON file.

    Returns:
        A dictionary mapping email addresses to their last switch timestamp (ISO 8601).
        Returns an empty dictionary if the file doesn't exist or is invalid.
    """
    path = os.path.expanduser(COOLDOWN_FILE_PATH)
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
            return {}
    except (json.JSONDecodeError, IOError):
        return {}

def record_switch(email: str, args=None):
    """
    Records an account switch using a "merge-before-write" strategy for cloud sync.
    It downloads the latest state from the cloud, adds the new entry, and uploads.

    Args:
        email: The email address of the account that has become active.
        args: Optional command-line arguments for cloud credentials.
    """
    if not email:
        return
        
    # If cloud is configured, sync down the master file first to merge with it.
    if args:
        _sync_cooldown_file(direction='download', args=args)
        
    path = os.path.expanduser(COOLDOWN_FILE_PATH)
    # Now, get the most up-to-date data (either from cloud or local).
    data = get_cooldown_data()
    
    # Get current time in ISO 8601 format and update the record.
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    data[email] = now_iso
    
    try:
        # Write the newly merged data back to the local file.
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        cprint(NEON_RED, f"Error: Could not write to local cooldown file at {path}: {e}")
        return # Don't proceed to upload if local write failed

    # If cloud is configured, sync the merged file back up.
    if args:
        _sync_cooldown_file(direction='upload', args=args)

def do_cooldown_list(args=None):
    """
    Displays the cooldown status for all tracked accounts.
    Syncs from the cloud first if cloud args are provided.
    """
    # If cloud args are provided, trigger a download first
    if args and getattr(args, 'cloud', False):
        _sync_cooldown_file(direction='download', args=args)

    cprint(NEON_CYAN, "🕰️ Checking account cooldown status...")
    
    data = get_cooldown_data()
    
    if not data:
        cprint(NEON_YELLOW, "No account switch data found. All accounts are ready to use.")
        return
        
    now = datetime.datetime.now(datetime.timezone.utc)
    cooldown_delta = datetime.timedelta(hours=COOLDOWN_HOURS)
    
    # Sort by email address for consistent output
    sorted_emails = sorted(data.keys())

    for email in sorted_emails:
        last_switch_str = data[email]
        try:
            last_switch_time = datetime.datetime.fromisoformat(last_switch_str)
            
            # Ensure timestamp is timezone-aware for correct comparison
            if last_switch_time.tzinfo is None:
                last_switch_time = last_switch_time.replace(tzinfo=datetime.timezone.utc)

            time_since_switch = now - last_switch_time
            
            if time_since_switch >= cooldown_delta:
                cprint(NEON_GREEN, f"✅ {email:<40} Ready to use")
            else:
                time_remaining = cooldown_delta - time_since_switch
                
                # Formatting the remaining time
                hours, remainder = divmod(time_remaining.total_seconds(), 3600)
                minutes, _ = divmod(remainder, 60)
                
                cprint(NEON_YELLOW, f"⏳ {email:<40} Cooldown active: {int(hours)}h {int(minutes)}m remaining")

        except ValueError:
            cprint(NEON_RED, f"❌ {email:<40} Invalid timestamp format: {last_switch_str}")

