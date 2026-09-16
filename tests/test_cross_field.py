"""
Unit Test for Module 8: Cross-Field Consistency Correlator
"""
import unittest
from satyashield.models.cross_field_validator import CrossFieldValidator
from satyashield.core.types import CheckStatus


class TestCrossFieldValidator(unittest.TestCase):
    def setUp(self):
        self.validator = CrossFieldValidator()

    def test_consistent_fields_pass(self):
        visual = {
            "name": "Rohan Sharma",
            "dob": "15/08/1995",
            "aadhaar_number": "XXXX-XXXX-9876"
        }
        qr = {
            "name": "Rohan Sharma",
            "dob": "15-08-1995",
            "masked_aadhaar": "XXXX-XXXX-9876",
            "cryptographically_verified": True
        }
        mod_res = self.validator.evaluate(visual, qr_fields=qr)
        self.assertEqual(mod_res.status, CheckStatus.PASS)
        self.assertEqual(len(mod_res.details["discrepancies"]), 0)
        print(f"\n[Test Cross-Field] Consistent fields: Status = {mod_res.status}, Time = {mod_res.execution_time_ms:.4f}ms")

    def test_spliced_name_fraud_detected(self):
        visual = {
            "name": "Kunal Verma",  # Attacker edited name on image
            "dob": "15/08/1995",
            "aadhaar_number": "XXXX-XXXX-9876"
        }
        qr = {
            "name": "Rohan Sharma",  # Original cardholder in signed QR
            "dob": "15-08-1995",
            "masked_aadhaar": "XXXX-XXXX-9876",
            "cryptographically_verified": True
        }
        mod_res = self.validator.evaluate(visual, qr_fields=qr)
        self.assertEqual(mod_res.status, CheckStatus.FAIL)
        self.assertTrue(any("CRITICAL NAME MISMATCH" in r for r in mod_res.reasons))
        print(f"[Test Cross-Field] Spliced name detected: Status = {mod_res.status}, Reason = {mod_res.reasons[0]}")

    def test_tampered_dob_detected(self):
        visual = {
            "name": "Rohan Sharma",
            "dob": "15/08/1980",    # Attacker modified age
            "aadhaar_number": "XXXX-XXXX-9876"
        }
        qr = {
            "name": "Rohan Sharma",
            "dob": "15-08-1995",    # True DOB in QR
            "masked_aadhaar": "XXXX-XXXX-9876",
            "cryptographically_verified": True
        }
        mod_res = self.validator.evaluate(visual, qr_fields=qr)
        self.assertEqual(mod_res.status, CheckStatus.FAIL)
        self.assertTrue(any("DOB TAMPERING DETECTED" in r for r in mod_res.reasons))
        print(f"[Test Cross-Field] Altered DOB detected: Status = {mod_res.status}, Reason = {mod_res.reasons[0]}")


if __name__ == "__main__":
    unittest.main()
