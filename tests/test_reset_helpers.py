import pytest
from unittest.mock import patch, mock_open, MagicMock
import os
import subprocess
from datetime import datetime, timedelta, timezone
from geminiai_cli import reset_helpers

def test_run_cmd_safe():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "output"
        mock_run.return_value.stderr = ""

        rc, out, err = reset_helpers.run_cmd_safe("ls")
        assert rc == 0
        assert out == "output"

@patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="ls", timeout=1))
def test_run_cmd_safe_timeout(mock_run):
    rc, out, err = reset_helpers.run_cmd_safe("ls")
    assert rc == 124

@patch("subprocess.run", side_effect=Exception("error"))
def test_run_cmd_safe_exception(mock_run):
    rc, out, err = reset_helpers.run_cmd_safe("ls")
    assert rc == 1

@patch("geminiai_cli.reset_helpers._load_store", return_value=[])
@patch("geminiai_cli.reset_helpers._save_store")
def test_add_reset_entry(mock_save, mock_load):
    # Mock time to avoid timezone issues
    with patch("geminiai_cli.reset_helpers._now_ist") as mock_now:
        mock_now.return_value = datetime(2025, 10, 22, 10, 0, tzinfo=timezone(timedelta(hours=5, minutes=30)))
        entry = reset_helpers.add_reset_entry("11:00 AM", "test@test.com")
        assert entry["email"] == "test@test.com"
        assert "reset_ist" in entry

def test_add_reset_entry_invalid():
    with pytest.raises(ValueError):
        reset_helpers.add_reset_entry("invalid")

@patch("geminiai_cli.reset_helpers._load_store")
@patch("geminiai_cli.reset_helpers._save_store")
def test_cleanup_expired(mock_save, mock_load):
    now = datetime.now(timezone(timedelta(hours=5, minutes=30)))
    past = now - timedelta(hours=1)
    future = now + timedelta(hours=1)

    mock_load.return_value = [
        {"reset_ist": past.isoformat()},
        {"reset_ist": future.isoformat()}
    ]

    removed = reset_helpers.cleanup_expired()
    assert len(removed) == 1
    mock_save.assert_called()

@patch("geminiai_cli.reset_helpers.add_reset_entry")
def test_save_reset_time_from_output(mock_add):
    mock_add.return_value = {"email": "test@test.com", "reset_ist": "iso"}
    assert reset_helpers.save_reset_time_from_output("Access resets at 11:00 AM UTC")

def test_save_reset_time_from_output_fail():
    assert not reset_helpers.save_reset_time_from_output("invalid")

@patch("builtins.input", return_value="AM")
@patch("geminiai_cli.reset_helpers.add_reset_entry")
def test_save_reset_time_from_output_ambiguous(mock_add, mock_input):
    # Should prompt for AM/PM
    assert reset_helpers.save_reset_time_from_output("Access resets at 10:00")
    mock_input.assert_called()

@patch("geminiai_cli.reset_helpers._load_and_cleanup_store", return_value=[])
def test_do_list_resets_empty(mock_load):
    reset_helpers.do_list_resets()

@patch("geminiai_cli.reset_helpers._load_and_cleanup_store")
def test_do_list_resets(mock_load):
    mock_load.return_value = [
        {"id": "1", "email": "t@t.com", "reset_ist": datetime.now().isoformat()}
    ]
    reset_helpers.do_list_resets()

@patch("geminiai_cli.reset_helpers._load_and_cleanup_store", return_value=[])
def test_do_next_reset_empty(mock_load):
    reset_helpers.do_next_reset()

@patch("geminiai_cli.reset_helpers._load_and_cleanup_store")
def test_do_next_reset(mock_load):
    future = datetime.now(timezone(timedelta(hours=5, minutes=30))) + timedelta(hours=1)
    mock_load.return_value = [
        {"id": "1", "email": "t@t.com", "reset_ist": future.isoformat()}
    ]
    reset_helpers.do_next_reset()

@patch("geminiai_cli.reset_helpers.save_reset_time_from_output", return_value=True)
def test_do_capture_reset_arg(mock_save):
    reset_helpers.do_capture_reset("text")
    mock_save.assert_called()

@patch("sys.stdin.isatty", return_value=False)
@patch("sys.stdin.read", return_value="text")
@patch("geminiai_cli.reset_helpers.save_reset_time_from_output", return_value=True)
def test_do_capture_reset_stdin(mock_save, mock_read, mock_isatty):
    reset_helpers.do_capture_reset()
    mock_save.assert_called()

@patch("sys.stdin.isatty", return_value=True)
@patch("builtins.input", return_value="text")
@patch("geminiai_cli.reset_helpers.save_reset_time_from_output", return_value=True)
def test_do_capture_reset_interactive(mock_save, mock_input, mock_isatty):
    reset_helpers.do_capture_reset()
    mock_save.assert_called()

@patch("geminiai_cli.reset_helpers._load_store")
@patch("geminiai_cli.reset_helpers._save_store")
def test_remove_entry_by_id(mock_save, mock_load):
    mock_load.return_value = [{"id": "123", "email": "test"}]
    assert reset_helpers.remove_entry_by_id("123")
    mock_save.assert_called()

@patch("geminiai_cli.reset_helpers._load_store")
@patch("geminiai_cli.reset_helpers._save_store")
def test_remove_entry_by_email(mock_save, mock_load):
    mock_load.return_value = [{"id": "123", "email": "test"}]
    assert reset_helpers.remove_entry_by_id("test")
    mock_save.assert_called()

@patch("geminiai_cli.reset_helpers._load_store")
def test_remove_entry_not_found(mock_load):
    mock_load.return_value = [{"id": "123", "email": "test"}]
    assert not reset_helpers.remove_entry_by_id("other")

def test_parse_time_from_text():
    assert reset_helpers._parse_time_from_text("10:00 AM") == (10, 0, "AM")
    assert reset_helpers._parse_time_from_text("10:00") == (10, 0, None)
    assert reset_helpers._parse_time_from_text("invalid") is None

def test_normalize_minutes():
    assert reset_helpers._normalize_minutes(60) == 59
    assert reset_helpers._normalize_minutes(-1) == 0
    assert reset_helpers._normalize_minutes(30) == 30

def test_parse_email_from_text():
    assert reset_helpers._parse_email_from_text("test test@example.com test") == "test@example.com"
    assert reset_helpers._parse_email_from_text("no email") is None

@patch("geminiai_cli.reset_helpers._now_ist")
def test_compute_next_ist_for_time_am(mock_now):
    mock_now.return_value = datetime(2023, 1, 1, 9, 0, tzinfo=timezone(timedelta(hours=5, minutes=30)))
    # 10 AM same day
    dt = reset_helpers._compute_next_ist_for_time(10, 0, "AM")
    assert dt.hour == 10
    assert dt.day == 1

@patch("geminiai_cli.reset_helpers._now_ist")
def test_compute_next_ist_for_time_pm(mock_now):
    mock_now.return_value = datetime(2023, 1, 1, 9, 0, tzinfo=timezone(timedelta(hours=5, minutes=30)))
    # 1 PM (13:00) same day
    dt = reset_helpers._compute_next_ist_for_time(1, 0, "PM")
    assert dt.hour == 13
    assert dt.day == 1

@patch("geminiai_cli.reset_helpers._now_ist")
def test_compute_next_ist_for_time_next_day(mock_now):
    mock_now.return_value = datetime(2023, 1, 1, 11, 0, tzinfo=timezone(timedelta(hours=5, minutes=30)))
    # 10 AM next day
    dt = reset_helpers._compute_next_ist_for_time(10, 0, "AM")
    assert dt.hour == 10
    assert dt.day == 2

def test_load_store_no_file():
    with patch("os.path.exists", return_value=False):
        assert reset_helpers._load_store() == []

def test_load_store_invalid_json():
    with patch("os.path.exists", return_value=True):
        with patch("builtins.open", mock_open(read_data="invalid")):
             assert reset_helpers._load_store() == []

def test_load_store_valid():
    data = '[{"reset_ist": "2023-01-01T10:00:00+05:30"}]'
    with patch("os.path.exists", return_value=True):
        with patch("builtins.open", mock_open(read_data=data)):
            store = reset_helpers._load_store()
            assert len(store) == 1

def test_save_store_fail():
    with patch("builtins.open", side_effect=Exception):
        reset_helpers._save_store([]) # Should not raise

@patch("geminiai_cli.reset_helpers.add_reset_entry")
@patch("builtins.input", return_value="invalid")
def test_save_reset_time_from_output_ambiguous_invalid(mock_input, mock_add):
    assert not reset_helpers.save_reset_time_from_output("10:00")

@patch("geminiai_cli.reset_helpers.add_reset_entry", side_effect=Exception("Error"))
def test_save_reset_time_from_output_exception(mock_add):
    assert not reset_helpers.save_reset_time_from_output("10:00 AM")

@patch("geminiai_cli.reset_helpers.save_reset_time_from_output", return_value=True)
def test_do_capture_reset_success(mock_save):
    reset_helpers.do_capture_reset("text")

@patch("geminiai_cli.reset_helpers._load_and_cleanup_store", return_value=[])
def test_do_next_reset_no_entries(mock_load):
    reset_helpers.do_next_reset()

@patch("geminiai_cli.reset_helpers._load_and_cleanup_store")
def test_do_next_reset_found(mock_load):
    future = datetime.now(timezone(timedelta(hours=5, minutes=30))) + timedelta(hours=1)
    mock_load.return_value = [
        {"id": "1", "email": "t@t.com", "reset_ist": future.isoformat()}
    ]
    reset_helpers.do_next_reset("t@t.com") # Filter by email

@patch("geminiai_cli.reset_helpers._load_and_cleanup_store")
def test_do_next_reset_not_found(mock_load):
    mock_load.return_value = [
        {"id": "1", "email": "other@t.com", "reset_ist": datetime.now().isoformat()}
    ]
    reset_helpers.do_next_reset("t@t.com") # Filter by email

@patch("geminiai_cli.reset_helpers._load_and_cleanup_store")
@patch("geminiai_cli.reset_helpers.cleanup_expired")
def test_do_next_reset_expired_now(mock_cleanup, mock_load):
    past = datetime.now(timezone(timedelta(hours=5, minutes=30))) - timedelta(seconds=1)
    mock_load.return_value = [
        {"id": "1", "email": "t@t.com", "reset_ist": past.isoformat()}
    ]
    reset_helpers.do_next_reset()
    mock_cleanup.assert_called()

@patch("geminiai_cli.reset_helpers.save_reset_time_from_output", return_value=False)
def test_do_capture_reset_invalid(mock_save):
    reset_helpers.do_capture_reset("invalid")

@patch("sys.stdin.isatty", return_value=True)
@patch("builtins.input", side_effect=EOFError)
def test_do_capture_reset_no_input(mock_input, mock_isatty):
    reset_helpers.do_capture_reset("")

@patch("geminiai_cli.reset_helpers._load_store")
def test_load_and_cleanup_store(mock_load):
    mock_load.return_value = []
    assert reset_helpers._load_and_cleanup_store() == []

@patch("geminiai_cli.reset_helpers._load_store")
@patch("geminiai_cli.reset_helpers._save_store")
def test_cleanup_expired_malformed(mock_save, mock_load):
    mock_load.return_value = [{"reset_ist": "invalid"}]
    removed = reset_helpers.cleanup_expired()
    assert len(removed) == 1
