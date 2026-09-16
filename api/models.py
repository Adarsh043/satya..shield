from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from api.database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_type = Column(String, index=True) # 'indian' or 'foreign'
    mobile_number = Column(String, unique=True, index=True, nullable=True)
    aadhaar_number = Column(String, unique=True, index=True, nullable=True)
    passport_number = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, index=True, nullable=True)
    
    # Profile fields
    name = Column(String, nullable=True)
    dob = Column(String, nullable=True)
    address = Column(String, nullable=True)
    profile_complete = Column(Integer, default=0) # 0 for false, 1 for true (using Integer for sqlite compat)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    verification_requests = relationship("VerificationRequest", back_populates="user")

class Officer(Base):
    __tablename__ = "officers"

    id = Column(Integer, primary_key=True, index=True)
    badge_number = Column(String, unique=True, index=True)
    name = Column(String)
    station = Column(String) # Precinct/Station
    rank = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    verification_requests = relationship("VerificationRequest", back_populates="officer")

class VerificationRequest(Base):
    __tablename__ = "verification_requests"

    id = Column(Integer, primary_key=True, index=True)
    booking_number = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    officer_id = Column(Integer, ForeignKey("officers.id"), nullable=True)
    
    document_front_path = Column(String, nullable=True)
    document_back_path = Column(String, nullable=True)
    live_selfie_path = Column(String, nullable=True)
    
    source = Column(String) # 'UPLOAD' or 'DIGILOCKER'
    ocr_text = Column(String, nullable=True)
    qr_payload = Column(String, nullable=True)
    
    status = Column(String, default="PENDING") # PENDING, IN_PROGRESS, VERIFIED, REJECTED
    rejection_reason = Column(String, nullable=True)
    claimed_document_type = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="verification_requests")
    officer = relationship("Officer", back_populates="verification_requests")
    report = relationship("VerificationReport", back_populates="request", uselist=False)

class VerificationReport(Base):
    __tablename__ = "verification_reports"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("verification_requests.id"), unique=True)
    
    overall_risk_level = Column(String) # LOW_GREEN, MEDIUM_AMBER, HIGH_RED
    trust_score_percentage = Column(Float)
    
    # Store the complete pipeline analysis as a JSON string
    pipeline_json_dump = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    request = relationship("VerificationRequest", back_populates="report")
