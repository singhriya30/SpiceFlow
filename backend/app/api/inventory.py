import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.inventory import (
    InventoryResponse,
    InventoryAdjust,
    MinimumStockUpdate,
    InventoryHistoryResponse
)
from app.services.inventory_service import (
    get_inventory_by_product_id,
    adjust_stock,
    update_minimum_stock,
    get_inventory_history,
    get_low_stock_products
)
from app.core.dependencies import require_role
from app.models.user import User

router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"]
)


@router.get("/low-stock", response_model=list[InventoryResponse])
def low_stock_alert(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Owner", "Employee"))
):
    return get_low_stock_products(db)


@router.get("/{product_id}", response_model=InventoryResponse)
def get_product_inventory(
    product_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Owner", "Employee"))
):
    return get_inventory_by_product_id(db, product_id)


@router.post("/{product_id}/adjust", response_model=InventoryResponse)
def adjust_product_stock(
    product_id: uuid.UUID,
    adjustment: InventoryAdjust,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Owner", "Employee"))
):
    return adjust_stock(db, product_id, adjustment)


@router.put("/{product_id}/minimum-stock", response_model=InventoryResponse)
def set_minimum_stock(
    product_id: uuid.UUID,
    data: MinimumStockUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Owner"))
):
    return update_minimum_stock(db, product_id, data)


@router.get("/{product_id}/history", response_model=list[InventoryHistoryResponse])
def get_product_inventory_history(
    product_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Owner", "Employee"))
):
    return get_inventory_history(db, product_id)