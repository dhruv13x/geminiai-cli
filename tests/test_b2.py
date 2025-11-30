# tests/test_b2.py

import pytest
from unittest.mock import patch, MagicMock
import sys
import io

# Mock b2sdk module
mock_b2sdk = MagicMock()
mock_b2_api_class = MagicMock()
mock_b2sdk.B2Api = mock_b2_api_class
mock_b2sdk.InMemoryAccountInfo = MagicMock()

with patch.dict(sys.modules, {"b2sdk.v2": mock_b2sdk}):
    from geminiai_cli.b2 import B2Manager

def test_b2_manager_init():
    mock_b2_api_class.return_value.get_bucket_by_name.return_value = MagicMock()
    b2 = B2Manager("id", "key", "bucket")
    assert b2.bucket is not None
    mock_b2_api_class.return_value.authorize_account.assert_called_with("production", "id", "key")

def test_b2_manager_init_fail():
    mock_b2_api_class.return_value.authorize_account.side_effect = Exception("Auth fail")
    with pytest.raises(SystemExit):
        B2Manager("id", "key", "bucket")
    mock_b2_api_class.return_value.authorize_account.side_effect = None

def test_b2_manager_upload():
    mock_bucket = MagicMock()
    mock_b2_api_class.return_value.get_bucket_by_name.return_value = mock_bucket
    b2 = B2Manager("id", "key", "bucket")

    b2.upload("local_file")
    mock_bucket.upload_local_file.assert_called()

def test_b2_manager_upload_fail():
    mock_bucket = MagicMock()
    mock_bucket.upload_local_file.side_effect = Exception("Upload fail")
    mock_b2_api_class.return_value.get_bucket_by_name.return_value = mock_bucket
    b2 = B2Manager("id", "key", "bucket")

    b2.upload("local_file") # Should handle exception and print error

def test_b2_manager_download():
    mock_bucket = MagicMock()
    mock_b2_api_class.return_value.get_bucket_by_name.return_value = mock_bucket
    b2 = B2Manager("id", "key", "bucket")

    b2.download("remote", "local")
    mock_bucket.download_file_by_name.assert_called()

def test_b2_manager_download_fail():
    mock_bucket = MagicMock()
    mock_bucket.download_file_by_name.side_effect = Exception("Download fail")
    mock_b2_api_class.return_value.get_bucket_by_name.return_value = mock_bucket
    b2 = B2Manager("id", "key", "bucket")

    with pytest.raises(SystemExit):
        b2.download("remote", "local")

def test_b2_manager_list_backups():
    mock_bucket = MagicMock()
    mock_b2_api_class.return_value.get_bucket_by_name.return_value = mock_bucket
    b2 = B2Manager("id", "key", "bucket")

    b2.list_backups()
    mock_bucket.ls.assert_called()

# Test import error handling
def test_b2_import_error():
    # We want to test the code path where B2Api is None
    # We can mock the module attribute directly on the already imported module
    from geminiai_cli import b2
    original_b2api = b2.B2Api

    try:
        b2.B2Api = None
        with pytest.raises(SystemExit):
            b2.B2Manager("id", "key", "bucket")
    finally:
        b2.B2Api = original_b2api

def test_b2_manager_upload_with_name():
    mock_bucket = MagicMock()
    mock_b2_api_class.return_value.get_bucket_by_name.return_value = mock_bucket
    b2 = B2Manager("id", "key", "bucket")

    b2.upload("local_file", remote_name="remote_file")
    mock_bucket.upload_local_file.assert_called_with(local_file="local_file", file_name="remote_file")

def test_b2_manager_upload_string_success():
    mock_bucket = MagicMock()
    mock_b2_api_class.return_value.get_bucket_by_name.return_value = mock_bucket
    b2 = B2Manager("id", "key", "bucket")

    data = "some data"
    b2.upload_string(data, "remote_file")

    mock_bucket.upload_bytes.assert_called_with(
        data_bytes=data.encode('utf-8'),
        file_name="remote_file"
    )

def test_b2_manager_upload_string_fail():
    mock_bucket = MagicMock()
    mock_bucket.upload_bytes.side_effect = Exception("Upload bytes fail")
    mock_b2_api_class.return_value.get_bucket_by_name.return_value = mock_bucket
    b2 = B2Manager("id", "key", "bucket")

    with pytest.raises(Exception):
        b2.upload_string("data", "remote_file")

def test_b2_manager_download_to_string_success():
    mock_bucket = MagicMock()
    mock_download_dest = MagicMock()

    # Mock save behavior to write to the BytesIO buffer passed to it
    def side_effect_save(file_obj):
        file_obj.write(b"remote content")

    mock_download_dest.save.side_effect = side_effect_save
    mock_bucket.download_file_by_name.return_value = mock_download_dest

    mock_b2_api_class.return_value.get_bucket_by_name.return_value = mock_bucket
    b2 = B2Manager("id", "key", "bucket")

    result = b2.download_to_string("remote_file")
    assert result == "remote content"
    mock_bucket.download_file_by_name.assert_called_with("remote_file")

def test_b2_manager_download_to_string_fail():
    mock_bucket = MagicMock()
    mock_bucket.download_file_by_name.side_effect = Exception("Not found")
    mock_b2_api_class.return_value.get_bucket_by_name.return_value = mock_bucket
    b2 = B2Manager("id", "key", "bucket")

    result = b2.download_to_string("remote_file")
    assert result is None
