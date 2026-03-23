from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import asyncio

geolocator = Nominatim(user_agent="crowdroute_app")

# Average speeds (km/h) per transport in Indian cities
TRANSPORT_SPEEDS = {
    "bus":        18,   # city bus avg including stops
    "metro":      35,   # metro avg
    "train":      45,   # suburban train avg
    "chigari":    20,   # electric bus
    "ferry":      15,   # ferry
    "tram":       12,   # tram
    "toy_train":  20,   # mountain railway
    "shared_cab": 25,   # shared cab
    "shikara":    8,    # shikara
}

# Crowd level → speed reduction factor
CROWD_SPEED_FACTOR = {
    "LOW":    1.0,    # full speed
    "MEDIUM": 0.75,   # 25% slower
    "HIGH":   0.5,    # 50% slower
}


def get_coords(location: str, city: str) -> tuple:
    """Get lat/lon for a location in a city."""
    try:
        query    = f"{location}, {city}, India"
        loc      = geolocator.geocode(query, timeout=10)
        if loc:
            return (loc.latitude, loc.longitude)
    except Exception:
        pass
    return None


def calculate_distance(source: str, destination: str, city: str) -> float:
    """Calculate straight-line distance in km between source and destination."""
    src_coords  = get_coords(source, city)
    dst_coords  = get_coords(destination, city)

    if src_coords and dst_coords:
        dist = geodesic(src_coords, dst_coords).km
        # Road distance is typically 1.3x straight line
        return round(dist * 1.3, 2)

    # Fallback — return None if geocoding fails
    return None


def estimate_travel_time(
    distance_km:     float,
    transport_type:  str,
    crowd_level:     str
) -> str:
    """Estimate travel time based on distance, transport, and crowd."""
    if distance_km is None:
        return "N/A"

    base_speed    = TRANSPORT_SPEEDS.get(transport_type, 20)
    crowd_factor  = CROWD_SPEED_FACTOR.get(crowd_level, 1.0)
    effective_speed = base_speed * crowd_factor

    # Time in minutes
    time_minutes  = (distance_km / effective_speed) * 60

    # Add boarding/waiting time per transport
    waiting_times = {
        "bus":        8,
        "metro":      5,
        "train":      10,
        "chigari":    8,
        "ferry":      15,
        "shared_cab": 5,
        "tram":       6,
        "toy_train":  10,
        "shikara":    5,
    }
    total_minutes = time_minutes + waiting_times.get(transport_type, 5)
    total_minutes = round(total_minutes)

    if total_minutes < 60:
        return f"{total_minutes} mins"
    else:
        hours   = total_minutes // 60
        minutes = total_minutes % 60
        return f"{hours}h {minutes}m"


def get_route_note(
    transport_type: str,
    source:         str,
    destination:    str,
    crowd_level:    str
) -> str:
    """Generate a helpful route note."""
    notes = {
        "bus": {
            "LOW":    f"Direct bus from {source} to {destination} — smooth ride!",
            "MEDIUM": f"Buses running but expect some crowding near stops.",
            "HIGH":   f"Buses very crowded — consider waiting for next one.",
        },
        "metro": {
            "LOW":    f"Metro is the fastest option right now.",
            "MEDIUM": f"Metro is moderately busy — stand near doors for easy exit.",
            "HIGH":   f"Metro is packed — wait for the next train if possible.",
        },
        "train": {
            "LOW":    f"Train is comfortable and quick.",
            "MEDIUM": f"Train is filling up — board from less busy coaches.",
            "HIGH":   f"Train is very crowded — consider general vs reserved coaches.",
        },
        "chigari": {
            "LOW":    f"Chigari electric bus is running smoothly — eco-friendly choice!",
            "MEDIUM": f"Chigari is moderately occupied.",
            "HIGH":   f"Chigari is crowded — next bus in ~10 mins.",
        },
        "ferry": {
            "LOW":    f"Ferry is calm and comfortable.",
            "MEDIUM": f"Ferry is filling up — book your ticket early.",
            "HIGH":   f"Ferry is at capacity — next departure recommended.",
        },
    }
    transport_notes = notes.get(transport_type, {})
    return transport_notes.get(crowd_level, f"Travel from {source} to {destination}.")