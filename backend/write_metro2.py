content = '''CITY_TRANSPORT = {
    "Mumbai":            ["bus", "metro", "train", "ferry"],
    "Delhi":             ["bus", "metro", "train"],
    "Kolkata":           ["bus", "metro", "train", "tram"],
    "Chennai":           ["bus", "metro", "train"],
    "Bengaluru":         ["bus", "metro"],
    "Hyderabad":         ["bus", "metro"],
    "Pune":              ["bus", "metro", "train"],
    "Ahmedabad":         ["bus", "metro"],
    "Jaipur":            ["bus", "metro"],
    "Kochi":             ["bus", "metro", "train", "ferry"],
    "Lucknow":           ["bus", "metro"],
    "Nagpur":            ["bus", "metro"],
    "Noida":             ["bus", "metro"],
    "Chandigarh":        ["bus"],
    "Faridabad":         ["bus", "metro", "train"],
    "Hubli":             ["bus", "chigari", "train"],
    "Dharwad":           ["bus", "chigari", "train"],
    "Shimla":            ["bus", "toy_train"],
    "Gangtok":           ["bus", "shared_cab"],
    "Port Blair":        ["bus", "ferry"],
    "Panaji":            ["bus", "ferry"],
    "Srinagar":          ["bus", "shikara"],
    "Shillong":          ["bus", "shared_cab"],
    "Kavaratti":         ["ferry"],
    "Surat":             ["bus", "train"],
    "Vadodara":          ["bus", "train"],
    "Indore":            ["bus", "train"],
    "Bhopal":            ["bus", "train"],
    "Patna":             ["bus", "train"],
    "Coimbatore":        ["bus", "train"],
    "Madurai":           ["bus", "train"],
    "Vijayawada":        ["bus", "train"],
    "Warangal":          ["bus", "train"],
    "Tiruppur":          ["bus", "train"],
    "Tiruchirappalli":   ["bus", "train"],
    "Mysuru":            ["bus", "train"],
    "Guwahati":          ["bus", "train", "ferry"],
    "Bhubaneswar":       ["bus", "train"],
    "Ranchi":            ["bus", "train"],
    "Jamshedpur":        ["bus", "train"],
    "Amritsar":          ["bus", "train"],
    "Jalandhar":         ["bus", "train"],
    "Ludhiana":          ["bus", "train"],
    "Agra":              ["bus", "train"],
    "Varanasi":          ["bus", "train"],
    "Allahabad":         ["bus", "train"],
    "Jodhpur":           ["bus", "train"],
    "Bikaner":           ["bus", "train"],
    "Dehradun":          ["bus", "train"],
    "Thiruvananthapuram":["bus", "train"],
    "Kozhikode":         ["bus", "train"],
    "Thrissur":          ["bus", "train"],
    "Salem":             ["bus", "train"],
    "Raipur":            ["bus", "train"],
    "Nashik":            ["bus", "train"],
    "Aurangabad":        ["bus", "train"],
    "Solapur":           ["bus", "train"],
    "Bhilai":            ["bus", "train"],
    "Cuttack":           ["bus", "train"],
    "Gorakhpur":         ["bus", "train"],
    "Bareilly":          ["bus", "train"],
    "Moradabad":         ["bus", "train"],
    "Saharanpur":        ["bus", "train"],
    "Gwalior":           ["bus", "train"],
    "Jabalpur":          ["bus", "train"],
    "Meerut":            ["bus", "train"],
    "Rajkot":            ["bus", "train"],
    "Kota":              ["bus", "train"],
    "Dhanbad":           ["bus", "train"],
    "Howrah":            ["bus", "train"],
    "Bhiwandi":          ["bus", "train"],
    "Firozabad":         ["bus", "train"],
    "Amravati":          ["bus", "train"],
    "Guntur":            ["bus", "train"],
    "Kanpur":            ["bus", "train"],
    "Aizawl":            ["bus"],
    "Imphal":            ["bus"],
    "Kohima":            ["bus"],
    "Itanagar":          ["bus"],
    "Dispur":            ["bus"],
    "Agartala":          ["bus"],
    "Silvassa":          ["bus"],
    "Daman":             ["bus"],
}

TRANSPORT_INFO = {
    "bus":        {"label": "Bus",        "description": "City bus service"},
    "metro":      {"label": "Metro",      "description": "Underground/elevated metro rail"},
    "train":      {"label": "Train",      "description": "Indian Railways / suburban rail"},
    "chigari":    {"label": "Chigari",    "description": "Electric bus - Hubli-Dharwad corridor only"},
    "ferry":      {"label": "Ferry",      "description": "Water transport - specific routes only"},
    "tram":       {"label": "Tram",       "description": "Heritage tram - Kolkata specific routes only"},
    "toy_train":  {"label": "Toy Train",  "description": "Narrow gauge - Shimla Kalka route only"},
    "shared_cab": {"label": "Shared Cab", "description": "Shared taxi - hill route corridors only"},
    "shikara":    {"label": "Shikara",    "description": "Wooden boat - Dal Lake Srinagar only"},
}

DEFAULT_TRANSPORT = ["bus", "train"]

TRANSPORT_CORRIDORS = {
    "chigari": {
        "cities":      ["Hubli", "Dharwad"],
        "both_ends":   True,
        "description": "Hubli-Dharwad twin city corridor only",
        "keywords": [
            "hubli", "dharwad", "hubballi", "keshwapur",
            "vidyanagar", "gokul", "navanagar", "unkal",
            "hosur", "durgadbail", "tarihal", "hdmc",
            "ksrtc", "cpc", "sadashivnagar", "shivbasavnagar",
            "akshay colony", "shirur park", "jubilee circle",
            "koppikar road", "club road", "lamington road",
            "deshpande nagar", "belur", "dharwad bus stand",
            "toll naka", "rto", "vishwavidyalaya",
            "kittur rani channamma circle",
        ]
    },
    "tram": {
        "cities":      ["Kolkata"],
        "both_ends":   False,
        "description": "Kolkata tram - Esplanade, Shyambazar, Gariahat routes",
        "keywords": [
            "esplanade", "shyambazar", "gariahat", "ballygunge",
            "tollygunge", "maidan", "park street", "kalighat",
            "college street", "ultadanga", "sealdah", "dharmatala",
            "victoria memorial", "princep ghat", "burrabazar",
            "maniktala", "phoolbagan", "rabindra sarani",
        ]
    },
    "ferry": {
        "cities":      ["Mumbai", "Kochi", "Guwahati", "Port Blair", "Panaji", "Kavaratti"],
        "both_ends":   False,
        "description": "Water routes - ghats, jetties and water terminals only",
        "keywords": [
            "gateway of india", "colaba", "elephanta", "mandwa",
            "alibaug", "ferry wharf", "bhaucha dhakka", "gorai",
            "manori", "versova", "fort kochi", "ernakulam",
            "mattancherry", "willingdon island", "vypeen",
            "bolgatty", "high court jetty", "main jetty",
            "umananda", "north guwahati", "pandu", "fancy bazar",
            "sukreswar ghat", "havelock", "neil island",
            "phoenix bay jetty", "ross island", "betim",
            "old goa", "ribandar", "mandovi river",
        ]
    },
    "toy_train": {
        "cities":      ["Shimla"],
        "both_ends":   False,
        "description": "Kalka-Shimla UNESCO heritage narrow gauge railway",
        "keywords": [
            "shimla", "kalka", "solan", "kandaghat", "barog",
            "dharampur", "kumarhatti", "taradevi", "jutogh",
            "summer hill", "shoghi", "railway station",
        ]
    },
    "shikara": {
        "cities":      ["Srinagar"],
        "both_ends":   False,
        "description": "Dal Lake and Nagin Lake only",
        "keywords": [
            "dal lake", "nagin lake", "dal gate", "nehru park",
            "hazratbal", "nishat bagh", "shalimar bagh",
            "boulevard road", "houseboats", "floating market",
            "char chinar", "lal chowk",
        ]
    },
    "shared_cab": {
        "cities":      ["Gangtok", "Shillong"],
        "both_ends":   False,
        "description": "Hill route shared jeep/cab corridors",
        "keywords": [
            "gangtok", "mg marg", "rumtek", "rangpo", "namchi",
            "pelling", "nathula", "tsomgo", "tadong", "deorali",
            "shillong", "police bazar", "laitumkhrah", "iewduh",
            "cherrapunji", "dawki", "barapani",
        ]
    },
}


def _check_corridor(source, destination, corridor_key):
    if corridor_key not in TRANSPORT_CORRIDORS:
        return True
    corridor   = TRANSPORT_CORRIDORS[corridor_key]
    keywords   = corridor["keywords"]
    src        = source.lower()
    dest       = destination.lower()
    src_match  = any(k in src  for k in keywords)
    dest_match = any(k in dest for k in keywords)
    if corridor["both_ends"]:
        return src_match and dest_match
    return src_match or dest_match


def validate_transport_for_route(transport_type, source, destination, city):
    t = transport_type.lower()
    if t == "chigari":
        valid = _check_corridor(source, destination, "chigari")
        return {"valid": valid, "reason": None if valid else "Chigari only operates within Hubli-Dharwad corridor."}
    elif t == "tram":
        valid = _check_corridor(source, destination, "tram")
        return {"valid": valid, "reason": None if valid else "Tram only runs on specific Kolkata routes."}
    elif t == "ferry":
        if city == "Kavaratti":
            return {"valid": True, "reason": None}
        valid = _check_corridor(source, destination, "ferry")
        return {"valid": valid, "reason": None if valid else f"Ferry does not serve this route in {city}."}
    elif t == "toy_train":
        valid = _check_corridor(source, destination, "toy_train")
        return {"valid": valid, "reason": None if valid else "Toy Train only runs on Kalka-Shimla route."}
    elif t == "shikara":
        valid = _check_corridor(source, destination, "shikara")
        return {"valid": valid, "reason": None if valid else "Shikara only operates on Dal Lake and Nagin Lake."}
    elif t == "shared_cab":
        valid = _check_corridor(source, destination, "shared_cab")
        return {"valid": valid, "reason": None if valid else f"Shared cab route not available for this route in {city}."}
    return {"valid": True, "reason": None}


def is_chigari_route(source, destination):
    return _check_corridor(source, destination, "chigari")


def get_transport_types(city):
    return CITY_TRANSPORT.get(city, DEFAULT_TRANSPORT)


def get_transport_info(transport_type):
    info = TRANSPORT_INFO.get(transport_type, {
        "label":       transport_type.title(),
        "description": transport_type.title()
    })
    # Add emoji labels
    emoji_map = {
        "Bus": "🚌 Bus", "Metro": "🚇 Metro", "Train": "🚆 Train",
        "Chigari": "⚡ Chigari", "Ferry": "⛴️ Ferry", "Tram": "🚋 Tram",
        "Toy Train": "🚂 Toy Train", "Shared Cab": "🚖 Shared Cab",
        "Shikara": "🛶 Shikara",
    }
    label = info.get("label", transport_type.title())
    return {
        "label":       emoji_map.get(label, f"🚌 {label}"),
        "description": info.get("description", label)
    }
'''

with open("app/data/metro_cities.py", "w", encoding="utf-8") as f:
    f.write(content.strip())

print("File written successfully!")

# Verify
import importlib.util
spec = importlib.util.spec_from_file_location("metro_cities", "app/data/metro_cities.py")
mod  = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
print("validate_transport_for_route found:", hasattr(mod, "validate_transport_for_route"))
print("Chigari test:", mod.validate_transport_for_route("chigari", "keshwapur", "dharwad bus stand", "Hubli"))
print("Ferry test:  ", mod.validate_transport_for_route("ferry",   "gateway of india", "elephanta", "Mumbai"))
print("Tram test:   ", mod.validate_transport_for_route("tram",    "esplanade", "shyambazar", "Kolkata"))
print("Bus test:    ", mod.validate_transport_for_route("bus",     "anywhere", "anywhere", "Delhi"))