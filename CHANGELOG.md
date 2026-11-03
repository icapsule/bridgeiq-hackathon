# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **#T1.1**: Created `app/clients.py` singleton managing unified Azure connections (`AzureOpenAI`, `SearchClient`, `CosmosClient`, `BlobServiceClient`) via passwordless `DefaultAzureCredential`.
- **#T1.2**: Developed `app/prompts/extract_v1.md` prompt for English CV skill decomposition into structured Pydantic schemas with Swedish translation search phrases.
- **#T1.3**: Implemented `app/pipeline/extract.py` performing Stage 1 Extract & Ground: PII scrub &rarr; `gpt-5-mini` extraction &rarr; batched `text-embedding-3-small` &rarr; hybrid vector/BM25 grounding on Sweden JobTech taxonomy &rarr; quote verification &rarr; profile vector generation.
- **#T1.4**: Implemented REST API endpoints in `app/routers/v1.py` for `/api/v1/extract-skills`, `/api/v1/candidates`, and `/api/v1/jobs`.
- **#T1.5**: Wired live Streamlit dashboard in `ui/streamlit_app.py` with persona selectors, real-time extraction, JobTech skill cards, and live Azure AI Search integration.
- **#T1.6**: Added unit test coverage for extraction and structured response parsing in `tests/test_extract.py` (10/10 tests passing).

---

## [0.1.0] - 2026-11-03

### Added
- Milestone 0: Core foundations, Azure identity wiring, container packaging, and CI/CD automation pipeline.
