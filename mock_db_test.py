import os
import json
import numpy as np
from PIL import Image

# Import the sample generator
from satyashield.data.sample_generator import SampleDocumentGenerator

# Import all modules
from satyashield.models.preflight import PreflightGatekeeper
from satyashield.models.crypto_qr import CryptoQRAuthenticator
from satyashield.models.checksums import ChecksumEngine
from satyashield.models.perceptual_hash import PerceptualHasher
from satyashield.models.doc_classifier import DocumentClassifier
from satyashield.models.roi_extractor import ROIExtractor
from satyashield.models.pii_redactor import PIIRedactor
from satyashield.models.cross_field_validator import CrossFieldValidator
from satyashield.models.micro_typography import MicroTypographyForensics
from satyashield.models.fft_forensics import FFTFrequencyForensics
from satyashield.models.photo_splicing import PhotoSplicingDetector
from satyashield.models.face_verifier import FaceVerifier
from satyashield.models.liveness_pad import LivenessPADDetector
from satyashield.models.morph_detector import FaceMorphDetector
from satyashield.models.trust_engine import FactorizedTrustEngine
from satyashield.models.audit_ledger import CryptographicAuditLedger

def generate_mock_db():
    gen = SampleDocumentGenerator()
    db = []
    
    # 1. Authentic Aadhaar
    doc, qr, ocr, face, meta = gen.generate_authentic_aadhaar()
    db.append({"id": "doc1", "type": "aadhaar", "status": "authentic", "image": doc, "qr": qr, "ocr": ocr, "face": face, "meta": meta})
    
    # 2. Forged Aadhaar
    doc, qr, ocr, face, meta = gen.generate_forged_aadhaar()
    db.append({"id": "doc2", "type": "aadhaar", "status": "forged", "image": doc, "qr": qr, "ocr": ocr, "face": face, "meta": meta})
    
    # 3. Authentic PAN
    doc, qr, ocr, face, meta = gen.generate_authentic_pan()
    db.append({"id": "doc3", "type": "pan", "status": "authentic", "image": doc, "qr": qr, "ocr": ocr, "face": face, "meta": meta})
    
    # 4. Forged PAN (Mismatch)
    doc, qr, ocr, face, meta = gen.generate_forged_pan_mismatch()
    db.append({"id": "doc4", "type": "pan", "status": "forged", "image": doc, "qr": qr, "ocr": ocr, "face": face, "meta": meta})
    
    # 5. Authentic Passport
    doc, qr, ocr, face, meta = gen.generate_authentic_passport()
    db.append({"id": "doc5", "type": "passport", "status": "authentic", "image": doc, "qr": qr, "ocr": ocr, "face": face, "meta": meta})
    
    return db

def test_modules():
    db = generate_mock_db()
    print(f"Generated Mock Database with {len(db)} documents.")
    
    modules = {
        "PreflightGatekeeper": PreflightGatekeeper(),
        "CryptoQRAuthenticator": CryptoQRAuthenticator(),
        "ChecksumEngine": ChecksumEngine(),
        "PerceptualHasher": PerceptualHasher(),
        "DocumentClassifier": DocumentClassifier(),
        "ROIExtractor": ROIExtractor(),
        "PIIRedactor": PIIRedactor(),
        "CrossFieldValidator": CrossFieldValidator(),
        "MicroTypographyForensics": MicroTypographyForensics(),
        "FFTFrequencyForensics": FFTFrequencyForensics(),
        "PhotoSplicingDetector": PhotoSplicingDetector(),
        "FaceVerifier": FaceVerifier(),
        "LivenessPADDetector": LivenessPADDetector(),
        "FaceMorphDetector": FaceMorphDetector(),
        "FactorizedTrustEngine": FactorizedTrustEngine(),
        "CryptographicAuditLedger": CryptographicAuditLedger()
    }
    
    results = {name: [] for name in modules.keys()}
    
    for i, record in enumerate(db):
        img_array = np.array(record["image"])
        face_array = np.array(record["face"])
        ocr = record["ocr"]
        qr = record["qr"]
        meta = record["meta"]
        
        # 1. Preflight
        res = modules["PreflightGatekeeper"].analyze(img_array)
        results["PreflightGatekeeper"].append((record["id"], res.status.name, res.confidence))
        
        # 2. Crypto QR
        if qr:
            if record["type"] == "aadhaar":
                res = modules["CryptoQRAuthenticator"].verify_aadhaar_qr(qr)
            elif record["type"] == "pan":
                res = modules["CryptoQRAuthenticator"].verify_pan_qr(qr)
            else:
                res = modules["CryptoQRAuthenticator"].verify_aadhaar_qr(qr) # fallback
            results["CryptoQRAuthenticator"].append((record["id"], res.status.name, res.confidence))
        else:
            results["CryptoQRAuthenticator"].append((record["id"], "SKIPPED", 0.0))
            
        # 3. Checksums
        if record["type"] == "aadhaar":
            aadhaar_num = meta.get("document_number", "")
            res = modules["ChecksumEngine"].verify_aadhaar_verhoeff(aadhaar_num)
        elif record["type"] == "pan":
            res = modules["ChecksumEngine"].verify_pan_format(meta.get("document_number", ""))
        elif record["type"] == "passport":
            res = modules["ChecksumEngine"].verify_mrz_checksums(meta.get("mrz_line2", ""))
        else:
            res = modules["ChecksumEngine"].verify_pan_format("XXX")
        results["ChecksumEngine"].append((record["id"], res.status.name, res.confidence))
        
        # 4. Perceptual Hash
        res = modules["PerceptualHasher"].check_blacklist(img_array)
        results["PerceptualHasher"].append((record["id"], res.status.name, res.confidence))
        
        # 5. Classifier
        res = modules["DocumentClassifier"].classify(img_array, ocr)
        results["DocumentClassifier"].append((record["id"], res.status.name, res.confidence))
        
        # 6. ROI
        res = modules["ROIExtractor"].extract_faces(img_array)
        results["ROIExtractor"].append((record["id"], res.status.name, res.confidence))
        
        # 7. PII Redactor
        res = modules["PIIRedactor"].redact_image(img_array, [{"box": [10, 10, 50, 50], "type": "UID"}])
        results["PIIRedactor"].append((record["id"], res.status.name, res.confidence))
        
        # 8. Cross Field
        res = modules["CrossFieldValidator"].validate(ocr, meta)
        results["CrossFieldValidator"].append((record["id"], res.status.name, res.confidence))
        
        # 9. Micro Typography
        res = modules["MicroTypographyForensics"].analyze(img_array)
        results["MicroTypographyForensics"].append((record["id"], res.status.name, res.confidence))
        
        # 10. FFT Forensics
        res = modules["FFTFrequencyForensics"].analyze(img_array)
        results["FFTFrequencyForensics"].append((record["id"], res.status.name, res.confidence))
        
        # 11. Photo Splicing
        res = modules["PhotoSplicingDetector"].analyze(img_array)
        results["PhotoSplicingDetector"].append((record["id"], res.status.name, res.confidence))
        
        # 12. Face Verifier
        res = modules["FaceVerifier"].verify(face_array, face_array)
        results["FaceVerifier"].append((record["id"], res.status.name, res.confidence))
        
        # 13. Liveness PAD
        res = modules["LivenessPADDetector"].analyze(face_array)
        results["LivenessPADDetector"].append((record["id"], res.status.name, res.confidence))
        
        # 14. Morph Detector
        res = modules["FaceMorphDetector"].analyze(face_array)
        results["FaceMorphDetector"].append((record["id"], res.status.name, res.confidence))
        
        # 15. Trust Engine
        # mock green and amber path results
        dummy_res = modules["PreflightGatekeeper"].analyze(img_array)
        trust = modules["FactorizedTrustEngine"].compute_trust_score(
            green_path=[dummy_res], amber_path=[dummy_res], red_path=[]
        )
        results["FactorizedTrustEngine"].append((record["id"], "PASS" if trust.score > 70 else "WARNING", trust.score / 100))
        
        # 16. Audit Ledger
        tx_id = modules["CryptographicAuditLedger"].log_event("TEST", {"doc_id": record["id"]})
        status = "PASS" if tx_id else "FAIL"
        results["CryptographicAuditLedger"].append((record["id"], status, 1.0))
        
    # Print Markdown Table
    print("\n# Test Results\n")
    print("| Module | Doc 1 (Auth Aadhaar) | Doc 2 (Forged Aadhaar) | Doc 3 (Auth PAN) | Doc 4 (Forged PAN) | Doc 5 (Auth Passport) |")
    print("|--------|---------------------|------------------------|------------------|--------------------|-----------------------|")
    
    for name, rlist in results.items():
        row = f"| {name} "
        for item in rlist:
            row += f"| {item[1]} ({item[2]:.2f}) "
        row += "|"
        print(row)
        
if __name__ == '__main__':
    test_modules()
