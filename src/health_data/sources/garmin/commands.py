from datetime import date

import click

from health_data.output import output
from health_data.sources.garmin.auth import get_client, login as do_login
from health_data.sources.garmin import client as garmin_client
from health_data.sources.garmin.client import (
    get_sleep, get_hrv, get_stress, get_body_battery, get_rhr,
    get_respiration, get_vo2max, get_weight, get_steps,
    get_intensity_minutes, get_calories, get_race_predictions,
)
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
    data = get_sleep(c, target)
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
    data = get_hrv(c, target)
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
    data = get_stress(c, target)
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
    data = get_body_battery(c, target)
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
    data = get_rhr(c, target)
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
    data = get_respiration(c, target)
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
    data = get_vo2max(c, target)
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
    data = get_weight(c, target)
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
    data = get_steps(c, target)
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
    data = get_intensity_minutes(c, target)
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
    data = get_calories(c, target)
    if _use_json(ctx):
        output(data)
    else:
        click.echo(format_calories(data))


@garmin.command("race-predictions")
@click.pass_context
def race_predictions(ctx):
    """Latest race time predictions (5K, 10K, half, marathon)."""
    c = get_client()
    data = get_race_predictions(c)
    if _use_json(ctx):
        output(data)
    else:
        click.echo(format_race_predictions(data))
