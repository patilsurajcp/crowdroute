import joblib
import os

# ── Absolute path to saved_models/ ───────────────────────────
BACKEND_DIR  = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH   = os.path.join(BACKEND_DIR, "ml", "saved_models", "crowd_model.joblib")
COLUMNS_PATH = os.path.join(BACKEND_DIR, "ml", "saved_models", "feature_columns.joblib")

print(f"📂 Looking for model at: {MODEL_PATH}")   # helpful debug line


class ModelLoader:
    _model           = None
    _feature_columns = None

    @classmethod
    def get_model(cls):
        if cls._model is None:
            print("🔄 Loading ML model...")
            if not os.path.exists(MODEL_PATH):
                raise FileNotFoundError(
                    f"❌ Model not found at {MODEL_PATH}\n"
                    f"👉 Run: cd backend/ml && python create_dummy_model.py"
                )
            cls._model = joblib.load(MODEL_PATH)
            print("✅ Model loaded successfully!")
        return cls._model

    @classmethod
    def get_feature_columns(cls):
        if cls._feature_columns is None:
            cls._feature_columns = joblib.load(COLUMNS_PATH)
        return cls._feature_columns