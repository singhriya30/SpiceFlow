import uuid
from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.address import Address
from app.models.inventory import Inventory
from app.schemas.order import OrderCreate
from app.schemas.inventory import InventoryAdjust
from app.core.config import GST_RATE
from app.services.inventory_service import _apply_stock_adjustment

from app.models.user import User
from app.models.role import Role


def create_order(db: Session, customer_id: uuid.UUID, order_data: OrderCreate) -> Order:
    address = db.query(Address).filter(Address.id == order_data.shipping_address_id).first()
    if not address:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shipping address not found")
    if address.user_id != customer_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This address does not belong to you")

    requested_product_ids = [item.product_id for item in order_data.items]
    if len(requested_product_ids) != len(set(requested_product_ids)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duplicate product in order — each product can only appear once per order"
        )

    validated_items = []

    for item in order_data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {item.product_id} not found"
            )
        if product.status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product '{product.name}' is not currently available"
            )

        inventory = db.query(Inventory).filter(Inventory.product_id == product.id).first()
        if not inventory or inventory.quantity < item.quantity:
            available = inventory.quantity if inventory else 0
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for '{product.name}'. Available: {available}, requested: {item.quantity}"
            )

        validated_items.append({
            "product": product,
            "quantity": item.quantity,
            "unit_price": product.price
        })

    try:
        subtotal = sum(item["unit_price"] * item["quantity"] for item in validated_items)
        gst_amount = subtotal * Decimal(str(GST_RATE))
        total_amount = subtotal + gst_amount

        new_order = Order(
            customer_id=customer_id,
            status=OrderStatus.pending,
            shipping_label=address.label,
            shipping_address_line1=address.address_line1,
            shipping_address_line2=address.address_line2,
            shipping_city=address.city,
            shipping_state=address.state,
            shipping_pincode=address.pincode,
            subtotal=subtotal,
            gst_amount=gst_amount,
            total_amount=total_amount
        )
        db.add(new_order)
        db.flush()

        for item in validated_items:
            item_subtotal = item["unit_price"] * item["quantity"]

            order_item = OrderItem(
                order_id=new_order.id,
                product_id=item["product"].id,
                quantity=item["quantity"],
                unit_price=item["unit_price"],
                subtotal=item_subtotal
            )
            db.add(order_item)

            _apply_stock_adjustment(
                db,
                item["product"].id,
                InventoryAdjust(
                    quantity_change=-item["quantity"],
                    reason=f"Order {new_order.id}"
                )
            )

        db.commit()
        db.refresh(new_order)
        return new_order

    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create order due to an unexpected error"
        )


def get_order_by_id(db: Session, order_id: uuid.UUID) -> Order:
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


def get_order_for_customer(db: Session, order_id: uuid.UUID, customer_id: uuid.UUID) -> Order:
    order = get_order_by_id(db, order_id)
    if order.customer_id != customer_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This order does not belong to you")
    return order


def get_orders_for_customer(db: Session, customer_id: uuid.UUID) -> list[Order]:
    return db.query(Order).filter(Order.customer_id == customer_id).order_by(Order.created_at.desc()).all()


def get_all_orders(db: Session) -> list[Order]:
    return db.query(Order).order_by(Order.created_at.desc()).all()


VALID_TRANSITIONS = {
    OrderStatus.pending: [OrderStatus.confirmed, OrderStatus.cancelled],
    OrderStatus.confirmed: [OrderStatus.packed, OrderStatus.cancelled],
    OrderStatus.packed: [OrderStatus.shipped, OrderStatus.cancelled],
    OrderStatus.shipped: [OrderStatus.delivered],
    OrderStatus.delivered: [],
    OrderStatus.cancelled: [],
}


def update_order_status(db: Session, order_id: uuid.UUID, new_status: OrderStatus) -> Order:
    order = get_order_by_id(db, order_id)

    allowed_next_statuses = VALID_TRANSITIONS.get(order.status, [])
    if new_status not in allowed_next_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot change order status from '{order.status.value}' to '{new_status.value}'"
        )

    try:
        if new_status == OrderStatus.cancelled:
            for item in order.items:
                _apply_stock_adjustment(
                    db,
                    item.product_id,
                    InventoryAdjust(
                        quantity_change=item.quantity,
                        reason=f"Order {order.id} cancelled — stock restored"
                    )
                )

        order.status = new_status
        db.commit()
        db.refresh(order)
        return order

    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update order status due to an unexpected error"
        )


def assign_delivery(db: Session, order_id: uuid.UUID, delivery_employee_id: uuid.UUID) -> Order:
    order = get_order_by_id(db, order_id)

    if order.status not in [OrderStatus.packed, OrderStatus.shipped]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot assign delivery to an order with status '{order.status.value}'. Order must be packed or shipped."
        )

    delivery_user = (
        db.query(User)
        .join(Role, User.role_id == Role.id)
        .filter(User.id == delivery_employee_id, Role.role_name == "Delivery")
        .first()
    )
    if not delivery_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery employee not found or does not have the Delivery role"
        )
    if not delivery_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot assign an inactive delivery employee"
        )

    order.delivery_employee_id = delivery_employee_id
    db.commit()
    db.refresh(order)
    return order


def get_orders_for_delivery_employee(db: Session, delivery_employee_id: uuid.UUID) -> list[Order]:
    return (
        db.query(Order)
        .filter(Order.delivery_employee_id == delivery_employee_id)
        .order_by(Order.created_at.desc())
        .all()
    )


def mark_order_delivered(db: Session, order_id: uuid.UUID, delivery_employee_id: uuid.UUID) -> Order:
    order = get_order_by_id(db, order_id)

    if order.delivery_employee_id != delivery_employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This order is not assigned to you"
        )

    return update_order_status(db, order_id, OrderStatus.delivered)