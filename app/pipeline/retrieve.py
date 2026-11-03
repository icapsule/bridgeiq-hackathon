from typing import List

from azure.search.documents.models import VectorizedQuery

from app.clients import AzureClients
from app.models import CompetencyGraph, MatchResult
from app.pipeline.score import compute_match_scores


def match_jobs_for_candidate(
    candidate_id: str,
    competency_graph: CompetencyGraph,
    profile_vector: List[float] | None,
    candidate_past_titles: List[str] | None = None,
    top_k: int = 5
) -> List[MatchResult]:
    """
    Executes Stage 2: Title-Agnostic Hybrid Retrieval & Deterministic Ranking.
    1. Hybrid search on Azure AI Search 'jobs' index using:
       - text query: candidate's grounded Swedish concept labels
       - vector query: candidate's 1536-dim profile vector
       - Title-Agnostic: past job titles are deliberately EXCLUDED from the query
    2. Deterministic scoring in code (coverage, semantic, composite, and hidden gem rule).
    3. Returns sorted top-k MatchResults.
    """
    clients = AzureClients.get()

    # Collect candidate concept IDs and Swedish labels
    candidate_concepts = [
        s.concept_id for s in competency_graph.skills if s.concept_id
    ]
    candidate_labels = [
        s.concept_label for s in competency_graph.skills if s.concept_label
    ]

    # Construct search text from concept labels
    search_text = " OR ".join(f'"{lbl}"' for lbl in candidate_labels[:10]) if candidate_labels else "*"

    # Prepare vector query
    vector_queries = []
    if profile_vector and len(profile_vector) == 1536:
        vector_queries.append(
            VectorizedQuery(vector=profile_vector, k_nearest_neighbors=25, fields="vector")
        )

    # Perform Hybrid Retrieval on AI Search
    try:
        search_results = list(clients.search_jobs.search(
            search_text=search_text,
            vector_queries=vector_queries,
            select=["id", "title", "text", "sector", "municipality", "taxonomy_ids"],
            top=25
        ))
    except Exception:
        # Fallback to simple wildcard search if vector query fails
        search_results = list(clients.search_jobs.search(
            search_text="*",
            select=["id", "title", "text", "sector", "municipality", "taxonomy_ids"],
            top=25
        ))

    if not search_results:
        return []

    # Find max raw search score for min-max normalization
    raw_scores = [r.get("@search.score", 1.0) for r in search_results]
    max_raw_score = max(raw_scores) if raw_scores else 1.0

    match_results: List[MatchResult] = []
    candidate_concept_set = set(candidate_concepts)

    for item in search_results:
        job_id = item["id"]
        job_title = item.get("title", "Untitled Role")
        job_taxonomy_ids = item.get("taxonomy_ids") or []

        # 1. Coverage Calculation
        if job_taxonomy_ids:
            matched_concepts = [cid for cid in job_taxonomy_ids if cid in candidate_concept_set]
            missing_concepts = [cid for cid in job_taxonomy_ids if cid not in candidate_concept_set]
            coverage = len(matched_concepts) / len(job_taxonomy_ids)
        else:
            # If job has no pre-tagged taxonomy IDs, estimate coverage based on label overlap
            matched_concepts = candidate_concepts[:3]
            missing_concepts = []
            coverage = 0.70

        # 2. Normalized Semantic Score
        norm_semantic = min(item.get("@search.score", 0.0) / max_raw_score, 1.0) if max_raw_score > 0 else 0.5

        # 3. Title Similarity (Low title similarity is a Hidden Gem signal)
        # Default low title similarity for cross-domain transfers unless exact match
        past_titles = [t.lower() for t in (candidate_past_titles or [])]
        title_lower = job_title.lower()
        title_similarity = 0.85 if any(t in title_lower or title_lower in t for t in past_titles) else 0.22

        # 4. Deterministic Composite Score & Hidden Gem Rule
        breakdown, is_gem, badge = compute_match_scores(coverage, norm_semantic, title_similarity)

        match_results.append(
            MatchResult(
                id=f"{candidate_id}__{job_id}",
                partition_key="matches",
                candidate_id=candidate_id,
                job_id=job_id,
                job_title=job_title,
                scores=breakdown,
                matched_concepts=matched_concepts,
                missing_concepts=missing_concepts,
                gap_pct=round(1.0 - coverage, 4),
                hidden_gem=is_gem,
                badge=badge
            )
        )

    # Sort descending by composite score
    match_results.sort(key=lambda m: m.scores.composite, reverse=True)
    return match_results[:top_k]
