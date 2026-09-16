from api.database import SessionLocal
from api import models
import shutil
import os

db = SessionLocal()

# 1. Update paths for mock verification requests
reqs = db.query(models.VerificationRequest).all()
for req in reqs:
    if req.booking_number == "BKG-12345678":
        req.document_front_path = "secure_uploads/BKG-12345678.jpg"
        if os.path.exists("frontend/public/login-left-panel-2.jpg"):
            shutil.copy("frontend/public/login-left-panel-2.jpg", "secure_uploads/BKG-12345678.jpg")
    elif req.booking_number == "BKG-87654321":
        req.document_front_path = "secure_uploads/BKG-87654321.jpg"
        if os.path.exists("frontend/public/login-left-panel.jpg"):
            shutil.copy("frontend/public/login-left-panel.jpg", "secure_uploads/BKG-87654321.jpg")
        
        # Ensure it has a report since it is VERIFIED
        report = db.query(models.VerificationReport).filter(models.VerificationReport.request_id == req.id).first()
        if not report:
            import json
            report = models.VerificationReport(
                request_id=req.id,
                overall_risk_level="LOW_GREEN",
                trust_score_percentage=98.5,
                pipeline_json_dump=json.dumps([{"module_name": "Mock Module", "status": "PASS", "confidence": 0.99, "execution_time_ms": 10, "details": "Mock detail"}])
            )
            db.add(report)

db.commit()
db.close()
print("Database synced properly with file assets.")
