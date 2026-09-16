"""
Unit Test for Module 16: Cryptographic Hash-Chained Audit Ledger
"""
import unittest
from satyashield.models.audit_ledger import CryptographicAuditLedger
from satyashield.core.types import VerificationOutcome, DocumentType, RiskLevel, ModuleResult, CheckStatus


class TestAuditLedger(unittest.TestCase):
    def setUp(self):
        self.ledger = CryptographicAuditLedger()

    def test_record_and_verify_chain(self):
        # Record 3 outcomes
        outcomes = [
            VerificationOutcome("DOC-1", DocumentType.AADHAAR_FRONT, RiskLevel.LOW_GREEN, 98.0, True, 20.0),
            VerificationOutcome("DOC-2", DocumentType.PAN_CARD, RiskLevel.HIGH_RED, 15.0, False, 18.0),
            VerificationOutcome("DOC-3", DocumentType.PASSPORT, RiskLevel.LOW_GREEN, 95.0, False, 45.0)
        ]

        for out in outcomes:
            block = self.ledger.record_verification(out)
            self.assertIsNotNone(block.current_hash)

        self.assertEqual(len(self.ledger.chain), 3)
        # Verify integrity
        is_valid, msg = self.ledger.verify_ledger_integrity()
        self.assertTrue(is_valid)
        print(f"\n[Test Audit Ledger] Valid Chain of 3 blocks: {msg}")

    def test_tampered_block_detected(self):
        out1 = VerificationOutcome("DOC-1", DocumentType.AADHAAR_FRONT, RiskLevel.HIGH_RED, 10.0, False, 20.0)
        out2 = VerificationOutcome("DOC-2", DocumentType.PASSPORT, RiskLevel.LOW_GREEN, 95.0, False, 45.0)
        
        self.ledger.record_verification(out1)
        self.ledger.record_verification(out2)

        # Attacker tampers with Block #0: attempts to change HIGH risk to LOW
        self.ledger.chain[0].overall_risk = RiskLevel.LOW_GREEN.value

        is_valid, msg = self.ledger.verify_ledger_integrity()
        self.assertFalse(is_valid)
        self.assertIn("TAMPER DETECTED", msg)
        print(f"[Test Audit Ledger] Tamper caught: {msg}")


if __name__ == "__main__":
    unittest.main()
