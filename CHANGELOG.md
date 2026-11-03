# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **#T0.1**: Initialized public Git repository (`icapsule/bridgeiq-hackathon`) with strict zero-leak `.gitignore` protecting credentials.
- **#T0.2**: Configured GitHub Actions CI/CD workflow (`.github/workflows/ci-cd.yml`) to automatically run Ruff linting, Pytest test suites, and Docker builds targeting GitHub Container Registry (`ghcr.io`).
- **#T0.3**: Implemented Pydantic v2 core data contracts in `app/models.py` for JobTech taxonomy concepts, candidate competency graphs, deterministic match results, and explainability rationales.
- **#T0.4**: Implemented deterministic scoring algorithm (`app/pipeline/score.py`) with weighted must-have coverage, composite calculation, and automated `Hidden Gem` detection (`coverage >= 0.75 AND title_similarity < 0.45`).
- **#T0.5**: Added PII detection and redaction guardrail (`app/guardrails/pii.py`) targeting Swedish Personnummer, emails, and phone numbers.
- **#T0.6**: Added quote substring claim verifier (`app/guardrails/verify.py`) to eliminate LLM citation hallucinations.
- **#T0.7**: Built FastAPI service entrypoint (`app/main.py`) with `/healthz` liveness probes and execution timing middleware.
- **#T0.8**: Created interactive multi-perspective Streamlit dashboard (`ui/streamlit_app.py`) covering Jobseeker, Employer, Recruiter, and Architecture views with modern Glassmorphic styling.
- **#T0.9**: Engineered production `Dockerfile` and `start.sh` unifying FastAPI (port 8000) and Streamlit (port 8501) inside a single lightweight container.

---

## [0.1.0] - 2026-11-03

### Added
- Milestone 0: Core foundations, Azure identity wiring, container packaging, and CI/CD automation pipeline.
