"""
Unit Test for Module 6: ROI Extractor & Text Normalizer
"""
import unittest
from PIL import Image
from satyashield.models.roi_extractor import ROIExtractor
from satyashield.core.types import DocumentType, CheckStatus


class TestROIExtractor(unittest.TestCase):
    def setUp(self):
        self.extractor = ROIExtractor()

    def test_cropping_rois(self):
        img = Image.new("RGB", (1000, 600), color=(255, 255, 255))
        rois = self.extractor.crop_rois(img, DocumentType.AADHAAR_FRONT)
        self.assertIn("photo", rois)
        self.assertIn("id_number", rois)
        self.assertIn("qr_code", rois)
        # Check photo dimensions
        self.assertEqual(rois["photo"].size[0], int(0.195 * 1000))
        print(f"\n[Test ROI Extractor] Cropped ROIs successfully: {list(rois.keys())}")

    def test_parsing_noisy_ocr_text(self):
        noisy_aadhaar_text = """
        GOVERNMENT OF INDIA
        MERA AADHAAR MERI PEHCHAN
        To
        Arun Kumar Sharma
        DOB: 14/05/1988
        Male
        Your Aadhaar No. :
        4567 8901 2348
        1947
        """
        parsed = self.extractor.parse_raw_text(noisy_aadhaar_text, DocumentType.AADHAAR_FRONT)
        self.assertEqual(parsed.get("aadhaar_number"), "456789012348")
        self.assertEqual(parsed.get("dob"), "14/05/1988")
        self.assertEqual(parsed.get("gender"), "MALE")
        print(f"[Test ROI Extractor] Parsed Aadhaar OCR text: {parsed}")

    def test_parsing_pan_ocr_text(self):
        pan_text = """
        INCOME TAX DEPARTMENT
        GOVT. OF INDIA
        Permanent Account Number Card
        ABCPK1234D
        Name: ROHIT KAPOOR
        Father's Name: SURESH KAPOOR
        Date of Birth: 25/12/1990
        """
        parsed = self.extractor.parse_raw_text(pan_text, DocumentType.PAN_CARD)
        self.assertEqual(parsed.get("pan_number"), "ABCPK1234D")
        self.assertEqual(parsed.get("dob"), "25/12/1990")
        print(f"[Test ROI Extractor] Parsed PAN OCR text: {parsed}")


if __name__ == "__main__":
    unittest.main()
