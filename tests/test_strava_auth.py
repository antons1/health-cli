import json
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from health_data.sources.strava.auth import (
    CONFIG_DIR,
    setup,
    get_client,
    load_config,
    save_tokens,
    load_tokens,
)


class TestSetup:
    def test_saves_config(self, tmp_path):
        """setup() saves client_id and client_secret to config.json."""
        with patch("health_data.sources.strava.auth.CONFIG_DIR", tmp_path):
            setup("12345", "my_secret")

        config_file = tmp_path / "config.json"
        assert config_file.exists()
        data = json.loads(config_file.read_text())
        assert data["client_id"] == "12345"
        assert data["client_secret"] == "my_secret"

    def test_overwrites_existing_config(self, tmp_path):
        """setup() overwrites existing config."""
        with patch("health_data.sources.strava.auth.CONFIG_DIR", tmp_path):
            setup("old_id", "old_secret")
            setup("new_id", "new_secret")

        data = json.loads((tmp_path / "config.json").read_text())
        assert data["client_id"] == "new_id"


class TestLoadConfig:
    def test_loads_config(self, tmp_path):
        """load_config() reads client_id and client_secret."""
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({
            "client_id": "12345",
            "client_secret": "my_secret",
        }))
        with patch("health_data.sources.strava.auth.CONFIG_DIR", tmp_path):
            config = load_config()
        assert config["client_id"] == "12345"
        assert config["client_secret"] == "my_secret"

    def test_exits_when_no_config(self, tmp_path):
        """load_config() exits with code 1 if no config exists."""
        with patch("health_data.sources.strava.auth.CONFIG_DIR", tmp_path):
            with pytest.raises(SystemExit) as exc_info:
                load_config()
            assert exc_info.value.code == 1


class TestTokenPersistence:
    def test_save_and_load_tokens(self, tmp_path):
        """Tokens can be saved and loaded."""
        tokens = {
            "access_token": "abc",
            "refresh_token": "def",
            "expires_at": 1234567890,
        }
        with patch("health_data.sources.strava.auth.CONFIG_DIR", tmp_path):
            save_tokens(tokens)
            loaded = load_tokens()

        assert loaded["access_token"] == "abc"
        assert loaded["refresh_token"] == "def"
        assert loaded["expires_at"] == 1234567890

    def test_load_tokens_exits_when_missing(self, tmp_path):
        """load_tokens() exits with code 1 if no tokens exist."""
        with patch("health_data.sources.strava.auth.CONFIG_DIR", tmp_path):
            with pytest.raises(SystemExit) as exc_info:
                load_tokens()
            assert exc_info.value.code == 1


class TestGetClient:
    def test_returns_client_with_valid_token(self, tmp_path):
        """get_client() returns a stravalib Client when token is not expired."""
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({
            "client_id": "12345",
            "client_secret": "my_secret",
        }))
        tokens_file = tmp_path / "tokens.json"
        tokens_file.write_text(json.dumps({
            "access_token": "valid_token",
            "refresh_token": "refresh_tok",
            "expires_at": time.time() + 3600,  # expires in 1 hour
        }))

        with patch("health_data.sources.strava.auth.CONFIG_DIR", tmp_path):
            client = get_client()

        assert client.access_token == "valid_token"

    def test_refreshes_expired_token(self, tmp_path):
        """get_client() refreshes token when expired and saves new tokens."""
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({
            "client_id": "12345",
            "client_secret": "my_secret",
        }))
        tokens_file = tmp_path / "tokens.json"
        tokens_file.write_text(json.dumps({
            "access_token": "expired_token",
            "refresh_token": "refresh_tok",
            "expires_at": time.time() - 100,  # already expired
        }))

        mock_refresh_response = {
            "access_token": "new_token",
            "refresh_token": "new_refresh",
            "expires_at": time.time() + 3600,
        }

        with patch("health_data.sources.strava.auth.CONFIG_DIR", tmp_path), \
             patch("health_data.sources.strava.auth.Client") as MockClient:
            mock_instance = MockClient.return_value
            mock_instance.refresh_access_token.return_value = mock_refresh_response
            client = get_client()

        mock_instance.refresh_access_token.assert_called_once_with(
            client_id="12345",
            client_secret="my_secret",
            refresh_token="refresh_tok",
        )
        # Verify new tokens were saved
        saved = json.loads(tokens_file.read_text())
        assert saved["access_token"] == "new_token"
        assert saved["refresh_token"] == "new_refresh"

    def test_exits_when_not_setup(self, tmp_path):
        """get_client() exits if strava hasn't been set up."""
        with patch("health_data.sources.strava.auth.CONFIG_DIR", tmp_path):
            with pytest.raises(SystemExit):
                get_client()

    def test_exits_when_not_logged_in(self, tmp_path):
        """get_client() exits if no tokens exist (setup done but not logged in)."""
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({
            "client_id": "12345",
            "client_secret": "my_secret",
        }))
        with patch("health_data.sources.strava.auth.CONFIG_DIR", tmp_path):
            with pytest.raises(SystemExit):
                get_client()
