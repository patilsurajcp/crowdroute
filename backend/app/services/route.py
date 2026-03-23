import googlemaps
import os
from dotenv import load_dotenv
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(BASE_DIR, ".env"))

GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
gmaps          = googlemaps.Client(key=GOOGLE_API_KEY) if GOOGLE_API_KEY else None

print(f"🗺️  Google Maps API: {'✅ Connected' if gmaps else '❌ NOT FOUND'}")

# Fallback distances when API unavailable
CITY_AVG_DISTANCE = {
    "Mumbai": 12.0, "Delhi": 14.0, "Bengaluru": 11.0,
    "Chennai": 10.0, "Kolkata": 9.0, "Hyderabad": 11.0,
    "Pune": 8.0, "Ahmedabad": 9.0, "Hubli": 6.0,
    "Dharwad": 5.0, "Mysuru": 7.0, "Jaipur": 8.0,
    "Kochi": 7.0, "Surat": 7.0, "Lucknow": 10.0,
    "Patna": 8.0, "Bhopal": 8.0, "Indore": 8.0,
    "Nagpur": 9.0, "Varanasi": 7.0, "Chandigarh": 7.0,
    "Guwahati": 8.0, "Coimbatore": 8.0, "Madurai": 7.0,
}
DEFAULT_AVG_DISTANCE = 7.0

# Traffic congestion level thresholds
# Ratio = traffic_duration / normal_duration
# > 1.5 = HIGH, 1.2-1.5 = MEDIUM, < 1.2 = LOW
TRAFFIC_THRESHOLDS = {
    "LOW":    1.2,
    "MEDIUM": 1.5,
}

TRANSPORT_SPEEDS = {
    "bus":        18,
    "metro":      35,
    "train":      45,
    "chigari":    20,
    "ferry":      15,
    "tram":       12,
    "toy_train":  20,
    "shared_cab": 25,
    "shikara":    8,
}

CROWD_SPEED_FACTOR = {
    "LOW":    1.0,
    "MEDIUM": 0.75,
    "HIGH":   0.5,
}

WAITING_TIMES = {
    "bus": 8, "metro": 5, "train": 10, "chigari": 8,
    "ferry": 15, "shared_cab": 5, "tram": 6,
    "toy_train": 10, "shikara": 5,
}


def get_route_data(source: str, destination: str, city: str, departure_datetime: str = None) -> dict:
    """
    Get real route data from Google Maps including:
    - Distance
    - Normal duration
    - Traffic duration
    - Traffic congestion level
    - Route steps/waypoints
    """
    if not gmaps:
        fallback_dist = CITY_AVG_DISTANCE.get(city, DEFAULT_AVG_DISTANCE)
        return {
            "distance_km":       fallback_dist,
            "normal_duration":   None,
            "traffic_duration":  None,
            "traffic_ratio":     1.0,
            "traffic_level":     "UNKNOWN",
            "traffic_emoji":     "🟡",
            "route_polyline":    None,
            "via":               None,
            "source":            "fallback"
        }

    try:
        # Parse departure time
        if departure_datetime:
            dt = datetime.fromisoformat(departure_datetime)
            # Google requires future time for traffic — use now if past
            now = datetime.now()
            departure_time = dt if dt > now else now
        else:
            departure_time = datetime.now()

        # Format for Google
        origin      = f"{source}, {city}, India"
        destination_ = f"{destination}, {city}, India"

        # Call Directions API with traffic model
        directions = gmaps.directions(
            origin,
            destination_,
            mode="driving",
            departure_time=departure_time,
            traffic_model="best_guess",
            alternatives=False
        )

        if not directions:
            raise ValueError("No route found")

        leg = directions[0]["legs"][0]

        # Extract distance
        distance_m  = leg["distance"]["value"]
        distance_km = round(distance_m / 1000, 2)

        # Extract durations
        normal_secs  = leg["duration"]["value"]
        traffic_secs = leg.get("duration_in_traffic", {}).get("value", normal_secs)

        normal_mins  = round(normal_secs / 60)
        traffic_mins = round(traffic_secs / 60)

        # Traffic ratio
        traffic_ratio = traffic_secs / normal_secs if normal_secs > 0 else 1.0

        # Determine traffic level
        if traffic_ratio >= TRAFFIC_THRESHOLDS["MEDIUM"]:
            traffic_level = "HIGH"
            traffic_emoji = "🔴"
        elif traffic_ratio >= TRAFFIC_THRESHOLDS["LOW"]:
            traffic_level = "MEDIUM"
            traffic_emoji = "🟡"
        else:
            traffic_level = "LOW"
            traffic_emoji = "🟢"

        # Extract main road names from steps
        steps    = leg.get("steps", [])
        via_roads = []
        for step in steps[:3]:   # top 3 roads only
            html = step.get("html_instructions", "")
            import re
            roads = re.findall(r'<b>(.*?)</b>', html)
            via_roads.extend(roads)
        via_str = " → ".join(via_roads[:3]) if via_roads else None

        print(f"🗺️  Route: {origin} → {destination_}")
        print(f"📏  Distance: {distance_km} km")
        print(f"🚦  Traffic: {traffic_level} (ratio: {traffic_ratio:.2f})")
        print(f"⏱️   Normal: {normal_mins} mins, With traffic: {traffic_mins} mins")

        return {
            "distance_km":      distance_km,
            "normal_duration":  normal_mins,
            "traffic_duration": traffic_mins,
            "traffic_ratio":    round(traffic_ratio, 2),
            "traffic_level":    traffic_level,
            "traffic_emoji":    traffic_emoji,
            "via":              via_str,
            "source":           "google_maps"
        }

    except Exception as e:
        print(f"⚠️  Google Maps failed: {e} — using fallback")
        fallback_dist = CITY_AVG_DISTANCE.get(city, DEFAULT_AVG_DISTANCE)
        return {
            "distance_km":      fallback_dist,
            "normal_duration":  None,
            "traffic_duration": None,
            "traffic_ratio":    1.0,
            "traffic_level":    "UNKNOWN",
            "traffic_emoji":    "🟡",
            "via":              None,
            "source":           "fallback"
        }


def get_traffic_crowd_multiplier(traffic_ratio: float) -> float:
    """Convert traffic ratio to crowd multiplier for ML model adjustment."""
    if traffic_ratio >= 1.5:   return 1.4   # Heavy traffic = more crowd
    elif traffic_ratio >= 1.2: return 1.2
    else:                      return 1.0


def estimate_travel_time_from_route(
    route_data:     dict,
    transport_type: str,
    crowd_level:    str
) -> str:
    """
    Use Google Maps traffic duration if available,
    otherwise fall back to speed-based calculation.
    """
    # If we have real Google traffic data, use it for bus/cab
    if route_data.get("source") == "google_maps" and route_data.get("traffic_duration"):
        base_mins = route_data["traffic_duration"]

        # Adjust for transport type
        if transport_type in ["bus", "chigari"]:
            # Buses slower than cars + stops
            adjusted = round(base_mins * 1.3 + WAITING_TIMES.get(transport_type, 8))
        elif transport_type in ["metro", "train"]:
            # Metro/train unaffected by road traffic
            dist     = route_data["distance_km"]
            speed    = TRANSPORT_SPEEDS.get(transport_type, 35)
            factor   = CROWD_SPEED_FACTOR.get(crowd_level, 1.0)
            adjusted = round((dist / (speed * factor)) * 60 + WAITING_TIMES.get(transport_type, 5))
        elif transport_type == "shared_cab":
            adjusted = round(base_mins * 1.1 + WAITING_TIMES.get(transport_type, 5))
        else:
            adjusted = round(base_mins + WAITING_TIMES.get(transport_type, 5))

        if adjusted < 60:
            return f"{adjusted} mins"
        return f"{adjusted // 60}h {adjusted % 60}m"

    # Fallback — speed based
    dist  = route_data.get("distance_km", DEFAULT_AVG_DISTANCE)
    speed = TRANSPORT_SPEEDS.get(transport_type, 20)
    factor = CROWD_SPEED_FACTOR.get(crowd_level, 1.0)
    mins  = round((dist / (speed * factor)) * 60 + WAITING_TIMES.get(transport_type, 5))
    if mins < 60:
        return f"{mins} mins"
    return f"{mins // 60}h {mins % 60}m"


def get_route_note(transport_type: str, source: str, destination: str, crowd_level: str, via: str = None) -> str:
    via_str = f" via {via}" if via else ""
    notes = {
        "bus": {
            "LOW":    f"Direct bus from {source} to {destination}{via_str} — smooth ride!",
            "MEDIUM": f"Buses running{via_str} but expect some crowding near stops.",
            "HIGH":   "Buses very crowded — consider waiting for next one.",
        },
        "metro": {
            "LOW":    "Metro is the fastest option — unaffected by road traffic!",
            "MEDIUM": "Metro is moderately busy — stand near doors for easy exit.",
            "HIGH":   "Metro is packed — wait for the next train if possible.",
        },
        "train": {
            "LOW":    "Train is comfortable and quick.",
            "MEDIUM": "Train is filling up — board from less busy coaches.",
            "HIGH":   "Train is very crowded — consider general vs reserved coaches.",
        },
        "chigari": {
            "LOW":    f"Chigari electric bus{via_str} running smoothly — eco-friendly!",
            "MEDIUM": "Chigari is moderately occupied.",
            "HIGH":   "Chigari is crowded — next bus in ~10 mins.",
        },
        "ferry": {
            "LOW":    "Ferry is calm and comfortable.",
            "MEDIUM": "Ferry is filling up — board early.",
            "HIGH":   "Ferry is at capacity — next departure recommended.",
        },
        "shared_cab": {
            "LOW":    "Shared cab available quickly.",
            "MEDIUM": "Moderate wait time for shared cab.",
            "HIGH":   "High demand — expect longer wait for shared cab.",
        },
        "tram":      {"LOW": "Tram running smoothly.", "MEDIUM": "Tram moderately busy.", "HIGH": "Tram crowded — next in ~8 mins."},
        "toy_train": {"LOW": "Enjoy the scenic ride!", "MEDIUM": "Moderately occupied.", "HIGH": "Full — check next departure."},
        "shikara":   {"LOW": "Peaceful shikara ride!", "MEDIUM": "Moderate demand.", "HIGH": "High demand — book in advance."},
    }
    return notes.get(transport_type, {}).get(crowd_level, f"Travel from {source} to {destination}.")