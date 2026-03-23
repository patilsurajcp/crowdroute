# ── Real transport availability per Indian city ──────────────
CITY_TRANSPORT = {
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
    "bus":        {"label": "🚌 Bus",        "description": "City bus service"},
    "metro":      {"label": "🚇 Metro",      "description": "Underground/elevated metro rail"},
    "train":      {"label": "🚆 Train",      "description": "Indian Railways / suburban rail"},
    "chigari":    {"label": "⚡ Chigari",    "description": "Electric bus — Hubli-Dharwad corridor only"},
    "ferry":      {"label": "⛴️ Ferry",      "description": "Water transport — specific water routes only"},
    "tram":       {"label": "🚋 Tram",       "description": "Heritage tram — Kolkata specific routes only"},
    "toy_train":  {"label": "🚂 Toy Train",  "description": "Narrow gauge — Shimla Kalka route only"},
    "shared_cab": {"label": "🚖 Shared Cab", "description": "Shared taxi — hill route corridors only"},
    "shikara":    {"label": "🛶 Shikara",    "description": "Wooden boat — Dal Lake Srinagar only"},
}

DEFAULT_TRANSPORT = ["bus", "train"]


# ════════════════════════════════════════════════════════════
# CORRIDOR DEFINITIONS — per transport type
# Each entry has:
#   cities    → which cities this transport operates in
#   keywords  → location keywords that indicate valid corridor
#   both_ends → True = both source & dest must be in corridor
#               False = at least one end must be in corridor
# ════════════════════════════════════════════════════════════

TRANSPORT_CORRIDORS = {

    # ── Chigari ─────────────────────────────────────────────
    # Operates within Hubli-Dharwad twin city only
    "chigari": {
        "cities": ["Hubli", "Dharwad"],
        "both_ends": True,
        "description": "Hubli-Dharwad twin city corridor",
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

    # ── Tram ────────────────────────────────────────────────
    # Kolkata tram runs on specific north-south routes only
    "tram": {
        "cities": ["Kolkata"],
        "both_ends": False,
        "description": "Kolkata tram network (Esplanade, Shyambazar, Gariahat routes)",
        "keywords": [
            "esplanade", "shyambazar", "gariahat", "ballygunge",
            "tollygunge", "howrah", "maidan", "park street",
            "kalighat", "rabindra sarani", "college street",
            "shyambazar five point crossing", "ultadanga",
            "belgachia", "narkeldanga", "sealdah", "dharmatala",
            "birla planetarium", "victoria memorial",
            "princep ghat", "strand road", "burrabazar",
            "jorasanko", "maniktala", "phoolbagan",
        ]
    },

    # ── Ferry — Mumbai ───────────────────────────────────────
    # Mumbai ferry runs Gateway of India to Elephanta/Mandwa/Alibaug
    "ferry_mumbai": {
        "cities": ["Mumbai"],
        "both_ends": False,
        "description": "Mumbai ferry routes (Gateway of India, Alibaug, Mandwa)",
        "keywords": [
            "gateway of india", "colaba", "elephanta",
            "mandwa", "alibaug", "rewas", "mora",
            "ferry wharf", "bhaucha dhakka", "mazagaon",
            "juhu", "versova", "gorai", "manori",
        ]
    },

    # ── Ferry — Kochi ────────────────────────────────────────
    # Kochi ferry operates between Fort Kochi, Ernakulam, Mattancherry
    "ferry_kochi": {
        "cities": ["Kochi"],
        "both_ends": False,
        "description": "Kochi water metro & ferry routes",
        "keywords": [
            "fort kochi", "ernakulam", "mattancherry",
            "willingdon island", "vypeen", "bolgatty",
            "high court jetty", "main jetty", "customs jetty",
            "vaikom", "alleppey", "marine drive",
            "kakkanad", "edapally",
        ]
    },

    # ── Ferry — Guwahati ─────────────────────────────────────
    # Guwahati ferry crosses Brahmaputra river
    "ferry_guwahati": {
        "cities": ["Guwahati"],
        "both_ends": False,
        "description": "Guwahati Brahmaputra river ferry crossings",
        "keywords": [
            "umananda", "peacock island", "north guwahati",
            "south guwahati", "pandu", "fancy bazar",
            "pan bazar", "sukreswar ghat", "kachari ghat",
            "silghat", "neamati",
        ]
    },

    # ── Ferry — Port Blair ───────────────────────────────────
    "ferry_port_blair": {
        "cities": ["Port Blair"],
        "both_ends": False,
        "description": "Andaman ferry inter-island routes",
        "keywords": [
            "port blair", "havelock", "neil island",
            "phoenix bay jetty", "haddo wharf",
            "ross island", "north bay", "corbyn's cove",
            "wandoor", "chidiyatapu",
        ]
    },

    # ── Ferry — Panaji ───────────────────────────────────────
    "ferry_panaji": {
        "cities": ["Panaji"],
        "both_ends": False,
        "description": "Goa ferry river crossings",
        "keywords": [
            "panaji", "betim", "old goa", "ribandar",
            "cortalim", "zuari", "mandovi river",
            "panjim", "campal", "miramar",
        ]
    },

    # ── Toy Train — Shimla ───────────────────────────────────
    # Kalka-Shimla narrow gauge heritage railway
    "toy_train": {
        "cities": ["Shimla"],
        "both_ends": False,
        "description": "Kalka-Shimla UNESCO heritage railway",
        "keywords": [
            "shimla", "kalka", "solan", "kandaghat",
            "barog", "dharampur", "kumarhatti",
            "taradevi", "tara devi", "jutogh",
            "summer hill", "shoghi", "railway station",
        ]
    },

    # ── Shikara ─────────────────────────────────────────────
    # Only on Dal Lake and Nagin Lake, Srinagar
    "shikara": {
        "cities": ["Srinagar"],
        "both_ends": False,
        "description": "Dal Lake & Nagin Lake shikara routes",
        "keywords": [
            "dal lake", "nagin lake", "dal gate",
            "nehru park", "hazratbal", "srinagar",
            "nishat bagh", "shalimar bagh", "chashme shahi",
            "boulevard road", "lal chowk", "old city",
            "houseboats", "floating market", "char chinar",
        ]
    },

    # ── Shared Cab — Gangtok ─────────────────────────────────
    # Shared jeeps/cabs run on fixed hill routes
    "shared_cab_gangtok": {
        "cities": ["Gangtok"],
        "both_ends": False,
        "description": "Gangtok shared jeep routes to major points",
        "keywords": [
            "gangtok", "mg marg", "mahatma gandhi marg",
            "rumtek", "phodong", "singtam", "rangpo",
            "namchi", "ravangla", "pelling", "yuksom",
            "nathula", "tsomgo lake", "baba mandir",
            "tadong", "deorali", "new market",
        ]
    },

    # ── Shared Cab — Shillong ────────────────────────────────
    "shared_cab_shillong": {
        "cities": ["Shillong"],
        "both_ends": False,
        "description": "Shillong shared cab routes",
        "keywords": [
            "shillong", "police bazar", "laitumkhrah",
            "bara bazar", "iewduh", "mawlai", "nongthymmai",
            "cherrapunji", "sohra", "mawsynram",
            "dawki", "jowai", "nongpoh", "jorabat",
            "umiam", "barapani", "guwahati",
        ]
    },
}


# ── Unified ferry check (city-specific) ─────────────────────
FERRY_CORRIDOR_MAP = {
    "Mumbai":    "ferry_mumbai",
    "Kochi":     "ferry_kochi",
    "Guwahati":  "ferry_guwahati",
    "Port Blair":"ferry_port_blair",
    "Panaji":    "ferry_panaji",
    "Kavaratti": None,   # entire island = ferry everywhere
}

SHARED_CAB_CORRIDOR_MAP = {
    "Gangtok":  "shared_cab_gangtok",
    "Shillong": "shared_cab_shillong",
}


def _check_corridor(source: str, destination: str, corridor_key: str) -> bool:
    """Generic corridor checker."""
    if corridor_key not in TRANSPORT_CORRIDORS:
        return True   # No restriction defined → allow
    corridor  = TRANSPORT_CORRIDORS[corridor_key]
    keywords  = corridor["keywords"]
    src       = source.lower()
    dest      = destination.lower()
    src_match  = any(k in src  for k in keywords)
    dest_match = any(k in dest for k in keywords)
    if corridor["both_ends"]:
        return src_match and dest_match
    else:
        return src_match or dest_match


def is_chigari_route(source: str, destination: str) -> bool:
    return _check_corridor(source, destination, "chigari")


def is_tram_route(source: str, destination: str) -> bool:
    return _check_corridor(source, destination, "tram")


def is_ferry_route(source: str, destination: str, city: str) -> bool:
    if city == "Kavaratti":
        return True   # Entire island uses ferry
    corridor_key = FERRY_CORRIDOR_MAP.get(city)
    if not corridor_key:
        return False
    return _check_corridor(source, destination, corridor_key)


def is_toy_train_route(source: str, destination: str) -> bool:
    return _check_corridor(source, destination, "toy_train")


def is_shikara_route(source: str, destination: str) -> bool:
    return _check_corridor(source, destination, "shikara")


def is_shared_cab_route(source: str, destination: str, city: str) -> bool:
    corridor_key = SHARED_CAB_CORRIDOR_MAP.get(city)
    if not corridor_key:
        return True   # Generic shared cab → allow
    return _check_corridor(source, destination, corridor_key)


def validate_transport_for_route(
    transport_type: str,
    source: str,
    destination: str,
    city: str
) -> dict:
    """
    Master validator — checks if a transport type is valid
    for the given source → destination route in the city.
    Returns: { valid: bool, reason: str }
    """
    t = transport_type.lower()

    if t == "chigari":
        valid = is_chigari_route(source, destination)
        return {
            "valid":  valid,
            "reason": None if valid else
                      "Chigari only operates within Hubli-Dharwad corridor."
        }

    elif t == "tram":
        valid = is_tram_route(source, destination)
        return {
            "valid":  valid,
            "reason": None if valid else
                      "Tram only runs on specific Kolkata routes (Esplanade, Shyambazar, Gariahat)."
        }

    elif t == "ferry":
        valid = is_ferry_route(source, destination, city)
        return {
            "valid":  valid,
            "reason": None if valid else
                      f"Ferry does not serve this route in {city}. Check water-accessible ghats/jetties."
        }

    elif t == "toy_train":
        valid = is_toy_train_route(source, destination)
        return {
            "valid":  valid,
            "reason": None if valid else
                      "Toy Train only runs on the Kalka-Shimla heritage railway route."
        }

    elif t == "shikara":
        valid = is_shikara_route(source, destination)
        return {
            "valid":  valid,
            "reason": None if valid else
                      "Shikara only operates on Dal Lake and Nagin Lake in Srinagar."
        }

    elif t == "shared_cab":
        valid = is_shared_cab_route(source, destination, city)
        return {
            "valid":  valid,
            "reason": None if valid else
                      f"Shared cab route not available for this destination in {city}."
        }

    # bus, metro, train → always valid (city-wide)
    return {"valid": True, "reason": None}


def get_transport_types(city: str) -> list:
    return CITY_TRANSPORT.get(city, DEFAULT_TRANSPORT)


def get_transport_info(transport_type: str) -> dict:
    return TRANSPORT_INFO.get(transport_type, {
        "label":       f"🚌 {transport_type.title()}",
        "description": transport_type.title()
    })