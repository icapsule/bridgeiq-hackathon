import json
import logging
from pathlib import Path

from azure.search.documents.models import VectorizedQuery

from app.clients import AzureClients
from app.config import settings
from app.guardrails.pii import detect_pii, scrub_pii
from app.guardrails.verify import verify_quote
from app.models import (
    CompetencyGraph,
    Evidence,
    GroundedSkill,
    LLMExtractResponse,
    SkillCategory,
)

logger = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "extract_v1.md"


def load_extract_system_prompt() -> str:
    if PROMPT_PATH.exists():
        return PROMPT_PATH.read_text(encoding="utf-8")
    return "You are a bilingual skill extraction assistant. Extract skills into JSON conforming to schema."


def extract_and_ground_cv(cv_text: str) -> tuple[CompetencyGraph, list[float] | None, list[str]]:
    """
    Executes Stage 1 of BridgeIQ pipeline:
    1. PII Scrubbing
    2. LLM Extraction (gpt-5-mini with JSON output)
    3. Batched Embedding (text-embedding-3-small)
    4. Hybrid Search Grounding against Sweden JobTech Taxonomy (1,248 concepts)
    5. Quote Verifier checking
    6. Profile vector synthesis

    Returns (CompetencyGraph, profile_vector, warnings)
    """
    warnings: list[str] = []
    has_pii, pii_types = detect_pii(cv_text)
    if has_pii:
        warnings.append(f"PII detected and scrubbed ({', '.join(pii_types)})")
        clean_cv = scrub_pii(cv_text)
    else:
        clean_cv = cv_text

    clients = AzureClients.get()
    system_prompt = load_extract_system_prompt()

    user_prompt = f"""Extract transferable skills from the following candidate CV text.
Return JSON with key 'skills', where each item has:
- 'raw_text': concise description
- 'category': one of 'technical', 'domain', 'soft', 'certification', 'language'
- 'years': number of years if available, otherwise null
- 'evidence_quote': verbatim substring from the CV
- 'search_terms_sv': 1 to 3 Swedish search phrases
- 'search_terms_en': 1 to 3 English keywords

<cv>
{clean_cv}
</cv>"""

    # 1. LLM Extraction
    response = clients.openai_client.chat.completions.create(
        model=settings.chat_deployment,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.1,
    )

    raw_json_str = response.choices[0].message.content or "{}"
    try:
        parsed_data = json.loads(raw_json_str)
        extracted = LLMExtractResponse(**parsed_data)
    except Exception as e:
        logger.error(f"Failed to parse LLM extraction response: {e}")
        extracted = LLMExtractResponse(skills=[])
        warnings.append(f"Extraction parse error: {str(e)}")

    if not extracted.skills:
        return CompetencyGraph(skills=[], clusters={}, unmapped_count=0), None, warnings

    # 2. Batched Embeddings for Grounding
    embed_inputs = []
    for s in extracted.skills:
        text_for_embed = f"{s.raw_text} {' '.join(s.search_terms_sv)}"
        embed_inputs.append(text_for_embed)

    emb_response = clients.openai_client.embeddings.create(
        input=embed_inputs,
        model=settings.embed_deployment
    )
    skill_embeddings = [item.embedding for item in emb_response.data]

    # 3. Hybrid Search Grounding against JobTech Taxonomy
    grounded_skills: list[GroundedSkill] = []
    valid_embeddings: list[list[float]] = []
    clusters: dict[str, list[str]] = {}
    unmapped_count = 0

    for i, s in enumerate(extracted.skills):
        skill_emb = skill_embeddings[i]
        sv_query = " OR ".join(s.search_terms_sv) if s.search_terms_sv else s.raw_text

        # Quote verification against original CV
        is_quote_valid, char_start = verify_quote(s.evidence_quote, clean_cv)
        evidence_list = [
            Evidence(
                quote=s.evidence_quote,
                char_start=char_start if is_quote_valid else None
            )
        ]

        # Hybrid query on taxonomy
        vq = VectorizedQuery(vector=skill_emb, k_nearest_neighbors=3, fields="vector")
        try:
            hits = list(clients.search_taxonomy.search(
                search_text=sv_query,
                vector_queries=[vq],
                top=1
            ))
        except Exception as e:
            logger.warning(f"Taxonomy search query failed for skill '{s.raw_text}': {e}")
            hits = []

        if hits:
            top_hit = hits[0]
            concept_id = top_hit.get("id")
            concept_label = top_hit.get("preferred_label")
            raw_score = top_hit.get("@search.score", 0.0)
            norm_confidence = round(min(max(raw_score * 20.0, 0.40), 0.99), 2)

            grounded_skills.append(
                GroundedSkill(
                    raw_text=s.raw_text,
                    category=s.category,
                    concept_id=concept_id,
                    concept_label=concept_label,
                    confidence=norm_confidence,
                    years=s.years,
                    evidence=evidence_list
                )
            )
            valid_embeddings.append(skill_emb)

            # Add to cluster
            cat_name = s.category.value if isinstance(s.category, SkillCategory) else str(s.category)
            if cat_name not in clusters:
                clusters[cat_name] = []
            if concept_id:
                clusters[cat_name].append(concept_id)
        else:
            unmapped_count += 1
            grounded_skills.append(
                GroundedSkill(
                    raw_text=s.raw_text,
                    category=s.category,
                    concept_id=None,
                    concept_label=None,
                    confidence=0.0,
                    years=s.years,
                    evidence=evidence_list
                )
            )

    # 4. Synthesize Profile Vector (Mean of all grounded skills embeddings)
    profile_vector = None
    if valid_embeddings:
        dim = len(valid_embeddings[0])
        profile_vector = [
            sum(emb[d] for emb in valid_embeddings) / len(valid_embeddings)
            for d in range(dim)
        ]

    graph = CompetencyGraph(
        skills=grounded_skills,
        clusters=clusters,
        unmapped_count=unmapped_count
    )

    return graph, profile_vector, warnings
