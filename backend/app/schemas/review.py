import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ReviewCreate(BaseModel):
    product_id: uuid.UUID
    rating: int = Field(..., ge=1, le=5)
    review_text: Optional[str] = None


class ReviewResponse(BaseModel):
    id: uuid.UUID
    customer_id: uuid.UUID
    product_id: uuid.UUID
    rating: int
    review_text: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True