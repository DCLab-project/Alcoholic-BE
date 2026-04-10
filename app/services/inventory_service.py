from collections import Counter

from sqlalchemy.orm import Session

from app.repositories.inventory_repository import InventoryRepository
from app.schemas.inventory import (
    InventoryBulkCreate,
    InventoryBulkResponse,
    InventoryItemData,
    InventoryListResponse,
    InventoryQuantityPatchRequest,
    InventoryQuantityPatchResponse,
)


class InventoryService:
    def __init__(self, db: Session, repository: InventoryRepository):
        self.db = db
        self.repository = repository

    def list_inventory(self) -> InventoryListResponse:
        items = self.repository.list_inventory_items()
        return InventoryListResponse(
            status="success",
            data=[
                InventoryItemData(
                    ingredient_name=item.item_name,
                    quantity=item.count,
                    last_updated=item.updated_at,
                )
                for item in items
            ]
        )

    def bulk_save_inventory(self, payload: InventoryBulkCreate) -> InventoryBulkResponse:
        normalized_items = [item.strip() for item in payload.items if item.strip()]
        grouped_items = Counter(normalized_items)

        for ingredient_name, quantity in grouped_items.items():
            inventory_item = self.repository.upsert_inventory_count(ingredient_name, quantity)
            self.repository.create_event(
                item_name=ingredient_name,
                event_type="bulk_save",
                quantity=quantity,
                confidence=1.0,
                source="frontend_bulk_save",
                detected_at=inventory_item.updated_at,
            )

        self.db.commit()
        return InventoryBulkResponse(
            status="success",
            message="Inventory items saved successfully.",
            saved_count=len(normalized_items),
        )

    def patch_inventory_quantity(
        self, payload: InventoryQuantityPatchRequest
    ) -> InventoryQuantityPatchResponse:
        delta = 1 if payload.action == "add" else -1
        inventory_item = self.repository.upsert_inventory_count(payload.ingredient_name, delta)
        self.repository.create_event(
            item_name=payload.ingredient_name,
            event_type=payload.action,
            quantity=1,
            confidence=1.0,
            source="manual_quantity_patch",
            detected_at=inventory_item.updated_at,
        )
        self.db.commit()
        self.db.refresh(inventory_item)

        return InventoryQuantityPatchResponse(
            status="success",
            ingredient_name=payload.ingredient_name,
            current_quantity=inventory_item.count,
        )
