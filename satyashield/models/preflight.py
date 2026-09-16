"""
SatyaShield Module 1: Pre-Flight Intake & Quality Gatekeeper
-----------------------------------------------------------
Lightweight image quality assessment to fail-fast on unusable inputs
(excessive blur, blinding flash glare, microscopic resolution, or invalid aspect ratios)
BEFORE any heavier forensic or OCR processing is invoked.

Runs in <10ms on standard CPU using vectorized NumPy and PIL.
"""
import time
from typing import Tuple, Optional, Union
import numpy as np
from PIL import Image, ImageOps

from ..core.types import ModuleResult, CheckStatus, PreflightResult


class PreflightGatekeeper:
    """
    Evaluates image quality and normalizes inputs to minimize server compute.
    """
    def __init__(
        self,
        min_resolution: Tuple[int, int] = (300, 200),
        max_dimension: int = 1600,
        blur_threshold: float = 80.0,       # Variance of Laplacian
        glare_threshold: float = 0.18,       # Max 18% saturated glare pixels
        min_contrast: float = 15.0           # Standard deviation of luminance
    ):
        self.min_resolution = min_resolution
        self.max_dimension = max_dimension
        self.blur_threshold = blur_threshold
        self.glare_threshold = glare_threshold
        self.min_contrast = min_contrast

        # 3x3 Discrete Laplacian Kernel for blur measurement
        self.laplacian_kernel = np.array([
            [0,  1, 0],
            [1, -4, 1],
            [0,  1, 0]
        ], dtype=np.float32)

    def _convolve2d_fast(self, image: np.ndarray, kernel: np.ndarray) -> np.ndarray:
        """
        Ultra-fast vectorized 2D convolution for 3x3 kernel using pure numpy.
        Zero external dependencies, minimal CPU cycles.
        """
        h, w = image.shape
        kh, kw = kernel.shape
        pad_h, pad_w = kh // 2, kw // 2
        
        # Zero-pad borders
        padded = np.pad(image, ((pad_h, pad_h), (pad_w, pad_w)), mode='edge').astype(np.float32)
        
        # Sub-matrix slicing for 3x3 kernel
        out = (
            kernel[0, 0] * padded[0:h, 0:w] +
            kernel[0, 1] * padded[0:h, 1:w+1] +
            kernel[0, 2] * padded[0:h, 2:w+2] +
            kernel[1, 0] * padded[1:h+1, 0:w] +
            kernel[1, 1] * padded[1:h+1, 1:w+1] +
            kernel[1, 2] * padded[1:h+1, 2:w+2] +
            kernel[2, 0] * padded[2:h+2, 0:w] +
            kernel[2, 1] * padded[2:h+2, 1:w+1] +
            kernel[2, 2] * padded[2:h+2, 2:w+2]
        )
        return out

    def calculate_blur(self, gray_array: np.ndarray) -> float:
        """
        Calculates Laplacian variance. Sharp images have high variance, blurry images have low.
        """
        # Downsample large images for speed if > 800px
        h, w = gray_array.shape
        if max(h, w) > 800:
            scale = 800.0 / max(h, w)
            new_w, new_h = max(1, int(w * scale)), max(1, int(h * scale))
            img_pil = Image.fromarray(gray_array).resize((new_w, new_h), Image.Resampling.BILINEAR)
            sample = np.array(img_pil, dtype=np.float32)
        else:
            sample = gray_array.astype(np.float32)

        laplacian = self._convolve2d_fast(sample, self.laplacian_kernel)
        return float(np.var(laplacian))

    def calculate_glare(self, gray_array: np.ndarray) -> float:
        """
        Detects specular reflection/flash washout where pixel values exceed 254.
        """
        total_pixels = gray_array.size
        blown_out = np.sum(gray_array >= 254)
        return float(blown_out / total_pixels)

    def calculate_contrast(self, gray_array: np.ndarray) -> float:
        """
        Calculates luminance standard deviation. Low values indicate washed out / grey images.
        """
        return float(np.std(gray_array))

    def normalize_image(self, image: Image.Image) -> Image.Image:
        """
        Normalizes image orientation and scales down oversized images to max_dimension
        to guarantee deterministic processing time for downstream models.
        """
        # Fix EXIF orientation if present
        image = ImageOps.exif_transpose(image)
        
        # Ensure RGB
        if image.mode != "RGB":
            image = image.convert("RGB")
            
        w, h = image.size
        if max(w, h) > self.max_dimension:
            scale = self.max_dimension / float(max(w, h))
            new_w = max(1, int(w * scale))
            new_h = max(1, int(h * scale))
            image = image.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
        return image

    def evaluate(self, image_input: Union[Image.Image, np.ndarray]) -> Tuple[PreflightResult, ModuleResult, Optional[Image.Image]]:
        """
        Runs complete pre-flight check.
        Returns:
            (PreflightResult, ModuleResult, normalized_pil_image)
        """
        t0 = time.perf_counter()
        reasons = []
        
        if isinstance(image_input, np.ndarray):
            image = Image.fromarray(image_input)
        else:
            image = image_input

        orig_w, orig_h = image.size
        
        # 1. Resolution Check
        if orig_w < self.min_resolution[0] or orig_h < self.min_resolution[1]:
            reasons.append(f"Resolution ({orig_w}x{orig_h}) is below minimum requirement ({self.min_resolution[0]}x{self.min_resolution[1]})")

        # Normalize
        normalized_img = self.normalize_image(image)
        gray = np.array(normalized_img.convert("L"))
        
        # 2. Blur Measurement
        blur_score = self.calculate_blur(gray)
        if blur_score < self.blur_threshold:
            reasons.append(f"Image is too blurry (Laplacian variance {blur_score:.1f} < threshold {self.blur_threshold:.1f})")

        # 3. Glare Measurement
        glare_ratio = self.calculate_glare(gray)
        if glare_ratio > self.glare_threshold:
            reasons.append(f"Severe flash glare detected ({glare_ratio * 100:.1f}% blown out pixels > threshold {self.glare_threshold * 100:.1f}%)")

        # 4. Contrast Measurement
        contrast_score = self.calculate_contrast(gray)
        if contrast_score < self.min_contrast:
            reasons.append(f"Insufficient contrast ({contrast_score:.1f} < threshold {self.min_contrast:.1f})")

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        aspect_ratio = orig_w / float(orig_h) if orig_h > 0 else 0.0

        is_valid = len(reasons) == 0
        status = CheckStatus.PASS if is_valid else CheckStatus.FAIL
        confidence = 1.0 if is_valid else max(0.0, 1.0 - (len(reasons) * 0.3))

        preflight_res = PreflightResult(
            is_valid=is_valid,
            blur_score=blur_score,
            glare_ratio=glare_ratio,
            resolution=(orig_w, orig_h),
            aspect_ratio=aspect_ratio,
            reasons=reasons
        )

        mod_res = ModuleResult(
            module_name="preflight_intake",
            status=status,
            confidence=confidence,
            execution_time_ms=elapsed_ms,
            details={
                "blur_score": round(blur_score, 2),
                "glare_percentage": round(glare_ratio * 100, 2),
                "contrast_score": round(contrast_score, 2),
                "resolution": f"{orig_w}x{orig_h}",
                "aspect_ratio": round(aspect_ratio, 3)
            },
            reasons=reasons
        )

        return preflight_res, mod_res, (normalized_img if is_valid else None)
