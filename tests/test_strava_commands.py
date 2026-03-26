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


SAMPLE_GEAR = {
    "id": "g123",
    "name": "Hoka Mach 6",
    "brand_name": "Hoka",
    "distance": 450000.0,
}


class TestGearCommand:
    def test_gear_json_mode(self, runner, mock_strava_client):
        with patch(
            "health_data.sources.strava.commands.strava_client.get_gear",
            return_value=SAMPLE_GEAR,
        ):
            result = runner.invoke(main, ["--json", "strava", "gear", "g123"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["name"] == "Hoka Mach 6"

    def test_gear_human_mode(self, runner, mock_strava_client):
        with patch(
            "health_data.sources.strava.commands.strava_client.get_gear",
            return_value=SAMPLE_GEAR,
        ):
            result = runner.invoke(main, ["strava", "gear", "g123"])

        assert result.exit_code == 0
        assert "Hoka Mach 6" in result.output


class TestAthleteStatsCommand:
    def test_athlete_stats_json_mode(self, runner, mock_strava_client):
        stats = {"all_run_totals": {"count": 100, "distance": 500000.0}}
        with patch(
            "health_data.sources.strava.commands.strava_client.get_athlete_stats",
            return_value=stats,
        ):
            result = runner.invoke(main, ["--json", "strava", "athlete-stats"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["all_run_totals"]["count"] == 100

    def test_athlete_stats_human_mode(self, runner, mock_strava_client):
        stats = {
            "all_run_totals": {"count": 100, "distance": 500000.0, "moving_time": 180000, "elevation_gain": 5000.0},
        }
        with patch(
            "health_data.sources.strava.commands.strava_client.get_athlete_stats",
            return_value=stats,
        ):
            result = runner.invoke(main, ["strava", "athlete-stats"])

        assert result.exit_code == 0
        assert "100" in result.output


class TestLapsCommand:
    def test_laps_json_mode(self, runner, mock_strava_client):
        laps = [{"name": "Lap 1", "distance": 1000.0, "elapsed_time": 300}]
        with patch(
            "health_data.sources.strava.commands.strava_client.get_laps",
            return_value=laps,
        ):
            result = runner.invoke(main, ["--json", "strava", "laps", "789"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data[0]["name"] == "Lap 1"

    def test_laps_human_mode(self, runner, mock_strava_client):
        laps = [{"name": "Lap 1", "distance": 1000.0, "elapsed_time": 300}]
        with patch(
            "health_data.sources.strava.commands.strava_client.get_laps",
            return_value=laps,
        ):
            result = runner.invoke(main, ["strava", "laps", "789"])

        assert result.exit_code == 0
        assert "Lap 1" in result.output


class TestZonesCommand:
    def test_zones_json_mode(self, runner, mock_strava_client):
        zones = {"heart_rate": {"zones": [{"min": 0, "max": 120}]}}
        with patch(
            "health_data.sources.strava.commands.strava_client.get_zones",
            return_value=zones,
        ):
            result = runner.invoke(main, ["--json", "strava", "zones"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "heart_rate" in data

    def test_zones_human_mode(self, runner, mock_strava_client):
        zones = {"heart_rate": {"zones": [{"min": 0, "max": 120}]}}
        with patch(
            "health_data.sources.strava.commands.strava_client.get_zones",
            return_value=zones,
        ):
            result = runner.invoke(main, ["strava", "zones"])

        assert result.exit_code == 0
        assert "120" in result.output


class TestClubsCommand:
    def test_clubs_json_mode(self, runner, mock_strava_client):
        clubs = [{"id": 1, "name": "Oslo Running Club", "member_count": 150}]
        with patch(
            "health_data.sources.strava.commands.strava_client.get_clubs",
            return_value=clubs,
        ):
            result = runner.invoke(main, ["--json", "strava", "clubs"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data[0]["name"] == "Oslo Running Club"


class TestRoutesCommand:
    def test_routes_json_mode(self, runner, mock_strava_client):
        routes = [{"id": 1, "name": "Loop", "distance": 5000.0}]
        with patch(
            "health_data.sources.strava.commands.strava_client.get_routes",
            return_value=routes,
        ):
            result = runner.invoke(main, ["--json", "strava", "routes"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data[0]["name"] == "Loop"


class TestRouteCommand:
    def test_route_json_mode(self, runner, mock_strava_client):
        route = {"id": 1, "name": "Loop", "distance": 5000.0}
        with patch(
            "health_data.sources.strava.commands.strava_client.get_route",
            return_value=route,
        ):
            result = runner.invoke(main, ["--json", "strava", "route", "1"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["name"] == "Loop"


class TestSegmentCommand:
    def test_segment_json_mode(self, runner, mock_strava_client):
        segment = {"id": 1, "name": "Climb", "distance": 3200.0}
        with patch(
            "health_data.sources.strava.commands.strava_client.get_segment",
            return_value=segment,
        ):
            result = runner.invoke(main, ["--json", "strava", "segment", "1"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["name"] == "Climb"


class TestSegmentsCommand:
    def test_segments_json_mode(self, runner, mock_strava_client):
        segments = [{"id": 1, "name": "Climb"}]
        with patch(
            "health_data.sources.strava.commands.strava_client.explore_segments",
            return_value=segments,
        ):
            result = runner.invoke(
                main,
                ["--json", "strava", "segments", "--bounds", "59.9,10.7,60.0,10.8"],
            )

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data[0]["name"] == "Climb"


class TestCreateActivityCommand:
    def test_create_activity_json(self, runner, mock_strava_client):
        created = {"id": 999, "name": "Morning Run", "sport_type": "Run"}
        with patch(
            "health_data.sources.strava.commands.strava_client.create_activity",
            return_value=created,
        ):
            result = runner.invoke(main, [
                "--json", "strava", "create-activity",
                "--name", "Morning Run",
                "--sport-type", "Run",
                "--start", "2026-03-25T08:00:00",
                "--elapsed-time", "1800",
            ])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["id"] == 999

    def test_create_activity_human(self, runner, mock_strava_client):
        created = {"id": 999, "name": "Morning Run", "sport_type": "Run",
                   "distance": 5000.0, "moving_time": 1800}
        with patch(
            "health_data.sources.strava.commands.strava_client.create_activity",
            return_value=created,
        ):
            result = runner.invoke(main, [
                "strava", "create-activity",
                "--name", "Morning Run",
                "--sport-type", "Run",
                "--start", "2026-03-25T08:00:00",
                "--elapsed-time", "1800",
                "--distance", "5000",
            ])

        assert result.exit_code == 0
        assert "Morning Run" in result.output


class TestUpdateActivityCommand:
    def test_update_activity_json(self, runner, mock_strava_client):
        updated = {"id": 999, "name": "Updated Run"}
        with patch(
            "health_data.sources.strava.commands.strava_client.update_activity",
            return_value=updated,
        ):
            result = runner.invoke(main, [
                "--json", "strava", "update-activity", "999",
                "--name", "Updated Run",
            ])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["name"] == "Updated Run"


class TestUploadCommand:
    def test_upload_json(self, runner, mock_strava_client, tmp_path):
        fit_file = tmp_path / "run.fit"
        fit_file.write_bytes(b"fake data")
        uploaded = {"id": 888, "name": "Uploaded Run"}
        with patch(
            "health_data.sources.strava.commands.strava_client.upload_activity",
            return_value=uploaded,
        ):
            result = runner.invoke(main, [
                "--json", "strava", "upload", str(fit_file),
            ])

        assert result.exit_code == 0
        # Output contains "Uploading..." on stderr mixed in by CliRunner
        assert '"id": 888' in result.output
