import pytest
from unittest.mock import patch, mock_open
from src.geminiai_cli.utils import run_capture, run, read_file

@patch("subprocess.check_output")
def test_run_capture(mock_check_output):
    mock_check_output.return_value = "hello"
    assert run_capture("echo hello") == "hello"

import subprocess

@patch("subprocess.check_output", side_effect=subprocess.CalledProcessError(1, "cmd"))
def test_run_capture_exception(mock_check_output):
    assert run_capture("echo hello") == None

@patch("subprocess.run")
def test_run(mock_run):
    run("echo hello")
    mock_run.assert_called_with("echo hello", shell=True, check=True)

@patch("os.path.exists", return_value=False)
def test_read_file_not_exists(mock_exists):
    assert read_file("test.txt") == ""

@patch("os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data="hello")
def test_read_file_exists(mock_exists, mock_file):
    assert read_file("test.txt") == "hello"

@patch("os.path.exists", return_value=True)
@patch("builtins.open", side_effect=Exception)
def test_read_file_exception(mock_exists, mock_file):
    assert read_file("test.txt") == ""
