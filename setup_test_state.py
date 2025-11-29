#!/usr/bin/env python3
import argparse
import json
import os
import datetime

from geminiai_cli.cooldown import _sync_cooldown_file

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bucket", help="B2 Bucket Name")
    parser.add_argument("--b2-id", help="B2 Key ID")
    parser.add_argument("--b2-key", help="B2 App Key")
    args = parser.parse_args()

    # 1. Create and upload the master file with user_A
    print("1. Creating master cloud state with user_A...")
    master_data = {
        "user_A@example.com": (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=2)).isoformat()
    }
    local_path = os.path.expanduser("~/.gemini-cooldown.json")
    
    with open(local_path, "w") as f:
        json.dump(master_data, f)
        
    _sync_cooldown_file(direction='upload', args=args)
    print("   Master state uploaded.")

    # 2. Create a stale local file with user_B
    print("2. Creating stale local state with user_B...")
    stale_data = {
        "user_B@example.com": (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=10)).isoformat()
    }
    with open(local_path, "w") as f:
        json.dump(stale_data, f)
    print("   Stale local file created.")
    print("\nSetup complete.")

if __name__ == "__main__":
    main()
