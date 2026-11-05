"""Evidence model, provenance and confidence scoring."""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional


# Confidence baselines by source class (0.0 - 1.0)
SOURCE_CONFIDENCE = {
    "official": 0.95,     # government / registry / primary official source
    "registry": 0.75,     # public registry / structured index
    "scrape": 0.55,       # web scrape / search result
    "breach": 0.60,       # breach database entry
    "user_report": 0.40,  # community / user submitted
    "inferred": 0.30,     # inferred from other signals (never primary)
}


@dataclass
class Evidence:
    category: str            # username | email | phone | nik | domain | breach
    value: str
    source: str
    source_url: str = ""
    retrieved_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    confidence: float = 0.5
    notes: str = ""
    raw: dict = field(default_factory=dict)
    key: str = field(default="", init=False)

    def __post_init__(self):
        self.key = f"{self.category}:{self.value}"

    def with_source_class(self, source_class: str) -> "Evidence":
        self.confidence = SOURCE_CONFIDENCE.get(source_class, 0.5)
        return self


def normalize(evidence: Evidence) -> Evidence:
    """Normalize values for dedup (case, spacing, canonical form)."""
    v = evidence.value.strip().lower()
    if evidence.category == "email":
        evidence.value = v
    elif evidence.category == "phone":
        digits = "".join(ch for ch in evidence.value if ch.isdigit())
        # Indonesian mobile: strip leading 62 / +62, keep 08 format
        if digits.startswith("62") and len(digits) == 12:
            digits = "0" + digits[2:]
        evidence.value = digits
    else:
        evidence.value = v
    evidence.key = f"{evidence.category}:{evidence.value}"
    return evidence


def dedup(evidence_list: list[Evidence]) -> list[Evidence]:
    """Dedup by (category, normalized value), keep highest confidence."""
    best: dict[str, Evidence] = {}
    for e in evidence_list:
        normalize(e)
        cur = best.get(e.key)
        if cur is None or e.confidence > cur.confidence:
            best[e.key] = e
    return list(best.values())


def to_json(evidence_list: list[Evidence]) -> str:
    return json.dumps([asdict(e) for e in evidence_list], indent=2, ensure_ascii=False)


def from_json(text: str) -> list[Evidence]:
    data = json.loads(text)
    return [Evidence(**item) for item in data]
