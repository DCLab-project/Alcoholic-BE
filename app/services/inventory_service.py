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
from app.services.name_mapping import ingredient_display_name, normalize_ingredient_key


class InventoryService:
    def __init__(self, db: Session, repository: InventoryRepository):
        self.db = db
        self.repository = repository

    @staticmethod
    def _group_inventory_items(items) -> dict[str, dict]:
        grouped_items: dict[str, dict] = {}
        for item in items:
            ingredient_key = normalize_ingredient_key(item.item_name)
            if not ingredient_key:
                continue

            grouped_item = grouped_items.setdefault(
                ingredient_key,
                {
                    "quantity": 0,
                    "last_updated": item.updated_at,
                },
            )
            grouped_item["quantity"] += item.count
            if (
                item.updated_at
                and (
                    grouped_item["last_updated"] is None
                    or item.updated_at > grouped_item["last_updated"]
                )
            ):
                grouped_item["last_updated"] = item.updated_at

        return grouped_items

    def list_inventory(self) -> InventoryListResponse:
        grouped_items = self._group_inventory_items(
            self.repository.list_inventory_items()
        )
        return InventoryListResponse(
            status="success",
            data=[
                InventoryItemData(
                    ingredient_name=ingredient_display_name(ingredient_key),
                    quantity=item["quantity"],
                    last_updated=item["last_updated"],
                )
                for ingredient_key, item in sorted(
                    grouped_items.items(),
                    key=lambda grouped_item: ingredient_display_name(grouped_item[0]),
                )
            ]
        )

    def bulk_save_inventory(self, payload: InventoryBulkCreate) -> InventoryBulkResponse:
        normalized_items = [
            normalize_ingredient_key(item)
            for item in payload.items
            if item.strip()
        ]
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
            message="보관함에 저장되었습니다.",
            saved_count=len(normalized_items),
        )

    def patch_inventory_quantity(
        self, payload: InventoryQuantityPatchRequest
    ) -> InventoryQuantityPatchResponse:
        delta = 1 if payload.action == "add" else -1
        ingredient_name = normalize_ingredient_key(payload.ingredient_name)
        inventory_item = self.repository.upsert_inventory_count(ingredient_name, delta)
        self.repository.create_event(
            item_name=ingredient_name,
            event_type=payload.action,
            quantity=1,
            confidence=1.0,
            source="manual_quantity_patch",
            detected_at=inventory_item.updated_at,
        )
        self.db.commit()
        self.db.refresh(inventory_item)
        current_quantity = sum(
            item.count
            for item in self.repository.list_inventory_items()
            if normalize_ingredient_key(item.item_name) == ingredient_name
        )

        return InventoryQuantityPatchResponse(
            status="success",
            ingredient_name=ingredient_display_name(ingredient_name),
            current_quantity=current_quantity,
        )
