from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class InventoryItemData(BaseModel):
    ingredient_name: str = Field(description="사용자에게 보여줄 식재료 한글 이름입니다.")
    quantity: int = Field(description="현재 저장된 식재료 수량입니다.")
    last_updated: datetime | None = Field(
        default=None,
        description="해당 식재료 재고가 마지막으로 갱신된 시각입니다.",
    )


class InventoryListResponse(BaseModel):
    status: Literal["success"] = Field(description="요청 처리 결과 상태입니다.")
    data: list[InventoryItemData] = Field(description="현재 저장된 전체 식재료 재고 목록입니다.")


class InventoryBulkCreate(BaseModel):
    items: list[str] = Field(
        min_length=1,
        max_length=30,
        description="최종 저장할 식재료 이름 배열입니다. 1개부터 30개까지 받을 수 있고, 한글명과 내부 key를 모두 허용하며, 같은 이름이 여러 번 들어오면 수량이 그만큼 증가합니다.",
        examples=[["대파", "green_onion", "양파"]],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "items": ["대파", "대파", "green_onion", "양파"]
            }
        }
    }


class InventoryBulkResponse(BaseModel):
    status: Literal["success"] = Field(description="요청 처리 결과 상태입니다.")
    message: str = Field(description="일괄 저장 처리 결과를 설명하는 메시지입니다.")
    saved_count: int = Field(description="배열 기준으로 저장 처리된 총 식재료 항목 수입니다.")


class InventoryCreateRequest(BaseModel):
    ingredient_name: str = Field(min_length=1, max_length=100)
    quantity: int = Field(default=1, ge=0)


class InventoryUpdateRequest(BaseModel):
    new_ingredient_name: str | None = Field(default=None, min_length=1, max_length=100)
    quantity: int | None = Field(default=None, ge=0)


class InventoryMutationResponse(BaseModel):
    status: Literal["success"]
    message: str
    ingredient_name: str
    current_quantity: int


class InventoryDeleteResponse(BaseModel):
    status: Literal["success"]
    message: str


class InventoryQuantityPatchRequest(BaseModel):
    ingredient_name: str = Field(
        min_length=1,
        max_length=100,
        description="수량을 조절할 식재료 이름입니다. 한글명과 내부 key를 모두 허용합니다.",
        examples=["대파"],
    )
    action: Literal["add", "subtract"] = Field(
        description="수량 조절 방식입니다. add는 +1, subtract는 -1을 의미합니다.",
        examples=["add"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "ingredient_name": "대파",
                "action": "add",
            }
        }
    }


class InventoryQuantityPatchResponse(BaseModel):
    status: Literal["success"] = Field(description="요청 처리 결과 상태입니다.")
    ingredient_name: str = Field(description="수량이 조정된 식재료 이름입니다.")
    current_quantity: int = Field(description="수량 조정 후 현재 재고 수량입니다.")
