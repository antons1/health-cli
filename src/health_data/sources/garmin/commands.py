import click

from health_data.dates import DateParam
from health_data.output import output
from health_data.sources.garmin.auth import get_client, login as do_login


@click.group()
def garmin():
    """Garmin Connect data."""
    pass


@garmin.command()
@click.option("--email", prompt=True)
@click.option("--password", prompt=True, hide_input=True)
def login(email, password):
    """Authenticate with Garmin Connect."""
    do_login(email, password)
    click.echo("Logged in successfully.", err=True)


@garmin.command()
@click.argument("date", type=DateParam(), default="today")
def stats(date):
    """Daily stats (steps, calories, distance, floors, active minutes)."""
    c = get_client()
    output(c.get_stats(date.isoformat()))


@garmin.command()
@click.argument("date", type=DateParam(), default="today")
def sleep(date):
    """Sleep data (stages, duration, score)."""
    c = get_client()
    output(c.get_sleep_data(date.isoformat()))


@garmin.command("heart-rate")
@click.argument("date", type=DateParam(), default="today")
def heart_rate(date):
    """Heart rate data (resting HR, all-day HR)."""
    c = get_client()
    output(c.get_heart_rates(date.isoformat()))


@garmin.command()
@click.argument("date", type=DateParam(), default="today")
def stress(date):
    """Stress data."""
    c = get_client()
    output(c.get_stress_data(date.isoformat()))


@garmin.command()
@click.argument("date", type=DateParam(), default="today")
def hrv(date):
    """Heart rate variability data."""
    c = get_client()
    output(c.get_hrv_data(date.isoformat()))


@garmin.command()
@click.argument("date", type=DateParam(), default="today")
def spo2(date):
    """Blood oxygen saturation data."""
    c = get_client()
    output(c.get_spo2_data(date.isoformat()))


@garmin.command("weight")
@click.argument("date", type=DateParam(), default="today")
@click.option("--end", type=DateParam(), default=None, help="End date for range query")
def weight(date, end):
    """Body composition and weight data."""
    c = get_client()
    end_str = end.isoformat() if end else None
    output(c.get_body_composition(date.isoformat(), end_str))


@garmin.command()
@click.option("--limit", default=20, help="Number of activities")
def activities(limit):
    """List recent activities."""
    c = get_client()
    output(c.get_activities(0, limit))


@garmin.command()
@click.argument("activity_id")
def activity(activity_id):
    """Get detailed data for a specific activity."""
    c = get_client()
    output(c.get_activity(activity_id))
