from datetime import datetime
from pathlib import Path

import click

from health_data.output import output
from health_data.formatter import (
    format_activities,
    format_activity,
    format_streams,
    format_gear,
    format_gear_list,
    format_athlete_stats,
    format_laps,
    format_zones,
    format_clubs,
    format_routes,
    format_route,
    format_segment,
    format_segments,
)
from health_data.sources.strava.auth import (
    setup as do_setup,
    login as do_login,
    get_client,
)
from health_data.sources.strava import client as strava_client


def _use_json(ctx):
    """Check if --json flag was set on the top-level command."""
    return ctx.obj and ctx.obj.get("json", False)


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
@click.option("--after", default=None, type=click.DateTime(), help="Only activities after this date (YYYY-MM-DD)")
@click.option("--before", default=None, type=click.DateTime(), help="Only activities before this date (YYYY-MM-DD)")
@click.pass_context
def activities(ctx, limit, after, before):
    """List recent activities."""
    c = get_client()
    data = strava_client.get_activities(c, limit=limit, before=before, after=after)
    if _use_json(ctx):
        output(data)
    else:
        click.echo(format_activities(data))


@strava.command()
@click.argument("activity_id", type=int)
@click.pass_context
def activity(ctx, activity_id):
    """Get detailed data for a specific activity."""
    c = get_client()
    data = strava_client.get_activity(c, activity_id)
    if _use_json(ctx):
        output(data)
    else:
        click.echo(format_activity(data))


@strava.command()
@click.argument("activity_id", type=int)
@click.option(
    "--types",
    default=None,
    help="Comma-separated stream types (e.g. heartrate,watts,time)",
)
@click.pass_context
def streams(ctx, activity_id, types):
    """Get second-by-second time-series data for an activity.

    Available types: time, latlng, distance, altitude, velocity_smooth,
    heartrate, cadence, watts, temp, moving, grade_smooth.
    """
    type_list = types.split(",") if types else None
    c = get_client()
    data = strava_client.get_streams(c, activity_id, types=type_list)
    if _use_json(ctx):
        output(data)
    else:
        click.echo(format_streams(data))


@strava.command("gear-list")
@click.pass_context
def gear_list(ctx):
    """List all your gear (bikes and shoes)."""
    c = get_client()
    data = strava_client.get_gear_list(c)
    if _use_json(ctx):
        output(data)
    else:
        click.echo(format_gear_list(data))


@strava.command()
@click.argument("gear_id")
@click.pass_context
def gear(ctx, gear_id):
    """Get gear details (shoes, bikes, etc.)."""
    c = get_client()
    data = strava_client.get_gear(c, gear_id)
    if _use_json(ctx):
        output(data)
    else:
        click.echo(format_gear(data))


@strava.command("athlete-stats")
@click.pass_context
def athlete_stats(ctx):
    """Athlete statistics (totals, records by sport)."""
    c = get_client()
    data = strava_client.get_athlete_stats(c)
    if _use_json(ctx):
        output(data)
    else:
        click.echo(format_athlete_stats(data))


@strava.command()
@click.argument("activity_id", type=int)
@click.pass_context
def laps(ctx, activity_id):
    """Get laps for an activity."""
    c = get_client()
    data = strava_client.get_laps(c, activity_id)
    if _use_json(ctx):
        output(data)
    else:
        click.echo(format_laps(data))


@strava.command()
@click.pass_context
def zones(ctx):
    """Heart rate and power zones."""
    c = get_client()
    data = strava_client.get_zones(c)
    if _use_json(ctx):
        output(data)
    else:
        click.echo(format_zones(data))


@strava.command()
@click.pass_context
def clubs(ctx):
    """List your clubs."""
    c = get_client()
    data = strava_client.get_clubs(c)
    if _use_json(ctx):
        output(data)
    else:
        click.echo(format_clubs(data))


@strava.command()
@click.pass_context
def routes(ctx):
    """List your routes."""
    c = get_client()
    data = strava_client.get_routes(c)
    if _use_json(ctx):
        output(data)
    else:
        click.echo(format_routes(data))


@strava.command()
@click.argument("route_id", type=int)
@click.pass_context
def route(ctx, route_id):
    """Get details for a route."""
    c = get_client()
    data = strava_client.get_route(c, route_id)
    if _use_json(ctx):
        output(data)
    else:
        click.echo(format_route(data))


@strava.command()
@click.argument("segment_id", type=int)
@click.pass_context
def segment(ctx, segment_id):
    """Get segment details."""
    c = get_client()
    data = strava_client.get_segment(c, segment_id)
    if _use_json(ctx):
        output(data)
    else:
        click.echo(format_segment(data))


@strava.command()
@click.option(
    "--bounds", required=True,
    help="Bounding box: south_lat,west_lng,north_lat,east_lng",
)
@click.pass_context
def segments(ctx, bounds):
    """Explore segments in a geographic area."""
    parts = tuple(float(x) for x in bounds.split(","))
    c = get_client()
    data = strava_client.explore_segments(c, parts)
    if _use_json(ctx):
        output(data)
    else:
        click.echo(format_segments(data))


# --- Write commands ---


@strava.command("create-activity")
@click.option("--name", required=True, help="Activity name")
@click.option("--sport-type", required=True, help="Sport type (e.g. Run, Ride, Swim)")
@click.option("--start", required=True, help="Start time (ISO format, e.g. 2026-03-25T08:00:00)")
@click.option("--elapsed-time", required=True, type=int, help="Elapsed time in seconds")
@click.option("--distance", type=float, default=None, help="Distance in meters")
@click.option("--description", default=None, help="Activity description")
@click.option("--rpe", type=click.IntRange(1, 10), default=None, help="Rate of perceived exertion (1-10)")
@click.pass_context
def create_activity(ctx, name, sport_type, start, elapsed_time, distance, description, rpe):
    """Create a manual activity."""
    start_date = datetime.fromisoformat(start)
    c = get_client()
    data = strava_client.create_activity(
        c,
        name=name,
        sport_type=sport_type,
        start_date=start_date,
        elapsed_time=elapsed_time,
        distance=distance,
        description=description,
        perceived_exertion=rpe,
    )
    if _use_json(ctx):
        output(data)
    else:
        click.echo(format_activity(data))


@strava.command("update-activity")
@click.argument("activity_id", type=int)
@click.option("--name", default=None, help="New name")
@click.option("--sport-type", default=None, help="New sport type")
@click.option("--description", default=None, help="New description")
@click.option("--gear-id", default=None, help="Gear ID to assign")
@click.option("--rpe", type=click.IntRange(1, 10), default=None, help="Rate of perceived exertion (1-10)")
@click.pass_context
def update_activity(ctx, activity_id, name, sport_type, description, gear_id, rpe):
    """Update an existing activity."""
    kwargs = {}
    if name is not None:
        kwargs["name"] = name
    if sport_type is not None:
        kwargs["sport_type"] = sport_type
    if description is not None:
        kwargs["description"] = description
    if gear_id is not None:
        kwargs["gear_id"] = gear_id
    if rpe is not None:
        kwargs["perceived_exertion"] = rpe

    if not kwargs:
        click.echo("No fields to update. Use --name, --sport-type, --description, --gear-id, or --rpe.", err=True)
        return

    c = get_client()
    data = strava_client.update_activity(c, activity_id, **kwargs)
    if _use_json(ctx):
        output(data)
    else:
        click.echo(format_activity(data))


@strava.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--data-type", default=None, help="File type: fit, tcx, gpx (auto-detected from extension)")
@click.option("--name", default=None, help="Activity name")
@click.option("--description", default=None, help="Activity description")
@click.pass_context
def upload(ctx, file, data_type, name, description):
    """Upload a GPS file (FIT, TCX, GPX)."""
    if data_type is None:
        ext = Path(file).suffix.lower().lstrip(".")
        if ext in ("fit", "tcx", "gpx"):
            data_type = ext
        else:
            click.echo(f"Cannot detect file type from extension '.{ext}'. Use --data-type.", err=True)
            return

    c = get_client()
    click.echo(f"Uploading {file}...", err=True)
    data = strava_client.upload_activity(
        c, file, data_type=data_type, name=name, description=description
    )
    if _use_json(ctx):
        output(data)
    else:
        click.echo(format_activity(data))
