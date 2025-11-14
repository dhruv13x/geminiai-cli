#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys

# 🔥 NEON COLOR THEME (Bright & Glowing)
NEON_GREEN   = "\033[92;1m"
NEON_CYAN    = "\033[96;1m"
NEON_YELLOW  = "\033[93;1m"
NEON_MAGENTA = "\033[95;1m"
NEON_RED     = "\033[91;1m"
RESET        = "\033[0m"

LOGIN_URL_PATH = "/sdcard/tools/login_url.txt"

def cprint(color, text):
    print(color + text + RESET)

def banner():
    cprint(NEON_MAGENTA,
    "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
    cprint(NEON_CYAN,
    "┃      🚀  GEMINI AUTOMATION SCRIPT (NEON)  🚀     ┃")
    cprint(NEON_MAGENTA,
    "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n")

def run_capture(cmd):
    """Run a shell command and capture output."""
    try:
        return subprocess.check_output(cmd, shell=True, text=True).strip()
    except subprocess.CalledProcessError:
        return None

def run(cmd):
    """Run a shell command and stream output."""
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        cprint(NEON_RED, f"[ERROR] Command failed: {e}")
        sys.exit(1)

def read_file(path):
    """Safe file reader."""
    if not os.path.exists(path):
        return ""
    try:
        with open(path, "r", errors="ignore") as f:
            return f.read()
    except:
        return ""

def do_login():
    banner()

    cprint(NEON_YELLOW, "[INFO] Starting Gemini login flow...")
    cprint(NEON_YELLOW, f"[INFO] Saving output to: {NEON_CYAN}{LOGIN_URL_PATH}{RESET}")

    # ---------------------------------------------------
    # STEP 1 — FIRST RUN
    # ---------------------------------------------------
    cprint(NEON_YELLOW, "[INFO] Running FIRST command: gemini 2> login_url.txt")
    run(f"gemini 2> {LOGIN_URL_PATH}")

    output1 = read_file(LOGIN_URL_PATH).lower().strip()

    # ---------------------------------------------------
    # DETECT IF THIS IS FIRST RUN OR SECOND RUN
    # ---------------------------------------------------
    if "verification code" in output1 or "open this link" in output1 or "https://" in output1:
        # Already second run – do not press Enter
        cprint(NEON_GREEN, "[INFO] SECOND RUN detected immediately — skipping ENTER.")
    else:
        # FIRST RUN — press ENTER to choose Browser Login
        cprint(NEON_MAGENTA, "[INFO] FIRST RUN detected.")
        cprint(NEON_YELLOW, "[INFO] Auto-selecting Browser Login by pressing ENTER...")

        run(f'printf "\\n" | gemini 2> {LOGIN_URL_PATH}')

        cprint(NEON_GREEN, "[OK] Browser login selected.")

        # Now perform the actual second run
        cprint(NEON_YELLOW, "[INFO] Running SECOND command to get auth link...")
        run(f"gemini 2> {LOGIN_URL_PATH}")

    # ---------------------------------------------------
    # READ FINAL OUTPUT
    # ---------------------------------------------------
    output2 = read_file(LOGIN_URL_PATH)

    cprint(NEON_GREEN, "\n[OK] Authentication data captured.")
    cprint(NEON_CYAN, f"Saved at: {LOGIN_URL_PATH}\n")

    # Preview
    preview = "\n".join(output2.splitlines()[:15])
    cprint(NEON_MAGENTA, "Preview:")
    print(preview + "\n")

    # Instructions
    cprint(NEON_YELLOW, "✔ Open the URL in your browser")
    cprint(NEON_YELLOW, "✔ Complete the login")
    cprint(NEON_YELLOW, "✔ Copy the verification code shown in the browser")
    cprint(NEON_YELLOW, "✔ Gemini CLI will prompt for this code soon — paste it there\n")

    cprint(NEON_CYAN, "[INFO] Full file:")
    cprint(NEON_MAGENTA, f"  cat {LOGIN_URL_PATH}\n")
        
        
def do_logout():
    banner()

    gemini_dir = os.path.expanduser("~/.gemini")

    cprint(NEON_YELLOW, "[INFO] Logging out from Gemini CLI...")
    cprint(NEON_YELLOW, f"[INFO] Removing: {NEON_CYAN}{gemini_dir}{RESET}")

    if os.path.exists(gemini_dir):
        run(f"rm -rf {gemini_dir}")
        cprint(NEON_GREEN, "[OK] Directory removed.")
    else:
        cprint(NEON_GREEN, "[OK] Already logged out (directory missing).")

    cprint(NEON_YELLOW, "\n[INFO] Confirming logout status:")
    run("ls -d ~/.gemini || echo '[OK] Logout complete.'")

def do_update():
    banner()

    cprint(NEON_YELLOW, "[INFO] Updating Gemini CLI...")
    run("rm -f /usr/bin/gemini")
    run("npm install -g @google/gemini-cli")

    cprint(NEON_GREEN, "\n[OK] Update complete. Installed version:")
    run("gemini --version")

def do_check_update():
    banner()

    cprint(NEON_YELLOW, "[INFO] Checking Gemini CLI version...")

    installed = run_capture("gemini --version")
    latest = run_capture("npm view @google/gemini-cli version")

    if not installed:
        cprint(NEON_RED, "[ERROR] Gemini is not installed.")
        return

    cprint(NEON_CYAN, f"Installed version: {NEON_GREEN}{installed}")
    cprint(NEON_CYAN, f"Latest version:    {NEON_GREEN}{latest}")

    if installed == latest:
        cprint(NEON_GREEN, "\n[OK] You already have the latest version!")
        return

    cprint(NEON_MAGENTA, "\n⚡ Update available!")

    choice = input(NEON_YELLOW + "Do you want to update? (y/n): " + RESET).strip().lower()

    if choice == "y":
        do_update()
    else:
        cprint(NEON_CYAN, "Update cancelled.\n")

def main():
    parser = argparse.ArgumentParser(description="Gemini CLI Automation Script (Neon Theme)")
    parser.add_argument("--login", action="store_true", help="Login to Gemini CLI")
    parser.add_argument("--logout", action="store_true", help="Logout from Gemini CLI")
    parser.add_argument("--update", action="store_true", help="Reinstall / update Gemini CLI")
    parser.add_argument("--check-update", action="store_true", help="Check for updates")
    args = parser.parse_args()

    if args.login:
        do_login()
    elif args.logout:
        do_logout()
    elif args.update:
        do_update()
    elif args.check_update:
        do_check_update()
    else:
        banner()
        cprint(NEON_YELLOW, "Usage:")
        cprint(NEON_CYAN, "  python sgemini.py --login")
        cprint(NEON_CYAN, "  python sgemini.py --logout")
        cprint(NEON_CYAN, "  python sgemini.py --update")
        cprint(NEON_CYAN, "  python sgemini.py --check-update")

if __name__ == "__main__":
    main()