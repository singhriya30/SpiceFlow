import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.product import Product
from app.models.category import Category
from app.schemas.product import ProductCreate


def create_product(db: Session, product_data: ProductCreate) -> Product:
    category = db.query(Category).filter(Category.id == product_data.category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    existing_sku = db.query(Product).filter(Product.sku == product_data.sku).first()
    if existing_sku:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SKU already exists"
        )

    new_product = Product(**product_data.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


def get_all_products(db: Session) -> list[Product]:
    return db.query(Product).all()


def get_product_by_id(db: Session, product_id: uuid.UUID) -> Product:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product

from app.schemas.product import ProductUpdate


def update_product(
    db: Session,
    product_id: uuid.UUID,
    product_data: ProductUpdate
) -> Product:

    product = get_product_by_id(db, product_id)

    update_data = product_data.model_dump(exclude_unset=True)

    if "category_id" in update_data:
        category = db.query(Category).filter(
            Category.id == update_data["category_id"]
        ).first()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )

    if "sku" in update_data:
        existing_sku = db.query(Product).filter(
            Product.sku == update_data["sku"],
            Product.id != product_id
        ).first()

        if existing_sku:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="SKU already exists"
            )

    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)

    return product


def delete_product(db: Session, product_id: uuid.UUID) -> None:
    product = get_product_by_id(db, product_id)
    db.delete(product)
    db.commit()