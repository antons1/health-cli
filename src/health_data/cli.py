import click

from health_data.sources.garmin.commands import garmin


@click.group()
@click.version_option()
def main():
    """Fetch personal health data from various sources."""
    pass


main.add_command(garmin)
