from fastapi import APIRouter, HTTPException
from app.schemas.request import PredictionRequest, PredictionResponse
from app.models.loader import ModelLoader
from app.services.weather import get_forecast_weather
from app.services.holiday import get_holiday_impact        # ← ADD
from datetime import datetime
import pandas as pd

router = APIRouter()

TRANSPORT_MAP = {'bus': 0, 'metro': 1, 'train': 2}
LABEL_MAP = {
    0: {"level": "LOW",    "emoji": "🟢", "advice": "Great time to travel — very comfortable!"},
    1: {"level": "MEDIUM", "emoji": "🟡", "advice": "Moderate crowd — plan accordingly."},
    2: {"level": "HIGH",   "emoji": "🔴", "advice": "Very crowded — consider an alternate time."}
}

# Crowd multiplier → bump up predicted class
def apply_multiplier(pred_class: int, multiplier: float) -> int:
    if multiplier >= 2.0:
        return min(pred_class + 2, 2)
    elif multiplier >= 1.5:
        return min(pred_class + 1, 2)
    return pred_class


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

        # ── 1. Fetch Weather ─────────────────────────────────
        try:
            weather      = await get_forecast_weather(request.city, request.datetime_str)
            temperature  = weather["temperature"]
            weather_code = weather["weather_code"]
            print(f"🌤️  Weather: {weather['description']} {weather['weather_emoji']} {temperature}°C")
        except Exception as e:
            print(f"⚠️  Weather fetch failed: {e}")
            temperature  = request.temperature or 25.0
            weather_code = 0
            weather      = None

        # ── 2. Fetch Holiday Impact ──────────────────────────
        try:
            holiday_data = await get_holiday_impact(request.datetime_str)
            is_holiday   = holiday_data["is_holiday"]
            multiplier   = holiday_data["crowd_multiplier"]
            print(f"📅  Holiday impact: {holiday_data['impact_label']} (×{multiplier})")
            if holiday_data["reasons"]:
                print(f"    Reasons: {', '.join(holiday_data['reasons'])}")
        except Exception as e:
            print(f"⚠️  Holiday fetch failed: {e}")
            holiday_data = None
            is_holiday   = request.is_holiday
            multiplier   = 1.0

        # ── 3. Run Predictions ───────────────────────────────
        results = []
        for transport in request.transport_types:
            input_df   = build_input(
                request.datetime_str,
                transport.value,
                is_holiday,
                temperature,
                weather_code,
                feature_columns
            )
            pred_class = int(model.predict(input_df)[0])
            pred_proba = model.predict_proba(input_df)[0]

            # Apply holiday crowd multiplier
            adjusted_class = apply_multiplier(pred_class, multiplier)
            confidence     = round(float(pred_proba[pred_class]) * 100, 1)

            result = LABEL_MAP[adjusted_class].copy()
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