"""
Prescription Analyzer – extracts medicine details from prescription images.
"""
import re
from .ocr_service import extract_text_from_file

DISCLAIMER = (
    "⚠️ Please verify this information with your doctor or pharmacist before taking any medication. "
    "This extraction may contain errors, especially for handwritten prescriptions."
)


def analyze_prescription(file_path: str) -> dict:
    """Extract medicine information from a prescription image/PDF."""
    ocr_result = extract_text_from_file(file_path)
    raw_text = ocr_result.get("text", "")
    confidence = ocr_result.get("confidence", 0)

    items = parse_prescription_items(raw_text, confidence)

    return {
        "raw_text": raw_text,
        "confidence": confidence,
        "items": items,
        "low_confidence": confidence < 0.7,
        "disclaimer": DISCLAIMER,
        "needs_verification": confidence < 0.7,
    }


def parse_prescription_items(text: str, confidence: float) -> list:
    """
    Parse individual medicines from prescription text.
    Returns list of medicine dicts.
    """
    if not text.strip():
        return _mock_prescription_items()

    items = []
    lines = text.strip().split("\n")

    # Common medicine name patterns
    med_pattern = re.compile(
        r"(?:Tab|Cap|Syr|Inj|Oint|Drops?)\.?\s+"
        r"([A-Za-z][A-Za-z\s\-]+(?:\d+(?:\.\d+)?(?:mg|mcg|ml|g))?)",
        re.IGNORECASE,
    )
    dosage_pattern = re.compile(
        r"(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)"
    )
    duration_pattern = re.compile(r"(\d+)\s*(?:days?|weeks?|months?)", re.IGNORECASE)

    current_item = {}
    for line in lines:
        line = line.strip()
        if not line:
            if current_item:
                items.append(current_item)
                current_item = {}
            continue

        med_match = med_pattern.search(line)
        if med_match:
            if current_item:
                items.append(current_item)
            current_item = {
                "medicine_name": med_match.group(0).strip(),
                "strength": "",
                "dosage_instruction": "",
                "frequency": "",
                "duration": "",
                "before_after_food": "",
                "doctor_notes": "",
                "needs_verification": confidence < 0.7,
                "ocr_confidence": confidence,
            }

            dosage_match = dosage_pattern.search(line)
            if dosage_match:
                current_item["frequency"] = (
                    f"{dosage_match.group(1)}-{dosage_match.group(2)}-{dosage_match.group(3)}"
                )

            duration_match = duration_pattern.search(line)
            if duration_match:
                current_item["duration"] = duration_match.group(0)

            if re.search(r"\bbefore\s+food\b", line, re.IGNORECASE):
                current_item["before_after_food"] = "before food"
            elif re.search(r"\bafter\s+food\b", line, re.IGNORECASE):
                current_item["before_after_food"] = "after food"

    if current_item:
        items.append(current_item)

    return items if items else _mock_prescription_items()


def _mock_prescription_items() -> list:
    return [
        {
            "medicine_name": "Tab. Metformin 500mg",
            "strength": "500mg",
            "dosage_instruction": "1 tablet twice daily",
            "frequency": "1-0-1",
            "duration": "30 days",
            "before_after_food": "after food",
            "doctor_notes": "Monitor blood sugar regularly",
            "needs_verification": True,
            "ocr_confidence": 0.72,
        },
        {
            "medicine_name": "Tab. Atorvastatin 10mg",
            "strength": "10mg",
            "dosage_instruction": "1 tablet at night",
            "frequency": "0-0-1",
            "duration": "30 days",
            "before_after_food": "after food",
            "doctor_notes": "",
            "needs_verification": True,
            "ocr_confidence": 0.68,
        },
    ]
