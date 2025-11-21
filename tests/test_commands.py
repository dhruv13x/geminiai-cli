import pytest
from unittest.mock import patch, mock_open, MagicMock
# import commands individually as geminiai_cli.commands does not exist
from geminiai_cli.login import do_login
from geminiai_cli.logout import do_logout
from geminiai_cli.update import do_update, do_check_update

@patch("geminiai_cli.login.run_cmd_safe")
@patch("geminiai_cli.login.read_file", return_value="verification code")
def test_do_login_second_run(mock_read_file, mock_run_cmd_safe):
    # Mock run_cmd_safe to return success
    mock_run_cmd_safe.return_value = (0, "", "")
    do_login()
    # login.py calls run_cmd_safe with "gemini 2> {LOGIN_URL_PATH}"
    # check arguments
    assert mock_run_cmd_safe.called

@patch("geminiai_cli.login.run_cmd_safe")
@patch("geminiai_cli.login.read_file", side_effect=Exception("file not found"))
def test_do_login_first_run(mock_read_file, mock_run_cmd_safe):
    # Simulates first run where "choose a login method" is found in output
    mock_run_cmd_safe.side_effect = [
        (0, "Choose a login method", ""), # First attempt
        (0, "", ""), # Selection
        (0, "https://example.com", "") # Second attempt
    ]
    do_login(retries=1)
    assert mock_run_cmd_safe.call_count >= 2

@patch("geminiai_cli.login.run_cmd_safe")
@patch("geminiai_cli.login.read_file", return_value="")
def test_do_login_fail(mock_read_file, mock_run_cmd_safe):
    # Fail all attempts
    mock_run_cmd_safe.return_value = (1, "error", "error")
    do_login(retries=1)
    assert mock_run_cmd_safe.called

@patch("geminiai_cli.login.run_cmd_safe")
@patch("geminiai_cli.login.read_file", side_effect=Exception("File read error"))
def test_do_login_file_read_error(mock_read_file, mock_run_cmd_safe):
    mock_run_cmd_safe.return_value = (0, "output", "error")
    do_login(retries=1)
    assert mock_run_cmd_safe.called

@patch("geminiai_cli.login.run_cmd_safe")
@patch("geminiai_cli.login.read_file", return_value="")
def test_do_login_success_with_code(mock_read_file, mock_run_cmd_safe):
    mock_run_cmd_safe.return_value = (0, "Verification code: ABC-123", "")
    do_login(retries=1)
    assert mock_run_cmd_safe.called

import os

@patch("os.path.exists", return_value=True)
@patch("geminiai_cli.logout.run")
def test_do_logout_exists(mock_run, mock_exists):
    do_logout()
    mock_run.assert_any_call(f"rm -rf {os.path.expanduser('~/.gemini')}")

@patch("os.path.exists", return_value=False)
@patch("geminiai_cli.logout.run")
def test_do_logout_not_exists(mock_run, mock_exists):
    do_logout()
    assert mock_run.call_count == 1

@patch("geminiai_cli.update.run_cmd_safe")
def test_do_update(mock_run_cmd_safe):
    mock_run_cmd_safe.return_value = (0, "ok", "")
    do_update()
    # check calls to run_cmd_safe
    args_list = [c[0][0] for c in mock_run_cmd_safe.call_args_list]
    assert "rm -f /usr/bin/gemini" in args_list
    assert "npm install -g @google/gemini-cli" in args_list

@patch("geminiai_cli.update.run_cmd_safe")
def test_do_check_update_latest(mock_run_cmd_safe):
    # Mock responses for:
    # 1. command -v gemini -> /usr/bin/gemini
    # 2. gemini --version -> 1.0.0
    # 3. npm view ... -> 1.0.0
    mock_run_cmd_safe.side_effect = [
        (0, "/usr/bin/gemini", ""),
        (0, "1.0.0", ""),
        (0, "1.0.0", "")
    ]
    do_check_update()

@patch("geminiai_cli.update.run_cmd_safe")
@patch("builtins.input", return_value="n")
def test_do_check_update_available_no(mock_input, mock_run_cmd_safe):
    mock_run_cmd_safe.side_effect = [
        (0, "/usr/bin/gemini", ""),
        (0, "1.0.0", ""),
        (0, "1.0.1", "")
    ]
    do_check_update()

@patch("geminiai_cli.update.run_cmd_safe")
@patch("builtins.input", return_value="y")
@patch("geminiai_cli.update.do_update")
def test_do_check_update_available_yes(mock_do_update, mock_input, mock_run_cmd_safe):
    mock_run_cmd_safe.side_effect = [
        (0, "/usr/bin/gemini", ""),
        (0, "1.0.0", ""),
        (0, "1.0.1", "")
    ]
    do_check_update()
    mock_do_update.assert_called_once()

@patch("geminiai_cli.update.run_cmd_safe")
def test_do_check_update_no_gemini(mock_run_cmd_safe):
    mock_run_cmd_safe.return_value = (1, "", "")
    do_check_update()

@patch("geminiai_cli.update.run_cmd_safe")
def test_do_check_update_version_fail(mock_run_cmd_safe):
    mock_run_cmd_safe.side_effect = [
        (0, "/usr/bin/gemini", ""),
        (1, "", "error")
    ]
    do_check_update()

@patch("geminiai_cli.update.run_cmd_safe")
@patch("builtins.input", return_value="n")
def test_do_check_update_npm_fail(mock_input, mock_run_cmd_safe):
    mock_run_cmd_safe.side_effect = [
        (0, "/usr/bin/gemini", ""),
        (0, "1.0.0", ""),
        (1, "", "error")
    ]
    do_check_update()

@patch("geminiai_cli.update.run_cmd_safe")
def test_do_update_fail(mock_run_cmd_safe):
    mock_run_cmd_safe.return_value = (1, "error", "error")
    do_update()

@patch("geminiai_cli.update.run_cmd_safe")
def test_do_update_retry_success(mock_run_cmd_safe):
    # First fail, then retry success
    mock_run_cmd_safe.side_effect = [
        (0, "", ""), # rm
        (0, "/root", ""), # npm root
        (0, "", ""), # ls
        (1, "error", ""), # install fail
        (0, "success", ""), # retry success
        (0, "/usr/bin", "") # npm bin
    ]
    do_update()

@patch("geminiai_cli.update.run_cmd_safe")
def test_do_update_retry_fail(mock_run_cmd_safe):
    # First fail, retry fail
    mock_run_cmd_safe.side_effect = [
        (0, "", ""), # rm
        (0, "/root", ""), # npm root
        (0, "", ""), # ls
        (1, "error", ""), # install fail
        (1, "error", ""), # retry fail
        (0, "/usr/bin", "") # npm bin
    ]
    do_update()
