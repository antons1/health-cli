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
