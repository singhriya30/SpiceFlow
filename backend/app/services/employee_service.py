import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.models.role import Role
from app.schemas.employee import EmployeeCreate, EmployeeUpdate
from app.core.security import hash_password


def create_employee(db: Session, employee_data: EmployeeCreate) -> User:
    existing_user = db.query(User).filter(User.email == employee_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    role = db.query(Role).filter(Role.role_name == employee_data.role_name).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Role '{employee_data.role_name}' not found. Please seed roles first."
        )

    new_employee = User(
        first_name=employee_data.first_name,
        last_name=employee_data.last_name,
        email=employee_data.email,
        phone=employee_data.phone,
        password_hash=hash_password(employee_data.password),
        role_id=role.id,
        is_active=True
    )

    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    return new_employee


def get_employees(db: Session) -> list[User]:
    return (
        db.query(User)
        .join(Role, User.role_id == Role.id)
        .filter(Role.role_name.in_(["Employee", "Delivery"]))
        .all()
    )


def get_employee_by_id(db: Session, employee_id: uuid.UUID) -> User:
    employee = (
        db.query(User)
        .join(Role, User.role_id == Role.id)
        .filter(User.id == employee_id, Role.role_name.in_(["Employee", "Delivery"]))
        .first()
    )
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return employee


def update_employee(db: Session, employee_id: uuid.UUID, update_data: EmployeeUpdate) -> User:
    employee = get_employee_by_id(db, employee_id)

    changes = update_data.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(employee, field, value)

    db.commit()
    db.refresh(employee)
    return employee


def set_employee_active_status(db: Session, employee_id: uuid.UUID, is_active: bool) -> User:
    employee = get_employee_by_id(db, employee_id)
    employee.is_active = is_active
    db.commit()
    db.refresh(employee)
    return employee