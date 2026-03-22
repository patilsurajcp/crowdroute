from fastapi import APIRouter, HTTPException
from app.services.holiday import get_holiday_impact

router = APIRouter()

@router.get("/holiday/impact", tags=["Holiday"])
async def holiday_impact(datetime_str: str, country: str = "IN"):
    """
    Analyze holiday impact for a given date.
    Example: /api/v1/holiday/impact?datetime_str=2024-12-25T10:00:00
    """
    try:
        return await get_holiday_impact(datetime_str, country)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))