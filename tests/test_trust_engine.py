"""
Unit Test for Module 15: Factorized Trust Matrix (FTM) Decision Engine
"""
import unittest
from satyashield.models.trust_engine import FactorizedTrustEngine
from satyashield.core.types import RiskLevel, CheckStatus, ModuleResult, DocumentType


class TestFactorizedTrustEngine(unittest.TestCase):
    def setUp(self):
        self.engine = FactorizedTrustEngine()

    def test_clean_document_low_risk(self):
        results = [
            ModuleResult("preflight_intake", CheckStatus.PASS, 1.0, 5.0),
            ModuleResult("deterministic_checksums", CheckStatus.PASS, 1.0, 0.1),
            ModuleResult("biometric_face_verifier", CheckStatus.PASS, 0.95, 4.0),
            ModuleResult("micro_typography", CheckStatus.PASS, 0.90, 8.0),
            ModuleResult("photo_splicing_detector", CheckStatus.PASS, 0.95, 3.0),
        ]
        outcome = self.engine.fuse_evidence("DOC-101", DocumentType.AADHAAR_FRONT, results)
        self.assertEqual(outcome.overall_risk, RiskLevel.LOW_GREEN)
        self.assertGreater(outcome.trust_score, 85.0)
        print(f"\n[Test Trust Engine] Clean document: Risk = {outcome.overall_risk.value}, Trust Score = {outcome.trust_score}")

    def test_hard_checksum_failure_overrides_soft_scores(self):
        # Even if 4 other modules passed with 1.0 confidence, 1 checksum failure must force HIGH RED
        results = [
            ModuleResult("preflight_intake", CheckStatus.PASS, 1.0, 5.0),
            ModuleResult("deterministic_checksums", CheckStatus.FAIL, 0.0, 0.1, reasons=["INVALID AADHAAR CHECKSUM"]),
            ModuleResult("biometric_face_verifier", CheckStatus.PASS, 0.95, 4.0),
            ModuleResult("micro_typography", CheckStatus.PASS, 0.90, 8.0),
            ModuleResult("photo_splicing_detector", CheckStatus.PASS, 0.95, 3.0),
        ]
        outcome = self.engine.fuse_evidence("DOC-FRAUD-01", DocumentType.AADHAAR_FRONT, results)
        self.assertEqual(outcome.overall_risk, RiskLevel.HIGH_RED)
        self.assertLess(outcome.trust_score, 25.0)
        print(f"[Test Trust Engine] Checksum failure override: Risk = {outcome.overall_risk.value}, Trust Score = {outcome.trust_score}")

    def test_supporting_warnings_yield_amber_review(self):
        results = [
            ModuleResult("preflight_intake", CheckStatus.PASS, 1.0, 5.0),
            ModuleResult("deterministic_checksums", CheckStatus.PASS, 1.0, 0.1),
            ModuleResult("fft_frequency_forensics", CheckStatus.WARNING, 0.6, 12.0, reasons=["Periodic frequency grid"]),
            ModuleResult("micro_typography", CheckStatus.PASS, 0.90, 8.0),
        ]
        outcome = self.engine.fuse_evidence("DOC-AMBER-02", DocumentType.PASSPORT, results)
        self.assertEqual(outcome.overall_risk, RiskLevel.MEDIUM_AMBER)
        self.assertTrue(50.0 <= outcome.trust_score <= 75.0)
        print(f"[Test Trust Engine] Amber review case: Risk = {outcome.overall_risk.value}, Trust Score = {outcome.trust_score}")


if __name__ == "__main__":
    unittest.main()
