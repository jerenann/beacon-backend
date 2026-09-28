from app.database import Base, SessionLocal, engine
from app.models import RiskThreshold, User, UserRole
from app.routers.auth import hash_password

Base.metadata.create_all(bind=engine)

db = SessionLocal()

admin_email = "admin@beacon.com"

existing_admin = db.query(User).filter(User.email == admin_email).first()

if existing_admin is None:
    admin = User(
        full_name="Beacon Administrator",
        email=admin_email,
        password_hash=hash_password("Admin@123"),
        role=UserRole.ADMIN,
    )
    db.add(admin)

existing_threshold = db.query(RiskThreshold).filter(
    RiskThreshold.is_active.is_(True)
).first()

if existing_threshold is None:
    db.add(
        RiskThreshold(
            medium_threshold=0.30,
            high_threshold=0.60,
            is_active=True,
        )
    )

db.commit()
db.close()

print("Seed complete.")
print("Admin email: admin@beacon.com")
print("Admin password: Admin@123")