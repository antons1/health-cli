As part of an ongoing project to track nutrition and health, I need easy access to health data. Most of my available health data are available through Garmin Connect and Apple Health.

This project should end up in a CLI that can be used by Claude Code/Claude Cowork to fetch my health metrics, workouts etc.

## health CLI reference

The `health` CLI fetches personal health and fitness data. All commands output JSON to stdout. Errors go to stderr.

Binary location: `/Library/Frameworks/Python.framework/Versions/3.13/bin/health`

### Strava (working)

Auth tokens are stored in `~/.garmin-health/strava/`. Tokens refresh automatically.

#### List recent activities

```bash
health strava activities              # last 20 activities
health strava activities --limit 5    # last 5 activities
```

Returns a JSON array. Each activity includes:
- `id` — unique activity ID (use with `activity` and `streams` commands)
- `name` — activity name (e.g. "Afternoon Run")
- `type` / `sport_type` — activity type (e.g. "Run", "EBikeRide")
- `start_date_local` — local start time (ISO 8601)
- `distance` — distance in meters
- `moving_time` — moving time in seconds
- `elapsed_time` — total time in seconds
- `total_elevation_gain` — elevation gain in meters
- `average_speed` — m/s
- `max_speed` — m/s
- `average_heartrate` / `max_heartrate` — BPM (if heart rate monitor used)
- `average_cadence` — steps/min or RPM (if available)
- `average_watts` / `max_watts` — watts (if power meter or estimated)
- `kilojoules` — energy output
- `suffer_score` — Strava's relative effort score
- `start_latlng` / `end_latlng` — GPS coordinates [lat, lng]
- `timezone` — timezone string

#### Get detailed activity

```bash
health strava activity 17840848041
```

Returns a JSON object with everything from `activities` plus:
- `calories` — estimated calories burned
- `laps` — array of lap splits with per-lap distance, time, pace, HR
- `splits_metric` — per-km splits
- `splits_standard` — per-mile splits
- `best_efforts` — best times for standard distances (400m, 1km, 1mi, etc.)
- `segment_efforts` — performance on Strava segments
- `gear` — equipment used (shoes, bike)
- `device_name` — recording device
- `average_temp` — temperature in Celsius

#### Get second-by-second streams

```bash
health strava streams 17840848041                              # all available streams
health strava streams 17840848041 --types heartrate,time       # specific streams
health strava streams 17840848041 --types heartrate,cadence,watts,time
```

Returns a JSON object where each key is a stream type and each value is an array of data points (typically one per second):

Available stream types:
- `time` — seconds from activity start
- `heartrate` — BPM
- `cadence` — RPM or steps/min
- `watts` — power in watts
- `distance` — cumulative distance in meters
- `altitude` — elevation in meters
- `velocity_smooth` — speed in m/s (smoothed)
- `latlng` — GPS coordinates [lat, lng]
- `temp` — temperature in Celsius
- `grade_smooth` — gradient percentage
- `moving` — boolean, moving or stopped

Example output structure:
```json
{
  "heartrate": [92, 90, 93, 94, 95, ...],
  "time": [0, 4, 7, 8, 14, ...],
  "cadence": [0, 0, 74, 73, 72, ...]
}
```

#### Auth commands (typically only needed once)

```bash
health strava setup                           # save API credentials (prompted)
health strava login                           # OAuth2 flow (opens browser)
health strava login --code AUTH_CODE          # manual code exchange fallback
```

### Garmin Connect (currently blocked)

Garmin deployed Cloudflare bot detection on 2026-03-17 which blocks all programmatic login via python-garminconnect. Commands exist but cannot authenticate:

```bash
health garmin login
health garmin stats [DATE]
health garmin sleep [DATE]
health garmin heart-rate [DATE]
health garmin stress [DATE]
health garmin hrv [DATE]
health garmin spo2 [DATE]
health garmin weight [DATE] [--end DATE]
health garmin activities [--limit N]
health garmin activity ACTIVITY_ID
```

DATE supports: `today` (default), `yesterday`, `-7d`, `-1w`, `2024-03-20`.
