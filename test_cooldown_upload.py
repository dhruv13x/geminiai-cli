#!/usr/bin/env python3
import argparse
import os
from geminiai_cli.cooldown import record_switch
from geminiai_cli.credentials import resolve_credentials

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bucket", help="B2 Bucket Name")
    parser.add_argument("--b2-id", help="B2 Key ID")
    parser.add_argument("--b2-key", help="B2 App Key")
    args = parser.parse_args()

    # We need to ensure the local file exists first, as record_switch reads it
    # before writing and uploading.
    home_dir = os.path.expanduser("~")
    cooldown_file = os.path.join(home_dir, ".gemini-cooldown.json")
    if not os.path.exists(cooldown_file):
        with open(cooldown_file, "w") as f:
            f.write("{}")

    print("Simulating account switch for 'cloud.test@example.com'...")
    record_switch("cloud.test@example.com", args=args)
    print("Test complete. Check your B2 bucket for 'gemini-cooldown.json'.")

if __name__ == "__main__":
    main()
