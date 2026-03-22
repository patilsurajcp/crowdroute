import sys
import os

# ── Fix Python path so 'app' module is always found ──────────
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.predict import router as predict_router
from app.models.loader import ModelLoader
from app.routes.weather import router as weather_router
from app.routes.holiday import router as holiday_router
from app.routes.city import router as city_router
# ── Lifespan (replaces deprecated @app.on_event) ─────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🔄 Loading ML model...")
    ModelLoader.get_model()
    ModelLoader.get_feature_columns()
    print("✅ CrowdRoute API is ready!")
    yield
    # Shutdown (add cleanup here if needed)
    print("🛑 Shutting down CrowdRoute API...")


# ── Initialize App ────────────────────────────────────────────
app = FastAPI(
    title="🚌 CrowdRoute API",
    description="Predict crowd levels across public transport options and find your best ride.",
    version="1.0.0",
    lifespan=lifespan
)


# ── CORS Middleware ───────────────────────────────────────────
# Allows React frontend (localhost:5173) to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # React Vite dev server
        "http://localhost:3000",   # React CRA dev server (backup)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Register Routes ───────────────────────────────────────────
app.include_router(predict_router, prefix="/api/v1", tags=["Predictions"])
app.include_router(weather_router, prefix="/api/v1", tags=["Weather"])
app.include_router(holiday_router, prefix="/api/v1", tags=["Holiday"])
app.include_router(city_router, prefix="/api/v1", tags=["City"])
# ── Root Endpoint ─────────────────────────────────────────────
@app.get("/", tags=["General"])
async def root():
    return {
        "message":     "🚌 Welcome to CrowdRoute API",
        "description": "Predict crowd levels across public transport",
        "docs":        "/docs",
        "health":      "/api/v1/health",
        "version":     "1.0.0"
    }