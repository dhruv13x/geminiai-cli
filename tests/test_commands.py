import pytest
from unittest.mock import patch, mock_open
from geminiai_cli.commands import do_login, do_logout, do_update, do_check_update

@patch("geminiai_cli.commands.run")
@patch("geminiai_cli.commands.read_file", return_value="verification code")
def test_do_login_second_run(mock_read_file, mock_run):
    do_login()
    mock_run.assert_called_with("gemini 2> /sdcard/tools/login_url.txt")
    assert mock_run.call_count == 1

@patch("geminiai_cli.commands.run")
@patch("geminiai_cli.commands.read_file", return_value="")
def test_do_login_first_run(mock_read_file, mock_run):
    do_login()
    assert mock_run.call_count == 3

import os

@patch("os.path.exists", return_value=True)
@patch("geminiai_cli.commands.run")
def test_do_logout_exists(mock_run, mock_exists):
    do_logout()
    mock_run.assert_any_call(f"rm -rf {os.path.expanduser('~/.gemini')}")

@patch("os.path.exists", return_value=False)
@patch("geminiai_cli.commands.run")
def test_do_logout_not_exists(mock_run, mock_exists):
    do_logout()
    assert mock_run.call_count == 1

@patch("geminiai_cli.commands.run")
def test_do_update(mock_run):
    do_update()
    mock_run.assert_any_call("rm -f /usr/bin/gemini")
    mock_run.assert_any_call("npm install -g @google/gemini-cli")
    mock_run.assert_any_call("gemini --version")

@patch("geminiai_cli.commands.run_capture", side_effect=["1.0.0", "1.0.0"])
def test_do_check_update_latest(mock_run_capture):
    do_check_update()

@patch("geminiai_cli.commands.run_capture", side_effect=["1.0.0", "1.0.1"])
@patch("builtins.input", return_value="n")
def test_do_check_update_available_no(mock_input, mock_run_capture):
    do_check_update()

@patch("geminiai_cli.commands.run_capture", side_effect=["1.0.0", "1.0.1"])
@patch("builtins.input", return_value="y")
@patch("geminiai_cli.commands.do_update")
def test_do_check_update_available_yes(mock_do_update, mock_input, mock_run_capture):
    do_check_update()
    mock_do_update.assert_called_once()
