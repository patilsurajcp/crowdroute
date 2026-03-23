import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.predict import router as predict_router
from app.routes.weather import router as weather_router
from app.routes.holiday import router as holiday_router
from app.routes.city    import router as city_router
from app.models.loader  import ModelLoader


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🔄 Loading ML model...")
    ModelLoader.get_model()
    ModelLoader.get_feature_columns()
    print("✅ CrowdRoute API is ready!")
    yield
    print("🛑 Shutting down CrowdRoute API...")


app = FastAPI(
    title="🚌 CrowdRoute API",
    description="Predict crowd levels across public transport options",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict_router, prefix="/api/v1", tags=["Predictions"])
app.include_router(weather_router, prefix="/api/v1", tags=["Weather"])
app.include_router(holiday_router, prefix="/api/v1", tags=["Holiday"])
app.include_router(city_router,    prefix="/api/v1", tags=["City"])


@app.get("/", tags=["General"])
async def root():
    return {
        "message":     "🚌 Welcome to CrowdRoute API",
        "description": "Predict crowd levels across public transport",
        "docs":        "/docs",
        "health":      "/api/v1/health",
        "version":     "1.0.0"
    }