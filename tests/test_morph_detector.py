"""
Unit Test for Module 14: Face Morphing & Synthetic Artifact Detector
"""
import unittest
import numpy as np
from PIL import Image, ImageFilter
from satyashield.models.morph_detector import FaceMorphDetector
from satyashield.core.types import CheckStatus


class TestFaceMorphDetector(unittest.TestCase):
    def setUp(self):
        self.detector = FaceMorphDetector()

    def test_natural_face_texture_passes(self):
        # Create image with natural micro-texture
        arr = np.random.normal(128, 15, (128, 128)).clip(0, 255).astype(np.uint8)
        img = Image.fromarray(arr)

        mod_res = self.detector.evaluate(img)
        self.assertEqual(mod_res.status, CheckStatus.PASS)
        self.assertGreater(mod_res.details["pore_entropy"], 2.0)
        print(f"\n[Test Morph Detector] Natural Texture: Status = {mod_res.status}, Entropy = {mod_res.details['pore_entropy']}, Time = {mod_res.execution_time_ms:.2f}ms")

    def test_overly_smooth_morph_detected(self):
        # Create an unnaturally smooth, featureless surface simulating heavy blend morph
        arr = np.full((128, 128), 128, dtype=np.uint8)
        smooth_img = Image.fromarray(arr)

        mod_res = self.detector.evaluate(smooth_img)
        self.assertEqual(mod_res.status, CheckStatus.FAIL)
        self.assertLess(mod_res.details["pore_entropy"], 1.0)
        self.assertTrue(any("SYNTHETIC BLENDING DETECTED" in r for r in mod_res.reasons))
        print(f"[Test Morph Detector] Synthetic Smooth Morph: Status = {mod_res.status}, Entropy = {mod_res.details['pore_entropy']}")


if __name__ == "__main__":
    unittest.main()
