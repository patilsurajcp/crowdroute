import httpx
import os
import random
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

RAPIDAPI_KEY  = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = "irctc1.p.rapidapi.com"


# ── Train Availability (IRCTC via RapidAPI) ───────────────────
async def get_train_availability(
    from_city: str,
    to_city:   str,
    date:      str       # YYYYMMDD format
) -> dict:
    """
    Fetch train seat availability from RapidAPI IRCTC.
    Falls back to smart estimation if API unavailable.
    """
    if not RAPIDAPI_KEY:
        return _estimate_availability("train", date)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://irctc1.p.rapidapi.com/api/v3/trainBetweenStations",
                headers={
                    "x-rapidapi-key":  RAPIDAPI_KEY,
                    "x-rapidapi-host": RAPIDAPI_HOST
                },
                params={
                    "fromStationCode": _city_to_station_code(from_city),
                    "toStationCode":   _city_to_station_code(to_city),
                    "dateOfJourney":   date
                },
                timeout=10.0
            )
            data = response.json()

            if data.get("status") and data.get("data"):
                trains      = data["data"]
                total       = len(trains)
                # Count trains with available seats
                available   = sum(
                    1 for t in trains
                    if any(
                        cls.get("available_seats", 0) > 0
                        for cls in t.get("class_type", [])
                    )
                )
                booked_pct  = round((1 - available / max(total, 1)) * 100, 1)
                return {
                    "source":          "irctc_api",
                    "total_trains":    total,
                    "available_trains":available,
                    "booked_percent":  booked_pct,
                    "crowd_percent":   booked_pct,
                    "status":          _crowd_status(booked_pct)
                }
    except Exception as e:
        print(f"⚠️  IRCTC API failed: {e}")

    return _estimate_availability("train", date)


# ── Bus Availability (RedBus via RapidAPI) ────────────────────
async def get_bus_availability(
    from_city: str,
    to_city:   str,
    date:      str
) -> dict:
    """
    Fetch bus seat availability.
    Falls back to smart estimation if API unavailable.
    """
    if not RAPIDAPI_KEY:
        return _estimate_availability("bus", date)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://redbus1.p.rapidapi.com/api/v1/searchBuses",
                headers={
                    "x-rapidapi-key":  RAPIDAPI_KEY,
                    "x-rapidapi-host": "redbus1.p.rapidapi.com"
                },
                params={
                    "fromCity": from_city,
                    "toCity":   to_city,
                    "doj":      date       # DD-MMM-YYYY format
                },
                timeout=10.0
            )
            data = response.json()

            if data.get("inventoryItems"):
                buses       = data["inventoryItems"]
                total_seats = sum(b.get("seatsAvailable", 0) + b.get("seatsBooked", 0) for b in buses)
                booked      = sum(b.get("seatsBooked", 0) for b in buses)
                booked_pct  = round((booked / max(total_seats, 1)) * 100, 1)
                return {
                    "source":         "redbus_api",
                    "total_buses":    len(buses),
                    "total_seats":    total_seats,
                    "booked_seats":   booked,
                    "booked_percent": booked_pct,
                    "crowd_percent":  booked_pct,
                    "status":         _crowd_status(booked_pct)
                }
    except Exception as e:
        print(f"⚠️  RedBus API failed: {e}")

    return _estimate_availability("bus", date)


# ── Metro Crowd Estimation ────────────────────────────────────
def get_metro_crowd(city: str, datetime_str: str) -> dict:
    """
    Estimate metro crowd based on time patterns.
    Metro APIs are not publicly available in India —
    we use smart time-based estimation.
    """
    from app.data.metro_cities import get_metro_info, has_metro

    if not has_metro(city):
        return None

    metro_info  = get_metro_info(city)
    dt          = datetime.fromisoformat(datetime_str)
    hour        = dt.hour
    dow         = dt.weekday()    # 0=Mon, 6=Sun
    is_weekend  = dow >= 5

    # Base crowd % by hour (metro peak hours pattern)
    hourly_pattern = {
        0: 5,  1: 3,  2: 2,  3: 2,  4: 5,  5: 15,
        6: 35, 7: 75, 8: 92, 9: 85, 10: 55, 11: 45,
        12: 50, 13: 55, 14: 45, 15: 50, 16: 65, 17: 88,
        18: 95, 19: 82, 20: 65, 21: 45, 22: 30, 23: 15
    }

    base_crowd = hourly_pattern.get(hour, 40)

    # Weekend adjustment
    if is_weekend:
        base_crowd = int(base_crowd * 0.65)

    # City-specific ridership factor
    city_factors = {
        "Delhi":     1.2,
        "Mumbai":    1.1,
        "Bengaluru": 1.0,
        "Chennai":   0.9,
        "Kolkata":   1.0,
        "Hyderabad": 0.85,
        "Kochi":     0.7,
        "Jaipur":    0.6,
    }
    factor     = city_factors.get(city, 0.8)
    crowd_pct  = min(int(base_crowd * factor), 99)

    return {
        "source":          "smart_estimation",
        "city":            city,
        "operator":        metro_info["operator"],
        "lines":           metro_info["lines"],
        "total_stations":  metro_info["total_stations"],
        "crowd_percent":   crowd_pct,
        "status":          _crowd_status(crowd_pct),
        "peak_hours":      "7-9 AM & 5-7 PM",
        "note":            "Based on historical ridership patterns"
    }


# ── Combined Availability Check ───────────────────────────────
async def get_all_availability(
    city:         str,
    datetime_str: str,
    to_city:      str = None
) -> dict:
    """Get availability for all transport modes for a city."""
    from app.data.metro_cities import has_metro, get_metro_info

    dt   = datetime.fromisoformat(datetime_str)
    date = dt.strftime("%Y%m%d")

    results = {}

    # Train availability
    if to_city:
        results["train"] = await get_train_availability(city, to_city, date)
    else:
        results["train"] = _estimate_availability("train", datetime_str)

    # Bus availability
    if to_city:
        results["bus"] = await get_bus_availability(city, to_city, date)
    else:
        results["bus"] = _estimate_availability("bus", datetime_str)

    # Metro — only if city has metro
    if has_metro(city):
        results["metro"] = get_metro_crowd(city, datetime_str)
        results["metro"]["metro_info"] = get_metro_info(city)
    else:
        results["metro"] = {
            "available":  False,
            "reason":     f"{city} does not have an operational metro system",
            "status":     "no_metro"
        }

    return results


# ── Helpers ───────────────────────────────────────────────────
def _crowd_status(percent: float) -> dict:
    if percent >= 85:
        return {"level": "HIGH",   "emoji": "🔴", "label": "Very Crowded",     "color": "red"}
    elif percent >= 60:
        return {"level": "MEDIUM", "emoji": "🟡", "label": "Moderately Busy",  "color": "yellow"}
    elif percent >= 30:
        return {"level": "LOW",    "emoji": "🟢", "label": "Comfortable",      "color": "green"}
    else:
        return {"level": "VERY_LOW","emoji":"🟢🟢","label": "Very Comfortable", "color": "green"}


def _estimate_availability(transport: str, datetime_str: str) -> dict:
    """
    Smart fallback estimation when APIs are unavailable.
    Based on time-of-day patterns.
    """
    try:
        dt   = datetime.fromisoformat(datetime_str)
        hour = dt.hour
        dow  = dt.weekday()
    except Exception:
        dt   = datetime.now()
        hour = dt.hour
        dow  = dt.weekday()

    is_weekend = dow >= 5

    # Time-based crowd patterns per transport
    patterns = {
        "train": {
            0: 20, 1: 15, 2: 10, 3: 10, 4: 20, 5: 40,
            6: 60, 7: 80, 8: 90, 9: 75, 10: 55, 11: 50,
            12: 55, 13: 60, 14: 50, 15: 55, 16: 65, 17: 85,
            18: 90, 19: 80, 20: 65, 21: 50, 22: 40, 23: 25
        },
        "bus": {
            0: 10, 1: 8,  2: 5,  3: 5,  4: 15, 5: 35,
            6: 55, 7: 85, 8: 95, 9: 80, 10: 60, 11: 55,
            12: 60, 13: 65, 14: 55, 15: 60, 16: 70, 17: 90,
            18: 95, 19: 80, 20: 60, 21: 40, 22: 25, 23: 15
        }
    }

    base   = patterns.get(transport, patterns["bus"]).get(hour, 50)
    if is_weekend:
        base = int(base * 0.7)

    # Add slight randomness for realism
    crowd  = min(max(base + random.randint(-5, 5), 0), 99)

    return {
        "source":         "smart_estimation",
        "crowd_percent":  crowd,
        "status":         _crowd_status(crowd),
        "note":           "Estimated based on time patterns (API unavailable)"
    }


def _city_to_station_code(city: str) -> str:
    """Map city name to IRCTC station code."""
    codes = {
        "Mumbai":        "CSTM",
        "Delhi":         "NDLS",
        "Bengaluru":     "SBC",
        "Chennai":       "MAS",
        "Kolkata":       "HWH",
        "Hyderabad":     "SC",
        "Pune":          "PUNE",
        "Ahmedabad":     "ADI",
        "Jaipur":        "JP",
        "Lucknow":       "LKO",
        "Patna":         "PNBE",
        "Bhopal":        "BPL",
        "Indore":        "INDB",
        "Nagpur":        "NGP",
        "Surat":         "ST",
        "Vadodara":      "BRC",
        "Chandigarh":    "CDG",
        "Amritsar":      "ASR",
        "Varanasi":      "BSB",
        "Agra":          "AGC",
        "Kanpur":        "CNB",
        "Guwahati":      "GHY",
        "Bhubaneswar":   "BBS",
        "Thiruvananthapuram": "TVC",
        "Kochi":         "ERS",
        "Coimbatore":    "CBE",
        "Madurai":       "MDU",
    }
    return codes.get(city, city[:3].upper())