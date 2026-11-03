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
    concept_type: str                    # e.g. "skill", "occupation-name"
    broader_id: str | None = None        # parent concept, used for radar axes


class JobRequirement(BaseModel):
    concept_id: str
    label: str
    importance: Literal["must", "nice"] = "must"
    jd_clause: str                       # exact sentence from the JD that states it


class JobPosting(BaseModel):
    job_id: str
    title: str
    employer: str
    location: str | None = None
    sector: str | None = None            # IT, manufacturing, connectivity, services
    description: str
    requirements: list[JobRequirement] = []   # precomputed in M1
    language: Literal["sv", "en"] = "sv"


# ---------- Candidate side ----------

class Evidence(BaseModel):
    quote: str = Field(..., description="Verbatim substring of the CV text")
    char_start: int | None = None        # filled by the verifier, not the LLM


class GroundedSkill(BaseModel):
    raw_text: str                        # as written in the CV
    category: SkillCategory
    concept_id: str | None = None        # None = could not ground (unmapped)
    concept_label: str | None = None
    confidence: Score                    # combined score
    years: float | None = None
    evidence: conlist(Evidence, min_length=1, max_length=5)


class CompetencyGraph(BaseModel):
    skills: list[GroundedSkill]
    clusters: dict[str, list[str]] = {}  # broader concept label -> concept_ids
    unmapped_count: int = 0


class CandidateProfile(BaseModel):
    id: str                              # Cosmos id, e.g. "cand-042"
    candidate_id: str                    # partition key (same value as id)
    display_name: str                    # synthetic alias only, e.g. "Candidate 042"
    source: Literal["starter", "pasted"] = "pasted"
    headline: str | None = None          # non-standard title
    past_titles: list[str] = []
    cv_text: str                         # PII-scrubbed text
    competency_graph: CompetencyGraph | None = None
    profile_vector: list[float] | None = None   # 1536-dim
    created_at: datetime = Field(default_factory=datetime.utcnow)
    schema_version: int = 1


# ---------- Matching ----------

class ScoreBreakdown(BaseModel):
    coverage: Score          # weighted share of job's must-have concepts matched
    semantic: Score          # normalised hybrid search score
    title_similarity: Score  # cosine(candidate past titles, job title)
    composite: Score         # 0.6*coverage + 0.4*semantic


class MatchResult(BaseModel):
    id: str                              # f"{candidate_id}__{job_id}"
    candidate_id: str                    # partition key of `matches`
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
    what_good_looks_like: str            # 1–2 sentence rubric


class ProbeSet(BaseModel):
    candidate_id: str
    job_id: str
    probes: conlist(InterviewProbe, min_length=3, max_length=3)


MatchResult.model_rebuild()
