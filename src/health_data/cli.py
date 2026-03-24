import click


@click.group()
@click.version_option()
def main():
    """Fetch personal health data from various sources."""
    pass
