from app.guardrails.pii import detect_pii, scrub_pii


def test_detect_pii_swedish_personnummer():
    text = "My Swedish id is 19900101-1234 and I live in Stockholm."
    has_pii, categories = detect_pii(text)
    assert has_pii is True
    assert "personnummer" in categories


def test_detect_pii_email_phone():
    text = "Reach me at test.user@example.com or +46 70 123 4567."
    has_pii, categories = detect_pii(text)
    assert has_pii is True
    assert "email" in categories
    assert "phone" in categories


def test_clean_text_no_pii():
    text = "10 years experience running 4G and 5G packet core networks with five-nines uptime."
    has_pii, categories = detect_pii(text)
    assert has_pii is False
    assert len(categories) == 0


def test_scrub_pii():
    text = "Call me at 0701234567 or email john@acme.se (19850512-5678)"
    scrubbed = scrub_pii(text)
    assert "john@acme.se" not in scrubbed
    assert "19850512-5678" not in scrubbed
    assert "[REDACTED_EMAIL]" in scrubbed
    assert "[REDACTED_ID]" in scrubbed

