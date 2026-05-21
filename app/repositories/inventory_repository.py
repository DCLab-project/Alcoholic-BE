from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.models import InventoryEvent, InventoryItem


class InventoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_inventory_item(self, item_name: str) -> InventoryItem | None:
        stmt = select(InventoryItem).where(InventoryItem.item_name == item_name)
        return self.db.scalar(stmt)

    def list_inventory_items(self) -> list[InventoryItem]:
        stmt = select(InventoryItem).order_by(InventoryItem.item_name.asc())
        return list(self.db.scalars(stmt).all())

    def upsert_inventory_count(self, item_name: str, delta: int) -> InventoryItem:
        item = self.get_inventory_item(item_name)
        if item is None:
            item = InventoryItem(item_name=item_name, count=max(delta, 0))
            self.db.add(item)
            self.db.flush()
            return item

        item.count = max(item.count + delta, 0)
        self.db.flush()
        return item

    def set_inventory_count(self, item_name: str, quantity: int) -> InventoryItem:
        item = self.get_inventory_item(item_name)
        if item is None:
            item = InventoryItem(item_name=item_name, count=max(quantity, 0))
            self.db.add(item)
            self.db.flush()
            return item

        item.count = max(quantity, 0)
        self.db.flush()
        return item

    def delete_inventory_item(self, item_name: str) -> bool:
        item = self.get_inventory_item(item_name)
        if item is None:
            return False

        self.db.delete(item)
        self.db.flush()
        return True

    def create_event(
        self,
        *,
        item_name: str,
        event_type: str,
        quantity: int,
        confidence: float,
        source: str,
        detected_at,
    ) -> InventoryEvent:
        event = InventoryEvent(
            item_name=item_name,
            event_type=event_type,
            quantity=quantity,
            confidence=confidence,
            source=source,
            detected_at=detected_at,
        )
        self.db.add(event)
        self.db.flush()
        return event

