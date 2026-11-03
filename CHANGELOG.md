# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **#T4.4**: Created interactive **Pitch Demonstration Center** in `ui/streamlit_app.py` with 3 flagship archetypes:
  1. *Amara*: Ex-Telecom Core Network Engineer (Lagos) ➔ Industrial IoT Site Reliability Engineer (💎 Hidden Gem).
  2. *Marcus (cand-021)*: Sports Club Volunteer ➔ Warehouse Logistics Specialist (🔄 Career Pivot).
  3. *Samira (cand-051)*: Self-Taught Python Scripting ➔ Junior QA Automation / Developer (⚡ Skills Over Degrees).
- **#T4.5**: Added automatic **Pre-Click Demonstration Briefing & Judge Talking Points** in the UI, providing presenters with immediate ATS blindspot breakdowns, BridgeIQ breakthrough evidence, and spoken talking tracks before executing live runs.
- **#T4.6**: Integrated dynamic loader for all 100 official Microsoft Cosmos DB synthetic candidate profiles from Azure Blob Storage (`candidates.json`) with persistent results caching.

### Fixed
- **#T4.7**: Removed custom `temperature` parameters in `app/pipeline/extract.py`, `app/pipeline/explain.py`, and `app/pipeline/probes.py` to ensure complete compatibility with Azure OpenAI `gpt-5-mini` deployment.

---

## [0.1.0] - 2026-11-03

### Added
- Milestone 0: Core foundations, Azure identity wiring, container packaging, and CI/CD automation pipeline.
- Milestone 1: Stage 1 Extract & Ground pipeline against 1,248 Swedish JobTech taxonomy concepts and REST endpoints.
