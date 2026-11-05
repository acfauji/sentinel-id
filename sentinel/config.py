"""Configuration via environment variables."""
import os


def cf_api_token() -> str:
    return os.environ.get("CLOUDFLARE_API_TOKEN", "")


def cf_account_id() -> str:
    return os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")


def cf_model() -> str:
    return os.environ.get(
        "SENTINEL_CF_MODEL", "@cf/meta/llama-3.1-8b-instruct-fp8"
    )


def default_out_dir() -> str:
    return os.environ.get("SENTINEL_OUT", "out")
