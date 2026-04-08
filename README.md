# health-data

CLI for fetching and managing personal health and fitness data from Strava and Garmin Connect.

Built for use with [Claude Code](https://claude.ai/claude-code) — includes a custom agent for natural language health data queries.

## Install

```bash
pip install -e .
```

## Strava setup

1. Create a Strava API application at https://www.strava.com/settings/api
2. Configure credentials and authenticate:

```bash
health strava setup --client-id YOUR_ID --client-secret YOUR_SECRET
health strava login
```

## Strava usage

```bash
health strava activities              # list recent activities
health strava activities --after 2025-01-01  # activities after date
health strava activities --after 2025-01-01 --before 2025-02-01  # date range
health strava activity 12345          # activity details
health strava streams 12345           # second-by-second data
health strava laps 12345              # lap splits
health strava gear g12345             # shoe/bike details
health strava athlete-stats           # lifetime totals
health strava zones                   # HR/power zones
health strava clubs                   # your clubs
health strava routes                  # your routes
health strava segments --bounds 59.9,10.7,60.0,10.8  # explore segments
```

### Create and manage activities

```bash
health strava create-activity --name "Morning Run" --sport-type Run \
  --start 2026-03-25T08:00:00 --elapsed-time 1800 --distance 5000 --rpe 7
health strava update-activity 12345 --name "New Name" --gear-id g67890 --rpe 8
health strava upload activity.fit
```

## Garmin setup

Authenticate once — tokens are saved and reused automatically (no re-login needed for months):

```bash
health garmin login
```

## Garmin usage

All commands default to today. Pass an optional `DATE` (YYYY-MM-DD) for historical data.
Overnight metrics (sleep, HRV, respiration) use today as the wake-up date for last night's data.

```bash
# Sleep & recovery
health garmin sleep [DATE]            # sleep score, stages, stress
health garmin hrv [DATE]              # HRV avg, status, baseline
health garmin rhr [DATE]              # resting heart rate
health garmin respiration [DATE]      # sleep breathing rate
health garmin stress [DATE]           # avg and max stress
health garmin body-battery [DATE]     # body battery charged/drained/peak

# Daily activity
health garmin steps [DATE]            # step count, distance, goal
health garmin calories [DATE]         # total, active, BMR
health garmin intensity-minutes [DATE] # moderate/vigorous minutes, weekly totals

# Fitness metrics
health garmin vo2max [DATE]           # VO2 max estimate
health garmin weight [DATE]           # body weight (falls back to most recent entry)
health garmin race-predictions        # predicted race times (5K–marathon)

# Training metrics
health garmin training-status [DATE]   # status, ACWR, load balance with targets
health garmin training-readiness [DATE] # training readiness score
health garmin lactate-threshold        # LT heart rate and pace
health garmin hill-score [DATE]        # hill score (endurance + strength)

# Activities
health garmin activities [--limit N] [--activity-type running]
health garmin activity 12345          # full detail: training effect, load, dynamics, HR zones, splits
health garmin activity-splits 12345   # per-lap breakdown
health garmin activity-hr-zones 12345 # time in each HR zone
health garmin activity-weather 12345  # weather conditions
health garmin activity-details 12345  # second-by-second streams
health garmin activity-gear 12345     # gear used
```

Responses are cached: past dates indefinitely, today's static metrics (sleep, HRV, RHR) for 4 hours, dynamic metrics (steps, calories, stress, body battery) for 15 minutes. Cache lives in `~/.health-data/garmin/cache/`.

## Output modes

- Default: human-readable tables
- `--json`: raw JSON for programmatic use

```bash
health --json garmin sleep
health --json strava activities
```

## Claude Code agent

The `health-data` agent (`~/.claude/agents/health-data.md`) provides natural language access to all commands from any project directory.

## Development

```bash
pip install -e ".[dev]"
pytest
```
