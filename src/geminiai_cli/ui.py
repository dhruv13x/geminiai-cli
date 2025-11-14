#!/usr/bin/env python3

from .config import NEON_GREEN, NEON_CYAN, NEON_YELLOW, NEON_MAGENTA, NEON_RED, RESET

def cprint(color, text):
    print(color + text + RESET)

def banner():
    cprint(NEON_MAGENTA,
    "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
    cprint(NEON_CYAN,
    "┃      🚀  GEMINI AUTOMATION SCRIPT (NEON)  🚀     ┃")
    cprint(NEON_MAGENTA,
    "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n")
