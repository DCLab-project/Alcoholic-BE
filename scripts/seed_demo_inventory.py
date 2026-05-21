from app.db import Base, SessionLocal, engine
from app.domain.models import InventoryItem


DEMO_INVENTORY_COUNTS = {
    "beef": 4,
    "bread": 4,
    "broccoli": 4,
    "butter": 2,
    "cabbage": 3,
    "carrot": 3,
    "cheese": 4,
    "chicken": 4,
    "cucumber": 3,
    "egg": 8,
    "eggplant": 3,
    "fish": 3,
    "garlic": 5,
    "green_onion": 4,
    "lettuce": 3,
    "milk": 2,
    "mushroom": 4,
    "onion": 5,
    "pepper": 3,
    "pork": 4,
    "potato": 5,
    "sausage": 4,
    "tomato": 5,
    "zucchini": 3,
    "lemon": 3,
    "avocado": 2,
    "radish": 2,
    "tofu": 3,
    "ginger": 2,
    "salmon": 2,
}


def seed_demo_inventory() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        existing_items = {
            item.item_name: item for item in db.query(InventoryItem).all()
        }

        for item_name, count in DEMO_INVENTORY_COUNTS.items():
            item = existing_items.get(item_name)
            if item is None:
                db.add(InventoryItem(item_name=item_name, count=count))
            else:
                item.count = count

        db.commit()
        print(f"demo inventory seeded: {len(DEMO_INVENTORY_COUNTS)} items")
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_inventory()
