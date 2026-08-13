from app.database.database import SessionLocal
from app.models.role import Role
from app.models.user import User

ROLES = ["Owner", "Employee", "Delivery", "Customer"]


def seed_roles():
    db = SessionLocal()

    try:
        for role_name in ROLES:
            existing = db.query(Role).filter(
                Role.role_name == role_name
            ).first()

            if not existing:
                new_role = Role(role_name=role_name)
                db.add(new_role)
                print(f"Added role: {role_name}")
            else:
                print(f"Role already exists: {role_name}")

        db.commit()

    finally:
        db.close()


if __name__ == "__main__":
    seed_roles()