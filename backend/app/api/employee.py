import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse
from app.services.employee_service import (
    create_employee,
    get_employees,
    get_employee_by_id,
    update_employee,
    set_employee_active_status
)
from app.core.dependencies import require_role
from app.models.user import User

router = APIRouter(
    prefix="/employees",
    tags=["Employees"]
)


@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def add_employee(
    employee_data: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Owner"))
):
    return create_employee(db, employee_data)


@router.get("/", response_model=list[EmployeeResponse])
def list_employees(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Owner"))
):
    return get_employees(db)


@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(
    employee_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Owner"))
):
    return get_employee_by_id(db, employee_id)


@router.put("/{employee_id}", response_model=EmployeeResponse)
def edit_employee(
    employee_id: uuid.UUID,
    update_data: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Owner"))
):
    return update_employee(db, employee_id, update_data)


@router.put("/{employee_id}/deactivate", response_model=EmployeeResponse)
def deactivate_employee(
    employee_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Owner"))
):
    return set_employee_active_status(db, employee_id, False)


@router.put("/{employee_id}/activate", response_model=EmployeeResponse)
def activate_employee(
    employee_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Owner"))
):
    return set_employee_active_status(db, employee_id, True)