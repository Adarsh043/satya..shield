"""
Unit Test for Module 9: Micro-Typography & Font Consistency Forensics
"""
import unittest
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from satyashield.models.micro_typography import MicroTypographyForensics
from satyashield.core.types import CheckStatus


class TestMicroTypographyForensics(unittest.TestCase):
    def setUp(self):
        self.forensics = MicroTypographyForensics()

    def test_clean_authentic_text_line(self):
        # Create a clean text line with perfect baseline
        img = Image.new("RGB", (400, 60), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        draw.text((20, 20), "ARUN KUMAR SHARMA", fill=(0, 0, 0))

        mod_res = self.forensics.evaluate(img)
        self.assertEqual(mod_res.status, CheckStatus.PASS)
        self.assertGreater(mod_res.details["baseline_contrast"], 0.25)
        print(f"\n[Test Micro-Typography] Clean text: Status = {mod_res.status}, Contrast = {mod_res.details['baseline_contrast']}, Time = {mod_res.execution_time_ms:.2f}ms")

    def test_spliced_tampered_text_anomaly(self):
        # Create a tampered text line where letters are jaggedly pasted at different heights with noise
        img = Image.new("RGB", (400, 60), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        # Jittered letters
        for i, char in enumerate("VIKRAM SINGH"):
            y_offset = 15 + (i % 3) * 12  # Jagged baselines
            draw.text((20 + i * 28, y_offset), char, fill=(0, 0, 0))
            # Paste noisy border around each character simulating bad photoshop cutoff
            draw.rectangle([20 + i * 28 - 2, y_offset - 2, 20 + i * 28 + 22, y_offset + 22], outline=(120, 120, 120))

        mod_res = self.forensics.evaluate(img)
        print(f"[Test Micro-Typography] Tampered text: Status = {mod_res.status}, Stroke Energy = {mod_res.details['stroke_edge_energy']}, Details = {mod_res.details}")
        # Either fails or flags high stroke edge energy
        self.assertGreater(mod_res.details["stroke_edge_energy"], 1000.0)


if __name__ == "__main__":
    unittest.main()
