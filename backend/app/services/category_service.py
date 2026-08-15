import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.category import Category
from app.schemas.category import CategoryCreate


from app.schemas.category import CategoryUpdate


from sqlalchemy.exc import IntegrityError

def create_category(db: Session, category_data: CategoryCreate) -> Category:
    existing = db.query(Category).filter(Category.category_name == category_data.category_name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category already exists"
        )

    new_category = Category(**category_data.model_dump())
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category


def get_all_categories(db: Session) -> list[Category]:
    return db.query(Category).all()


def get_category_by_id(db: Session, category_id: uuid.UUID) -> Category:
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category



def update_category(db: Session, category_id: uuid.UUID, category_data: CategoryUpdate) -> Category:
    category = get_category_by_id(db, category_id)

    update_data = category_data.model_dump(exclude_unset=True)

    if "category_name" in update_data:
        existing = db.query(Category).filter(
            Category.category_name == update_data["category_name"],
            Category.id != category_id
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category name already exists"
            )

    for field, value in update_data.items():
        setattr(category, field, value)

    db.commit()
    db.refresh(category)
    return category




def delete_category(db: Session, category_id: uuid.UUID) -> None:
    category = get_category_by_id(db, category_id)

    try:
        db.delete(category)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete category — one or more products still belong to it"
        )