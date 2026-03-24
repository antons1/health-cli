import click

from health_data.output import output
from health_data.sources.strava.auth import (
    setup as do_setup,
    login as do_login,
    get_client,
)
from health_data.sources.strava import client as strava_client


@click.group()
def strava():
    """Strava data."""
    pass


@strava.command()
@click.option("--client-id", prompt="Client ID")
@click.option("--client-secret", prompt="Client Secret")
def setup(client_id, client_secret):
    """Save Strava API credentials.

    Get these from https://www.strava.com/settings/api
    """
    do_setup(client_id, client_secret)
    click.echo("Strava credentials saved.", err=True)


@strava.command()
@click.option("--code", default=None, help="Auth code from callback URL (skips browser flow)")
def login(code):
    """Authorize with Strava via OAuth2 (opens browser).

    If the browser callback doesn't work, copy the 'code' parameter
    from the callback URL and pass it with --code.
    """
    do_login(code=code)
    click.echo("Strava login successful.", err=True)


@strava.command()
@click.option("--limit", default=20, help="Number of activities")
def activities(limit):
    """List recent activities."""
    c = get_client()
    output(strava_client.get_activities(c, limit=limit))


@strava.command()
@click.argument("activity_id", type=int)
def activity(activity_id):
    """Get detailed data for a specific activity."""
    c = get_client()
    output(strava_client.get_activity(c, activity_id))


@strava.command()
@click.argument("activity_id", type=int)
@click.option(
    "--types",
    default=None,
    help="Comma-separated stream types (e.g. heartrate,watts,time)",
)
def streams(activity_id, types):
    """Get second-by-second time-series data for an activity.

    Available types: time, latlng, distance, altitude, velocity_smooth,
    heartrate, cadence, watts, temp, moving, grade_smooth.
    """
    type_list = types.split(",") if types else None
    c = get_client()
    output(strava_client.get_streams(c, activity_id, types=type_list))
