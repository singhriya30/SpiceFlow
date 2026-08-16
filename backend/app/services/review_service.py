import uuid
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.models.review import Review
from app.models.product import Product
from app.schemas.review import ReviewCreate

from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem

def has_purchased_product(db: Session, customer_id: uuid.UUID, product_id: uuid.UUID) -> bool:
    purchase = (
        db.query(OrderItem)
        .join(Order, OrderItem.order_id == Order.id)
        .filter(
            Order.customer_id == customer_id,
            Order.status == OrderStatus.delivered,
            OrderItem.product_id == product_id
        )
        .first()
    )
    return purchase is not None


def create_review(db: Session, customer_id: uuid.UUID, review_data: ReviewCreate) -> Review:
    product = db.query(Product).filter(Product.id == review_data.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    if not has_purchased_product(db, customer_id, review_data.product_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only review products you have purchased"
        )

    new_review = Review(customer_id=customer_id, **review_data.model_dump())
    db.add(new_review)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reviewed this product"
        )

    db.refresh(new_review)
    return new_review


def get_reviews_for_product(db: Session, product_id: uuid.UUID) -> list[Review]:
    return db.query(Review).filter(Review.product_id == product_id).all()


def delete_review(db: Session, review_id: uuid.UUID, customer_id: uuid.UUID) -> None:
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    if review.customer_id != customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this review"
        )
    db.delete(review)
    db.commit()