import pytest
from unittest.mock import patch
from datetime import datetime, timedelta, timezone
from freezegun import freeze_time

from src.geminiai_cli.recommend import get_recommendation, AccountStatus

# Constants matching implementation
COOLDOWN_HOURS = 24

@pytest.fixture
def mock_data_sources():
    with patch("src.geminiai_cli.recommend.get_cooldown_data") as mock_cd, \
         patch("src.geminiai_cli.recommend.get_all_resets") as mock_resets:
        yield mock_cd, mock_resets

@freeze_time("2025-01-01 12:00:00")
def test_recommend_no_accounts(mock_data_sources):
    mock_cd, mock_resets = mock_data_sources
    mock_cd.return_value = {}
    mock_resets.return_value = []

    rec = get_recommendation()
    assert rec is None

@freeze_time("2025-01-01 12:00:00")
def test_recommend_one_ready_account(mock_data_sources):
    mock_cd, mock_resets = mock_data_sources

    # Now is 2025-01-01 12:00:00 UTC
    now = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    # Account A: Used 30 hours ago (Ready)
    # Account B: Used 1 hour ago (Cooldown)
    t_ready = (now - timedelta(hours=30)).isoformat()
    t_locked = (now - timedelta(hours=1)).isoformat()

    mock_cd.return_value = {
        "ready@test.com": t_ready,
        "locked@test.com": t_locked
    }
    mock_resets.return_value = []

    rec = get_recommendation()
    assert rec is not None
    assert rec.email == "ready@test.com"
    assert rec.status == AccountStatus.READY

@freeze_time("2025-01-01 12:00:00")
def test_recommend_lru_logic(mock_data_sources):
    mock_cd, mock_resets = mock_data_sources
    now = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    # Both Ready
    # Account A: Used 30 hours ago
    # Account B: Used 100 hours ago (should be preferred as "more rested")

    t_recent = (now - timedelta(hours=30)).isoformat()
    t_old = (now - timedelta(hours=100)).isoformat()

    mock_cd.return_value = {
        "recent@test.com": t_recent,
        "old@test.com": t_old
    }
    # "unused@test.com" exists in resets (known account) but not in cooldowns (never switched to)
    mock_resets.return_value = [{"email": "unused@test.com", "reset_ist": "2025-01-01T00:00:00"}]

    rec = get_recommendation()
    # Logic: Unused (Never) > Oldest Used > ...
    assert rec.email == "unused@test.com"

    # Remove unused, test between recent and old
    mock_resets.return_value = []
    rec = get_recommendation()
    assert rec.email == "old@test.com"

@freeze_time("2025-01-01 12:00:00")
def test_recommend_scheduled_logic(mock_data_sources):
    mock_cd, mock_resets = mock_data_sources
    now = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    # Account A: Ready (Last used long ago)
    t_ready = (now - timedelta(hours=30)).isoformat()

    mock_cd.return_value = {
        "ready@test.com": t_ready,
        "scheduled@test.com": (now - timedelta(hours=30)).isoformat()
    }

    # Scheduled reset 1 hour in future
    future_reset = (now + timedelta(hours=1)).isoformat()
    mock_resets.return_value = [
        {"email": "scheduled@test.com", "reset_ist": future_reset}
    ]

    rec = get_recommendation()
    assert rec.email == "ready@test.com"
    assert rec.status == AccountStatus.READY

@freeze_time("2025-01-01 12:00:00")
def test_recommend_all_locked(mock_data_sources):
    mock_cd, mock_resets = mock_data_sources
    now = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    # All locked
    t_locked = (now - timedelta(hours=1)).isoformat()
    mock_cd.return_value = {"locked@test.com": t_locked}
    mock_resets.return_value = []

    rec = get_recommendation()
    assert rec is None
