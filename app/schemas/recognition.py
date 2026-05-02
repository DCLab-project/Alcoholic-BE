from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


class IngredientLiveRecognitionCreate(BaseModel):
    ingredient_name: str = Field(
        min_length=1,
        max_length=100,
        description="인식된 식재료 이름입니다. 한글명과 내부 key를 모두 허용합니다. 예: 대파, green_onion",
        examples=["대파"],
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="식재료가 감지된 시각입니다. ISO 8601 형식을 권장합니다.",
    )
    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="AI 모델의 신뢰도입니다. 선택 필드이며 0.0에서 1.0 사이 값을 사용합니다.",
        examples=[0.93],
    )
    source: str = Field(
        default="ingredient_classifier",
        min_length=1,
        max_length=100,
        description="이 인식 결과를 보낸 모델 또는 서비스 이름입니다.",
        examples=["ingredient_classifier"],
    )
    scan_request_id: str | None = Field(default=None, max_length=100)

    model_config = {
        "json_schema_extra": {
            "example": {
                "ingredient_name": "대파",
                "timestamp": "2026-04-10T17:16:01Z",
                "confidence": 0.93,
                "source": "ingredient_classifier",
            }
        }
    }


class IngredientStreamEvent(BaseModel):
    ingredient_name: str = Field(description="실시간으로 감지된 식재료 한글 이름입니다.")
    timestamp: datetime = Field(description="해당 식재료 이벤트가 발생한 시각입니다.")
    scan_request_id: str | None = Field(default=None)


class LiquorLiveRecognitionCreate(BaseModel):
    liquor_name: str = Field(
        min_length=1,
        max_length=100,
        description="인식된 주류 이름입니다. 한글명과 내부 key를 모두 허용합니다. 예: 소주, soju",
        examples=["소주"],
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="주류가 감지된 시각입니다. ISO 8601 형식을 권장합니다.",
    )
    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="AI 모델의 신뢰도입니다. 선택 필드이며 0.0에서 1.0 사이 값을 사용합니다.",
        examples=[0.97],
    )
    source: str = Field(
        default="liquor_classifier",
        min_length=1,
        max_length=100,
        description="이 인식 결과를 보낸 모델 또는 서비스 이름입니다.",
        examples=["liquor_classifier"],
    )
    scan_request_id: str | None = Field(default=None, max_length=100)

    model_config = {
        "json_schema_extra": {
            "example": {
                "liquor_name": "소주",
                "timestamp": "2026-04-10T17:20:00Z",
                "confidence": 0.97,
                "source": "liquor_classifier",
            }
        }
    }


class LiquorStreamEvent(BaseModel):
    liquor_name: str = Field(description="실시간으로 감지된 주류 한글 이름입니다.")
    timestamp: datetime = Field(description="해당 주류 이벤트가 발생한 시각입니다.")
    scan_request_id: str | None = Field(default=None)


class LiveRecognitionAcceptedResponse(BaseModel):
    status: Literal["success"] = Field(description="요청 처리 결과 상태입니다.")
    message: str = Field(description="처리 결과를 설명하는 메시지입니다.")


class LiquorScanStartRequest(BaseModel):
    triggered_by: str = Field(
        min_length=1,
        max_length=100,
        description="주류 스캔 요청을 발생시킨 주체입니다. 예: frontend",
        examples=["frontend"],
    )
    device_id: str = Field(
        min_length=1,
        max_length=100,
        description="스캔 요청을 보낸 디바이스 식별자입니다. 예: display-01",
        examples=["display-01"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "triggered_by": "frontend",
                "device_id": "display-01",
            }
        }
    }


class LiquorScanStartResponse(BaseModel):
    status: Literal["accepted"] = Field(
        description="주류 스캔 요청이 정상적으로 접수되었음을 나타냅니다."
    )
    message: str = Field(description="주류 스캔 시작 처리 결과 메시지입니다.")
    scan_request_id: str = Field(description="이번 주류 스캔 요청을 식별하는 ID입니다.")


class IngredientScanStartRequest(LiquorScanStartRequest):
    pass


class IngredientScanStartResponse(BaseModel):
    status: Literal["accepted"]
    message: str
    scan_request_id: str
