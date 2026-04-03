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
    entry = summaries[0] if summaries else data.get("previousDateWeight")

    if entry and entry.get("weight") is not None:
        weight_g = entry["weight"]
        result = {
            "date": entry.get("calendarDate", date),
            "weight_kg": round(weight_g / 1000, 1),
        }
    else:
        result = {"date": date, "weight_kg": None}

    write_cache("weight", date, result)
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
