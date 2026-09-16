"""
SatyaShield Master End-to-End Test Suite
----------------------------------------
Tests the entire pipeline across 9 distinct real-world and synthetic document scenarios:
1. Authentic e-Aadhaar (Fast Path Green clearance in <150ms)
2. Forged Aadhaar (Corrupted Verhoeff checksum & name tamper -> RED)
3. Authentic PAN Card (Valid entity and surname match -> GREEN)
4. Forged PAN Card (Mismatched 5th character -> RED)
5. Authentic Passport (Valid ICAO 9303 MRZ -> GREEN)
6. Spliced Photo Attack (Cut-and-paste boundary detected -> RED)
7. Replay Attack (Blacklisted pHash -> Instant RED)
8. Blurry / Unreadable Input (Preflight gatekeeper reject -> UNKNOWN)
9. Cryptographic Audit Ledger Chain Integrity Verification
"""
import unittest
from PIL import ImageFilter
from satyashield.pipeline.orchestrator import SatyaShieldPipeline
from satyashield.data.sample_generator import SampleDocumentGenerator
from satyashield.core.types import RiskLevel, CheckStatus, DocumentType


class TestSatyaShieldFullSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.generator = SampleDocumentGenerator()
        cls.pipeline = SatyaShieldPipeline()

    def test_01_authentic_aadhaar_fast_path_green(self):
        card, qr_b64, ocr_text, selfie, meta = self.generator.generate_authentic_aadhaar()
        outcome = self.pipeline.verify_document(
            document_id="AADHAAR-GENUINE-001",
            document_image=card,
            qr_payload=qr_b64,
            ocr_text=ocr_text,
            live_selfie=selfie,
            extra_metadata=meta
        )
        self.assertEqual(outcome.overall_risk, RiskLevel.LOW_GREEN)
        self.assertTrue(outcome.fast_path_cleared)
        self.assertGreater(outcome.trust_score, 90.0)
        self.assertLess(outcome.execution_time_ms, 250.0)
        print(f"\n[Scenario 1] Authentic Aadhaar: Risk = {outcome.overall_risk.value}, Trust = {outcome.trust_score}, FastPath = {outcome.fast_path_cleared}, Time = {outcome.execution_time_ms:.2f}ms")

    def test_02_forged_aadhaar_checksum_red(self):
        card, qr_b64, ocr_text, selfie, meta = self.generator.generate_forged_aadhaar()
        outcome = self.pipeline.verify_document(
            document_id="AADHAAR-FORGED-002",
            document_image=card,
            qr_payload=qr_b64,
            ocr_text=ocr_text,
            live_selfie=selfie,
            extra_metadata=meta
        )
        self.assertEqual(outcome.overall_risk, RiskLevel.HIGH_RED)
        self.assertFalse(outcome.fast_path_cleared)
        self.assertLess(outcome.trust_score, 30.0)
        print(f"[Scenario 2] Forged Aadhaar: Risk = {outcome.overall_risk.value}, Trust = {outcome.trust_score}, Time = {outcome.execution_time_ms:.2f}ms")

    def test_03_authentic_pan_card(self):
        card, qr_b64, ocr_text, selfie, meta = self.generator.generate_authentic_pan()
        outcome = self.pipeline.verify_document(
            document_id="PAN-GENUINE-003",
            document_image=card,
            qr_payload=qr_b64,
            ocr_text=ocr_text,
            live_selfie=selfie,
            extra_metadata=meta
        )
        self.assertEqual(outcome.overall_risk, RiskLevel.LOW_GREEN)
        self.assertGreater(outcome.trust_score, 85.0)
        print(f"[Scenario 3] Authentic PAN: Risk = {outcome.overall_risk.value}, Trust = {outcome.trust_score}, Time = {outcome.execution_time_ms:.2f}ms")

    def test_04_forged_pan_mismatched_surname(self):
        card, qr_b64, ocr_text, selfie, meta = self.generator.generate_forged_pan_mismatch()
        outcome = self.pipeline.verify_document(
            document_id="PAN-FORGED-004",
            document_image=card,
            qr_payload=qr_b64,
            ocr_text=ocr_text,
            live_selfie=selfie,
            extra_metadata=meta
        )
        self.assertEqual(outcome.overall_risk, RiskLevel.HIGH_RED)
        print(f"[Scenario 4] Forged PAN Mismatch: Risk = {outcome.overall_risk.value}, Trust = {outcome.trust_score}, Time = {outcome.execution_time_ms:.2f}ms")

    def test_05_authentic_passport(self):
        card, qr_b64, ocr_text, selfie, meta = self.generator.generate_authentic_passport()
        outcome = self.pipeline.verify_document(
            document_id="PASS-GENUINE-005",
            document_image=card,
            qr_payload=qr_b64,
            ocr_text=ocr_text,
            live_selfie=selfie,
            extra_metadata=meta
        )
        self.assertEqual(outcome.overall_risk, RiskLevel.LOW_GREEN)
        self.assertGreater(outcome.trust_score, 80.0)
        print(f"[Scenario 5] Authentic Passport: Risk = {outcome.overall_risk.value}, Trust = {outcome.trust_score}, Time = {outcome.execution_time_ms:.2f}ms")

    def test_06_spliced_photo_attack(self):
        card, qr_b64, ocr_text, selfie, meta = self.generator.generate_spliced_photo_attack()
        outcome = self.pipeline.verify_document(
            document_id="DOC-SPLICED-006",
            document_image=card,
            qr_payload="", # No QR, forcing deep forensic path
            ocr_text=ocr_text,
            live_selfie=selfie,
            extra_metadata=meta
        )
        self.assertEqual(outcome.overall_risk, RiskLevel.HIGH_RED)
        print(f"[Scenario 6] Spliced Photo Attack: Risk = {outcome.overall_risk.value}, Trust = {outcome.trust_score}, Time = {outcome.execution_time_ms:.2f}ms")

    def test_07_replay_attack_blacklist(self):
        card, qr_b64, ocr_text, selfie, meta = self.generator.generate_authentic_aadhaar()
        # Add card's hash to blacklist
        card_hash = self.pipeline.hasher.compute_phash(card)
        self.pipeline.fraud_blacklist.add(card_hash)

        outcome = self.pipeline.verify_document(
            document_id="DOC-REPLAY-007",
            document_image=card,
            qr_payload=qr_b64,
            ocr_text=ocr_text,
            live_selfie=selfie,
            extra_metadata=meta
        )
        self.assertEqual(outcome.overall_risk, RiskLevel.HIGH_RED)
        self.assertLess(outcome.execution_time_ms, 80.0) # Fail fast
        print(f"[Scenario 7] Blacklist Replay Attack: Risk = {outcome.overall_risk.value}, Trust = {outcome.trust_score}, Time = {outcome.execution_time_ms:.2f}ms")

    def test_08_blurry_image_preflight_reject(self):
        card, qr_b64, ocr_text, selfie, meta = self.generator.generate_authentic_aadhaar()
        blurry = card.filter(ImageFilter.GaussianBlur(radius=10))

        outcome = self.pipeline.verify_document(
            document_id="DOC-BLUR-008",
            document_image=blurry,
            qr_payload=qr_b64,
            ocr_text=ocr_text,
            live_selfie=selfie,
            extra_metadata=meta
        )
        self.assertEqual(outcome.overall_risk, RiskLevel.UNKNOWN_REVIEW)
        print(f"[Scenario 8] Blurry Preflight Reject: Risk = {outcome.overall_risk.value}, Trust = {outcome.trust_score}, Time = {outcome.execution_time_ms:.2f}ms")

    def test_09_audit_ledger_integrity(self):
        # Verify the cryptographic integrity of all verifications recorded in the ledger
        is_valid, msg = self.pipeline.audit_ledger.verify_ledger_integrity()
        self.assertTrue(is_valid)
        print(f"[Scenario 9] Cryptographic Audit Ledger: Total Blocks = {len(self.pipeline.audit_ledger.chain)}, Integrity = {is_valid} ('{msg}')")


if __name__ == "__main__":
    unittest.main()
