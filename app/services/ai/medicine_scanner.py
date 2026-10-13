"""
Medicine Scanner - scans medicine strip/packaging images for expiry and drug info.
"""
import re
from app.services.ai.ocr_service import extract_text_from_file, extract_text_from_bytes

EXPIRY_PATTERNS = [
    r"(?:exp(?:iry)?|expiration|use\s+by|best\s+before)[\s:]*(\d{2}[/\-]\d{4}|\d{2}[/\-]\d{2}[/\-]\d{2,4})",
    r"(?:mfg|manufactured|mfd|dom)[\s:]*(\w+\s+\d{4}|\d{2}[/\-]\d{4})",
    r"\b(0[1-9]|1[0-2])[/\-](20\d{2})\b",
]

BATCH_PATTERNS = [
    r"(?:batch|lot|b\.?no|b/n)[\s:]*([A-Z0-9\-]+)",
    r"\b([A-Z]{2,3}\d{4,8})\b",
]

MRP_PATTERNS = [
    r"(?:mrp|m\.r\.p|price|rs\.?)[\s:]*[\u20B9$]?\s*(\d+(?:\.\d{2})?)",
    r"[\u20B9$]\s*(\d+(?:\.\d{2})?)",
]


def scan_medicine_strip(file_path: str = None, file_bytes: bytes = None,
                        filename: str = "") -> dict:
    """
    Scan medicine packaging image for drug info.
    Returns dict with medicine_name, expiry_date, batch_no, mrp, raw_text.
    """
    if file_bytes is not None:
        ocr_result = extract_text_from_bytes(file_bytes, filename)
    elif file_path:
        ocr_result = extract_text_from_file(file_path)
    else:
        return _mock_scan_result()

    raw_text = ocr_result.get("text", "")
    confidence = ocr_result.get("confidence", 0.75)

    result = {
        "raw_text": raw_text,
        "ocr_confidence": confidence,
        "medicine_name": _extract_medicine_name(raw_text),
        "expiry_date": _extract_expiry(raw_text),
        "batch_no": _extract_batch(raw_text),
        "mrp": _extract_mrp(raw_text),
        "is_mock": False,
    }

    if not result["medicine_name"] and not result["expiry_date"]:
        mock = _mock_scan_result()
        mock["raw_text"] = raw_text
        mock["ocr_confidence"] = confidence
        return mock

    return result


def _extract_medicine_name(text: str) -> str:
    lines = [l.strip() for l in text.split("\n") if l.strip() and len(l.strip()) > 3]
    for line in lines[:5]:
        if re.search(r"[A-Za-z]{4,}", line) and not re.search(r"\d{4}", line):
            return line[:80]
    return ""


def _extract_expiry(text: str) -> str:
    text_lower = text.lower()
    for pattern in EXPIRY_PATTERNS:
        m = re.search(pattern, text_lower, re.IGNORECASE)
        if m:
            return m.group(1) if m.lastindex else m.group(0)
    return ""


def _extract_batch(text: str) -> str:
    for pattern in BATCH_PATTERNS:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            return m.group(1)
    return ""


def _extract_mrp(text: str) -> str:
    for pattern in MRP_PATTERNS:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            return f"₹{m.group(1)}"
    return ""


def _mock_scan_result() -> dict:
    return {
        "raw_text": "METFORMIN HCl 500mg\nBatch No: MF240901\nMfg: Jan 2024\nExp: 12/2026\nMRP: ₹45.00",
        "ocr_confidence": 0.85,
        "medicine_name": "Metformin HCl 500mg",
        "expiry_date": "12/2026",
        "batch_no": "MF240901",
        "mrp": "₹45.00",
        "is_mock": True,
    }


def check_expiry_status(expiry_str: str) -> dict:
    """Check if a medicine is expired, expiring soon, or valid."""
    import re
    from datetime import datetime

    if not expiry_str:
        return {"status": "unknown", "message": "Expiry date not found"}

    now = datetime.now()
    m = re.search(r"(\d{1,2})[/\-](\d{4})", expiry_str)
    if m:
        try:
            month, year = int(m.group(1)), int(m.group(2))
            from datetime import date
            exp_date = date(year, month, 1)
            today = now.date()
            diff = (exp_date.year - today.year) * 12 + (exp_date.month - today.month)
            if diff < 0:
                return {"status": "expired", "message": f"⛔ EXPIRED: {expiry_str}"}
            elif diff <= 3:
                return {"status": "expiring_soon", "message": f"⚠️ Expiring soon: {expiry_str}"}
            else:
                return {"status": "valid", "message": f"✅ Valid until: {expiry_str}"}
        except Exception:
            pass
    return {"status": "unknown", "message": f"Could not parse expiry: {expiry_str}"}
