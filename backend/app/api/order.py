import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.order import OrderCreate, OrderResponse, OrderStatusUpdate
from app.services.order_service import (
    create_order,
    get_order_for_customer,
    get_orders_for_customer,
    get_all_orders,
    get_order_by_id,
    update_order_status
)
from app.core.dependencies import get_current_user, require_role
from app.models.user import User

from app.schemas.order import DeliveryAssignment
from app.services.order_service import (
    assign_delivery,
    get_orders_for_delivery_employee,
    mark_order_delivered
)


router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def place_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Customer"))
):
    return create_order(db, current_user.id, order_data)


@router.get("/", response_model=list[OrderResponse])
def list_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Customer"))
):
    return get_orders_for_customer(db, current_user.id)


@router.get("/all", response_model=list[OrderResponse])
def list_all_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Owner", "Employee"))
):
    return get_all_orders(db)


@router.get("/my-deliveries", response_model=list[OrderResponse])
def list_my_deliveries(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Delivery"))
):
    return get_orders_for_delivery_employee(db, current_user.id)



@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.role_name == "Customer":
        return get_order_for_customer(db, order_id, current_user.id)
    return get_order_by_id(db, order_id)


@router.put("/{order_id}/status", response_model=OrderResponse)
def change_order_status(
    order_id: uuid.UUID,
    status_data: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Owner", "Employee"))
):
    return update_order_status(db, order_id, status_data.status)



@router.put("/{order_id}/assign-delivery", response_model=OrderResponse)
def assign_order_delivery(
    order_id: uuid.UUID,
    assignment: DeliveryAssignment,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Owner"))
):
    return assign_delivery(db, order_id, assignment.delivery_employee_id)




@router.put("/{order_id}/mark-delivered", response_model=OrderResponse)
def deliver_order(
    order_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Delivery"))
):
    return mark_order_delivered(db, order_id, current_user.id)