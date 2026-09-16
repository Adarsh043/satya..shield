"""
Unit Test for Module 4: Perceptual Hashing & Deduplication Engine
"""
import unittest
import io
from PIL import Image, ImageDraw
from satyashield.models.perceptual_hash import PerceptualHasher
from satyashield.core.types import CheckStatus


class TestPerceptualHasher(unittest.TestCase):
    def setUp(self):
        self.hasher = PerceptualHasher()

    def make_doc(self, title: str, bg_color=(240, 244, 248)) -> Image.Image:
        img = Image.new("RGB", (600, 380), color=bg_color)
        draw = ImageDraw.Draw(img)
        draw.rectangle([20, 20, 580, 360], outline=(15, 23, 42), width=2)
        draw.text((50, 50), title, fill=(15, 23, 42))
        return img

    def test_phash_computation_speed_and_format(self):
        doc = self.make_doc("PASSPORT REPUBLIC OF INDIA")
        phash = self.hasher.compute_phash(doc)
        dhash = self.hasher.compute_dhash(doc)
        self.assertEqual(len(phash), 16)
        self.assertEqual(len(dhash), 16)
        print(f"\n[Test Hash] pHash = {phash}, dHash = {dhash}")

    def test_recompression_robustness(self):
        doc1 = self.make_doc("AADHAAR CARD - GOVERNMENT OF INDIA")
        # Save as high-compression JPEG to simulate mobile/WhatsApp upload
        buf = io.BytesIO()
        doc1.save(buf, format="JPEG", quality=45)
        buf.seek(0)
        doc2_compressed = Image.open(buf)

        h1 = self.hasher.compute_phash(doc1)
        h2 = self.hasher.compute_phash(doc2_compressed)
        dist = self.hasher.hamming_distance(h1, h2)
        print(f"[Test Hash] Distance between uncompressed and 45% JPEG: {dist}")
        self.assertLessEqual(dist, 4)

    def test_unrelated_documents_have_high_distance(self):
        # Doc 1: Aadhaar Layout (Top red/blue tricolor stripe, photo on left, large QR on right)
        doc1 = Image.new("RGB", (600, 380), color=(255, 255, 255))
        d1 = ImageDraw.Draw(doc1)
        d1.rectangle([0, 0, 600, 50], fill=(255, 153, 51))  # Saffron header
        d1.rectangle([40, 80, 180, 260], fill=(50, 50, 50))  # Left photo box
        d1.rectangle([400, 120, 550, 270], fill=(0, 0, 0))   # Right QR code box

        # Doc 2: PAN Card Layout (Uniform cyan background, header on top, photo on bottom right, signature bar)
        doc2 = Image.new("RGB", (600, 380), color=(180, 220, 240))
        d2 = ImageDraw.Draw(doc2)
        d2.rectangle([50, 20, 550, 60], fill=(20, 40, 100))  # Dark blue header
        d2.rectangle([420, 80, 550, 240], fill=(80, 80, 80)) # Right photo box
        d2.rectangle([100, 280, 350, 340], fill=(255, 255, 255)) # Signature strip

        h1 = self.hasher.compute_phash(doc1)
        h2 = self.hasher.compute_phash(doc2)
        dist = self.hasher.hamming_distance(h1, h2)
        print(f"[Test Hash] Distance between Aadhaar and PAN: {dist}")
        self.assertGreater(dist, 15)

    def test_fraud_ring_blacklist_detection(self):
        doc = self.make_doc("LEAKED FORGED ID CARD #999")
        bad_hash = self.hasher.compute_phash(doc)
        
        # Test evaluation with blacklist
        blacklist = {bad_hash, "0123456789abcdef"}
        mod_res, match = self.hasher.evaluate(doc, known_fraud_hashes=blacklist)
        self.assertEqual(mod_res.status, CheckStatus.FAIL)
        self.assertTrue(any("FRAUD RING DETECTED" in r for r in mod_res.reasons))
        print(f"[Test Hash] Blacklist match: Status = {mod_res.status}, Reason = {mod_res.reasons[0]}")


if __name__ == "__main__":
    unittest.main()
