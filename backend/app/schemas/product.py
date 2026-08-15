import uuid
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field

from app.models.product import ProductStatus


class ProductCreate(BaseModel):
    category_id: uuid.UUID
    sku: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    weight: str = Field(..., min_length=1, max_length=50)
    price: Decimal = Field(..., gt=0)
    image_url: Optional[str] = None
    status: ProductStatus = ProductStatus.active


class ProductResponse(BaseModel):
    id: uuid.UUID
    category_id: uuid.UUID
    sku: str
    name: str
    description: Optional[str] = None
    weight: str
    price: Decimal
    image_url: Optional[str] = None
    status: ProductStatus

    class Config:
        from_attributes = True
    
class ProductUpdate(BaseModel):
    category_id: Optional[uuid.UUID] = None
    sku: Optional[str] = Field(None, min_length=1, max_length=50)
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    weight: Optional[str] = Field(None, min_length=1, max_length=50)
    price: Optional[Decimal] = Field(None, gt=0)
    image_url: Optional[str] = None
    status: Optional[ProductStatus] = None