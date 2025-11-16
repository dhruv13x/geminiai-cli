import pytest
from geminiai_cli.ui import cprint, banner
from geminiai_cli.config import NEON_GREEN, NEON_CYAN, NEON_MAGENTA, RESET

def test_cprint(capsys):
    cprint(NEON_GREEN, "Hello")
    captured = capsys.readouterr()
    assert captured.out == f"{NEON_GREEN}Hello{RESET}\n"

def test_banner(capsys):
    banner()
    captured = capsys.readouterr()
    assert "GEMINI AUTOMATION SCRIPT" in captured.out
