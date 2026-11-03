from app.models import CompetencyGraph, GroundedSkill, SkillCategory
from app.pipeline.score import compute_match_scores


def test_title_agnostic_hidden_gem_logic():
    # If a candidate has high coverage (0.85) but low title similarity (0.20), they are a Hidden Gem!
    breakdown, is_gem, badge = compute_match_scores(
        coverage=0.85,
        semantic_score=0.75,
        title_similarity=0.20
    )
    assert is_gem is True
    assert "Hidden Gem" in (badge or "")
    assert breakdown.composite == round(0.6 * 0.85 + 0.4 * 0.75, 4)


def test_competency_graph_concept_extraction():
    skills = [
        GroundedSkill(
            raw_text="5-nines uptime",
            category=SkillCategory.technical,
            concept_id="tax_001",
            concept_label="Hög tillgänglighet",
            confidence=0.92,
            evidence=[]
        )
    ]
    graph = CompetencyGraph(skills=skills, clusters={"technical": ["tax_001"]})
    assert len(graph.skills) == 1
    assert graph.skills[0].concept_id == "tax_001"
    assert "technical" in graph.clusters
