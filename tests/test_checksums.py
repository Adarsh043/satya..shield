"""
Unit Test for Module 3: Deterministic Checksum & Mathematical Rules Engine
"""
import unittest
from satyashield.models.checksums import ChecksumEngine
from satyashield.core.types import CheckStatus


class TestChecksumEngine(unittest.TestCase):
    def setUp(self):
        self.engine = ChecksumEngine()

    def test_verhoeff_aadhaar_validation(self):
        # 11-digit base: 23456789012
        base = "23456789012"
        check_digit = self.engine.calculate_verhoeff_checksum(base)
        valid_aadhaar = f"{base}{check_digit}"

        # Test Valid
        res_valid = self.engine.evaluate("aadhaar", valid_aadhaar)
        self.assertEqual(res_valid.status, CheckStatus.PASS)
        self.assertLess(res_valid.execution_time_ms, 1.0)
        print(f"\n[Test Checksums] Valid Aadhaar ({valid_aadhaar}): Status = {res_valid.status}, Time = {res_valid.execution_time_ms:.4f}ms")

        # Test Tampered (single digit altered: replace last digit with an incorrect one)
        wrong_digit = (check_digit + 1) % 10
        tampered_aadhaar = f"{base}{wrong_digit}"
        res_tampered = self.engine.evaluate("aadhaar", tampered_aadhaar)
        self.assertEqual(res_tampered.status, CheckStatus.FAIL)
        self.assertTrue(any("INVALID AADHAAR CHECKSUM" in r for r in res_tampered.reasons))
        print(f"[Test Checksums] Tampered Aadhaar ({tampered_aadhaar}): Status = {res_tampered.status}, Reason = {res_tampered.reasons[0]}")

    def test_passport_mrz_line2(self):
        # Standard TD3 line 2
        # Passport: L898902C<
        pass_num = "L898902C<"
        pass_chk = self.engine.calculate_mrz_check_digit(pass_num)
        dob = "690806"
        dob_chk = self.engine.calculate_mrz_check_digit(dob)
        exp = "940623"
        exp_chk = self.engine.calculate_mrz_check_digit(exp)
        
        valid_line2 = f"{pass_num}{pass_chk}UTO{dob}{dob_chk}F{exp}{exp_chk}ZE184226B<<<<<10"
        # Pad to 44 chars
        valid_line2 = valid_line2.ljust(44, '<')

        res_pass = self.engine.evaluate("passport", "", {"mrz_line2": valid_line2})
        self.assertEqual(res_pass.status, CheckStatus.PASS)
        print(f"[Test Checksums] Valid Passport MRZ Line 2: Status = {res_pass.status}, Time = {res_pass.execution_time_ms:.4f}ms")

        # Corrupt passport number check digit
        tampered_line2 = valid_line2[:9] + ("0" if valid_line2[9] != "0" else "1") + valid_line2[10:]
        res_fail = self.engine.evaluate("passport", "", {"mrz_line2": tampered_line2})
        self.assertEqual(res_fail.status, CheckStatus.FAIL)
        self.assertTrue(any("MRZ PASSPORT NUMBER CHECKSUM FAILED" in r for r in res_fail.reasons))
        print(f"[Test Checksums] Tampered Passport MRZ: Status = {res_fail.status}, Reason = {res_fail.reasons[0]}")

    def test_pan_semantic_validation(self):
        # Valid Individual PAN for "KAPOOR": 4th letter 'P', 5th letter 'K'
        pan_kapoor = "ABC PK 1234 D".replace(" ", "")
        res_pan = self.engine.evaluate("pan", pan_kapoor, {"surname": "Kapoor"})
        self.assertEqual(res_pan.status, CheckStatus.PASS)
        print(f"[Test Checksums] Valid PAN ({pan_kapoor}): Status = {res_pan.status}, Entity = {res_pan.details['entity']}")

        # Fraudulent PAN: 5th letter 'K' but surname is "Sharma" (expected 'S')
        res_fraud = self.engine.evaluate("pan", pan_kapoor, {"surname": "Sharma"})
        self.assertEqual(res_fraud.status, CheckStatus.FAIL)
        self.assertTrue(any("PAN SEMANTIC MISMATCH" in r for r in res_fraud.reasons))
        print(f"[Test Checksums] Mismatched PAN Surname: Status = {res_fraud.status}, Reason = {res_fraud.reasons[0]}")

    def test_dl_and_voter_id(self):
        # Valid DL: DL0420180012345
        res_dl = self.engine.evaluate("driving_licence", "DL0420180012345")
        self.assertEqual(res_dl.status, CheckStatus.PASS)
        self.assertEqual(res_dl.details["state"], "DL")

        # Invalid State Code DL: ZZ0420180012345
        res_dl_inv = self.engine.evaluate("driving_licence", "ZZ0420180012345")
        self.assertEqual(res_dl_inv.status, CheckStatus.FAIL)

        # Valid Voter ID: ABC1234567
        res_epic = self.engine.evaluate("voter_id", "ABC1234567")
        self.assertEqual(res_epic.status, CheckStatus.PASS)


if __name__ == "__main__":
    unittest.main()
