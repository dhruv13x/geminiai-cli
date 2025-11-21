#!/usr/bin/env python3

import os
import sys

from .config import NEON_GREEN, NEON_CYAN, NEON_YELLOW, NEON_MAGENTA, NEON_RED, RESET

def cprint(color, text):
    if sys.stdout.isatty():
        print(color + text + RESET)
    else:
        print(text)

def banner():
    cprint(NEON_MAGENTA,
    "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
    cprint(NEON_CYAN,
    "┃      🚀  GEMINI AUTOMATION SCRIPT (NEON)  🚀     ┃")
    cprint(NEON_MAGENTA,
    "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n")
