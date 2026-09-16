"""
Unit Test for Module 5: Lightweight Document Classifier & Anchor Locator
"""
import unittest
import numpy as np
from PIL import Image, ImageDraw
from satyashield.models.doc_classifier import DocumentClassifier
from satyashield.core.types import DocumentType, CheckStatus


class TestDocumentClassifier(unittest.TestCase):
    def setUp(self):
        self.classifier = DocumentClassifier()

    def test_passport_mrz_classification(self):
        # Create Passport layout: 800x560 (ratio ~1.42), top emblem, bottom dense MRZ alternating stripes
        img = Image.new("RGB", (800, 560), color=(250, 248, 240))
        draw = ImageDraw.Draw(img)
        # Draw bottom MRZ stripes
        for x in range(20, 780, 10):
            draw.line([(x, 460), (x, 490)], fill=(0, 0, 0), width=3)
            draw.line([(x, 500), (x, 530)], fill=(0, 0, 0), width=3)

        doc_type, mod_res = self.classifier.classify(img)
        self.assertEqual(doc_type, DocumentType.PASSPORT)
        self.assertEqual(mod_res.status, CheckStatus.PASS)
        self.assertLess(mod_res.execution_time_ms, 20.0)
        print(f"\n[Test Classifier] Passport Detected: Type = {doc_type.value}, Time = {mod_res.execution_time_ms:.2f}ms")

    def test_pan_card_classification(self):
        # Create PAN card layout: 856x540 (ID-1 ratio), cyan tint (G & B > R)
        img = Image.new("RGB", (856, 540), color=(140, 200, 230))
        draw = ImageDraw.Draw(img)
        draw.rectangle([50, 40, 800, 80], fill=(20, 50, 120)) # Dark blue banner

        doc_type, mod_res = self.classifier.classify(img)
        self.assertEqual(doc_type, DocumentType.PAN_CARD)
        print(f"[Test Classifier] PAN Card Detected: Type = {doc_type.value}, Cyan Score = {mod_res.details['cyan_score']}")

    def test_aadhaar_front_with_qr(self):
        # Create Aadhaar layout: 856x540, white background with high-contrast QR noise on the right
        img = Image.new("RGB", (856, 540), color=(255, 255, 255))
        # Add high-variance random noise block on right simulating QR code
        qr_noise = np.random.randint(0, 256, (200, 200, 3), dtype=np.uint8)
        qr_pil = Image.fromarray(qr_noise)
        img.paste(qr_pil, (580, 180))

        doc_type, mod_res = self.classifier.classify(img)
        self.assertEqual(doc_type, DocumentType.AADHAAR_FRONT)
        print(f"[Test Classifier] Aadhaar Front Detected: Type = {doc_type.value}, QR Pos = {mod_res.details['qr_position']}")

    def test_text_hint_classification(self):
        img = Image.new("RGB", (856, 540), color=(240, 240, 240))
        doc_type, mod_res = self.classifier.classify(img, ocr_hint="GOVERNMENT OF INDIA DRIVING LICENCE UNION")
        self.assertEqual(doc_type, DocumentType.DRIVING_LICENCE)
        print(f"[Test Classifier] DL Detected via Hint: Type = {doc_type.value}")


if __name__ == "__main__":
    unittest.main()
