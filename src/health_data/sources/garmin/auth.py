import json
import os
import sys
from pathlib import Path

import click
from garminconnect import Garmin

CONFIG_DIR = Path(
    os.environ.get("GARMIN_CONFIG_DIR", "~/.health-data/garmin")
).expanduser()


def save_config(email: str):
    """Save Garmin email to config.json."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    config_file = CONFIG_DIR / "config.json"
    config_file.write_text(json.dumps({"email": email}, indent=2))
    config_file.chmod(0o600)


def load_config() -> dict:
    """Load Garmin config. Exits with error if not configured."""
    config_file = CONFIG_DIR / "config.json"
    if not config_file.exists():
        click.echo("Garmin not configured. Run: health garmin login", err=True)
        sys.exit(1)
    return json.loads(config_file.read_text())


def login(email: str, password: str) -> Garmin:
    """Authenticate with Garmin, save tokens and email to config dir."""
    client = Garmin(email, password)
    client.login(tokenstore=str(CONFIG_DIR))
    client.client.dump(str(CONFIG_DIR))  # persist tokens to disk
    save_config(email)
    return client


def get_client() -> Garmin:
    """Return an authenticated Garmin client using saved tokens."""
    config = load_config()
    client = Garmin(config["email"])
    client.login(tokenstore=str(CONFIG_DIR))
    return client
