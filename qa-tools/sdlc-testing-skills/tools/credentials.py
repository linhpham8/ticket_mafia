"""Shared credential helpers for Confluence, Jira, and QMetry tools.

Priority order:
1. Process/User/Machine environment variables
2. .env file (in working directory or repo root)
3. ~/.atlassian config file
4. macOS/Linux shell profile exports
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load .env file from repo root if it exists
_repo_root = Path(__file__).resolve().parent.parent
_env_path = _repo_root / ".env"
if _env_path.exists():
    load_dotenv(_env_path)


PLACEHOLDER_FRAGMENTS = {
    "your-company",
    "your_email",
    "your.name",
    "replace_with",
    "YOURSPACE",
    "YOUR_PROJECT_ID",
}


def _looks_placeholder(value: str) -> bool:
    lowered = value.strip().lower()
    return not lowered or any(fragment.lower() in lowered for fragment in PLACEHOLDER_FRAGMENTS)


def get_env(var: str, default: str = "") -> str:
    """Read env vars safely, preferring real env over placeholder config values."""
    for scope in ("Process", "User", "Machine"):
        value = os.environ.get(var, "").strip() if scope == "Process" else os.getenv(var, "").strip()
        if value and not _looks_placeholder(value):
            return value

    config_path = Path.home() / ".atlassian"
    if config_path.exists():
        try:
            for line in config_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                if key.strip() == var:
                    candidate = value.strip().strip('"').strip("'")
                    if candidate and not _looks_placeholder(candidate):
                        return candidate
        except Exception:
            pass

    if sys.platform != "win32":
        for rc_name in (".zshrc", ".bashrc", ".bash_profile", ".profile"):
            rc_path = Path.home() / rc_name
            if not rc_path.exists():
                continue
            try:
                for line in rc_path.read_text(encoding="utf-8").splitlines():
                    marker = f"export {var}="
                    if marker in line:
                        _, _, value = line.partition(marker)
                        candidate = value.strip().strip('"').strip("'")
                        if candidate and not _looks_placeholder(candidate):
                            return candidate
            except Exception:
                pass

    return default


def load_atlassian_credentials(require_space_key: bool = False) -> tuple[str, ...]:
    email = get_env("ATLASSIAN_EMAIL") or get_env("ATLASSIAN_USER_EMAIL")
    token = get_env("ATLASSIAN_API_TOKEN")
    base_url = get_env("ATLASSIAN_BASE_URL", "").rstrip("/")

    required = {
        "ATLASSIAN_EMAIL": email,
        "ATLASSIAN_API_TOKEN": token,
        "ATLASSIAN_BASE_URL": base_url,
    }

    space_key = ""
    if require_space_key:
        space_key = get_env("CONFLUENCE_SPACE_KEY")
        required["CONFLUENCE_SPACE_KEY"] = space_key

    missing = [key for key, value in required.items() if not value]
    if missing:
        missing_text = ", ".join(missing)
        raise RuntimeError(f"Missing credentials: {missing_text}. Set env vars or ~/.atlassian first.")

    if require_space_key:
        return email, token, base_url, space_key
    return email, token, base_url


def load_qmetry_token(env_var: str = "QMETRY_API_TOKEN") -> str:
    token = get_env(env_var)
    if not token:
        raise RuntimeError(f"Missing QMetry token env var: {env_var}")
    return token
