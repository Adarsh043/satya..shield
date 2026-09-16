import os
import json
import numpy as np
from PIL import Image

from satyashield.data.sample_generator import SampleDocumentGenerator
from satyashield.core.types import DocumentType

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
    
    doc, qr, ocr, face, meta = gen.generate_authentic_aadhaar()
    db.append({"id": "doc1", "type": "aadhaar", "image": doc, "qr": qr, "ocr": ocr, "face": face, "meta": meta})
    
    doc, qr, ocr, face, meta = gen.generate_forged_aadhaar()
    db.append({"id": "doc2", "type": "aadhaar", "image": doc, "qr": qr, "ocr": ocr, "face": face, "meta": meta})
    
    doc, qr, ocr, face, meta = gen.generate_authentic_pan()
    db.append({"id": "doc3", "type": "pan", "image": doc, "qr": qr, "ocr": ocr, "face": face, "meta": meta})
    
    doc, qr, ocr, face, meta = gen.generate_forged_pan_mismatch()
    db.append({"id": "doc4", "type": "pan", "image": doc, "qr": qr, "ocr": ocr, "face": face, "meta": meta})
    
    doc, qr, ocr, face, meta = gen.generate_authentic_passport()
    db.append({"id": "doc5", "type": "passport", "image": doc, "qr": qr, "ocr": ocr, "face": face, "meta": meta})
    
    return db

def test_modules():
    db = generate_mock_db()
    
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
    
    for record in db:
        img = record["image"]
        face = record["face"]
        ocr = record["ocr"]
        qr = record["qr"]
        meta = record["meta"]
        doc_type_str = record["type"]
        
        # 1
        _, mod_preflight, norm_img = modules["PreflightGatekeeper"].evaluate(img)
        results["PreflightGatekeeper"].append(mod_preflight.status.name)
        
        # 2
        mod_qr, qr_data = modules["CryptoQRAuthenticator"].decode_and_verify(qr if qr else "")
        results["CryptoQRAuthenticator"].append(mod_qr.status.name)
        
        # 3
        mod_hash, _ = modules["PerceptualHasher"].evaluate(norm_img, set(), {})
        results["PerceptualHasher"].append(mod_hash.status.name)
        
        # 4
        dt, mod_cls = modules["DocumentClassifier"].classify(norm_img, ocr)
        results["DocumentClassifier"].append(mod_cls.status.name)
        
        # 5
        mod_roi, fields = modules["ROIExtractor"].evaluate(norm_img, dt, ocr)
        results["ROIExtractor"].append(mod_roi.status.name)
        
        # 6
        mod_pii, _, _ = modules["PIIRedactor"].evaluate(fields, norm_img)
        results["PIIRedactor"].append(mod_pii.status.name)
        
        # 7
        doc_num = meta.get("document_number", "")
        mod_chk = modules["ChecksumEngine"].evaluate(doc_type_str, doc_num, meta)
        results["ChecksumEngine"].append(mod_chk.status.name)
        
        # 8
        mod_cross = modules["CrossFieldValidator"].evaluate(meta, qr_data)
        results["CrossFieldValidator"].append(mod_cross.status.name)
        
        # 9
        mod_typo = modules["MicroTypographyForensics"].evaluate(norm_img)
        results["MicroTypographyForensics"].append(mod_typo.status.name)
        
        # 10
        mod_fft = modules["FFTFrequencyForensics"].evaluate(norm_img)
        results["FFTFrequencyForensics"].append(mod_fft.status.name)
        
        # 11
        mod_splice = modules["PhotoSplicingDetector"].evaluate(norm_img)
        results["PhotoSplicingDetector"].append(mod_splice.status.name)
        
        # 12
        mod_face, _ = modules["FaceVerifier"].verify(face, face)
        results["FaceVerifier"].append(mod_face.status.name)
        
        # 13
        mod_liveness = modules["LivenessPADDetector"].evaluate(face)
        results["LivenessPADDetector"].append(mod_liveness.status.name)
        
        # 14
        mod_morph = modules["FaceMorphDetector"].evaluate(face)
        results["FaceMorphDetector"].append(mod_morph.status.name)
        
        # 15
        all_mods = [mod_preflight, mod_qr, mod_hash, mod_cls, mod_roi, mod_pii, mod_chk, mod_cross, mod_typo, mod_fft, mod_splice, mod_face, mod_liveness, mod_morph]
        outcome = modules["FactorizedTrustEngine"].fuse_evidence("mock_id", dt, all_mods)
        results["FactorizedTrustEngine"].append(outcome.overall_risk.name)
        
        # 16
        modules["CryptographicAuditLedger"].record_verification(outcome)
        results["CryptographicAuditLedger"].append("LOGGED")
        
    print("| Module | Doc 1 (Auth Aadhaar) | Doc 2 (Forged Aadhaar) | Doc 3 (Auth PAN) | Doc 4 (Forged PAN) | Doc 5 (Auth Passport) |")
    print("|--------|---------------------|------------------------|------------------|--------------------|-----------------------|")
    
    for name, rlist in results.items():
        row = f"| {name} "
        for status in rlist:
            row += f"| {status} "
        row += "|"
        print(row)
        
if __name__ == '__main__':
    test_modules()
