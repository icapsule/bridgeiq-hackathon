import re
from typing import Tuple, List

# Swedish Personnummer pattern: YYYYMMDD-XXXX or YYMMDD-XXXX or without dash
PERSONNUMMER_PATTERN = re.compile(r"\b(?:\d{4}|\d{2})(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])[-+]?\d{4}\b")
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
PHONE_PATTERN = re.compile(r"\b(?:\+46|0046|0)[0-9\s\-/]{6,14}\b")


def detect_pii(text: str) -> Tuple[bool, List[str]]:
    """
    Checks if text contains PII: Swedish personal identity number, email, or phone.
    Returns (has_pii, detected_categories).
    """
    detected = []
    if PERSONNUMMER_PATTERN.search(text):
        detected.append("personnummer")
    if EMAIL_PATTERN.search(text):
        detected.append("email")
    if PHONE_PATTERN.search(text):
        detected.append("phone")

    return len(detected) > 0, detected


def scrub_pii(text: str) -> str:
    """
    Replaces detected PII tokens with neutral placeholders.
    """
    scrubbed = PERSONNUMMER_PATTERN.sub("[REDACTED_ID]", text)
    scrubbed = EMAIL_PATTERN.sub("[REDACTED_EMAIL]", scrubbed)
    scrubbed = PHONE_PATTERN.sub("[REDACTED_PHONE]", scrubbed)
    return scrubbed
