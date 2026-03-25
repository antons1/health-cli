import json
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from health_data.cli import main


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_strava_client():
    """Patch get_client to return a mock stravalib Client."""
    mock_client = MagicMock()
    with patch(
        "health_data.sources.strava.commands.get_client",
        return_value=mock_client,
    ):
        yield mock_client


class TestStravaGroup:
    def test_strava_group_exists(self, runner):
        result = runner.invoke(main, ["strava", "--help"])
        assert result.exit_code == 0
        assert "Strava data" in result.output

    def test_strava_shows_subcommands(self, runner):
        result = runner.invoke(main, ["strava", "--help"])
        assert "setup" in result.output
        assert "login" in result.output
        assert "activities" in result.output
        assert "activity" in result.output
        assert "streams" in result.output


class TestSetupCommand:
    def test_setup_saves_credentials(self, runner):
        with patch("health_data.sources.strava.commands.do_setup") as mock_setup:
            result = runner.invoke(
                main,
                ["strava", "setup"],
                input="12345\nmy_secret\n",
            )
        assert result.exit_code == 0
        assert "saved" in result.output.lower()
        mock_setup.assert_called_once_with("12345", "my_secret")

    def test_setup_accepts_options(self, runner):
        with patch("health_data.sources.strava.commands.do_setup") as mock_setup:
            result = runner.invoke(
                main,
                ["strava", "setup", "--client-id", "99", "--client-secret", "sec"],
            )
        assert result.exit_code == 0
        mock_setup.assert_called_once_with("99", "sec")


class TestLoginCommand:
    def test_login_runs_oauth_flow(self, runner):
        with patch("health_data.sources.strava.commands.do_login") as mock_login:
            result = runner.invoke(main, ["strava", "login"])
        assert result.exit_code == 0
        assert "success" in result.output.lower()
        mock_login.assert_called_once()


SAMPLE_ACTIVITY = {
    "id": 1,
    "name": "Run",
    "sport_type": "Run",
    "start_date_local": "2026-03-24T14:52:27+00:00",
    "distance": 5000.0,
    "moving_time": 1500,
    "average_heartrate": 150.0,
    "total_elevation_gain": 20.0,
}


class TestActivitiesCommand:
    def test_activities_json_mode(self, runner, mock_strava_client):
        """--json flag outputs raw JSON."""
        with patch(
            "health_data.sources.strava.commands.strava_client.get_activities",
            return_value=[SAMPLE_ACTIVITY],
        ):
            result = runner.invoke(main, ["--json", "strava", "activities"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data == [SAMPLE_ACTIVITY]

    def test_activities_human_mode(self, runner, mock_strava_client):
        """Default output is human-readable table."""
        with patch(
            "health_data.sources.strava.commands.strava_client.get_activities",
            return_value=[SAMPLE_ACTIVITY],
        ):
            result = runner.invoke(main, ["strava", "activities"])

        assert result.exit_code == 0
        assert "Run" in result.output
        assert "5.0 km" in result.output
        # Should NOT be valid JSON
        with pytest.raises(json.JSONDecodeError):
            json.loads(result.output)

    def test_activities_with_limit(self, runner, mock_strava_client):
        with patch(
            "health_data.sources.strava.commands.strava_client.get_activities",
            return_value=[],
        ) as mock_get:
            result = runner.invoke(main, ["strava", "activities", "--limit", "5"])

        assert result.exit_code == 0
        mock_get.assert_called_once_with(mock_strava_client, limit=5)


class TestActivityCommand:
    def test_activity_json_mode(self, runner, mock_strava_client):
        with patch(
            "health_data.sources.strava.commands.strava_client.get_activity",
            return_value=SAMPLE_ACTIVITY,
        ):
            result = runner.invoke(main, ["--json", "strava", "activity", "1"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["id"] == 1

    def test_activity_human_mode(self, runner, mock_strava_client):
        with patch(
            "health_data.sources.strava.commands.strava_client.get_activity",
            return_value=SAMPLE_ACTIVITY,
        ):
            result = runner.invoke(main, ["strava", "activity", "1"])

        assert result.exit_code == 0
        assert "Run" in result.output
        assert "5.0 km" in result.output


class TestStreamsCommand:
    def test_streams_json_mode(self, runner, mock_strava_client):
        with patch(
            "health_data.sources.strava.commands.strava_client.get_streams",
            return_value={"heartrate": [120, 125], "time": [0, 1]},
        ):
            result = runner.invoke(main, ["--json", "strava", "streams", "789"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["heartrate"] == [120, 125]

    def test_streams_human_mode(self, runner, mock_strava_client):
        with patch(
            "health_data.sources.strava.commands.strava_client.get_streams",
            return_value={"heartrate": [120, 125, 130], "time": [0, 1, 2]},
        ):
            result = runner.invoke(main, ["strava", "streams", "789"])

        assert result.exit_code == 0
        assert "heartrate" in result.output
        assert "3" in result.output  # data points

    def test_streams_custom_types(self, runner, mock_strava_client):
        with patch(
            "health_data.sources.strava.commands.strava_client.get_streams",
            return_value={"heartrate": [120]},
        ) as mock_get:
            result = runner.invoke(
                main, ["--json", "strava", "streams", "789", "--types", "heartrate,watts"]
            )

        assert result.exit_code == 0
        mock_get.assert_called_once_with(
            mock_strava_client, 789, types=["heartrate", "watts"]
        )
