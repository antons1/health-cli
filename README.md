# health-data

CLI for fetching and managing personal health and fitness data from Strava.

Built for use with [Claude Code](https://claude.ai/claude-code) — includes a custom agent for natural language health data queries.

## Install

```bash
pip install -e .
```

## Setup

1. Create a Strava API application at https://www.strava.com/settings/api
2. Configure credentials and authenticate:

```bash
health strava setup --client-id YOUR_ID --client-secret YOUR_SECRET
health strava login
```

## Usage

```bash
health strava activities              # list recent activities
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
  --start 2026-03-25T08:00:00 --elapsed-time 1800 --distance 5000
health strava update-activity 12345 --name "New Name" --gear-id g67890
health strava upload activity.fit
```

### Output modes

- Default: human-readable tables
- `--json`: raw JSON for programmatic use

```bash
health --json strava activities
```

## Claude Code agent

The `health-data` agent (`~/.claude/agents/health-data.md`) provides natural language access to all commands from any project directory.

## Development

```bash
pip install -e ".[dev]"
pytest
```
