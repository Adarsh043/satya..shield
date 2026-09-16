"""
Unit Test for Module 10: 2D-FFT Frequency Forensics
"""
import unittest
import numpy as np
from PIL import Image, ImageDraw
from satyashield.models.fft_forensics import FFTFrequencyForensics
from satyashield.core.types import CheckStatus


class TestFFTFrequencyForensics(unittest.TestCase):
    def setUp(self):
        self.forensics = FFTFrequencyForensics()

    def test_natural_document_spectrum(self):
        # Create a natural smooth document with standard text
        img = Image.new("RGB", (500, 350), color=(245, 245, 240))
        draw = ImageDraw.Draw(img)
        draw.rectangle([30, 30, 470, 320], outline=(40, 40, 40), width=2)
        draw.text((60, 60), "REPUBLIC OF INDIA - IDENTITY PASSPORT", fill=(20, 20, 20))
        draw.text((60, 100), "OFFICIAL CANONICAL RECORD", fill=(20, 20, 20))

        mod_res = self.forensics.evaluate(img)
        self.assertEqual(mod_res.status, CheckStatus.PASS)
        self.assertLess(mod_res.execution_time_ms, 100.0)
        print(f"\n[Test 2D-FFT] Natural document: Status = {mod_res.status}, Grid Ratio = {mod_res.details['grid_anomaly_ratio']}, Time = {mod_res.execution_time_ms:.2f}ms")

    def test_synthetic_periodic_tamper_artifact(self):
        # Create an image with an artificial high-frequency grid (resampling artifact)
        arr = np.zeros((256, 256), dtype=np.uint8)
        # Inject strong periodic vertical stripes every 4 pixels
        arr[:, ::4] = 255
        img = Image.fromarray(arr)

        mod_res = self.forensics.evaluate(img)
        self.assertEqual(mod_res.status, CheckStatus.WARNING)
        self.assertGreater(mod_res.details["grid_anomaly_ratio"], 3.0)
        print(f"[Test 2D-FFT] Tampered Periodic Grid: Status = {mod_res.status}, Grid Ratio = {mod_res.details['grid_anomaly_ratio']}")


if __name__ == "__main__":
    unittest.main()
