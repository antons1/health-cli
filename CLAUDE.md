As part of an ongoing project to track nutrition and health, I need easy access to health data. Data comes from Strava and Garmin Connect via their APIs.

This project is a CLI (`health`) used by Claude Code/Claude Cowork to fetch health metrics, workouts, and manage activities.

## Sources

- **Strava** — workouts, activities (with RPE support), gear, segments, routes
- **Garmin Connect** — daily bio metrics (sleep, HRV, RHR, stress, body battery, respiration, VO2 max, weight, steps, calories, intensity minutes, race predictions), training metrics (training status, training readiness, lactate threshold, hill score), and full activity data (details, splits, HR zones, weather, gear, time-series streams)

## Agents

The `health-data` agent (`~/.claude/agents/health-data.md`) is globally available from any project to fetch health and fitness data. It wraps the `health` CLI.

## Garmin auth

Garmin uses `garminconnect` v0.3.0 with `curl_cffi` for TLS fingerprint spoofing (required since Garmin deployed Cloudflare bot protection in March 2026). Tokens are stored in `~/.health-data/garmin/` and persist for months. Run `health garmin login` once to bootstrap.

## Caching

Garmin API responses are cached in `~/.health-data/garmin/cache/`:
- Past dates: cached indefinitely (data is immutable)
- Today, static metrics (sleep, HRV, RHR, respiration, VO2 max, weight): 4-hour TTL
- Today, dynamic metrics (stress, body battery, steps, calories, intensity minutes): 15-minute TTL
