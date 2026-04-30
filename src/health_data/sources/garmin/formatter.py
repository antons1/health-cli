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


# --- Activity formatting ---


def _fmt_dist(meters):
    if meters is None:
        return "-"
    if meters < 1000:
        return f"{meters:.0f} m"
    return f"{meters / 1000:.2f} km"


def _fmt_dur(seconds):
    if seconds is None:
        return "-"
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def _fmt_split(seconds):
    """Format a fastest split time (seconds) as m:ss."""
    if seconds is None:
        return None
    return _fmt_dur(seconds)


def format_activities(activities: list[dict]) -> str:
    if not activities:
        return "No activities found."
    rows = []
    for a in activities:
        rows.append([
            a.get("activity_id", "-"),
            (a.get("start_time") or "-")[:16].replace("T", " "),
            a.get("name", "-"),
            a.get("sport_type", "-"),
            _fmt_dist(a.get("distance_m")),
            _fmt_dur(a.get("moving_duration_s") or a.get("duration_s")),
            f"{a['avg_hr']:.0f}" if a.get("avg_hr") else "-",
            f"{a['elevation_gain_m']:.0f} m" if a.get("elevation_gain_m") else "-",
        ])
    headers = ["ID", "Date", "Name", "Type", "Distance", "Time", "Avg HR", "Elev"]
    return tabulate(rows, headers=headers, tablefmt="simple")


def format_activity(data: dict) -> str:
    name = data.get("name", "Activity")
    sport = data.get("sport_type", "")
    lines = [f"{name}  ({sport})", ""]

    fields = [
        ("Date", (data.get("start_time") or "-")[:16].replace("T", " ")),
        ("Location", data.get("location")),
        ("Distance", _fmt_dist(data.get("distance_m"))),
        ("Duration", _fmt_dur(data.get("duration_s"))),
        ("Moving time", _fmt_dur(data.get("moving_duration_s"))),
        ("Elapsed time", _fmt_dur(data.get("elapsed_duration_s"))),
        ("Avg pace", data.get("avg_pace")),
        ("Avg moving pace", data.get("avg_moving_pace")),
        ("Avg HR", f"{data['avg_hr']:.0f} bpm" if data.get("avg_hr") else None),
        ("Max HR", f"{data['max_hr']:.0f} bpm" if data.get("max_hr") else None),
        ("Min HR", f"{data['min_hr']:.0f} bpm" if data.get("min_hr") else None),
        ("Cadence", f"{data['avg_cadence_spm']:.0f} spm" if data.get("avg_cadence_spm") else None),
        ("Max cadence", f"{data['max_cadence_spm']:.0f} spm" if data.get("max_cadence_spm") else None),
        ("Stride length", f"{data['avg_stride_length_cm']:.0f} cm" if data.get("avg_stride_length_cm") else None),
        ("Steps", str(data["steps"]) if data.get("steps") else None),
        ("Elevation gain", f"{data['elevation_gain_m']:.0f} m" if data.get("elevation_gain_m") else None),
        ("Elevation loss", f"{data['elevation_loss_m']:.0f} m" if data.get("elevation_loss_m") else None),
        ("Calories", f"{data['calories']:.0f} kcal" if data.get("calories") else None),
        ("Temperature", f"{data['avg_temperature_c']:.0f}°C" if data.get("avg_temperature_c") is not None else None),
    ]

    # Training metrics section
    training = [
        ("Aerobic TE", f"{data['aerobic_te']:.1f}" if data.get("aerobic_te") else None),
        ("Anaerobic TE", f"{data['anaerobic_te']:.1f}" if data.get("anaerobic_te") else None),
        ("TE label", (data.get("training_effect_label") or "").replace("_", " ").title() or None),
        ("Training load", f"{data['training_load']:.1f}" if data.get("training_load") else None),
        ("VO2 max", f"{data['vo2max']:.1f}" if data.get("vo2max") else None),
        ("Workout feel", str(data["workout_feel"]) if data.get("workout_feel") else None),
        ("Workout RPE", str(data["workout_rpe"]) if data.get("workout_rpe") else None),
    ]

    # Fastest splits section
    splits = [
        ("Fastest 1 km", _fmt_split(data.get("fastest_1km_s"))),
        ("Fastest mile", _fmt_split(data.get("fastest_mile_s"))),
        ("Fastest 5 km", _fmt_split(data.get("fastest_5km_s"))),
        ("Fastest 10 km", _fmt_split(data.get("fastest_10km_s"))),
    ]

    # Running dynamics section
    dynamics = [
        ("GCT", f"{data['ground_contact_time_ms']:.0f} ms" if data.get("ground_contact_time_ms") else None),
        ("GCT balance", f"{data['ground_contact_balance_pct']:.1f}% L" if data.get("ground_contact_balance_pct") else None),
        ("Vert. oscillation", f"{data['vertical_oscillation_cm']:.1f} cm" if data.get("vertical_oscillation_cm") else None),
        ("Vert. ratio", f"{data['vertical_ratio_pct']:.1f}%" if data.get("vertical_ratio_pct") else None),
        ("Respiration", f"{data['avg_respiration_rate']:.0f} brpm" if data.get("avg_respiration_rate") else None),
    ]

    # HR zones section
    hr_zones = []
    for i in range(1, 6):
        secs = data.get(f"hr_zone_{i}_s")
        if secs is not None:
            hr_zones.append((f"HR zone {i}", _fmt_dur(secs)))

    # Other
    other = [
        ("Water est.", f"{data['water_estimated_ml']:.0f} ml" if data.get("water_estimated_ml") else None),
        ("Laps", str(data["lap_count"]) if data.get("lap_count") else None),
    ]

    def _render_section(section_fields, header=None):
        filtered = [(k, v) for k, v in section_fields if v]
        if not filtered:
            return
        if header:
            lines.append("")
            lines.append(header)
        max_label = max(len(k) for k, _ in filtered)
        for label, value in filtered:
            lines.append(f"  {label:<{max_label}}  {value}")

    _render_section(fields)
    _render_section(training, "Training")
    _render_section(splits, "Fastest Splits")
    _render_section(dynamics, "Running Dynamics")
    _render_section(hr_zones, "HR Zones")
    _render_section(other, "Other")

    return "\n".join(lines)


def format_activity_splits(splits: list[dict]) -> str:
    if not splits:
        return "No splits found."
    rows = []
    for s in splits:
        rows.append([
            s.get("lap", "-"),
            _fmt_dist(s.get("distance_m")),
            _fmt_dur(s.get("duration_s")),
            s.get("avg_pace", "-"),
            f"{s['avg_hr']:.0f}" if s.get("avg_hr") else "-",
            f"{s['max_hr']:.0f}" if s.get("max_hr") else "-",
            f"{s['avg_cadence_spm']:.0f}" if s.get("avg_cadence_spm") else "-",
            f"{s['elevation_gain_m']:.0f} m" if s.get("elevation_gain_m") else "-",
        ])
    headers = ["Lap", "Distance", "Time", "Pace", "Avg HR", "Max HR", "Cadence", "Elev"]
    return tabulate(rows, headers=headers, tablefmt="simple")


def format_activity_hr_zones(zones: list[dict]) -> str:
    if not zones:
        return "No HR zone data available."
    rows = []
    for z in zones:
        low = z.get("low_bpm")
        low_str = f"{low} bpm" if low is not None else "-"
        rows.append([
            f"Z{z.get('zone', '?')}",
            z.get("time", "-"),
            low_str,
        ])
    headers = ["Zone", "Time", "From"]
    return tabulate(rows, headers=headers, tablefmt="simple")


def format_activity_weather(data: dict) -> str:
    rows = [
        ("Condition", data.get("condition")),
        ("Temperature", f"{data['temp_c']}°C" if data.get("temp_c") is not None else None),
        ("Feels like", f"{data['feels_like_c']}°C" if data.get("feels_like_c") is not None else None),
        ("Humidity", f"{data['humidity_pct']}%" if data.get("humidity_pct") is not None else None),
        ("Wind", f"{_val(data.get('wind_speed'))} ({_val(data.get('wind_direction'))})" if data.get("wind_speed") is not None else None),
        ("Wind gust", _val(data.get("wind_gust")) if data.get("wind_gust") else None),
    ]
    rows = [(k, v) for k, v in rows if v]
    if not rows:
        return "No weather data available."
    return _kv_table(rows)


def format_activity_details(streams: dict) -> str:
    if not streams:
        return "No detail data available."
    rows = []
    for name, data in streams.items():
        if not data or "Latitude" in name or "Longitude" in name or "Timestamp" in name:
            continue
        nums = [v for v in data if isinstance(v, (int, float))]
        if nums:
            rows.append([
                name.replace("direct", "").replace("sum", ""),
                len(nums),
                f"{min(nums):.1f}",
                f"{sum(nums) / len(nums):.1f}",
                f"{max(nums):.1f}",
            ])
    if not rows:
        return "No detail data available."
    headers = ["Metric", "Points", "Min", "Avg", "Max"]
    return tabulate(rows, headers=headers, tablefmt="simple")


def format_activity_running_dynamics(segments: list[dict]) -> str:
    if not segments:
        return "No running dynamics data available."
    rows = []
    for s in segments:
        rows.append([
            s.get("segment", "-"),
            s.get("avg_pace") or "-",
            f"{s['cadence_spm']:.0f}" if s.get("cadence_spm") is not None else "-",
            f"{s['stride_length_cm']:.0f}" if s.get("stride_length_cm") is not None else "-",
            f"{s['gct_ms']:.0f}" if s.get("gct_ms") is not None else "-",
            f"{s['gct_balance_pct']:.1f}%" if s.get("gct_balance_pct") is not None else "-",
            f"{s['vertical_oscillation_cm']:.1f}" if s.get("vertical_oscillation_cm") is not None else "-",
            f"{s['vertical_ratio_pct']:.1f}%" if s.get("vertical_ratio_pct") is not None else "-",
            f"{s['avg_hr_bpm']:.0f}" if s.get("avg_hr_bpm") is not None else "-",
        ])
    headers = ["Seg", "Pace", "Cad", "Stride", "GCT", "GCT bal L", "Vert osc", "Vert ratio", "HR"]
    return tabulate(rows, headers=headers, tablefmt="simple")


def format_activity_gear(gear: list[dict]) -> str:
    if not gear:
        return "No gear found."
    rows = []
    for g in gear:
        rows.append([
            g.get("name", "-"),
            g.get("type", "-"),
            g.get("make", "-"),
            g.get("model", "-"),
        ])
    headers = ["Name", "Type", "Make", "Model"]
    return tabulate(rows, headers=headers, tablefmt="simple")


# --- Daily training metrics formatting ---


def format_lactate_threshold(data: dict) -> str:
    rows = [
        ("As of", data.get("date", "-")),
        ("HR", f"{data['hr_bpm']} bpm" if data.get("hr_bpm") is not None else "-"),
        ("Pace", _val(data.get("pace"))),
    ]
    return _kv_table(rows)


def format_training_status(data: dict) -> str:
    status = _qualifier(data.get("status"))
    acwr_pct = data.get("acwr_pct")
    acwr_status = data.get("acwr_status")
    acwr_str = f"{acwr_pct}% ({acwr_status})" if acwr_pct is not None else "-"

    def _load_line(key, target_key):
        val = data.get(key)
        target = data.get(target_key)
        if val is None:
            return "-"
        s = f"{val:.0f}"
        if target:
            s += f"  (target: {target})"
        return s

    rows = [
        ("Date", data.get("date", "-")),
        ("Status", status),
        ("ACWR", acwr_str),
        ("Acute load", f"{data['acute_load']:.0f}" if data.get("acute_load") is not None else "-"),
        ("Chronic load max", f"{data['chronic_load_max']:.0f}" if data.get("chronic_load_max") is not None else "-"),
        ("Aerobic low", _load_line("load_aerobic_low", "load_aerobic_low_target")),
        ("Aerobic high", _load_line("load_aerobic_high", "load_aerobic_high_target")),
        ("Anaerobic", _load_line("load_anaerobic", "load_anaerobic_target")),
        ("Balance", _qualifier(data.get("balance_feedback"))),
    ]
    return _kv_table(rows)


def format_training_readiness(data: dict) -> str:
    rows = [
        ("Date", data.get("date", "-")),
        ("Score", _val(data.get("score"))),
        ("Level", _qualifier(data.get("level"))),
    ]
    return _kv_table(rows)


def format_hill_score(data: dict) -> str:
    rows = [
        ("Date", data.get("date", "-")),
        ("Hill score", _val(data.get("score"))),
        ("Endurance", _val(data.get("endurance"))),
        ("Strength", _val(data.get("strength"))),
    ]
    return _kv_table(rows)
