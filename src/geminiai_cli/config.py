#!/usr/bin/env python3
# src/geminiai_cli/config.py


import os
import re

# 🔥 NEON COLOR THEME (Bright & Glowing)
NEON_GREEN   = "\033[92;1m"
NEON_CYAN    = "\033[96;1m"
NEON_YELLOW  = "\033[93;1m"
NEON_MAGENTA = "\033[95;1m"
NEON_RED     = "\033[91;1m"
RESET        = "\033[0m"

# Dynamic Paths
DEFAULT_GEMINI_HOME = os.path.join(os.path.expanduser("~"), ".gemini")
GEMINIAI_WORK_DIR = os.path.join(os.path.expanduser("~"), "geminiai")

# Sub-directories
DEFAULT_BACKUP_DIR = os.path.join(GEMINIAI_WORK_DIR, "backups")
GEMINIAI_DATA_DIR = os.path.join(GEMINIAI_WORK_DIR, "data")
GEMINIAI_ARCHIVE_DIR = os.path.join(GEMINIAI_WORK_DIR, "archive")

# Ensure base directories exist
for _dir in [GEMINIAI_WORK_DIR, DEFAULT_BACKUP_DIR, GEMINIAI_DATA_DIR, GEMINIAI_ARCHIVE_DIR]:
    os.makedirs(_dir, exist_ok=True)

LOGIN_URL_PATH = "/sdcard/tools/login_url.txt"
TIMESTAMPED_DIR_REGEX = re.compile(r"^(\d{4}-\d{2}-\d{2}_\d{6})-.+\.gemini(\.tar\.gz)?$")
