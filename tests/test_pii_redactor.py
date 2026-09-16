"""
Unit Test for Module 7: PII Redactor & Legal Compliance Engine
"""
import unittest
import numpy as np
from PIL import Image
from satyashield.models.pii_redactor import PIIRedactor
from satyashield.core.types import CheckStatus


class TestPIIRedactor(unittest.TestCase):
    def setUp(self):
        self.redactor = PIIRedactor()

    def test_mask_string_and_token(self):
        raw_aadhaar = "4567 8901 2348"
        masked = self.redactor.mask_aadhaar_string(raw_aadhaar)
        self.assertEqual(masked, "XXXX-XXXX-2348")

        token1 = self.redactor.generate_blind_index_token(raw_aadhaar)
        token2 = self.redactor.generate_blind_index_token("456789012348")
        # Ensure spaces don't affect hash token
        self.assertEqual(token1, token2)
        self.assertEqual(len(token1), 64)
        print(f"\n[Test PII Redactor] Masked string: {masked}, Blind token: {token1[:16]}...")

    def test_evaluate_and_image_redaction(self):
        fields = {"name": "Arun Sharma", "aadhaar_number": "987654321098"}
        # Create white image
        img = Image.new("RGB", (600, 400), color=(255, 255, 255))
        
        mod_res, sanitized, redacted_img = self.redactor.evaluate(fields, img)
        self.assertEqual(mod_res.status, CheckStatus.PASS)
        self.assertNotIn("aadhaar_number", sanitized)
        self.assertEqual(sanitized["masked_aadhaar"], "XXXX-XXXX-1098")
        self.assertIsNotNone(redacted_img)
        
        # Verify the redacted area on image is blacked out (pixels == (10, 10, 10))
        arr = np.array(redacted_img)
        # Check center of box: x = 0.3 * 600 = 180, y = 0.8 * 400 = 320
        self.assertEqual(list(arr[320, 180]), [10, 10, 10])
        print(f"[Test PII Redactor] Image redacted successfully, execution time = {mod_res.execution_time_ms:.3f}ms")


if __name__ == "__main__":
    unittest.main()
