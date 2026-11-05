# SENTINEL-ID

**Bilingual (English/Indonesia) AI-OSINT investigation workspace.**

Gathers OSINT evidence, labels it with provenance and confidence scoring, runs free Cloudflare Workers AI analysis, and auto-generates citable investigation reports in **English AND Bahasa Indonesia**.

## Why

- Existing LLM+OSINT tools are English-only and embryonic (no bilingual output, no evidence-labeling discipline).
- Indonesian investigators, journalists, and anti-scam efforts lack an open, programmatic tool.
- This repo applies **data-labeling quality standards** to investigation evidence: provenance, dedup, confidence, traceability.

## Architecture

```
sentinel/
├── cli.py            # command-line entrypoint
├── config.py         # env-driven configuration
├── collectors/       # evidence collection (username, email, NIK, DNS, breach)
├── labeling/         # evidence model, provenance, confidence scoring
├── analyze/          # Cloudflare Workers AI client + bilingual analysis
└── report/           # bilingual Markdown report renderers
```

## Quickstart

```bash
pip install -r requirements.txt

# Collect evidence for a handle (local/registry sources only)
python -m sentinel.cli collect username --value johndoe --out evidence.json

# Label + score the evidence
python -m sentinel.cli label --in evidence.json --out labeled.json

# Run AI analysis (Cloudflare Workers AI; set CLOUDFLARE_API_TOKEN)
export CLOUDFLARE_API_TOKEN=...
python -m sentinel.cli analyze --in labeled.json --out analysis.json

# Generate bilingual report
python -m sentinel.cli report --in analysis.json --out report/ --lang both
```

## AI backend

- Default: **Cloudflare Workers AI** (`@cf/meta/llama-3.1-8b-instruct-fp8`) — free tier.
- Set `CLOUDFLARE_API_TOKEN` and optionally `CLOUDFLARE_ACCOUNT_ID`.
- Analysis is **advisory only**; reports explicitly separate collected facts from AI commentary.

## Ethics & legality

Use only for **authorized investigations** (fraud cases, anti-scam work, OSINT research with permission). Do not use to harass or stalk. Respect local privacy laws — including Indonesia's UU PDP (Personal Data Protection Law).

## License

MIT
