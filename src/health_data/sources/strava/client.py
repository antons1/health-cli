from stravalib import Client

# Default stream types to fetch — covers common fitness metrics.
DEFAULT_STREAM_TYPES = [
    "time",
    "latlng",
    "distance",
    "altitude",
    "velocity_smooth",
    "heartrate",
    "cadence",
    "watts",
    "temp",
    "moving",
    "grade_smooth",
]


def get_activities(client: Client, limit: int = 20) -> list[dict]:
    """Fetch recent activities as a list of dicts."""
    activities = client.get_activities(limit=limit)
    return [
        a.model_dump(exclude={"bound_client"}, exclude_none=True)
        for a in activities
    ]


def get_activity(client: Client, activity_id: int) -> dict:
    """Fetch detailed data for a single activity."""
    activity = client.get_activity(activity_id)
    return activity.model_dump(exclude={"bound_client"}, exclude_none=True)


def get_streams(
    client: Client,
    activity_id: int,
    types: list[str] | None = None,
) -> dict:
    """Fetch second-by-second time-series data for an activity.

    Returns a dict mapping stream type names to lists of values.
    E.g. {"heartrate": [120, 125, ...], "time": [0, 1, ...]}
    """
    if types is None:
        types = DEFAULT_STREAM_TYPES

    streams = client.get_activity_streams(
        activity_id,
        types=types,
    )

    return {name: stream.data for name, stream in streams.items()}
