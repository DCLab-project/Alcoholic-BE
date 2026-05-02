from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.repositories.inventory_repository import InventoryRepository
from app.schemas.inventory import (
    InventoryBulkCreate,
    InventoryBulkResponse,
    InventoryCreateRequest,
    InventoryDeleteResponse,
    InventoryListResponse,
    InventoryMutationResponse,
    InventoryQuantityPatchRequest,
    InventoryQuantityPatchResponse,
    InventoryUpdateRequest,
)
from app.services.inventory_service import InventoryService

router = APIRouter(prefix="/api/v1/inventory", tags=["재고 관리"])


@router.get(
    "",
    response_model=InventoryListResponse,
    summary="전체 식재료 재고 조회",
    description="현재 DB에 저장된 모든 식재료 목록과 각 수량, 마지막 갱신 시각을 조회합니다.",
    response_description="현재 저장된 전체 식재료 재고 목록을 반환합니다.",
)
def get_inventory(db: Session = Depends(get_db)) -> InventoryListResponse:
    repository = InventoryRepository(db)
    service = InventoryService(db, repository)
    return service.list_inventory()


@router.post(
    "/bulk",
    response_model=InventoryBulkResponse,
    status_code=201,
    summary="인식된 식재료 목록 일괄 저장",
    description=(
        "프론트 화면에 임시로 쌓여 있던 식재료 배열을 한 번에 재고 DB에 반영합니다. "
        "한글명과 내부 key를 모두 받을 수 있으며, "
        "같은 식재료 이름이 여러 번 들어오면 수량을 합산해 저장합니다."
    ),
    response_description="일괄 저장 결과와 저장된 총 항목 수를 반환합니다.",
)
def bulk_save_inventory(
    payload: InventoryBulkCreate,
    db: Session = Depends(get_db),
) -> InventoryBulkResponse:
    repository = InventoryRepository(db)
    service = InventoryService(db, repository)
    return service.bulk_save_inventory(payload)


@router.post(
    "",
    response_model=InventoryMutationResponse,
    status_code=201,
    summary="식재료 직접 추가",
    description="사용자가 식재료 이름과 수량을 직접 입력해 DB에 추가합니다.",
)
def add_inventory_item(
    payload: InventoryCreateRequest,
    db: Session = Depends(get_db),
) -> InventoryMutationResponse:
    repository = InventoryRepository(db)
    service = InventoryService(db, repository)
    return service.add_inventory_item(payload)


@router.patch(
    "/quantity",
    response_model=InventoryQuantityPatchResponse,
    summary="식재료 수량 수동 조절",
    description=(
        "사용자가 + 또는 - 버튼을 눌렀을 때 특정 식재료의 현재 재고 수량을 수동으로 반영합니다. "
        "식재료 이름은 한글명과 내부 key를 모두 받을 수 있습니다."
    ),
    response_description="수량 조정 후 현재 식재료 수량을 반환합니다.",
)
def patch_inventory_quantity(
    payload: InventoryQuantityPatchRequest,
    db: Session = Depends(get_db),
) -> InventoryQuantityPatchResponse:
    repository = InventoryRepository(db)
    service = InventoryService(db, repository)
    return service.patch_inventory_quantity(payload)


@router.patch(
    "/{ingredient_name}",
    response_model=InventoryMutationResponse,
    summary="식재료 이름/수량 직접 수정",
    description="사용자가 식재료 이름 또는 수량을 직접 수정합니다.",
)
def update_inventory_item(
    ingredient_name: str,
    payload: InventoryUpdateRequest,
    db: Session = Depends(get_db),
) -> InventoryMutationResponse:
    repository = InventoryRepository(db)
    service = InventoryService(db, repository)
    return service.update_inventory_item(ingredient_name, payload)


@router.delete(
    "/{ingredient_name}",
    response_model=InventoryDeleteResponse,
    summary="식재료 삭제",
    description="사용자가 식재료를 DB에서 삭제합니다.",
)
def delete_inventory_item(
    ingredient_name: str,
    db: Session = Depends(get_db),
) -> InventoryDeleteResponse:
    repository = InventoryRepository(db)
    service = InventoryService(db, repository)
    return service.delete_inventory_item(ingredient_name)
