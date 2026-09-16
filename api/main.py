import io
import os
import uuid
import logging
from typing import Optional, List

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image
from sqlalchemy.orm import Session

from api.database import engine, get_db
from api import models
from satyashield.pipeline.orchestrator import SatyaShieldPipeline
from satyashield.core.types import DocumentSource

# Create DB Tables
models.Base.metadata.create_all(bind=engine)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SatyaShield Dual Portal API",
    description="Backend for Citizen Intake and Officer Verification Portals.",
    version="2.0.0"
)

from fastapi.staticfiles import StaticFiles

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory="secure_uploads"), name="uploads")

pipeline = SatyaShieldPipeline(fraud_blacklist=set())

# Ensure upload directory exists
UPLOAD_DIR = "secure_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- Pydantic Models ---
class BookingResponse(BaseModel):
    booking_number: str
    message: str

class AppointmentList(BaseModel):
    booking_number: str
    visitor_name: str
    document_type: str
    source: str
    status: str
    created_at: str

class VerificationResponse(BaseModel):
    document_id: str
    document_type: str
    overall_risk: str
    trust_score: float
    execution_time_ms: float
    modules: list
    message: str

class LoginResponse(BaseModel):
    token: str
    officer_id: str

class VisitorOTPRequest(BaseModel):
    visitor_type: str
    id_type: str
    id_value: str
    email: Optional[str] = None

class VisitorOTPVerifyRequest(BaseModel):
    session_id: str
    otp: str
    id_value: str
    id_type: str
    visitor_type: str

class VisitorOTPResponse(BaseModel):
    message: str
    session_id: str

class VisitorLoginResponse(BaseModel):
    message: str
    token: str
    user_id: int
    profile_complete: bool
    visitor_type: str

class VisitorProfileUpdateRequest(BaseModel):
    user_id: int
    name: str
    dob: str
    address: str

# --- CITIZEN PORTAL ENDPOINTS ---

@app.post("/api/v1/citizen/book", response_model=BookingResponse)
async def citizen_book_appointment(
    document: UploadFile = File(...),
    source: str = Form("UPLOAD"),
    user_id: int = Form(...),
    ocr_text: Optional[str] = Form(None),
    qr_payload: Optional[str] = Form(None),
    claimed_document_type: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Citizen uploads document securely. No verification is run here.
    """
    try:
        # Generate booking ID and secure filename
        booking_id = f"BKG-{str(uuid.uuid4())[:8].upper()}"
        file_ext = document.filename.split('.')[-1] if '.' in document.filename else 'jpg'
        secure_path = os.path.join(UPLOAD_DIR, f"{booking_id}.{file_ext}")

        # Save file to secure storage
        with open(secure_path, "wb") as buffer:
            buffer.write(await document.read())

        # Save to DB
        new_req = models.VerificationRequest(
            booking_number=booking_id,
            user_id=user_id,
            document_front_path=secure_path,
            source=source.upper(),
            ocr_text=ocr_text,
            qr_payload=qr_payload,
            claimed_document_type=claimed_document_type,
            status="PENDING"
        )
        db.add(new_req)
        db.commit()

        return BookingResponse(
            booking_number=booking_id,
            message="Document securely submitted. Present this booking number to the officer."
        )
    except Exception as e:
        logger.error(f"Error booking appointment: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to book appointment")

class StatusUpdateRequest(BaseModel):
    status: str
    rejection_reason: Optional[str] = None

@app.patch("/api/v1/officer/status/{booking_number}")
async def update_booking_status(booking_number: str, req: StatusUpdateRequest, db: Session = Depends(get_db)):
    # Retrieve the verification request
    v_req = db.query(models.VerificationRequest).filter(models.VerificationRequest.booking_number == booking_number).first()
    if not v_req:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if req.status not in ["VERIFIED", "REJECTED"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    v_req.status = req.status
    if req.rejection_reason:
        v_req.rejection_reason = req.rejection_reason

    # If rejected, create a verification report for case file generation (if not exists)
    if req.status == "REJECTED":
        existing_report = db.query(models.VerificationReport).filter(models.VerificationReport.request_id == v_req.id).first()
        if not existing_report:
            report = models.VerificationReport(
                request_id=v_req.id,
                overall_risk_level="HIGH_RED",
                trust_score_percentage=0.0,
                pipeline_json_dump=None  # Placeholder – can be populated with detailed module results later
            )
            db.add(report)

    db.commit()
    return {"message": "Status updated successfully"}

@app.get("/api/v1/citizen/status/{booking_number}")
async def check_booking_status(booking_number: str, db: Session = Depends(get_db)):
    """Allows a citizen to poll the status of their verification request."""
    v_req = db.query(models.VerificationRequest).filter(models.VerificationRequest.booking_number == booking_number).first()
    if not v_req:
        raise HTTPException(status_code=404, detail="Booking not found")
    return {"status": v_req.status}



# --- OFFICER PORTAL ENDPOINTS ---

@app.post("/api/v1/officer/login", response_model=LoginResponse)
async def officer_login(
    username: str = Form(...),
    password: str = Form(...)
):
    """Mock Login for BSF/Police"""
    if username == "admin" and password == "admin":
        return LoginResponse(token="mock-jwt-token-789", officer_id="BSF-OFFICER-001")
    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.get("/api/v1/officer/appointments", response_model=List[AppointmentList])
async def get_appointments(db: Session = Depends(get_db)):
    """Fetch all verifications for history and queue"""
    appointments = db.query(models.VerificationRequest).order_by(models.VerificationRequest.created_at.desc()).all()
    return [
        AppointmentList(
            booking_number=a.booking_number,
            visitor_name=a.user.name if a.user and a.user.name else "Unknown Visitor",
            document_type=a.document_front_path.split('.')[-1].upper() if a.document_front_path else "DOC",
            source=a.source,
            status=a.status,
            created_at=a.created_at.isoformat()
        )
        for a in appointments
    ]

class AppointmentDetails(BaseModel):
    booking_number: str
    visitor_name: str
    document_type: str
    source: str
    status: str
    created_at: str
    document_url: str

@app.get("/api/v1/officer/appointments/{booking_number}", response_model=AppointmentDetails)
async def get_appointment_details(booking_number: str, db: Session = Depends(get_db)):
    """Fetch details of a single pending verification"""
    v_req = db.query(models.VerificationRequest).filter(models.VerificationRequest.booking_number == booking_number).first()
    if not v_req:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    file_ext = v_req.document_front_path.split('.')[-1]
    return AppointmentDetails(
        booking_number=v_req.booking_number,
        visitor_name=v_req.user.name if v_req.user and v_req.user.name else "Unknown Visitor",
        document_type=v_req.document_front_path.split('.')[-1].upper() if v_req.document_front_path else "DOC",
        source=v_req.source,
        status=v_req.status,
        created_at=v_req.created_at.isoformat(),
        document_url=f"http://localhost:8000/uploads/{booking_number}.{file_ext}"
    )

@app.post("/api/v1/officer/verify/{booking_number}", response_model=VerificationResponse)
async def officer_verify(
    booking_number: str,
    selfie: UploadFile = File(...),
    thumb_impression: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Officer triggers verification by providing live selfie (and thumb).
    """
    try:
        # 1. Retrieve citizen document from DB
        v_req = db.query(models.VerificationRequest).filter(models.VerificationRequest.booking_number == booking_number).first()
        if not v_req:
            raise HTTPException(status_code=404, detail="Booking not found")
        if v_req.status == "VERIFIED":
            raise HTTPException(status_code=400, detail="Booking already verified")

        if not os.path.exists(v_req.document_front_path):
            raise HTTPException(status_code=500, detail="Secure document file missing")

        # 2. Load images
        doc_img = Image.open(v_req.document_front_path).convert("RGB")
        
        selfie_bytes = await selfie.read()
        selfie_img = Image.open(io.BytesIO(selfie_bytes)).convert("RGB")
        
        # Note: Thumb impression logic would be handled here (mocked for now)

        try:
            doc_source = DocumentSource[v_req.source]
        except KeyError:
            doc_source = DocumentSource.UPLOAD

        # 3. OCR Extraction (Using EasyOCR)
        try:
            import easyocr
            import numpy as np
            global reader
            if 'reader' not in globals() or reader is None:
                reader = easyocr.Reader(['en'], gpu=False)
            import cv2
            img_cv = np.array(doc_img)
            
            # Fast downscale to max 800px dimension for >10x speedup on CPU OCR
            h, w = img_cv.shape[:2]
            if max(h, w) > 800:
                scale = 800 / max(h, w)
                img_cv = cv2.resize(img_cv, (int(w * scale), int(h * scale)))
                
            ocr_results = reader.readtext(img_cv, detail=0)
            ocr_text = " ".join(ocr_results)
            logger.info(f"Extracted OCR text length: {len(ocr_text)}")
        except Exception as e:
            logger.error(f"OCR Failed: {e}")
            ocr_text = v_req.ocr_text
        
        # 4. Execute Pipeline
        logger.info(f"Officer verifying {booking_number}")
        
        claimed_name = v_req.user.name if v_req.user and v_req.user.name else ""
        claimed_dob = v_req.user.dob if v_req.user and v_req.user.dob else ""
        
        outcome = pipeline.verify_document(
            document_id=booking_number,
            document_image=doc_img,
            qr_payload=v_req.qr_payload,
            ocr_text=ocr_text,
            live_selfie=selfie_img,
            source=doc_source,
            extra_metadata={
                "claimed_document_type": v_req.claimed_document_type,
                "claimed_name": claimed_name,
                "claimed_dob": claimed_dob
            }
        )

        # 4. Update DB status and create report
        v_req.status = "IN_PROGRESS"
        
        import json
        serialized_modules = []
        for mod in outcome.module_results:
            serialized_modules.append({
                "module_name": mod.module_name,
                "status": mod.status.name,
                "confidence": mod.confidence,
                "execution_time_ms": mod.execution_time_ms,
                "details": mod.details
            })
            
        report = models.VerificationReport(
            request=v_req,
            overall_risk_level=outcome.overall_risk.name,
            trust_score_percentage=outcome.trust_score,
            pipeline_json_dump=json.dumps(serialized_modules)
        )
        db.add(report)
        db.commit()

        # 5. Serialize results
        serialized_modules = []
        for mod in outcome.module_results:
            serialized_modules.append({
                "module_name": mod.module_name,
                "status": mod.status.name,
                "confidence": mod.confidence,
                "execution_time_ms": mod.execution_time_ms,
                "details": mod.details
            })

        return VerificationResponse(
            document_id=outcome.document_id,
            document_type=outcome.document_type.name if outcome.document_type else "UNKNOWN",
            overall_risk=outcome.overall_risk.name,
            trust_score=outcome.trust_score,
            execution_time_ms=outcome.execution_time_ms,
            modules=serialized_modules,
            message="Verification completed by Officer."
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in officer verify: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# --- VISITOR PORTAL ENDPOINTS ---

@app.post("/api/v1/visitor/request-otp", response_model=VisitorOTPResponse)
async def visitor_request_otp(req: VisitorOTPRequest):
    """Mock OTP request for visitors."""
    # In a real system, we'd send an SMS/Email here and save the generated OTP to a DB/Cache.
    session_id = f"sess-{str(uuid.uuid4())}"
    logger.info(f"OTP requested for {req.visitor_type} visitor using {req.id_type}: {req.id_value}")
    return VisitorOTPResponse(message="OTP sent successfully", session_id=session_id)


@app.post("/api/v1/visitor/verify-otp", response_model=VisitorLoginResponse)
async def visitor_verify_otp(req: VisitorOTPVerifyRequest, db: Session = Depends(get_db)):
    """Mock OTP verification for visitors."""
    if req.otp == "123456":
        logger.info(f"Successful OTP verification for {req.id_value}")
        
        # Look up or create user
        user = None
        if req.id_type == 'mobile':
            user = db.query(models.User).filter(models.User.mobile_number == req.id_value).first()
        elif req.id_type == 'passport':
            user = db.query(models.User).filter(models.User.passport_number == req.id_value).first()
        elif req.id_type == 'aadhaar':
            user = db.query(models.User).filter(models.User.aadhaar_number == req.id_value).first()
            
        if not user:
            user = models.User(
                user_type=req.visitor_type,
                mobile_number=req.id_value if req.id_type == 'mobile' else None,
                passport_number=req.id_value if req.id_type == 'passport' else None,
                aadhaar_number=req.id_value if req.id_type == 'aadhaar' else None,
                profile_complete=0
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        return VisitorLoginResponse(
            message="Login successful", 
            token="mock-visitor-jwt-token-123",
            user_id=user.id,
            profile_complete=bool(user.profile_complete),
            visitor_type=req.visitor_type
        )
    
    logger.warning(f"Failed OTP verification for session {req.session_id}")
    raise HTTPException(status_code=400, detail="Incorrect verification code. Please try again.")

@app.get("/api/v1/visitor/profile/{user_id}")
async def get_visitor_profile(user_id: int, db: Session = Depends(get_db)):
    """Fetch visitor profile data (name, dob, visitor_type)."""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "user_id": user.id,
        "name": user.name,
        "dob": user.dob,
        "address": user.address,
        "user_type": user.user_type,
        "profile_complete": bool(user.profile_complete)
    }

@app.post("/api/v1/visitor/profile")
async def update_visitor_profile(req: VisitorProfileUpdateRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.name = req.name
    user.dob = req.dob
    user.address = req.address
    user.profile_complete = 1
    db.commit()
    
    return {"message": "Profile updated successfully"}

@app.get("/api/v1/visitor/requests/{user_id}")
async def get_visitor_requests(user_id: int, db: Session = Depends(get_db)):
    requests = db.query(models.VerificationRequest).filter(models.VerificationRequest.user_id == user_id).order_by(models.VerificationRequest.created_at.desc()).all()
    
    result = []
    for req in requests:
        result.append({
            "id": req.booking_number,
            "visitorName": req.user.name if req.user and req.user.name else "Unknown",
            "documentType": req.document_front_path.split('.')[-1].upper() if req.document_front_path else "DOC",
            "documentSource": req.source,
            "status": req.status,
            "submittedAt": req.created_at.isoformat(),
            "rejectionReason": req.rejection_reason
        })
    return result
