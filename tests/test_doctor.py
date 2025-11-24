import pytest
from unittest.mock import patch, MagicMock
import os
from geminiai_cli.doctor import do_doctor

@patch("geminiai_cli.doctor.shutil.which")
@patch("geminiai_cli.doctor.os.path.isdir")
@patch("geminiai_cli.doctor.os.access")
@patch("geminiai_cli.doctor.urllib.request.urlopen")
@patch("geminiai_cli.doctor.get_setting")
@patch("geminiai_cli.doctor.B2Manager")
@patch("geminiai_cli.doctor.console.print")
def test_do_doctor(mock_print, mock_b2, mock_get_setting, mock_urlopen, mock_access, mock_isdir, mock_which):
    # Setup mocks
    mock_which.side_effect = lambda x: f"/usr/bin/{x}" if x != "missing_tool" else None
    mock_isdir.return_value = True
    mock_access.return_value = True
    mock_get_setting.side_effect = lambda x: "test_value" if x in ["b2_id", "b2_key", "bucket"] else None

    do_doctor()

    # Assertions
    assert mock_print.call_count >= 2 # Header, Table, Footer

@patch("geminiai_cli.doctor.shutil.which")
@patch("geminiai_cli.doctor.os.path.isdir")
@patch("geminiai_cli.doctor.os.access")
@patch("geminiai_cli.doctor.urllib.request.urlopen")
@patch("geminiai_cli.doctor.get_setting")
@patch("geminiai_cli.doctor.B2Manager")
@patch("geminiai_cli.doctor.console.print")
def test_do_doctor_failures(mock_print, mock_b2, mock_get_setting, mock_urlopen, mock_access, mock_isdir, mock_which):
    # Setup mocks for failures
    mock_which.return_value = None # No tools
    mock_isdir.return_value = False # No dirs
    mock_urlopen.side_effect = Exception("No Internet") # No internet
    mock_get_setting.return_value = None # No B2 Creds

    do_doctor()

    assert mock_print.call_count >= 2

@patch("geminiai_cli.doctor.shutil.which")
@patch("geminiai_cli.doctor.os.path.isdir")
@patch("geminiai_cli.doctor.os.access")
@patch("geminiai_cli.doctor.urllib.request.urlopen")
@patch("geminiai_cli.doctor.get_setting")
@patch("geminiai_cli.doctor.B2Manager")
@patch("geminiai_cli.doctor.console.print")
def test_do_doctor_b2_fail(mock_print, mock_b2, mock_get_setting, mock_urlopen, mock_access, mock_isdir, mock_which):
    # Setup mocks for B2 fail
    mock_which.return_value = "/bin/tool"
    mock_isdir.return_value = True
    mock_access.return_value = False # Read-only dir
    mock_urlopen.return_value = True
    mock_get_setting.return_value = "test"
    mock_b2.side_effect = Exception("B2 Fail")

    do_doctor()

    assert mock_print.call_count >= 2
