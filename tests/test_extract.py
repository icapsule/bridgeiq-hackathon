from app.models import (
    ExtractSkillsRequest,
    LLMExtractResponse,
    SkillCategory,
)


def test_extract_skills_request_validation():
    req = ExtractSkillsRequest(
        cv_text="10 years experienced network engineer with 5-nines SLA uptime.",
        display_name="Candidate Hero"
    )
    assert req.display_name == "Candidate Hero"
    assert len(req.cv_text) > 10


def test_llm_extract_response_parsing():
    sample_json = {
        "skills": [
            {
                "raw_text": "Maintained 99.999% uptime",
                "category": "technical",
                "years": 10.0,
                "evidence_quote": "Kept a 4G/5G packet core at 99.999% uptime",
                "search_terms_sv": ["hög tillgänglighet", "systemdrift"],
                "search_terms_en": ["high availability", "uptime"]
            }
        ]
    }
    parsed = LLMExtractResponse(**sample_json)
    assert len(parsed.skills) == 1
    skill = parsed.skills[0]
    assert skill.category == SkillCategory.technical
    assert "hög tillgänglighet" in skill.search_terms_sv
    assert skill.years == 10.0
