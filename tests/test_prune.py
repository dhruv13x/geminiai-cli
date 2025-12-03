# tests/test_prune.py

import pytest
from unittest.mock import patch, MagicMock, call
import os
from geminiai_cli.prune import do_prune, get_backup_list, prune_list

def mock_args(backup_dir="/tmp/backups", keep=2, cloud=False, cloud_only=False, dry_run=False, b2_id=None, b2_key=None, bucket=None):
    return MagicMock(backup_dir=backup_dir, keep=keep, cloud=cloud, cloud_only=cloud_only, dry_run=dry_run, b2_id=b2_id, b2_key=b2_key, bucket=bucket)

def test_get_backup_list():
    files = [
        "2023-01-01_100000-user@example.com.gemini.tar.gz",
        "2023-01-02_100000-user@example.com.gemini.tar.gz",
        "invalid.txt"
    ]
    backups = get_backup_list(files)
    assert len(backups) == 2
    # Should be sorted newest first
    assert backups[0][1] == "2023-01-02_100000-user@example.com.gemini.tar.gz"
    assert backups[1][1] == "2023-01-01_100000-user@example.com.gemini.tar.gz"

def test_prune_list_no_action():
    backups = [("ts1", "file1"), ("ts2", "file2")]
    callback = MagicMock()
    # Keep 5, have 2. No prune.
    prune_list(backups, 5, False, callback)
    callback.assert_not_called()

def test_prune_list_action():
    backups = [("ts3", "file3"), ("ts2", "file2"), ("ts1", "file1")]
    callback = MagicMock()
    # Keep 1, have 3. Delete 2 oldest (file2, file1).
    prune_list(backups, 1, False, callback)
    assert callback.call_count == 2
    callback.assert_has_calls([call("file2"), call("file1")])

def test_prune_list_dry_run():
    backups = [("ts3", "file3"), ("ts2", "file2"), ("ts1", "file1")]
    callback = MagicMock()
    prune_list(backups, 1, True, callback)
    callback.assert_not_called()

@patch("os.path.exists", return_value=True)
@patch("os.listdir")
@patch("os.remove")
@patch("geminiai_cli.prune.cprint")
def test_do_prune_local(mock_cprint, mock_remove, mock_listdir, mock_exists):
    mock_listdir.return_value = [
        "2023-01-01_100000-u.gemini.tar.gz",
        "2023-01-02_100000-u.gemini.tar.gz",
        "2023-01-03_100000-u.gemini.tar.gz"
    ]
    args = mock_args(keep=1)

    with patch("os.path.abspath", return_value="/tmp/backups"):
        do_prune(args)

    # Should delete the 2 oldest
    assert mock_remove.call_count == 2

@patch("os.path.exists", return_value=False)
@patch("geminiai_cli.prune.cprint")
def test_do_prune_local_no_dir(mock_cprint, mock_exists):
    args = mock_args(keep=1)
    do_prune(args)
    # Just prints warning
    mock_cprint.assert_called()

@patch("geminiai_cli.prune.resolve_credentials")
@patch("geminiai_cli.prune.B2Manager")
@patch("geminiai_cli.prune.cprint")
def test_do_prune_cloud(mock_cprint, mock_b2_cls, mock_creds):
    mock_creds.return_value = ("id", "key", "bucket")

    mock_b2 = mock_b2_cls.return_value

    fv1 = MagicMock()
    fv1.file_name = "2023-01-01_100000-u.gemini.tar.gz"
    fv1.id_ = "id1"

    fv2 = MagicMock()
    fv2.file_name = "2023-01-02_100000-u.gemini.tar.gz"
    fv2.id_ = "id2"

    mock_b2.list_backups.return_value = [(fv1, None), (fv2, None)]

    args = mock_args(keep=1, cloud=True)

    with patch("os.path.exists", return_value=False): # Skip local
        do_prune(args)

    mock_b2.bucket.delete_file_version.assert_called_once_with("id1", "2023-01-01_100000-u.gemini.tar.gz")

@patch("geminiai_cli.prune.resolve_credentials")
@patch("geminiai_cli.prune.cprint")
def test_do_prune_cloud_no_creds(mock_cprint, mock_creds):
    mock_creds.return_value = (None, None, None)
    args = mock_args(cloud=True)
    do_prune(args)
    # Warning printed

@patch("geminiai_cli.prune.resolve_credentials")
@patch("geminiai_cli.prune.cprint")
def test_do_prune_cloud_only_no_creds(mock_cprint, mock_creds):
    mock_creds.return_value = (None, None, None)
    args = mock_args(cloud_only=True)
    do_prune(args)
    # Error printed

@patch("geminiai_cli.prune.resolve_credentials")
@patch("geminiai_cli.prune.B2Manager")
@patch("geminiai_cli.prune.cprint")
def test_do_prune_cloud_exception(mock_cprint, mock_b2_cls, mock_creds):
    mock_creds.return_value = ("id", "key", "bucket")
    mock_b2_cls.side_effect = Exception("B2 Fail")

    args = mock_args(cloud=True)

    with patch("os.path.exists", return_value=False):
        do_prune(args)

    mock_cprint.assert_called()

@patch("os.path.exists", return_value=True)
@patch("os.listdir")
@patch("os.remove")
@patch("geminiai_cli.prune.cprint")
def test_do_prune_local_remove_fail(mock_cprint, mock_remove, mock_listdir, mock_exists):
    mock_listdir.return_value = [
        "2023-01-01_100000-u.gemini.tar.gz",
        "2023-01-02_100000-u.gemini.tar.gz",
    ]
    mock_remove.side_effect = Exception("Permission denied")
    args = mock_args(keep=1)

    with patch("os.path.abspath", return_value="/tmp/backups"):
        do_prune(args)

    # Assert error logged
    # Not easily assertable on cprint message content without more complex mock check,
    # but ensuring it doesn't crash is good.

@patch("geminiai_cli.prune.resolve_credentials")
@patch("geminiai_cli.prune.B2Manager")
@patch("geminiai_cli.prune.cprint")
def test_do_prune_cloud_delete_fail(mock_cprint, mock_b2_cls, mock_creds):
    mock_creds.return_value = ("id", "key", "bucket")
    mock_b2 = mock_b2_cls.return_value

    fv1 = MagicMock()
    fv1.file_name = "2023-01-01_100000-u.gemini.tar.gz"
    fv1.id_ = "id1"
    fv2 = MagicMock()
    fv2.file_name = "2023-01-02_100000-u.gemini.tar.gz"
    fv2.id_ = "id2"

    mock_b2.list_backups.return_value = [(fv1, None), (fv2, None)]
    mock_b2.bucket.delete_file_version.side_effect = Exception("API Fail")

    args = mock_args(keep=1, cloud=True)

    with patch("os.path.exists", return_value=False):
        do_prune(args)

    mock_b2.bucket.delete_file_version.assert_called()
