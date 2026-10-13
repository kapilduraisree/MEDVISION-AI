"""
MedVision AI – Live Medical Data Service
Fetches real-time drug and interaction data from free public APIs.

APIs used (no API key required):
  1. OpenFDA Drug API        https://api.fda.gov/drug/label.json
     → drug labeling, warnings, dosage, side effects, contraindications
  2. RxNorm API              https://rxnav.nlm.nih.gov/REST/
     → drug name normalisation, concept lookup
  3. RxNorm Interaction API  https://rxnav.nlm.nih.gov/REST/interaction/
     → pairwise drug interaction lookup by RxCUI
  4. OpenFDA Drug Event API  https://api.fda.gov/drug/event.json
     → adverse event counts for a drug

All responses are cached in st.session_state to avoid repeated network calls.
Cache TTL: 30 minutes per unique query.
"""
from __future__ import annotations
import time
from typing import Optional

import httpx
import streamlit as st

_OPENFDA_LABEL   = "https://api.fda.gov/drug/label.json"
_OPENFDA_EVENT   = "https://api.fda.gov/drug/event.json"
_RXNORM_BASE     = "https://rxnav.nlm.nih.gov/REST"
_TIMEOUT         = 8.0   # seconds
_CACHE_TTL       = 1800  # 30 minutes

# ── Cache helpers ─────────────────────────────────────────────────────────────

def _cache_get(key: str):
    store = st.session_state.get("live_data_cache", {})
    entry = store.get(key)
    if entry and (time.time() - entry["ts"]) < _CACHE_TTL:
        return entry["data"]
    return None


def _cache_set(key: str, data):
    if "live_data_cache" not in st.session_state:
        st.session_state["live_data_cache"] = {}
    st.session_state["live_data_cache"][key] = {"data": data, "ts": time.time()}


# ── OpenFDA: drug label search ────────────────────────────────────────────────

def search_drug_fda(drug_name: str) -> dict:
    """
    Search OpenFDA for a drug's label information.
    Returns a structured dict with warnings, dosage, side effects, etc.
    """
    key = f"fda_label_{drug_name.lower().strip()}"
    cached = _cache_get(key)
    if cached:
        return cached

    try:
        params = {
            "search": f'openfda.brand_name:"{drug_name}" OR openfda.generic_name:"{drug_name}"',
            "limit": 1,
        }
        r = httpx.get(_OPENFDA_LABEL, params=params, timeout=_TIMEOUT)
        r.raise_for_status()
        data = r.json()
        results = data.get("results", [])
        if not results:
            # Fallback: broader search
            params["search"] = f'"{drug_name}"'
            r = httpx.get(_OPENFDA_LABEL, params=params, timeout=_TIMEOUT)
            r.raise_for_status()
            data = r.json()
            results = data.get("results", [])

        if not results:
            result = {"found": False, "drug_name": drug_name, "source": "OpenFDA"}
            _cache_set(key, result)
            return result

        raw = results[0]
        openfda = raw.get("openfda", {})

        def _first(lst):
            """Return first item of a list, or empty string."""
            return lst[0] if isinstance(lst, list) and lst else (lst or "")

        def _join(lst, max_chars=500):
            """Join list items into a readable string, truncated."""
            if isinstance(lst, list):
                text = " ".join(lst)
            else:
                text = str(lst) if lst else ""
            return text[:max_chars].strip()

        result = {
            "found":                  True,
            "source":                 "OpenFDA (US FDA)",
            "drug_name":              drug_name,
            "brand_names":            openfda.get("brand_name", []),
            "generic_names":          openfda.get("generic_name", []),
            "manufacturer":           _first(openfda.get("manufacturer_name", [])),
            "drug_class":             openfda.get("pharm_class_epc", []),
            "purpose":                _join(raw.get("purpose", [])),
            "indications":            _join(raw.get("indications_and_usage", []), 600),
            "dosage":                 _join(raw.get("dosage_and_administration", []), 600),
            "warnings":               _join(raw.get("warnings", []), 600),
            "contraindications":      _join(raw.get("contraindications", []), 500),
            "adverse_reactions":      _join(raw.get("adverse_reactions", []), 500),
            "drug_interactions_text": _join(raw.get("drug_interactions", []), 500),
            "precautions":            _join(raw.get("precautions", []), 500),
            "storage":                _join(raw.get("storage_and_handling", [])),
            "pregnancy_category":     _join(raw.get("pregnancy", [])),
            "overdosage":             _join(raw.get("overdosage", []), 400),
        }
        _cache_set(key, result)
        return result

    except httpx.TimeoutException:
        return {"found": False, "drug_name": drug_name, "error": "Request timed out", "source": "OpenFDA"}
    except Exception as e:
        return {"found": False, "drug_name": drug_name, "error": str(e), "source": "OpenFDA"}


def get_adverse_event_count(drug_name: str) -> dict:
    """
    Get adverse event report count for a drug from OpenFDA.
    Returns {"drug_name", "total_reports", "serious_reports", "source"}
    """
    key = f"fda_events_{drug_name.lower().strip()}"
    cached = _cache_get(key)
    if cached:
        return cached

    try:
        # Total reports
        params_total = {
            "search": f'patient.drug.openfda.generic_name:"{drug_name}"',
            "limit": 1,
        }
        r_total = httpx.get(_OPENFDA_EVENT, params=params_total, timeout=_TIMEOUT)
        total = 0
        if r_total.status_code == 200:
            total = r_total.json().get("meta", {}).get("results", {}).get("total", 0)

        # Serious reports
        params_serious = {
            "search": (
                f'patient.drug.openfda.generic_name:"{drug_name}"'
                ' AND serious:1'
            ),
            "limit": 1,
        }
        r_serious = httpx.get(_OPENFDA_EVENT, params=params_serious, timeout=_TIMEOUT)
        serious = 0
        if r_serious.status_code == 200:
            serious = r_serious.json().get("meta", {}).get("results", {}).get("total", 0)

        result = {
            "drug_name":       drug_name,
            "total_reports":   total,
            "serious_reports": serious,
            "source":          "OpenFDA Adverse Event Reporting System (FAERS)",
        }
        _cache_set(key, result)
        return result

    except Exception as e:
        return {"drug_name": drug_name, "total_reports": 0, "serious_reports": 0,
                "error": str(e), "source": "OpenFDA"}


# ── RxNorm: drug normalisation ────────────────────────────────────────────────

def get_rxcui(drug_name: str) -> Optional[str]:
    """Return the RxNorm concept unique identifier (RxCUI) for a drug name."""
    key = f"rxcui_{drug_name.lower().strip()}"
    cached = _cache_get(key)
    if cached is not None:
        return cached if cached else None

    try:
        r = httpx.get(
            f"{_RXNORM_BASE}/rxcui.json",
            params={"name": drug_name, "search": 1},
            timeout=_TIMEOUT,
        )
        r.raise_for_status()
        data = r.json()
        rxcui = data.get("idGroup", {}).get("rxnormId", [None])[0]
        _cache_set(key, rxcui or "")
        return rxcui
    except Exception:
        _cache_set(key, "")
        return None


def get_rxnorm_interactions(drug_names: list[str]) -> list[dict]:
    """
    Check interactions for a list of drug names via RxNorm Interaction API.
    Returns list of interaction dicts from the live API.
    """
    key = f"rxnorm_ixn_{'-'.join(sorted(d.lower() for d in drug_names))}"
    cached = _cache_get(key)
    if cached is not None:
        return cached

    # Resolve RxCUIs
    rxcuis = []
    name_map = {}
    for name in drug_names:
        rxcui = get_rxcui(name)
        if rxcui:
            rxcuis.append(rxcui)
            name_map[rxcui] = name

    if len(rxcuis) < 2:
        _cache_set(key, [])
        return []

    try:
        r = httpx.get(
            f"{_RXNORM_BASE}/interaction/list.json",
            params={"rxcuis": " ".join(rxcuis)},
            timeout=_TIMEOUT,
        )
        r.raise_for_status()
        data = r.json()
        full_ixn = data.get("fullInteractionTypeGroup", [])

        interactions = []
        for group in full_ixn:
            for ixn_type in group.get("fullInteractionType", []):
                concept_pairs = ixn_type.get("interactionPair", [])
                for pair in concept_pairs:
                    concepts = pair.get("interactionConcept", [])
                    if len(concepts) < 2:
                        continue
                    drug_a = concepts[0].get("minConceptItem", {}).get("name", "")
                    drug_b = concepts[1].get("minConceptItem", {}).get("name", "")
                    severity = pair.get("severity", "unknown").lower()
                    description = pair.get("description", "")
                    interactions.append({
                        "drug_a":          drug_a,
                        "drug_b":          drug_b,
                        "severity":        severity,
                        "description":     description,
                        "source":          "RxNorm / NLM",
                        "severity_label":  _severity_label(severity),
                    })

        _cache_set(key, interactions)
        return interactions

    except Exception as e:
        _cache_set(key, [])
        return []


def _severity_label(severity: str) -> str:
    mapping = {
        "high":    "🔴 High",
        "medium":  "🟡 Moderate",
        "moderate":"🟡 Moderate",
        "low":     "🟢 Low",
        "unknown": "⚪ Unknown",
    }
    return mapping.get(severity.lower(), f"• {severity.capitalize()}")


# ── OpenFDA: drug recall search ───────────────────────────────────────────────

def get_drug_recalls(drug_name: str, limit: int = 5) -> list[dict]:
    """
    Fetch recent FDA drug recall records for a given drug name.
    Returns list of recall dicts.
    """
    key = f"fda_recall_{drug_name.lower().strip()}_{limit}"
    cached = _cache_get(key)
    if cached is not None:
        return cached

    try:
        r = httpx.get(
            "https://api.fda.gov/drug/enforcement.json",
            params={
                "search": f'product_description:"{drug_name}"',
                "limit": limit,
                "sort": "report_date:desc",
            },
            timeout=_TIMEOUT,
        )
        if r.status_code == 404:
            _cache_set(key, [])
            return []
        r.raise_for_status()
        data = r.json()
        recalls = []
        for rec in data.get("results", []):
            recalls.append({
                "recall_number":   rec.get("recall_number", ""),
                "product":         rec.get("product_description", "")[:200],
                "reason":          rec.get("reason_for_recall", "")[:300],
                "classification":  rec.get("classification", ""),
                "status":          rec.get("status", ""),
                "date":            rec.get("report_date", ""),
                "recalling_firm":  rec.get("recalling_firm", ""),
                "source":          "FDA Enforcement Database",
            })
        _cache_set(key, recalls)
        return recalls
    except Exception:
        _cache_set(key, [])
        return []


# ── Combined enrichment ───────────────────────────────────────────────────────

def enrich_drug_info(drug_name: str) -> dict:
    """
    Fetch FDA label + adverse event count for a drug.
    Returns merged dict for display.
    """
    label = search_drug_fda(drug_name)
    events = get_adverse_event_count(drug_name)
    label["adverse_event_total"]   = events.get("total_reports", 0)
    label["adverse_event_serious"] = events.get("serious_reports", 0)
    return label
