import httpx
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

API_KEY  = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5"

# Weather code → simple category mapping
WEATHER_CODE_MAP = {
    range(200, 300): {"code": 3, "label": "Thunderstorm", "emoji": "⛈️"},
    range(300, 400): {"code": 2, "label": "Drizzle",      "emoji": "🌦️"},
    range(500, 600): {"code": 2, "label": "Rain",         "emoji": "🌧️"},
    range(600, 700): {"code": 1, "label": "Snow",         "emoji": "❄️"},
    range(700, 800): {"code": 1, "label": "Foggy",        "emoji": "🌫️"},
    range(800, 801): {"code": 0, "label": "Clear",        "emoji": "☀️"},
    range(801, 900): {"code": 1, "label": "Cloudy",       "emoji": "☁️"},
}

def get_weather_category(weather_id: int) -> dict:
    for code_range, info in WEATHER_CODE_MAP.items():
        if weather_id in code_range:
            return info
    return {"code": 0, "label": "Unknown", "emoji": "🌡️"}


async def get_current_weather(city: str) -> dict:
    """Fetch current weather for a city."""
    if not API_KEY:
        raise ValueError("❌ OPENWEATHER_API_KEY not set in .env file!")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/weather",
            params={
                "q":     city,
                "appid": API_KEY,
                "units": "metric"   # Celsius
            },
            timeout=10.0
        )

        if response.status_code == 404:
            raise ValueError(f"❌ City '{city}' not found in OpenWeatherMap")

        if response.status_code == 401:
            raise ValueError("❌ Invalid API key — check your .env file")

        response.raise_for_status()
        data = response.json()

        weather_id       = data["weather"][0]["id"]
        weather_category = get_weather_category(weather_id)

        return {
            "city":         city,
            "temperature":  round(data["main"]["temp"], 1),
            "feels_like":   round(data["main"]["feels_like"], 1),
            "humidity":     data["main"]["humidity"],
            "description":  data["weather"][0]["description"].title(),
            "weather_id":   weather_id,
            "weather_code": weather_category["code"],
            "weather_label":weather_category["label"],
            "weather_emoji":weather_category["emoji"],
            "wind_speed":   data["wind"]["speed"],
            "fetched_at":   datetime.utcnow().isoformat()
        }


async def get_forecast_weather(city: str, target_datetime: str) -> dict:
    """Fetch weather forecast for a future date (up to 5 days)."""
    if not API_KEY:
        raise ValueError("❌ OPENWEATHER_API_KEY not set in .env file!")

    target_dt = datetime.fromisoformat(target_datetime)
    now       = datetime.utcnow()
    diff_hours = (target_dt - now).total_seconds() / 3600

    # If date is within 5 days → use forecast API
    # If beyond 5 days → fall back to current weather
    if 0 < diff_hours <= 120:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/forecast",
                params={
                    "q":     city,
                    "appid": API_KEY,
                    "units": "metric",
                    "cnt":   40         # 5 days × 8 readings/day
                },
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()

            # Find forecast closest to target datetime
            best_match = min(
                data["list"],
                key=lambda x: abs(
                    datetime.fromtimestamp(x["dt"]) - target_dt
                )
            )

            weather_id       = best_match["weather"][0]["id"]
            weather_category = get_weather_category(weather_id)

            return {
                "city":          city,
                "temperature":   round(best_match["main"]["temp"], 1),
                "feels_like":    round(best_match["main"]["feels_like"], 1),
                "humidity":      best_match["main"]["humidity"],
                "description":   best_match["weather"][0]["description"].title(),
                "weather_id":    weather_id,
                "weather_code":  weather_category["code"],
                "weather_label": weather_category["label"],
                "weather_emoji": weather_category["emoji"],
                "wind_speed":    best_match["wind"]["speed"],
                "fetched_at":    datetime.utcnow().isoformat()
            }

    # Fallback → current weather
    return await get_current_weather(city)