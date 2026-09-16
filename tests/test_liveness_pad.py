"""
Unit Test for Module 13: Presentation Attack Detection (PAD) & Liveness
"""
import unittest
import numpy as np
from PIL import Image, ImageDraw
from satyashield.models.liveness_pad import LivenessPADDetector
from satyashield.core.types import CheckStatus


class TestLivenessPADDetector(unittest.TestCase):
    def setUp(self):
        self.pad = LivenessPADDetector()

    def test_authentic_live_selfie_passes(self):
        # Create image with natural 3D skin gradient and highlights
        img = Image.new("RGB", (128, 128), color=(200, 160, 140))
        draw = ImageDraw.Draw(img)
        # Specular nose/forehead highlights
        draw.ellipse([50, 40, 78, 65], fill=(250, 240, 230))
        draw.ellipse([30, 80, 98, 120], fill=(120, 80, 60)) # Shadow under chin

        mod_res = self.pad.evaluate(img)
        self.assertEqual(mod_res.status, CheckStatus.PASS)
        self.assertFalse(mod_res.details["screen_attack_flag"])
        print(f"\n[Test Liveness PAD] Live 3D Selfie: Status = {mod_res.status}, Dyn Range = {mod_res.details['dynamic_range']}, Time = {mod_res.execution_time_ms:.2f}ms")

    def test_screen_replay_attack_detected(self):
        # Create image with LCD/OLED subpixel grid ripple (high frequency moire fringe)
        arr = np.zeros((128, 128), dtype=np.uint8)
        # Inject periodic raster grid every 4 pixels
        arr[::4, :] = 255
        arr[:, ::4] = 255
        screen_img = Image.fromarray(arr).convert("RGB")

        mod_res = self.pad.evaluate(screen_img)
        self.assertEqual(mod_res.status, CheckStatus.FAIL)
        self.assertTrue(mod_res.details["screen_attack_flag"])
        self.assertTrue(any("PRESENTATION ATTACK DETECTED" in r for r in mod_res.reasons))
        print(f"[Test Liveness PAD] Screen Replay Spoof: Status = {mod_res.status}, Moiré = {mod_res.details['moire_ratio']}")

    def test_flat_paper_printout_detected(self):
        # Create flat washed out uniform paper image (dynamic range < 40)
        arr = np.full((128, 128, 3), 180, dtype=np.uint8)
        # Minimal variance (+- 5)
        noise = np.random.randint(-5, 5, (128, 128, 3), dtype=np.int16)
        flat_img = Image.fromarray(np.clip(arr + noise, 0, 255).astype(np.uint8))

        mod_res = self.pad.evaluate(flat_img)
        self.assertEqual(mod_res.status, CheckStatus.FAIL)
        self.assertTrue(mod_res.details["paper_attack_flag"])
        print(f"[Test Liveness PAD] Flat Paper Print Spoof: Status = {mod_res.status}, Dyn Range = {mod_res.details['dynamic_range']}")


if __name__ == "__main__":
    unittest.main()
