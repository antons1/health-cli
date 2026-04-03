---
name: health-data
description: >
  Fetch health and fitness data from Garmin Connect and Strava using the `health` CLI.
  Use when you need activity data, sleep stats, HRV, resting HR, stress, body battery,
  respiration, VO2 max, weight, steps, calories, intensity minutes, or race predictions.
  Trigger phrases: "garmin data", "strava data", "activities", "sleep score", "hrv",
  "resting heart rate", "body battery", "training data", "workout analysis",
  or when any skill needs device-measured health or fitness data.
---

# Health Data

`health` CLI on PATH. Always use `--json 2>/dev/null`. All date args are `YYYY-MM-DD` and default to today.

## Garmin Connect

Auth via saved tokens — no login needed unless `health garmin login` has never been run.

```bash
health --json garmin sleep [DATE]              # score, stages (deep/light/REM/awake), avg stress, feedback
health --json garmin hrv [DATE]                # last_night_avg, weekly_avg, status, baseline_low/high
health --json garmin rhr [DATE]                # rhr (bpm)
health --json garmin stress [DATE]             # avg, max (0–100)
health --json garmin body-battery [DATE]       # charged, drained, peak, end (0–100)
health --json garmin respiration [DATE]        # avg_sleep, avg_waking, low, high (breaths/min)
health --json garmin vo2max [DATE]             # vo2max, vo2max_precise
health --json garmin weight [DATE]             # weight_kg (falls back to most recent entry)
health --json garmin steps [DATE]              # steps, distance_km, goal
health --json garmin calories [DATE]           # total, active, bmr (kcal)
health --json garmin intensity-minutes [DATE]  # moderate, vigorous (today); weekly_total, weekly_goal
health --json garmin race-predictions          # 5k, 10k, half_marathon, marathon (h:mm:ss)
```

Sleep, HRV, and respiration use today as the **wake-up date** — i.e. they return last night's data.

## Strava

Auth via OAuth tokens — refreshed automatically.

```bash
health --json strava activities [--limit N] [--after DATE] [--before DATE]
# → id, name, sport_type, start_date_local, distance (m), moving_time (s),
#   total_elevation_gain (m), average_heartrate, average_speed (m/s), gear_id

health --json strava activity ID       # full detail + calories, splits, segment_efforts
health --json strava streams ID [--types heartrate,watts,time,cadence,altitude,latlng]
# → {type: [values...]} — one value per second
health --json strava laps ID           # distance, elapsed_time, average_heartrate per lap
health --json strava athlete-stats     # lifetime/YTD/recent totals by sport
health --json strava zones             # HR and power zones
```
