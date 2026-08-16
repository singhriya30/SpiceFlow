import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.address import Address
from app.schemas.address import AddressCreate, AddressUpdate


def create_address(db: Session, user_id: uuid.UUID, address_data: AddressCreate) -> Address:
    if address_data.is_default:
        db.query(Address).filter(
            Address.user_id == user_id,
            Address.is_default == True
        ).update({"is_default": False})

    new_address = Address(user_id=user_id, **address_data.model_dump())
    db.add(new_address)
    db.commit()
    db.refresh(new_address)
    return new_address


def get_addresses_for_user(db: Session, user_id: uuid.UUID) -> list[Address]:
    return db.query(Address).filter(Address.user_id == user_id).all()


def get_address_by_id(db: Session, address_id: uuid.UUID) -> Address:
    address = db.query(Address).filter(Address.id == address_id).first()
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )
    return address

def get_address_for_user(db: Session, address_id: uuid.UUID, user_id: uuid.UUID) -> Address:
    address = get_address_by_id(db, address_id)

    if address.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this address"
        )

    return address


def update_address(db: Session, address_id: uuid.UUID, user_id: uuid.UUID, address_data: AddressUpdate) -> Address:
    address = get_address_by_id(db, address_id)

    if address.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this address"
        )

    update_data = address_data.model_dump(exclude_unset=True)

    if update_data.get("is_default") is True:
        db.query(Address).filter(
            Address.user_id == user_id,
            Address.is_default == True,
            Address.id != address_id
        ).update({"is_default": False})

    for field, value in update_data.items():
        setattr(address, field, value)

    db.commit()
    db.refresh(address)
    return address


def delete_address(db: Session, address_id: uuid.UUID, user_id: uuid.UUID) -> None:
    address = get_address_by_id(db, address_id)

    if address.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this address"
        )

    db.delete(address)
    db.commit()