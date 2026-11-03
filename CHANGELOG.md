# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **#T4.10**: Designed and implemented Claude Prototype-inspired 3-Column **Employer Screen & Decision Engine** (`ui/streamlit_app.py` & `app/pipeline/benchmarks.py`).
- **#T4.11**: Implemented **Multi-Dimensional Quantitative Representation** with explicit colored progress bars and mathematical formula display:
  - Competence Coverage ($Cov \in [0, 1]$, Teal `#0B6B63`).
  - Semantic Fit ($Sem \in [0, 1]$, Blue `#3C7DD9`).
  - Title Similarity ($TSim \in [0, 1]$, Amber `#B76E00`, highlighting cross-domain hidden gems).
  - Explicit deterministic formula card: `composite = 0.60 * cov + 0.40 * sem`.
- **#T4.12**: Integrated interactive **Candidate Selection & Shortlisting Workflow**:
  - Open Roles Navigator across 3 flagship Swedish benchmark roles (IoT Reliability in Västerås, OT Security in Luleå, Production Planning in Jönköping) plus 200 Azure AI Search live jobs.
  - One-click `[x] Show only hidden gems` filter.
  - Interactive candidate shortlist button (`➕ Shortlist for Interview` $\leftrightarrow$ `✓ Shortlisted for Interview`) with persistent session state.
  - Verifiable Dual-Quote Evidence Chain ("Job ad requires" vs "Candidate delivered" + "Why it matches" reasoning).
  - Quantified Gap-to-Close breakdown with time-to-onboard effort badges (`days`, `weeks`, `months`) and concrete bridging strategies.
  - Traditional Keyword ATS vs. BridgeIQ Comparison Expander (illustrating why Amara is #94 in ATS vs #1 in BridgeIQ).
  - Dynamic Interview Probes Generator in Recruiter Tab with live Azure OpenAI `gpt-5-mini` support.
- **#T4.13**: Added test coverage in `tests/test_benchmarks.py` covering deterministic composite scoring, hidden gem identification, and evidence quote structures (17 passing tests).

### Fixed
- **#T4.14**: Resolved raw HTML (`<div>` / `<span>`) code block rendering escape bug in Streamlit by creating `render_html` sanitizer. Eliminates leading indentation (>= 4 spaces) and internal blank lines that previously triggered CommonMark `<pre><code>` block parsing in candidate and evidence cards.

### Security
- **#T4.15**: Restricted public documentation exposure in `.gitignore` to `Docs/hackathon-plan.md` only; untracked internal drafts, kickoff briefs, and brainstorm documents from Git before repository sharing.

---

## [0.2.0] - 2026-11-03

### Added
- **#T4.4**: Created interactive **Pitch Demonstration Center** in `ui/streamlit_app.py` with 3 flagship archetypes:
  1. *Amara*: Ex-Telecom Core Network Engineer (Lagos) ➔ Industrial IoT Site Reliability Engineer (💎 Hidden Gem).
  2. *Marcus (cand-021)*: Sports Club Volunteer ➔ Warehouse Logistics Specialist (🔄 Career Pivot).
  3. *Samira (cand-051)*: Self-Taught Python Scripting ➔ Junior QA Automation / Developer (⚡ Skills Over Degrees).
- **#T4.5**: Added automatic **Pre-Click Demonstration Briefing & Judge Talking Points** in the UI, providing presenters with immediate ATS blindspot breakdowns, BridgeIQ breakthrough evidence, and spoken talking tracks before executing live runs.
- **#T4.6**: Integrated dynamic loader for all 100 official Microsoft Cosmos DB synthetic candidate profiles from Azure Blob Storage (`candidates.json`) with persistent results caching.

### Fixed
- **#T4.7**: Removed custom `temperature` parameters in `app/pipeline/extract.py`, `app/pipeline/explain.py`, and `app/pipeline/probes.py` to ensure complete compatibility with Azure OpenAI `gpt-5-mini` deployment.
- **#T4.8**: Resolved `ModuleNotFoundError: No module named 'app'` by explicitly configuring `PYTHONPATH="/app"` in `Dockerfile`, `start.sh`, and injecting workspace root into `sys.path` in `ui/streamlit_app.py`.
- **#T4.9**: Fixed `DefaultAzureCredential` 400 invalid_scope authentication failure by binding User-Assigned Managed Identity Client ID (`e30be7ef-2179-4700-b542-f2f4abbd1d20`) across `app/clients.py`, `app/config.py`, `Dockerfile`, `start.sh`, and Azure Container Apps environment variables.

---

## [0.1.0] - 2026-11-03

### Added
- Milestone 0: Core foundations, Azure identity wiring, container packaging, and CI/CD automation pipeline.
- Milestone 1: Stage 1 Extract & Ground pipeline against 1,248 Swedish JobTech taxonomy concepts and REST endpoints.
