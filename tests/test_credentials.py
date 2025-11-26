import os
import unittest
from unittest.mock import patch, MagicMock
import argparse
from geminiai_cli.credentials import resolve_credentials

class TestCredentials(unittest.TestCase):

    @patch('geminiai_cli.credentials.os.environ', {})
    @patch('geminiai_cli.credentials.load_env_file')
    @patch('geminiai_cli.credentials.get_doppler_token')
    @patch('geminiai_cli.credentials.get_setting')
    def test_cli_priority(self, mock_get_setting, mock_get_token, mock_load_env):
        # CLI args should win
        args = argparse.Namespace(b2_id="CLI_ID", b2_key="CLI_KEY", bucket="CLI_BUCKET")
        
        # Setup mocks to provide conflicting info
        mock_get_token.return_value = None
        mock_get_setting.return_value = "SETTINGS_VAL"
        
        cid, ckey, cbucket = resolve_credentials(args)
        self.assertEqual(cid, "CLI_ID")
        self.assertEqual(ckey, "CLI_KEY")
        self.assertEqual(cbucket, "CLI_BUCKET")

    @patch('geminiai_cli.credentials.os.environ', {})
    @patch('geminiai_cli.credentials.load_env_file')
    @patch('geminiai_cli.credentials.get_doppler_token')
    @patch('geminiai_cli.credentials.fetch_doppler_secrets')
    @patch('geminiai_cli.credentials.get_setting')
    def test_doppler_priority(self, mock_get_setting, mock_fetch, mock_get_token, mock_load_env):
        # CLI args missing
        args = argparse.Namespace(b2_id=None, b2_key=None, bucket=None)
        
        # Doppler token found
        mock_get_token.return_value = "TOKEN"
        mock_fetch.return_value = {
            "GEMINI_B2_KEY_ID": "DOPPLER_ID",
            "GEMINI_B2_APP_KEY": "DOPPLER_KEY",
            "GEMINI_B2_BUCKET": "DOPPLER_BUCKET"
        }
        
        mock_get_setting.return_value = "SETTINGS_VAL"

        cid, ckey, cbucket = resolve_credentials(args)
        self.assertEqual(cid, "DOPPLER_ID")
        self.assertEqual(ckey, "DOPPLER_KEY")
        self.assertEqual(cbucket, "DOPPLER_BUCKET")

    @patch('geminiai_cli.credentials.os.environ', {
        "GEMINI_B2_KEY_ID": "ENV_ID",
        "GEMINI_B2_APP_KEY": "ENV_KEY",
        "GEMINI_B2_BUCKET": "ENV_BUCKET"
    })
    @patch('geminiai_cli.credentials.load_env_file')
    @patch('geminiai_cli.credentials.get_doppler_token')
    @patch('geminiai_cli.credentials.get_setting')
    def test_env_priority(self, mock_get_setting, mock_get_token, mock_load_env):
        args = argparse.Namespace(b2_id=None, b2_key=None, bucket=None)
        mock_get_token.return_value = None
        mock_get_setting.return_value = "SETTINGS_VAL"
        
        cid, ckey, cbucket = resolve_credentials(args)
        self.assertEqual(cid, "ENV_ID")

    @patch('geminiai_cli.credentials.os.environ', {})
    @patch('geminiai_cli.credentials.load_env_file')
    @patch('geminiai_cli.credentials.get_doppler_token')
    @patch('geminiai_cli.credentials.get_setting')
    def test_env_file_priority(self, mock_get_setting, mock_get_token, mock_load_env):
        args = argparse.Namespace(b2_id=None, b2_key=None, bucket=None)
        mock_get_token.return_value = None
        mock_load_env.side_effect = lambda x: {"GEMINI_B2_KEY_ID": "FILE_ID", "GEMINI_B2_APP_KEY": "FILE_KEY", "GEMINI_B2_BUCKET": "FILE_BUCKET"} if x == ".env" else {}
        mock_get_setting.return_value = "SETTINGS_VAL"
        
        cid, ckey, cbucket = resolve_credentials(args)
        self.assertEqual(cid, "FILE_ID")

if __name__ == '__main__':
    unittest.main()
