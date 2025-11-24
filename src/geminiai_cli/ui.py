#!/usr/bin/env python3

import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.text import Text

from .config import NEON_GREEN, NEON_CYAN, NEON_YELLOW, NEON_MAGENTA, NEON_RED, RESET

# Export console for use in other modules
console = Console()

def cprint(color, text):
    """
    Legacy cprint wrapper using rich.
    concatenates color (ANSI) + text + RESET and renders it using Text.from_ansi
    to ensure ANSI codes are displayed correctly.
    """
    # Check if color or text is None to prevent TypeError
    full_text = (color or "") + (text or "") + (RESET or "")
    console.print(Text.from_ansi(full_text))

def banner():
    """
    Displays the ALICE banner using a Rich Panel.
    """
    title = "[bold cyan]🚀  ALICE (GEMINI AUTOMATION)  🚀[/]"
    panel = Panel(Align.center(title), style="bold magenta", expand=False)
    console.print(panel)
    console.print("") # Newline
