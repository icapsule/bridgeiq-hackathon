from app.models import EvidenceLink, ExplainabilityRationale, GapItem, InterviewProbe, ProbeSet


def test_explainability_rationale_schema():
    link = EvidenceLink(
        jd_clause="Ansvarar för driftsäkerhet i våra IoT-plattformar.",
        candidate_evidence="Kept a 4G/5G packet core at 99.999% uptime",
        concept_label="Hög tillgänglighet",
        explanation="Telecom core reliability exceeds platform requirements.",
        verified=True
    )
    gap = GapItem(
        concept_id="nis2_001",
        label="NIS2-direktivet",
        why_it_matters="Critical infrastructure regulation.",
        bridging_strategy="Complete a 2-day self-paced NIS2 fundamentals course.",
        effort="days"
    )
    rationale = ExplainabilityRationale(
        employer_summary="Ten years maintaining carrier-grade packet core translates to IoT reliability.",
        evidence_chain=[link],
        candidate_why_you_fit="Your high-availability experience is exactly what this IoT team needs.",
        gaps=[gap],
        transferable_story="Telecom core HA → industrial IoT platform uptime"
    )

    assert len(rationale.evidence_chain) == 1
    assert rationale.evidence_chain[0].verified is True
    assert rationale.gaps[0].effort == "days"


def test_probe_set_schema():
    probe = InterviewProbe(
        question="Can you describe an unexpected failover incident?",
        type="technical",
        targets_concept="High Availability",
        what_good_looks_like="Candidate explains automated isolation."
    )
    probe_set = ProbeSet(
        candidate_id="cand-001",
        job_id="job-077",
        probes=[probe, probe, probe]
    )
    assert len(probe_set.probes) == 3
    assert probe_set.probes[0].type == "technical"
