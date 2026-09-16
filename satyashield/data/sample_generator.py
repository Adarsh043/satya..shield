"""
SatyaShield Sample Document Generator
------------------------------------
Generates high-fidelity synthetic and realistic test cases representing
diverse online document types and attack vectors.
"""
from typing import Dict, Any, Tuple
import numpy as np
from PIL import Image, ImageDraw
from ..models.crypto_qr import CryptoQRAuthenticator
from ..models.checksums import ChecksumEngine


class SampleDocumentGenerator:
    """
    Produces standardized test fixtures covering genuine documents and attack vectors.
    """
    def __init__(self):
        self.crypto = CryptoQRAuthenticator()
        self.checksums = ChecksumEngine()

    def make_base_card(self, w=856, h=540, bg_color=(238, 242, 246)) -> Image.Image:
        img = Image.new("RGB", (w, h), color=bg_color)
        draw = ImageDraw.Draw(img)
        draw.rectangle([10, 10, w-10, h-10], outline=(160, 170, 180), width=2)
        return img

    def make_face_crop(self, w=160, h=200) -> Image.Image:
        """
        Generates a realistic synthetic human face portrait with authentic
        continuous shading, specular highlights, and skin pore micro-entropy.
        """
        img = Image.new("RGB", (w, h), color=(210, 215, 220))
        draw = ImageDraw.Draw(img)
        cx = w // 2

        # 3D gradient face oval
        for rad in range(60, 10, -5):
            tone = int(180 + (60 - rad) * 1.2)
            draw.ellipse([cx - rad, 30 + (60 - rad)//2, cx + rad, 160 - (60 - rad)//2], fill=(tone, tone - 25, tone - 45))

        # Eyes
        draw.ellipse([cx - 28, 75, cx - 14, 87], fill=(30, 20, 15))
        draw.ellipse([cx + 14, 75, cx + 28, 87], fill=(30, 20, 15))

        # Nose bridge
        draw.polygon([(cx, 80), (cx - 7, 105), (cx + 7, 105)], fill=(160, 120, 100))

        # Mouth
        draw.rectangle([cx - 18, 125, cx + 18, 134], fill=(150, 50, 50))

        # Specular highlight on forehead / nose
        draw.ellipse([cx - 10, 50, cx + 10, 68], fill=(250, 240, 230))
        draw.ellipse([cx - 3, 90, cx + 3, 102], fill=(245, 235, 225))

        # Add realistic micro-texture skin pore noise
        arr = np.array(img, dtype=np.float32)
        noise = np.random.normal(0, 4.0, arr.shape)
        noisy = np.clip(arr + noise, 0, 255).astype(np.uint8)
        return Image.fromarray(noisy)

    # --- 1. Authentic Aadhaar ---
    def generate_authentic_aadhaar(self) -> Tuple[Image.Image, str, str, Image.Image, Dict[str, Any]]:
        card = self.make_base_card()
        draw = ImageDraw.Draw(card)
        w, h = card.size

        # Tricolor header bar
        draw.rectangle([10, 10, w-10, 45], fill=(255, 153, 51)) # Saffron
        draw.rectangle([10, 45, w-10, 55], fill=(255, 255, 255)) # White
        draw.rectangle([10, 55, w-10, 65], fill=(19, 136, 8))   # Green
        draw.text((w//2 - 120, 20), "GOVERNMENT OF INDIA - UIDAI", fill=(0, 0, 0))

        # Photo on left (matches ROI photo fraction 0.05..0.28, 0.25..0.72)
        # 0.05 * 856 = 42.8, 0.25 * 540 = 135
        face = self.make_face_crop(160, 200)
        card.paste(face, (42, 135))

        # Text fields
        name = "KAVITA PATEL"
        dob = "12/08/1994"
        gender = "FEMALE"
        base_num = "34567890123"
        chk = self.checksums.calculate_verhoeff_checksum(base_num)
        aadhaar_num = f"{base_num}{chk}"

        draw.text((240, 140), f"Name: {name}", fill=(15, 23, 42))
        draw.text((240, 180), f"DOB: {dob}", fill=(15, 23, 42))
        draw.text((240, 220), f"Gender: {gender}", fill=(15, 23, 42))
        draw.text((240, 280), f"{aadhaar_num[:4]} {aadhaar_num[4:8]} {aadhaar_num[8:]}", fill=(15, 23, 42))

        # QR code on right
        qr_noise = np.random.randint(0, 256, (180, 180, 3), dtype=np.uint8)
        card.paste(Image.fromarray(qr_noise), (600, 135))

        qr_b64 = self.crypto.generate_signed_aadhaar_qr(
            ref_id="4029202609139999",
            name=name,
            dob="12-08-1994",
            gender="F",
            masked_aadhaar=f"XXXX-XXXX-{aadhaar_num[-4:]}"
        )

        ocr_text = f"GOVERNMENT OF INDIA\n{name}\nDOB: {dob}\n{gender}\n{aadhaar_num}"
        meta = {"document_number": aadhaar_num, "name": name, "dob": dob}
        return card, qr_b64, ocr_text, face, meta

    # --- 2. Forged Aadhaar (Name tampered + Invalid Checksum) ---
    def generate_forged_aadhaar(self) -> Tuple[Image.Image, str, str, Image.Image, Dict[str, Any]]:
        card, qr_b64, ocr_text, face, meta = self.generate_authentic_aadhaar()
        orig_num = meta["document_number"]
        bad_num = orig_num[:-1] + ("0" if orig_num[-1] != "0" else "1")
        
        forged_name = "VIKRAM KHANNA"
        ocr_text_forged = f"GOVERNMENT OF INDIA\n{forged_name}\nDOB: 12/08/1994\nFEMALE\n{bad_num}"
        meta_forged = {"document_number": bad_num, "name": forged_name, "dob": "12/08/1994"}
        return card, qr_b64, ocr_text_forged, face, meta_forged

    # --- 3. Authentic PAN Card ---
    def generate_authentic_pan(self) -> Tuple[Image.Image, str, str, Image.Image, Dict[str, Any]]:
        card = self.make_base_card(bg_color=(160, 210, 235)) # Cyan Income Tax palette
        draw = ImageDraw.Draw(card)
        w, h = card.size

        # Top banner
        draw.rectangle([10, 10, w-10, 60], fill=(20, 50, 120))
        draw.text((w//2 - 140, 25), "INCOME TAX DEPARTMENT - GOVT. OF INDIA", fill=(255, 255, 255))

        # Photo (ROI: 0.04 * 856 = 34, 0.20 * 540 = 108)
        face = self.make_face_crop(160, 200)
        card.paste(face, (36, 110))

        pan_num = "ABCPS1234F"
        name = "RAHUL SHARMA"
        fname = "RAMESH SHARMA"
        dob = "24/09/1991"

        draw.text((220, 100), f"PAN: {pan_num}", fill=(10, 20, 60))
        draw.text((220, 140), f"Name: {name}", fill=(10, 20, 60))
        draw.text((220, 180), f"Father's Name: {fname}", fill=(10, 20, 60))
        draw.text((220, 220), f"DOB: {dob}", fill=(10, 20, 60))

        qr_b64 = self.crypto.generate_signed_pan_qr(pan_num, name, fname, dob)
        ocr_text = f"INCOME TAX DEPARTMENT\n{pan_num}\n{name}\n{fname}\n{dob}"
        meta = {"document_number": pan_num, "surname": "Sharma", "name": name}
        return card, qr_b64, ocr_text, face, meta

    # --- 4. Forged PAN Card (Mismatched 5th character) ---
    def generate_forged_pan_mismatch(self) -> Tuple[Image.Image, str, str, Image.Image, Dict[str, Any]]:
        card, qr_b64, ocr_text, face, meta = self.generate_authentic_pan()
        bad_pan = "ABCPK1234F"
        ocr_bad = ocr_text.replace("ABCPS1234F", bad_pan)
        meta_bad = {"document_number": bad_pan, "surname": "Sharma", "name": "RAHUL SHARMA"}
        return card, qr_b64, ocr_bad, face, meta_bad

    # --- 5. Authentic Passport ---
    def generate_authentic_passport(self) -> Tuple[Image.Image, str, str, Image.Image, Dict[str, Any]]:
        w, h = 800, 560
        passport_page = Image.new("RGB", (w, h), color=(240, 238, 230))
        draw = ImageDraw.Draw(passport_page)

        draw.rectangle([20, 20, w-20, h-20], outline=(140, 130, 120), width=2)
        draw.text((w//2 - 100, 35), "PASSPORT - REPUBLIC OF INDIA", fill=(30, 30, 30))

        # Photo at (35, 135)
        face = self.make_face_crop(160, 200)
        passport_page.paste(face, (35, 135))

        pass_num = "Z1234567<"
        pass_chk = self.checksums.calculate_mrz_check_digit(pass_num)
        dob = "920514"
        dob_chk = self.checksums.calculate_mrz_check_digit(dob)
        exp = "320513"
        exp_chk = self.checksums.calculate_mrz_check_digit(exp)

        mrz_line1 = "P<INDVERMA<<ANANYA<<<<<<<<<<<<<<<<<<<<<<<<<<"
        mrz_line2 = f"{pass_num}{pass_chk}IND{dob}{dob_chk}F{exp}{exp_chk}<<<<<<<<<<<<<<<4"
        mrz_line2 = mrz_line2.ljust(44, '<')

        draw.text((40, 460), mrz_line1, fill=(0, 0, 0))
        draw.text((40, 495), mrz_line2, fill=(0, 0, 0))

        ocr_text = f"PASSPORT REPUBLIC OF INDIA\n{mrz_line1}\n{mrz_line2}"
        meta = {"document_number": "Z1234567", "mrz_line2": mrz_line2, "name": "ANANYA VERMA"}
        return passport_page, "", ocr_text, face, meta

    # --- 6. Forged Spliced Photo ID ---
    def generate_spliced_photo_attack(self) -> Tuple[Image.Image, str, str, Image.Image, Dict[str, Any]]:
        card, qr_b64, ocr_text, face, meta = self.generate_authentic_aadhaar()
        # Paste stark alien black box creating extreme step boundary
        alien_box = Image.new("RGB", (160, 200), color=(10, 10, 10))
        card.paste(alien_box, (42, 135))
        return card, qr_b64, ocr_text, alien_box, meta
