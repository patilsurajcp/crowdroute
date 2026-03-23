from fastapi import APIRouter, HTTPException
from app.schemas.request       import PredictionRequest, PredictionResponse
from app.models.loader         import ModelLoader
from app.services.weather      import get_forecast_weather
from app.services.holiday      import get_holiday_impact
from app.services.route        import (
    get_route_data,
    get_traffic_crowd_multiplier,
    estimate_travel_time_from_route,
    get_route_note
)
from app.services.corridor_validator import validate_corridor
from datetime import datetime
import pandas as pd

router = APIRouter()

TRANSPORT_MAP = {
    'bus': 0, 'metro': 1, 'train': 2,
    'chigari': 0, 'ferry': 1, 'tram': 1,
    'toy_train': 2, 'shared_cab': 0, 'shikara': 0
}

LABEL_MAP = {
    0: {"level": "LOW",    "emoji": "🟢", "advice": "Great time to travel — very comfortable!"},
    1: {"level": "MEDIUM", "emoji": "🟡", "advice": "Moderate crowd — plan accordingly."},
    2: {"level": "HIGH",   "emoji": "🔴", "advice": "Very crowded — consider an alternate time."}
}

# All Indian city names for intercity detection
INDIAN_CITIES = [
    "mumbai", "delhi", "bengaluru", "bangalore", "chennai", "kolkata",
    "hyderabad", "pune", "ahmedabad", "jaipur", "lucknow", "hubli",
    "dharwad", "hubballi", "surat", "indore", "bhopal", "patna", "nagpur",
    "kochi", "chandigarh", "mysuru", "mysore", "coimbatore", "madurai",
    "visakhapatnam", "agra", "varanasi", "amritsar", "ranchi", "bhubaneswar",
    "guwahati", "shimla", "srinagar", "dehradun", "jodhpur", "rajkot",
    "vadodara", "ludhiana", "jalandhar", "meerut", "faridabad", "noida",
    "gurgaon", "gurugram", "vijayawada", "thiruvananthapuram", "thrissur",
    "salem", "tiruchirappalli", "tiruppur", "kozhikode", "allahabad",
    "kanpur", "gwalior", "jabalpur", "raipur", "nashik", "aurangabad",
    "solapur", "gorakhpur", "bareilly", "moradabad", "saharanpur", "bikaner",
    "kota", "ajmer", "udaipur", "bhilai", "bilaspur", "howrah", "durgapur",
    "warangal", "guntur", "nellore", "tirupati", "kurnool", "mangaluru",
    "mangalore", "belgaum", "belagavi", "gulbarga", "davanagere", "shimoga",
]


def is_intercity_route(source: str, destination: str, city: str) -> bool:
    """
    Detect if the route spans multiple cities.
    Uses full address strings from Google Places autocomplete.
    """
    city_lower = city.lower()
    dest_lower = destination.lower()
    src_lower  = source.lower()

    # Check if destination explicitly mentions a different Indian city
    for other_city in INDIAN_CITIES:
        if other_city == city_lower:
            continue
        # Skip if it's just a substring match with selected city
        if other_city in city_lower or city_lower in other_city:
            continue
        if other_city in dest_lower:
            print(f"🚌 Intercity detected: destination contains '{other_city}' (selected: {city})")
            return True

    # Also check if source is in a different city than destination
    src_cities  = [c for c in INDIAN_CITIES if c in src_lower]
    dest_cities = [c for c in INDIAN_CITIES if c in dest_lower]

    if src_cities and dest_cities:
        if set(src_cities).isdisjoint(set(dest_cities)):
            print(f"🚌 Intercity: src_cities={src_cities} dest_cities={dest_cities}")
            return True

    return False


def apply_multiplier(pred_class: int, multiplier: float) -> int:
    if multiplier >= 2.0:   return min(pred_class + 2, 2)
    elif multiplier >= 1.5: return min(pred_class + 1, 2)
    return pred_class


def build_input(
    datetime_str, transport_type, is_holiday,
    temperature, weather_code, feature_columns
):
    dt = datetime.fromisoformat(datetime_str)
    data = {
        'hour':              dt.hour,
        'day_of_week':       dt.weekday(),
        'month':             dt.month,
        'is_weekend':        int(dt.weekday() >= 5),
        'is_peak_hour':      int(dt.hour in [7, 8, 9, 17, 18, 19]),
        'is_holiday':        int(is_holiday),
        'temperature':       temperature,
        'weather_code':      weather_code,
        'transport_encoded': TRANSPORT_MAP.get(transport_type, 1)
    }
    df = pd.DataFrame([data])
    df = df[[col for col in feature_columns if col in df.columns]]
    return df


@router.post("/predict", response_model=PredictionResponse)
async def predict_crowd(request: PredictionRequest):
    try:
        model           = ModelLoader.get_model()
        feature_columns = ModelLoader.get_feature_columns()

        # ── 1. Detect Intercity ──────────────────────────────
        intercity = is_intercity_route(
            request.source,
            request.destination,
            request.city
        )
        print(f"🗺️  Route: {request.source} → {request.destination}")
        print(f"🌐  Intercity: {intercity}")

        # ── 2. Validate Transport Corridors ──────────────────
        filtered_transports = []
        warnings            = []

        for transport in request.transport_types:
            # For intercity routes — only bus and train are valid
            if intercity and transport.value not in ['bus', 'train']:
                warnings.append(
                    f"{transport.value.upper()} removed — not available for intercity travel."
                )
                print(f"❌ {transport.value} removed (intercity)")
                continue

            validation = validate_corridor(
                transport.value,
                request.source,
                request.destination,
                request.city
            )
            if validation["valid"]:
                filtered_transports.append(transport)
                print(f"✅ {transport.value} valid")
            else:
                warnings.append(f"{transport.value.upper()}: {validation['reason']}")
                print(f"❌ {transport.value} removed — {validation['reason']}")

        # Fallback
        if not filtered_transports:
            from app.schemas.request import TransportType
            filtered_transports = [TransportType.train, TransportType.bus] \
                if intercity else [TransportType.bus]
            warnings.append("All transports removed — using defaults.")

        # ── 3. Get Route + Traffic from Google Maps ──────────
        route_data = get_route_data(
            request.source,
            request.destination,
            request.city,
            request.datetime_str
        )
        distance_km        = route_data["distance_km"]
        traffic_level      = route_data["traffic_level"]
        traffic_ratio      = route_data["traffic_ratio"]
        traffic_multiplier = get_traffic_crowd_multiplier(traffic_ratio)
        print(f"📏  Distance: {distance_km} km | Traffic: {traffic_level} ×{traffic_multiplier}")

        # ── 4. Fetch Weather ─────────────────────────────────
        try:
            weather      = await get_forecast_weather(request.city, request.datetime_str)
            temperature  = weather["temperature"]
            weather_code = weather["weather_code"]
            print(f"🌤️  Weather: {weather['description']} {temperature}°C")
        except Exception as e:
            print(f"⚠️  Weather failed: {e}")
            temperature  = request.temperature or 25.0
            weather_code = 0

        # ── 5. Fetch Holiday Impact ──────────────────────────
        try:
            holiday_data   = await get_holiday_impact(request.datetime_str)
            is_holiday     = holiday_data["is_holiday"]
            hol_multiplier = holiday_data["crowd_multiplier"]
            print(f"📅  Holiday: {holiday_data['impact_label']} ×{hol_multiplier}")
        except Exception as e:
            print(f"⚠️  Holiday failed: {e}")
            is_holiday     = request.is_holiday
            hol_multiplier = 1.0

        # ── 6. Combined Multiplier ───────────────────────────
        # For intercity — traffic on long routes matters less
        if intercity:
            traffic_multiplier = 1.0   # reset — highway traffic ≠ city crowd
        combined_multiplier = min(hol_multiplier * traffic_multiplier, 2.5)
        print(f"📊  Combined multiplier: ×{combined_multiplier:.2f}")

        # ── 7. Run Predictions ───────────────────────────────
        results = []
        for transport in filtered_transports:
            input_df       = build_input(
                request.datetime_str, transport.value,
                is_holiday, temperature, weather_code, feature_columns
            )
            pred_class     = int(model.predict(input_df)[0])
            pred_proba     = model.predict_proba(input_df)[0]
            adjusted_class = apply_multiplier(pred_class, combined_multiplier)
            confidence     = round(float(pred_proba[pred_class]) * 100, 1)
            label          = LABEL_MAP[adjusted_class]
            travel_time    = estimate_travel_time_from_route(
                route_data, transport.value, label["level"]
            )
            route_note     = get_route_note(
                transport.value, request.source,
                request.destination, label["level"],
                route_data.get("via")
            )
            results.append({
                "transport":      transport.value,
                "level":          label["level"],
                "emoji":          label["emoji"],
                "confidence":     confidence,
                "advice":         label["advice"],
                "estimated_time": travel_time,
                "route_note":     route_note,
            })

        # ── 8. Sort & Build Response ─────────────────────────
        results.sort(key=lambda x: ['LOW', 'MEDIUM', 'HIGH'].index(x['level']))
        best     = results[0]
        time_str = (
            f", ~{best['estimated_time']}"
            if best['estimated_time'] and best['estimated_time'] != 'N/A'
            else ""
        )
        intercity_note = " (Intercity)" if intercity else ""
        summary = (
            f"Best option is {best['transport'].upper()}"
            f" ({best['level']} crowd{time_str}){intercity_note}. {best['advice']}"
        )
        if warnings:
            summary += " | ⚠️ " + " | ".join(warnings)

        # NEW — always show traffic ✅
        route_summary = (
        f"{request.source} → {request.destination}"
        + (f" ({distance_km} km)"              if distance_km else "")
        + (" 🌐 Intercity"                     if intercity   else "")
        + (f" · {route_data['traffic_emoji']} {traffic_level} traffic"
       if traffic_level != 'UNKNOWN'       else "")
    )

        return PredictionResponse(
            city=request.city,
            source=request.source,
            destination=request.destination,
            datetime_str=request.datetime_str,
            best_option=best['transport'],
            results=results,
            summary=summary,
            route_summary=route_summary
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    return {
        "status":       "ok",
        "model_loaded": ModelLoader._model is not None
    }