from __future__ import annotations

from typing import Any

from app.schemas.sensor import SensorEventCreate, SensorEventData, SensorRecommendedMode
from app.services.event_stream import sensor_event_broker


class SensorService:
    async def publish_sensor_event(self, payload: SensorEventCreate) -> SensorEventData:
        event = self.build_sensor_event(payload)
        await sensor_event_broker.publish(event.model_dump(mode="json"))
        return event

    def build_sensor_event(self, payload: SensorEventCreate) -> SensorEventData:
        extra = payload.model_extra or {}
        raw = dict(payload.raw)
        if extra:
            raw.update(extra)

        door_open = self._resolve_bool(
            payload.door_open,
            raw,
            aliases=("door_open", "door", "is_door_open", "door_state"),
        )
        motion_detected = self._resolve_bool(
            payload.motion_detected,
            raw,
            aliases=("motion_detected", "motion", "pir", "pir_state", "motion_state"),
        )
        distance_cm = self._resolve_float(
            payload.distance_cm,
            raw,
            aliases=("distance_cm", "distance", "ultrasonic_cm", "ultrasonic"),
        )

        door_open_value = bool(door_open)
        motion_detected_value = bool(motion_detected)
        recommended_mode = self._recommend_mode(
            door_open=door_open_value,
            motion_detected=motion_detected_value,
        )

        return SensorEventData(
            device_id=payload.device_id,
            door_open=door_open_value,
            motion_detected=motion_detected_value,
            distance_cm=distance_cm,
            recommended_mode=recommended_mode,
            timestamp=payload.timestamp,
            source=payload.source,
            raw=raw,
        )

    def _recommend_mode(
        self,
        *,
        door_open: bool,
        motion_detected: bool,
    ) -> SensorRecommendedMode:
        if door_open:
            return "ingredient_scan"
        if motion_detected:
            return "liquor_scan_ready"
        return "standby"

    def _resolve_bool(
        self,
        explicit_value: bool | None,
        raw: dict[str, Any],
        *,
        aliases: tuple[str, ...],
    ) -> bool | None:
        if explicit_value is not None:
            return explicit_value

        for alias in aliases:
            if alias not in raw:
                continue
            value = raw[alias]
            if isinstance(value, bool):
                return value
            if isinstance(value, (int, float)):
                return value != 0
            if isinstance(value, str):
                normalized = value.strip().lower()
                if normalized in {"1", "true", "yes", "y", "on", "open", "detected"}:
                    return True
                if normalized in {"0", "false", "no", "n", "off", "closed", "none"}:
                    return False
        return None

    def _resolve_float(
        self,
        explicit_value: float | None,
        raw: dict[str, Any],
        *,
        aliases: tuple[str, ...],
    ) -> float | None:
        if explicit_value is not None:
            return explicit_value

        for alias in aliases:
            if alias not in raw:
                continue
            value = raw[alias]
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str):
                try:
                    return float(value.strip())
                except ValueError:
                    continue
        return None
