from datetime import date

import click

from health_data.output import output
from health_data.sources.garmin.auth import get_client, login as do_login
from health_data.sources.garmin import client as garmin_client
from health_data.sources.garmin.formatter import (
    format_sleep,
    format_hrv,
    format_stress,
    format_body_battery,
    format_rhr,
    format_respiration,
    format_vo2max,
    format_weight,
    format_steps,
    format_intensity_minutes,
    format_calories,
    format_race_predictions,
    format_activities,
    format_activity,
    format_activity_splits,
    format_activity_hr_zones,
    format_activity_weather,
    format_activity_details,
    format_activity_running_dynamics,
    format_activity_gear,
    format_lactate_threshold,
    format_training_status,
    format_training_readiness,
    format_hill_score,
)


def _today() -> str:
    return date.today().isoformat()


def _use_json(ctx) -> bool:
    return ctx.obj and ctx.obj.get("json", False)


@click.group()
def garmin():
    """Garmin health data."""
    pass


@garmin.command()
@click.option("--email", prompt="Email")
@click.option("--password", prompt="Password", hide_input=True)
def login(email, password):
    """Authenticate with Garmin and save tokens."""
    do_login(email, password)
    click.echo("Garmin login successful.", err=True)


@garmin.command()
@click.argument("date", default="")
@click.pass_context
def sleep(ctx, date):
    """Sleep score and stage breakdown.

    DATE defaults to today (wake-up date for last night's sleep).
    """
    target = date or _today()
    c = get_client()
    data = garmin_client.get_sleep(c, target)
    if _use_json(ctx):
        output(data)
    else:
        click.echo(format_sleep(data))


@garmin.command()
@click.argument("date", default="")
@click.pass_context
def hrv(ctx, date):
    """HRV summary for last night.

    DATE defaults to today (wake-up date for last night's data).
    """
    target = date or _today()
    c = get_client()
    data = garmin_client.get_hrv(c, target)
    if _use_json(ctx):
        output(data)
    else:
        click.echo(format_hrv(data))


@garmin.command()
@click.argument("date", default="")
@click.pass_context
def stress(ctx, date):
    """Daily stress summary.

    DATE defaults to today.
    """
    target = date or _today()
    c = get_client()
    data = garmin_client.get_stress(c, target)
    if _use_json(ctx):
        output(data)
    else:
        click.echo(format_stress(data))


@garmin.command("body-battery")
@click.argument("date", default="")
@click.pass_context
def body_battery(ctx, date):
    """Body battery summary.

    DATE defaults to today.
    """
    target = date or _today()
    c = get_client()
    data = garmin_client.get_body_battery(c, target)
    if _use_json(ctx):
        output(data)
    else:
        click.echo(format_body_battery(data))


@garmin.command()
@click.argument("date", default="")
@click.pass_context
def rhr(ctx, date):
    """Resting heart rate.

    DATE defaults to today.
    """
    target = date or _today()
    c = get_client()
    data = garmin_client.get_rhr(c, target)
    if _use_json(ctx):
        output(data)
    else:
        click.echo(format_rhr(data))


@garmin.command()
@click.argument("date", default="")
@click.pass_context
def respiration(ctx, date):
    """Sleep respiration (breathing rate).

    DATE defaults to today (wake-up date for last night's data).
    """
    target = date or _today()
    c = get_client()
    data = garmin_client.get_respiration(c, target)
    if _use_json(ctx):
        output(data)
    else:
        click.echo(format_respiration(data))


@garmin.command()
@click.argument("date", default="")
@click.pass_context
def vo2max(ctx, date):
    """VO2 max estimate.

    DATE defaults to today.
    """
    target = date or _today()
    c = get_client()
    data = garmin_client.get_vo2max(c, target)
    if _use_json(ctx):
        output(data)
    else:
        click.echo(format_vo2max(data))


@garmin.command()
@click.argument("date", default="")
@click.pass_context
def weight(ctx, date):
    """Body weight. Falls back to most recent logged entry if none today.

    DATE defaults to today.
    """
    target = date or _today()
    c = get_client()
    data = garmin_client.get_weight(c, target)
    if _use_json(ctx):
        output(data)
    else:
        click.echo(format_weight(data))


@garmin.command()
@click.argument("date", default="")
@click.pass_context
def steps(ctx, date):
    """Daily step count.

    DATE defaults to today.
    """
    target = date or _today()
    c = get_client()
    data = garmin_client.get_steps(c, target)
    if _use_json(ctx):
        output(data)
    else:
        click.echo(format_steps(data))


@garmin.command("intensity-minutes")
@click.argument("date", default="")
@click.pass_context
def intensity_minutes(ctx, date):
    """Daily and weekly intensity minutes.

    DATE defaults to today.
    """
    target = date or _today()
    c = get_client()
    data = garmin_client.get_intensity_minutes(c, target)
    if _use_json(ctx):
        output(data)
    else:
        click.echo(format_intensity_minutes(data))


@garmin.command()
@click.argument("date", default="")
@click.pass_context
def calories(ctx, date):
    """Daily calorie summary (total, active, BMR).

    DATE defaults to today.
    """
    target = date or _today()
    c = get_client()
    data = garmin_client.get_calories(c, target)
    if _use_json(ctx):
        output(data)
    else:
        click.echo(format_calories(data))


@garmin.command("race-predictions")
@click.pass_context
def race_predictions(ctx):
    """Latest race time predictions (5K, 10K, half, marathon)."""
    c = get_client()
    data = garmin_client.get_race_predictions(c)
    if _use_json(ctx):
        output(data)
    else:
        click.echo(format_race_predictions(data))


# --- Activity commands ---


@garmin.command()
@click.option("--limit", default=20, help="Number of activities")
@click.option("--start", default=0, help="Start index (for pagination)")
@click.option("--activity-type", default=None, help="Filter by activity type (e.g. running, cycling)")
@click.pass_context
def activities(ctx, limit, start, activity_type):
    """List recent activities."""
    c = get_client()
    data = garmin_client.get_activities(c, limit=limit, start=start, activity_type=activity_type)
    if _use_json(ctx):
        output(data)
    else:
        click.echo(format_activities(data))


@garmin.command()
@click.argument("activity_id", type=int)
@click.pass_context
def activity(ctx, activity_id):
    """Get detailed data for a specific activity."""
    c = get_client()
    data = garmin_client.get_activity(c, activity_id)
    if _use_json(ctx):
        output(data)
    else:
        click.echo(format_activity(data))


@garmin.command("activity-splits")
@click.argument("activity_id", type=int)
@click.pass_context
def activity_splits(ctx, activity_id):
    """Get lap splits for an activity."""
    c = get_client()
    data = garmin_client.get_activity_splits(c, activity_id)
    if _use_json(ctx):
        output(data)
    else:
        click.echo(format_activity_splits(data))


@garmin.command("activity-hr-zones")
@click.argument("activity_id", type=int)
@click.pass_context
def activity_hr_zones(ctx, activity_id):
    """Get HR zone breakdown for an activity."""
    c = get_client()
    data = garmin_client.get_activity_hr_zones(c, activity_id)
    if _use_json(ctx):
        output(data)
    else:
        click.echo(format_activity_hr_zones(data))


@garmin.command("activity-weather")
@click.argument("activity_id", type=int)
@click.pass_context
def activity_weather(ctx, activity_id):
    """Get weather conditions during an activity."""
    c = get_client()
    data = garmin_client.get_activity_weather(c, activity_id)
    if _use_json(ctx):
        output(data)
    else:
        click.echo(format_activity_weather(data))


@garmin.command("activity-details")
@click.argument("activity_id", type=int)
@click.pass_context
def activity_details(ctx, activity_id):
    """Get time-series data for an activity (like Strava streams)."""
    c = get_client()
    data = garmin_client.get_activity_details(c, activity_id)
    if _use_json(ctx):
        output(data)
    else:
        click.echo(format_activity_details(data))


@garmin.command("activity-running-dynamics")
@click.argument("activity_id", type=int)
@click.option("--segment-km", default=1.0, type=float, help="Segment size in km (default: 1.0)")
@click.pass_context
def activity_running_dynamics(ctx, activity_id, segment_km):
    """Per-segment running dynamics (cadence, GCT, vertical oscillation, etc.)."""
    c = get_client()
    data = garmin_client.get_activity_running_dynamics(c, activity_id, segment_km=segment_km)
    if _use_json(ctx):
        output(data)
    else:
        click.echo(format_activity_running_dynamics(data))


@garmin.command("activity-gear")
@click.argument("activity_id", type=int)
@click.pass_context
def activity_gear(ctx, activity_id):
    """Get gear used for an activity."""
    c = get_client()
    data = garmin_client.get_activity_gear(c, activity_id)
    if _use_json(ctx):
        output(data)
    else:
        click.echo(format_activity_gear(data))


# --- Daily training metrics ---


@garmin.command("lactate-threshold")
@click.pass_context
def lactate_threshold(ctx):
    """Latest lactate threshold HR and pace."""
    c = get_client()
    data = garmin_client.get_lactate_threshold(c)
    if _use_json(ctx):
        output(data)
    else:
        click.echo(format_lactate_threshold(data))


@garmin.command("training-status")
@click.argument("date", default="")
@click.pass_context
def training_status(ctx, date):
    """Training status, load balance, and ACWR.

    DATE defaults to today.
    """
    target = date or _today()
    c = get_client()
    data = garmin_client.get_training_status(c, target)
    if _use_json(ctx):
        output(data)
    else:
        click.echo(format_training_status(data))


@garmin.command("training-readiness")
@click.argument("date", default="")
@click.pass_context
def training_readiness(ctx, date):
    """Training readiness score.

    DATE defaults to today.
    """
    target = date or _today()
    c = get_client()
    data = garmin_client.get_training_readiness(c, target)
    if _use_json(ctx):
        output(data)
    else:
        click.echo(format_training_readiness(data))


@garmin.command("hill-score")
@click.argument("date", default="")
@click.pass_context
def hill_score(ctx, date):
    """Hill score (endurance + strength).

    DATE defaults to today.
    """
    target = date or _today()
    c = get_client()
    data = garmin_client.get_hill_score(c, target)
    if _use_json(ctx):
        output(data)
    else:
        click.echo(format_hill_score(data))
