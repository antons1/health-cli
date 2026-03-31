from datetime import datetime

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


def get_activities(
    client: Client,
    limit: int = 20,
    before: datetime | None = None,
    after: datetime | None = None,
) -> list[dict]:
    """Fetch recent activities as a list of dicts."""
    kwargs: dict = {"limit": limit}
    if before is not None:
        kwargs["before"] = before
    if after is not None:
        kwargs["after"] = after
    activities = client.get_activities(**kwargs)
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


def get_gear_list(client: Client) -> list[dict]:
    """Fetch all gear (bikes and shoes) from athlete profile."""
    athlete = client.get_athlete()
    gear = []
    for item in list(athlete.bikes or []) + list(athlete.shoes or []):
        gear.append(item.model_dump(exclude={"bound_client"}, exclude_none=True))
    return gear


def get_gear(client: Client, gear_id: str) -> dict:
    """Fetch gear details (shoes, bikes, etc.)."""
    gear = client.get_gear(gear_id)
    return gear.model_dump(exclude={"bound_client"}, exclude_none=True)


def get_athlete_stats(client: Client) -> dict:
    """Fetch athlete statistics (totals, records)."""
    athlete = client.get_athlete()
    stats = client.get_athlete_stats(athlete.id)
    return stats.model_dump(exclude={"bound_client"}, exclude_none=True)


def get_laps(client: Client, activity_id: int) -> list[dict]:
    """Fetch laps for an activity."""
    laps = client.get_activity_laps(activity_id)
    return [
        lap.model_dump(exclude={"bound_client"}, exclude_none=True)
        for lap in laps
    ]


def get_zones(client: Client) -> dict:
    """Fetch athlete heart rate and power zones."""
    zones = client.get_athlete_zones()
    return zones.model_dump(exclude={"bound_client"}, exclude_none=True)


def get_clubs(client: Client) -> list[dict]:
    """Fetch athlete's clubs."""
    clubs = client.get_athlete_clubs()
    return [
        club.model_dump(exclude={"bound_client"}, exclude_none=True)
        for club in clubs
    ]


def get_routes(client: Client) -> list[dict]:
    """Fetch athlete's routes."""
    routes = client.get_routes()
    return [
        route.model_dump(exclude={"bound_client"}, exclude_none=True)
        for route in routes
    ]


def get_route(client: Client, route_id: int) -> dict:
    """Fetch details for a single route."""
    route = client.get_route(route_id)
    return route.model_dump(exclude={"bound_client"}, exclude_none=True)


def get_segment(client: Client, segment_id: int) -> dict:
    """Fetch segment details."""
    segment = client.get_segment(segment_id)
    return segment.model_dump(exclude={"bound_client"}, exclude_none=True)


def explore_segments(
    client: Client, bounds: tuple[float, float, float, float]
) -> list[dict]:
    """Explore segments in a geographic area.

    bounds: (south_lat, west_lng, north_lat, east_lng)
    """
    result = client.explore_segments(bounds)
    return [
        seg.model_dump(exclude={"bound_client"}, exclude_none=True)
        for seg in result.segments
    ]


# --- Write operations ---


def create_activity(
    client: Client,
    name: str,
    sport_type: str,
    start_date: datetime,
    elapsed_time: int,
    distance: float | None = None,
    description: str | None = None,
) -> dict:
    """Create a manual activity."""
    kwargs = {
        "name": name,
        "sport_type": sport_type,
        "start_date_local": start_date,
        "elapsed_time": elapsed_time,
    }
    if distance is not None:
        kwargs["distance"] = distance
    if description is not None:
        kwargs["description"] = description

    activity = client.create_activity(**kwargs)
    return activity.model_dump(exclude={"bound_client"}, exclude_none=True)


def update_activity(client: Client, activity_id: int, **kwargs) -> dict:
    """Update an existing activity."""
    activity = client.update_activity(activity_id, **kwargs)
    return activity.model_dump(exclude={"bound_client"}, exclude_none=True)


def upload_activity(
    client: Client,
    file_path: str,
    data_type: str = "fit",
    name: str | None = None,
    description: str | None = None,
) -> dict:
    """Upload a GPS file (FIT, TCX, GPX)."""
    with open(file_path, "rb") as f:
        upload = client.upload_activity(
            activity_file=f,
            data_type=data_type,
            name=name,
            description=description,
        )
    result = upload.wait()
    return result.model_dump(exclude={"bound_client"}, exclude_none=True)
