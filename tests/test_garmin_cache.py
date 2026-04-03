import json
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from health_data.sources.garmin.cache import read_cache, write_cache, STATIC_TTL, DYNAMIC_TTL


@pytest.fixture
def cache_dir(tmp_path):
    with patch("health_data.sources.garmin.cache.CACHE_DIR", tmp_path):
        yield tmp_path


class TestWriteCache:
    def test_writes_data_to_file(self, cache_dir):
        write_cache("sleep", "2026-04-02", {"score": 72})
        path = cache_dir / "sleep_2026-04-02.json"
        assert path.exists()
        entry = json.loads(path.read_text())
        assert entry["data"] == {"score": 72}

    def test_records_cached_at_timestamp(self, cache_dir):
        before = time.time()
        write_cache("hrv", "2026-04-02", {"last_night_avg": 66})
        after = time.time()
        entry = json.loads((cache_dir / "hrv_2026-04-02.json").read_text())
        assert before <= entry["cached_at"] <= after


class TestReadCache:
    def test_returns_none_when_no_cache_file(self, cache_dir):
        result = read_cache("sleep", "2026-04-02", ttl=None)
        assert result is None

    def test_returns_data_when_cache_exists_and_no_ttl(self, cache_dir):
        write_cache("sleep", "2026-04-02", {"score": 72})
        result = read_cache("sleep", "2026-04-02", ttl=None)
        assert result == {"score": 72}

    def test_returns_data_within_ttl(self, cache_dir):
        write_cache("sleep", "2026-04-02", {"score": 72})
        result = read_cache("sleep", "2026-04-02", ttl=3600)
        assert result == {"score": 72}

    def test_returns_none_when_expired(self, cache_dir):
        write_cache("stress", "2026-04-02", {"avg": 26})
        # Backdate the cached_at timestamp
        path = cache_dir / "stress_2026-04-02.json"
        entry = json.loads(path.read_text())
        entry["cached_at"] = time.time() - 3601
        path.write_text(json.dumps(entry))

        result = read_cache("stress", "2026-04-02", ttl=3600)
        assert result is None

    def test_no_ttl_returns_old_data(self, cache_dir):
        """Past-date data with ttl=None should never expire."""
        write_cache("sleep", "2020-01-01", {"score": 80})
        path = cache_dir / "sleep_2020-01-01.json"
        entry = json.loads(path.read_text())
        entry["cached_at"] = 0  # epoch — very old
        path.write_text(json.dumps(entry))

        result = read_cache("sleep", "2020-01-01", ttl=None)
        assert result == {"score": 80}


class TestTtlConstants:
    def test_static_ttl_is_at_least_one_hour(self):
        assert STATIC_TTL >= 3600

    def test_dynamic_ttl_is_shorter_than_static(self):
        assert DYNAMIC_TTL < STATIC_TTL
