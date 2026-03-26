import click

from health_data.sources.strava.commands import strava


@click.group()
@click.version_option()
@click.option("--json", "use_json", is_flag=True, default=False,
              help="Output raw JSON instead of human-readable format")
@click.pass_context
def main(ctx, use_json):
    """Fetch personal health data from various sources."""
    ctx.ensure_object(dict)
    ctx.obj["json"] = use_json


main.add_command(strava)
