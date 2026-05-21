from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


SensorRecommendedMode = Literal["ingredient_scan", "liquor_scan_ready", "standby"]


class SensorEventCreate(BaseModel):
    device_id: str = Field(
        default="jetson-arduino-bridge",
        min_length=1,
        max_length=100,
        description="Sensor source device ID. Arduino is connected through the Jetson bridge.",
    )
    door_open: bool | None = Field(
        default=None,
        description="Whether the ultrasonic sensor judged the refrigerator door as open.",
    )
    motion_detected: bool | None = Field(
        default=None,
        description="Whether the motion sensor detected user approach or movement.",
    )
    distance_cm: float | None = Field(
        default=None,
        ge=0,
        description="Optional ultrasonic distance reading in centimeters.",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Sensor event timestamp.",
    )
    source: str = Field(
        default="jetson-arduino-bridge",
        min_length=1,
        max_length=100,
        description="Sensor event source name.",
    )
    raw: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional raw Arduino or Jetson payload for debugging.",
    )

    model_config = {
        "extra": "allow",
        "json_schema_extra": {
            "example": {
                "device_id": "jetson-arduino-bridge",
                "door_open": False,
                "motion_detected": True,
                "distance_cm": 32.4,
                "source": "arduino",
                "raw": {"pir": 1, "ultrasonic_cm": 32.4},
            }
        },
    }


class SensorEventData(BaseModel):
    device_id: str
    door_open: bool
    motion_detected: bool
    distance_cm: float | None = None
    recommended_mode: SensorRecommendedMode
    timestamp: datetime
    source: str
    raw: dict[str, Any] = Field(default_factory=dict)


class SensorEventAcceptedResponse(BaseModel):
    status: Literal["success"] = "success"
    message: str
    event: SensorEventData
