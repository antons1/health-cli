import json
import os
import sys
import time
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from threading import Thread
from urllib.parse import urlparse, parse_qs

import logging

import click
from stravalib import Client

# Suppress stravalib warnings about missing env vars —
# we manage credentials ourselves via config files.
logging.getLogger("stravalib.client").setLevel(logging.ERROR)
logging.getLogger("root").setLevel(logging.ERROR)
os.environ["SILENCE_TOKEN_WARNINGS"] = "true"

CONFIG_DIR = Path(
    os.environ.get("STRAVA_CONFIG_DIR", "~/.garmin-health/strava")
).expanduser()

# OAuth2 callback server settings
# Port 5000 is used by AirPlay on macOS — use 8339 instead
CALLBACK_PORT = 8339
REDIRECT_URI = f"http://localhost:{CALLBACK_PORT}/callback"
SCOPES = "read,activity:read_all,profile:read_all"


def setup(client_id: str, client_secret: str):
    """Save Strava API credentials to config file.

    Get these from https://www.strava.com/settings/api
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    config_file = CONFIG_DIR / "config.json"
    config_file.write_text(json.dumps({
        "client_id": client_id,
        "client_secret": client_secret,
    }, indent=2))


def load_config() -> dict:
    """Load Strava API credentials from config file."""
    config_file = CONFIG_DIR / "config.json"
    if not config_file.exists():
        click.echo(
            "Strava not configured. Run: health strava setup",
            err=True,
        )
        sys.exit(1)
    return json.loads(config_file.read_text())


def save_tokens(tokens: dict):
    """Save OAuth2 tokens to disk."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    tokens_file = CONFIG_DIR / "tokens.json"
    tokens_file.write_text(json.dumps(tokens, indent=2))


def load_tokens() -> dict:
    """Load OAuth2 tokens from disk."""
    tokens_file = CONFIG_DIR / "tokens.json"
    if not tokens_file.exists():
        click.echo(
            "Not logged in to Strava. Run: health strava login",
            err=True,
        )
        sys.exit(1)
    return json.loads(tokens_file.read_text())


def login(code: str | None = None):
    """Run OAuth2 authorization flow.

    If code is provided, skips the browser flow and exchanges
    the code directly. Otherwise opens browser and starts a local
    HTTP server to catch the callback.
    """
    config = load_config()
    client = Client()

    if code is None:
        # Generate authorization URL
        auth_url = client.authorization_url(
            client_id=config["client_id"],
            redirect_uri=REDIRECT_URI,
            scope=SCOPES.split(","),
        )

        # Start local server to catch the OAuth callback
        code = _run_callback_server(auth_url)

    # Exchange auth code for tokens
    token_response = client.exchange_code_for_token(
        client_id=config["client_id"],
        client_secret=config["client_secret"],
        code=code,
    )

    save_tokens({
        "access_token": token_response["access_token"],
        "refresh_token": token_response["refresh_token"],
        "expires_at": token_response["expires_at"],
    })

    return client


def get_client() -> Client:
    """Get an authenticated Strava client.

    Loads saved tokens and refreshes automatically if expired.
    """
    config = load_config()
    tokens = load_tokens()

    client = Client()

    # Check if token is expired (with 60s buffer)
    if tokens["expires_at"] < time.time() + 60:
        # Refresh the token
        new_tokens = client.refresh_access_token(
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            refresh_token=tokens["refresh_token"],
        )
        tokens = {
            "access_token": new_tokens["access_token"],
            "refresh_token": new_tokens["refresh_token"],
            "expires_at": new_tokens["expires_at"],
        }
        save_tokens(tokens)

    client.access_token = tokens["access_token"]
    return client


def _run_callback_server(auth_url: str) -> str:
    """Start a local HTTP server, open browser, wait for OAuth callback.

    Returns the authorization code from the callback URL.
    """
    auth_code = None

    class CallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            nonlocal auth_code
            query = parse_qs(urlparse(self.path).query)

            if "code" in query:
                auth_code = query["code"][0]
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(
                    b"<html><body><h2>Authorization successful!</h2>"
                    b"<p>You can close this tab and return to the terminal.</p>"
                    b"</body></html>"
                )
            elif "error" in query:
                self.send_response(400)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                error = query.get("error", ["unknown"])[0]
                self.wfile.write(
                    f"<html><body><h2>Authorization failed: {error}</h2>"
                    f"</body></html>".encode()
                )
            else:
                self.send_response(404)
                self.end_headers()

        def log_message(self, format, *args):
            # Suppress default request logging
            pass

    server = HTTPServer(("localhost", CALLBACK_PORT), CallbackHandler)

    click.echo("Open this URL in your browser to authorize:", err=True)
    click.echo(auth_url, err=True)
    click.echo("", err=True)

    # Try to open browser automatically (may not work in all environments)
    webbrowser.open(auth_url)

    click.echo(f"Waiting for callback on port {CALLBACK_PORT}...", err=True)

    # Handle one request (the OAuth callback)
    server.handle_request()
    server.server_close()

    if auth_code is None:
        click.echo("Authorization failed — no code received.", err=True)
        sys.exit(1)

    return auth_code
