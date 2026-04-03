import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from health_data.sources.garmin.auth import (
    CONFIG_DIR,
    save_config,
    load_config,
    login,
    get_client,
)


class TestSaveConfig:
    def test_saves_email(self, tmp_path):
        """save_config() writes email to config.json."""
        with patch("health_data.sources.garmin.auth.CONFIG_DIR", tmp_path):
            save_config("user@example.com")

        data = json.loads((tmp_path / "config.json").read_text())
        assert data["email"] == "user@example.com"

    def test_creates_dir_if_missing(self, tmp_path):
        """save_config() creates the config directory if it doesn't exist."""
        config_dir = tmp_path / "subdir"
        with patch("health_data.sources.garmin.auth.CONFIG_DIR", config_dir):
            save_config("user@example.com")

        assert (config_dir / "config.json").exists()

    def test_overwrites_existing_config(self, tmp_path):
        """save_config() overwrites existing config."""
        with patch("health_data.sources.garmin.auth.CONFIG_DIR", tmp_path):
            save_config("old@example.com")
            save_config("new@example.com")

        data = json.loads((tmp_path / "config.json").read_text())
        assert data["email"] == "new@example.com"


class TestLoadConfig:
    def test_loads_email(self, tmp_path):
        """load_config() returns config dict with email."""
        (tmp_path / "config.json").write_text(json.dumps({"email": "user@example.com"}))

        with patch("health_data.sources.garmin.auth.CONFIG_DIR", tmp_path):
            config = load_config()

        assert config["email"] == "user@example.com"

    def test_exits_when_no_config(self, tmp_path):
        """load_config() exits with code 1 if config.json is missing."""
        with patch("health_data.sources.garmin.auth.CONFIG_DIR", tmp_path):
            with pytest.raises(SystemExit) as exc_info:
                load_config()
        assert exc_info.value.code == 1


class TestLogin:
    def test_saves_config_and_returns_client(self, tmp_path):
        """login() saves email to config and returns an authenticated Garmin client."""
        mock_garmin = MagicMock()

        with patch("health_data.sources.garmin.auth.CONFIG_DIR", tmp_path), \
             patch("health_data.sources.garmin.auth.Garmin", return_value=mock_garmin) as MockGarmin:
            result = login("user@example.com", "secret")

        MockGarmin.assert_called_once_with("user@example.com", "secret")
        mock_garmin.login.assert_called_once_with(tokenstore=str(tmp_path))
        mock_garmin.client.dump.assert_called_once_with(str(tmp_path))
        assert result is mock_garmin

        data = json.loads((tmp_path / "config.json").read_text())
        assert data["email"] == "user@example.com"


class TestGetClient:
    def test_returns_client_using_saved_tokens(self, tmp_path):
        """get_client() loads email from config and authenticates with saved tokens."""
        (tmp_path / "config.json").write_text(json.dumps({"email": "user@example.com"}))
        mock_garmin = MagicMock()

        with patch("health_data.sources.garmin.auth.CONFIG_DIR", tmp_path), \
             patch("health_data.sources.garmin.auth.Garmin", return_value=mock_garmin) as MockGarmin:
            client = get_client()

        MockGarmin.assert_called_once_with("user@example.com")
        mock_garmin.login.assert_called_once_with(tokenstore=str(tmp_path))
        assert client is mock_garmin

    def test_exits_when_not_configured(self, tmp_path):
        """get_client() exits if no config exists."""
        with patch("health_data.sources.garmin.auth.CONFIG_DIR", tmp_path):
            with pytest.raises(SystemExit):
                get_client()
