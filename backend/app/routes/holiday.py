from fastapi import APIRouter, HTTPException
from app.services.holiday import get_holiday_impact

router = APIRouter()


@router.get("/holiday/impact", tags=["Holiday"])
async def holiday_impact(datetime_str: str, country: str = "IN"):
    try:
        return await get_holiday_impact(datetime_str, country)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))