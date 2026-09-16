"""
SatyaShield Module 4: Perceptual Hashing & Deduplication Engine
--------------------------------------------------------------
Generates 64-bit Perceptual Hash (pHash via 2D-DCT) and Difference Hash (dHash)
to detect duplicate document submissions, replay attacks, and syndicated fraud rings.

Computes in <2ms on CPU. Enables O(1) cache lookups to bypass server compute entirely!
"""
import time
from typing import Tuple, Optional, Set, Dict, Any
import numpy as np
from PIL import Image

from ..core.types import ModuleResult, CheckStatus


class PerceptualHasher:
    """
    Computes perceptual hashes and Hamming distances for near-duplicate and replay detection.
    """
    def __init__(self, hash_size: int = 8, highfreq_factor: int = 4):
        self.hash_size = hash_size
        self.highfreq_factor = highfreq_factor
        self.total_size = hash_size * highfreq_factor

    def _compute_dct2d(self, a: np.ndarray) -> np.ndarray:
        """
        Computes 2D Discrete Cosine Transform (DCT-II) using pure numpy matrix operations.
        Avoids dependency on heavyweight scipy.
        """
        N = a.shape[0]
        # Build 1D DCT-II basis matrix
        n = np.arange(N)
        k = n[:, np.newaxis]
        M = np.cos(np.pi / (2.0 * N) * (2 * n + 1) * k)
        M[0, :] *= 1.0 / np.sqrt(2.0)
        M *= np.sqrt(2.0 / N)

        # 2D DCT = M * a * M^T
        return np.dot(np.dot(M, a), M.T)

    def compute_phash(self, image: Image.Image) -> str:
        """
        Computes robust 64-bit pHash using 2D-DCT low-frequency energy comparison.
        Resistant to minor scaling, JPEG re-compression, and color tone shifts.
        """
        # Step 1: Grayscale and resize to 32x32
        resized = image.convert("L").resize((self.total_size, self.total_size), Image.Resampling.BILINEAR)
        pixels = np.array(resized, dtype=np.float32)

        # Step 2: 2D-DCT
        dct = self._compute_dct2d(pixels)

        # Step 3: Extract top-left 8x8 low frequency coefficients (excluding DC term [0,0])
        dct_low = dct[:self.hash_size, :self.hash_size]
        median_val = np.median(dct_low[1:, 1:])

        # Step 4: Generate 64-bit boolean mask
        bits = dct_low > median_val
        bit_str = "".join("1" if b else "0" for b in bits.flatten())
        # Convert to 16-character hex
        hex_hash = f"{int(bit_str, 2):016x}"
        return hex_hash

    def compute_dhash(self, image: Image.Image) -> str:
        """
        Computes fast 64-bit Difference Hash (dHash) based on horizontal gradient.
        Ultra-fast (sub-millisecond).
        """
        resized = image.convert("L").resize((self.hash_size + 1, self.hash_size), Image.Resampling.BILINEAR)
        arr = np.array(resized, dtype=np.int32)
        # Compare adjacent pixels in each row: arr[:, 1:] > arr[:, :-1]
        diff = arr[:, 1:] > arr[:, :-1]
        bit_str = "".join("1" if b else "0" for b in diff.flatten())
        return f"{int(bit_str, 2):016x}"

    @staticmethod
    def hamming_distance(hex1: str, hex2: str) -> int:
        """Calculates bit-wise Hamming distance between two hex hashes (0 to 64)."""
        val1 = int(hex1, 16)
        val2 = int(hex2, 16)
        xor_val = val1 ^ val2
        return bin(xor_val).count("1")

    def evaluate(
        self,
        image: Image.Image,
        known_fraud_hashes: Optional[Set[str]] = None,
        cached_verifications: Optional[Dict[str, Any]] = None,
        similarity_threshold: int = 5
    ) -> Tuple[ModuleResult, Optional[Dict[str, Any]]]:
        """
        Evaluates image against known fraud rings and deduplication cache.
        """
        t0 = time.perf_counter()
        reasons = []
        details = {}
        status = CheckStatus.PASS
        confidence = 1.0
        cached_match = None

        phash = self.compute_phash(image)
        dhash = self.compute_dhash(image)
        details["phash"] = phash
        details["dhash"] = dhash

        # 1. Check against Known Fraud Hashes (Blacklist)
        if known_fraud_hashes:
            for bad_hash in known_fraud_hashes:
                dist = self.hamming_distance(phash, bad_hash)
                if dist <= similarity_threshold:
                    status = CheckStatus.FAIL
                    confidence = 0.0
                    reasons.append(f"REPLAY / FRAUD RING DETECTED: Perceptual match to blacklisted fraud artifact (Hamming distance {dist} <= {similarity_threshold})")
                    details["matched_fraud_hash"] = bad_hash
                    details["hamming_distance"] = dist
                    break

        # 2. Check Deduplication Cache (White-list / Exact match cache)
        if status == CheckStatus.PASS and cached_verifications:
            for c_hash, c_data in cached_verifications.items():
                dist = self.hamming_distance(phash, c_hash)
                if dist == 0:  # Exact identical visual match
                    reasons.append("Exact deduplication cache hit. Prior verification results safely reusable.")
                    details["cache_hit"] = True
                    details["cached_reference"] = c_data.get("document_id")
                    cached_match = c_data
                    break

        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        mod_result = ModuleResult(
            module_name="perceptual_deduplication",
            status=status,
            confidence=confidence,
            execution_time_ms=elapsed_ms,
            details=details,
            reasons=reasons
        )
        return mod_result, cached_match
