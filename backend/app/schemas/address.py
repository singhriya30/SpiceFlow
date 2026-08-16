import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class AddressCreate(BaseModel):
    label: str = Field(..., min_length=1, max_length=50)
    address_line1: str = Field(..., min_length=1, max_length=255)
    address_line2: Optional[str] = None
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=100)
    pincode: str = Field(..., min_length=6, max_length=10)
    is_default: bool = False


class AddressUpdate(BaseModel):
    label: Optional[str] = Field(None, min_length=1, max_length=50)
    address_line1: Optional[str] = Field(None, min_length=1, max_length=255)
    address_line2: Optional[str] = None
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    state: Optional[str] = Field(None, min_length=1, max_length=100)
    pincode: Optional[str] = Field(None, min_length=6, max_length=10)
    is_default: Optional[bool] = None


class AddressResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    label: str
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    pincode: str
    is_default: bool
    created_at: datetime

    class Config:
        from_attributes = True