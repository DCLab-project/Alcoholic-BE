# AI API Contract

이 문서는 Jetson/AI 쪽에서 BE로 인식 결과를 전송할 때 지켜야 하는 계약입니다. AI API는 내부 입력용이며, FE 화면에는 SSE와 추천 API를 통해 전달됩니다.

## 공통

- Base URL local: `http://127.0.0.1:8000`
- Content-Type: `application/json`
- timestamp: ISO 8601 UTC 권장
- confidence: `0.0` 이상 `1.0` 이하, 모르면 생략 가능
- source: 모델 또는 장치/파이프라인 이름

## Sensor Event (Jetson-Arduino Bridge)

Arduino는 Jetson에 연결된 센서 입력 장치로 사용합니다. 초음파 거리 센서와 모션감지 센서의 판단 결과는 Jetson 또는 Jetson-Arduino bridge 프로세스가 백엔드로 전달합니다. 이 API는 센서 상태를 기록하고 SSE로 전달하기 위한 보조 흐름이며, 실제 식재료/주류 인식 결과는 기존 recognition API로 별도 전송합니다.

### POST `/api/v1/sensors/events`

Request:

```json
{
  "device_id": "jetson-arduino-bridge",
  "door_open": false,
  "motion_detected": true,
  "distance_cm": 32.4,
  "source": "arduino",
  "raw": {
    "pir": 1,
    "ultrasonic_cm": 32.4
  }
}
```

Response:

```json
{
  "status": "success",
  "message": "센서 이벤트가 수신되었습니다.",
  "event": {
    "device_id": "jetson-arduino-bridge",
    "door_open": false,
    "motion_detected": true,
    "distance_cm": 32.4,
    "recommended_mode": "liquor_scan_ready",
    "timestamp": "2026-05-19T12:00:00Z",
    "source": "arduino",
    "raw": {
      "pir": 1,
      "ultrasonic_cm": 32.4
    }
  }
}
```

Mode policy:

- `door_open=true`이면 식재료 반입·반출 가능성을 우선하여 `recommended_mode=ingredient_scan`
- `door_open=false`이고 `motion_detected=true`이면 주류 촬영 준비 상태로 보고 `recommended_mode=liquor_scan_ready`
- 두 조건이 모두 아니면 `recommended_mode=standby`

Side effect:

- `GET /api/v1/stream/sensors` 구독자에게 `sensor` 이벤트 발행
- 이 이벤트만으로 추천을 생성하지 않습니다. 주류 추천은 `/api/v1/recognitions/liquor`로 확정된 주류 카테고리가 전송된 뒤 수행합니다.

## Ingredient Recognition

### POST `/api/v1/recognitions/ingredients`

AI가 식재료 하나를 감지할 때마다 호출합니다. 이 단계는 바로 inventory DB에 저장하지 않고, FE가 구독 중인 식재료 SSE로만 전달합니다. 사용자가 FE에서 최종 저장하면 `/api/v1/inventory/bulk`가 호출됩니다.

Request:

```json
{
  "ingredient_name": "green_onion",
  "timestamp": "2026-04-27T12:00:00Z",
  "confidence": 0.93,
  "source": "ingredient_classifier"
}
```

Response:

```json
{
  "status": "success",
  "message": "식재료 인식 이벤트가 발행되었습니다."
}
```

Side effect:

- `GET /api/v1/stream/ingredients` 구독자에게 `ingredient_name`, `timestamp` 이벤트 발행

## Ingredient Key Policy

BE 추천 seed core ingredient key는 27개입니다.

```text
bacon, beef, bread, broccoli, butter, cabbage, carrot, cheese, chicken,
cucumber, egg, eggplant, fish, garlic, green_onion, lettuce, milk,
mushroom, onion, pepper, pork, potato, sausage, spinach, tomato,
yogurt, zucchini
```

AI label 차이 처리:

- `beef`, `pork`는 AI 추가 예정 클래스이므로 BE seed core ingredient로 사용합니다.
- `leek`, `scallion`, `spring_onion`은 BE에서 `green_onion`으로 정규화합니다.
- `ginger`는 AI label에는 있을 수 있지만 추천 seed core ingredient로 사용하지 않습니다.
- `pepper`는 고추가 아니라 파프리카입니다.
- `fish`, `mushroom`, `cheese`는 broad key입니다. AI/BE 모두 세부 품종을 확정하지 않습니다.

AI가 보내면 좋은 값:

```text
green_onion
beef
pork
pepper
```

전환기 호환 값:

```text
leek
scallion
spring_onion
spring onion
```

위 값들은 BE에서 `green_onion`으로 정규화합니다.

## Liquor Recognition

### POST `/api/v1/recognitions/liquor`

AI가 주류를 감지했을 때 호출합니다. BE는 주류 SSE를 먼저 발행하고, 이어 추천 결과를 계산해 추천 SSE를 발행합니다.

Request:

```json
{
  "liquor_name": "soju",
  "timestamp": "2026-04-27T12:00:05Z",
  "confidence": 0.97,
  "source": "liquor_classifier"
}
```

Response:

```json
{
  "status": "success",
  "message": "주류 인식 이벤트가 발행되었습니다."
}
```

Supported liquor keys:

```text
soju, beer, red_wine, white_wine, sparkling_wine, whisky, sake
```

Side effects:

- `GET /api/v1/stream/liquor` 구독자에게 주류 이벤트 발행
- `GET /api/v1/stream/recommendations` 구독자에게 추천 결과 이벤트 발행

## Failure/Retry Guidance

- BE가 4xx를 반환하면 payload key 또는 타입을 확인합니다.
- 네트워크 실패는 같은 timestamp/source로 재시도해도 됩니다.
- 동일 프레임에서 같은 label이 반복 감지되면 AI 쪽에서 debounce 후 전송하는 것을 권장합니다.

