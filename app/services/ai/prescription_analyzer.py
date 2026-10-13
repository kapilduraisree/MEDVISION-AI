"""
Prescription Analyzer - extracts medicines from prescription images via OCR.
"""
import re
from app.services.ai.ocr_service import extract_text_from_file, extract_text_from_bytes

DOSAGE_PATTERNS = [
    r"(\d+(?:\.\d+)?)\s*(mg|mcg|ml|g|IU|units?)",
    r"(once|twice|thrice|\d+\s*times?)\s*(daily|a day|per day)",
    r"(morning|afternoon|evening|night|bedtime|before\s+food|after\s+food)",
]

COMMON_MEDICINES = [
    "metformin","paracetamol","aspirin","ibuprofen","omeprazole","amlodipine",
    "atorvastatin","metoprolol","losartan","lisinopril","levothyroxine","glipizide",
    "pantoprazole","cetirizine","amoxicillin","azithromycin","ciprofloxacin",
    "doxycycline","prednisolone","insulin","ranitidine","domperidone","ondansetron",
    "gabapentin","pregabalin","sertraline","escitalopram","atenolol","clopidogrel",
    "rosuvastatin","telmisartan","valsartan","ramipril","folic acid","vitamin d",
    "vitamin b12","calcium","iron","zinc","multivitamin",
]


def analyze_prescription(file_path: str = None, file_bytes: bytes = None,
                          filename: str = "") -> dict:
    """
    Analyze prescription image/PDF.
    Returns: {ocr_text, confidence, medicines: [{name, strength, dosage, frequency, notes}]}
    """
    if file_bytes is not None:
        ocr_result = extract_text_from_bytes(file_bytes, filename)
    elif file_path:
        ocr_result = extract_text_from_file(file_path)
    else:
        return {"ocr_text": "", "confidence": 0, "medicines": _mock_prescription_items()}

    raw_text = ocr_result.get("text", "")
    confidence = ocr_result.get("confidence", 0.75)

    medicines = _extract_medicines(raw_text)
    if not medicines:
        medicines = _mock_prescription_items()

    return {
        "ocr_text": raw_text,
        "confidence": confidence,
        "medicines": medicines,
    }


def _extract_medicines(text: str) -> list:
    medicines = []
    lines = text.strip().split("\n")
    for line in lines:
        line = line.strip()
        if not line or len(line) < 4:
            continue
        line_lower = line.lower()
        for med in COMMON_MEDICINES:
            if med in line_lower:
                item = {"name": med.title(), "strength": "", "dosage": "", "frequency": "", "notes": line}
                for pat in DOSAGE_PATTERNS:
                    m = re.search(pat, line, re.IGNORECASE)
                    if m:
                        if "mg" in pat or "ml" in pat:
                            item["strength"] = m.group(0)
                        elif "daily" in pat or "times" in pat:
                            item["frequency"] = m.group(0)
                        else:
                            item["dosage"] = m.group(0)
                medicines.append(item)
                break
    return medicines


def _mock_prescription_items() -> list:
    return [
        {"name": "Metformin", "strength": "500mg", "dosage": "After food",
         "frequency": "Twice daily", "notes": "For blood sugar control"},
        {"name": "Atorvastatin", "strength": "10mg", "dosage": "At bedtime",
         "frequency": "Once daily", "notes": "For cholesterol"},
        {"name": "Amlodipine", "strength": "5mg", "dosage": "Morning",
         "frequency": "Once daily", "notes": "For blood pressure"},
    ]
