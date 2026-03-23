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

EMOJI_MAP = {
    "Bus": "🚌 Bus", "Metro": "🚇 Metro", "Train": "🚆 Train",
    "Chigari": "⚡ Chigari", "Ferry": "⛴️ Ferry", "Tram": "🚋 Tram",
    "Toy Train": "🚂 Toy Train", "Shared Cab": "🚖 Shared Cab",
    "Shikara": "🛶 Shikara",
}

DEFAULT_TRANSPORT = ["bus", "train"]


def get_transport_types(city: str) -> list:
    return CITY_TRANSPORT.get(city, DEFAULT_TRANSPORT)


def get_transport_info(transport_type: str) -> dict:
    info  = TRANSPORT_INFO.get(transport_type, {
        "label":       transport_type.title(),
        "description": transport_type.title()
    })
    label = info.get("label", transport_type.title())
    return {
        "label":       EMOJI_MAP.get(label, f"🚌 {label}"),
        "description": info.get("description", label)
    }
'''

with open("app/data/metro_cities.py", "w", encoding="utf-8") as f:
    f.write(content.strip())
print("metro_cities.py written successfully!")

# Verify
import importlib.util
spec = importlib.util.spec_from_file_location("metro_cities", "app/data/metro_cities.py")
mod  = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
print("get_transport_types('Hubli'):", mod.get_transport_types("Hubli"))
print("get_transport_info('chigari'):", mod.get_transport_info("chigari"))
print("Total cities:", len(mod.CITY_TRANSPORT))