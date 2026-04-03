from tabulate import tabulate


def _qualifier(key: str | None) -> str:
    if not key:
        return "-"
    return key.replace("_", " ").title()


def _val(v) -> str:
    if v is None:
        return "-"
    return str(v)


def _kv_table(rows: list[tuple]) -> str:
    return tabulate(rows, tablefmt="plain")


def format_sleep(data: dict) -> str:
    rows = [
        ("Date", data.get("date", "-")),
        ("Score", f"{_val(data.get('score'))}  {_qualifier(data.get('score_qualifier'))}"),
        ("Total", _val(data.get("total"))),
        ("Deep", _val(data.get("deep"))),
        ("Light", _val(data.get("light"))),
        ("REM", _val(data.get("rem"))),
        ("Awake", _val(data.get("awake"))),
        ("Avg stress", _val(data.get("avg_stress"))),
        ("Feedback", _qualifier(data.get("feedback"))),
    ]
    return _kv_table(rows)


def format_hrv(data: dict) -> str:
    baseline_low = data.get("baseline_low")
    baseline_high = data.get("baseline_high")
    baseline = f"{baseline_low}–{baseline_high}" if baseline_low and baseline_high else "-"
    rows = [
        ("Date", data.get("date", "-")),
        ("Last night", _val(data.get("last_night_avg"))),
        ("Weekly avg", _val(data.get("weekly_avg"))),
        ("Status", _qualifier(data.get("status"))),
        ("Baseline", baseline),
    ]
    return _kv_table(rows)


def format_stress(data: dict) -> str:
    rows = [
        ("Date", data.get("date", "-")),
        ("Avg", _val(data.get("avg"))),
        ("Max", _val(data.get("max"))),
    ]
    return _kv_table(rows)


def format_body_battery(data: dict) -> str:
    rows = [
        ("Date", data.get("date", "-")),
        ("Charged", _val(data.get("charged"))),
        ("Drained", _val(data.get("drained"))),
        ("Peak", _val(data.get("peak"))),
        ("End of day", _val(data.get("end"))),
    ]
    return _kv_table(rows)


def format_rhr(data: dict) -> str:
    rhr = data.get("rhr")
    rows = [
        ("Date", data.get("date", "-")),
        ("Resting HR", f"{rhr} bpm" if rhr is not None else "-"),
    ]
    return _kv_table(rows)


def format_respiration(data: dict) -> str:
    rows = [
        ("Date", data.get("date", "-")),
        ("Avg sleep", f"{_val(data.get('avg_sleep'))} brpm"),
        ("Avg waking", f"{_val(data.get('avg_waking'))} brpm"),
        ("Low / High", f"{_val(data.get('low'))} / {_val(data.get('high'))} brpm"),
    ]
    return _kv_table(rows)


def format_vo2max(data: dict) -> str:
    rows = [
        ("Date", data.get("date", "-")),
        ("VO2 max", _val(data.get("vo2max"))),
        ("Precise", _val(data.get("vo2max_precise"))),
    ]
    return _kv_table(rows)


def format_weight(data: dict) -> str:
    weight = data.get("weight_kg")
    rows = [
        ("Date", data.get("date", "-")),
        ("Weight", f"{weight} kg" if weight is not None else "-"),
    ]
    return _kv_table(rows)


def format_steps(data: dict) -> str:
    steps = data.get("steps")
    goal = data.get("goal")
    goal_str = f"  (goal: {goal})" if goal is not None else ""
    rows = [
        ("Date", data.get("date", "-")),
        ("Steps", f"{steps}{goal_str}" if steps is not None else "-"),
        ("Distance", f"{_val(data.get('distance_km'))} km"),
    ]
    return _kv_table(rows)


def format_intensity_minutes(data: dict) -> str:
    weekly_total = data.get("weekly_total")
    weekly_goal = data.get("weekly_goal")
    weekly_str = f"{_val(weekly_total)} / {_val(weekly_goal)}" if weekly_goal else _val(weekly_total)
    rows = [
        ("Date", data.get("date", "-")),
        ("Moderate", f"{_val(data.get('moderate'))} min"),
        ("Vigorous", f"{_val(data.get('vigorous'))} min"),
        ("Weekly total / goal", weekly_str),
    ]
    return _kv_table(rows)


def format_calories(data: dict) -> str:
    rows = [
        ("Date", data.get("date", "-")),
        ("Total", f"{_val(data.get('total'))} kcal"),
        ("Active", f"{_val(data.get('active'))} kcal"),
        ("BMR", f"{_val(data.get('bmr'))} kcal"),
    ]
    return _kv_table(rows)


def format_race_predictions(data: dict) -> str:
    rows = [
        ("As of", data.get("date", "-")),
        ("5K", _val(data.get("5k"))),
        ("10K", _val(data.get("10k"))),
        ("Half marathon", _val(data.get("half_marathon"))),
        ("Marathon", _val(data.get("marathon"))),
    ]
    return _kv_table(rows)
