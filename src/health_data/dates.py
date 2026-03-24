import re
from datetime import date, timedelta

import click

# Matches "-7d", "-1w", etc.
_RELATIVE_RE = re.compile(r"^-(\d+)([dw])$")


def parse_date(value: str) -> date:
    """Parse a user-friendly date string into a date object.

    Supported formats:
        - ISO: "2024-03-20"
        - Keywords: "today", "yesterday"
        - Relative: "-7d" (7 days ago), "-1w" (1 week ago)
    """
    if value == "today":
        return date.today()

    if value == "yesterday":
        return date.today() - timedelta(days=1)

    match = _RELATIVE_RE.fullmatch(value)
    if match:
        amount = int(match.group(1))
        unit = match.group(2)
        if unit == "d":
            return date.today() - timedelta(days=amount)
        if unit == "w":
            return date.today() - timedelta(weeks=amount)

    try:
        return date.fromisoformat(value)
    except ValueError:
        raise ValueError(f"Invalid date format: {value!r}")


class DateParam(click.ParamType):
    """Click parameter type that parses user-friendly date strings."""

    name = "date"

    def convert(self, value, param, ctx):
        if isinstance(value, date):
            return value
        try:
            return parse_date(value)
        except ValueError as e:
            self.fail(str(e), param, ctx)
