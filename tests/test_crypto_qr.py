"""
Unit Test for Module 2: Cryptographic QR & Digital Signature Authenticator
"""
import unittest
import base64
import zlib
from satyashield.models.crypto_qr import CryptoQRAuthenticator
from satyashield.core.types import CheckStatus


class TestCryptoQRAuthenticator(unittest.TestCase):
    def setUp(self):
        self.auth = CryptoQRAuthenticator()

    def test_authentic_aadhaar_qr_passes_fast(self):
        qr_b64 = self.auth.generate_signed_aadhaar_qr(
            ref_id="4029202609131234",
            name="Rohan Sharma",
            dob="15-08-1995",
            gender="M",
            masked_aadhaar="XXXX-XXXX-9876"
        )
        mod_res, data = self.auth.decode_and_verify(qr_b64)
        self.assertEqual(mod_res.status, CheckStatus.PASS)
        self.assertLess(mod_res.execution_time_ms, 15.0)  # Must be fast
        self.assertIsNotNone(data)
        self.assertEqual(data["name"], "Rohan Sharma")
        self.assertEqual(data["masked_aadhaar"], "XXXX-XXXX-9876")
        self.assertTrue(data["cryptographically_verified"])
        print(f"\n[Test Crypto QR] Authentic Aadhaar QR: Time = {mod_res.execution_time_ms:.2f}ms, Status = {mod_res.status}, Name = {data['name']}")

    def test_tampered_aadhaar_qr_detected(self):
        # Attacker takes valid payload, uncompresses it, edits name, re-encodes without valid private key
        qr_b64 = self.auth.generate_signed_aadhaar_qr(
            ref_id="4029202609131234",
            name="Rohan Sharma",
            dob="15-08-1995",
            gender="M"
        )
        raw_bytes = base64.b64decode(qr_b64)
        decompressed = zlib.decompress(raw_bytes).decode("utf-8")
        tampered_text = decompressed.replace("Rohan Sharma", "Vikram Singh (Attacker)")
        tampered_b64 = base64.b64encode(zlib.compress(tampered_text.encode("utf-8"))).decode("ascii")

        mod_res, data = self.auth.decode_and_verify(tampered_b64)
        self.assertEqual(mod_res.status, CheckStatus.FAIL)
        self.assertIsNone(data)
        self.assertTrue(any("TAMPERING DETECTED" in r for r in mod_res.reasons))
        print(f"[Test Crypto QR] Tampered Aadhaar QR: Time = {mod_res.execution_time_ms:.2f}ms, Status = {mod_res.status}, Reason = {mod_res.reasons[0]}")

    def test_authentic_pan_qr_passes(self):
        pan_b64 = self.auth.generate_signed_pan_qr(
            pan_number="ABCDE1234F",
            name="PRIYA VERMA",
            father_name="ANIL VERMA",
            dob="22/11/1992"
        )
        mod_res, data = self.auth.decode_and_verify(pan_b64)
        self.assertEqual(mod_res.status, CheckStatus.PASS)
        self.assertIsNotNone(data)
        self.assertEqual(data["pan_number"], "ABCDE1234F")
        print(f"[Test Crypto QR] Authentic PAN QR: Time = {mod_res.execution_time_ms:.2f}ms, Status = {mod_res.status}, PAN = {data['pan_number']}")

    def test_tampered_pan_qr_fails(self):
        pan_b64 = self.auth.generate_signed_pan_qr(
            pan_number="ABCDE1234F",
            name="PRIYA VERMA",
            father_name="ANIL VERMA",
            dob="22/11/1992"
        )
        raw = base64.b64decode(pan_b64).decode("utf-8")
        tampered = raw.replace("ABCDE1234F", "XYZPQ9999Z")
        tampered_b64 = base64.b64encode(tampered.encode("utf-8")).decode("ascii")

        mod_res, data = self.auth.decode_and_verify(tampered_b64)
        self.assertEqual(mod_res.status, CheckStatus.FAIL)
        self.assertIsNone(data)
        print(f"[Test Crypto QR] Tampered PAN QR: Time = {mod_res.execution_time_ms:.2f}ms, Status = {mod_res.status}")


if __name__ == "__main__":
    unittest.main()
