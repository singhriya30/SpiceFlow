import uuid
from typing import Optional
from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    category_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class CategoryResponse(BaseModel):
    id: uuid.UUID
    category_name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class CategoryUpdate(BaseModel):
    category_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None