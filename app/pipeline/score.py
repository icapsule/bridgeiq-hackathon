
from app.models import JobRequirement, ScoreBreakdown


def calculate_coverage(
    candidate_concept_ids: list[str],
    job_requirements: list[JobRequirement]
) -> tuple[float, list[str], list[str]]:
    """
    Computes coverage score based on weighted requirement satisfaction:
    - must: weight 1.0
    - nice: weight 0.4

    Returns (coverage_score, matched_concept_ids, missing_must_concept_ids)
    """
    if not job_requirements:
        return 1.0, [], []

    candidate_set = set(candidate_concept_ids)
    total_weight = 0.0
    matched_weight = 0.0
    matched_concepts: list[str] = []
    missing_concepts: list[str] = []

    for req in job_requirements:
        weight = 1.0 if req.importance == "must" else 0.4
        total_weight += weight

        if req.concept_id in candidate_set:
            matched_weight += weight
            matched_concepts.append(req.concept_id)
        else:
            if req.importance == "must":
                missing_concepts.append(req.concept_id)

    coverage = matched_weight / total_weight if total_weight > 0 else 0.0
    return round(min(max(coverage, 0.0), 1.0), 4), matched_concepts, missing_concepts


def compute_match_scores(
    coverage: float,
    semantic_score: float,
    title_similarity: float
) -> tuple[ScoreBreakdown, bool, str | None]:
    """
    Calculates deterministic composite score:
    composite = 0.6 * coverage + 0.4 * semantic
    Hidden Gem detection: coverage >= 0.75 and title_similarity < 0.45
    """
    norm_coverage = min(max(coverage, 0.0), 1.0)
    norm_semantic = min(max(semantic_score, 0.0), 1.0)
    norm_title = min(max(title_similarity, 0.0), 1.0)

    composite = round(0.6 * norm_coverage + 0.4 * norm_semantic, 4)

    is_hidden_gem = (norm_coverage >= 0.75) and (norm_title < 0.45)
    badge = f"Hidden Gem: {round(norm_coverage * 100)}% Competence Overlap" if is_hidden_gem else None

    breakdown = ScoreBreakdown(
        coverage=norm_coverage,
        semantic=norm_semantic,
        title_similarity=norm_title,
        composite=composite
    )

    return breakdown, is_hidden_gem, badge
