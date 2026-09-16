"""
Unit Test for Module 11: Photo Boundary & Splicing Detector
"""
import unittest
import numpy as np
from PIL import Image, ImageDraw
from satyashield.models.photo_splicing import PhotoSplicingDetector
from satyashield.core.types import CheckStatus


class TestPhotoSplicingDetector(unittest.TestCase):
    def setUp(self):
        self.detector = PhotoSplicingDetector()

    def test_continuous_authentic_portrait(self):
        # Create a document with smoothly blended photo
        doc = Image.new("RGB", (600, 400), color=(230, 235, 240))
        draw = ImageDraw.Draw(doc)
        # Draw photo box with natural subtle gradient (soft border)
        draw.rectangle([30, 100, 168, 288], fill=(210, 215, 220), outline=(180, 185, 190))

        mod_res = self.detector.evaluate(doc, photo_box_fraction=(0.05, 0.25, 0.28, 0.72))
        self.assertEqual(mod_res.status, CheckStatus.PASS)
        self.assertLess(mod_res.details["step_gradient"], 50.0)
        print(f"\n[Test Photo Splicing] Authentic portrait: Status = {mod_res.status}, Step Gradient = {mod_res.details['step_gradient']}, Time = {mod_res.execution_time_ms:.2f}ms")

    def test_spliced_alien_photo_detected(self):
        # Create document with white background, and paste a stark black/high-contrast rectangle (extreme step gradient)
        doc = Image.new("RGB", (600, 400), color=(255, 255, 255))
        draw = ImageDraw.Draw(doc)
        # Paste solid dark box simulating cut-and-paste photo
        draw.rectangle([30, 100, 168, 288], fill=(10, 10, 10))

        mod_res = self.detector.evaluate(doc, photo_box_fraction=(0.05, 0.25, 0.28, 0.72))
        self.assertEqual(mod_res.status, CheckStatus.FAIL)
        self.assertGreater(mod_res.details["step_gradient"], 85.0)
        self.assertTrue(any("PORTRAIT SPLICING DETECTED" in r for r in mod_res.reasons))
        print(f"[Test Photo Splicing] Spliced portrait: Status = {mod_res.status}, Step Gradient = {mod_res.details['step_gradient']}, Reason = {mod_res.reasons[0]}")


if __name__ == "__main__":
    unittest.main()
