from datetime import date
from unittest.mock import MagicMock, patch, call

import pytest

from health_data.sources.garmin.client import (
    get_sleep,
    get_hrv,
    get_stress,
    get_body_battery,
    get_rhr,
    get_respiration,
    get_vo2max,
    get_weight,
    get_steps,
    get_intensity_minutes,
    get_calories,
    get_race_predictions,
)

DATE = "2026-04-02"
TODAY = date.today().isoformat()


SLEEP_RESPONSE = {
    "dailySleepDTO": {
        "calendarDate": DATE,
        "sleepTimeSeconds": 25920,
        "deepSleepSeconds": 2940,
        "lightSleepSeconds": 20460,
        "remSleepSeconds": 2520,
        "awakeSleepSeconds": 2580,
        "avgSleepStress": 12.0,
        "sleepScoreFeedback": "NEGATIVE_LONG_BUT_NOT_ENOUGH_REM",
        "sleepScores": {
            "overall": {"value": 72, "qualifierKey": "FAIR"},
        },
    }
}

HRV_RESPONSE = {
    "hrvSummary": {
        "calendarDate": DATE,
        "weeklyAvg": 61,
        "lastNightAvg": 66,
        "status": "BALANCED",
        "baseline": {"balancedLow": 50, "balancedUpper": 72},
    },
}

STRESS_RESPONSE = {
    "calendarDate": DATE,
    "avgStressLevel": 26,
    "maxStressLevel": 96,
}

BODY_BATTERY_RESPONSE = [
    {
        "date": DATE,
        "charged": 76,
        "drained": 76,
        "bodyBatteryValuesArray": [
            [1775080800000, 28],
            [1775109060000, 93],
            [1775112120000, 97],
            [1775138220000, 45],
            [1775158560000, 21],
        ],
    }
]

RHR_RESPONSE = {
    "allMetrics": {
        "metricsMap": {
            "WELLNESS_RESTING_HEART_RATE": [{"value": 51.0, "calendarDate": DATE}]
        }
    }
}


@pytest.fixture(autouse=True)
def no_cache(tmp_path):
    """Redirect cache to tmp_path for all tests."""
    with patch("health_data.sources.garmin.client.read_cache", return_value=None), \
         patch("health_data.sources.garmin.client.write_cache"):
        yield


class TestGetSleep:
    def setup_method(self):
        self.client = MagicMock()
        self.client.get_sleep_data.return_value = SLEEP_RESPONSE

    def test_returns_score(self):
        assert get_sleep(self.client, DATE)["score"] == 72

    def test_returns_qualifier(self):
        assert get_sleep(self.client, DATE)["score_qualifier"] == "FAIR"

    def test_returns_total_sleep_as_hours_minutes(self):
        assert get_sleep(self.client, DATE)["total"] == "7h 12m"

    def test_returns_sleep_stages(self):
        result = get_sleep(self.client, DATE)
        assert result["deep"] == "0h 49m"
        assert result["light"] == "5h 41m"
        assert result["rem"] == "0h 42m"
        assert result["awake"] == "0h 43m"

    def test_returns_avg_stress(self):
        assert get_sleep(self.client, DATE)["avg_stress"] == 12.0

    def test_returns_feedback(self):
        assert get_sleep(self.client, DATE)["feedback"] == "NEGATIVE_LONG_BUT_NOT_ENOUGH_REM"

    def test_calls_correct_endpoint(self):
        get_sleep(self.client, DATE)
        self.client.get_sleep_data.assert_called_once_with(DATE)


class TestGetHrv:
    def setup_method(self):
        self.client = MagicMock()
        self.client.get_hrv_data.return_value = HRV_RESPONSE

    def test_returns_last_night_avg(self):
        assert get_hrv(self.client, DATE)["last_night_avg"] == 66

    def test_returns_weekly_avg(self):
        assert get_hrv(self.client, DATE)["weekly_avg"] == 61

    def test_returns_status(self):
        assert get_hrv(self.client, DATE)["status"] == "BALANCED"

    def test_returns_baseline(self):
        result = get_hrv(self.client, DATE)
        assert result["baseline_low"] == 50
        assert result["baseline_high"] == 72

    def test_calls_correct_endpoint(self):
        get_hrv(self.client, DATE)
        self.client.get_hrv_data.assert_called_once_with(DATE)


class TestGetStress:
    def setup_method(self):
        self.client = MagicMock()
        self.client.get_stress_data.return_value = STRESS_RESPONSE

    def test_returns_avg_stress(self):
        assert get_stress(self.client, DATE)["avg"] == 26

    def test_returns_max_stress(self):
        assert get_stress(self.client, DATE)["max"] == 96

    def test_calls_correct_endpoint(self):
        get_stress(self.client, DATE)
        self.client.get_stress_data.assert_called_once_with(DATE)


class TestGetBodyBattery:
    def setup_method(self):
        self.client = MagicMock()
        self.client.get_body_battery.return_value = BODY_BATTERY_RESPONSE

    def test_returns_charged_and_drained(self):
        result = get_body_battery(self.client, DATE)
        assert result["charged"] == 76
        assert result["drained"] == 76

    def test_returns_peak(self):
        assert get_body_battery(self.client, DATE)["peak"] == 97

    def test_returns_end_of_day(self):
        assert get_body_battery(self.client, DATE)["end"] == 21

    def test_calls_correct_endpoint(self):
        get_body_battery(self.client, DATE)
        self.client.get_body_battery.assert_called_once_with(DATE, DATE)

    def test_handles_empty_response(self):
        self.client.get_body_battery.return_value = []
        result = get_body_battery(self.client, DATE)
        assert result["peak"] is None
        assert result["end"] is None


class TestGetRhr:
    def setup_method(self):
        self.client = MagicMock()
        self.client.get_rhr_day.return_value = RHR_RESPONSE

    def test_returns_rhr(self):
        assert get_rhr(self.client, DATE)["rhr"] == 51

    def test_returns_int_not_float(self):
        assert isinstance(get_rhr(self.client, DATE)["rhr"], int)

    def test_calls_correct_endpoint(self):
        get_rhr(self.client, DATE)
        self.client.get_rhr_day.assert_called_once_with(DATE)

    def test_handles_missing_rhr(self):
        self.client.get_rhr_day.return_value = {"allMetrics": {"metricsMap": {}}}
        assert get_rhr(self.client, DATE)["rhr"] is None


class TestCaching:
    def test_returns_cached_value_without_calling_api(self):
        garmin = MagicMock()
        cached_data = {"date": DATE, "score": 80}
        with patch("health_data.sources.garmin.client.read_cache", return_value=cached_data):
            result = get_sleep(garmin, DATE)
        garmin.get_sleep_data.assert_not_called()
        assert result == cached_data

    def test_writes_result_to_cache_on_api_call(self):
        garmin = MagicMock()
        garmin.get_sleep_data.return_value = SLEEP_RESPONSE
        with patch("health_data.sources.garmin.client.read_cache", return_value=None), \
             patch("health_data.sources.garmin.client.write_cache") as mock_write:
            get_sleep(garmin, DATE)
        mock_write.assert_called_once()
        args = mock_write.call_args[0]
        assert args[0] == "sleep"
        assert args[1] == DATE

    def test_past_date_uses_no_ttl(self):
        garmin = MagicMock()
        garmin.get_sleep_data.return_value = SLEEP_RESPONSE
        with patch("health_data.sources.garmin.client.read_cache", return_value=None) as mock_read, \
             patch("health_data.sources.garmin.client.write_cache"):
            get_sleep(garmin, "2020-01-01")
        # ttl=None for past dates
        assert mock_read.call_args[0][2] is None

    def test_today_static_metric_uses_static_ttl(self):
        from health_data.sources.garmin.cache import STATIC_TTL
        garmin = MagicMock()
        garmin.get_sleep_data.return_value = SLEEP_RESPONSE
        with patch("health_data.sources.garmin.client.read_cache", return_value=None) as mock_read, \
             patch("health_data.sources.garmin.client.write_cache"):
            get_sleep(garmin, TODAY)
        assert mock_read.call_args[0][2] == STATIC_TTL

    def test_today_dynamic_metric_uses_dynamic_ttl(self):
        from health_data.sources.garmin.cache import DYNAMIC_TTL
        garmin = MagicMock()
        garmin.get_stress_data.return_value = STRESS_RESPONSE
        with patch("health_data.sources.garmin.client.read_cache", return_value=None) as mock_read, \
             patch("health_data.sources.garmin.client.write_cache"):
            get_stress(garmin, TODAY)
        assert mock_read.call_args[0][2] == DYNAMIC_TTL


RESPIRATION_RESPONSE = {
    "calendarDate": DATE,
    "avgSleepRespirationValue": 13.0,
    "avgWakingRespirationValue": 15.0,
    "lowestRespirationValue": 9.0,
    "highestRespirationValue": 18.0,
}

VO2MAX_RESPONSE = [
    {
        "generic": {
            "calendarDate": DATE,
            "vo2MaxValue": 43.0,
            "vo2MaxPreciseValue": 43.3,
        }
    }
]

WEIGHT_RESPONSE_WITH_ENTRY = {
    "dailyWeightSummaries": [
        {
            "summaryDate": DATE,
            "latestWeight": {"calendarDate": DATE, "weight": 92100.0, "sourceType": "MANUAL"},
        }
    ],
    "previousDateWeight": None,
}

WEIGHT_RESPONSE_NO_ENTRY = {
    "dailyWeightSummaries": [],
    "previousDateWeight": {
        "calendarDate": "2026-04-01",
        "weight": 92098.0,
        "sourceType": "MANUAL",
    },
}

STEPS_RESPONSE = [
    {"calendarDate": DATE, "totalSteps": 12829, "totalDistance": 11379, "stepGoal": 8830}
]

INTENSITY_MINUTES_RESPONSE = {
    "calendarDate": DATE,
    "moderateMinutes": 12,
    "vigorousMinutes": 40,
    "weeklyModerate": 102,
    "weeklyVigorous": 101,
    "weeklyTotal": 304,
    "weekGoal": 150,
}

STATS_RESPONSE = {
    "calendarDate": DATE,
    "totalKilocalories": 3018.0,
    "activeKilocalories": 692.0,
    "bmrKilocalories": 2326.0,
}

RACE_PREDICTIONS_RESPONSE = {
    "calendarDate": DATE,
    "time5K": 1634,
    "time10K": 3564,
    "timeHalfMarathon": 8237,
    "timeMarathon": 18576,
}


class TestGetRespiration:
    def setup_method(self):
        self.client = MagicMock()
        self.client.get_respiration_data.return_value = RESPIRATION_RESPONSE

    def test_returns_avg_sleep(self):
        assert get_respiration(self.client, DATE)["avg_sleep"] == 13.0

    def test_returns_avg_waking(self):
        assert get_respiration(self.client, DATE)["avg_waking"] == 15.0

    def test_returns_low_and_high(self):
        result = get_respiration(self.client, DATE)
        assert result["low"] == 9.0
        assert result["high"] == 18.0

    def test_calls_correct_endpoint(self):
        get_respiration(self.client, DATE)
        self.client.get_respiration_data.assert_called_once_with(DATE)


class TestGetVo2max:
    def setup_method(self):
        self.client = MagicMock()
        self.client.get_max_metrics.return_value = VO2MAX_RESPONSE

    def test_returns_vo2max(self):
        assert get_vo2max(self.client, DATE)["vo2max"] == 43.0

    def test_returns_precise_value(self):
        assert get_vo2max(self.client, DATE)["vo2max_precise"] == 43.3

    def test_returns_date(self):
        assert get_vo2max(self.client, DATE)["date"] == DATE

    def test_handles_empty_response(self):
        self.client.get_max_metrics.return_value = []
        result = get_vo2max(self.client, DATE)
        assert result["vo2max"] is None

    def test_calls_correct_endpoint(self):
        get_vo2max(self.client, DATE)
        self.client.get_max_metrics.assert_called_once_with(DATE)


class TestGetWeight:
    def setup_method(self):
        self.client = MagicMock()

    def test_returns_weight_from_daily_summary(self):
        self.client.get_weigh_ins.return_value = WEIGHT_RESPONSE_WITH_ENTRY
        result = get_weight(self.client, DATE)
        assert result["weight_kg"] == 92.1

    def test_falls_back_to_previous_date_when_no_entry_today(self):
        self.client.get_weigh_ins.return_value = WEIGHT_RESPONSE_NO_ENTRY
        result = get_weight(self.client, DATE)
        assert result["weight_kg"] == 92.1
        assert result["date"] == "2026-04-01"

    def test_converts_grams_to_kg(self):
        self.client.get_weigh_ins.return_value = WEIGHT_RESPONSE_WITH_ENTRY
        result = get_weight(self.client, DATE)
        assert isinstance(result["weight_kg"], float)

    def test_handles_no_weight_data(self):
        self.client.get_weigh_ins.return_value = {
            "dailyWeightSummaries": [],
            "previousDateWeight": None,
        }
        result = get_weight(self.client, DATE)
        assert result["weight_kg"] is None

    def test_does_not_cache_null_result(self):
        self.client.get_weigh_ins.return_value = {
            "dailyWeightSummaries": [],
            "previousDateWeight": None,
        }
        with patch("health_data.sources.garmin.client.read_cache", return_value=None), \
             patch("health_data.sources.garmin.client.write_cache") as mock_write:
            get_weight(self.client, DATE)
        mock_write.assert_not_called()

    def test_calls_correct_endpoint(self):
        self.client.get_weigh_ins.return_value = WEIGHT_RESPONSE_WITH_ENTRY
        get_weight(self.client, DATE)
        self.client.get_weigh_ins.assert_called_once_with(DATE, DATE)


class TestGetSteps:
    def setup_method(self):
        self.client = MagicMock()
        self.client.get_daily_steps.return_value = STEPS_RESPONSE

    def test_returns_steps(self):
        assert get_steps(self.client, DATE)["steps"] == 12829

    def test_returns_distance_in_km(self):
        assert get_steps(self.client, DATE)["distance_km"] == 11.4

    def test_returns_goal(self):
        assert get_steps(self.client, DATE)["goal"] == 8830

    def test_handles_empty_response(self):
        self.client.get_daily_steps.return_value = []
        result = get_steps(self.client, DATE)
        assert result["steps"] is None

    def test_calls_correct_endpoint(self):
        get_steps(self.client, DATE)
        self.client.get_daily_steps.assert_called_once_with(DATE, DATE)


class TestGetIntensityMinutes:
    def setup_method(self):
        self.client = MagicMock()
        self.client.get_intensity_minutes_data.return_value = INTENSITY_MINUTES_RESPONSE

    def test_returns_daily_minutes(self):
        result = get_intensity_minutes(self.client, DATE)
        assert result["moderate"] == 12
        assert result["vigorous"] == 40

    def test_returns_weekly_totals(self):
        result = get_intensity_minutes(self.client, DATE)
        assert result["weekly_total"] == 304
        assert result["weekly_goal"] == 150

    def test_calls_correct_endpoint(self):
        get_intensity_minutes(self.client, DATE)
        self.client.get_intensity_minutes_data.assert_called_once_with(DATE)


class TestGetCalories:
    def setup_method(self):
        self.client = MagicMock()
        self.client.get_stats.return_value = STATS_RESPONSE

    def test_returns_total_calories(self):
        assert get_calories(self.client, DATE)["total"] == 3018

    def test_returns_active_calories(self):
        assert get_calories(self.client, DATE)["active"] == 692

    def test_returns_bmr(self):
        assert get_calories(self.client, DATE)["bmr"] == 2326

    def test_returns_integers(self):
        result = get_calories(self.client, DATE)
        assert isinstance(result["total"], int)
        assert isinstance(result["active"], int)
        assert isinstance(result["bmr"], int)

    def test_calls_correct_endpoint(self):
        get_calories(self.client, DATE)
        self.client.get_stats.assert_called_once_with(DATE)


class TestGetRacePredictions:
    def setup_method(self):
        self.client = MagicMock()
        self.client.get_race_predictions.return_value = RACE_PREDICTIONS_RESPONSE

    def test_returns_formatted_5k(self):
        assert get_race_predictions(self.client)["5k"] == "27:14"

    def test_returns_formatted_10k(self):
        assert get_race_predictions(self.client)["10k"] == "59:24"

    def test_returns_formatted_half_marathon(self):
        assert get_race_predictions(self.client)["half_marathon"] == "2:17:17"

    def test_returns_formatted_marathon(self):
        assert get_race_predictions(self.client)["marathon"] == "5:09:36"

    def test_calls_correct_endpoint(self):
        get_race_predictions(self.client)
        self.client.get_race_predictions.assert_called_once_with()
