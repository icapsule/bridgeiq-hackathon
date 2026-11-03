import re


def normalize_whitespace(text: str) -> str:
    """Normalize internal and external whitespace for robust matching."""
    return re.sub(r"\s+", " ", text).strip().lower()


def verify_quote(quote: str, source_text: str) -> tuple[bool, int]:
    """
    Checks if quote is present verbatim (ignoring case & whitespace variance) in source_text.
    Returns (is_found, char_start).
    """
    if not quote or not source_text:
        return False, -1

    norm_quote = normalize_whitespace(quote)
    norm_source = normalize_whitespace(source_text)

    idx = norm_source.find(norm_quote)
    if idx != -1:
        return True, idx

    # Fallback: check raw containment
    raw_idx = source_text.lower().find(quote.lower().strip())
    if raw_idx != -1:
        return True, raw_idx

    return False, -1
