from app.models import JobRequirement
from app.pipeline.score import calculate_coverage, compute_match_scores


def test_calculate_coverage_weighted():
    reqs = [
        JobRequirement(concept_id="c1", label="Skill 1", importance="must", jd_clause="Must know c1"),
        JobRequirement(concept_id="c2", label="Skill 2", importance="must", jd_clause="Must know c2"),
        JobRequirement(concept_id="c3", label="Skill 3", importance="nice", jd_clause="Nice to know c3"),
    ]
    # Candidate has c1 (must=1.0) and c3 (nice=0.4). Total = 2.4. Matched = 1.4 -> 1.4/2.4 = 0.5833
    cov, matched, missing = calculate_coverage(["c1", "c3"], reqs)
    assert round(cov, 2) == 0.58
    assert "c1" in matched
    assert "c3" in matched
    assert missing == ["c2"]


def test_hidden_gem_detection():
    # coverage 0.85, title similarity 0.20 -> Hidden Gem!
    breakdown, is_gem, badge = compute_match_scores(0.85, 0.70, 0.20)
    assert is_gem is True
    assert badge == "Hidden Gem: 85% Competence Overlap"
    assert round(breakdown.composite, 2) == round(0.6 * 0.85 + 0.4 * 0.70, 2)

    # coverage 0.60, title similarity 0.10 -> Not a gem (coverage < 0.75)
    _, is_gem2, _ = compute_match_scores(0.60, 0.70, 0.10)
    assert is_gem2 is False

    # coverage 0.90, title similarity 0.80 -> High match, but not hidden gem (already obvious title)
    _, is_gem3, _ = compute_match_scores(0.90, 0.80, 0.80)
    assert is_gem3 is False
