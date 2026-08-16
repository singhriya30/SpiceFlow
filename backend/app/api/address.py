import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.address import AddressCreate, AddressUpdate, AddressResponse
from app.services.address_service import (
    create_address,
    get_addresses_for_user,
    get_address_for_user,
    update_address,
    delete_address
)

from app.core.dependencies import get_current_user, require_role
from app.models.user import User

router = APIRouter(
    prefix="/addresses",
    tags=["Addresses"]
)


@router.post("/", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
def add_address(
    address_data: AddressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_address(db, current_user.id, address_data)


@router.get("/", response_model=list[AddressResponse])
def list_my_addresses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_addresses_for_user(db, current_user.id)


@router.get("/{address_id}", response_model=AddressResponse)
def get_address(
    address_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_address_for_user(db, address_id, current_user.id)


@router.put("/{address_id}", response_model=AddressResponse)
def edit_address(
    address_id: uuid.UUID,
    address_data: AddressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return update_address(db, address_id, current_user.id, address_data)


@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_address(
    address_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    delete_address(db, address_id, current_user.id)


@router.get("/user/{user_id}", response_model=list[AddressResponse])
def list_customer_addresses(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Owner", "Employee"))
):
    return get_addresses_for_user(db, user_id)