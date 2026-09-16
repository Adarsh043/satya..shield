"""
SatyaShield Core Type Definitions and Data Contracts
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
import time


class DocumentType(str, Enum):
    AADHAAR_FRONT = "aadhaar_front"
    AADHAAR_BACK = "aadhaar_back"
    PAN_CARD = "pan_card"
    PASSPORT = "passport"
    DRIVING_LICENCE = "driving_licence"
    VOTER_ID = "voter_id"
    UNKNOWN = "unknown"


class DocumentSource(str, Enum):
    UPLOAD = "upload"
    DIGILOCKER = "digilocker"


class RiskLevel(str, Enum):
    LOW_GREEN = "LOW"             # Fast clear, high trust
    MEDIUM_AMBER = "MEDIUM"       # Suspicious signals, needs review
    HIGH_RED = "HIGH"             # Proven forgery, stolen, or major tamper
    UNKNOWN_REVIEW = "UNKNOWN"     # Missing critical evidence / corrupted


class CheckStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"
    SKIPPED = "SKIPPED"
    ERROR = "ERROR"


@dataclass
class ModuleResult:
    module_name: str
    status: CheckStatus
    confidence: float             # 0.0 to 1.0
    execution_time_ms: float
    details: Dict[str, Any] = field(default_factory=dict)
    reasons: List[str] = field(default_factory=list)


@dataclass
class PreflightResult:
    is_valid: bool
    blur_score: float             # Laplacian variance
    glare_ratio: float            # Percentage of blown out pixels
    resolution: tuple             # (width, height)
    aspect_ratio: float
    reasons: List[str] = field(default_factory=list)


@dataclass
class VerificationOutcome:
    document_id: str
    document_type: DocumentType
    overall_risk: RiskLevel
    trust_score: float            # 0 to 100
    fast_path_cleared: bool       # True if bypassed heavy AI models
    execution_time_ms: float
    factorized_scores: Dict[str, float] = field(default_factory=dict)
    module_results: List[ModuleResult] = field(default_factory=list)
    audit_hash: str = ""
    timestamp: float = field(default_factory=time.time)
    document_source: DocumentSource = DocumentSource.UPLOAD
