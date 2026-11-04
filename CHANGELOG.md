# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **#T4.21**: Comprehensive Enterprise UI/UX Redesign & Production Hardening (`ui/streamlit_app.py`, `ui/theme.py`, `.streamlit/config.toml`, `.env.example`):
  - **LinkedIn-Style Pure Typographic Wordmark**: Replaced dual-ring SVG with high-contrast text badge `Bridge` (`#0B6B63`) + `[IQ]` (inverted white-on-emerald capsule) for crisp 4K presentation rendering.
  - **Native Streamlit Theme & React Aria Tabs**: Configured `.streamlit/config.toml` with `primaryColor = "#0B6B63"` to eradicate default `#FF4B4B` orange line natively; implemented React Aria hardware-accelerated zero-reflow active tab scaling (`transform: scale(1.06)`).
  - **Navigation De-cluttering & Hero Strips**: Streamlined tabs to punchy names (`👤 Jobseeker`, `💼 Recruiter Workspace`, `📊 Azure Cloud Assets`); added role cockpit hero strips across both main views.
  - **Enterprise Design Tokens (`ui/theme.py`)**: Centralized WCAG AA-compliant color palettes and helper formatters (`safe_text`, `nordic_quote`) eliminating color drift.
  - **Permanent ATS Blindspot Proof**: Unfolded Traditional Keyword ATS comparison table into permanently visible, uncollapsed enterprise proof cards in both Jobseeker and Recruiter views.
  - **Global Enterprise Footer & Attribution Cleanup**: Deployed global fixed-base footer with `Team 04` copyright, `Accenture · Microsoft AISpire Hackathon` branding, EU AI Act Art. 14 compliance badges, and 100% eradication of legacy "Avanade" references across code and documentation.
  - **Endpoint & Secret Redaction**: Sanitized `.env.example` with standard `<your-...>` placeholders across all Azure resources (OpenAI, AI Search, Cosmos DB, Storage) to prevent endpoint leakage on GitHub.
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
- **#T4.16**: Documented UI Optimization **Path A** architectural roadmap in `README.md` (embedded force-directed competency graph, dual-layer ATS radar, zero-hallucination evidence drawer, judge presentation stepper).
- **#T4.17**: Redesigned and implemented authentic 3-Column **Jobseeker View & Career Radar Cockpit** (`ui/streamlit_app.py` & `app/pipeline/benchmarks.py`) with complete UI and algorithmic symmetry to Employer View:
  - Column 1: Verified Competence Passport, Swedish JobTech taxonomy grounding tags, Privacy Shield indicator, and 1-click discovery CTA.
  - Column 2: Ranked Matched Opportunities with `Untapped Career Pivot` (Hidden Gem) badges, keyword ATS rejection warnings, and interactive role selection.
  - Column 3: Opportunity Decision & Evidence Center featuring transferable story callouts, quantitative progress bars ($Cov$, $Sem$, $TSim$), deterministic composite formula, verifiable dual-quote evidence chains, constructive gap-to-close roadmaps, and live Azure OpenAI (`gpt-5-mini`) interview pitch generation.
- **#T4.18**: Added candidate-to-jobs benchmark mapping in `app/pipeline/benchmarks.py` (`get_candidate_benchmark_matches`) with comprehensive unit test coverage in `tests/test_benchmarks.py` (18 passing tests).
- **#T4.20**: Transformed Recruiter View into **Title-Agnostic Recruiter Copilot & Transferability Assessor** (`ui/streamlit_app.py` & `app/pipeline/probes.py`) tailored to Swedish hiring realities (Option A):
  - **Feature 2 (STAR Probes)**: Live structured competency-based interview probes generated by Azure OpenAI `gpt-5-mini` aligned with Swedish *Kompetensbaserad intervjumetodik*.
  - **Feature 3 (Objective & Anti-BS Rubrics)**: Dual-layer rubric cards defining "What Good Looks Like" (Green Flags) vs "Red Flags & Buzzword Warnings" for non-technical recruiters.
  - **Feature 5 (Provanställning De-risking)**: 6-month probation safety index with quantified gap ramp-up timelines (`⚡ 3 to 5 Days (Low Risk)`) and Swedish LAS risk mitigation verdicts.
  - **Feature 6 (1-Click Line Manager Pitch)**: `generate_hiring_manager_memo` function producing ready-to-send Swedish TA internal recommendation memos (Sälja in-memo) with test coverage in `tests/test_explain.py` (19 passing tests).

### Changed
- **#T4.19**: Streamlined Jobseeker View layout by removing the redundant 3 top persona showcase cards, elevating the 3-column cockpit directly into the above-the-fold view and consolidating candidate switching into the unified identity selector (`ui/streamlit_app.py`).

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
