from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def request_json(
    method: str,
    base_url: str,
    path: str,
    payload: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    query = ""
    if params:
        query = "?" + urlencode(
            {
                key: str(value).lower() if isinstance(value, bool) else value
                for key, value in params.items()
                if value is not None
            }
        )

    body = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = Request(
        f"{base_url.rstrip('/')}{path}{query}",
        data=body,
        method=method,
        headers=headers,
    )
    try:
        with urlopen(request, timeout=10) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {path} failed: HTTP {exc.code} {detail}") from exc
    except URLError as exc:
        raise RuntimeError(
            f"{method} {path} failed: cannot reach {base_url}. "
            "Start the FastAPI server first."
        ) from exc


def print_step(title: str, payload: dict[str, Any]) -> None:
    print(f"\n[{title}]")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Smoke-test Arduino sensor, Jetson recognition, inventory save, and recommendation APIs."
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--device-id", default="jetson-arduino-bridge")
    parser.add_argument("--ingredient", default="green_onion")
    parser.add_argument("--liquor", default="soju")
    parser.add_argument("--skip-inventory-save", action="store_true")
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    device_id = args.device_id

    ingredient_scan = request_json(
        "POST",
        base_url,
        "/api/v1/scan/ingredients/start",
        {"triggered_by": "smoke_hardware_flow", "device_id": device_id},
    )
    print_step("ingredient scan request", ingredient_scan)

    door_event = request_json(
        "POST",
        base_url,
        "/api/v1/sensors/events",
        {
            "device_id": device_id,
            "door_open": True,
            "motion_detected": False,
            "distance_cm": 8.0,
            "timestamp": utc_now(),
            "source": "arduino",
            "raw": {"pir": 0, "ultrasonic_cm": 8.0},
        },
    )
    print_step("door-open sensor event", door_event)
    if door_event.get("event", {}).get("recommended_mode") != "ingredient_scan":
        raise RuntimeError("door-open sensor event did not select ingredient_scan mode")

    ingredient_result = request_json(
        "POST",
        base_url,
        "/api/v1/recognitions/ingredients",
        {
            "ingredient_name": args.ingredient,
            "timestamp": utc_now(),
            "confidence": 0.93,
            "source": "jetson-ingredient-classifier",
            "scan_request_id": ingredient_scan["scan_request_id"],
        },
    )
    print_step("ingredient recognition", ingredient_result)

    if not args.skip_inventory_save:
        inventory_result = request_json(
            "POST",
            base_url,
            "/api/v1/inventory/bulk",
            {"items": [args.ingredient]},
        )
        print_step("inventory save", inventory_result)

    liquor_scan = request_json(
        "POST",
        base_url,
        "/api/v1/scan/liquor/start",
        {"triggered_by": "smoke_hardware_flow", "device_id": device_id},
    )
    print_step("liquor scan request", liquor_scan)

    motion_event = request_json(
        "POST",
        base_url,
        "/api/v1/sensors/events",
        {
            "device_id": device_id,
            "door_open": False,
            "motion_detected": True,
            "distance_cm": 32.4,
            "timestamp": utc_now(),
            "source": "arduino",
            "raw": {"pir": 1, "ultrasonic_cm": 32.4},
        },
    )
    print_step("motion sensor event", motion_event)
    if motion_event.get("event", {}).get("recommended_mode") != "liquor_scan_ready":
        raise RuntimeError("motion sensor event did not select liquor_scan_ready mode")

    liquor_result = request_json(
        "POST",
        base_url,
        "/api/v1/recognitions/liquor",
        {
            "liquor_name": args.liquor,
            "timestamp": utc_now(),
            "confidence": 0.97,
            "source": "jetson-liquor-classifier",
            "scan_request_id": liquor_scan["scan_request_id"],
        },
    )
    print_step("liquor recognition", liquor_result)

    time.sleep(0.2)
    recommendations = request_json(
        "GET",
        base_url,
        "/api/v1/recommendations",
        params={"liquor": args.liquor, "refresh": False},
    )
    print_step("recommendations", recommendations)

    items = recommendations.get("recommendations", [])
    if len(items) != 3:
        raise RuntimeError(f"expected 3 recommendations, got {len(items)}")

    first_ingredient_keys = [
        detail.get("item_name")
        for detail in items[0].get("ingredient_details", [])
        if isinstance(detail, dict)
    ]
    print(f"\nFirst recommendation ingredient keys: {first_ingredient_keys}")
    print("\nSmoke flow completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
