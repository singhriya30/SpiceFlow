from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.order import Order, OrderStatus

from app.models.order_item import OrderItem
from app.models.product import Product

from app.models.category import Category

from sqlalchemy import cast, Date

from app.models.user import User as UserModel
from app.models.role import Role

def get_summary(db: Session) -> dict:
    total_revenue = (
        db.query(func.coalesce(func.sum(Order.total_amount), 0))
        .filter(Order.status == OrderStatus.delivered)
        .scalar()
    )

    total_orders = db.query(func.count(Order.id)).scalar()

    orders_by_status = (
        db.query(Order.status, func.count(Order.id))
        .group_by(Order.status)
        .all()
    )

    status_breakdown = {status.value: 0 for status in OrderStatus}
    for status_value, count in orders_by_status:
        status_breakdown[status_value.value] = count

    return {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "orders_by_status": status_breakdown
    }



def get_top_products(db: Session, limit: int = 10) -> list[dict]:
    results = (
        db.query(
            Product.id,
            Product.name,
            func.sum(OrderItem.quantity).label("total_quantity_sold"),
            func.sum(OrderItem.subtotal).label("total_revenue")
        )
        .join(OrderItem, OrderItem.product_id == Product.id)
        .join(Order, OrderItem.order_id == Order.id)
        .filter(Order.status == OrderStatus.delivered)
        .group_by(Product.id, Product.name)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "product_id": row.id,
            "product_name": row.name,
            "total_quantity_sold": row.total_quantity_sold,
            "total_revenue": row.total_revenue
        }
        for row in results
    ]



def get_top_categories(db: Session, limit: int = 10) -> list[dict]:
    results = (
        db.query(
            Category.id,
            Category.category_name,
            func.sum(OrderItem.quantity).label("total_quantity_sold"),
            func.sum(OrderItem.subtotal).label("total_revenue")
        )
        .join(Product, Product.category_id == Category.id)
        .join(OrderItem, OrderItem.product_id == Product.id)
        .join(Order, OrderItem.order_id == Order.id)
        .filter(Order.status == OrderStatus.delivered)
        .group_by(Category.id, Category.category_name)
        .order_by(func.sum(OrderItem.subtotal).desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "category_id": row.id,
            "category_name": row.category_name,
            "total_quantity_sold": row.total_quantity_sold,
            "total_revenue": row.total_revenue
        }
        for row in results
    ]



def get_sales_over_time(db: Session) -> list[dict]:
    results = (
        db.query(
            cast(Order.created_at, Date).label("order_date"),
            func.count(Order.id).label("order_count"),
            func.sum(Order.total_amount).label("revenue")
        )
        .filter(Order.status == OrderStatus.delivered)
        .group_by(cast(Order.created_at, Date))
        .order_by(cast(Order.created_at, Date).asc())
        .all()
    )

    return [
        {
            "date": row.order_date,
            "order_count": row.order_count,
            "revenue": row.revenue
        }
        for row in results
    ]



def get_customer_stats(db: Session, limit: int = 10) -> dict:
    total_customers = (
        db.query(func.count(UserModel.id))
        .join(Role, UserModel.role_id == Role.id)
        .filter(Role.role_name == "Customer")
        .scalar()
    )

    top_customers_results = (
        db.query(
            UserModel.id,
            UserModel.first_name,
            UserModel.last_name,
            func.sum(Order.total_amount).label("total_spent"),
            func.count(Order.id).label("order_count")
        )
        .join(Order, Order.customer_id == UserModel.id)
        .filter(Order.status == OrderStatus.delivered)
        .group_by(UserModel.id, UserModel.first_name, UserModel.last_name)
        .order_by(func.sum(Order.total_amount).desc())
        .limit(limit)
        .all()
    )

    top_customers = [
        {
            "customer_id": row.id,
            "customer_name": f"{row.first_name} {row.last_name}",
            "total_spent": row.total_spent,
            "order_count": row.order_count
        }
        for row in top_customers_results
    ]

    return {
        "total_customers": total_customers,
        "top_customers": top_customers
    }