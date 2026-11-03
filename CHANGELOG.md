# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **#T2.1-T2.5**: Implemented Stage 2 Title-Agnostic Hybrid Retrieval & Deterministic Ranking in `app/pipeline/retrieve.py`, querying Azure AI Search `jobs` index with profile vectors and JobTech concept terms, calculating composite coverage, and exposing `POST /api/v1/match-jobs`.
- **#T3.1-T3.3**: Implemented Stage 3 Explainable Synthesis with Machine-Checked Verifier in `app/pipeline/explain.py`, generating bidirectional rationales, verifiable claim-to-evidence links, and low-barrier gap bridging roadmaps, exposed via `POST /api/v1/explain-match`.
- **#T4.1**: Implemented Recruiter Interview Probes generator in `app/pipeline/probes.py` with structured evaluation rubrics across Technical, Situational, and Gap categories, exposed via `POST /api/v1/generate-probes`.
- **#T4.2**: Integrated complete end-to-end pipeline into `ui/streamlit_app.py` with interactive candidate-job matching, live evidence links, and interview probe accordions.
- **#T4.3**: Expanded automated test suite with unit tests in `tests/test_retrieve.py` and `tests/test_explain.py` (14/14 tests passing).

---

## [0.1.0] - 2026-11-03

### Added
- Milestone 0: Core foundations, Azure identity wiring, container packaging, and CI/CD automation pipeline.
- Milestone 1: Stage 1 Extract & Ground pipeline against 1,248 Swedish JobTech taxonomy concepts and REST endpoints.
