import sys
from functools import wraps

import click
from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError,
    GarminConnectConnectionError,
)


def api_call(fn):
    """Decorator that catches Garmin API errors and exits cleanly.

    Handles two error types:
    - GarminConnectAuthenticationError: token expired or invalid
    - GarminConnectConnectionError: network/server issue

    Prints the error to stderr and exits with code 1, keeping
    stdout clean for JSON output.
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except GarminConnectAuthenticationError:
            click.echo("Authentication failed. Run: health garmin login", err=True)
            sys.exit(1)
        except GarminConnectConnectionError as e:
            click.echo(f"Connection error: {e}", err=True)
            sys.exit(1)

    return wrapper


@api_call
def get_stats(client: Garmin, date_str: str):
    return client.get_stats(date_str)


@api_call
def get_heart_rates(client: Garmin, date_str: str):
    return client.get_heart_rates(date_str)


@api_call
def get_sleep(client: Garmin, date_str: str):
    return client.get_sleep_data(date_str)


@api_call
def get_stress(client: Garmin, date_str: str):
    return client.get_stress_data(date_str)


@api_call
def get_hrv(client: Garmin, date_str: str):
    return client.get_hrv_data(date_str)


@api_call
def get_spo2(client: Garmin, date_str: str):
    return client.get_spo2_data(date_str)


@api_call
def get_body_composition(client: Garmin, start_str: str, end_str: str = None):
    return client.get_body_composition(start_str, end_str)


@api_call
def get_activities(client: Garmin, start: int = 0, limit: int = 20):
    return client.get_activities(start, limit)


@api_call
def get_activity(client: Garmin, activity_id):
    return client.get_activity(activity_id)
