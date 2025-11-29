#!/usr/bin/env python3
import argparse
from geminiai_cli.cooldown import record_switch

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bucket", help="B2 Bucket Name")
    parser.add_argument("--b2-id", help="B2 Key ID")
    parser.add_argument("--b2-key", help="B2 App Key")
    args = parser.parse_args()

    print("Running merge test: recording switch for user_C...")
    record_switch("user_C@example.com", args=args)
    print("Test execution finished.")

if __name__ == "__main__":
    main()
