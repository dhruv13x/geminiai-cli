import pytest
from unittest.mock import patch
from geminiai_cli.cli import main

@patch("geminiai_cli.cli.do_login")
def test_main_login(mock_do_login):
    with patch("sys.argv", ["sgemini.py", "--login"]):
        main()
        mock_do_login.assert_called_once()

@patch("geminiai_cli.cli.do_logout")
def test_main_logout(mock_do_logout):
    with patch("sys.argv", ["sgemini.py", "--logout"]):
        main()
        mock_do_logout.assert_called_once()

@patch("geminiai_cli.cli.do_update")
def test_main_update(mock_do_update):
    with patch("sys.argv", ["sgemini.py", "--update"]):
        main()
        mock_do_update.assert_called_once()

@patch("geminiai_cli.cli.do_check_update")
def test_main_check_update(mock_do_check_update):
    with patch("sys.argv", ["sgemini.py", "--check-update"]):
        main()
        mock_do_check_update.assert_called_once()

@patch("geminiai_cli.cli.banner")
def test_main_no_args(mock_banner):
    with patch("sys.argv", ["sgemini.py"]):
        main()
        mock_banner.assert_called_once()
