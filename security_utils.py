"""Security and privacy helpers for the Employee QR Register."""

from __future__ import annotations

import csv
import hashlib
import hmac
import json
import os
import re
import secrets
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


PROJECT_ROOT = Path(__file__).resolve().parent
LOCAL_CREDENTIALS_PATH = PROJECT_ROOT / "LOCAL_CREDENTIALS.txt"
USERNAME_RE = re.compile(r"^[A-Za-z0-9_.-]{3,50}$")
FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


@dataclass(frozen=True)
class SecurityConfig:
    username: str
    password: str
    qr_signing_key: str


def _read_key_value_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise RuntimeError(f"Invalid credentials file entry on line {line_number}.")
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def load_security_config(
    credentials_path: Path = LOCAL_CREDENTIALS_PATH,
    environment: Mapping[str, str] | None = None,
) -> SecurityConfig:
    """Load credentials from environment first, then the ignored local file."""
    env = os.environ if environment is None else environment
    local = _read_key_value_file(credentials_path)

    username = env.get("EMPLOYEE_APP_USERNAME") or local.get("EMPLOYEE_APP_USERNAME", "")
    password = env.get("EMPLOYEE_APP_PASSWORD") or local.get("EMPLOYEE_APP_PASSWORD", "")
    signing_key = env.get("QR_SIGNING_KEY") or local.get("QR_SIGNING_KEY", "")

    if not USERNAME_RE.fullmatch(username):
        raise RuntimeError("EMPLOYEE_APP_USERNAME must contain 3-50 safe characters.")
    if len(password) < 16:
        raise RuntimeError("EMPLOYEE_APP_PASSWORD must be at least 16 characters.")
    if not all((re.search(r"[A-Z]", password), re.search(r"[a-z]", password), re.search(r"\d", password))):
        raise RuntimeError("EMPLOYEE_APP_PASSWORD must include uppercase, lowercase, and numeric characters.")
    if len(signing_key) < 32:
        raise RuntimeError("QR_SIGNING_KEY must be a unique random value of at least 32 characters.")

    return SecurityConfig(username=username, password=password, qr_signing_key=signing_key)


def verify_login(config: SecurityConfig, username: str, password: str) -> bool:
    """Compare both credential fields in constant time."""
    username_ok = hmac.compare_digest(config.username.encode(), username.strip().encode())
    password_ok = hmac.compare_digest(config.password.encode(), password.encode())
    return username_ok and password_ok


def sanitize_csv_cell(value: str) -> str:
    """Neutralize spreadsheet formulas while preserving visible user input."""
    normalized = str(value).replace("\x00", "").strip()
    if normalized.startswith(FORMULA_PREFIXES):
        return "'" + normalized
    return normalized


def _safe_name(value: str, field_name: str) -> str:
    normalized = sanitize_csv_cell(value)
    if not 1 <= len(normalized) <= 80:
        raise ValueError(f"{field_name} must contain 1-80 characters.")
    if not all(character.isalpha() or character in " -'" for character in normalized):
        raise ValueError(f"{field_name} may contain letters, spaces, apostrophes, and hyphens only.")
    return normalized


def validate_employee(fields: Mapping[str, str]) -> dict[str, str]:
    """Validate employee input before it reaches disk or a QR payload."""
    first_name = _safe_name(fields.get("first_name", ""), "First name")
    last_name = _safe_name(fields.get("last_name", ""), "Last name")
    gender = sanitize_csv_cell(fields.get("gender", ""))
    country = sanitize_csv_cell(fields.get("country", ""))
    birth_date = sanitize_csv_cell(fields.get("birth_date", ""))
    address = sanitize_csv_cell(fields.get("address", ""))

    if gender not in {"Male", "Female", "Other"}:
        raise ValueError("Choose a valid gender.")
    if not 2 <= len(country) <= 80:
        raise ValueError("Choose or enter a valid country.")
    if not 4 <= len(birth_date) <= 20:
        raise ValueError("Choose a valid birth date.")
    if not 3 <= len(address) <= 250:
        raise ValueError("Address must contain 3-250 characters.")

    return {
        "first_name": first_name,
        "last_name": last_name,
        "gender": gender,
        "country": country,
        "birth_date": birth_date,
        "address": address,
    }


def new_employee_id() -> str:
    return "emp_" + secrets.token_urlsafe(12)


def build_signed_qr_payload(employee_id: str, issued_at: str, signing_key: str) -> str:
    """Build a privacy-preserving QR token with tamper detection."""
    canonical = f"v1|{employee_id}|{issued_at}"
    signature = hmac.new(signing_key.encode(), canonical.encode(), hashlib.sha256).hexdigest()
    return json.dumps(
        {"version": 1, "employee_id": employee_id, "issued_at": issued_at, "signature": signature},
        separators=(",", ":"),
        sort_keys=True,
    )


def verify_signed_qr_payload(payload: str, signing_key: str) -> bool:
    try:
        data = json.loads(payload)
        canonical = f"v{data['version']}|{data['employee_id']}|{data['issued_at']}"
        expected = hmac.new(signing_key.encode(), canonical.encode(), hashlib.sha256).hexdigest()
        return data["version"] == 1 and hmac.compare_digest(expected, data["signature"])
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        return False


def append_employee_record(path: Path, record: Mapping[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "employee_id",
        "first_name",
        "last_name",
        "gender",
        "birth_date",
        "country",
        "address",
        "created_at",
    ]
    should_write_header = not path.exists() or path.stat().st_size == 0
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        if should_write_header:
            writer.writeheader()
        writer.writerow({field: sanitize_csv_cell(record.get(field, "")) for field in fieldnames})
