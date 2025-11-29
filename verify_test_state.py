#!/usr/bin/env python3
import argparse
import json
import os
import sys

from geminiai_cli.cooldown import _sync_cooldown_file

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bucket", help="B2 Bucket Name")
    parser.add_argument("--b2-id", help="B2 Key ID")
    parser.add_argument("--b2-key", help="B2 App Key")
    args = parser.parse_args()

    print("Verifying final state from cloud...")
    
    # Download the final version
    _sync_cooldown_file(direction='download', args=args)
    
    local_path = os.path.expanduser("~/.gemini-cooldown.json")
    
    with open(local_path, "r") as f:
        final_data = json.load(f)

    print("Final data from cloud:", json.dumps(final_data, indent=2))

    # Verification checks
    has_user_A = "user_A@example.com" in final_data
    has_user_C = "user_C@example.com" in final_data
    has_user_B = "user_B@example.com" in final_data

    if has_user_A and has_user_C and not has_user_B:
        print("\n✅ PASSED: Final state is correct. (user_A and user_C exist, user_B was discarded)")
        sys.exit(0)
    else:
        print("\n❌ FAILED: Final state is incorrect.")
        print(f"  - Expected user_A to be present: {has_user_A}")
        print(f"  - Expected user_C to be present: {has_user_C}")
        print(f"  - Expected user_B to be absent: {not has_user_B}")
        sys.exit(1)

if __name__ == "__main__":
    main()
