# health CLI reference

Complete catalog of `health` subcommands, flags, and return fields. Read this instead of running `--help`.

All commands accept `--json` as a top-level flag (before the subcommand). All commands with a `DATE` argument default to today; `DATE` format is `YYYY-MM-DD`.

---

## `health garmin`

Auth: `health garmin login` (runs once per few months; stores tokens in `~/.health-data/garmin/`).

### Daily bio metrics

Each returns one JSON object for the given date.

| Command | Arg | Fields |
| --- | --- | --- |
| `garmin sleep [DATE]` | DATE = wake-up date (returns last night) | `date`, `score` (0–100), `score_qualifier` (`POOR`/`FAIR`/`GOOD`/`EXCELLENT`), `total`/`deep`/`light`/`rem`/`awake` (formatted `Xh Ym`), `avg_stress`, `feedback` |
| `garmin hrv [DATE]` | wake-up date | `date`, `last_night_avg`, `weekly_avg`, `status` (`BALANCED`/`LOW`/`UNBALANCED`/`POOR`/`NO_STATUS`), `baseline_low`, `baseline_high` |
| `garmin rhr [DATE]` | | `date`, `rhr` (bpm) |
| `garmin stress [DATE]` | | `date`, `avg`, `max` (0–100) |
| `garmin body-battery [DATE]` | | `date`, `charged`, `drained`, `peak`, `end` (0–100) |
| `garmin respiration [DATE]` | wake-up date | `date`, `avg_sleep`, `avg_waking`, `low`, `high` (breaths/min) |
| `garmin vo2max [DATE]` | | `date`, `vo2max`, `vo2max_precise` |
| `garmin weight [DATE]` | | `date`, `weight_kg` — falls back to most recent logged entry |
| `garmin steps [DATE]` | | `date`, `steps`, `distance_km`, `goal` |
| `garmin calories [DATE]` | | `date`, `total`, `active`, `bmr` (kcal) |
| `garmin intensity-minutes [DATE]` | | `date`, `moderate`, `vigorous`, `weekly_total`, `weekly_goal` |
| `garmin race-predictions` | no DATE — latest estimate | `5k`, `10k`, `half_marathon`, `marathon` (`h:mm:ss`) |

### Training metrics

| Command | Fields |
| --- | --- |
| `garmin training-status [DATE]` | `date`, `status` (e.g. `STRAINED_3`, `PRODUCTIVE_2`), `acute_load`, `chronic_load_max`, `acwr_pct`, `acwr_status` (`LOW`/`OPTIMAL`/`HIGH`), `load_aerobic_low`, `load_aerobic_high`, `load_anaerobic`, matching `*_target` strings like `"123-334"`, `balance_feedback` |
| `garmin training-readiness [DATE]` | `date`, `score` (0–100 or null), `level` (or null) |
| `garmin lactate-threshold` | `heart_rate` (bpm), `pace` (min:ss/km) |
| `garmin hill-score [DATE]` | `date`, `hill_score`, `endurance`, `strength` |

### Garmin activities

```
garmin activities [--limit N] [--start N] [--activity-type TYPE]
```

- `--limit` — default 20.
- `--start` — pagination offset.
- `--activity-type` — `running`, `cycling`, `swimming`, `strength_training`, etc.

Returns an array; each element: `activity_id`, `name`, `sport_type`, `start_time`, `distance_m`, `duration_s`, `avg_hr`, `elevation_gain_m`, `vo2max`, `aerobic_te`, `anaerobic_te`, `training_load`, `location`.

```
garmin activity ACTIVITY_ID
```

Full detail. Includes everything above plus:
- Training: `aerobic_te`, `anaerobic_te`, `training_load`, `vo2max`, `workout_feel`, `workout_rpe`.
- Running dynamics: `gct` (ground contact time), `gct_balance`, `vertical_oscillation`, `vertical_ratio`, `avg_respiration`.
- HR zones: `time_in_zone_1` … `time_in_zone_5` (seconds).
- Fastest splits: `fastest_1km`, `fastest_mile`, `fastest_5km`, `fastest_10km`.
- `water_estimate_ml`.

```
garmin activity-splits ACTIVITY_ID        # per-lap: distance, time, pace, HR, cadence, elevation
garmin activity-hr-zones ACTIVITY_ID      # time in each zone + zone boundary bpm
garmin activity-weather ACTIVITY_ID       # temp, feels_like, humidity, wind, condition
garmin activity-details ACTIVITY_ID       # second-by-second streams (HR, speed, cadence, elevation, …)
garmin activity-gear ACTIVITY_ID          # gear name, type, make, model
```

---

## `health strava`

Auth: `health strava setup --client-id X --client-secret Y` once, then `health strava login` (browser OAuth). Tokens refresh automatically.

### Reads

```
strava activities [--limit N] [--after DATE] [--before DATE]
```
- `--after` / `--before` — `YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SS`. **No `--days` flag** — use `--after` with a computed date.
- Default `--limit` = 20.

Each activity (partial list of frequently-used fields): `id`, `name`, `sport_type`, `type`, `start_date`, `start_date_local`, `distance` (m), `moving_time`, `elapsed_time`, `total_elevation_gain` (m), `elev_high`, `elev_low`, `average_speed` (m/s), `max_speed`, `average_heartrate`, `max_heartrate`, `average_cadence`, `average_watts`, `suffer_score`, `kudos_count`, `gear_id`, `has_heartrate`, `trainer`, `commute`, `manual`, `map.summary_polyline`, `athlete.id`, `start_latlng`, `end_latlng`, `timezone`, `utc_offset`.

```
strava activity ACTIVITY_ID
```
Returns everything `activities` returns plus: `description`, `calories`, `device_name`, `average_temp`, `gear` (object with `id`, `name`, `distance`), `laps[]`, `splits_metric[]` (per-km), `splits_standard[]` (per-mile), `best_efforts[]` (`400m`, `1/2 mile`, `1K`, `1 mile`, `2 mile`, `5K`, `10K`, `half-marathon`, `marathon` — whichever were reached), `segment_efforts[]`, `photos`, `map.polyline` (full, not summary), `embed_token`.

Per-lap fields: `lap_index`, `distance`, `elapsed_time`, `moving_time`, `average_speed`, `max_speed`, `average_heartrate`, `max_heartrate`, `average_cadence`, `pace_zone` (1–5), `total_elevation_gain`, `start_index`, `end_index`.

Per-km split (`splits_metric`): `split`, `distance`, `elapsed_time`, `moving_time`, `average_speed`, `average_heartrate`, `elevation_difference`, `pace_zone`, `average_grade_adjusted_speed`.

Segment effort: `distance`, `elapsed_time`, `moving_time`, `average_heartrate`, `max_heartrate`, `average_cadence`, `segment.name`, `segment.distance`, `segment.average_grade`, `segment.maximum_grade`, `segment.city`, `segment.state`, `segment.country`, `segment.climb_category`.

```
strava streams ACTIVITY_ID --types t1,t2,…
```
Available types: `time`, `latlng`, `distance`, `altitude`, `velocity_smooth`, `heartrate`, `cadence`, `watts`, `temp`, `moving`, `grade_smooth`.

Returns `{type: [values]}`. Parallel arrays; `time` is seconds from start but non-dense (gaps on pause — index ≠ second). Omit `--types` to get all.

Units: `heartrate`=bpm, `cadence`=strides/min (Strava halves running cadence — multiply by 2 for steps/min), `watts`=W, `distance`=m (cumulative), `altitude`=m, `velocity_smooth`=m/s, `temp`=°C, `grade_smooth`=%, `moving`=bool.

```
strava laps ACTIVITY_ID
```
Returns lap array, same per-lap shape as inside `strava activity` but as top-level list.

```
strava athlete-stats
```
Lifetime + YTD + recent totals, per sport (`recent_run_totals`, `ytd_run_totals`, `all_run_totals`, same for ride and swim, plus `biggest_ride_distance`, `biggest_climb_elevation_gain`).

```
strava zones
```
HR and power zone definitions: `heart_rate.zones[].min/max`, `power.zones[].min/max` (if power meter configured).

```
strava gear-list
strava gear GEAR_ID                # shoe/bike details: name, brand_name, model_name, distance, primary, retired
strava route ROUTE_ID
strava routes                      # your saved routes
strava segment SEGMENT_ID
strava segments --bounds S,W,N,E   # explore — required bounding box as comma-separated floats
strava clubs
```

### Writes

```
strava create-activity --name NAME --sport-type TYPE --start ISO --elapsed-time SEC \
                       [--distance M] [--description TEXT] [--rpe 1-10]
```
- `--name`, `--sport-type`, `--start`, `--elapsed-time` are required.
- `--start` accepts `YYYY-MM-DDTHH:MM:SS` (no timezone — local).
- `--sport-type` examples: `Run`, `Ride`, `Swim`, `WeightTraining`, `Walk`, `Hike`, `Workout`.
- `--rpe` is integer 1–10.

```
strava update-activity ACTIVITY_ID [--name TEXT] [--sport-type TEXT] [--description TEXT] \
                                   [--gear-id TEXT] [--rpe 1-10]
```
All flags optional. Pass only what changes.

```
strava upload PATH
```
Accepts `.fit`, `.tcx`, `.gpx`. Returns upload status; the activity may take a minute to process.

---

## Top-level commands

```
health --version
health --json <subcommand> …    # always pass --json as top-level flag, before subcommand
```

## Caching (info only)

Garmin responses are cached in `~/.health-data/garmin/cache/`:
- Past dates: cached indefinitely (immutable).
- Today + static metrics (sleep, hrv, rhr, respiration, vo2max, weight): 4-hour TTL.
- Today + dynamic metrics (stress, body-battery, steps, calories, intensity-minutes): 15-minute TTL.

You don't need to manage this. If data looks stale and you absolutely need fresh: `rm -rf ~/.health-data/garmin/cache/` (destructive — ask the user first).
