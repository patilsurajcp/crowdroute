from fastapi import APIRouter, HTTPException
from app.services.availability import get_all_availability
from app.data.metro_cities import (
    get_metro_info, has_metro,
    get_all_metro_cities, METRO_CITIES
)

router = APIRouter()


@router.get("/availability", tags=["Availability"])
async def check_availability(
    city:         str,
    datetime_str: str,
    to_city:      str = None
):
    """
    Check real-time seat availability for all transport modes.
    Metro section only appears if city has an operational metro.
    """
    try:
        return await get_all_availability(city, datetime_str, to_city)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metro/cities", tags=["Metro"])
async def metro_cities():
    """Get all Indian cities with metro systems."""
    operational = []
    upcoming    = []

    for city, info in METRO_CITIES.items():
        entry = {
            "city":     city,
            "operator": info["operator"],
            "lines":    len(info.get("lines", [])),
            "stations": info.get("total_stations", 0),
        }
        if info.get("operational"):
            operational.append(entry)
        else:
            entry["status"] = info.get("status", "planned")
            upcoming.append(entry)

    return {
        "operational_count": len(operational),
        "upcoming_count":    len(upcoming),
        "operational":       operational,
        "upcoming":          upcoming
    }


@router.get("/metro/{city}", tags=["Metro"])
async def city_metro_info(city: str, datetime_str: str = None):
    """Get metro details and crowd estimate for a specific city."""
    info = get_metro_info(city)
    if not info:
        raise HTTPException(
            status_code=404,
            detail=f"No metro data found for {city}"
        )
    if not info["has_metro"]:
        return {
            "city":       city,
            "has_metro":  False,
            "status":     info["status"],
            "message":    f"{city} metro is {info['status']}",
            "operator":   info["operator"]
        }

    # Add live crowd if datetime provided
    if datetime_str:
        from app.services.availability import get_metro_crowd
        crowd = get_metro_crowd(city, datetime_str)
        info["crowd"] = crowd

    return info