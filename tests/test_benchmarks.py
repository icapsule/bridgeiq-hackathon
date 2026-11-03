from app.pipeline.benchmarks import (
    compute_candidate_composite,
    get_benchmark_role,
    is_hidden_gem,
    list_benchmark_roles,
)


def test_list_and_get_benchmark_roles():
    roles = list_benchmark_roles()
    assert len(roles) == 3
    assert {r["id"] for r in roles} == {"job-077", "job-012", "job-150"}

    r77 = get_benchmark_role("job-077")
    assert r77 is not None
    assert r77["title"] == "Reliability Engineer, Industrial IoT"
    assert len(r77["cands"]) == 3
    assert r77["reqs"] == [
        "Hög tillgänglighet",
        "Distribuerade system",
        "Incidenthantering",
        "Linux",
        "NIS2-direktivet",
    ]


def test_deterministic_scoring_and_hidden_gem():
    # Amara / Candidate 042: cov=0.85, sem=0.78, tsim=0.21 -> Hidden Gem
    composite_amara = compute_candidate_composite(0.85, 0.78)
    assert composite_amara == 0.822  # 0.6*0.85 + 0.4*0.78 = 0.51 + 0.312 = 0.822
    assert is_hidden_gem(0.85, 0.21) is True

    # Conventional candidate: cov=0.80, sem=0.88, tsim=0.92 -> Not a hidden gem (high title similarity)
    composite_conv = compute_candidate_composite(0.80, 0.88)
    assert composite_conv == 0.832
    assert is_hidden_gem(0.80, 0.92) is False

    # Low coverage candidate: cov=0.60, sem=0.70, tsim=0.20 -> Not a hidden gem (insufficient competence)
    assert is_hidden_gem(0.60, 0.20) is False


def test_evidence_quotes_structure():
    r77 = get_benchmark_role("job-077")
    cand042 = next(c for c in r77["cands"] if "042" in c["alias"])
    assert cand042["story"] == "Telecom core-network reliability → industrial IoT uptime"
    assert len(cand042["evidence"]) >= 3
    for ev in cand042["evidence"]:
        assert "concept" in ev
        assert "jd" in ev
        assert "cv" in ev
        assert "why" in ev
    assert len(cand042["gaps"]) == 1
    assert cand042["gaps"][0]["effort"] == "days"
