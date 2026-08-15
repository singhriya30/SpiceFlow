from app.database.database import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.core.security import hash_password

OWNER_EMAIL = "amriva.05@gmail.com"
OWNER_PASSWORD = "AtharvSingh@221203"

def seed_owner():
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == OWNER_EMAIL).first()
        if existing:
            print("Owner account already exists.")
            return

        owner_role = db.query(Role).filter(Role.role_name == "Owner").first()
        if not owner_role:
            print("Owner role not found. Run seed_roles.py first.")
            return

        owner = User(
            first_name="Riya",
            last_name="Singh",
            email=OWNER_EMAIL,
            phone="9798681287",
            password_hash=hash_password(OWNER_PASSWORD),
            role_id=owner_role.id
        )
        db.add(owner)
        db.commit()
        print(f"Owner account created: {OWNER_EMAIL}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_owner()