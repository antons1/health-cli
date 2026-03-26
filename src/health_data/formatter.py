"""Human-readable formatting for health data.

Converts raw JSON data (meters, seconds, m/s) into readable
strings (km, mm:ss, min/km pace) and formats as tables or
key-value blocks.
"""

from tabulate import tabulate


# --- Unit conversion helpers ---

def format_distance(meters):
    """Meters to km (or m if short). Returns string."""
    if meters is None:
        return "-"
    if meters < 1000:
        return f"{meters:.0f} m"
    return f"{meters / 1000:.1f} km"


def format_duration(seconds):
    """Seconds to h:mm:ss or mm:ss. Returns string."""
    if seconds is None:
        return "-"
    seconds = int(seconds)
    h, remainder = divmod(seconds, 3600)
    m, s = divmod(remainder, 60)
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def format_pace(speed_ms):
    """m/s to min:ss/km pace. Returns string."""
    if not speed_ms:
        return "-"
    pace_seconds = 1000 / speed_ms
    m, s = divmod(int(pace_seconds), 60)
    return f"{m}:{s:02d}/km"


def _format_date(value):
    """Datetime or ISO string to 'YYYY-MM-DD HH:MM'."""
    if not value:
        return "-"
    from datetime import datetime
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M")
    # Fall back to string slicing for ISO strings
    return str(value)[:16].replace("T", " ")


def _val(data, key, fmt=None):
    """Extract a value from dict, format it, or return '-'."""
    v = data.get(key)
    if v is None:
        return "-"
    if fmt == "dist":
        return format_distance(v)
    if fmt == "dur":
        return format_duration(v)
    if fmt == "pace":
        return format_pace(v)
    if fmt == "hr":
        return f"{v:.0f} bpm"
    if fmt == "int":
        return f"{int(v)}"
    if fmt == "elev":
        return f"{v:.0f} m"
    if fmt == "cal":
        return f"{v:.0f} kcal"
    if fmt == "cad":
        return f"{v:.0f} spm"
    if fmt == "temp":
        return f"{v:.0f}°C"
    return str(v)


# --- List formatting ---

def format_activities(activities):
    """Format activity list as a table."""
    if not activities:
        return "No activities found."

    rows = []
    for a in activities:
        rows.append([
            a.get("id", "-"),
            _format_date(a.get("start_date_local")),
            a.get("name", "-"),
            a.get("sport_type", a.get("type", "-")),
            format_distance(a.get("distance")),
            format_duration(a.get("moving_time")),
            _val(a, "average_heartrate", "int"),
            _val(a, "total_elevation_gain", "elev"),
        ])

    headers = ["ID", "Date", "Name", "Type", "Distance", "Time", "Avg HR", "Elev"]
    return tabulate(rows, headers=headers, tablefmt="simple")


# --- Detail formatting ---

def format_activity(activity):
    """Format a single activity as key-value pairs."""
    lines = []
    name = activity.get("name", "Activity")
    sport = activity.get("sport_type", activity.get("type", ""))
    lines.append(f"{name}  ({sport})")
    lines.append("")

    fields = [
        ("Date", _format_date(activity.get("start_date_local"))),
        ("Distance", _val(activity, "distance", "dist")),
        ("Moving time", _val(activity, "moving_time", "dur")),
        ("Elapsed time", _val(activity, "elapsed_time", "dur")),
        ("Avg pace", _val(activity, "average_speed", "pace")),
        ("Max pace", _val(activity, "max_speed", "pace")),
        ("Avg HR", _val(activity, "average_heartrate", "hr")),
        ("Max HR", _val(activity, "max_heartrate", "hr")),
        ("Cadence", _val(activity, "average_cadence", "cad")),
        ("Elevation", _val(activity, "total_elevation_gain", "elev")),
        ("Calories", _val(activity, "calories", "cal")),
        ("Temperature", _val(activity, "average_temp", "temp")),
    ]

    # Filter out fields with "-" value to keep output clean
    fields = [(k, v) for k, v in fields if v != "-"]
    if fields:
        max_label = max(len(k) for k, _ in fields)
        for label, value in fields:
            lines.append(f"  {label:<{max_label}}  {value}")

    return "\n".join(lines)


# --- Gear formatting ---

def format_gear(gear):
    """Format gear details as key-value pairs."""
    name = gear.get("name", "Gear")
    lines = [name, ""]

    fields = [
        ("Brand", gear.get("brand_name")),
        ("Model", gear.get("model_name")),
        ("Distance", format_distance(gear.get("distance"))),
        ("Type", gear.get("resource_state") and gear.get("type")),
    ]
    fields = [(k, v) for k, v in fields if v and v != "-"]
    if fields:
        max_label = max(len(k) for k, _ in fields)
        for label, value in fields:
            lines.append(f"  {label:<{max_label}}  {value}")
    return "\n".join(lines)


# --- Athlete stats formatting ---

def format_athlete_stats(stats):
    """Format athlete statistics as a table."""
    if not stats:
        return "No stats available."

    categories = [
        ("all", "All time"),
        ("ytd", "YTD"),
        ("recent", "Last 4 wk"),
    ]
    sport_types = ["run", "ride", "swim"]
    rows = []
    for sport in sport_types:
        for prefix, period_label in categories:
            key = f"{prefix}_{sport}_totals"
            totals = stats.get(key, {})
            if not totals or not totals.get("count"):
                continue
            rows.append([
                sport.capitalize(),
                period_label,
                totals.get("count", 0),
                format_distance(totals.get("distance")),
                format_duration(totals.get("moving_time")),
                _val(totals, "elevation_gain", "elev"),
            ])

    if not rows:
        return "No stats available."

    headers = ["Sport", "Period", "Count", "Distance", "Time", "Elev"]
    return tabulate(rows, headers=headers, tablefmt="simple")


# --- Laps formatting ---

def format_laps(laps):
    """Format activity laps as a table."""
    if not laps:
        return "No laps found."

    rows = []
    for lap in laps:
        rows.append([
            lap.get("name", "-"),
            format_distance(lap.get("distance")),
            format_duration(lap.get("elapsed_time")),
            _val(lap, "average_heartrate", "int"),
            _val(lap, "average_speed", "pace"),
        ])

    headers = ["Name", "Distance", "Time", "Avg HR", "Pace"]
    return tabulate(rows, headers=headers, tablefmt="simple")


# --- Zones formatting ---

def format_zones(zones):
    """Format heart rate and power zones."""
    if not zones:
        return "No zone data available."

    lines = []
    hr = zones.get("heart_rate", {})
    if hr and hr.get("zones"):
        lines.append("Heart Rate Zones")
        for i, z in enumerate(hr["zones"], 1):
            max_val = z.get("max", -1)
            max_str = str(max_val) if max_val > 0 else "∞"
            lines.append(f"  Z{i}  {z.get('min', 0)}–{max_str} bpm")

    power = zones.get("power", {})
    if power and power.get("zones"):
        if lines:
            lines.append("")
        lines.append("Power Zones")
        for i, z in enumerate(power["zones"], 1):
            max_val = z.get("max", -1)
            max_str = str(max_val) if max_val > 0 else "∞"
            lines.append(f"  Z{i}  {z.get('min', 0)}–{max_str} W")

    if not lines:
        return "No zone data available."
    return "\n".join(lines)


# --- Clubs formatting ---

def format_clubs(clubs):
    """Format clubs as a table."""
    if not clubs:
        return "No clubs found."

    rows = []
    for c in clubs:
        rows.append([
            c.get("id", "-"),
            c.get("name", "-"),
            c.get("sport_type", "-"),
            c.get("member_count", "-"),
        ])

    headers = ["ID", "Name", "Sport", "Members"]
    return tabulate(rows, headers=headers, tablefmt="simple")


# --- Routes formatting ---

def format_routes(routes):
    """Format route list as a table."""
    if not routes:
        return "No routes found."

    rows = []
    for r in routes:
        rows.append([
            r.get("id", "-"),
            r.get("name", "-"),
            format_distance(r.get("distance")),
            _val(r, "elevation_gain", "elev"),
        ])

    headers = ["ID", "Name", "Distance", "Elev"]
    return tabulate(rows, headers=headers, tablefmt="simple")


def format_route(route):
    """Format a single route as key-value pairs."""
    name = route.get("name", "Route")
    lines = [name, ""]

    fields = [
        ("Distance", _val(route, "distance", "dist")),
        ("Elevation", _val(route, "elevation_gain", "elev")),
        ("Description", route.get("description")),
    ]
    fields = [(k, v) for k, v in fields if v and v != "-"]
    if fields:
        max_label = max(len(k) for k, _ in fields)
        for label, value in fields:
            lines.append(f"  {label:<{max_label}}  {value}")
    return "\n".join(lines)


# --- Segment formatting ---

def format_segment(segment):
    """Format a segment as key-value pairs."""
    name = segment.get("name", "Segment")
    lines = [name, ""]

    fields = [
        ("Distance", _val(segment, "distance", "dist")),
        ("Avg grade", f"{segment['average_grade']}%" if segment.get("average_grade") is not None else None),
        ("Max grade", f"{segment['maximum_grade']}%" if segment.get("maximum_grade") is not None else None),
        ("Elev high", _val(segment, "elevation_high", "elev")),
        ("Elev low", _val(segment, "elevation_low", "elev")),
        ("Climb cat", str(segment.get("climb_category")) if segment.get("climb_category") is not None else None),
    ]
    fields = [(k, v) for k, v in fields if v and v != "-"]
    if fields:
        max_label = max(len(k) for k, _ in fields)
        for label, value in fields:
            lines.append(f"  {label:<{max_label}}  {value}")
    return "\n".join(lines)


def format_segments(segments):
    """Format segment list as a table."""
    if not segments:
        return "No segments found."

    rows = []
    for s in segments:
        rows.append([
            s.get("id", "-"),
            s.get("name", "-"),
            format_distance(s.get("distance")),
            f"{s['average_grade']}%" if s.get("average_grade") is not None else "-",
        ])

    headers = ["ID", "Name", "Distance", "Avg Grade"]
    return tabulate(rows, headers=headers, tablefmt="simple")


# --- Streams formatting ---

def format_streams(streams):
    """Format streams as a summary table (count, min, avg, max)."""
    if not streams:
        return "No stream data available."

    rows = []
    for name, data in streams.items():
        if not data or name == "latlng":
            continue
        nums = [v for v in data if isinstance(v, (int, float))]
        if nums:
            rows.append([
                name,
                len(nums),
                f"{min(nums):.1f}",
                f"{sum(nums) / len(nums):.1f}",
                f"{max(nums):.1f}",
            ])

    if not rows:
        return "No stream data available."

    headers = ["Stream", "Points", "Min", "Avg", "Max"]
    return tabulate(rows, headers=headers, tablefmt="simple")
