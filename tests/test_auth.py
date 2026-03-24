import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from health_data.sources.garmin.auth import get_client, login, TOKEN_DIR


class TestLogin:
    def test_login_authenticates_and_saves_tokens(self, tmp_path):
        """login() calls Garmin.login() and dumps tokens to disk."""
        mock_client = MagicMock()

        with patch("health_data.sources.garmin.auth.Garmin", return_value=mock_client) as MockGarmin, \
             patch("health_data.sources.garmin.auth.TOKEN_DIR", tmp_path / "tokens"):
            result = login("user@example.com", "secret123")

        # Garmin was constructed with credentials
        MockGarmin.assert_called_once_with("user@example.com", "secret123")
        # .login() was called to authenticate
        mock_client.login.assert_called_once()
        # Tokens were saved to disk
        mock_client.garth.dump.assert_called_once()
        # Returns the client
        assert result is mock_client

    def test_login_does_not_persist_password(self, tmp_path):
        """After login, the token directory should not contain the password."""
        mock_client = MagicMock()

        with patch("health_data.sources.garmin.auth.Garmin", return_value=mock_client), \
             patch("health_data.sources.garmin.auth.TOKEN_DIR", tmp_path / "tokens"):
            login("user@example.com", "secret123")

        # garth.dump is called with a path, not with credentials
        dump_call_args = mock_client.garth.dump.call_args
        dump_path = str(dump_call_args[0][0])
        assert "secret123" not in dump_path

    def test_login_rate_limit_exits(self, tmp_path):
        """login() exits cleanly on 429 rate limit."""
        from garminconnect import GarminConnectConnectionError
        mock_client = MagicMock()
        mock_client.login.side_effect = GarminConnectConnectionError("429 Too Many Requests")

        with patch("health_data.sources.garmin.auth.Garmin", return_value=mock_client), \
             patch("health_data.sources.garmin.auth.TOKEN_DIR", tmp_path / "tokens"):
            with pytest.raises(SystemExit) as exc_info:
                login("user@example.com", "secret123")
            assert exc_info.value.code == 1

    def test_login_auth_error_exits(self, tmp_path):
        """login() exits cleanly on authentication failure."""
        from garminconnect import GarminConnectAuthenticationError
        mock_client = MagicMock()
        mock_client.login.side_effect = GarminConnectAuthenticationError("bad creds")

        with patch("health_data.sources.garmin.auth.Garmin", return_value=mock_client), \
             patch("health_data.sources.garmin.auth.TOKEN_DIR", tmp_path / "tokens"):
            with pytest.raises(SystemExit) as exc_info:
                login("user@example.com", "secret123")
            assert exc_info.value.code == 1


class TestGetClient:
    def test_exits_when_not_logged_in(self, tmp_path):
        """get_client() exits with code 1 if no saved tokens exist."""
        with patch("health_data.sources.garmin.auth.TOKEN_DIR", tmp_path / "nonexistent"):
            with pytest.raises(SystemExit) as exc_info:
                get_client()
            assert exc_info.value.code == 1

    def test_loads_tokens_when_they_exist(self, tmp_path):
        """get_client() loads saved tokens and returns a Garmin client."""
        token_dir = tmp_path / "tokens"
        token_dir.mkdir()

        mock_client = MagicMock()

        with patch("health_data.sources.garmin.auth.Garmin", return_value=mock_client) as MockGarmin, \
             patch("health_data.sources.garmin.auth.TOKEN_DIR", token_dir):
            result = get_client()

        # Garmin was constructed without credentials (token-based)
        MockGarmin.assert_called_once_with()
        # Tokens were loaded
        mock_client.garth.load.assert_called_once_with(str(token_dir))
        # .login() was called to refresh if needed
        mock_client.login.assert_called_once()
        # Returns the client
        assert result is mock_client
