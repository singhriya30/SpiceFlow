import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.inventory import Inventory
from app.models.inventory_history import InventoryHistory
from app.models.product import Product
from app.schemas.inventory import InventoryAdjust, MinimumStockUpdate


def get_inventory_by_product_id(db: Session, product_id: uuid.UUID) -> Inventory:
    inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory record not found for this product"
        )
    return inventory


def create_inventory_for_product(db: Session, product_id: uuid.UUID) -> Inventory:
    new_inventory = Inventory(product_id=product_id, quantity=0, minimum_stock=0)
    db.add(new_inventory)
    db.commit()
    db.refresh(new_inventory)
    return new_inventory


def _apply_stock_adjustment(db: Session, product_id: uuid.UUID, adjustment: InventoryAdjust) -> Inventory:
    inventory = get_inventory_by_product_id(db, product_id)

    new_quantity = inventory.quantity + adjustment.quantity_change
    if new_quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reduce stock below zero. Current quantity: {inventory.quantity}"
        )

    inventory.quantity = new_quantity

    history_entry = InventoryHistory(
        product_id=product_id,
        quantity_change=adjustment.quantity_change,
        reason=adjustment.reason
    )
    db.add(history_entry)

    return inventory


def adjust_stock(db: Session, product_id: uuid.UUID, adjustment: InventoryAdjust) -> Inventory:
    inventory = _apply_stock_adjustment(db, product_id, adjustment)
    db.commit()
    db.refresh(inventory)
    return inventory

def update_minimum_stock(db: Session, product_id: uuid.UUID, data: MinimumStockUpdate) -> Inventory:
    inventory = get_inventory_by_product_id(db, product_id)
    inventory.minimum_stock = data.minimum_stock
    db.commit()
    db.refresh(inventory)
    return inventory


def get_inventory_history(db: Session, product_id: uuid.UUID) -> list[InventoryHistory]:
    return db.query(InventoryHistory).filter(
        InventoryHistory.product_id == product_id
    ).order_by(InventoryHistory.created_at.desc()).all()


def get_low_stock_products(db: Session) -> list[Inventory]:
    return db.query(Inventory).filter(Inventory.quantity <= Inventory.minimum_stock).all()