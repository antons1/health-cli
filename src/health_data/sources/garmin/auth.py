import os
import sys
from pathlib import Path

import click
from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError,
    GarminConnectConnectionError,
)

TOKEN_DIR = Path(
    os.environ.get("GARMIN_TOKEN_DIR", "~/.garmin-health/tokens")
).expanduser()


def login(email: str, password: str) -> Garmin:
    """Authenticate with Garmin Connect and persist OAuth tokens.

    The password is only used for the initial SSO handshake over HTTPS.
    Only OAuth tokens are saved to disk — the password is never persisted.
    """
    client = Garmin(email, password)
    try:
        client.login()
    except GarminConnectConnectionError as e:
        if "429" in str(e):
            click.echo(
                "Rate limited by Garmin. Wait 15-30 minutes and try again.",
                err=True,
            )
        else:
            click.echo(f"Connection error: {e}", err=True)
        sys.exit(1)
    except GarminConnectAuthenticationError as e:
        click.echo(f"Authentication failed: {e}", err=True)
        sys.exit(1)
    TOKEN_DIR.mkdir(parents=True, exist_ok=True)
    client.garth.dump(str(TOKEN_DIR))
    return client


def get_client() -> Garmin:
    """Load a Garmin client from saved OAuth tokens.

    Exits with code 1 if no saved tokens exist.
    """
    if not TOKEN_DIR.exists():
        click.echo("Not logged in. Run: health garmin login", err=True)
        sys.exit(1)
    client = Garmin()
    client.garth.load(str(TOKEN_DIR))
    try:
        client.login()
    except GarminConnectConnectionError as e:
        if "429" in str(e):
            click.echo(
                "Rate limited by Garmin. Wait 15-30 minutes and try again.",
                err=True,
            )
        else:
            click.echo(f"Connection error: {e}", err=True)
        sys.exit(1)
    except GarminConnectAuthenticationError as e:
        click.echo(
            "Saved tokens expired. Run: health garmin login", err=True
        )
        sys.exit(1)
    return client
