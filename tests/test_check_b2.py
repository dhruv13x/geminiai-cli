import pytest
from unittest.mock import patch, MagicMock
import sys
from geminiai_cli import check_b2

@patch("geminiai_cli.check_b2.B2Manager")
def test_main_success(mock_b2):
    with patch("sys.argv", ["check_b2.py", "--b2-id", "i", "--b2-key", "k", "--bucket", "b"]):
        check_b2.main()
        mock_b2.assert_called_with("i", "k", "b")

def test_main_missing_creds():
    with patch("sys.argv", ["check_b2.py"]):
        with pytest.raises(SystemExit):
            check_b2.main()

@patch("geminiai_cli.check_b2.B2Manager")
def test_main_b2_fail(mock_b2):
    with patch("sys.argv", ["check_b2.py", "--b2-id", "i", "--b2-key", "k", "--bucket", "b"]):
        mock_b2.side_effect = SystemExit(1)
        with pytest.raises(SystemExit):
            check_b2.main()

@patch("geminiai_cli.check_b2.B2Manager")
def test_main_b2_exception(mock_b2):
    with patch("sys.argv", ["check_b2.py", "--b2-id", "i", "--b2-key", "k", "--bucket", "b"]):
        mock_b2.side_effect = Exception("Unexpected")
        with pytest.raises(SystemExit):
            check_b2.main()
