import os
import json
import numpy as np
from PIL import Image, ImageDraw

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

class AdvancedForgeryGenerator(SampleDocumentGenerator):
    # 1. Tampered MRZ Passport (Fake Checksum)
    def generate_forged_mrz_passport(self):
        doc, qr, ocr, face, meta = self.generate_authentic_passport()
        bad_mrz = meta["mrz_line2"].replace("4", "9") # Tamper a digit
        ocr = ocr.replace(meta["mrz_line2"], bad_mrz)
        meta["mrz_line2"] = bad_mrz
        return {"id": "fake1_bad_mrz", "type": "passport", "image": doc, "qr": qr, "ocr": ocr, "face": face, "meta": meta}

    # 2. Spliced Photo Passport (Alien Box)
    def generate_spliced_photo_passport(self):
        doc, qr, ocr, face, meta = self.generate_authentic_passport()
        alien_box = Image.new("RGB", (160, 200), color=(10, 10, 10))
        doc.paste(alien_box, (35, 135))
        return {"id": "fake2_spliced", "type": "passport", "image": doc, "qr": qr, "ocr": ocr, "face": alien_box, "meta": meta}

    # 3. Morphed Face Passport (Ghosting/Blurry face)
    def generate_morphed_passport(self):
        doc, qr, ocr, face, meta = self.generate_authentic_passport()
        # Add ghosting artifact
        morphed = face.copy().convert("RGBA")
        ghost = face.copy().convert("RGBA")
        ghost.putalpha(128)
        morphed = Image.alpha_composite(morphed, ghost.rotate(2))
        morphed = morphed.convert("RGB")
        doc.paste(morphed, (35, 135))
        return {"id": "fake3_morphed", "type": "passport", "image": doc, "qr": qr, "ocr": ocr, "face": morphed, "meta": meta}

    # 4. Forged Aadhaar QR (Unsigned/Corrupt QR)
    def generate_bad_qr_aadhaar(self):
        doc, qr, ocr, face, meta = self.generate_authentic_aadhaar()
        bad_qr = "eyJhbGciOiJOT05FIiwidHlwIjoiSldUIn0.eyJ1aWQiOiIxMjM0In0." # Invalid signature
        return {"id": "fake4_bad_qr", "type": "aadhaar", "image": doc, "qr": bad_qr, "ocr": ocr, "face": face, "meta": meta}

    # 5. Typographically Forged PAN (Bad font/alignment)
    def generate_typo_forged_pan(self):
        doc, qr, ocr, face, meta = self.generate_authentic_pan()
        draw = ImageDraw.Draw(doc)
        # Paste a badly aligned text block
        draw.rectangle([210, 130, 400, 160], fill=(160, 210, 235))
        draw.text((225, 135), "Name: RAHUL SHARMA", fill=(0, 0, 0)) # Wrong color and slightly off
        return {"id": "fake5_typo", "type": "pan", "image": doc, "qr": qr, "ocr": ocr, "face": face, "meta": meta}

    # 6. Screen Replay Attack (Moire Patterns)
    def generate_replay_attack_id(self):
        doc, qr, ocr, face, meta = self.generate_authentic_aadhaar()
        # Add Moire pattern to the face
        arr = np.array(face, dtype=np.float32)
        x = np.arange(arr.shape[1])
        y = np.arange(arr.shape[0])
        xv, yv = np.meshgrid(x, y)
        moire = np.sin(xv * 0.5) * np.cos(yv * 0.5) * 50
        arr[:, :, 0] = np.clip(arr[:, :, 0] + moire, 0, 255)
        arr[:, :, 1] = np.clip(arr[:, :, 1] + moire, 0, 255)
        arr[:, :, 2] = np.clip(arr[:, :, 2] + moire, 0, 255)
        replay_face = Image.fromarray(arr.astype(np.uint8))
        doc.paste(replay_face, (42, 135))
        return {"id": "fake6_replay", "type": "aadhaar", "image": doc, "qr": qr, "ocr": ocr, "face": replay_face, "meta": meta}

    # 7. Cross-Field Mismatch (DOB discrepancy)
    def generate_cross_field_mismatch(self):
        doc, qr, ocr, face, meta = self.generate_authentic_aadhaar()
        # QR says 1994, OCR says 2004
        ocr = ocr.replace("12/08/1994", "12/08/2004")
        meta["dob"] = "12/08/2004"
        return {"id": "fake7_crossfield", "type": "aadhaar", "image": doc, "qr": qr, "ocr": ocr, "face": face, "meta": meta}

    # 8. Blacklisted Phash (Syndicate Fraud)
    def generate_blacklisted_doc(self):
        doc, qr, ocr, face, meta = self.generate_authentic_pan()
        return {"id": "fake8_blacklisted", "type": "pan", "image": doc, "qr": qr, "ocr": ocr, "face": face, "meta": meta}

    # 9. Low Quality / Glare Document
    def generate_glare_document(self):
        doc, qr, ocr, face, meta = self.generate_authentic_passport()
        # Add massive glare
        draw = ImageDraw.Draw(doc)
        draw.ellipse([200, 100, 600, 500], fill=(255, 255, 255))
        return {"id": "fake9_glare", "type": "passport", "image": doc, "qr": qr, "ocr": ocr, "face": face, "meta": meta}

    # 10. Completely Synthetic / AI Generated Layout (FFT Anomaly)
    def generate_ai_generated_layout(self):
        doc, qr, ocr, face, meta = self.generate_authentic_aadhaar()
        # Add high-frequency noise
        arr = np.array(doc, dtype=np.float32)
        noise = np.random.normal(0, 30.0, arr.shape)
        noisy = np.clip(arr + noise, 0, 255).astype(np.uint8)
        ai_doc = Image.fromarray(noisy)
        return {"id": "fake10_ai_gen", "type": "aadhaar", "image": ai_doc, "qr": qr, "ocr": ocr, "face": face, "meta": meta}


def test_10_forgeries():
    gen = AdvancedForgeryGenerator()
    db = [
        gen.generate_forged_mrz_passport(),
        gen.generate_spliced_photo_passport(),
        gen.generate_morphed_passport(),
        gen.generate_bad_qr_aadhaar(),
        gen.generate_typo_forged_pan(),
        gen.generate_replay_attack_id(),
        gen.generate_cross_field_mismatch(),
        gen.generate_blacklisted_doc(),
        gen.generate_glare_document(),
        gen.generate_ai_generated_layout()
    ]
    
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
        "FactorizedTrustEngine": FactorizedTrustEngine()
    }
    
    # Pre-calculate a blacklist hash for doc 8
    blacklist_hash, _ = modules["PerceptualHasher"].evaluate(db[7]["image"], set(), {})
    blacklist = {blacklist_hash.details.get("phash", "")}
    
    print("| Module | " + " | ".join([f"Doc {i+1}" for i in range(10)]) + " |")
    print("|" + "-"*8 + "|" + "|".join(["-"*7 for _ in range(10)]) + "|")
    
    results = {name: [] for name in modules.keys()}
    
    for record in db:
        img = record["image"]
        face = record["face"]
        ocr = record["ocr"]
        qr = record["qr"]
        meta = record["meta"]
        doc_type_str = record["type"]
        
        _, mod_preflight, norm_img = modules["PreflightGatekeeper"].evaluate(img)
        norm_img = norm_img if norm_img is not None else img
        results["PreflightGatekeeper"].append(mod_preflight.status.name)
        
        mod_qr, qr_data = modules["CryptoQRAuthenticator"].decode_and_verify(qr if qr else "")
        results["CryptoQRAuthenticator"].append(mod_qr.status.name)
        
        mod_hash, _ = modules["PerceptualHasher"].evaluate(norm_img, blacklist, {})
        results["PerceptualHasher"].append(mod_hash.status.name)
        
        dt, mod_cls = modules["DocumentClassifier"].classify(norm_img, ocr)
        results["DocumentClassifier"].append(mod_cls.status.name)
        
        mod_roi, fields = modules["ROIExtractor"].evaluate(norm_img, dt, ocr)
        results["ROIExtractor"].append(mod_roi.status.name)
        
        mod_pii, _, _ = modules["PIIRedactor"].evaluate(fields, norm_img)
        results["PIIRedactor"].append(mod_pii.status.name)
        
        doc_num = meta.get("document_number", "")
        mod_chk = modules["ChecksumEngine"].evaluate(doc_type_str, doc_num, meta)
        results["ChecksumEngine"].append(mod_chk.status.name)
        
        mod_cross = modules["CrossFieldValidator"].evaluate(meta, qr_data)
        results["CrossFieldValidator"].append(mod_cross.status.name)
        
        mod_typo = modules["MicroTypographyForensics"].evaluate(norm_img)
        results["MicroTypographyForensics"].append(mod_typo.status.name)
        
        mod_fft = modules["FFTFrequencyForensics"].evaluate(norm_img)
        results["FFTFrequencyForensics"].append(mod_fft.status.name)
        
        mod_splice = modules["PhotoSplicingDetector"].evaluate(norm_img)
        results["PhotoSplicingDetector"].append(mod_splice.status.name)
        
        mod_face, _ = modules["FaceVerifier"].verify(face, face)
        results["FaceVerifier"].append(mod_face.status.name)
        
        mod_liveness = modules["LivenessPADDetector"].evaluate(face)
        results["LivenessPADDetector"].append(mod_liveness.status.name)
        
        mod_morph = modules["FaceMorphDetector"].evaluate(face)
        results["FaceMorphDetector"].append(mod_morph.status.name)
        
        all_mods = [mod_preflight, mod_qr, mod_hash, mod_cls, mod_roi, mod_pii, mod_chk, mod_cross, mod_typo, mod_fft, mod_splice, mod_face, mod_liveness, mod_morph]
        outcome = modules["FactorizedTrustEngine"].fuse_evidence("fake_id", dt, all_mods)
        results["FactorizedTrustEngine"].append(outcome.overall_risk.name)
        
    for name, rlist in results.items():
        row = f"| {name} "
        for status in rlist:
            row += f"| {status} "
        row += "|"
        print(row)
        
if __name__ == '__main__':
    test_10_forgeries()
