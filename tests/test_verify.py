from app.guardrails.verify import verify_quote


def test_verify_quote_exact_and_normalized():
    cv = """
    Senior Core Network Engineer (2013-2023).
    Kept a 4G/5G packet core at 99.999% uptime across 12 datacenters.
    Managed incident response and failover protocols.
    """

    found, idx = verify_quote("Kept a 4G/5G packet core at 99.999% uptime", cv)
    assert found is True
    assert idx >= 0

    # With extra spaces and different casing
    found2, idx2 = verify_quote("kept a  4g/5g   packet core at 99.999% uptime", cv)
    assert found2 is True
    assert idx2 >= 0


def test_verify_quote_hallucinated():
    cv = "Junior developer with python experience."
    found, idx = verify_quote("Designed distributed microservices in Go", cv)
    assert found is False
    assert idx == -1

