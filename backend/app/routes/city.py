from fastapi import APIRouter, HTTPException
from app.data.metro_cities import get_transport_types, get_transport_info, CITY_TRANSPORT

router = APIRouter()


@router.get("/city/transport/{city}", tags=["City"])
async def city_transport(city: str):
    transports = get_transport_types(city)
    return {
        "city":       city,
        "transports": [
            {"type": t, **get_transport_info(t)}
            for t in transports
        ]
    }


@router.get("/cities", tags=["City"])
async def list_cities():
    return {
        "cities": sorted(CITY_TRANSPORT.keys()),
        "total":  len(CITY_TRANSPORT)
    }