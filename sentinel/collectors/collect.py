"""Collectors: username, email, NIK validation, DNS, breach."""
from __future__ import annotations

import json
import re
import subprocess
import urllib.request

from ..labeling.evidence import Evidence


def collect_username(value: str) -> list[Evidence]:
    """Check a username across a few public, aggregation-free checks.

    NOTE: This deliberately does NOT scrape social platforms.
    It returns registry/structured checks only (DNS, email-pattern hint).
    For full platform presence, wrap Sherlock/Maigret externally.
    """
    out: list[Evidence] = []
    # If the value looks like an email, route to email collector
    if "@" in value:
        return collect_email(value)

    out.append(
        Evidence(
            category="username",
            value=value,
            source="manual-entry",
            notes="Username captured for investigation; platform checks are external.",
        ).with_source_class("user_report")
    )
    # username@pattern check for common mail provider guesses is skipped (privacy).
    return out


def collect_email(value: str) -> list[Evidence]:
    out: list[Evidence] = []
    email = value.strip().lower()
    domain = email.split("@")[-1] if "@" in email else ""

    out.append(
        Evidence(
            category="email",
            value=email,
            source="manual-entry",
            notes="Email address provided by investigator.",
        ).with_source_class("inferred")
    )
    if domain:
        # DNS MX check for the domain (registry-level, non-invasive)
        try:
            r = subprocess.run(
                ["dig", "+short", "MX", domain],
                capture_output=True, text=True, timeout=15,
            )
            mx = [line.strip() for line in r.stdout.splitlines() if line.strip()][:5]
            if mx:
                out.append(
                    Evidence(
                        category="domain",
                        value=domain,
                        source="dns-mx",
                        source_url=f"dig MX {domain}",
                        notes="; ".join(mx),
                    ).with_source_class("registry")
                )
        except Exception:
            pass
    return out


def validate_nik(value: str) -> Evidence:
    """Validate the STRUCTURE of an Indonesian NIK (Nomor Induk Kependudukan).

    Per spec: 16 digits; DD-MM-YY birthdate (day+40 for female) in positions 7-12.
    This is validation only, not lookup of personal data.
    """
    nik = re.sub(r"\D", "", value)
    ok = len(nik) == 16
    gender = None
    birthdate = None
    if ok:
        day = int(nik[6:8])
        gender = "female" if day > 40 else "male"
        day_adj = day - 40 if gender == "female" else day
        month = int(nik[8:10])
        year = int(nik[10:12])
        birthdate = f"{day_adj:02d}-{month:02d}-19{year:02d}" if year > 40 else f"{day_adj:02d}-{month:02d}-20{year:02d}"
    return Evidence(
        category="nik",
        value=nik,
        source="structural-validation",
        notes=f"valid={ok}; gender={gender}; birthdate={birthdate}",
    ).with_source_class("official")


def collect_breach(value: str) -> list[Evidence]:
    """Breach check is intentionally stubbed — use a consented API key externally.

    (e.g. HaveIBeenPwned v3 requires a paid key and has strict ToS;
    we leave the integration point for the investigator.)
    """
    return [
        Evidence(
            category="breach",
            value=value,
            source="unconfigured",
            notes="Breach API not configured; supply an API key or external tool.",
        ).with_source_class("inferred")
    ]


def run_collector(kind: str, value: str) -> list[Evidence]:
    if kind == "username":
        return collect_username(value)
    if kind == "email":
        return collect_email(value)
    if kind == "nik":
        return [validate_nik(value)]
    if kind == "breach":
        return collect_breach(value)
    raise ValueError(f"unknown collector: {kind}")
