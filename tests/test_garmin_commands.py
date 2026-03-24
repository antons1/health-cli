import json
from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from health_data.cli import main


@pytest.fixture
def runner():
    """Click test runner — invokes CLI commands in isolation."""
    return CliRunner()


@pytest.fixture
def mock_get_client():
    """Patch get_client to return a mock Garmin client."""
    mock_client = MagicMock()
    with patch(
        "health_data.sources.garmin.commands.get_client",
        return_value=mock_client,
    ) as patcher:
        yield mock_client


class TestGarminGroup:
    def test_garmin_group_exists(self, runner):
        result = runner.invoke(main, ["garmin", "--help"])
        assert result.exit_code == 0
        assert "Garmin Connect data" in result.output

    def test_garmin_shows_subcommands(self, runner):
        result = runner.invoke(main, ["garmin", "--help"])
        assert "stats" in result.output
        assert "sleep" in result.output
        assert "heart-rate" in result.output
        assert "stress" in result.output
        assert "hrv" in result.output
        assert "spo2" in result.output
        assert "weight" in result.output
        assert "activities" in result.output
        assert "activity" in result.output
        assert "login" in result.output


class TestLoginCommand:
    def test_login_prompts_and_authenticates(self, runner):
        """In non-TTY mode (CliRunner), falls back to click.prompt for password."""
        with patch("health_data.sources.garmin.commands.do_login") as mock_login:
            result = runner.invoke(
                main,
                ["garmin", "login"],
                input="user@example.com\nsecret123\n",
            )
        assert result.exit_code == 0
        assert "Logged in successfully" in result.output
        mock_login.assert_called_once_with("user@example.com", "secret123")

    def test_login_accepts_options(self, runner):
        with patch("health_data.sources.garmin.commands.do_login") as mock_login:
            result = runner.invoke(
                main,
                ["garmin", "login", "--email", "a@b.com", "--password", "pw"],
            )
        assert result.exit_code == 0
        mock_login.assert_called_once_with("a@b.com", "pw")


class TestStatsCommand:
    def test_stats_default_today(self, runner, mock_get_client):
        mock_get_client.get_stats.return_value = {"steps": 10000}
        result = runner.invoke(main, ["garmin", "stats"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data == {"steps": 10000}
        mock_get_client.get_stats.assert_called_once_with(date.today().isoformat())

    def test_stats_with_date(self, runner, mock_get_client):
        mock_get_client.get_stats.return_value = {"steps": 8000}
        result = runner.invoke(main, ["garmin", "stats", "2024-03-20"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data == {"steps": 8000}
        mock_get_client.get_stats.assert_called_once_with("2024-03-20")


class TestSleepCommand:
    def test_sleep_default_today(self, runner, mock_get_client):
        mock_get_client.get_sleep_data.return_value = {"sleepScore": 85}
        result = runner.invoke(main, ["garmin", "sleep"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data == {"sleepScore": 85}

    def test_sleep_with_yesterday(self, runner, mock_get_client):
        from datetime import timedelta
        mock_get_client.get_sleep_data.return_value = {"sleepScore": 90}
        result = runner.invoke(main, ["garmin", "sleep", "yesterday"])
        assert result.exit_code == 0
        expected_date = (date.today() - timedelta(days=1)).isoformat()
        mock_get_client.get_sleep_data.assert_called_once_with(expected_date)


class TestHeartRateCommand:
    def test_heart_rate(self, runner, mock_get_client):
        mock_get_client.get_heart_rates.return_value = {"restingHR": 55}
        result = runner.invoke(main, ["garmin", "heart-rate"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data == {"restingHR": 55}


class TestStressCommand:
    def test_stress(self, runner, mock_get_client):
        mock_get_client.get_stress_data.return_value = {"avgStress": 30}
        result = runner.invoke(main, ["garmin", "stress"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data == {"avgStress": 30}


class TestHrvCommand:
    def test_hrv(self, runner, mock_get_client):
        mock_get_client.get_hrv_data.return_value = {"weeklyAvg": 45}
        result = runner.invoke(main, ["garmin", "hrv"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data == {"weeklyAvg": 45}


class TestSpo2Command:
    def test_spo2(self, runner, mock_get_client):
        mock_get_client.get_spo2_data.return_value = {"avgSpo2": 96}
        result = runner.invoke(main, ["garmin", "spo2"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data == {"avgSpo2": 96}


class TestWeightCommand:
    def test_weight_default(self, runner, mock_get_client):
        mock_get_client.get_body_composition.return_value = {"weight": 75.0}
        result = runner.invoke(main, ["garmin", "weight"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data == {"weight": 75.0}

    def test_weight_with_range(self, runner, mock_get_client):
        mock_get_client.get_body_composition.return_value = {"weight": 75.0}
        result = runner.invoke(
            main, ["garmin", "weight", "2024-03-01", "--end", "2024-03-20"]
        )
        assert result.exit_code == 0
        mock_get_client.get_body_composition.assert_called_once_with(
            "2024-03-01", "2024-03-20"
        )


class TestActivitiesCommand:
    def test_activities_default(self, runner, mock_get_client):
        mock_get_client.get_activities.return_value = [{"name": "Run"}]
        result = runner.invoke(main, ["garmin", "activities"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data == [{"name": "Run"}]
        mock_get_client.get_activities.assert_called_once_with(0, 20)

    def test_activities_with_limit(self, runner, mock_get_client):
        mock_get_client.get_activities.return_value = []
        result = runner.invoke(main, ["garmin", "activities", "--limit", "5"])
        assert result.exit_code == 0
        mock_get_client.get_activities.assert_called_once_with(0, 5)


class TestActivityCommand:
    def test_activity_by_id(self, runner, mock_get_client):
        mock_get_client.get_activity.return_value = {"activityId": 123}
        result = runner.invoke(main, ["garmin", "activity", "123"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data == {"activityId": 123}
