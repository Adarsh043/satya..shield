"""
SatyaShield Module 8: Cross-Field Consistency Correlator
--------------------------------------------------------
Correlates visual OCR fields, cryptographically certified QR payload,
and ICAO MRZ records to catch visual Photoshop forgeries, name substitutions,
and age/DOB modifications.

Uses normalized Levenshtein distance and structured date reconciliation.
Executes in <1ms on CPU.
"""
import time
from typing import Dict, Any, Tuple, List, Optional
from ..core.types import ModuleResult, CheckStatus


class CrossFieldValidator:
    """
    Multi-source reconciliation and tamper correlator.
    """
    @staticmethod
    def levenshtein_similarity(s1: str, s2: str) -> float:
        """
        Computes normalized Levenshtein similarity ratio between 0.0 (unrelated) and 1.0 (identical).
        """
        a = s1.strip().upper()
        b = s2.strip().upper()
        if not a and not b:
            return 1.0
        if not a or not b:
            return 0.0
        if a == b:
            return 1.0

        len_a, len_b = len(a), len(b)
        dp = [[0] * (len_b + 1) for _ in range(len_a + 1)]

        for i in range(len_a + 1):
            dp[i][0] = i
        for j in range(len_b + 1):
            dp[0][j] = j

        for i in range(1, len_a + 1):
            for j in range(1, len_b + 1):
                cost = 0 if a[i - 1] == b[j - 1] else 1
                dp[i][j] = min(
                    dp[i - 1][j] + 1,        # deletion
                    dp[i][j - 1] + 1,        # insertion
                    dp[i - 1][j - 1] + cost   # substitution
                )

        dist = dp[len_a][len_b]
        max_len = max(len_a, len_b)
        return float(1.0 - (dist / max_len))

    @staticmethod
    def normalize_date(date_str: str) -> str:
        """Standardizes various date formats (DD/MM/YYYY, DD-MM-YYYY, YYYY-MM-DD, YYMMDD) to YYYYMMDD."""
        clean = "".join(c for c in date_str if c.isalnum())
        if len(clean) == 8:
            # Check if DDMMYYYY or YYYYMMDD
            if int(clean[:2]) <= 31 and int(clean[2:4]) <= 12 and int(clean[4:]) > 1900:
                # DDMMYYYY -> YYYYMMDD
                return f"{clean[4:]}{clean[2:4]}{clean[:2]}"
            return clean
        elif len(clean) == 6:
            # YYMMDD (MRZ format)
            yy = int(clean[:2])
            century = "19" if yy > 30 else "20"
            return f"{century}{clean}"
        return clean

    def evaluate(
        self,
        visual_fields: Dict[str, Any],
        qr_fields: Optional[Dict[str, Any]] = None,
        mrz_fields: Optional[Dict[str, Any]] = None
    ) -> ModuleResult:
        """
        Cross-examines all sources of evidence.
        """
        t0 = time.perf_counter()
        reasons = []
        discrepancies = []
        matches = []
        confidence = 1.0

        # --- 1. Visual OCR vs. Cryptographic QR ---
        if qr_fields and qr_fields.get("cryptographically_verified"):
            # Check Name
            vis_name = visual_fields.get("name", "")
            qr_name = qr_fields.get("name", "")
            if vis_name and qr_name:
                sim = self.levenshtein_similarity(vis_name, qr_name)
                if sim < 0.80:
                    discrepancies.append(
                        f"CRITICAL NAME MISMATCH: Visual text displays '{vis_name}' but certified QR contains '{qr_name}' (similarity: {sim:.2f})"
                    )
                else:
                    matches.append(f"Name matched between visual OCR and QR ({sim:.2f})")

            # Check DOB
            vis_dob = visual_fields.get("dob", "")
            qr_dob = qr_fields.get("dob", "")
            if vis_dob and qr_dob:
                norm_vis = self.normalize_date(vis_dob)
                norm_qr = self.normalize_date(qr_dob)
                if norm_vis != norm_qr:
                    discrepancies.append(
                        f"DOB TAMPERING DETECTED: Visual DOB '{vis_dob}' conflicts with certified QR DOB '{qr_dob}'"
                    )
                else:
                    matches.append("DOB perfectly reconciled with QR")

            # Check Aadhaar masked ID
            vis_id = visual_fields.get("aadhaar_number") or visual_fields.get("masked_aadhaar", "")
            qr_id = qr_fields.get("masked_aadhaar", "")
            if vis_id and qr_id:
                vis_last4 = vis_id[-4:]
                qr_last4 = qr_id[-4:]
                if vis_last4 != qr_last4:
                    discrepancies.append(
                        f"ID NUMBER MISMATCH: Visual ending digits '{vis_last4}' != QR certified ending '{qr_last4}'"
                    )

        # --- 2. Visual OCR vs. MRZ Fields (Passports) ---
        if mrz_fields:
            vis_pass = visual_fields.get("passport_number", "")
            mrz_pass = mrz_fields.get("passport_number", "")
            if vis_pass and mrz_pass:
                if vis_pass.upper().replace("<", "") != mrz_pass.upper().replace("<", ""):
                    discrepancies.append(
                        f"PASSPORT NUMBER TAMPER: Visual '{vis_pass}' != MRZ '{mrz_pass}'"
                    )

            vis_dob = visual_fields.get("dob", "")
            mrz_dob = mrz_fields.get("dob", "")
            if vis_dob and mrz_dob:
                norm_vis = self.normalize_date(vis_dob)
                norm_mrz = self.normalize_date(mrz_dob)
                if norm_vis != norm_mrz:
                    discrepancies.append(
                        f"PASSPORT DOB MISMATCH: Visual '{vis_dob}' != MRZ '{mrz_dob}'"
                    )

        # --- 3. Profile vs. Document OCR ---
        claimed_name = visual_fields.get("claimed_name", "")
        extracted_name = visual_fields.get("name", "")
        
        if not claimed_name:
            discrepancies.append("IDENTITY MISMATCH: Profile name is completely missing. Cannot verify document.")
        elif not extracted_name:
            discrepancies.append(
                f"IDENTITY MISMATCH: Could not read any name from the document to verify against profile name '{claimed_name}'. OCR extraction failed."
            )
        else:
            sim = self.levenshtein_similarity(claimed_name, extracted_name)
            if sim < 0.6:
                discrepancies.append(
                    f"IDENTITY MISMATCH: Profile name '{claimed_name}' does not match document name '{extracted_name}'"
                )
            else:
                matches.append(f"Profile name verified against document (similarity {sim*100:.0f}%)")

        claimed_dob = visual_fields.get("claimed_dob", "")
        extracted_dob = visual_fields.get("dob", "")
        
        if not claimed_dob:
            discrepancies.append("DOB MISMATCH: Profile DOB is completely missing. Cannot verify document.")
        elif not extracted_dob:
            discrepancies.append(
                f"DOB MISMATCH: Could not read any Date of Birth from the document to verify against profile DOB '{claimed_dob}'. OCR extraction failed."
            )
        else:
            norm_claimed = self.normalize_date(claimed_dob)
            norm_extracted = self.normalize_date(extracted_dob)
            if norm_claimed != norm_extracted:
                discrepancies.append(
                    f"DOB MISMATCH: Profile DOB '{claimed_dob}' does not match document DOB '{extracted_dob}'"
                )
            else:
                matches.append("Profile DOB perfectly verified against document OCR")

        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        if discrepancies:
            status = CheckStatus.FAIL
            confidence = 0.0
            reasons.extend(discrepancies)
        else:
            status = CheckStatus.PASS
            confidence = 1.0
            reasons.extend(matches or ["No cross-field conflicts observed."])

        return ModuleResult(
            module_name="cross_field_correlator",
            status=status,
            confidence=confidence,
            execution_time_ms=elapsed_ms,
            details={
                "discrepancies": discrepancies,
                "matches": matches,
                "total_comparisons": len(discrepancies) + len(matches)
            },
            reasons=reasons
        )
