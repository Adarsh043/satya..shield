"""
Unit Test for Module 12: Biometric Face Verifier
"""
import unittest
import numpy as np
from PIL import Image, ImageDraw
from satyashield.models.face_verifier import FaceVerifier
from satyashield.core.types import CheckStatus


class TestFaceVerifier(unittest.TestCase):
    def setUp(self):
        self.verifier = FaceVerifier(match_threshold=0.75)

    def generate_face(self, eye_spacing=30, nose_y=55, mouth_y=80) -> Image.Image:
        """Generates a synthetic face layout with distinct biometric coordinates."""
        img = Image.new("RGB", (120, 140), color=(220, 190, 170))
        draw = ImageDraw.Draw(img)
        # Face oval
        draw.ellipse([15, 10, 105, 130], fill=(235, 205, 185))
        # Eyes
        cx = 60
        draw.ellipse([cx - eye_spacing - 6, 40, cx - eye_spacing + 6, 50], fill=(40, 20, 10)) # Left eye
        draw.ellipse([cx + eye_spacing - 6, 40, cx + eye_spacing + 6, 50], fill=(40, 20, 10)) # Right eye
        # Nose
        draw.polygon([(cx, 48), (cx - 6, nose_y), (cx + 6, nose_y)], fill=(180, 150, 130))
        # Mouth
        draw.rectangle([cx - 18, mouth_y, cx + 18, mouth_y + 8], fill=(160, 60, 60))
        return img

    def test_same_person_high_match(self):
        face1 = self.generate_face(eye_spacing=25, nose_y=60, mouth_y=85)
        # Same person with slight illumination shift (slight gamma change)
        face2 = face1.point(lambda p: int(p * 0.92))

        mod_res, is_match = self.verifier.verify(face1, face2)
        self.assertTrue(is_match)
        self.assertEqual(mod_res.status, CheckStatus.PASS)
        self.assertGreater(mod_res.details["similarity_score"], 0.90)
        print(f"\n[Test Face Matcher] Same Person: Status = {mod_res.status}, Similarity = {mod_res.details['similarity_score']}, Time = {mod_res.execution_time_ms:.2f}ms")

    def test_different_person_mismatch(self):
        face_person_a = self.generate_face(eye_spacing=18, nose_y=50, mouth_y=75)
        face_person_b = self.generate_face(eye_spacing=38, nose_y=75, mouth_y=105)

        mod_res, is_match = self.verifier.verify(face_person_a, face_person_b)
        self.assertFalse(is_match)
        self.assertEqual(mod_res.status, CheckStatus.FAIL)
        self.assertLess(mod_res.details["similarity_score"], 0.75)
        print(f"[Test Face Matcher] Different Person: Status = {mod_res.status}, Similarity = {mod_res.details['similarity_score']}")


if __name__ == "__main__":
    unittest.main()
