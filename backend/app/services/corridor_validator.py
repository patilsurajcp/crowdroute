import googlemaps
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(BASE_DIR, ".env"))

GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
gmaps          = googlemaps.Client(key=GOOGLE_API_KEY) if GOOGLE_API_KEY else None

print(f"🗺️  Corridor Validator: {'✅ Google Maps connected' if gmaps else '⚠️  No API key - using fallback'}")

# Twin city corridors
TWIN_CITY_MAP = {
    "hubli":   ["hubli", "hubballi", "dharwad", "hubli-dharwad"],
    "dharwad": ["hubli", "hubballi", "dharwad", "hubli-dharwad"],
}

# Ferry cities
FERRY_CITIES = [
    "mumbai", "kochi", "guwahati",
    "port blair", "panaji", "kavaratti"
]

# Hill/shared cab cities
HILL_CITIES = [
    "gangtok", "shillong", "shimla",
    "darjeeling", "mussoorie", "nainital",
    "manali", "ooty", "kodaikanal"
]

# Water keywords for ferry/shikara
WATER_KEYWORDS = {
    "ferry": [
        "jetty", "ghat", "wharf", "pier", "dock",
        "ferry", "harbour", "harbor", "port",
        "gateway", "island", "creek", "bridge",
    ],
    "shikara": [
        "lake", "dal", "nagin", "ghat", "houseboat",
        "boulevard", "water", "floating", "char chinar",
    ],
}


def get_location_info(place: str, city: str) -> dict:
    """
    Geocode a place and return city/district it falls in.
    Returns dict with city, district, state, lat, lng.
    """
    if not gmaps:
        return {
            "city":        city.lower(),
            "district":    city.lower(),
            "state":       "unknown",
            "sublocality": "",
            "lat":         0,
            "lng":         0
        }

    try:
        # Try with city context first
        results = gmaps.geocode(f"{place}, {city}, India")
        if not results:
            results = gmaps.geocode(f"{place}, India")
        if not results:
            return {
                "city":        city.lower(),
                "district":    city.lower(),
                "state":       "unknown",
                "sublocality": "",
                "lat":         0,
                "lng":         0
            }

        components = results[0]["address_components"]
        location   = results[0]["geometry"]["location"]

        data = {
            "lat":         location["lat"],
            "lng":         location["lng"],
            "city":        "",
            "district":    "",
            "state":       "",
            "sublocality": "",
            "locality":    "",
        }

        for comp in components:
            types = comp["types"]
            if "locality" in types:
                data["city"] = comp["long_name"].lower()
            elif "administrative_area_level_2" in types:
                data["district"] = comp["long_name"].lower()
            elif "administrative_area_level_1" in types:
                data["state"] = comp["long_name"].lower()
            elif "sublocality" in types or "sublocality_level_1" in types:
                data["sublocality"] = comp["long_name"].lower()
            elif "neighborhood" in types:
                data["locality"] = comp["long_name"].lower()

        print(f"📍 Geocoded '{place}' → city={data['city']} district={data['district']}")
        return data

    except Exception as e:
        print(f"⚠️  Geocoding failed for '{place}': {e}")
        return {
            "city":        city.lower(),
            "district":    city.lower(),
            "state":       "unknown",
            "sublocality": "",
            "lat":         0,
            "lng":         0
        }


def is_within_city(place: str, expected_city: str) -> bool:
    """
    Check if a place is within the expected city using geocoding.
    """
    if not gmaps:
        return True

    loc      = get_location_info(place, expected_city)
    expected = expected_city.lower()

    return (
        expected in loc.get("city",     "") or
        expected in loc.get("district", "") or
        loc.get("city",     "").replace(" ", "") in expected.replace(" ", "") or
        loc.get("district", "").replace(" ", "") in expected.replace(" ", "")
    )


def _is_in_twin_city(loc_data: dict, valid_cities: list) -> bool:
    """Check if geocoded location is within twin city corridor."""
    city_str = (
        loc_data.get("city",        "") + " " +
        loc_data.get("district",    "") + " " +
        loc_data.get("sublocality", "") + " " +
        loc_data.get("locality",    "")
    ).lower()
    return any(vc in city_str for vc in valid_cities)


def validate_corridor(
    transport_type: str,
    source:         str,
    destination:    str,
    city:           str
) -> dict:
    """
    Master validator — uses Google Maps geocoding to check
    if transport is valid for the route in the city.
    Works for ALL Indian cities automatically.
    """
    t          = transport_type.lower()
    city_lower = city.lower()

    # ── bus, metro, train → always valid city-wide ───────────
    if t in ["bus", "metro", "train"]:
        return {"valid": True, "reason": None}

    # ── chigari ──────────────────────────────────────────────
    # Only Hubli-Dharwad twin city corridor
    if t == "chigari":
        valid_twin = TWIN_CITY_MAP.get(city_lower)

        if not valid_twin:
            return {
                "valid":  False,
                "reason": f"Chigari only operates in Hubli-Dharwad twin city, not in {city}."
            }

        # Geocode both ends
        src_loc  = get_location_info(source,      city)
        dest_loc = get_location_info(destination, city)

        src_valid  = _is_in_twin_city(src_loc,  valid_twin)
        dest_valid = _is_in_twin_city(dest_loc, valid_twin)

        print(f"⚡ Chigari: src_valid={src_valid} dest_valid={dest_valid}")

        if src_valid and dest_valid:
            return {"valid": True, "reason": None}
        elif not src_valid:
            return {
                "valid":  False,
                "reason": f"'{source}' is outside Hubli-Dharwad corridor. Chigari cannot serve this route."
            }
        else:
            return {
                "valid":  False,
                "reason": f"'{destination}' is outside Hubli-Dharwad corridor. Chigari cannot serve this route."
            }

    # ── tram ─────────────────────────────────────────────────
    # Only Kolkata
    elif t == "tram":
        if city_lower != "kolkata":
            return {
                "valid":  False,
                "reason": f"Tram only operates in Kolkata, not in {city}."
            }
        src_valid  = is_within_city(source,      "Kolkata")
        dest_valid = is_within_city(destination, "Kolkata")
        if src_valid and dest_valid:
            return {"valid": True, "reason": None}
        return {
            "valid":  False,
            "reason": "Tram route not available — locations must be within Kolkata tram network."
        }

    # ── ferry ─────────────────────────────────────────────────
    elif t == "ferry":
        if city_lower not in FERRY_CITIES:
            return {
                "valid":  False,
                "reason": f"Ferry service is not available in {city}."
            }

        # Kavaratti — entire island uses ferry
        if city_lower == "kavaratti":
            return {"valid": True, "reason": None}

        # Check if source or destination mentions water-related keywords
        src_lower  = source.lower()
        dest_lower = destination.lower()
        water_kw   = WATER_KEYWORDS["ferry"]
        near_water = any(
            kw in src_lower or kw in dest_lower
            for kw in water_kw
        )
        if near_water:
            return {"valid": True, "reason": None}

        # Geocode and check within city
        src_valid  = is_within_city(source,      city)
        dest_valid = is_within_city(destination, city)
        if src_valid or dest_valid:
            return {"valid": True, "reason": None}

        return {
            "valid":  False,
            "reason": f"Ferry does not serve this route in {city}. Ensure one end is at a ghat/jetty/port."
        }

    # ── toy_train ─────────────────────────────────────────────
    elif t == "toy_train":
        if city_lower != "shimla":
            return {
                "valid":  False,
                "reason": f"Toy Train only runs on Kalka-Shimla heritage route, not in {city}."
            }
        src_valid  = is_within_city(source,      "Shimla")
        dest_valid = is_within_city(destination, "Shimla")
        if src_valid or dest_valid:
            return {"valid": True, "reason": None}
        return {
            "valid":  False,
            "reason": "Toy Train only runs between Kalka and Shimla railway stations."
        }

    # ── shikara ───────────────────────────────────────────────
    elif t == "shikara":
        if city_lower != "srinagar":
            return {
                "valid":  False,
                "reason": f"Shikara only operates in Srinagar, not in {city}."
            }
        src_lower  = source.lower()
        dest_lower = destination.lower()
        water_kw   = WATER_KEYWORDS["shikara"]
        near_water = any(
            kw in src_lower or kw in dest_lower
            for kw in water_kw
        )
        if near_water:
            return {"valid": True, "reason": None}

        src_valid = is_within_city(source, "Srinagar")
        if src_valid:
            return {"valid": True, "reason": None}
        return {
            "valid":  False,
            "reason": "Shikara only operates on Dal Lake and Nagin Lake in Srinagar."
        }

    # ── shared_cab ────────────────────────────────────────────
    elif t == "shared_cab":
        if city_lower not in HILL_CITIES:
            return {
                "valid":  False,
                "reason": f"Shared cab service is not standard in {city}."
            }
        src_valid = is_within_city(source, city)
        if src_valid:
            return {"valid": True, "reason": None}
        return {
            "valid":  False,
            "reason": f"Shared cab route not available for '{source}' in {city}."
        }

    # ── default — allow ───────────────────────────────────────
    return {"valid": True, "reason": None}