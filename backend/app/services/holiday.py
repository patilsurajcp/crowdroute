import httpx
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from functools import lru_cache

load_dotenv()

API_KEY  = os.getenv("CALENDARIFIC_API_KEY")
BASE_URL = "https://calendarific.com/api/v2"


async def get_holidays(year: int, country: str = "IN") -> list:
    """Fetch all public holidays for a country and year."""
    if not API_KEY:
        print("⚠️  CALENDARIFIC_API_KEY not set — using empty holiday list")
        return []

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/holidays",
            params={
                "api_key": API_KEY,
                "country": country,
                "year":    year,
                "type":    "national"
            },
            timeout=10.0
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", {}).get("holidays", [])


def analyze_holiday_impact(target_date: datetime, holidays: list) -> dict:
    """
    Analyze holiday impact on crowd levels.
    Detects: single holidays, long weekends, bridge days, festival clusters.
    """
    target_d    = target_date.date()
    holiday_dates = set()
    holiday_map   = {}

    for h in holidays:
        try:
            hd = datetime.strptime(h["date"]["iso"][:10], "%Y-%m-%d").date()
            holiday_dates.add(hd)
            holiday_map[hd] = h["name"]
        except Exception:
            continue

    # ── Check if target date is a holiday ───────────────────
    is_holiday    = target_d in holiday_dates
    holiday_name  = holiday_map.get(target_d, None)

    # ── Check surrounding days (±4 days) ────────────────────
    window        = [target_d + timedelta(days=i) for i in range(-4, 5)]
    nearby_hols   = [d for d in window if d in holiday_dates]

    # ── Detect long weekend ──────────────────────────────────
    # Long weekend = holiday touches Saturday(5) or Sunday(6)
    def touches_weekend(d):
        prev_day = d - timedelta(days=1)
        next_day = d + timedelta(days=1)
        return (
            d.weekday() in [5, 6] or
            prev_day.weekday() in [5, 6] or
            next_day.weekday() in [5, 6]
        )

    long_weekend_holidays = [d for d in nearby_hols if touches_weekend(d)]
    is_long_weekend       = len(long_weekend_holidays) > 0

    # ── Detect bridge day ────────────────────────────────────
    # Bridge day = weekday sandwiched between holiday and weekend
    # e.g. Holiday Mon + Tue(bridge) + Wed = 4-day break
    is_bridge_day = False
    if not is_holiday and target_d.weekday() not in [5, 6]:
        prev_d = target_d - timedelta(days=1)
        next_d = target_d + timedelta(days=1)
        if (prev_d in holiday_dates or prev_d.weekday() in [5, 6]) and \
           (next_d in holiday_dates or next_d.weekday() in [5, 6]):
            is_bridge_day = True

    # ── Detect festival cluster ──────────────────────────────
    # 3+ holidays within 7 days = festival season
    week_window       = [target_d + timedelta(days=i) for i in range(-3, 4)]
    holidays_in_week  = [d for d in week_window if d in holiday_dates]
    is_festival_cluster = len(holidays_in_week) >= 3

    # ── Calculate crowd multiplier ───────────────────────────
    crowd_multiplier = 1.0
    reasons          = []

    if is_holiday:
        crowd_multiplier += 0.6
        reasons.append(f"Public holiday: {holiday_name}")

    if is_long_weekend:
        crowd_multiplier += 0.8
        hol_names = [holiday_map[d] for d in long_weekend_holidays if d in holiday_map]
        reasons.append(f"Long weekend due to: {', '.join(hol_names)}")

    if is_bridge_day:
        crowd_multiplier += 0.5
        reasons.append("Bridge day — many people take day off")

    if is_festival_cluster:
        crowd_multiplier += 0.4
        reasons.append("Festival season — multiple holidays nearby")

    # ── Day-of-week base factor ──────────────────────────────
    dow = target_d.weekday()
    if dow == 4:    # Friday before long weekend
        if is_long_weekend:
            crowd_multiplier += 0.5
            reasons.append("Friday before long weekend — heavy travel")
    elif dow == 0:  # Monday after long weekend
        if is_long_weekend:
            crowd_multiplier += 0.3
            reasons.append("Monday return rush after long weekend")

    # ── Cap multiplier ───────────────────────────────────────
    crowd_multiplier = min(crowd_multiplier, 2.5)

    # ── Impact label ─────────────────────────────────────────
    if crowd_multiplier >= 2.0:
        impact_label = "VERY HIGH"
        impact_emoji = "🔴🔴"
        impact_tip   = "Expect extreme crowding — book in advance or travel off-peak!"
    elif crowd_multiplier >= 1.5:
        impact_label = "HIGH"
        impact_emoji = "🔴"
        impact_tip   = "Very crowded period — consider travelling early morning."
    elif crowd_multiplier >= 1.2:
        impact_label = "ELEVATED"
        impact_emoji = "🟡"
        impact_tip   = "Moderately higher crowds than usual."
    else:
        impact_label = "NORMAL"
        impact_emoji = "🟢"
        impact_tip   = "Normal crowd levels expected."

    return {
        "is_holiday":           is_holiday,
        "is_long_weekend":      is_long_weekend,
        "is_bridge_day":        is_bridge_day,
        "is_festival_cluster":  is_festival_cluster,
        "holiday_name":         holiday_name,
        "crowd_multiplier":     round(crowd_multiplier, 2),
        "impact_label":         impact_label,
        "impact_emoji":         impact_emoji,
        "impact_tip":           impact_tip,
        "reasons":              reasons,
        "nearby_holidays":      [
            {"date": str(d), "name": holiday_map[d]}
            for d in sorted(nearby_hols)
            if d in holiday_map
        ]
    }


async def get_holiday_impact(target_datetime: str, country: str = "IN") -> dict:
    """Main function — fetch holidays and analyze impact for a date."""
    dt       = datetime.fromisoformat(target_datetime)
    holidays = await get_holidays(dt.year, country)

    # Also fetch next year's holidays if date is in Dec
    # (long weekend might span new year)
    if dt.month == 12:
        next_year_holidays = await get_holidays(dt.year + 1, country)
        holidays           = holidays + next_year_holidays

    return analyze_holiday_impact(dt, holidays)