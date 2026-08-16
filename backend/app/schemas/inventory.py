import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class InventoryResponse(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    quantity: int
    minimum_stock: int
    updated_at: datetime

    class Config:
        from_attributes = True


class InventoryAdjust(BaseModel):
    quantity_change: int
    reason: str = Field(..., min_length=1, max_length=255)


class MinimumStockUpdate(BaseModel):
    minimum_stock: int = Field(..., ge=0)


class InventoryHistoryResponse(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    quantity_change: int
    reason: str
    created_at: datetime

    class Config:
        from_attributes = True