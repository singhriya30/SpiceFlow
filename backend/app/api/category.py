import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.category import CategoryCreate, CategoryResponse
from app.services.category_service import create_category, get_all_categories, get_category_by_id
from app.core.dependencies import require_role
from app.models.user import User

from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.services.category_service import (
    create_category,
    get_all_categories,
    get_category_by_id,
    update_category,
    delete_category
)

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def add_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Owner"))
):
    return create_category(db, category_data)


@router.get("/", response_model=list[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    return get_all_categories(db)


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: uuid.UUID, db: Session = Depends(get_db)):
    return get_category_by_id(db, category_id)

@router.put("/{category_id}", response_model=CategoryResponse)
def edit_category(
    category_id: uuid.UUID,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Owner"))
):
    return update_category(db, category_id, category_data)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_category(
    category_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Owner"))
):
    delete_category(db, category_id)