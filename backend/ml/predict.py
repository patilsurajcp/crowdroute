import joblib
import pandas as pd
from datetime import datetime

# Load model once at startup
model = joblib.load("saved_models/crowd_model.joblib")
feature_columns = joblib.load("saved_models/feature_columns.joblib")

LABEL_MAP = {
    0: {"level": "LOW",    "emoji": "🟢", "advice": "Great time to travel — very comfortable!"},
    1: {"level": "MEDIUM", "emoji": "🟡", "advice": "Moderate crowd — plan accordingly."},
    2: {"level": "HIGH",   "emoji": "🔴", "advice": "Very crowded — consider an alternate time."}
}

TRANSPORT_MAP = {'bus': 0, 'metro': 1, 'train': 2}


def build_input(
    datetime_str: str,
    transport_type: str,
    is_holiday: bool = False,
    temperature: float = 25.0
) -> pd.DataFrame:
    dt = datetime.fromisoformat(datetime_str)

    data = {
        'hour':              dt.hour,
        'day_of_week':       dt.weekday(),
        'month':             dt.month,
        'is_weekend':        int(dt.weekday() >= 5),
        'is_peak_hour':      int(dt.hour in [7, 8, 9, 17, 18, 19]),
        'is_holiday':        int(is_holiday),
        'temperature':       temperature,
        'transport_encoded': TRANSPORT_MAP.get(transport_type, 1)
    }

    # Only use features the model was trained on
    df = pd.DataFrame([data])
    df = df[[col for col in feature_columns if col in df.columns]]
    return df


def predict_crowd(
    datetime_str: str,
    transport_types: list,
    is_holiday: bool = False,
    temperature: float = 25.0
) -> list:
    results = []

    for transport in transport_types:
        input_df = build_input(datetime_str, transport, is_holiday, temperature)
        pred_class = model.predict(input_df)[0]
        pred_proba = model.predict_proba(input_df)[0]
        confidence = round(float(pred_proba[pred_class]) * 100, 1)

        result = LABEL_MAP[pred_class].copy()
        result['transport'] = transport
        result['confidence'] = confidence
        results.append(result)

    # Sort by crowd level (LOW first = best recommendation)
    results.sort(key=lambda x: ['LOW', 'MEDIUM', 'HIGH'].index(x['level']))
    return results


# ── Quick test ───────────────────────────────────────────────
if __name__ == "__main__":
    predictions = predict_crowd(
        datetime_str="2024-12-25T08:30:00",
        transport_types=["bus", "metro", "train"],
        is_holiday=True,
        temperature=22.0
    )

    print("\n🚌 CrowdRoute Predictions:")
    print("=" * 40)
    for p in predictions:
        print(f"{p['emoji']} {p['transport'].upper():<8} → {p['level']:<6} ({p['confidence']}% confidence)")
        print(f"   💬 {p['advice']}")
    print("\n✅ Best option:", predictions[0]['transport'].upper())
