"""Cloudflare Workers AI client for bilingual analysis."""
from __future__ import annotations

import json
import os
import urllib.request

from .. import config

AI_RUN_URL = "https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{model}"

SYSTEM_PROMPT = (
    "You are an OSINT analysis assistant. You analyze labeled evidence about a subject "
    "and produce cautious, factual observations. You NEVER invent facts, phone numbers, "
    "accounts, or URLs. You clearly separate what the evidence shows from what is unknown. "
    "Keep every answer under 120 words. Respond in the language requested by the user."
)


def analyze(evidence_json: str, language: str = "en") -> str:
    """Send evidence to Cloudflare Workers AI and return the analysis text."""
    token = config.cf_api_token()
    account_id = config.cf_account_id()
    if not token or not account_id:
        raise RuntimeError(
            "CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID must be set "
            "(free Workers AI tier)."
        )

    model = config.cf_model()
    url = AI_RUN_URL.format(account_id=account_id, model=model)

    lang_hint = "Bahasa Indonesia" if language == "id" else "English"
    payload = {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Language: {lang_hint}\n\n"
                    "Labeled evidence (JSON):\n" + evidence_json
                ),
            },
        ],
        "max_tokens": 400,
        "temperature": 0.3,
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode())
    result = data.get("result", {})
    return result.get("response", "") or ""
