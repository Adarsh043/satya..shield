"""
Unit Test for Module 1: Pre-Flight Intake & Quality Gatekeeper
"""
import unittest
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from satyashield.models.preflight import PreflightGatekeeper
from satyashield.core.types import CheckStatus


class TestPreflightGatekeeper(unittest.TestCase):
    def setUp(self):
        self.gatekeeper = PreflightGatekeeper()

    def create_synthetic_id(self, w=800, h=500, text="REPUBLIC OF INDIA / PASSPORT") -> Image.Image:
        """Generates a clean synthetic ID card with sharp text and borders."""
        img = Image.new("RGB", (w, h), color=(240, 244, 248))
        draw = ImageDraw.Draw(img)
        # Add high-contrast text and geometric structures
        draw.rectangle([20, 20, w-20, h-20], outline=(15, 23, 42), width=3)
        draw.rectangle([40, 60, 200, 260], fill=(71, 85, 105), outline=(15, 23, 42), width=2)
        # Mock text lines
        for y in range(60, 400, 30):
            draw.text((230, y), f"{text} LINE {y}", fill=(15, 23, 42))
        return img

    def test_sharp_clean_document_passes(self):
        img = self.create_synthetic_id()
        preflight_res, mod_res, normalized = self.gatekeeper.evaluate(img)
        self.assertTrue(preflight_res.is_valid)
        self.assertEqual(mod_res.status, CheckStatus.PASS)
        self.assertGreater(preflight_res.blur_score, 100.0)
        self.assertLess(preflight_res.glare_ratio, 0.05)
        self.assertIsNotNone(normalized)
        print(f"\n[Test Preflight] Sharp Clean Image: Time = {mod_res.execution_time_ms:.2f}ms, Blur = {preflight_res.blur_score:.1f}, Status = {mod_res.status}")

    def test_blurry_document_fails(self):
        img = self.create_synthetic_id()
        # Apply heavy Gaussian Blur simulating out-of-focus camera
        blurred = img.filter(ImageFilter.GaussianBlur(radius=8))
        preflight_res, mod_res, normalized = self.gatekeeper.evaluate(blurred)
        self.assertFalse(preflight_res.is_valid)
        self.assertEqual(mod_res.status, CheckStatus.FAIL)
        self.assertLess(preflight_res.blur_score, 100.0)
        self.assertIn("too blurry", preflight_res.reasons[0])
        print(f"[Test Preflight] Blurry Image: Time = {mod_res.execution_time_ms:.2f}ms, Blur = {preflight_res.blur_score:.1f}, Status = {mod_res.status}")

    def test_glare_washout_fails(self):
        img = self.create_synthetic_id()
        draw = ImageDraw.Draw(img)
        # Simulate blinding flash reflection covering 25% of card
        draw.ellipse([100, 50, 600, 450], fill=(255, 255, 255))
        preflight_res, mod_res, normalized = self.gatekeeper.evaluate(img)
        self.assertFalse(preflight_res.is_valid)
        self.assertEqual(mod_res.status, CheckStatus.FAIL)
        self.assertGreater(preflight_res.glare_ratio, 0.18)
        self.assertTrue(any("glare" in r for r in preflight_res.reasons))
        print(f"[Test Preflight] Glare Image: Time = {mod_res.execution_time_ms:.2f}ms, Glare = {preflight_res.glare_ratio*100:.1f}%, Status = {mod_res.status}")

    def test_low_resolution_fails(self):
        tiny_img = Image.new("RGB", (150, 100), color=(200, 200, 200))
        preflight_res, mod_res, normalized = self.gatekeeper.evaluate(tiny_img)
        self.assertFalse(preflight_res.is_valid)
        self.assertEqual(mod_res.status, CheckStatus.FAIL)
        self.assertTrue(any("Resolution" in r for r in preflight_res.reasons))
        print(f"[Test Preflight] Low-Res Image: Time = {mod_res.execution_time_ms:.2f}ms, Res = {preflight_res.resolution}, Status = {mod_res.status}")


if __name__ == "__main__":
    unittest.main()
