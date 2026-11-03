# 🎯 AISpire Hackathon: Product & Architectural Kickoff Brief
> **Target Audience / Purpose**: Master input document for Opus to generate a comprehensive, execution-ready `requirement.md` / PRD.  
> **Challenge**: Build an AI-Powered Hidden Talent Tool Bridging the Gap Between Talent & Jobs  
> **Hosts / Partners**: Avanade · Accenture · Microsoft  
> **Target Ecosystem**: Swedish Labour Market (JobTech Taxonomy, Sweden Central, EU Data Zone)  
> **Project Working Title**: **BridgeIQ (The Hidden Talent Intelligence Box)**

---

## 1. Executive Context & Core Mission

### 1.1 The Challenge Statement
> *"Every day the right person and the right job pass each other by — not because the competence is missing, but because no one translates."*

Thousands of candidates have the requisite competencies, but their experiences are articulated in non-standard, cross-industry, or international terminology that mismatches how enterprise ATS and hiring managers search.  
The challenge is to build an **Azure-native AI tool** that surfaces "Hidden Talent" by deconstructing raw experiences into standardized competence graphs, performing title-agnostic matching against live vacancies, and providing transparent, trustworthy explanations to both sides.

### 1.2 Core Data Points & Market Urgency (The "Why")
* **73% of Swedish employers** struggle to find the skilled talent they need *(ManpowerGroup Talent Shortage Survey, 2026)*.
* **58% of qualified jobseekers** report being rejected despite meeting requirements due to rigid keyword screening *(University of Phoenix, 2026)*.
* **48% of hiring decision-makers** admit passing on skilled candidates simply because applicants struggle to demonstrate their skills clearly in CVs *(University of Phoenix, 2026)*.
* **Foreign Education & Experience Barrier**: Swedish employers find international credentials and non-local job titles difficult to verify and contextualize *(Vinnova Research)*.
* **ATS Overload**: Recruiters read hundreds of CVs daily, relying on blunt keyword filters that discard transferable and non-traditional talent *(HiringThing, 2026)*.

---

## 2. Core Paradigm: The "AI Box" Concept

Rather than a simple conversational chatbot or a brittle multi-agent swarm, the product is modeled as a centralized **Intelligent Brokerage "AI Box"** serving a three-party triad:

```
      [ 👤 1. Jobseeker ]                      [ 🏢 2. Employer ]
      • Non-standard / Foreign CV              • Hard-to-fill vacancies
      • Keyword-filtered out                   • 73% talent shortage
             │                                        │
             ▼                                        ▼
    ┌────────────────────────────────────────────────────────┐
    │              THE "AI BOX" (BridgeIQ Engine)            │
    │                                                        │
    │  1. Competency Extraction & Grounding (JobTech Map)    │
    │  2. Title-Agnostic Hybrid Retrieval (Azure AI Search)  │
    │  3. Dual-Sided Explainable Synthesis & Gap Remediation │
    └────────────────────────────────────────────────────────┘
                                ▲
                                │
                 [ 💼 3. Recruiter / TA Specialist ]
                 • High screening noise & manual fatigue
                 • Consumes: Match Radar & Interview Probes
```

---

## 3. Official Lab Infrastructure & Starter Datasets

The solution **MUST** strictly leverage the pre-provisioned Azure sandbox:

### 3.1 Pre-Provisioned Azure Stack
* **Azure AI Foundry (Project: `hidden-talent`)**:
  * Chat & Reasoning: **`gpt-5-mini`**
  * Vector Embedding: **`text-embedding-3-small`**
* **Azure AI Search**:
  * Pre-configured indexes: **`jobs`** (job vacancies) and **`taxonomy`** (skills concepts)
  * Capabilities: **Hybrid Search (Keyword / BM25 + Vector Similarity)**
* **Azure Cosmos DB (Database: `hidden-talent`)**:
  * Containers: **`candidates`** (candidate profiles) and **`matches`** (computed matching graphs)
* **Azure Storage**:
  * Container: **`datasets`** (raw starter datasets)
* **Azure Container Apps**:
  * Pre-provisioned placeholder starter page (target for containerized deployment)
* **Identity & Compliance**:
  * Managed Identities for secure zero-credential cross-resource access
  * Deployment Region: `Sweden Central` (Search: `North Europe`), strictly processed within **EU Data Zone**

### 3.2 Starter Datasets Provided
1. **200 Swedish Job Postings**: Real-world job descriptions spanning IT, manufacturing, connectivity, and services.
2. **1,248 JobTech Taxonomy Concepts**: The official national skill ontology published by the Swedish Public Employment Service (*Arbetsförmedlingen*).
3. **100 Fictional English Candidate Profiles**: Synthetic resumes covering diverse backgrounds (e.g., international telecom engineers, career switchers, non-standard titles).

### 3.3 Strict Hackathon Guardrails
* ⛔ **Synthetic Data ONLY**: Strictly prohibited to upload real CVs or any personally identifiable information (PII).
* ⛔ **Zero Credential Leaks**: Never commit API keys, connection strings, or tokens to GitHub.
* ⏱️ **Deadline & Cost**: Ephemeral environment active until Friday EOD; minimize redundant GPU/cloud resources.

---

## 4. Architectural Pattern: The Agentic RAG Pipeline

### 4.1 Rejection of Anti-Patterns
* **No Massive Single Prompt**: Dumping 200 jobs + 1,248 taxonomy items into an LLM context blows up token limits, introduces hallucination, and ignores pre-built Azure AI Search indexes.
* **No Unbounded Multi-Agent Loops**: Over-engineered autonomous agent swarms (e.g. CrewAI/AutoGen) introduce latency (>60s per match) and demo instability under live judging.

### 4.2 The 4-Stage Operational Flow
1. **Stage 1: Competency Extraction & Grounding (`Extract & Ground Agent`)**
   * LLM extracts raw technical, domain, and soft skills from candidate text.
   * Embeds extracted skills using `text-embedding-3-small`.
   * Vector-searches the `taxonomy` index in Azure AI Search to map raw expressions into standardized Swedish JobTech concepts.
2. **Stage 2: Title-Agnostic Hybrid Retrieval (`Hybrid Retrieval Engine`)**
   * Uses standardized JobTech vector representations to query the `jobs` index.
   * Executes **Hybrid Search** (vector similarity + keyword scoring) to surface jobs based on *functional competence*, not *job titles* (e.g., matching a Telecom Core Network engineer to an Industrial IoT Reliability role).
3. **Stage 3: Explainable Synthesis & Gap Remediation (`Reasoning Agent`)**
   * `gpt-5-mini` calculates composite fit and generates dual-sided transparent explanations:
     * *For Employer*: Evidence-based rationale linking past candidate achievements to specific JD requirements.
     * *For Candidate*: Actionable "15% gap analysis" with specific micro-upskilling recommendations.
4. **Stage 4: Persistence & Interactive Copilot UI**
   * Match vectors and reasoning payloads stored in Cosmos DB (`matches`).
   * Rendered in a responsive Dual-View Dashboard deployed on Azure Container Apps.

---

## 5. Tri-Party User Stories & Acceptance Criteria

### Epic 1: Jobseeker Journey (Translation & Enablement)
* **US-1.1: Non-Standard CV Skill Translation**
  * *As an* international or career-transitioning jobseeker,
  * *I want to* submit my raw, non-Swedish CV and have AI extract and map my experience to official Swedish JobTech taxonomy standards,
  * *So that* my actual competencies are visible to Swedish hiring managers without being rejected by ATS keyword filters.
  * **Acceptance Criteria**: System maps raw input (e.g., "10 years core network high availability") to verified JobTech tags (`Distribuerade system`, `Hög tillgänglighet`) with confidence scores.
* **US-1.2: Cross-Industry Title-Agnostic Matching**
  * *As a* jobseeker with transferable capabilities,
  * *I want to* discover job vacancies matched on core problem-solving capability rather than my previous exact job title,
  * *So that* I uncover lucrative, high-fit opportunities I didn't realize I qualified for.
  * **Acceptance Criteria**: System returns Top 3–5 vacancies with a "Why You Fit" breakdown citing specific past experiences.
* **US-1.3: The 15% Gap Remediation Roadmap**
  * *As a* candidate reviewing a recommended vacancy,
  * *I want to* see the precise 10%–20% skill gap preventing a 100% match and receive actionable closing advice,
  * *So that* I can upskill strategically instead of receiving silent rejections.
  * **Acceptance Criteria**: AI highlights specific missing local certifications/skills (e.g. NIS2 / Swedish regulatory familiarity) and suggests a 1-sentence bridging strategy.

### Epic 2: Employer Journey (De-biasing & Hidden Gem Discovery)
* **US-2.1: Surfacing "Hidden Gems"**
  * *As a* Swedish hiring manager facing severe talent shortages,
  * *I want to* select my open requisition and instantly surface high-competency candidates whose resumes lack conventional titles,
  * *So that* I can interview qualified talent invisible to competitors.
  * **Acceptance Criteria**: Queries return non-obvious candidates with clear `[Hidden Gem: 88% Competence Overlap]` badges.
* **US-2.2: Evidence-Based Match Rationale**
  * *As a* hiring decision-maker reviewing candidates,
  * *I want to* review a bulleted evidence chain mapping candidate achievements directly to our JD clauses,
  * *So that* I can make unbiased, rapid interview screening decisions in under 30 seconds.
  * **Acceptance Criteria**: Every recommended profile displays 3 verifiable claim-to-evidence links.

### Epic 3: Recruiter Journey (Noise Reduction & Screening Augmentation)
* **US-3.1: Visual Competency Radar & Multi-Job Triaging**
  * *As a* corporate recruiter or talent acquisition specialist,
  * *I want to* view a multi-dimensional radar chart comparing candidate capabilities against multiple open vacancies,
  * *So that* I can redirect high-potential applicants to the highest-need business units.
* **US-3.2: Automated High-Signal Interview Probe Generator**
  * *As a* recruiter conducting initial phone screens,
  * *I want* AI to generate 3 targeted technical and situational probe questions based on verified transferable skills and identified gaps,
  * *So that* I can validate candidate depth in a 15-minute screen.

---

## 6. Recommended Technical & Implementation Stack

To ensure a production-grade, demo-ready submission by Friday EOD:

| Layer | Recommended Technology | Justification |
| :--- | :--- | :--- |
| **LLM & Reasoning** | Azure AI Foundry (`gpt-5-mini`) | Pre-provisioned; fast inference, strong structured JSON output. |
| **Embeddings** | `text-embedding-3-small` | 1536-dim vector representation for skills and job ads. |
| **Vector & Search** | Azure AI Search (Hybrid BM25 + Vector) | Native index already hosts 1,248 JobTech concepts & 200 jobs. |
| **Database** | Azure Cosmos DB (NoSQL API) | Pre-configured `candidates` & `matches` containers for fast document retrieval. |
| **Backend API** | Python 3.11+ / FastAPI | High-speed async, native Azure SDK support (`azure-search-documents`, `azure-cosmos`). |
| **Frontend UI** | Streamlit OR Next.js 15 (Tailwind CSS) | Instant interactive dashboard supporting Dual-View (Jobseeker vs Employer). |
| **Deployment** | Docker & Azure Container Apps | Pre-provisioned Container App environment; clean CI/CD via GitHub. |

---

## 7. Direct Prompt / Instructions for Opus

> **Prompt Directive for Claude Opus**:
> *"You are the Lead Systems Architect and Product Director for an AI innovation team at the AISpire Hackathon. Based on the complete Kickoff Brief above, generate an exhaustive, professional, and engineering-ready **`requirement.md`**.*  
> *The output must include:*
> 1. **System Topology & Architecture Diagram (Mermaid)** showing data flow between Azure Foundry, AI Search, Cosmos DB, and Container Apps.
> 2. **Pydantic / TypeScript Data Contracts** (Schemas for `CandidateProfile`, `CompetencyGraph`, `JobPosting`, `MatchResult`, and `ExplainabilityRationale`).
> 3. **API Endpoint Specifications** (`/api/v1/extract-skills`, `/api/v1/match-jobs`, `/api/v1/explain-match`, `/api/v1/generate-probes`).
> 4. **Concrete 48-Hour Implementation Task DAG** broken into 4 modular milestones with verify commands.
> 5. **3-Minute High-Impact Demo Pitch Script** tailored for Microsoft / Avanade judges highlighting Explainability and EU compliance."*

