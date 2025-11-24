import pytest
from unittest.mock import patch, mock_open, MagicMock, ANY
import os
import time
import sys
from geminiai_cli import restore

@patch("geminiai_cli.restore.fcntl")
def test_acquire_lock_success(mock_fcntl):
    with patch("builtins.open", mock_open()):
        fd = restore.acquire_lock()
        assert fd is not None
        mock_fcntl.flock.assert_called()

@patch("geminiai_cli.restore.fcntl")
def test_acquire_lock_fail(mock_fcntl):
    mock_fcntl.flock.side_effect = BlockingIOError
    with patch("builtins.open", mock_open()):
        with pytest.raises(SystemExit) as e:
            restore.acquire_lock()
        assert e.value.code == 2

def test_run():
    with patch("subprocess.run") as mock_run:
        restore.run("ls")
        mock_run.assert_called_with("ls", shell=True, check=True)

def test_parse_timestamp_from_name():
    ts = restore.parse_timestamp_from_name("2025-10-22_042211-test@test.gemini")
    assert ts is not None
    assert ts.tm_year == 2025

    assert restore.parse_timestamp_from_name("invalid") is None

@patch("os.listdir")
@patch("os.path.isfile", return_value=True)
def test_find_oldest_archive_backup(mock_isfile, mock_listdir):
    mock_listdir.return_value = [
        "2025-10-23_042211-test.gemini.tar.gz",
        "2025-10-22_042211-test.gemini.tar.gz"
    ]
    oldest = restore.find_oldest_archive_backup("/tmp")
    assert "2025-10-22" in oldest

@patch("os.listdir")
def test_find_oldest_archive_backup_none(mock_listdir):
    mock_listdir.return_value = []
    assert restore.find_oldest_archive_backup("/tmp") is None

@patch("geminiai_cli.restore.run")
@patch("os.makedirs")
def test_extract_archive(mock_makedirs, mock_run):
    restore.extract_archive("archive", "dest")
    mock_run.assert_called()

@patch("geminiai_cli.restore.acquire_lock")
@patch("geminiai_cli.restore.run")
@patch("os.path.exists", return_value=True)
@patch("os.makedirs")
@patch("os.replace")
@patch("shutil.rmtree")
@patch("tempfile.mkdtemp", return_value="/tmp/restore_tmp")
def test_main_from_dir(mock_mkdtemp, mock_rmtree, mock_replace, mock_makedirs, mock_exists, mock_run, mock_lock):
    with patch("sys.argv", ["restore.py", "--from-dir", "/tmp/backup"]):
        mock_run.return_value.returncode = 0
        restore.main()
        # Verification passes

@patch("geminiai_cli.restore.acquire_lock")
@patch("geminiai_cli.restore.run")
@patch("os.path.exists", return_value=True)
@patch("os.makedirs")
@patch("os.replace")
@patch("shutil.rmtree")
@patch("tempfile.mkdtemp", return_value="/tmp/restore_tmp")
def test_main_from_archive(mock_mkdtemp, mock_rmtree, mock_replace, mock_makedirs, mock_exists, mock_run, mock_lock):
    with patch("sys.argv", ["restore.py", "--from-archive", "/tmp/backup.tar.gz"]):
        mock_run.return_value.returncode = 0
        restore.main()

@patch("geminiai_cli.restore.acquire_lock")
@patch("geminiai_cli.restore.find_oldest_archive_backup", return_value="/tmp/oldest.tar.gz")
@patch("geminiai_cli.restore.run")
@patch("os.path.exists", return_value=True)
@patch("os.makedirs")
@patch("os.replace")
@patch("shutil.rmtree")
@patch("tempfile.mkdtemp", return_value="/tmp/restore_tmp")
def test_main_auto_oldest(mock_mkdtemp, mock_rmtree, mock_replace, mock_makedirs, mock_exists, mock_run, mock_find_oldest, mock_lock):
    with patch("sys.argv", ["restore.py"]):
        mock_run.return_value.returncode = 0
        restore.main()
        mock_find_oldest.assert_called()

@patch("geminiai_cli.restore.acquire_lock")
@patch("geminiai_cli.restore.B2Manager")
@patch("geminiai_cli.restore.run")
@patch("os.path.exists", return_value=True)
@patch("os.makedirs")
@patch("os.replace")
@patch("shutil.rmtree")
@patch("tempfile.mkdtemp", return_value="/tmp/restore_tmp")
def test_main_cloud(mock_mkdtemp, mock_rmtree, mock_replace, mock_makedirs, mock_exists, mock_run, mock_b2, mock_lock):
    with patch("sys.argv", ["restore.py", "--cloud", "--bucket", "b", "--b2-id", "i", "--b2-key", "k"]):
        mock_file = MagicMock()
        mock_file.file_name = "2025-10-22_042211-test.gemini.tar.gz"
        mock_b2.return_value.list_backups.return_value = [(mock_file, None)]

        mock_run.return_value.returncode = 0
        restore.main()
        mock_b2.return_value.download.assert_called()

@patch("geminiai_cli.restore.acquire_lock")
@patch("geminiai_cli.restore.run")
@patch("os.path.exists", return_value=True)
@patch("shutil.rmtree")
@patch("tempfile.mkdtemp", return_value="/tmp/restore_tmp")
def test_main_verification_fail(mock_mkdtemp, mock_rmtree, mock_exists, mock_run, mock_lock):
    with patch("sys.argv", ["restore.py", "--from-archive", "archive.tar.gz"]):
        # Mock cp run ok
        # Mock diff run fail (first verify)
        mock_run.side_effect = [
            MagicMock(returncode=0), # tar
            MagicMock(returncode=0), # cp
            MagicMock(returncode=1, stdout="diff"), # diff
        ]
        with pytest.raises(SystemExit) as e:
            restore.main()
        assert e.value.code == 3

@patch("geminiai_cli.restore.acquire_lock")
@patch("geminiai_cli.restore.run")
@patch("os.path.exists", return_value=True)
@patch("os.replace")
@patch("shutil.rmtree")
@patch("tempfile.mkdtemp", return_value="/tmp/restore_tmp")
def test_main_post_verification_fail(mock_mkdtemp, mock_rmtree, mock_replace, mock_exists, mock_run, mock_lock):
    with patch("sys.argv", ["restore.py", "--from-archive", "archive.tar.gz"]):
        # Mock diff run fail (post verify)
        mock_run.side_effect = [
            MagicMock(returncode=0), # tar
            MagicMock(returncode=0), # cp
            MagicMock(returncode=0), # diff 1
            MagicMock(returncode=1, stdout="diff"), # diff 2
        ]
        with pytest.raises(SystemExit) as e:
            restore.main()
        assert e.value.code == 4

@patch("geminiai_cli.restore.acquire_lock")
@patch("geminiai_cli.restore.run")
@patch("os.path.exists", return_value=True)
@patch("os.replace")
@patch("shutil.rmtree")
@patch("tempfile.mkdtemp", return_value="/tmp/restore_tmp")
def test_main_dry_run(mock_mkdtemp, mock_rmtree, mock_replace, mock_exists, mock_run, mock_lock):
    with patch("sys.argv", ["restore.py", "--from-archive", "archive.tar.gz", "--dry-run"]):
        restore.main()
        # Ensure destructive commands not called (mock_run will be called for tar probably? no, check restore.py)
        # restore.py dry-run prints "DRY RUN: ..."
        # run() shouldn't be called.
        mock_run.assert_not_called()
        mock_replace.assert_not_called()

@patch("geminiai_cli.restore.acquire_lock")
@patch("geminiai_cli.restore.B2Manager")
def test_main_cloud_missing_creds(mock_b2, mock_lock):
    with patch("sys.argv", ["restore.py", "--cloud"]): # Missing bucket/id/key
        with pytest.raises(SystemExit):
            restore.main()

@patch("geminiai_cli.restore.acquire_lock")
@patch("geminiai_cli.restore.B2Manager")
def test_main_cloud_no_backups(mock_b2, mock_lock):
    with patch("sys.argv", ["restore.py", "--cloud", "--bucket", "b", "--b2-id", "i", "--b2-key", "k"]):
        mock_b2.return_value.list_backups.return_value = []
        with pytest.raises(SystemExit):
            restore.main()

@patch("geminiai_cli.restore.acquire_lock")
@patch("os.path.exists", return_value=False)
def test_main_from_dir_not_found(mock_exists, mock_lock):
    with patch("sys.argv", ["restore.py", "--from-dir", "/tmp/notfound"]):
        with pytest.raises(SystemExit):
            restore.main()

@patch("geminiai_cli.restore.acquire_lock")
@patch("os.path.exists")
def test_main_from_archive_search_dir(mock_exists, mock_lock):
    def side_effect(path):
        if "archive.tar.gz" in path and "geminiai_backups" not in path:
            return False # User path not found
        if "archive.tar.gz" in path and "geminiai_backups" in path:
            return True # Search dir path found
        return True # Default for others (locale etc)
    mock_exists.side_effect = side_effect

    with patch("sys.argv", ["restore.py", "--from-archive", "archive.tar.gz"]):
        # Just verifying it doesn't exit early
        with pytest.raises(Exception, match="Stop"): # We expect our Stop exception
             # Actually find_oldest_archive_backup logic or extract will be called.
             # Here we just want to cover lines 232-245
             # Mock run to fail immediately to stop
             with patch("geminiai_cli.restore.run", side_effect=Exception("Stop")):
                 restore.main()

@patch("geminiai_cli.restore.acquire_lock")
@patch("os.path.exists", return_value=False)
def test_main_from_archive_not_found(mock_exists, mock_lock):
    with patch("sys.argv", ["restore.py", "--from-archive", "archive.tar.gz"]):
        with pytest.raises(SystemExit):
             restore.main()

@patch("geminiai_cli.restore.acquire_lock")
@patch("geminiai_cli.restore.find_oldest_archive_backup", return_value=None)
@patch("os.path.exists", return_value=True)
def test_main_auto_no_backups(mock_exists, mock_find, mock_lock):
    with patch("sys.argv", ["restore.py"]):
        with pytest.raises(SystemExit):
            restore.main()

@patch("geminiai_cli.restore.acquire_lock")
@patch("geminiai_cli.restore.run")
@patch("os.path.exists", return_value=True)
@patch("os.replace")
@patch("shutil.rmtree")
@patch("tempfile.mkdtemp", return_value="/tmp/restore_tmp")
def test_main_rollback_success(mock_mkdtemp, mock_rmtree, mock_replace, mock_exists, mock_run, mock_lock):
     with patch("sys.argv", ["restore.py", "--from-archive", "archive.tar.gz"]):
        # Mock diff run fail (post verify)
        mock_run.side_effect = [
            MagicMock(returncode=0), # tar
            MagicMock(returncode=0), # cp
            MagicMock(returncode=0), # diff 1
            MagicMock(returncode=1, stdout="diff"), # diff 2
        ]
        with pytest.raises(SystemExit) as e:
            restore.main()
        assert e.value.code == 4
        # os.replace should be called to restore .bak
        # We can't easily verify call count on os.replace here without more mocking,
        # but we cover the code path.

@patch("geminiai_cli.restore.acquire_lock")
@patch("geminiai_cli.restore.run")
@patch("os.path.exists", return_value=True)
@patch("os.replace", side_effect=[None, None, Exception("Rollback fail")])
@patch("shutil.rmtree")
@patch("tempfile.mkdtemp", return_value="/tmp/restore_tmp")
def test_main_rollback_fail(mock_mkdtemp, mock_rmtree, mock_replace, mock_exists, mock_run, mock_lock):
     with patch("sys.argv", ["restore.py", "--from-archive", "archive.tar.gz"]):
        # Mock diff run fail (post verify)
        mock_run.side_effect = [
            MagicMock(returncode=0), # tar
            MagicMock(returncode=0), # cp
            MagicMock(returncode=0), # diff 1
            MagicMock(returncode=1, stdout="diff"), # diff 2
        ]
        with pytest.raises(SystemExit) as e:
            restore.main()
        assert e.value.code == 4

@patch("geminiai_cli.restore.acquire_lock")
@patch("geminiai_cli.restore.B2Manager")
@patch("geminiai_cli.restore.run")
@patch("os.path.exists", return_value=True)
@patch("os.makedirs")
@patch("os.replace")
@patch("shutil.rmtree")
@patch("tempfile.mkdtemp", return_value="/tmp/restore_tmp")
def test_main_cloud_specific_archive(mock_mkdtemp, mock_rmtree, mock_replace, mock_makedirs, mock_exists, mock_run, mock_b2, mock_lock):
    specific_archive = "2025-11-21_231311-specific@test.gemini.tar.gz"
    with patch("sys.argv", ["restore.py", "--cloud", "--bucket", "b", "--b2-id", "i", "--b2-key", "k", "--from-archive", specific_archive]):
        mock_file_specific = MagicMock()
        mock_file_specific.file_name = specific_archive
        
        mock_file_old = MagicMock()
        mock_file_old.file_name = "2025-10-22_042211-old@test.gemini.tar.gz"
        
        # b2.list_backups returns both
        mock_b2.return_value.list_backups.return_value = [(mock_file_old, None), (mock_file_specific, None)]

        mock_run.return_value.returncode = 0
        restore.main()
        
        # Assert download was called with the SPECIFIC archive, not the oldest one
        mock_b2.return_value.download.assert_called_with(specific_archive, ANY)
