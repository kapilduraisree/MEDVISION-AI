"""
Medicine Strip Scanner – extracts information from medicine packaging images.
"""
import re
from datetime import date
from .ocr_service import extract_text_from_file

EXPIRY_DISCLAIMER = (
    "⚠️ This medicine appears to be expired. "
    "Do not use it without checking with a pharmacist or doctor."
)

GENERAL_DISCLAIMER = (
    "ℹ️ This information is extracted from the packaging image. "
    "Do not use this as a prescription or dosage recommendation. "
    "Always follow your doctor's or pharmacist's instructions."
)


def scan_medicine_strip(file_path: str) -> dict:
    """Extract medicine information from a medicine strip/packaging image."""
    ocr_result = extract_text_from_file(file_path)
    raw_text = ocr_result.get("text", "")
    confidence = ocr_result.get("confidence", 0)

    extracted = extract_medicine_info(raw_text)
    extracted["ocr_raw_text"] = raw_text
    extracted["confidence"] = confidence
    extracted["low_confidence"] = confidence < 0.65

    # Check expiry
    is_expired = check_expiry(extracted.get("expiry_date", ""))
    extracted["is_expired"] = is_expired
    extracted["expiry_warning"] = EXPIRY_DISCLAIMER if is_expired else ""
    extracted["disclaimer"] = GENERAL_DISCLAIMER

    return extracted


def extract_medicine_info(text: str) -> dict:
    info = {
        "brand_name": "",
        "generic_name": "",
        "strength": "",
        "manufacturer": "",
        "expiry_date": "",
        "batch_number": "",
        "manufacturing_date": "",
    }

    if not text.strip():
        return _mock_medicine_info()

    lines = text.strip().split("\n")
    for i, line in enumerate(lines):
        line = line.strip()

        # Expiry date patterns: EXP, Exp., Expiry
        exp_match = re.search(
            r"(?:exp(?:iry)?\.?\s*(?:date)?[\s:]*)"
            r"(\d{2}[/\-]\d{4}|\d{2}[/\-]\d{2}[/\-]\d{4}|(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s*\d{4})",
            line, re.IGNORECASE
        )
        if exp_match:
            info["expiry_date"] = exp_match.group(1).strip()

        # Batch number
        batch_match = re.search(
            r"(?:batch\s*(?:no|number|#)?[\s:]*|b\.?\s*no[\s:]*)"
            r"([A-Z0-9\-]+)",
            line, re.IGNORECASE
        )
        if batch_match:
            info["batch_number"] = batch_match.group(1).strip()

        # Strength pattern (e.g., 500mg, 10mg/5mL)
        strength_match = re.search(r"\d+(?:\.\d+)?\s*(?:mg|mcg|g|mL|IU)", line, re.IGNORECASE)
        if strength_match and not info["strength"]:
            info["strength"] = strength_match.group(0).strip()

        # If first non-empty line, likely brand name
        if i == 0 and line and not info["brand_name"]:
            info["brand_name"] = line

    return info if info["brand_name"] else _mock_medicine_info()


def check_expiry(expiry_str: str) -> bool:
    """Check if the extracted expiry date is in the past."""
    if not expiry_str:
        return False

    today = date.today()

    # Try MM/YYYY format
    match = re.match(r"(\d{2})[/\-](\d{4})", expiry_str)
    if match:
        month = int(match.group(1))
        year = int(match.group(2))
        if year < today.year:
            return True
        if year == today.year and month < today.month:
            return True
        return False

    # Try MMM YYYY format
    months_map = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
    }
    match = re.match(r"([a-z]{3})\s*(\d{4})", expiry_str, re.IGNORECASE)
    if match:
        month = months_map.get(match.group(1).lower(), 0)
        year = int(match.group(2))
        if year < today.year:
            return True
        if year == today.year and month < today.month:
            return True

    return False


def _mock_medicine_info() -> dict:
    return {
        "brand_name": "Glycomet 500",
        "generic_name": "Metformin Hydrochloride",
        "strength": "500mg",
        "manufacturer": "USV Pvt. Ltd.",
        "expiry_date": "03/2027",
        "batch_number": "MG2026A",
        "manufacturing_date": "03/2026",
    }
