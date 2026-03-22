from fastapi import APIRouter, HTTPException
from app.schemas.request import PredictionRequest, PredictionResponse
from app.models.loader import ModelLoader
from app.services.weather import get_forecast_weather   # ← ADD THIS
from datetime import datetime
import pandas as pd

router = APIRouter()

TRANSPORT_MAP = {'bus': 0, 'metro': 1, 'train': 2}
LABEL_MAP = {
    0: {"level": "LOW",    "emoji": "🟢", "advice": "Great time to travel — very comfortable!"},
    1: {"level": "MEDIUM", "emoji": "🟡", "advice": "Moderate crowd — plan accordingly."},
    2: {"level": "HIGH",   "emoji": "🔴", "advice": "Very crowded — consider an alternate time."}
}


def build_input(datetime_str, transport_type, is_holiday, temperature, weather_code, feature_columns):
    dt = datetime.fromisoformat(datetime_str)
    data = {
        'hour':              dt.hour,
        'day_of_week':       dt.weekday(),
        'month':             dt.month,
        'is_weekend':        int(dt.weekday() >= 5),
        'is_peak_hour':      int(dt.hour in [7, 8, 9, 17, 18, 19]),
        'is_holiday':        int(is_holiday),
        'temperature':       temperature,
        'weather_code':      weather_code,       # ← NEW
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

        # ── Auto-fetch real weather ──────────────────────────
        try:
            weather      = await get_forecast_weather(request.city, request.datetime_str)
            temperature  = weather["temperature"]
            weather_code = weather["weather_code"]
            weather_info = {
                "description": weather["description"],
                "emoji":       weather["weather_emoji"],
                "temperature": temperature
            }
            print(f"🌤️  Weather for {request.city}: {weather['description']} {weather['weather_emoji']} {temperature}°C")
        except Exception as e:
            # Fallback if weather API fails
            print(f"⚠️  Weather fetch failed: {e} — using defaults")
            temperature  = request.temperature or 25.0
            weather_code = 0
            weather_info = {"description": "Unknown", "emoji": "🌡️", "temperature": temperature}

        # ── Run predictions ──────────────────────────────────
        results = []
        for transport in request.transport_types:
            input_df   = build_input(
                request.datetime_str,
                transport.value,
                request.is_holiday,
                temperature,
                weather_code,
                feature_columns
            )
            pred_class = model.predict(input_df)[0]
            pred_proba = model.predict_proba(input_df)[0]
            confidence = round(float(pred_proba[pred_class]) * 100, 1)

            result = LABEL_MAP[pred_class].copy()
            result['transport']  = transport.value
            result['confidence'] = confidence
            results.append(result)

        results.sort(key=lambda x: ['LOW', 'MEDIUM', 'HIGH'].index(x['level']))
        best = results[0]

        return PredictionResponse(
            city=request.city,
            datetime_str=request.datetime_str,
            best_option=best['transport'],
            results=results,
            summary=f"Best option is {best['transport'].upper()} ({best['level']} crowd). {best['advice']}"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    return {"status": "ok", "model_loaded": ModelLoader._model is not None}