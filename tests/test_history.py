
import json
import os
import datetime
import pytest
from unittest.mock import patch, mock_open

# We will create this module later
from geminiai_cli import history

# Mock constant for test isolation
TEST_HISTORY_FILE = "test_gemini_history.json"

@pytest.fixture
def mock_history_file(fs):
    """
    Uses pyfakefs to mock the file system.
    Sets the history file path to a fake path.
    """
    # We need to patch the constant in the module,
    # but since we haven't imported it yet (or it might not exist),
    # we'll rely on the module using a variable we can patch or
    # we'll patch os.path.expanduser if the module uses that.
    # Ideally, the module allows overriding the path.
    pass

def test_record_event_creates_file_if_missing(fs):
    """Test that record_event creates the history file if it doesn't exist."""
    # Setup
    fs.create_dir(os.path.expanduser("~"))

    # Action
    with patch("geminiai_cli.history.HISTORY_FILE", os.path.expanduser("~/test_history.json")):
        history.record_event("test@example.com", "switch")

        # Assertion
        path = os.path.expanduser("~/test_history.json")
        assert os.path.exists(path)
        with open(path, "r") as f:
            data = json.load(f)
            assert len(data) == 1
            assert data[0]["email"] == "test@example.com"
            assert data[0]["event"] == "switch"
            assert "timestamp" in data[0]

def test_record_event_appends_to_existing_file(fs):
    """Test that record_event appends to an existing history file."""
    # Setup
    path = os.path.expanduser("~/test_history.json")
    existing_data = [
        {"timestamp": "2023-01-01T00:00:00", "email": "old@example.com", "event": "switch"}
    ]
    fs.create_file(path, contents=json.dumps(existing_data))

    # Action
    with patch("geminiai_cli.history.HISTORY_FILE", path):
        history.record_event("new@example.com", "switch")

        # Assertion
        with open(path, "r") as f:
            data = json.load(f)
            assert len(data) == 2
            assert data[0]["email"] == "old@example.com"
            assert data[1]["email"] == "new@example.com"

def test_get_events_last_7_days(fs):
    """Test filtering events for the last 7 days."""
    path = os.path.expanduser("~/test_history.json")
    now = datetime.datetime.now(datetime.timezone.utc)

    events = []
    # Event 1: Today
    events.append({
        "timestamp": now.isoformat(),
        "email": "today@example.com",
        "event": "switch"
    })
    # Event 2: 5 days ago (Should be included)
    events.append({
        "timestamp": (now - datetime.timedelta(days=5)).isoformat(),
        "email": "5days@example.com",
        "event": "switch"
    })
    # Event 3: 10 days ago (Should be excluded)
    events.append({
        "timestamp": (now - datetime.timedelta(days=10)).isoformat(),
        "email": "10days@example.com",
        "event": "switch"
    })

    fs.create_file(path, contents=json.dumps(events))

    with patch("geminiai_cli.history.HISTORY_FILE", path):
        # We need to mock datetime in history module to ensure consistency if it uses 'now'
        # But get_events usually takes a range or calculates from 'now'.
        # For this test, we assume get_events filters based on actual time.

        recent_events = history.get_events_last_n_days(7)

        assert len(recent_events) == 2
        emails = [e["email"] for e in recent_events]
        assert "today@example.com" in emails
        assert "5days@example.com" in emails
        assert "10days@example.com" not in emails
