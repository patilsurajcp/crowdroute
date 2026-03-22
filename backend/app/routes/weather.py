from fastapi import APIRouter, HTTPException
from app.services.weather import get_current_weather, get_forecast_weather

router = APIRouter()

@router.get("/weather/current/{city}", tags=["Weather"])
async def current_weather(city: str):
    try:
        return await get_current_weather(city)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/weather/forecast/{city}", tags=["Weather"])
async def forecast_weather(city: str, datetime_str: str):
    try:
        return await get_forecast_weather(city, datetime_str)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))