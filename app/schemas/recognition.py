from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


class IngredientLiveRecognitionCreate(BaseModel):
    ingredient_name: str = Field(
        min_length=1,
        max_length=100,
        description="인식된 식재료의 영문 표준 이름입니다. 예: green_onion, onion, tomato",
        examples=["green_onion"],
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

    model_config = {
        "json_schema_extra": {
            "example": {
                "ingredient_name": "green_onion",
                "timestamp": "2026-04-10T17:16:01Z",
                "confidence": 0.93,
                "source": "ingredient_classifier",
            }
        }
    }


class IngredientStreamEvent(BaseModel):
    ingredient_name: str = Field(description="실시간으로 감지된 식재료 이름입니다.")
    timestamp: datetime = Field(description="해당 식재료 이벤트가 발생한 시각입니다.")


class LiquorLiveRecognitionCreate(BaseModel):
    liquor_name: str = Field(
        min_length=1,
        max_length=100,
        description="인식된 주류의 영문 표준 이름입니다. 예: soju, beer, whiskey",
        examples=["soju"],
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

    model_config = {
        "json_schema_extra": {
            "example": {
                "liquor_name": "soju",
                "timestamp": "2026-04-10T17:20:00Z",
                "confidence": 0.97,
                "source": "liquor_classifier",
            }
        }
    }


class LiquorStreamEvent(BaseModel):
    liquor_name: str = Field(description="실시간으로 감지된 주류 이름입니다.")
    timestamp: datetime = Field(description="해당 주류 이벤트가 발생한 시각입니다.")


class LiveRecognitionAcceptedResponse(BaseModel):
    status: Literal["success"] = Field(description="요청 처리 결과 상태입니다.")
    message: str = Field(description="처리 결과를 설명하는 메시지입니다.")
