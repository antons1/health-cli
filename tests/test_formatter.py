import pytest

from health_data.formatter import (
    format_distance,
    format_duration,
    format_pace,
    format_activities,
    format_activity,
    format_streams,
)


class TestFormatDistance:
    def test_meters_to_km(self):
        assert format_distance(10000.0) == "10.0 km"

    def test_short_distance(self):
        assert format_distance(500.0) == "500 m"

    def test_none(self):
        assert format_distance(None) == "-"


class TestFormatDuration:
    def test_minutes_and_seconds(self):
        assert format_duration(3661) == "1:01:01"

    def test_under_one_hour(self):
        assert format_duration(754) == "12:34"

    def test_none(self):
        assert format_duration(None) == "-"


class TestFormatPace:
    def test_running_pace(self):
        # 3.0 m/s = 5:33/km
        result = format_pace(3.0)
        assert result == "5:33/km"

    def test_zero_speed(self):
        assert format_pace(0) == "-"

    def test_none(self):
        assert format_pace(None) == "-"


class TestFormatActivities:
    def test_table_output(self):
        activities = [
            {
                "id": 123,
                "name": "Morning Run",
                "sport_type": "Run",
                "start_date_local": "2026-03-24T14:52:27+00:00",
                "distance": 2785.9,
                "moving_time": 1081,
                "average_heartrate": 143.4,
                "total_elevation_gain": 16.0,
            },
        ]
        result = format_activities(activities)
        assert "Morning Run" in result
        assert "Run" in result
        assert "2.8 km" in result

    def test_empty_list(self):
        result = format_activities([])
        assert "No activities" in result


class TestFormatActivity:
    def test_key_value_output(self):
        activity = {
            "name": "Afternoon Run",
            "sport_type": "Run",
            "start_date_local": "2026-03-24T14:52:27+00:00",
            "distance": 5000.0,
            "moving_time": 1500,
            "elapsed_time": 1600,
            "average_speed": 3.33,
            "max_speed": 4.5,
            "average_heartrate": 155.0,
            "max_heartrate": 175,
            "total_elevation_gain": 42.0,
            "calories": 350.0,
            "average_cadence": 82.5,
        }
        result = format_activity(activity)
        assert "Afternoon Run" in result
        assert "5.0 km" in result
        assert "155" in result
        assert "350" in result

    def test_missing_fields_handled(self):
        """Activity with minimal fields doesn't crash."""
        activity = {"name": "Walk", "distance": 1000.0}
        result = format_activity(activity)
        assert "Walk" in result


class TestFormatStreams:
    def test_summary_output(self):
        streams = {
            "heartrate": [120, 130, 140, 150, 160],
            "time": [0, 1, 2, 3, 4],
            "cadence": [80, 82, 81, 83, 80],
        }
        result = format_streams(streams)
        assert "heartrate" in result
        assert "120" in result  # min
        assert "160" in result  # max
        assert "5" in result    # data points

    def test_empty_streams(self):
        result = format_streams({})
        assert "No stream" in result
