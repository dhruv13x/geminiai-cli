import pytest
from unittest.mock import patch, MagicMock
from geminiai_cli.settings_cli import do_config

def mock_args(action="list", key=None, value=None):
    return MagicMock(config_action=action, key=key, value=value)

@patch("geminiai_cli.settings_cli.list_settings")
@patch("geminiai_cli.settings_cli.cprint")
def test_do_config_list(mock_cprint, mock_list):
    mock_list.return_value = {"my_key": "my_value", "secret_key": "secret12345"}

    with patch("builtins.print") as mock_print:
        do_config(mock_args(action="list"))

        # Check masking
        found_masked = False
        for call in mock_print.call_args_list:
            # The exact string is: '  \x1b[92;1msecret_key\x1b[0m: se*******45'
            # My previous assertion "se***45" was not matching because there are 7 asterisks.
            # secret12345 (11 chars) -> se (2) + * (11-4=7) + 45 (2) = se*******45
            if "se*******45" in str(call):
                 found_masked = True
        assert found_masked

@patch("geminiai_cli.settings_cli.list_settings")
@patch("geminiai_cli.settings_cli.cprint")
def test_do_config_list_empty(mock_cprint, mock_list):
    mock_list.return_value = {}
    do_config(mock_args(action="list"))
    assert any("No settings configured" in str(c) for c in mock_cprint.call_args_list)

@patch("geminiai_cli.settings_cli.cprint")
def test_do_config_no_key(mock_cprint):
    # Action set/get/unset requires key
    do_config(mock_args(action="set", key=None))
    assert any("Key required" in str(c) for c in mock_cprint.call_args_list)

@patch("geminiai_cli.settings_cli.set_setting")
@patch("geminiai_cli.settings_cli.cprint")
def test_do_config_set(mock_cprint, mock_set):
    do_config(mock_args(action="set", key="k", value="v"))
    mock_set.assert_called_with("k", "v")
    assert any("Set k = v" in str(c) for c in mock_cprint.call_args_list)

@patch("geminiai_cli.settings_cli.cprint")
def test_do_config_set_no_value(mock_cprint):
    do_config(mock_args(action="set", key="k", value=None))
    assert any("Value required" in str(c) for c in mock_cprint.call_args_list)

@patch("geminiai_cli.settings_cli.get_setting")
@patch("geminiai_cli.settings_cli.cprint")
def test_do_config_get(mock_cprint, mock_get):
    mock_get.return_value = "my_val"
    do_config(mock_args(action="get", key="k"))
    assert any("my_val" in str(c) for c in mock_cprint.call_args_list)

@patch("geminiai_cli.settings_cli.get_setting")
@patch("geminiai_cli.settings_cli.cprint")
def test_do_config_get_none(mock_cprint, mock_get):
    mock_get.return_value = None
    do_config(mock_args(action="get", key="k"))
    assert any("(not set)" in str(c) for c in mock_cprint.call_args_list)

@patch("geminiai_cli.settings_cli.remove_setting")
@patch("geminiai_cli.settings_cli.cprint")
def test_do_config_unset(mock_cprint, mock_remove):
    mock_remove.return_value = True
    do_config(mock_args(action="unset", key="k"))
    assert any("Removed k" in str(c) for c in mock_cprint.call_args_list)

@patch("geminiai_cli.settings_cli.remove_setting")
@patch("geminiai_cli.settings_cli.cprint")
def test_do_config_unset_fail(mock_cprint, mock_remove):
    mock_remove.return_value = False
    do_config(mock_args(action="unset", key="k"))
    assert any("Key k not found" in str(c) for c in mock_cprint.call_args_list)
