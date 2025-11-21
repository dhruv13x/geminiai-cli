#!/usr/bin/env python3

import os
import subprocess
import sys
from .ui import cprint
from .config import NEON_RED



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
