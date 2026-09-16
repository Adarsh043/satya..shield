from api.database import SessionLocal, engine, Base
from api import models
import datetime

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# Check if already seeded
if db.query(models.Officer).count() == 0:
    # Add Users
    u1 = models.User(user_type="indian", mobile_number="9876543210", aadhaar_number="123456789012", name="Rahul Sharma", dob="1990-01-01", address="Delhi", profile_complete=1)
    u2 = models.User(user_type="foreign", passport_number="Z1234567", email="john.doe@example.com", name="John Doe", dob="1985-05-15", address="New York", profile_complete=1)
    db.add_all([u1, u2])
    db.commit()

    # Add Officer
    o1 = models.Officer(badge_number="BSF-OFFICER-001", name="Amit Kumar", station="Border Post Alpha", rank="Inspector")
    db.add(o1)
    db.commit()

    # Add Verification Requests
    v1 = models.VerificationRequest(
        booking_number="BKG-12345678",
        user_id=u1.id,
        officer_id=o1.id,
        document_front_path="public/login-left-panel-2.jpg",
        source="UPLOAD",
        status="PENDING",
        created_at=datetime.datetime.utcnow()
    )
    v2 = models.VerificationRequest(
        booking_number="BKG-87654321",
        user_id=u2.id,
        officer_id=o1.id,
        document_front_path="public/login-left-panel.jpg",
        source="UPLOAD",
        status="VERIFIED",
        created_at=datetime.datetime.utcnow() - datetime.timedelta(days=1)
    )
    db.add_all([v1, v2])
    db.commit()
    print("Database seeded with mock data successfully.")
else:
    print("Database already contains data.")

db.close()
