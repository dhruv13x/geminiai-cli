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
        with pytest.raises(SystemExit):
            main()
        mock_banner.assert_called_once()

@patch("geminiai_cli.cli.backup_main")
def test_main_backup(mock_backup_main):
    with patch("sys.argv", ["geminiai", "backup"]):
        main()
        mock_backup_main.assert_called_once()

@patch("geminiai_cli.cli.restore_main")
def test_main_restore(mock_restore_main):
    with patch("sys.argv", ["geminiai", "restore"]):
        main()
        mock_restore_main.assert_called_once()

@patch("geminiai_cli.cli.integrity_main")
def test_main_integrity(mock_integrity_main):
    with patch("sys.argv", ["geminiai", "check-integrity"]):
        main()
        mock_integrity_main.assert_called_once()

@patch("geminiai_cli.cli.list_backups_main")
def test_main_list_backups(mock_list_backups_main):
    with patch("sys.argv", ["geminiai", "list-backups"]):
        main()
        mock_list_backups_main.assert_called_once()

@patch("geminiai_cli.cli.check_b2_main")
def test_main_check_b2(mock_check_b2_main):
    with patch("sys.argv", ["geminiai", "check-b2"]):
        main()
        mock_check_b2_main.assert_called_once()

@patch("geminiai_cli.cli.do_list_resets")
def test_main_list(mock_list):
    with patch("sys.argv", ["geminiai", "--list"]):
        main()
        mock_list.assert_called_once()

@patch("geminiai_cli.cli.remove_entry_by_id")
def test_main_remove(mock_remove):
    mock_remove.return_value = True
    with patch("sys.argv", ["geminiai", "--remove", "id"]):
        main()
        mock_remove.assert_called_once_with("id")

@patch("geminiai_cli.cli.remove_entry_by_id")
def test_main_remove_fail(mock_remove):
    mock_remove.return_value = False
    with patch("sys.argv", ["geminiai", "--remove", "id"]):
        main()
        mock_remove.assert_called_once_with("id")

@patch("geminiai_cli.cli.do_next_reset")
def test_main_next(mock_next):
    with patch("sys.argv", ["geminiai", "--next"]):
        main()
        mock_next.assert_called_once_with(None)

@patch("geminiai_cli.cli.do_next_reset")
def test_main_next_arg(mock_next):
    with patch("sys.argv", ["geminiai", "--next", "id"]):
        main()
        mock_next.assert_called_once_with("id")

@patch("geminiai_cli.cli.do_capture_reset")
def test_main_add(mock_add):
    with patch("sys.argv", ["geminiai", "--add", "time"]):
        main()
        mock_add.assert_called_once_with("time")
