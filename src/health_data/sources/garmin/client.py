from datetime import date as date_cls

from garminconnect import Garmin

from health_data.sources.garmin.cache import read_cache, write_cache, STATIC_TTL, DYNAMIC_TTL


def _ttl(date: str, is_static: bool) -> int | None:
    """Return cache TTL for the given date.

    Past dates are immutable — no expiry (None).
    Today uses a metric-specific TTL.
    """
    if date == date_cls.today().isoformat():
        return STATIC_TTL if is_static else DYNAMIC_TTL
    return None


def _seconds_to_hm(seconds: int) -> str:
    h, m = divmod(seconds // 60, 60)
    return f"{h}h {m}m"


def _seconds_to_race_time(seconds: int) -> str:
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def get_sleep(client: Garmin, date: str) -> dict:
    """Return key sleep metrics for the given date (wake-up date)."""
    ttl = _ttl(date, is_static=True)
    cached = read_cache("sleep", date, ttl)
    if cached is not None:
        return cached

    data = client.get_sleep_data(date)
    dto = data.get("dailySleepDTO", {})
    scores = dto.get("sleepScores", {})
    result = {
        "date": date,
        "score": scores.get("overall", {}).get("value"),
        "score_qualifier": scores.get("overall", {}).get("qualifierKey"),
        "total": _seconds_to_hm(dto.get("sleepTimeSeconds", 0)),
        "deep": _seconds_to_hm(dto.get("deepSleepSeconds", 0)),
        "light": _seconds_to_hm(dto.get("lightSleepSeconds", 0)),
        "rem": _seconds_to_hm(dto.get("remSleepSeconds", 0)),
        "awake": _seconds_to_hm(dto.get("awakeSleepSeconds", 0)),
        "avg_stress": dto.get("avgSleepStress"),
        "feedback": dto.get("sleepScoreFeedback"),
    }
    write_cache("sleep", date, result)
    return result


def get_hrv(client: Garmin, date: str) -> dict:
    """Return HRV summary for the given date (wake-up date)."""
    ttl = _ttl(date, is_static=True)
    cached = read_cache("hrv", date, ttl)
    if cached is not None:
        return cached

    data = client.get_hrv_data(date)
    summary = data.get("hrvSummary", {})
    baseline = summary.get("baseline", {})
    result = {
        "date": date,
        "last_night_avg": summary.get("lastNightAvg"),
        "weekly_avg": summary.get("weeklyAvg"),
        "status": summary.get("status"),
        "baseline_low": baseline.get("balancedLow"),
        "baseline_high": baseline.get("balancedUpper"),
    }
    write_cache("hrv", date, result)
    return result


def get_stress(client: Garmin, date: str) -> dict:
    """Return daily stress summary for the given date."""
    ttl = _ttl(date, is_static=False)
    cached = read_cache("stress", date, ttl)
    if cached is not None:
        return cached

    data = client.get_stress_data(date)
    result = {
        "date": date,
        "avg": data.get("avgStressLevel"),
        "max": data.get("maxStressLevel"),
    }
    write_cache("stress", date, result)
    return result


def get_body_battery(client: Garmin, date: str) -> dict:
    """Return body battery summary for the given date."""
    ttl = _ttl(date, is_static=False)
    cached = read_cache("body_battery", date, ttl)
    if cached is not None:
        return cached

    data = client.get_body_battery(date, date)
    if not data:
        result = {"date": date, "charged": None, "drained": None, "peak": None, "end": None}
    else:
        day = data[0]
        values = [v[1] for v in day.get("bodyBatteryValuesArray", [])]
        result = {
            "date": date,
            "charged": day.get("charged"),
            "drained": day.get("drained"),
            "peak": max(values) if values else None,
            "end": values[-1] if values else None,
        }
    write_cache("body_battery", date, result)
    return result


def get_rhr(client: Garmin, date: str) -> dict:
    """Return resting heart rate for the given date."""
    ttl = _ttl(date, is_static=True)
    cached = read_cache("rhr", date, ttl)
    if cached is not None:
        return cached

    data = client.get_rhr_day(date)
    metrics = data.get("allMetrics", {}).get("metricsMap", {})
    rhr_list = metrics.get("WELLNESS_RESTING_HEART_RATE", [])
    value = rhr_list[0].get("value") if rhr_list else None
    result = {
        "date": date,
        "rhr": int(value) if value is not None else None,
    }
    write_cache("rhr", date, result)
    return result


def get_respiration(client: Garmin, date: str) -> dict:
    """Return respiration summary for the given date (wake-up date)."""
    ttl = _ttl(date, is_static=True)
    cached = read_cache("respiration", date, ttl)
    if cached is not None:
        return cached

    data = client.get_respiration_data(date)
    result = {
        "date": date,
        "avg_sleep": data.get("avgSleepRespirationValue"),
        "avg_waking": data.get("avgWakingRespirationValue"),
        "low": data.get("lowestRespirationValue"),
        "high": data.get("highestRespirationValue"),
    }
    write_cache("respiration", date, result)
    return result


def get_vo2max(client: Garmin, date: str) -> dict:
    """Return VO2 max for the given date."""
    ttl = _ttl(date, is_static=True)
    cached = read_cache("vo2max", date, ttl)
    if cached is not None:
        return cached

    data = client.get_max_metrics(date)
    if not data:
        result = {"date": date, "vo2max": None, "vo2max_precise": None}
    else:
        generic = data[0].get("generic", {})
        result = {
            "date": generic.get("calendarDate", date),
            "vo2max": generic.get("vo2MaxValue"),
            "vo2max_precise": generic.get("vo2MaxPreciseValue"),
        }
    write_cache("vo2max", date, result)
    return result


def get_weight(client: Garmin, date: str) -> dict:
    """Return weight for the given date, falling back to most recent entry."""
    ttl = _ttl(date, is_static=True)
    cached = read_cache("weight", date, ttl)
    if cached is not None:
        return cached

    data = client.get_weigh_ins(date, date)
    summaries = data.get("dailyWeightSummaries", [])

    if summaries:
        summary = summaries[0]
        latest = summary.get("latestWeight") or {}
        weight_g = latest.get("weight")
        entry_date = summary.get("summaryDate", date)
    else:
        fallback = data.get("previousDateWeight") or {}
        weight_g = fallback.get("weight")
        entry_date = fallback.get("calendarDate", date)

    if weight_g is not None:
        result = {
            "date": entry_date,
            "weight_kg": round(weight_g / 1000, 1),
        }
        write_cache("weight", date, result)
    else:
        result = {"date": date, "weight_kg": None}
        # Don't cache null — weight may not have synced yet

    return result


def get_steps(client: Garmin, date: str) -> dict:
    """Return step count for the given date."""
    ttl = _ttl(date, is_static=False)
    cached = read_cache("steps", date, ttl)
    if cached is not None:
        return cached

    data = client.get_daily_steps(date, date)
    if not data:
        result = {"date": date, "steps": None, "distance_km": None, "goal": None}
    else:
        item = data[0]
        distance_m = item.get("totalDistance")
        result = {
            "date": item.get("calendarDate", date),
            "steps": item.get("totalSteps"),
            "distance_km": round(distance_m / 1000, 1) if distance_m is not None else None,
            "goal": item.get("stepGoal"),
        }
    write_cache("steps", date, result)
    return result


def get_intensity_minutes(client: Garmin, date: str) -> dict:
    """Return intensity minutes for the given date."""
    ttl = _ttl(date, is_static=False)
    cached = read_cache("intensity_minutes", date, ttl)
    if cached is not None:
        return cached

    data = client.get_intensity_minutes_data(date)
    result = {
        "date": date,
        "moderate": data.get("moderateMinutes"),
        "vigorous": data.get("vigorousMinutes"),
        "weekly_moderate": data.get("weeklyModerate"),
        "weekly_vigorous": data.get("weeklyVigorous"),
        "weekly_total": data.get("weeklyTotal"),
        "weekly_goal": data.get("weekGoal"),
    }
    write_cache("intensity_minutes", date, result)
    return result


def get_calories(client: Garmin, date: str) -> dict:
    """Return calorie summary for the given date."""
    ttl = _ttl(date, is_static=False)
    cached = read_cache("calories", date, ttl)
    if cached is not None:
        return cached

    data = client.get_stats(date)
    result = {
        "date": date,
        "total": int(data["totalKilocalories"]) if data.get("totalKilocalories") is not None else None,
        "active": int(data["activeKilocalories"]) if data.get("activeKilocalories") is not None else None,
        "bmr": int(data["bmrKilocalories"]) if data.get("bmrKilocalories") is not None else None,
    }
    write_cache("calories", date, result)
    return result


def get_race_predictions(client: Garmin) -> dict:
    """Return latest race time predictions."""
    cached = read_cache("race_predictions", "latest", ttl=STATIC_TTL)
    if cached is not None:
        return cached

    data = client.get_race_predictions()
    result = {
        "date": data.get("calendarDate"),
        "5k": _seconds_to_race_time(data["time5K"]) if data.get("time5K") else None,
        "10k": _seconds_to_race_time(data["time10K"]) if data.get("time10K") else None,
        "half_marathon": _seconds_to_race_time(data["timeHalfMarathon"]) if data.get("timeHalfMarathon") else None,
        "marathon": _seconds_to_race_time(data["timeMarathon"]) if data.get("timeMarathon") else None,
    }
    write_cache("race_predictions", "latest", result)
    return result


# --- Activity commands ---


def _format_pace_ms(speed_ms: float | None) -> str | None:
    """m/s to min:ss/km pace string."""
    if not speed_ms:
        return None
    pace_seconds = 1000 / speed_ms
    m, s = divmod(int(pace_seconds), 60)
    return f"{m}:{s:02d}/km"


def get_activities(
    client: Garmin,
    limit: int = 20,
    start: int = 0,
    activity_type: str | None = None,
) -> list[dict]:
    """Fetch recent activities as a list of summary dicts."""
    data = client.get_activities(start=start, limit=limit, activitytype=activity_type)
    results = []
    for a in data:
        results.append({
            "activity_id": a.get("activityId"),
            "name": a.get("activityName"),
            "sport_type": (a.get("activityType") or {}).get("typeKey"),
            "start_time": a.get("startTimeLocal"),
            "distance_m": a.get("distance"),
            "duration_s": a.get("duration"),
            "moving_duration_s": a.get("movingDuration"),
            "elevation_gain_m": a.get("elevationGain"),
            "avg_hr": a.get("averageHR"),
            "max_hr": a.get("maxHR"),
            "calories": a.get("calories"),
            "avg_speed_ms": a.get("averageSpeed"),
            "vo2max": a.get("vO2MaxValue"),
            "aerobic_te": a.get("aerobicTrainingEffect"),
            "anaerobic_te": a.get("anaerobicTrainingEffect"),
            "training_load": a.get("activityTrainingLoad"),
            "location": a.get("locationName"),
        })
    return results


def get_activity(client: Garmin, activity_id: int) -> dict:
    """Fetch detailed data for a single activity."""
    data = client.get_activity(activity_id)
    s = data.get("summaryDTO", {})
    meta = data.get("metadataDTO", {})

    result = {
        "activity_id": meta.get("activityId") or data.get("activityId"),
        "name": data.get("activityName"),
        "sport_type": (data.get("activityTypeDTO") or {}).get("typeKey"),
        "start_time": s.get("startTimeLocal"),
        "location": data.get("locationName"),

        # Distance & duration
        "distance_m": s.get("distance"),
        "duration_s": s.get("duration"),
        "moving_duration_s": s.get("movingDuration"),
        "elapsed_duration_s": s.get("elapsedDuration"),
        "elevation_gain_m": s.get("elevationGain"),
        "elevation_loss_m": s.get("elevationLoss"),
        "min_elevation_m": s.get("minElevation"),
        "max_elevation_m": s.get("maxElevation"),

        # Speed & pace
        "avg_speed_ms": s.get("averageSpeed"),
        "avg_moving_speed_ms": s.get("averageMovingSpeed"),
        "max_speed_ms": s.get("maxSpeed"),
        "avg_pace": _format_pace_ms(s.get("averageSpeed")),
        "avg_moving_pace": _format_pace_ms(s.get("averageMovingSpeed")),

        # Heart rate
        "avg_hr": s.get("averageHR"),
        "max_hr": s.get("maxHR"),
        "min_hr": s.get("minHR"),

        # Cadence & stride
        "avg_cadence_spm": s.get("averageRunningCadenceInStepsPerMinute"),
        "max_cadence_spm": s.get("maxRunningCadenceInStepsPerMinute"),
        "avg_stride_length_cm": s.get("avgStrideLength"),
        "steps": s.get("steps"),

        # Calories & temperature
        "calories": s.get("calories"),
        "avg_temperature_c": s.get("averageTemperature"),
        "min_temperature_c": s.get("minTemperature"),
        "max_temperature_c": s.get("maxTemperature"),

        # Training metrics
        "aerobic_te": s.get("aerobicTrainingEffect"),
        "anaerobic_te": s.get("anaerobicTrainingEffect"),
        "training_effect_label": s.get("trainingEffectLabel"),
        "training_load": s.get("activityTrainingLoad"),
        "vo2max": s.get("vO2MaxValue"),

        # Workout feel & RPE (user-entered post-activity)
        "workout_feel": s.get("directWorkoutFeel"),
        "workout_rpe": s.get("directWorkoutRpe"),

        # Running dynamics
        "ground_contact_time_ms": s.get("groundContactTime"),
        "ground_contact_balance_pct": s.get("groundContactBalanceLeft"),
        "vertical_oscillation_cm": s.get("verticalOscillation"),
        "vertical_ratio_pct": s.get("verticalRatio"),
        "avg_respiration_rate": s.get("avgRespirationRate"),
        "max_respiration_rate": s.get("maxRespirationRate"),

        # HR zone time (seconds)
        "hr_zone_1_s": s.get("hrTimeInZone1"),
        "hr_zone_2_s": s.get("hrTimeInZone2"),
        "hr_zone_3_s": s.get("hrTimeInZone3"),
        "hr_zone_4_s": s.get("hrTimeInZone4"),
        "hr_zone_5_s": s.get("hrTimeInZone5"),

        # Fastest splits
        "fastest_1km_s": s.get("fastestSplit_1000"),
        "fastest_mile_s": s.get("fastestSplit_1609"),
        "fastest_5km_s": s.get("fastestSplit_5000"),
        "fastest_10km_s": s.get("fastestSplit_10000"),

        # Water
        "water_estimated_ml": s.get("waterEstimated"),

        # Lap count
        "lap_count": meta.get("lapCount"),
    }
    # Strip None values for clean output
    return {k: v for k, v in result.items() if v is not None}


def get_activity_splits(client: Garmin, activity_id: int) -> list[dict]:
    """Fetch lap splits for an activity."""
    data = client.get_activity_splits(activity_id)
    laps = data.get("lapDTOs", [])
    results = []
    for i, lap in enumerate(laps, 1):
        results.append({
            "lap": i,
            "distance_m": lap.get("distance"),
            "duration_s": lap.get("duration"),
            "moving_duration_s": lap.get("movingDuration"),
            "avg_speed_ms": lap.get("averageSpeed"),
            "avg_moving_speed_ms": lap.get("averageMovingSpeed"),
            "max_speed_ms": lap.get("maxSpeed"),
            "avg_pace": _format_pace_ms(lap.get("averageSpeed")),
            "avg_hr": lap.get("averageHR"),
            "max_hr": lap.get("maxHR"),
            "avg_cadence_spm": lap.get("averageRunCadence"),
            "max_cadence_spm": lap.get("maxRunCadence"),
            "stride_length_cm": lap.get("strideLength"),
            "elevation_gain_m": lap.get("elevationGain"),
            "elevation_loss_m": lap.get("elevationLoss"),
            "calories": lap.get("calories"),
        })
    return results


def get_activity_hr_zones(client: Garmin, activity_id: int) -> list[dict]:
    """Fetch HR zone breakdown for an activity."""
    data = client.get_activity_hr_in_timezones(activity_id)
    zones = []
    for z in data:
        zones.append({
            "zone": z.get("zoneNumber"),
            "seconds": z.get("secsInZone"),
            "time": _seconds_to_hm(int(z.get("secsInZone", 0))),
            "low_bpm": z.get("zoneLowBoundary"),
        })
    return zones


def get_activity_weather(client: Garmin, activity_id: int) -> dict:
    """Fetch weather conditions during an activity."""
    data = client.get_activity_weather(activity_id)
    # Garmin returns temp in Fahrenheit — convert to Celsius
    temp_f = data.get("temp")
    apparent_f = data.get("apparentTemp")
    temp_c = round((temp_f - 32) * 5 / 9, 1) if temp_f is not None else None
    apparent_c = round((apparent_f - 32) * 5 / 9, 1) if apparent_f is not None else None
    result = {
        "temp_c": temp_c,
        "feels_like_c": apparent_c,
        "humidity_pct": data.get("relativeHumidity"),
        "wind_speed": data.get("windSpeed"),
        "wind_gust": data.get("windGust"),
        "wind_direction": data.get("windDirectionCompassPoint"),
        "condition": (data.get("weatherTypeDTO") or {}).get("desc"),
    }
    return {k: v for k, v in result.items() if v is not None}


def get_activity_details(client: Garmin, activity_id: int) -> dict:
    """Fetch time-series data for an activity.

    Returns a dict mapping metric names to lists of values, similar
    to Strava streams.
    """
    data = client.get_activity_details(activity_id, maxchart=10000, maxpoly=10000)
    descriptors = data.get("metricDescriptors", [])
    metrics = data.get("activityDetailMetrics", [])

    # Build index: position in metrics array -> metric key
    index_map = {d["metricsIndex"]: d["key"] for d in descriptors}

    streams: dict[str, list] = {d["key"]: [] for d in descriptors}
    for point in metrics:
        raw = point.get("metrics", [])
        for idx, key in index_map.items():
            if idx < len(raw) and raw[idx] is not None:
                streams[key].append(raw[idx])

    return streams


def get_activity_running_dynamics(
    client: Garmin,
    activity_id: int,
    segment_km: float = 1.0,
) -> list[dict]:
    """Per-segment running dynamics derived from time-series streams.

    Buckets points by cumulative distance into `segment_km` segments and
    averages each running-dynamics metric within the segment.
    """
    data = client.get_activity_details(activity_id, maxchart=10000, maxpoly=10000)
    descriptors = data.get("metricDescriptors", [])
    metrics = data.get("activityDetailMetrics", [])

    key_to_idx = {d["key"]: d["metricsIndex"] for d in descriptors}
    dist_idx = key_to_idx.get("sumDistance")
    if dist_idx is None or not metrics:
        return []

    fields = {
        "speed_ms": "directSpeed",
        "cadence_spm": "directDoubleCadence",
        "gct_ms": "directGroundContactTime",
        "gct_balance_pct": "directGroundContactBalanceLeft",
        "vertical_oscillation_cm": "directVerticalOscillation",
        "vertical_ratio_pct": "directVerticalRatio",
        "stride_length_cm": "directStrideLength",
        "heart_rate_bpm": "directHeartRate",
    }
    field_indices = {f: key_to_idx.get(k) for f, k in fields.items()}

    segment_m = segment_km * 1000.0
    buckets: dict[int, dict[str, list]] = {}

    for point in metrics:
        raw = point.get("metrics", [])
        if dist_idx >= len(raw) or raw[dist_idx] is None:
            continue
        seg = int(raw[dist_idx] // segment_m)
        bucket = buckets.setdefault(seg, {f: [] for f in fields})
        for f, idx in field_indices.items():
            if idx is None or idx >= len(raw):
                continue
            v = raw[idx]
            if v is not None:
                bucket[f].append(v)

    def _avg(vals):
        return sum(vals) / len(vals) if vals else None

    results = []
    for seg_idx in sorted(buckets):
        b = buckets[seg_idx]
        speed = _avg(b["speed_ms"])
        results.append({
            "segment": seg_idx + 1,
            "segment_km": segment_km,
            "avg_speed_ms": speed,
            "avg_pace": _format_pace_ms(speed),
            "cadence_spm": _avg(b["cadence_spm"]),
            "gct_ms": _avg(b["gct_ms"]),
            "gct_balance_pct": _avg(b["gct_balance_pct"]),
            "vertical_oscillation_cm": _avg(b["vertical_oscillation_cm"]),
            "vertical_ratio_pct": _avg(b["vertical_ratio_pct"]),
            "stride_length_cm": _avg(b["stride_length_cm"]),
            "avg_hr_bpm": _avg(b["heart_rate_bpm"]),
        })
    return results


def get_activity_gear(client: Garmin, activity_id: int) -> list[dict]:
    """Fetch gear used for an activity."""
    data = client.get_activity_gear(activity_id)
    results = []
    for g in data:
        results.append({
            "name": g.get("displayName"),
            "type": g.get("gearTypeName"),
            "make": g.get("gearMakeName"),
            "model": g.get("gearModelName"),
        })
    return results


# --- Daily training metrics ---


def _format_pace_spm(speed_spm: float | None) -> str | None:
    """Garmin LT speed (seconds per meter) to min:ss/km pace string."""
    if not speed_spm:
        return None
    pace_seconds = speed_spm * 1000
    m, s = divmod(int(pace_seconds), 60)
    return f"{m}:{s:02d}/km"


def get_lactate_threshold(client: Garmin) -> dict:
    """Return latest lactate threshold HR and pace."""
    cached = read_cache("lactate_threshold", "latest", ttl=STATIC_TTL)
    if cached is not None:
        return cached

    data = client.get_lactate_threshold()
    shr = data.get("speed_and_heart_rate") or {}
    result = {
        "date": (shr.get("calendarDate") or "")[:10] or None,
        "hr_bpm": shr.get("heartRate"),
        "pace": _format_pace_spm(shr.get("speed")),
    }
    write_cache("lactate_threshold", "latest", result)
    return result


def _first_device_data(device_map: dict) -> dict:
    """Extract data from the first device in a Garmin device map."""
    if not device_map:
        return {}
    return next(iter(device_map.values()), {})


def get_training_status(client: Garmin, date: str) -> dict:
    """Return training status summary for the given date."""
    ttl = _ttl(date, is_static=True)
    cached = read_cache("training_status", date, ttl)
    if cached is not None:
        return cached

    data = client.get_training_status(date)

    # Training status is nested under mostRecentTrainingStatus -> latestTrainingStatusData -> {deviceId}
    ts_map = (data.get("mostRecentTrainingStatus") or {}).get("latestTrainingStatusData", {})
    ts = _first_device_data(ts_map)
    acute_dto = ts.get("acuteTrainingLoadDTO") or {}

    # Training load balance is nested similarly
    tlb_map = (data.get("mostRecentTrainingLoadBalance") or {}).get("metricsTrainingLoadBalanceDTOMap", {})
    tlb = _first_device_data(tlb_map)

    result = {
        "date": date,
        "status": ts.get("trainingStatusFeedbackPhrase"),
        "fitness_trend": ts.get("fitnessTrend"),
        "acute_load": acute_dto.get("dailyTrainingLoadAcute"),
        "chronic_load_max": acute_dto.get("maxTrainingLoadChronic"),
        "acwr_pct": acute_dto.get("acwrPercent"),
        "acwr_status": acute_dto.get("acwrStatus"),
        "load_aerobic_low": tlb.get("monthlyLoadAerobicLow"),
        "load_aerobic_high": tlb.get("monthlyLoadAerobicHigh"),
        "load_anaerobic": tlb.get("monthlyLoadAnaerobic"),
        "load_aerobic_low_target": f"{tlb.get('monthlyLoadAerobicLowTargetMin')}-{tlb.get('monthlyLoadAerobicLowTargetMax')}" if tlb.get("monthlyLoadAerobicLowTargetMin") is not None else None,
        "load_aerobic_high_target": f"{tlb.get('monthlyLoadAerobicHighTargetMin')}-{tlb.get('monthlyLoadAerobicHighTargetMax')}" if tlb.get("monthlyLoadAerobicHighTargetMin") is not None else None,
        "load_anaerobic_target": f"{tlb.get('monthlyLoadAnaerobicTargetMin')}-{tlb.get('monthlyLoadAnaerobicTargetMax')}" if tlb.get("monthlyLoadAnaerobicTargetMin") is not None else None,
        "balance_feedback": tlb.get("trainingBalanceFeedbackPhrase"),
    }
    write_cache("training_status", date, result)
    return result


def get_training_readiness(client: Garmin, date: str) -> dict:
    """Return training readiness score for the given date."""
    ttl = _ttl(date, is_static=True)
    cached = read_cache("training_readiness", date, ttl)
    if cached is not None:
        return cached

    data = client.get_training_readiness(date)
    # API returns a list; take the first entry if available
    entry = data[0] if data else {}
    result = {
        "date": date,
        "score": entry.get("score"),
        "level": entry.get("level"),
    }
    write_cache("training_readiness", date, result)
    return result


def get_hill_score(client: Garmin, date: str) -> dict:
    """Return hill score for the given date."""
    ttl = _ttl(date, is_static=True)
    cached = read_cache("hill_score", date, ttl)
    if cached is not None:
        return cached

    data = client.get_hill_score(date)
    result = {
        "date": date,
        "score": data.get("overallScore"),
        "endurance": data.get("enduranceScore"),
        "strength": data.get("strengthScore"),
    }
    write_cache("hill_score", date, result)
    return result
