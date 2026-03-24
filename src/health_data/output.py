import json
import sys
from datetime import date, datetime


def output(data):
    """Print data as JSON to stdout."""
    print(json.dumps(data, indent=2, default=_serializer))


def _serializer(obj):
    """Fallback serializer for json.dumps.

    Called for objects that json.dumps doesn't handle natively.
    """
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    raise TypeError(f"Not JSON serializable: {type(obj)}")
