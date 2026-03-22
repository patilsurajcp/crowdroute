from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class TransportType(str, Enum):
    bus   = "bus"
    metro = "metro"
    train = "train"

class PredictionRequest(BaseModel):
    datetime_str:     str            = Field(..., example="2024-12-25T08:30:00")
    city:             str            = Field(..., example="Mumbai")
    transport_types:  List[TransportType] = Field(
        default=["bus", "metro", "train"]
    )
    is_holiday:       Optional[bool]  = False
    temperature:      Optional[float] = 25.0

    model_config = {
    "json_schema_extra": {
        "example": {
            "datetime_str":    "2024-12-25T08:30:00",
            "city":            "Mumbai",
            "transport_types": ["bus", "metro", "train"],
            "is_holiday":      True,
            "temperature":     22.0
        }
    }
}


class TransportPrediction(BaseModel):
    transport:   str
    level:       str        # LOW / MEDIUM / HIGH
    emoji:       str        # 🟢 🟡 🔴
    confidence:  float
    advice:      str

class PredictionResponse(BaseModel):
    city:            str
    datetime_str:    str
    best_option:     str
    results:         List[TransportPrediction]
    summary:         str