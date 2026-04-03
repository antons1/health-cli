from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from health_data.cli import main

TODAY = date.today().isoformat()


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_garmin_client():
    mock = MagicMock()
    with patch("health_data.sources.garmin.commands.get_client", return_value=mock):
        yield mock


SLEEP_DATA = {
    "date": TODAY,
    "score": 72,
    "score_qualifier": "FAIR",
    "total": "7h 12m",
    "deep": "0h 49m",
    "light": "5h 41m",
    "rem": "0h 42m",
    "awake": "0h 43m",
    "avg_stress": 12.0,
    "feedback": "NEGATIVE_LONG_BUT_NOT_ENOUGH_REM",
}

HRV_DATA = {
    "date": TODAY,
    "last_night_avg": 66,
    "weekly_avg": 61,
    "status": "BALANCED",
    "baseline_low": 50,
    "baseline_high": 72,
}

STRESS_DATA = {"date": TODAY, "avg": 26, "max": 96}

BODY_BATTERY_DATA = {"date": TODAY, "charged": 76, "drained": 76, "peak": 97, "end": 21}

RHR_DATA = {"date": TODAY, "rhr": 51}


class TestGarminGroup:
    def test_garmin_group_exists(self, runner):
        result = runner.invoke(main, ["garmin", "--help"])
        assert result.exit_code == 0
        assert "Garmin" in result.output

    def test_shows_subcommands(self, runner):
        result = runner.invoke(main, ["garmin", "--help"])
        for cmd in ("login", "sleep", "hrv", "stress", "body-battery", "rhr"):
            assert cmd in result.output


class TestLoginCommand:
    def test_login_calls_do_login(self, runner):
        with patch("health_data.sources.garmin.commands.do_login") as mock_login:
            mock_login.return_value = MagicMock()
            result = runner.invoke(
                main,
                ["garmin", "login"],
                input="user@example.com\nsecret\n",
            )
        assert result.exit_code == 0
        mock_login.assert_called_once_with("user@example.com", "secret")

    def test_login_prints_success(self, runner):
        with patch("health_data.sources.garmin.commands.do_login") as mock_login:
            mock_login.return_value = MagicMock()
            result = runner.invoke(
                main,
                ["garmin", "login"],
                input="user@example.com\nsecret\n",
            )
        assert "success" in result.output.lower()


class TestSleepCommand:
    def test_defaults_to_today(self, runner, mock_garmin_client):
        with patch("health_data.sources.garmin.commands.get_sleep", return_value=SLEEP_DATA) as mock:
            runner.invoke(main, ["garmin", "sleep"])
        mock.assert_called_once_with(mock_garmin_client, TODAY)

    def test_accepts_date_argument(self, runner, mock_garmin_client):
        with patch("health_data.sources.garmin.commands.get_sleep", return_value=SLEEP_DATA) as mock:
            runner.invoke(main, ["garmin", "sleep", "2026-04-01"])
        mock.assert_called_once_with(mock_garmin_client, "2026-04-01")

    def test_output_contains_score(self, runner, mock_garmin_client):
        with patch("health_data.sources.garmin.commands.get_sleep", return_value=SLEEP_DATA):
            result = runner.invoke(main, ["garmin", "sleep"])
        assert "72" in result.output

    def test_output_contains_stages(self, runner, mock_garmin_client):
        with patch("health_data.sources.garmin.commands.get_sleep", return_value=SLEEP_DATA):
            result = runner.invoke(main, ["garmin", "sleep"])
        assert "7h 12m" in result.output
        assert "0h 49m" in result.output

    def test_json_flag_outputs_raw_data(self, runner, mock_garmin_client):
        with patch("health_data.sources.garmin.commands.get_sleep", return_value=SLEEP_DATA):
            result = runner.invoke(main, ["--json", "garmin", "sleep"])
        import json
        data = json.loads(result.output)
        assert data["score"] == 72


class TestHrvCommand:
    def test_defaults_to_today(self, runner, mock_garmin_client):
        with patch("health_data.sources.garmin.commands.get_hrv", return_value=HRV_DATA) as mock:
            runner.invoke(main, ["garmin", "hrv"])
        mock.assert_called_once_with(mock_garmin_client, TODAY)

    def test_output_contains_last_night_avg(self, runner, mock_garmin_client):
        with patch("health_data.sources.garmin.commands.get_hrv", return_value=HRV_DATA):
            result = runner.invoke(main, ["garmin", "hrv"])
        assert "66" in result.output

    def test_output_contains_status(self, runner, mock_garmin_client):
        with patch("health_data.sources.garmin.commands.get_hrv", return_value=HRV_DATA):
            result = runner.invoke(main, ["garmin", "hrv"])
        assert "Balanced" in result.output or "BALANCED" in result.output


class TestStressCommand:
    def test_defaults_to_today(self, runner, mock_garmin_client):
        with patch("health_data.sources.garmin.commands.get_stress", return_value=STRESS_DATA) as mock:
            runner.invoke(main, ["garmin", "stress"])
        mock.assert_called_once_with(mock_garmin_client, TODAY)

    def test_output_contains_avg(self, runner, mock_garmin_client):
        with patch("health_data.sources.garmin.commands.get_stress", return_value=STRESS_DATA):
            result = runner.invoke(main, ["garmin", "stress"])
        assert "26" in result.output

    def test_output_contains_max(self, runner, mock_garmin_client):
        with patch("health_data.sources.garmin.commands.get_stress", return_value=STRESS_DATA):
            result = runner.invoke(main, ["garmin", "stress"])
        assert "96" in result.output


class TestBodyBatteryCommand:
    def test_defaults_to_today(self, runner, mock_garmin_client):
        with patch("health_data.sources.garmin.commands.get_body_battery", return_value=BODY_BATTERY_DATA) as mock:
            runner.invoke(main, ["garmin", "body-battery"])
        mock.assert_called_once_with(mock_garmin_client, TODAY)

    def test_output_contains_peak(self, runner, mock_garmin_client):
        with patch("health_data.sources.garmin.commands.get_body_battery", return_value=BODY_BATTERY_DATA):
            result = runner.invoke(main, ["garmin", "body-battery"])
        assert "97" in result.output

    def test_output_contains_end(self, runner, mock_garmin_client):
        with patch("health_data.sources.garmin.commands.get_body_battery", return_value=BODY_BATTERY_DATA):
            result = runner.invoke(main, ["garmin", "body-battery"])
        assert "21" in result.output


class TestRhrCommand:
    def test_defaults_to_today(self, runner, mock_garmin_client):
        with patch("health_data.sources.garmin.commands.get_rhr", return_value=RHR_DATA) as mock:
            runner.invoke(main, ["garmin", "rhr"])
        mock.assert_called_once_with(mock_garmin_client, TODAY)

    def test_output_contains_rhr(self, runner, mock_garmin_client):
        with patch("health_data.sources.garmin.commands.get_rhr", return_value=RHR_DATA):
            result = runner.invoke(main, ["garmin", "rhr"])
        assert "51" in result.output


RESPIRATION_DATA = {"date": TODAY, "avg_sleep": 13.0, "avg_waking": 15.0, "low": 9.0, "high": 18.0}
VO2MAX_DATA = {"date": TODAY, "vo2max": 43.0, "vo2max_precise": 43.3}
WEIGHT_DATA = {"date": TODAY, "weight_kg": 92.1}
STEPS_DATA = {"date": TODAY, "steps": 12829, "distance_km": 11.4, "goal": 8830}
INTENSITY_MINUTES_DATA = {"date": TODAY, "moderate": 12, "vigorous": 40, "weekly_total": 304, "weekly_goal": 150}
CALORIES_DATA = {"date": TODAY, "total": 3018, "active": 692, "bmr": 2326}
RACE_PREDICTIONS_DATA = {"date": TODAY, "5k": "27:14", "10k": "59:24", "half_marathon": "2:17:17", "marathon": "5:09:36"}


class TestRespirationCommand:
    def test_defaults_to_today(self, runner, mock_garmin_client):
        with patch("health_data.sources.garmin.commands.get_respiration", return_value=RESPIRATION_DATA) as mock:
            runner.invoke(main, ["garmin", "respiration"])
        mock.assert_called_once_with(mock_garmin_client, TODAY)

    def test_output_contains_avg_sleep(self, runner, mock_garmin_client):
        with patch("health_data.sources.garmin.commands.get_respiration", return_value=RESPIRATION_DATA):
            result = runner.invoke(main, ["garmin", "respiration"])
        assert "13.0" in result.output


class TestVo2maxCommand:
    def test_defaults_to_today(self, runner, mock_garmin_client):
        with patch("health_data.sources.garmin.commands.get_vo2max", return_value=VO2MAX_DATA) as mock:
            runner.invoke(main, ["garmin", "vo2max"])
        mock.assert_called_once_with(mock_garmin_client, TODAY)

    def test_output_contains_value(self, runner, mock_garmin_client):
        with patch("health_data.sources.garmin.commands.get_vo2max", return_value=VO2MAX_DATA):
            result = runner.invoke(main, ["garmin", "vo2max"])
        assert "43.0" in result.output


class TestWeightCommand:
    def test_defaults_to_today(self, runner, mock_garmin_client):
        with patch("health_data.sources.garmin.commands.get_weight", return_value=WEIGHT_DATA) as mock:
            runner.invoke(main, ["garmin", "weight"])
        mock.assert_called_once_with(mock_garmin_client, TODAY)

    def test_output_contains_weight(self, runner, mock_garmin_client):
        with patch("health_data.sources.garmin.commands.get_weight", return_value=WEIGHT_DATA):
            result = runner.invoke(main, ["garmin", "weight"])
        assert "92.1" in result.output


class TestStepsCommand:
    def test_defaults_to_today(self, runner, mock_garmin_client):
        with patch("health_data.sources.garmin.commands.get_steps", return_value=STEPS_DATA) as mock:
            runner.invoke(main, ["garmin", "steps"])
        mock.assert_called_once_with(mock_garmin_client, TODAY)

    def test_output_contains_steps_and_goal(self, runner, mock_garmin_client):
        with patch("health_data.sources.garmin.commands.get_steps", return_value=STEPS_DATA):
            result = runner.invoke(main, ["garmin", "steps"])
        assert "12829" in result.output
        assert "8830" in result.output


class TestIntensityMinutesCommand:
    def test_defaults_to_today(self, runner, mock_garmin_client):
        with patch("health_data.sources.garmin.commands.get_intensity_minutes", return_value=INTENSITY_MINUTES_DATA) as mock:
            runner.invoke(main, ["garmin", "intensity-minutes"])
        mock.assert_called_once_with(mock_garmin_client, TODAY)

    def test_output_contains_daily_and_weekly(self, runner, mock_garmin_client):
        with patch("health_data.sources.garmin.commands.get_intensity_minutes", return_value=INTENSITY_MINUTES_DATA):
            result = runner.invoke(main, ["garmin", "intensity-minutes"])
        assert "40" in result.output   # vigorous
        assert "304" in result.output  # weekly total


class TestCaloriesCommand:
    def test_defaults_to_today(self, runner, mock_garmin_client):
        with patch("health_data.sources.garmin.commands.get_calories", return_value=CALORIES_DATA) as mock:
            runner.invoke(main, ["garmin", "calories"])
        mock.assert_called_once_with(mock_garmin_client, TODAY)

    def test_output_contains_total_and_bmr(self, runner, mock_garmin_client):
        with patch("health_data.sources.garmin.commands.get_calories", return_value=CALORIES_DATA):
            result = runner.invoke(main, ["garmin", "calories"])
        assert "3018" in result.output
        assert "2326" in result.output


class TestRacePredictionsCommand:
    def test_no_date_argument(self, runner, mock_garmin_client):
        with patch("health_data.sources.garmin.commands.get_race_predictions", return_value=RACE_PREDICTIONS_DATA) as mock:
            runner.invoke(main, ["garmin", "race-predictions"])
        mock.assert_called_once_with(mock_garmin_client)

    def test_output_contains_times(self, runner, mock_garmin_client):
        with patch("health_data.sources.garmin.commands.get_race_predictions", return_value=RACE_PREDICTIONS_DATA):
            result = runner.invoke(main, ["garmin", "race-predictions"])
        assert "27:14" in result.output
        assert "5:09:36" in result.output
