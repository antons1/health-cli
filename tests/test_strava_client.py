from unittest.mock import MagicMock, patch

import pytest

from health_data.sources.strava import client as strava_client


@pytest.fixture
def mock_client():
    return MagicMock()


class TestGetActivities:
    def test_returns_list_of_dicts(self, mock_client):
        """get_activities() converts Activity objects to dicts."""
        mock_activity = MagicMock()
        mock_activity.model_dump.return_value = {
            "id": 123,
            "name": "Morning Run",
            "distance": 10000.0,
            "moving_time": 3600,
        }
        mock_client.get_activities.return_value = iter([mock_activity])

        result = strava_client.get_activities(mock_client, limit=10)

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["name"] == "Morning Run"
        mock_client.get_activities.assert_called_once_with(limit=10)

    def test_excludes_bound_client_and_none(self, mock_client):
        """model_dump excludes bound_client and None fields."""
        mock_activity = MagicMock()
        mock_activity.model_dump.return_value = {"id": 1, "name": "Run"}
        mock_client.get_activities.return_value = iter([mock_activity])

        strava_client.get_activities(mock_client, limit=5)

        mock_activity.model_dump.assert_called_once_with(
            exclude={"bound_client"}, exclude_none=True
        )

    def test_default_limit(self, mock_client):
        """Default limit is 20."""
        mock_client.get_activities.return_value = iter([])
        strava_client.get_activities(mock_client)
        mock_client.get_activities.assert_called_once_with(limit=20)


class TestGetActivity:
    def test_returns_dict(self, mock_client):
        """get_activity() converts DetailedActivity to dict."""
        mock_activity = MagicMock()
        mock_activity.model_dump.return_value = {
            "id": 456,
            "name": "Afternoon Ride",
            "distance": 50000.0,
        }
        mock_client.get_activity.return_value = mock_activity

        result = strava_client.get_activity(mock_client, 456)

        assert result["id"] == 456
        assert result["name"] == "Afternoon Ride"
        mock_client.get_activity.assert_called_once_with(456)


class TestGetStreams:
    def test_returns_dict_of_data_lists(self, mock_client):
        """get_streams() extracts .data from each Stream object."""
        mock_hr_stream = MagicMock()
        mock_hr_stream.data = [120, 125, 130, 128]

        mock_time_stream = MagicMock()
        mock_time_stream.data = [0, 1, 2, 3]

        mock_client.get_activity_streams.return_value = {
            "heartrate": mock_hr_stream,
            "time": mock_time_stream,
        }

        result = strava_client.get_streams(mock_client, 789)

        assert result["heartrate"] == [120, 125, 130, 128]
        assert result["time"] == [0, 1, 2, 3]

    def test_default_stream_types(self, mock_client):
        """Default stream types include common fitness metrics."""
        mock_client.get_activity_streams.return_value = {}
        strava_client.get_streams(mock_client, 789)

        call_args = mock_client.get_activity_streams.call_args
        assert call_args[0][0] == 789  # activity_id
        types = call_args[1]["types"]
        assert "heartrate" in types
        assert "time" in types
        assert "latlng" in types

    def test_custom_stream_types(self, mock_client):
        """Can specify which stream types to fetch."""
        mock_client.get_activity_streams.return_value = {}
        strava_client.get_streams(mock_client, 789, types=["heartrate", "watts"])

        call_args = mock_client.get_activity_streams.call_args
        assert call_args[1]["types"] == ["heartrate", "watts"]

    def test_empty_streams(self, mock_client):
        """Returns empty dict when no streams available."""
        mock_client.get_activity_streams.return_value = {}
        result = strava_client.get_streams(mock_client, 789)
        assert result == {}


class TestGetGear:
    def test_returns_dict(self, mock_client):
        mock_gear = MagicMock()
        mock_gear.model_dump.return_value = {
            "id": "g123",
            "name": "Hoka Mach 6",
            "distance": 450000.0,
        }
        mock_client.get_gear.return_value = mock_gear

        result = strava_client.get_gear(mock_client, "g123")

        assert result["name"] == "Hoka Mach 6"
        mock_client.get_gear.assert_called_once_with("g123")


class TestGetAthleteStats:
    def test_returns_dict(self, mock_client):
        mock_stats = MagicMock()
        mock_stats.model_dump.return_value = {
            "all_run_totals": {"count": 100, "distance": 500000.0},
        }
        mock_client.get_athlete.return_value = MagicMock(id=12345)
        mock_client.get_athlete_stats.return_value = mock_stats

        result = strava_client.get_athlete_stats(mock_client)

        assert result["all_run_totals"]["count"] == 100
        mock_client.get_athlete_stats.assert_called_once_with(12345)


class TestGetLaps:
    def test_returns_list_of_dicts(self, mock_client):
        mock_lap = MagicMock()
        mock_lap.model_dump.return_value = {
            "name": "Lap 1",
            "distance": 1000.0,
            "elapsed_time": 300,
        }
        mock_client.get_activity_laps.return_value = [mock_lap]

        result = strava_client.get_laps(mock_client, 789)

        assert len(result) == 1
        assert result[0]["name"] == "Lap 1"
        mock_client.get_activity_laps.assert_called_once_with(789)


class TestGetZones:
    def test_returns_dict(self, mock_client):
        mock_zones = MagicMock()
        mock_zones.model_dump.return_value = {
            "heart_rate": {"zones": [{"min": 0, "max": 120}]},
        }
        mock_client.get_athlete_zones.return_value = mock_zones

        result = strava_client.get_zones(mock_client)

        assert "heart_rate" in result


class TestGetClubs:
    def test_returns_list_of_dicts(self, mock_client):
        mock_club = MagicMock()
        mock_club.model_dump.return_value = {
            "id": 1,
            "name": "Oslo Running Club",
            "member_count": 150,
        }
        mock_client.get_athlete_clubs.return_value = [mock_club]

        result = strava_client.get_clubs(mock_client)

        assert len(result) == 1
        assert result[0]["name"] == "Oslo Running Club"


class TestGetRoutes:
    def test_returns_list_of_dicts(self, mock_client):
        mock_route = MagicMock()
        mock_route.model_dump.return_value = {
            "id": 1,
            "name": "Frognerparken Loop",
            "distance": 5000.0,
        }
        mock_client.get_routes.return_value = iter([mock_route])

        result = strava_client.get_routes(mock_client)

        assert len(result) == 1
        assert result[0]["name"] == "Frognerparken Loop"


class TestGetRoute:
    def test_returns_dict(self, mock_client):
        mock_route = MagicMock()
        mock_route.model_dump.return_value = {
            "id": 1,
            "name": "Frognerparken Loop",
            "distance": 5000.0,
        }
        mock_client.get_route.return_value = mock_route

        result = strava_client.get_route(mock_client, 1)

        assert result["name"] == "Frognerparken Loop"
        mock_client.get_route.assert_called_once_with(1)


class TestGetSegment:
    def test_returns_dict(self, mock_client):
        mock_segment = MagicMock()
        mock_segment.model_dump.return_value = {
            "id": 1,
            "name": "Holmenkollen Climb",
            "distance": 3200.0,
        }
        mock_client.get_segment.return_value = mock_segment

        result = strava_client.get_segment(mock_client, 1)

        assert result["name"] == "Holmenkollen Climb"
        mock_client.get_segment.assert_called_once_with(1)


class TestExploreSegments:
    def test_returns_list_of_dicts(self, mock_client):
        mock_segment = MagicMock()
        mock_segment.model_dump.return_value = {
            "id": 1,
            "name": "Holmenkollen Climb",
        }
        mock_result = MagicMock()
        mock_result.segments = [mock_segment]
        mock_client.explore_segments.return_value = mock_result

        result = strava_client.explore_segments(
            mock_client, (59.9, 10.7, 60.0, 10.8)
        )

        assert len(result) == 1
        assert result[0]["name"] == "Holmenkollen Climb"


class TestCreateActivity:
    def test_creates_and_returns_dict(self, mock_client):
        mock_activity = MagicMock()
        mock_activity.model_dump.return_value = {
            "id": 999,
            "name": "Morning Run",
        }
        mock_client.create_activity.return_value = mock_activity

        from datetime import datetime
        result = strava_client.create_activity(
            mock_client,
            name="Morning Run",
            sport_type="Run",
            start_date=datetime(2026, 3, 25, 8, 0),
            elapsed_time=1800,
            distance=5000.0,
            description="Easy run",
        )

        assert result["id"] == 999
        mock_client.create_activity.assert_called_once_with(
            name="Morning Run",
            sport_type="Run",
            start_date_local=datetime(2026, 3, 25, 8, 0),
            elapsed_time=1800,
            distance=5000.0,
            description="Easy run",
        )


class TestUpdateActivity:
    def test_updates_and_returns_dict(self, mock_client):
        mock_activity = MagicMock()
        mock_activity.model_dump.return_value = {
            "id": 999,
            "name": "Updated Run",
        }
        mock_client.update_activity.return_value = mock_activity

        result = strava_client.update_activity(
            mock_client, 999, name="Updated Run", gear_id="g123"
        )

        assert result["name"] == "Updated Run"
        mock_client.update_activity.assert_called_once_with(
            999, name="Updated Run", gear_id="g123"
        )


class TestUploadActivity:
    def test_uploads_and_returns_dict(self, mock_client, tmp_path):
        fit_file = tmp_path / "activity.fit"
        fit_file.write_bytes(b"fake fit data")

        mock_upload = MagicMock()
        mock_upload.wait.return_value = MagicMock(
            model_dump=MagicMock(return_value={"id": 888, "name": "Uploaded"})
        )
        mock_client.upload_activity.return_value = mock_upload

        result = strava_client.upload_activity(
            mock_client, str(fit_file), data_type="fit"
        )

        assert result["id"] == 888
        mock_client.upload_activity.assert_called_once()
