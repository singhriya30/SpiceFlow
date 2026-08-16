import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.review import ReviewCreate, ReviewResponse
from app.services.review_service import create_review, get_reviews_for_product, delete_review
from app.core.dependencies import get_current_user, require_role
from app.models.user import User

router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"]
)


@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def add_review(
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Customer"))
):
    return create_review(db, current_user.id, review_data)


@router.get("/product/{product_id}", response_model=list[ReviewResponse])
def list_product_reviews(product_id: uuid.UUID, db: Session = Depends(get_db)):
    return get_reviews_for_product(db, product_id)


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_review(
    review_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    delete_review(db, review_id, current_user.id)