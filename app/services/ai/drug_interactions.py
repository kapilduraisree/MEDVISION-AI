"""
Drug Interactions Checker - checks safety of medicine combinations.
Uses a curated knowledge base; can be extended with external API.
"""
from app.core.config import settings

INTERACTION_DB = {
    ("warfarin", "aspirin"): {
        "severity": "major",
        "effect": "Significantly increased bleeding risk. Both drugs inhibit clotting through different mechanisms.",
        "action": "Avoid combination unless under close medical supervision. Monitor INR frequently.",
    },
    ("metformin", "alcohol"): {
        "severity": "major",
        "effect": "Risk of lactic acidosis, a rare but serious condition.",
        "action": "Avoid alcohol while taking metformin.",
    },
    ("simvastatin", "amlodipine"): {
        "severity": "moderate",
        "effect": "Amlodipine can increase simvastatin blood levels, raising risk of muscle damage.",
        "action": "Limit simvastatin dose to 20mg/day when used with amlodipine.",
    },
    ("lisinopril", "potassium"): {
        "severity": "moderate",
        "effect": "ACE inhibitors like lisinopril can raise potassium levels; potassium supplements worsen this.",
        "action": "Monitor potassium levels regularly.",
    },
    ("ciprofloxacin", "antacids"): {
        "severity": "moderate",
        "effect": "Antacids reduce absorption of ciprofloxacin by up to 90%.",
        "action": "Take ciprofloxacin 2 hours before or 6 hours after antacids.",
    },
    ("ssri", "tramadol"): {
        "severity": "major",
        "effect": "Risk of serotonin syndrome — potentially life-threatening.",
        "action": "Avoid combination. Consult your doctor for alternatives.",
    },
    ("methotrexate", "nsaids"): {
        "severity": "major",
        "effect": "NSAIDs reduce methotrexate excretion, increasing toxicity risk.",
        "action": "Use with extreme caution. Monitor methotrexate levels closely.",
    },
    ("clopidogrel", "omeprazole"): {
        "severity": "moderate",
        "effect": "Omeprazole reduces activation of clopidogrel, reducing its antiplatelet effect.",
        "action": "Consider alternative PPI such as pantoprazole if combination needed.",
    },
    ("levothyroxine", "calcium"): {
        "severity": "moderate",
        "effect": "Calcium supplements reduce levothyroxine absorption.",
        "action": "Take levothyroxine at least 4 hours apart from calcium.",
    },
    ("digoxin", "amiodarone"): {
        "severity": "major",
        "effect": "Amiodarone significantly raises digoxin levels, risking toxicity.",
        "action": "Reduce digoxin dose by 30-50% and monitor closely.",
    },
}

SEVERITY_COLORS = {
    "major": "🔴 Major",
    "moderate": "🟡 Moderate",
    "minor": "🟢 Minor",
    "no interaction": "✅ No known interaction",
}


def check_interactions(medicines: list) -> list:
    """
    Check all pairwise interactions for a list of medicine names.
    Returns list of interaction dicts.
    """
    results = []
    meds_lower = [m.lower().strip() for m in medicines]

    for i in range(len(meds_lower)):
        for j in range(i + 1, len(meds_lower)):
            a, b = meds_lower[i], meds_lower[j]
            interaction = _find_interaction(a, b)
            results.append({
                "drug_a": medicines[i],
                "drug_b": medicines[j],
                "severity": interaction.get("severity", "no interaction"),
                "severity_label": SEVERITY_COLORS.get(
                    interaction.get("severity", "no interaction"),
                    "✅ No known interaction"
                ),
                "effect": interaction.get("effect", "No known interaction found in database."),
                "action": interaction.get("action", "Continue as prescribed. Consult your doctor if concerned."),
                "found": interaction.get("severity") is not None,
            })
    return results


def _find_interaction(a: str, b: str) -> dict:
    """Look up interaction between two drug names (fuzzy match)."""
    for (k1, k2), info in INTERACTION_DB.items():
        if (k1 in a or a in k1) and (k2 in b or b in k2):
            return info
        if (k2 in a or a in k2) and (k1 in b or b in k1):
            return info
    return {}


def get_interaction_summary(interactions: list) -> dict:
    """Return counts by severity for a summary."""
    major = sum(1 for i in interactions if i.get("severity") == "major")
    moderate = sum(1 for i in interactions if i.get("severity") == "moderate")
    minor = sum(1 for i in interactions if i.get("severity") == "minor")
    none = sum(1 for i in interactions if not i.get("found"))
    return {"major": major, "moderate": moderate, "minor": minor, "none": none, "total": len(interactions)}
