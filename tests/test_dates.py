from datetime import date, timedelta

import pytest

from health_data.dates import parse_date, DateParam


class TestParseDate:
    def test_iso_format(self):
        assert parse_date("2024-03-20") == date(2024, 3, 20)

    def test_today(self):
        assert parse_date("today") == date.today()

    def test_yesterday(self):
        assert parse_date("yesterday") == date.today() - timedelta(days=1)

    def test_relative_days(self):
        assert parse_date("-7d") == date.today() - timedelta(days=7)

    def test_relative_days_single(self):
        assert parse_date("-1d") == date.today() - timedelta(days=1)

    def test_relative_weeks(self):
        assert parse_date("-1w") == date.today() - timedelta(weeks=1)

    def test_relative_weeks_multiple(self):
        assert parse_date("-2w") == date.today() - timedelta(weeks=2)

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            parse_date("not-a-date")

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            parse_date("")


class TestDateParam:
    """DateParam is a click.ParamType that wraps parse_date."""

    def test_is_click_param_type(self):
        import click
        assert isinstance(DateParam(), click.ParamType)

    def test_converts_iso(self):
        param = DateParam()
        result = param.convert("2024-03-20", None, None)
        assert result == date(2024, 3, 20)

    def test_converts_keyword(self):
        param = DateParam()
        result = param.convert("today", None, None)
        assert result == date.today()

    def test_passes_through_date_object(self):
        """If the value is already a date, return it as-is."""
        param = DateParam()
        d = date(2024, 1, 1)
        assert param.convert(d, None, None) is d

    def test_invalid_fails(self):
        """click ParamType.fail raises click.exceptions.BadParameter."""
        import click
        param = DateParam()
        with pytest.raises(click.exceptions.BadParameter):
            param.convert("garbage", None, None)
