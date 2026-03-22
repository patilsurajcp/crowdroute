from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class TransportType(str, Enum):
    bus        = "bus"
    metro      = "metro"
    train      = "train"
    chigari    = "chigari"
    ferry      = "ferry"
    tram       = "tram"
    toy_train  = "toy_train"
    shared_cab = "shared_cab"
    shikara    = "shikara"

class PredictionRequest(BaseModel):
    datetime_str:     str
    city:             str
    transport_types:  List[TransportType] = ["bus", "train"]
    is_holiday:       Optional[bool]  = False
    temperature:      Optional[float] = 25.0

    model_config = {
        "json_schema_extra": {
            "example": {
                "datetime_str":    "2024-12-25T08:30:00",
                "city":            "Hubli",
                "transport_types": ["bus", "chigari", "train"],
                "is_holiday":      False,
                "temperature":     25.0
            }
        }
    }

class TransportPrediction(BaseModel):
    transport:   str
    level:       str
    emoji:       str
    confidence:  float
    advice:      str

class PredictionResponse(BaseModel):
    city:         str
    datetime_str: str
    best_option:  str
    results:      List[TransportPrediction]
    summary:      str