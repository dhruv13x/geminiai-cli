
import json
import os
import datetime
import pytest
from unittest.mock import MagicMock, patch, mock_open
from geminiai_cli import cooldown
from geminiai_cli.cooldown import (
    _sync_cooldown_file,
    get_cooldown_data,
    record_switch,
    do_cooldown_list,
    COOLDOWN_FILE_PATH,
    CLOUD_COOLDOWN_FILENAME,
)
from rich.table import Table

# Constants for testing
TEST_EMAIL = "test@example.com"
TEST_TIMESTAMP = "2023-10-27T10:00:00+00:00"
MOCK_HOME = "/home/testuser"
MOCK_COOLDOWN_PATH = os.path.join(MOCK_HOME, ".gemini-cooldown.json")


@pytest.fixture
def mock_args():
    args = MagicMock()
    args.cloud = True
    return args


@pytest.fixture
def mock_b2_manager(mocker):
    return mocker.patch("geminiai_cli.cooldown.B2Manager")


@pytest.fixture
def mock_resolve_credentials(mocker):
    return mocker.patch("geminiai_cli.cooldown.resolve_credentials")


@pytest.fixture
def mock_cprint(mocker):
    return mocker.patch("geminiai_cli.cooldown.cprint")

@pytest.fixture
def mock_console(mocker):
    return mocker.patch("geminiai_cli.cooldown.console")

@pytest.fixture
def mock_fs(fs):
    """
    Using pyfakefs to mock the file system.
    """
    fs.create_dir(MOCK_HOME)
    return fs


@pytest.fixture(autouse=True)
def patch_env(monkeypatch):
    # Patch the COOLDOWN_FILE_PATH in the module to point to our mock path
    monkeypatch.setattr("geminiai_cli.cooldown.COOLDOWN_FILE_PATH", MOCK_COOLDOWN_PATH)


def test_sync_cooldown_file_no_creds(mock_resolve_credentials, mock_cprint, mock_args):
    mock_resolve_credentials.return_value = (None, None, None)
    _sync_cooldown_file("upload", mock_args)
    mock_cprint.assert_any_call(cooldown.NEON_YELLOW, "Warning: Cloud credentials not fully configured. Skipping cloud sync.")


def test_sync_cooldown_file_download_success(mock_resolve_credentials, mock_b2_manager, mock_cprint, mock_args):
    mock_resolve_credentials.return_value = ("key", "app", "bucket")
    b2_instance = mock_b2_manager.return_value

    _sync_cooldown_file("download", mock_args)

    b2_instance.download.assert_called_once()
    mock_cprint.assert_any_call(cooldown.NEON_GREEN, "Cooldown file synced from cloud.")


def test_sync_cooldown_file_download_fail_not_found(mock_resolve_credentials, mock_b2_manager, mock_cprint, mock_args):
    mock_resolve_credentials.return_value = ("key", "app", "bucket")
    b2_instance = mock_b2_manager.return_value
    b2_instance.download.side_effect = Exception("file_not_present")

    _sync_cooldown_file("download", mock_args)

    mock_cprint.assert_any_call(cooldown.NEON_YELLOW, "No cooldown file found in the cloud. Using local version.")


def test_sync_cooldown_file_download_fail_other(mock_resolve_credentials, mock_b2_manager, mock_cprint, mock_args):
    mock_resolve_credentials.return_value = ("key", "app", "bucket")
    b2_instance = mock_b2_manager.return_value
    b2_instance.download.side_effect = Exception("Network error")

    _sync_cooldown_file("download", mock_args)

    # Check that error message is printed
    args, _ = mock_cprint.call_args_list[-1]
    assert args[0] == cooldown.NEON_RED
    assert "Error downloading cooldown file" in args[1]


def test_sync_cooldown_file_upload_no_local_file(mock_resolve_credentials, mock_b2_manager, mock_cprint, mock_args, fs):
    mock_resolve_credentials.return_value = ("key", "app", "bucket")
    # Ensure file does not exist
    if os.path.exists(MOCK_COOLDOWN_PATH):
        os.remove(MOCK_COOLDOWN_PATH)

    _sync_cooldown_file("upload", mock_args)

    mock_cprint.assert_any_call(cooldown.NEON_YELLOW, "Local cooldown file not found. Skipping upload.")
    mock_b2_manager.return_value.upload.assert_not_called()


def test_sync_cooldown_file_upload_success(mock_resolve_credentials, mock_b2_manager, mock_cprint, mock_args, fs):
    mock_resolve_credentials.return_value = ("key", "app", "bucket")
    fs.create_file(MOCK_COOLDOWN_PATH, contents="{}")

    _sync_cooldown_file("upload", mock_args)

    mock_b2_manager.return_value.upload.assert_called_once()
    mock_cprint.assert_any_call(cooldown.NEON_GREEN, "Cooldown file synced to cloud.")


def test_sync_cooldown_file_upload_fail(mock_resolve_credentials, mock_b2_manager, mock_cprint, mock_args, fs):
    mock_resolve_credentials.return_value = ("key", "app", "bucket")
    fs.create_file(MOCK_COOLDOWN_PATH, contents="{}")
    mock_b2_manager.return_value.upload.side_effect = Exception("Upload fail")

    _sync_cooldown_file("upload", mock_args)

    args, _ = mock_cprint.call_args_list[-1]
    assert args[0] == cooldown.NEON_RED
    assert "Error uploading cooldown file" in args[1]


def test_sync_cooldown_file_unexpected_exception(mock_resolve_credentials, mock_cprint, mock_args):
    mock_resolve_credentials.side_effect = Exception("Unexpected")

    _sync_cooldown_file("upload", mock_args)

    args, _ = mock_cprint.call_args_list[-1]
    assert args[0] == cooldown.NEON_RED
    assert "An unexpected error occurred" in args[1]


def test_get_cooldown_data_no_file(fs):
    # fs is empty (except what mock_fs created)
    # Ensure file doesn't exist
    if os.path.exists(MOCK_COOLDOWN_PATH):
        os.remove(MOCK_COOLDOWN_PATH)
    assert get_cooldown_data() == {}


def test_get_cooldown_data_valid_file(fs):
    data = {TEST_EMAIL: TEST_TIMESTAMP}
    fs.create_file(MOCK_COOLDOWN_PATH, contents=json.dumps(data))
    assert get_cooldown_data() == data


def test_get_cooldown_data_invalid_json(fs):
    fs.create_file(MOCK_COOLDOWN_PATH, contents="invalid json")
    assert get_cooldown_data() == {}


def test_record_switch_no_email():
    record_switch(None)
    # Should just return


def test_record_switch_local_only(fs, mocker):
    mock_datetime = mocker.patch("geminiai_cli.cooldown.datetime")
    mock_datetime.datetime.now.return_value.isoformat.return_value = TEST_TIMESTAMP
    mock_datetime.timezone.utc = datetime.timezone.utc

    record_switch(TEST_EMAIL)

    with open(MOCK_COOLDOWN_PATH, "r") as f:
        data = json.load(f)
    assert data[TEST_EMAIL] == TEST_TIMESTAMP


def test_record_switch_with_cloud(mock_fs, fs, mocker, mock_args, mock_resolve_credentials, mock_b2_manager):
    mock_resolve_credentials.return_value = ("key", "app", "bucket")
    mock_datetime = mocker.patch("geminiai_cli.cooldown.datetime")
    mock_datetime.datetime.now.return_value.isoformat.return_value = TEST_TIMESTAMP
    mock_datetime.timezone.utc = datetime.timezone.utc

    # Mock download to populate local file with some existing data
    def side_effect_download(remote, local):
        # We need to write to the local file in the fake fs
        with open(local, "w") as f:
            json.dump({"other@example.com": "2020-01-01T00:00:00+00:00"}, f)

    mock_b2_manager.return_value.download.side_effect = side_effect_download

    record_switch(TEST_EMAIL, args=mock_args)

    # Verify download called
    mock_b2_manager.return_value.download.assert_called_once()

    # Verify local file updated with BOTH
    with open(MOCK_COOLDOWN_PATH, "r") as f:
        data = json.load(f)
    assert data[TEST_EMAIL] == TEST_TIMESTAMP
    assert "other@example.com" in data

    # Verify upload called
    mock_b2_manager.return_value.upload.assert_called_once()


def test_record_switch_write_fail(fs, mocker, mock_cprint):
    mock_datetime = mocker.patch("geminiai_cli.cooldown.datetime")
    mock_datetime.datetime.now.return_value.isoformat.return_value = TEST_TIMESTAMP
    mock_datetime.timezone.utc = datetime.timezone.utc

    # Simulate IOError during write
    if os.path.exists(MOCK_COOLDOWN_PATH):
        os.remove(MOCK_COOLDOWN_PATH)
    fs.create_dir(MOCK_COOLDOWN_PATH)

    record_switch(TEST_EMAIL)

    args, _ = mock_cprint.call_args_list[-1]
    assert args[0] == cooldown.NEON_RED
    assert "Error: Could not write" in args[1]


def test_do_cooldown_list_no_data(fs, mock_cprint):
    if os.path.exists(MOCK_COOLDOWN_PATH):
        os.remove(MOCK_COOLDOWN_PATH)
    do_cooldown_list()
    mock_cprint.assert_any_call(cooldown.NEON_YELLOW, "No account data found (switches or resets).")


def test_do_cooldown_list_with_cloud(fs, mock_args, mock_resolve_credentials, mock_b2_manager):
    mock_resolve_credentials.return_value = ("key", "app", "bucket")

    do_cooldown_list(args=mock_args)

    mock_b2_manager.return_value.download.assert_called_once()


def _get_printed_table(mock_console):
    """Helper to extract the Rich Table from mock_console calls."""
    for call in mock_console.print.call_args_list:
        if call.args and isinstance(call.args[0], Table):
            return call.args[0]
    return None

def _get_table_rows(table):
    """Extract rows from a Rich Table."""
    # Table stores data in columns.
    # We can reconstruct rows by iterating over columns and taking the i-th element.

    # table.columns is a list of Column objects.
    # Each Column object has ._cells which is a list.

    col_cells = [list(col.cells) for col in table.columns]
    # col_cells is [[col1_row1, col1_row2], [col2_row1, col2_row2], ...]

    # Transpose to get rows
    # zip(*col_cells)

    return list(zip(*col_cells))


def test_do_cooldown_list_ready(fs, mock_console, mocker):
    # Set time so that > 24h has passed
    past_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=25)
    data = {TEST_EMAIL: past_time.isoformat()}
    fs.create_file(MOCK_COOLDOWN_PATH, contents=json.dumps(data))

    do_cooldown_list()

    table = _get_printed_table(mock_console)
    assert table is not None

    rows = _get_table_rows(table)

    found_email = False
    found_status = False
    for row in rows:
        # row is a tuple of cells
        if TEST_EMAIL in str(row[0]):
            found_email = True
            if "READY" in str(row[1]):
                found_status = True

    assert found_email, "Email not found in table"
    assert found_status, "Status READY not found in table"


def test_do_cooldown_list_active(fs, mock_console, mocker):
    # Set time so that < 24h has passed (e.g., 1 hour ago)
    past_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=1)
    data = {TEST_EMAIL: past_time.isoformat()}
    fs.create_file(MOCK_COOLDOWN_PATH, contents=json.dumps(data))

    do_cooldown_list()

    table = _get_printed_table(mock_console)
    assert table is not None

    rows = _get_table_rows(table)

    found_email = False
    found_status = False
    for row in rows:
        if TEST_EMAIL in str(row[0]):
            found_email = True
            if "COOLDOWN" in str(row[1]):
                found_status = True

    assert found_email
    assert found_status


def test_do_cooldown_list_invalid_timestamp(fs, mock_console):
    data = {TEST_EMAIL: "invalid-timestamp"}
    fs.create_file(MOCK_COOLDOWN_PATH, contents=json.dumps(data))

    do_cooldown_list()

    table = _get_printed_table(mock_console)
    assert table is not None

    rows = _get_table_rows(table)

    found_email = False
    found_invalid = False
    for row in rows:
        if TEST_EMAIL in str(row[0]):
            found_email = True
            # Column 3 is Last Used
            if "Invalid TS" in str(row[3]):
                found_invalid = True

    assert found_email
    assert found_invalid


def test_do_cooldown_list_naive_timestamp_fix(fs, mock_console, mocker):
    naive_time = datetime.datetime.now() # Naive
    data = {TEST_EMAIL: naive_time.isoformat()}
    fs.create_file(MOCK_COOLDOWN_PATH, contents=json.dumps(data))

    do_cooldown_list()

    table = _get_printed_table(mock_console)
    assert table is not None

    # Just verify it rendered
    found_email = False
    rows = _get_table_rows(table)
    for row in rows:
        if TEST_EMAIL in str(row[0]):
            found_email = True

    assert found_email
