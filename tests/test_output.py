import json
from datetime import date, datetime

from health_data.output import output


class TestOutput:
    def test_dict_output(self, capsys):
        """Simple dict is printed as JSON to stdout."""
        output({"steps": 10000})
        captured = capsys.readouterr()
        assert json.loads(captured.out) == {"steps": 10000}
        assert captured.err == ""

    def test_list_output(self, capsys):
        """A list is printed as a JSON array."""
        output([1, 2, 3])
        captured = capsys.readouterr()
        assert json.loads(captured.out) == [1, 2, 3]

    def test_date_serialization(self, capsys):
        """datetime.date objects are serialized to ISO format strings."""
        output({"date": date(2024, 3, 20)})
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed["date"] == "2024-03-20"

    def test_datetime_serialization(self, capsys):
        """datetime.datetime objects are serialized to ISO format strings."""
        output({"timestamp": datetime(2024, 3, 20, 14, 30, 0)})
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed["timestamp"] == "2024-03-20T14:30:00"

    def test_nested_structure(self, capsys):
        """Nested dicts/lists with dates serialize correctly."""
        data = {
            "sleep": {
                "date": date(2024, 3, 20),
                "stages": [{"stage": "deep", "duration": 3600}],
            }
        }
        output(data)
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed["sleep"]["date"] == "2024-03-20"
        assert parsed["sleep"]["stages"][0]["stage"] == "deep"

    def test_output_is_valid_json(self, capsys):
        """Output is always parseable JSON."""
        output({"key": "value", "number": 42, "flag": True, "empty": None})
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed["flag"] is True
        assert parsed["empty"] is None
