---
name: health-data
description: >
  Fetch health and fitness data from Garmin Connect and Strava using the `health` CLI.
  Use when you need activity data, sleep stats, weight, HRV, resting HR, stress, body battery,
  respiration, VO2 max, steps, calories, intensity minutes, race predictions,
  training status, training readiness, lactate threshold, hill score, or workout analysis.
  Trigger phrases: "hent treningsdata", "garmin data", "strava data", "activities", "sleep score", "hrv",
  "resting heart rate", "body battery", "training data", "workout analysis", "training status",
  "training load", "lactate threshold", "training readiness", "hill score",
  or when any skill needs device-measured health or fitness data.
---

# Health Data

`health` CLI on PATH. Always use `--json 2>/dev/null`. All date args are `YYYY-MM-DD` and default to today.

## Garmin Connect

Auth via saved tokens — no login needed unless `health garmin login` has never been run.

### Daily bio metrics

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

### Training metrics

```bash
health --json garmin training-status [DATE]    # status, ACWR, acute/chronic load, load balance (aerobic low/high, anaerobic) with targets
health --json garmin training-readiness [DATE]  # readiness score, level
health --json garmin lactate-threshold          # LT heart rate (bpm), pace (min:ss/km)
health --json garmin hill-score [DATE]          # hill score, endurance, strength
```

### Activities

```bash
health --json garmin activities [--limit N] [--start N] [--activity-type TYPE]
# → activity_id, name, sport_type, start_time, distance_m, duration_s, avg_hr, elevation_gain_m,
#   vo2max, aerobic_te, anaerobic_te, training_load, location

health --json garmin activity ID
# → all core metrics + training (aerobic/anaerobic TE, training load, VO2 max, workout feel/RPE),
#   running dynamics (GCT, GCT balance, vert. oscillation, vert. ratio, respiration),
#   HR zones (time in zones 1-5), fastest splits (1km, mile, 5km, 10km), water estimate

health --json garmin activity-splits ID        # per-lap: distance, time, pace, HR, cadence, elevation
health --json garmin activity-hr-zones ID      # time in each HR zone with zone boundaries
health --json garmin activity-weather ID       # temp, feels like, humidity, wind, condition
health --json garmin activity-details ID       # second-by-second streams (HR, speed, cadence, elevation, etc.)
health --json garmin activity-gear ID          # gear name, type, make, model
```

## Strava

Auth via OAuth tokens — refreshed automatically.

```bash
health --json strava activities [--limit N] [--after DATE] [--before DATE]
# → id, name, sport_type, start_date_local, distance (m), moving_time (s),
#   total_elevation_gain (m), average_heartrate, average_speed (m/s), gear_id

health --json strava activity ID       # full detail + calories, splits, segment_efforts, perceived_exertion
health --json strava streams ID [--types heartrate,watts,time,cadence,altitude,latlng]
# → {type: [values...]} — one value per second
health --json strava laps ID           # distance, elapsed_time, average_heartrate per lap
health --json strava athlete-stats     # lifetime/YTD/recent totals by sport
health --json strava zones             # HR and power zones

# Write operations
health --json strava create-activity --name "Run" --sport-type Run \
  --start 2026-03-25T08:00:00 --elapsed-time 1800 [--distance 5000] [--rpe 7]
health --json strava update-activity ID [--name X] [--sport-type X] [--description X] [--gear-id X] [--rpe N]
health --json strava upload activity.fit
```
