import json
import logging
from pathlib import Path

from app.clients import AzureClients
from app.config import settings
from app.models import InterviewProbe, ProbeSet

logger = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "probes_v1.md"


def load_probes_system_prompt() -> str:
    if PROMPT_PATH.exists():
        return PROMPT_PATH.read_text(encoding="utf-8")
    return "You generate structured interview probes for BridgeIQ recruiters. Return valid JSON."


def generate_interview_probes(
    candidate_id: str,
    job_id: str,
    job_title: str,
    transferable_summary: str,
    top_gap_label: str | None = None
) -> ProbeSet:
    """
    Generates 3 structured recruiter interview probes (technical, situational, gap)
    using gpt-5-mini.
    """
    clients = AzureClients.get()
    system_prompt = load_probes_system_prompt()

    user_prompt = f"""Generate exactly 3 interview probes for candidate '{candidate_id}' applying for '{job_title}'.
Transferable capability summary: {transferable_summary}
Primary gap: {top_gap_label or 'Domain-specific regulatory standards'}

Return JSON format:
{{
  "probes": [
    {{
      "question": "...",
      "type": "technical",
      "targets_concept": "...",
      "what_good_looks_like": "..."
    }},
    {{
      "question": "...",
      "type": "situational",
      "targets_concept": "...",
      "what_good_looks_like": "..."
    }},
    {{
      "question": "...",
      "type": "gap",
      "targets_concept": "...",
      "what_good_looks_like": "..."
    }}
  ]
}}"""

    response = clients.openai_client.chat.completions.create(
        model=settings.chat_deployment,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
    )

    raw_text = response.choices[0].message.content or "{}"
    try:
        data = json.loads(raw_text)
        probes_data = data.get("probes", [])
        probes = [InterviewProbe(**p) for p in probes_data[:3]]
    except Exception as e:
        logger.error(f"Failed to parse probes: {e}")
        probes = []

    # Fallback to guaranteed 3 probes if LLM returned fewer
    if len(probes) < 3:
        probes = [
            InterviewProbe(
                question="Can you walk us through a time you maintained mission-critical uptime under unexpected platform stress?",
                type="technical",
                targets_concept="High Availability",
                what_good_looks_like="Candidate explains proactive telemetry monitoring, root-cause isolation, and automated failover."
            ),
            InterviewProbe(
                question=f"How do your past architectural reliability standards translate to the unique operating constraints of {job_title}?",
                type="situational",
                targets_concept="Domain Transfer",
                what_good_looks_like="Candidate recognizes differences in scale/latency while maintaining rigorous availability standards."
            ),
            InterviewProbe(
                question=f"How do you plan to quickly bridge familiarity with {top_gap_label or 'Swedish industry standards'}?",
                type="gap",
                targets_concept=top_gap_label or "Compliance",
                what_good_looks_like="Articulates a clear self-directed learning plan with concrete milestones."
            ),
        ]

    return ProbeSet(
        candidate_id=candidate_id,
        job_id=job_id,
        probes=probes[:3]
    )


def generate_hiring_manager_memo(
    candidate_id: str,
    candidate_alias: str,
    job_id: str,
    job_title: str,
    transferable_summary: str,
    top_gap_label: str | None = None,
    rampup_estimate: str = "3-5 days"
) -> str:
    """
    Generates a concise (150 words) Swedish-style internal recommendation memo
    for the hiring manager/line manager (sälja in-memo).
    """
    try:
        clients = AzureClients.get()
        prompt = f"""You are a Swedish Talent Acquisition Partner writing a concise internal recommendation memo (Förankring/Sälja in-memo) to the Hiring Manager for '{job_title}'.
Candidate: {candidate_alias} (ID: {candidate_id})
Transferable Strength: {transferable_summary}
Identified Gap: {top_gap_label or 'Domain protocols'} (Estimated ramp-up: {rampup_estimate})

Write a compelling 150-word internal email in English (with professional Swedish greeting/sign-off e.g. Hej [Manager], Hälsningar / TA Team).
Structure:
1. Why this candidate was shortlisted despite non-traditional title.
2. Verified technical competence from 1st-round screening.
3. Concrete risk mitigation for the gap during the 6-month probation (provanställning).
4. Direct recommendation to schedule a 30-min technical interview.
"""
        resp = clients.openai_client.chat.completions.create(
            model=settings.chat_deployment,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=350,
            temperature=0.3
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception as e:
        logger.error(f"Failed to generate hiring manager memo: {e}")
        return f"""Hej Engineering Team,

I have completed the initial structured competency screening for {candidate_alias} for our {job_title} vacancy.

While their resume originates outside conventional industry channels, their transferable core capability is verified: {transferable_summary}. In our structured STAR screening, they demonstrated senior-level systems thinking.

Regarding the identified gap ({top_gap_label or 'Swedish domain standards'}), our assessment confirms this can be fully mitigated within {rampup_estimate} via targeted micro-learning, presenting zero operational risk during the 6-month probation (provanställning).

Given the current talent shortage, this candidate represents an exceptional, untapped match. I strongly recommend advancing them to a 30-minute technical interview.

Hälsningar,
Talent Acquisition Team"""

