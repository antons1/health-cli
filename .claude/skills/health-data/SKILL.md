---
name: health-data
description: >
  Fetch health and fitness data from Garmin Connect and Strava using the `health` CLI.
  Use when you need activity data, sleep stats, weight, HRV, resting HR, stress, body battery,
  respiration, VO2 max, steps, calories, intensity minutes, race predictions,
  training status, training readiness, lactate threshold, hill score, or workout analysis.
  Also for writing to Strava: RPE, rename, re-gear, manual activity, upload .fit.
  Trigger phrases: "hent treningsdata", "garmin data", "strava data", "activities", "sleep score",
  "hrv", "resting heart rate", "body battery", "training data", "workout analysis",
  "training status", "training load", "lactate threshold", "training readiness", "hill score",
  or when any skill needs device-measured health or fitness data.
allowed-tools: Bash(health *)
---

# health-data

`health` CLI on PATH. Fetches from Garmin Connect and Strava, writes to Strava. JSON output only.

## Rules

- Every invocation: `health --json <cmd> 2>/dev/null`. Always `--json`, always suppress stderr.
- Dates: `YYYY-MM-DD`; omit for today. **Overnight metrics (`sleep`, `hrv`, `respiration`) use the wake-up date** — passing today's date returns last night.
- **Do NOT run `health --help` or `<subcommand> --help`.** The intent table below is authoritative. For commands or flags not listed here, read `reference.md` in this directory.
- Parallelize independent reads in a single tool-call batch (see Primitives).
- On command failure, report once. Do not retry.
- Auth is pre-configured. Only run `health garmin login` / `health strava login` if a command explicitly reports an auth failure.

## Intent → command

| User wants | Command |
| --- | --- |
| Last night's sleep (score + stages) | `health --json garmin sleep [DATE]` |
| HRV (nightly avg + status + baseline) | `health --json garmin hrv [DATE]` |
| Resting heart rate | `health --json garmin rhr [DATE]` |
| Stress (avg + max) | `health --json garmin stress [DATE]` |
| Body battery (charged/drained/peak/end) | `health --json garmin body-battery [DATE]` |
| Respiration (breaths/min, sleep + waking) | `health --json garmin respiration [DATE]` |
| Weight in kg (falls back to most recent entry) | `health --json garmin weight [DATE]` |
| VO2 max | `health --json garmin vo2max [DATE]` |
| Steps (count, distance, goal) | `health --json garmin steps [DATE]` |
| Calories (total, active, BMR) | `health --json garmin calories [DATE]` |
| Intensity minutes (daily + weekly) | `health --json garmin intensity-minutes [DATE]` |
| Training status + load balance | `health --json garmin training-status [DATE]` |
| Training readiness score | `health --json garmin training-readiness [DATE]` |
| Lactate threshold HR + pace | `health --json garmin lactate-threshold` |
| Hill score (endurance + strength) | `health --json garmin hill-score [DATE]` |
| Race predictions (5K, 10K, HM, marathon) | `health --json garmin race-predictions` |
| Recent Strava activities | `health --json strava activities [--limit N] [--after YYYY-MM-DD] [--before YYYY-MM-DD]` |
| Full Strava activity (detail + splits + segments) | `health --json strava activity ID` |
| Lap splits for a Strava activity | `health --json strava laps ID` |
| Second-by-second streams | `health --json strava streams ID --types heartrate,time,velocity_smooth,altitude` |
| Athlete totals (YTD, all-time) | `health --json strava athlete-stats` |
| HR & power zones | `health --json strava zones` |
| Garmin activities list | `health --json garmin activities [--limit N] [--activity-type TYPE]` |
| Full Garmin activity (aerobic/anaerobic TE, running dynamics, HR zones) | `health --json garmin activity ID` |
| Add RPE / rename / re-gear a Strava activity | `health --json strava update-activity ID [--rpe N] [--name "..."] [--gear-id G] [--description "..."] [--sport-type X]` |
| Log a manual activity (watch didn't record) | `health --json strava create-activity --name "..." --sport-type Run --start YYYY-MM-DDTHH:MM:SS --elapsed-time SEC [--distance M] [--rpe N] [--description "..."]` |
| Upload a FIT/TCX/GPX file | `health --json strava upload PATH` |

Anything not in this table → `reference.md`. Not `--help`.

## Primitives (composable recipes)

### `daily-snapshot DATE` — morning readiness check

Issue these as a single parallel batch:

```
health --json garmin sleep DATE
health --json garmin hrv DATE
health --json garmin rhr DATE
health --json garmin body-battery DATE
health --json garmin training-readiness DATE
```

`training-readiness` often returns `{"score": null, "level": null}` if Garmin hasn't computed it yet (common mid-morning) — treat null as "not available", don't retry.

### `week-range START END` — weekly training rollup

One activities call, then per-day Garmin reads in parallel:

```
health --json strava activities --after START --before END --limit 50
```

Then for each date D in [START..END], in parallel:

```
health --json garmin sleep D
health --json garmin rhr D
health --json garmin hrv D
```

Sum `distance` / `moving_time` across the activities array for training load. The per-day Garmin loop gives a recovery trend.

### `activity-deep-dive STRAVA_ID` — workout analysis

First two in parallel. Skip streams unless you need second-by-second data (HR stability within an interval, pace within a rep, etc.):

```
health --json strava activity STRAVA_ID
health --json strava laps STRAVA_ID

# Optional — ~1000 points per hour of activity:
health --json strava streams STRAVA_ID --types heartrate,time,velocity_smooth,altitude
```

`strava activity` already includes `splits_metric` (per-km), `splits_standard` (per-mile), `best_efforts`, `segment_efforts`, `description`, `gear`, `calories`. Don't also call `laps` unless the user explicitly cares about **watch-recorded laps** (e.g. interval reps vs. recoveries) — those have a different structure than the auto-generated per-km splits.

## Example outputs

Shape before calling. Structures are shown abbreviated; some location/id fields redacted.

### `garmin sleep`
```json
{
  "date": "2026-04-22",
  "score": 78,
  "score_qualifier": "FAIR",
  "total": "6h 26m",
  "deep": "0h 58m",
  "light": "4h 25m",
  "rem": "1h 3m",
  "awake": "0h 8m",
  "avg_stress": 14.0,
  "feedback": "POSITIVE_CONTINUOUS"
}
```

### `garmin hrv`
```json
{
  "date": "2026-04-22",
  "last_night_avg": 59,
  "weekly_avg": 46,
  "status": "LOW",
  "baseline_low": 52,
  "baseline_high": 76
}
```
`status` is one of `BALANCED`, `LOW`, `UNBALANCED`, `POOR`, `NO_STATUS`.

### `garmin training-status`
```json
{
  "date": "2026-04-22",
  "status": "STRAINED_3",
  "acute_load": 120,
  "chronic_load_max": 283.5,
  "acwr_pct": 25,
  "acwr_status": "LOW",
  "load_aerobic_low": 718.76,
  "load_aerobic_high": 0.0,
  "load_anaerobic": 0.0,
  "load_aerobic_low_target": "123-334",
  "load_aerobic_high_target": "264-475",
  "load_anaerobic_target": "0-211",
  "balance_feedback": "AEROBIC_HIGH_SHORTAGE"
}
```
Load values are Garmin's internal EPOC-based units (not TRIMP, not TSS). Compare against the `*_target` string, not absolute numbers.

### `strava activities` (array — one element, location fields redacted)
```json
[
  {
    "id": 18197654006,
    "name": "Week 5: Group run 4×4 Z1",
    "sport_type": "Run",
    "type": "Run",
    "start_date_local": "2026-04-21T14:33:51",
    "distance": 5345.5,
    "moving_time": 2488,
    "elapsed_time": 3312,
    "total_elevation_gain": 42.0,
    "average_speed": 2.149,
    "max_speed": 3.9,
    "average_heartrate": 135.8,
    "max_heartrate": 175,
    "average_cadence": 71.9,
    "suffer_score": 14,
    "gear_id": "g28464066",
    "has_heartrate": true
  }
]
```

### `strava activity` (abbreviated — drops `map.polyline`, `photos`, redacts segment locations)
```json
{
  "id": 18197654006,
  "name": "Week 5: Group run 4×4 Z1",
  "sport_type": "Run",
  "distance": 5345.5,
  "moving_time": 2488,
  "elapsed_time": 3312,
  "average_heartrate": 135.8,
  "max_heartrate": 175,
  "average_cadence": 71.9,
  "suffer_score": 14,
  "calories": 478.0,
  "description": "Goal: Z1 easy only, HR cap 145.\nActual: 5.35 km, avg HR 136...",
  "device_name": "Garmin fēnix 6X",
  "average_temp": 25,
  "gear": {"id": "g28464066", "name": "ASICS Novablast 5", "distance": 144853.0},
  "laps": [
    {"lap_index": 1, "distance": 1000.0, "moving_time": 558, "average_speed": 1.79,
     "average_heartrate": 116.4, "max_heartrate": 134.0, "average_cadence": 67.0,
     "pace_zone": 1, "total_elevation_gain": 6.4}
  ],
  "splits_metric": [
    {"split": 1, "distance": 1001.5, "moving_time": 524, "average_speed": 1.91,
     "average_heartrate": 116.4, "elevation_difference": -5.4, "pace_zone": 1}
  ],
  "splits_standard": [/* per-mile, same shape as splits_metric */],
  "best_efforts": [
    {"name": "1K",     "distance": 1000.0, "elapsed_time": 424},
    {"name": "1 mile", "distance": 1609.0, "elapsed_time": 695},
    {"name": "5K",     "distance": 5000.0, "elapsed_time": 3121}
  ],
  "segment_efforts": [/* {distance, moving_time, average_heartrate, max_heartrate, segment:{name, distance, average_grade}} */]
}
```

### `strava streams ID --types heartrate,time,velocity_smooth`
```json
{
  "heartrate":        [104, 96, 92, 95, 92, 90, 91, 91, 93, 94, "…"],
  "time":             [0,   1,  3,  5,  7,  9, 10, 11, 12, 18, "…"],
  "velocity_smooth":  [0.0, 0.8, 1.2, 1.5, 1.6, "…"]
}
```
Parallel arrays — `heartrate[i]` matches `time[i]`. `time` is seconds from activity start; gaps appear where recording paused (watch out: index != second).

## Unit conventions

- **Distance**: meters everywhere. `/1000` for km.
- **Duration**: seconds. `moving_time` excludes pauses; `elapsed_time` includes them.
- **Speed**: m/s. Running pace (min/km) = `1000 / (speed * 60)`. Bike km/h = `speed * 3.6`.
- **Weight**: `weight_kg` is already kg (CLI converts from Garmin's grams).
- **Heart rate**: bpm.
- **Temperature**: °C.
- **Pace zones / HR zones**: integers 1–5 matching Strava/Garmin zone config (fetch `strava zones` for boundaries).

## Auth (only on failure)

- Strava refresh is automatic. If a command reports an auth error, re-run once. Still failing → `health strava login`.
- Garmin tokens last months. On failure → `health garmin login` (uses curl_cffi TLS fingerprint — Cloudflare gate).
