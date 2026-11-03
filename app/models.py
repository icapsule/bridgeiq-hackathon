from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, confloat, conlist

Score = confloat(ge=0.0, le=1.0)


class SkillCategory(str, Enum):
    technical = "technical"
    domain = "domain"
    soft = "soft"
    certification = "certification"
    language = "language"


# ---------- Taxonomy & jobs (read-only, from AI Search) ----------

class TaxonomyConcept(BaseModel):
    concept_id: str                      # JobTech concept id, e.g. "aBcD_123"
    preferred_label: str                 # Swedish label, e.g. "Hög tillgänglighet"
    label_en: str | None = None          # English label/translation if available
    concept_type: str = "skill"          # e.g. "skill", "occupation-name"
    broader_id: str | None = None        # parent concept


class JobRequirement(BaseModel):
    concept_id: str
    label: str
    importance: Literal["must", "nice"] = "must"
    jd_clause: str                       # exact sentence from the JD


class JobPosting(BaseModel):
    job_id: str
    title: str
    employer: str
    location: str | None = None
    sector: str | None = None
    description: str
    requirements: list[JobRequirement] = []
    taxonomy_ids: list[str] = []
    language: Literal["sv", "en"] = "sv"


# ---------- Extraction Schemas (LLM Structured Outputs) ----------

class RawExtractedSkill(BaseModel):
    raw_text: str = Field(..., description="Concise statement of the skill or experience")
    category: SkillCategory
    years: float | None = Field(None, description="Estimated years of experience if mentioned")
    evidence_quote: str = Field(..., description="Exact verbatim substring quote from the CV text")
    search_terms_sv: list[str] = Field(
        ...,
        description="1 to 3 Swedish search phrases translating this skill for Swedish JobTech taxonomy search"
    )
    search_terms_en: list[str] = Field(
        ...,
        description="1 to 3 English keywords describing this skill"
    )


class LLMExtractResponse(BaseModel):
    skills: list[RawExtractedSkill] = Field(..., max_length=25)


class ExtractSkillsRequest(BaseModel):
    cv_text: str
    candidate_id: str | None = None
    display_name: str | None = None


# ---------- Candidate side ----------

class Evidence(BaseModel):
    quote: str = Field(..., description="Verbatim substring of the CV text")
    char_start: int | None = None        # filled by the verifier


class GroundedSkill(BaseModel):
    raw_text: str
    category: SkillCategory
    concept_id: str | None = None        # None = could not ground (unmapped)
    concept_label: str | None = None
    confidence: Score                    # normalised matching score
    years: float | None = None
    evidence: list[Evidence] = Field(default_factory=list)


class CompetencyGraph(BaseModel):
    skills: list[GroundedSkill]
    clusters: dict[str, list[str]] = {}  # broader category -> concept_ids
    unmapped_count: int = 0


class CandidateProfile(BaseModel):
    id: str                              # Cosmos id, e.g. "candidate-001"
    partition_key: str = "synthetic-candidates"
    candidate_id: str                    # identifier
    display_name: str                    # alias, e.g. "Candidate 101"
    source: Literal["starter", "pasted"] = "pasted"
    headline: str | None = None
    past_titles: list[str] = []
    cv_text: str                         # scrubbed text
    competency_graph: CompetencyGraph | None = None
    profile_vector: list[float] | None = None   # 1536-dim
    created_at: datetime = Field(default_factory=datetime.utcnow)
    schema_version: int = 1


class ExtractSkillsResponse(BaseModel):
    candidate_id: str
    display_name: str
    competency_graph: CompetencyGraph
    warnings: list[str] = []


# ---------- Matching ----------

class ScoreBreakdown(BaseModel):
    coverage: Score          # weighted share of job's must-have concepts matched
    semantic: Score          # normalised hybrid search score
    title_similarity: Score  # cosine(candidate past titles, job title)
    composite: Score         # 0.6*coverage + 0.4*semantic


class MatchResult(BaseModel):
    id: str                              # f"{candidate_id}__{job_id}"
    partition_key: str = "matches"
    candidate_id: str                    # candidate id
    job_id: str
    job_title: str
    scores: ScoreBreakdown
    matched_concepts: list[str] = []     # concept_ids
    missing_concepts: list[str] = []     # must-have concept_ids not covered
    gap_pct: Score                       # 1 - coverage
    hidden_gem: bool = False
    badge: str | None = None             # "Hidden Gem: 88% Competence Overlap"
    rationale: ExplainabilityRationale | None = None
    computed_at: datetime = Field(default_factory=datetime.utcnow)


# ---------- Explainability ----------

class EvidenceLink(BaseModel):
    jd_clause: str                       # verbatim from job description
    candidate_evidence: str              # verbatim from CV
    concept_label: str
    explanation: str                     # 1 sentence
    verified: bool = False               # set by code after substring check


class GapItem(BaseModel):
    concept_id: str
    label: str                           # e.g. "NIS2-direktivet"
    why_it_matters: str
    bridging_strategy: str               # exactly one sentence
    effort: Literal["days", "weeks", "months"] = "days"


class ExplainabilityRationale(BaseModel):
    employer_summary: str                # <= 60 words
    evidence_chain: list[EvidenceLink] = Field(default_factory=list)
    candidate_why_you_fit: str           # <= 60 words
    gaps: list[GapItem] = Field(default_factory=list)
    transferable_story: str              # e.g. "Telecom core HA → industrial IoT uptime"


class InterviewProbe(BaseModel):
    question: str
    type: Literal["technical", "situational", "gap"]
    targets_concept: str
    what_good_looks_like: str


class ProbeSet(BaseModel):
    candidate_id: str
    job_id: str
    probes: conlist(InterviewProbe, min_length=3, max_length=3)


MatchResult.model_rebuild()
