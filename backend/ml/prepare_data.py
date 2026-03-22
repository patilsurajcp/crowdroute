import pandas as pd
import numpy as np

def load_and_prepare(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath)

    # ── Parse datetime ──────────────────────────────────────
    df['datetime'] = pd.to_datetime(df['datetime'])  # adjust column name
    df['hour']        = df['datetime'].dt.hour
    df['day_of_week'] = df['datetime'].dt.dayofweek  # 0=Mon, 6=Sun
    df['month']       = df['datetime'].dt.month
    df['is_weekend']  = df['day_of_week'].isin([5, 6]).astype(int)
    df['is_peak_hour']= df['hour'].isin([7,8,9,17,18,19]).astype(int)

    # ── Create target label ──────────────────────────────────
    # Adjust thresholds based on YOUR dataset's ridership range
    def label_crowd(count):
        if count < 1000:
            return 0   # LOW
        elif count < 3000:
            return 1   # MEDIUM
        else:
            return 2   # HIGH

    df['crowd_level'] = df['passenger_count'].apply(label_crowd)

    # ── Encode transport type ────────────────────────────────
    transport_map = {'bus': 0, 'metro': 1, 'train': 2}
    df['transport_encoded'] = df['transport_type'].map(transport_map)

    # ── Drop rows with nulls ─────────────────────────────────
    df = df.dropna(subset=['crowd_level', 'hour', 'passenger_count'])

    return df


def get_features_and_target(df: pd.DataFrame):
    features = [
        'hour',
        'day_of_week',
        'month',
        'is_weekend',
        'is_peak_hour',
        'is_holiday',       # add if available
        'temperature',      # add if available
        'transport_encoded'
    ]
    # Only use columns that exist in your dataset
    features = [f for f in features if f in df.columns]

    X = df[features]
    y = df['crowd_level']
    return X, y