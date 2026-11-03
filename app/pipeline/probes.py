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
