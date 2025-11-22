import pytest
from unittest.mock import patch, mock_open, MagicMock
import subprocess
import os
import sys

# Import commands individually
from geminiai_cli.login import do_login
from geminiai_cli.logout import do_logout
from geminiai_cli.update import do_update, do_check_update
from geminiai_cli.utils import run, read_file
from geminiai_cli.reset_helpers import run_cmd_safe, save_reset_time_from_output # Ensure run_cmd_safe is imported correctly
from geminiai_cli.config import LOGIN_URL_PATH

# --- Tests for do_login ---

@patch("geminiai_cli.reset_helpers.run_cmd_safe")
@patch("geminiai_cli.utils.read_file")
def test_do_login_second_run(mock_read_file, mock_run_cmd_safe):
    # Mock run_cmd_safe to return success with a URL
    mock_run_cmd_safe.return_value = (0, "https://example.com/auth", "")
    mock_read_file.return_value = "https://example.com/auth" # Simulate file content
    
    do_login()
    # login.py calls run_cmd_safe with "gemini 2> {LOGIN_URL_PATH}"
    mock_run_cmd_safe.assert_called_with(f"gemini 2> {LOGIN_URL_PATH}", timeout=30, capture=True)
    assert mock_run_cmd_safe.call_count == 1
    # Check that read_file was called
    mock_read_file.assert_called_with(LOGIN_URL_PATH)


@patch("geminiai_cli.reset_helpers.run_cmd_safe")
@patch("geminiai_cli.utils.read_file")
def test_do_login_first_run(mock_read_file, mock_run_cmd_safe):
    # Simulates first run where "choose a login method" is found in output
    mock_run_cmd_safe.side_effect = [
        # First attempt: output indicates interactive menu
        (0, "Choose a login method", ""), 
        # Second attempt: after sending ENTER, returns URL
        (0, "https://example.com/auth-interactive", ""),
        # Third attempt (from login.py) after sleep to capture URL
        (0, "https://example.com/auth-interactive-final", ""), 
    ]
    mock_read_file.return_value = "https://example.com/auth-interactive-final" # Simulate file content
    
    do_login(retries=1)
    # Expect at least 3 calls for the interactive flow: initial, enter, final capture
    assert mock_run_cmd_safe.call_count >= 3
    # Check that it tried to send ENTER
    assert any("printf \"\\n\" | gemini" in call[0][0] for call in mock_run_cmd_safe.call_args_list)
    mock_read_file.assert_called_with(LOGIN_URL_PATH)


@patch("geminiai_cli.reset_helpers.run_cmd_safe")
@patch("geminiai_cli.utils.read_file", return_value="")
def test_do_login_fail(mock_read_file, mock_run_cmd_safe):
    # Fail all attempts - return no URL/code in output
    mock_run_cmd_safe.return_value = (1, "error", "error")
    # Redirect stderr to suppress output during test
    with patch('sys.stderr', new_callable=MagicMock):
        do_login(retries=1) # Reduced retries to speed up test if it actually loops
    assert mock_run_cmd_safe.called
    # Assert that read_file was called even in failure to get preview
    mock_read_file.assert_called_with(LOGIN_URL_PATH)


@patch("geminiai_cli.reset_helpers.run_cmd_safe")
@patch("geminiai_cli.utils.read_file", side_effect=Exception("File read error"))
def test_do_login_file_read_error(mock_read_file, mock_run_cmd_safe):
    mock_run_cmd_safe.return_value = (0, "output", "error") # Should return something to exit loop
    with patch('sys.stderr', new_callable=MagicMock):
        do_login(retries=1)
    assert mock_run_cmd_safe.called
    mock_read_file.assert_called_with(LOGIN_URL_PATH)


@patch("geminiai_cli.reset_helpers.run_cmd_safe")
@patch("geminiai_cli.utils.read_file")
def test_do_login_success_with_code(mock_read_file, mock_run_cmd_safe):
    mock_run_cmd_safe.return_value = (0, "Verification code: ABC-123", "")
    mock_read_file.return_value = "Verification code: ABC-123" # Simulate file content
    do_login(retries=1)
    assert mock_run_cmd_safe.called
    mock_read_file.assert_called_with(LOGIN_URL_PATH)

# --- Tests for do_logout ---

@patch("os.path.exists", return_value=True)
@patch("geminiai_cli.utils.run")
def test_do_logout_exists(mock_run, mock_exists):
    do_logout()
    expected_rm_call = f"rm -rf {os.path.expanduser('~/.gemini')}"
    expected_ls_call = "ls -d ~/.gemini || echo '[OK] Logout complete.'"
    mock_run.assert_any_call(expected_rm_call)
    mock_run.assert_any_call(expected_ls_call)
    assert mock_run.call_count == 2 # Ensure only these two were called


@patch("os.path.exists", return_value=False)
@patch("geminiai_cli.utils.run")
def test_do_logout_not_exists(mock_run, mock_exists):
    do_logout()
    expected_ls_call = "ls -d ~/.gemini || echo '[OK] Logout complete.'"
    mock_run.assert_any_call(expected_ls_call)
    assert not any("rm -rf" in call[0][0] for call in mock_run.call_args_list) # No rm -rf call
    assert mock_run.call_count == 1 # Only ls call

# --- Tests for do_update and do_check_update ---

@patch("geminiai_cli.update.run_cmd_safe")
def test_do_update(mock_run_cmd_safe):
    mock_run_cmd_safe.return_value = (0, "ok", "")
    do_update()
    args_list = [c[0][0] for c in mock_run_cmd_safe.call_args_list]
    assert "rm -f /usr/bin/gemini" in args_list
    assert "npm install -g @google/gemini-cli" in args_list

@patch("geminiai_cli.update.run_cmd_safe")
def test_do_check_update_latest(mock_run_cmd_safe):
    mock_run_cmd_safe.side_effect = [
        (0, "/usr/bin/gemini", ""), # command -v gemini
        (0, "1.0.0", ""),            # gemini --version
        (0, "1.0.0", "")             # npm view @google/gemini-cli version
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
    mock_run_cmd_safe.return_value = (1, "", "") # command -v gemini fails
    do_check_update()

@patch("geminiai_cli.update.run_cmd_safe")
def test_do_check_update_version_fail(mock_run_cmd_safe):
    mock_run_cmd_safe.side_effect = [
        (0, "/usr/bin/gemini", ""), # command -v gemini
        (1, "", "error")             # gemini --version fails
    ]
    do_check_update()

@patch("geminiai_cli.update.run_cmd_safe")
@patch("builtins.input", return_value="n")
def test_do_check_update_npm_fail(mock_input, mock_run_cmd_safe):
    mock_run_cmd_safe.side_effect = [
        (0, "/usr/bin/gemini", ""), # command -v gemini
        (0, "1.0.0", ""),            # gemini --version
        (1, "", "error")             # npm view fails
    ]
    do_check_update()

@patch("geminiai_cli.update.run_cmd_safe")
def test_do_update_fail(mock_run_cmd_safe):
    mock_run_cmd_safe.return_value = (1, "error", "error")
    # Redirect stderr to suppress output during test
    with patch('sys.stderr', new_callable=MagicMock):
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
    # Redirect stderr to suppress output during test
    with patch('sys.stderr', new_callable=MagicMock):
        do_update()
