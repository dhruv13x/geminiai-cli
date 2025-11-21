import pytest
from unittest.mock import patch
from geminiai_cli.ui import cprint, banner
from geminiai_cli.config import NEON_GREEN, NEON_CYAN, NEON_MAGENTA, RESET

@patch("sys.stdout.isatty", return_value=True)
def test_cprint_tty(mock_isatty, capsys):
    cprint(NEON_GREEN, "Hello")
    captured = capsys.readouterr()
    assert captured.out == f"{NEON_GREEN}Hello{RESET}\n"

@patch("sys.stdout.isatty", return_value=False)
def test_cprint_no_tty(mock_isatty, capsys):
    cprint(NEON_GREEN, "Hello")
    captured = capsys.readouterr()
    assert captured.out == "Hello\n"

def test_banner(capsys):
    banner()
    captured = capsys.readouterr()
    assert "GEMINI AUTOMATION SCRIPT" in captured.out
