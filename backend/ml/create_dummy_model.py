import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import os

# Create dummy training data
X_dummy = np.array([
    [8,  0, 12, 0, 1, 0, 25.0, 1],   # morning weekday metro
    [18, 4, 12, 0, 1, 0, 28.0, 0],   # evening weekday bus
    [14, 6, 12, 1, 0, 0, 22.0, 2],   # afternoon weekend train
    [23, 2, 12, 0, 0, 0, 20.0, 1],   # night weekday metro
    [9,  1, 12, 0, 1, 1, 30.0, 2],   # morning holiday train
    [7,  0, 12, 0, 1, 0, 26.0, 0],   # rush hour bus
    [12, 5, 12, 1, 0, 0, 24.0, 1],   # noon weekend metro
    [17, 3, 12, 0, 1, 0, 27.0, 0],   # evening weekday bus
])

y_dummy = np.array([2, 2, 0, 0, 1, 1, 0, 2])  # HIGH, HIGH, LOW, LOW, MED, MED, LOW, HIGH

feature_columns = [
    'hour', 'day_of_week', 'month', 'is_weekend',
    'is_peak_hour', 'is_holiday', 'temperature', 'transport_encoded'
]

# Train a quick dummy model
model = RandomForestClassifier(n_estimators=10, random_state=42)
model.fit(X_dummy, y_dummy)

# Save it
os.makedirs("saved_models", exist_ok=True)
joblib.dump(model, "saved_models/crowd_model.joblib")
joblib.dump(feature_columns, "saved_models/feature_columns.joblib")

print("✅ Dummy model saved to saved_models/")
print("⚠️  Replace this with your real trained model later!")