import pytest

from health_data.formatter import (
    format_distance,
    format_duration,
    format_pace,
    format_activities,
    format_activity,
    format_streams,
    format_gear,
    format_athlete_stats,
    format_laps,
    format_zones,
    format_clubs,
    format_routes,
    format_route,
    format_segment,
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


class TestFormatGear:
    def test_shows_gear_details(self):
        gear = {
            "id": "g123",
            "name": "Hoka Mach 6",
            "brand_name": "Hoka",
            "model_name": "Mach 6",
            "distance": 450000.0,
        }
        result = format_gear(gear)
        assert "Hoka Mach 6" in result
        assert "450.0 km" in result

    def test_minimal_gear(self):
        gear = {"name": "Old Shoes"}
        result = format_gear(gear)
        assert "Old Shoes" in result


class TestFormatAthleteStats:
    def test_shows_totals(self):
        stats = {
            "all_run_totals": {"count": 100, "distance": 500000.0, "moving_time": 180000, "elevation_gain": 5000.0},
            "ytd_run_totals": {"count": 20, "distance": 100000.0, "moving_time": 36000, "elevation_gain": 1000.0},
            "recent_run_totals": {"count": 5, "distance": 25000.0, "moving_time": 9000, "elevation_gain": 250.0},
        }
        result = format_athlete_stats(stats)
        assert "All time" in result or "all" in result.lower()
        assert "100" in result  # count

    def test_empty_stats(self):
        result = format_athlete_stats({})
        assert "No" in result


class TestFormatLaps:
    def test_shows_lap_table(self):
        laps = [
            {"name": "Lap 1", "distance": 1000.0, "elapsed_time": 300, "average_heartrate": 150.0},
            {"name": "Lap 2", "distance": 1000.0, "elapsed_time": 290, "average_heartrate": 155.0},
        ]
        result = format_laps(laps)
        assert "Lap 1" in result
        assert "Lap 2" in result
        assert "1.0 km" in result

    def test_empty_laps(self):
        result = format_laps([])
        assert "no lap" in result.lower()


class TestFormatZones:
    def test_shows_hr_zones(self):
        zones = {
            "heart_rate": {
                "zones": [
                    {"min": 0, "max": 120},
                    {"min": 120, "max": 150},
                    {"min": 150, "max": 170},
                    {"min": 170, "max": 185},
                    {"min": 185, "max": -1},
                ]
            },
        }
        result = format_zones(zones)
        assert "Z1" in result or "Zone" in result
        assert "120" in result

    def test_empty_zones(self):
        result = format_zones({})
        assert "no zone" in result.lower()


class TestFormatClubs:
    def test_shows_club_list(self):
        clubs = [
            {"id": 1, "name": "Oslo Running Club", "member_count": 150, "sport_type": "running"},
        ]
        result = format_clubs(clubs)
        assert "Oslo Running Club" in result
        assert "150" in result

    def test_empty_clubs(self):
        result = format_clubs([])
        assert "no club" in result.lower()


class TestFormatRoutes:
    def test_shows_route_table(self):
        routes = [
            {"id": 1, "name": "Frognerparken Loop", "distance": 5000.0, "elevation_gain": 50.0},
        ]
        result = format_routes(routes)
        assert "Frognerparken" in result
        assert "5.0 km" in result

    def test_empty_routes(self):
        result = format_routes([])
        assert "no route" in result.lower()


class TestFormatRoute:
    def test_shows_route_details(self):
        route = {
            "name": "Frognerparken Loop",
            "distance": 5000.0,
            "elevation_gain": 50.0,
            "description": "Nice loop",
        }
        result = format_route(route)
        assert "Frognerparken" in result
        assert "5.0 km" in result


class TestFormatSegment:
    def test_shows_segment_details(self):
        segment = {
            "name": "Holmenkollen Climb",
            "distance": 3200.0,
            "average_grade": 8.5,
            "elevation_high": 371.0,
            "elevation_low": 120.0,
        }
        result = format_segment(segment)
        assert "Holmenkollen" in result
        assert "3.2 km" in result
        assert "8.5" in result
