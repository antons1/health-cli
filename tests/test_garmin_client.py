from unittest.mock import MagicMock, patch

import pytest

from health_data.sources.garmin import client as garmin_client


@pytest.fixture
def mock_garmin():
    """A mock Garmin client with all API methods."""
    return MagicMock()


class TestGetStats:
    def test_calls_get_stats(self, mock_garmin):
        mock_garmin.get_stats.return_value = {"steps": 10000}
        result = garmin_client.get_stats(mock_garmin, "2024-03-20")
        mock_garmin.get_stats.assert_called_once_with("2024-03-20")
        assert result == {"steps": 10000}


class TestGetHeartRates:
    def test_calls_get_heart_rates(self, mock_garmin):
        mock_garmin.get_heart_rates.return_value = {"restingHR": 55}
        result = garmin_client.get_heart_rates(mock_garmin, "2024-03-20")
        mock_garmin.get_heart_rates.assert_called_once_with("2024-03-20")
        assert result == {"restingHR": 55}


class TestGetSleep:
    def test_calls_get_sleep_data(self, mock_garmin):
        mock_garmin.get_sleep_data.return_value = {"sleepScore": 85}
        result = garmin_client.get_sleep(mock_garmin, "2024-03-20")
        mock_garmin.get_sleep_data.assert_called_once_with("2024-03-20")
        assert result == {"sleepScore": 85}


class TestGetStress:
    def test_calls_get_stress_data(self, mock_garmin):
        mock_garmin.get_stress_data.return_value = {"avgStress": 30}
        result = garmin_client.get_stress(mock_garmin, "2024-03-20")
        mock_garmin.get_stress_data.assert_called_once_with("2024-03-20")
        assert result == {"avgStress": 30}


class TestGetHrv:
    def test_calls_get_hrv_data(self, mock_garmin):
        mock_garmin.get_hrv_data.return_value = {"weeklyAvg": 45}
        result = garmin_client.get_hrv(mock_garmin, "2024-03-20")
        mock_garmin.get_hrv_data.assert_called_once_with("2024-03-20")
        assert result == {"weeklyAvg": 45}


class TestGetSpo2:
    def test_calls_get_spo2_data(self, mock_garmin):
        mock_garmin.get_spo2_data.return_value = {"avgSpo2": 96}
        result = garmin_client.get_spo2(mock_garmin, "2024-03-20")
        mock_garmin.get_spo2_data.assert_called_once_with("2024-03-20")
        assert result == {"avgSpo2": 96}


class TestGetBodyComposition:
    def test_calls_with_start_only(self, mock_garmin):
        mock_garmin.get_body_composition.return_value = {"weight": 75.0}
        result = garmin_client.get_body_composition(mock_garmin, "2024-03-20")
        mock_garmin.get_body_composition.assert_called_once_with("2024-03-20", None)
        assert result == {"weight": 75.0}

    def test_calls_with_start_and_end(self, mock_garmin):
        mock_garmin.get_body_composition.return_value = {"weight": 75.0}
        result = garmin_client.get_body_composition(mock_garmin, "2024-03-01", "2024-03-20")
        mock_garmin.get_body_composition.assert_called_once_with("2024-03-01", "2024-03-20")


class TestGetActivities:
    def test_calls_with_defaults(self, mock_garmin):
        mock_garmin.get_activities.return_value = [{"name": "Run"}]
        result = garmin_client.get_activities(mock_garmin)
        mock_garmin.get_activities.assert_called_once_with(0, 20)
        assert result == [{"name": "Run"}]

    def test_calls_with_custom_limit(self, mock_garmin):
        mock_garmin.get_activities.return_value = []
        garmin_client.get_activities(mock_garmin, start=10, limit=5)
        mock_garmin.get_activities.assert_called_once_with(10, 5)


class TestGetActivity:
    def test_calls_get_activity(self, mock_garmin):
        mock_garmin.get_activity.return_value = {"activityId": 123}
        result = garmin_client.get_activity(mock_garmin, 123)
        mock_garmin.get_activity.assert_called_once_with(123)
        assert result == {"activityId": 123}


class TestErrorHandling:
    def test_auth_error_exits(self, mock_garmin):
        """Authentication errors exit with code 1."""
        from garminconnect import GarminConnectAuthenticationError
        mock_garmin.get_stats.side_effect = GarminConnectAuthenticationError("expired")
        with pytest.raises(SystemExit) as exc_info:
            garmin_client.get_stats(mock_garmin, "2024-03-20")
        assert exc_info.value.code == 1

    def test_connection_error_exits(self, mock_garmin):
        """Connection errors exit with code 1."""
        from garminconnect import GarminConnectConnectionError
        mock_garmin.get_stats.side_effect = GarminConnectConnectionError("timeout")
        with pytest.raises(SystemExit) as exc_info:
            garmin_client.get_stats(mock_garmin, "2024-03-20")
        assert exc_info.value.code == 1
