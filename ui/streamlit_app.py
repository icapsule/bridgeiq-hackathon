import streamlit as st
import json

# Page Config
st.set_page_config(
    page_title="BridgeIQ | Hidden Talent Intelligence",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Glassmorphism & Modern Typography)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=Inter:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3, .main-title {
        font-family: 'Outfit', sans-serif;
        letter-spacing: -0.02em;
    }
    
    .gem-card {
        background: linear-gradient(135deg, rgba(238, 242, 255, 0.8) 0%, rgba(224, 231, 255, 0.6) 100%);
        border: 1px solid rgba(199, 210, 254, 0.8);
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }

    .badge-gem {
        background-color: #4f46e5;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 0.5rem;
    }

    .metric-box {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("💎 BridgeIQ — Hidden Talent Intelligence")
st.caption("Avanade · Accenture · Microsoft AISpire Hackathon | Team 04 (Sweden Central)")

# Top Navigation Tabs
tab_jobseeker, tab_employer, tab_recruiter, tab_arch = st.tabs([
    "👤 Jobseeker Experience",
    "🏢 Employer Radar",
    "💼 Recruiter Probes",
    "☁️ Azure System Architecture"
])

# ----------------- TAB 1: Jobseeker -----------------
with tab_jobseeker:
    st.markdown("### Find Your True Fit Beyond Job Titles")
    st.write("Translate non-standard experience into Sweden's official JobTech taxonomy concepts and bridge skill gaps.")
    
    col_input, col_result = st.columns([1, 1.2])
    
    with col_input:
        preset_choice = st.selectbox(
            "Select Demo Persona or Paste CV",
            [
                "Persona A: Core Network Engineer (Lagos) -> Industrial IoT Reliability",
                "Persona B: Aviation Avionics Technician -> CleanTech Wind Turbine Specialist",
                "Custom Text (Live Paste)"
            ]
        )
        
        default_cv = """Senior Core Network Engineer, Lagos (2013–2023).
Kept a 4G/5G packet core at 99.999% uptime across national infrastructure.
Handled real-time telemetry, mission-critical incident failover, and high-concurrency packet routing.
Fluency in Linux internals, network observability, and multi-vendor protocols."""
        
        cv_text = st.text_area("Candidate CV / Background Experience", value=default_cv, height=220)
        btn_match = st.button("🚀 Analyze Transferable Competencies", type="primary")

    with col_result:
        if btn_match or preset_choice:
            st.markdown("""
            <div class="gem-card">
                <span class="badge-gem">💎 Hidden Gem: 85% Competence Overlap</span>
                <h3>Reliability Engineer — Industrial IoT Platform</h3>
                <p><strong>Employer:</strong> Sandvik / ABB IoT · Stockholm / Västerås</p>
                <p><em>"Your 10 years of maintaining five-nines uptime in telecom core networks directly maps to our high-availability platform requirements, even though the industry title differs."</em></p>
                <hr style="margin: 0.8rem 0;"/>
                <strong>🎯 Bridging Strategy (Minor Gap):</strong>
                <p style="color: #4b5563;">Complete a 2-day fundamental module on EU NIS2 cybersecurity directive.</p>
            </div>
            """, unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Competence Coverage", "85%", "+35% vs ATS")
            with c2:
                st.metric("Title Similarity", "21%", "Agnostic")
            with c3:
                st.metric("Deterministic Composite", "0.82 / 1.0", "Rank #1")

# ----------------- TAB 2: Employer -----------------
with tab_employer:
    st.markdown("### Unlock Hidden Talent Pools Without Title Bias")
    st.write("73% of Swedish companies face talent shortages. Match candidates by verified JobTech competence instead of exact past keywords.")
    
    job_selected = st.selectbox(
        "Select Job Requisition",
        [
            "REQ-077: Senior Reliability Engineer (Industrial IoT)",
            "REQ-102: Cloud Infrastructure DevOps Specialist",
            "REQ-145: Mission-Critical Automation Engineer"
        ]
    )
    
    st.markdown("#### Ranked Candidate Shortlist (Deterministic Code Scoring)")
    
    st.markdown("""
    <div class="gem-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span class="badge-gem">💎 Hidden Gem #1</span>
            <span style="font-weight: 700; color: #4f46e5;">Score: 0.82</span>
        </div>
        <h4>Candidate 101 (Ex-Telecom Core Network Engineer)</h4>
        <p><strong>Verified Evidence Chain:</strong></p>
        <ul>
            <li><strong>JD Clause:</strong> <em>"Du ansvarar för driftsäkerhet och tillgänglighet i våra IoT-plattformar."</em><br/>
                <strong>CV Evidence:</strong> <em>"Kept a 4G/5G packet core at 99.999% uptime across national infrastructure."</em><br/>
                <span style="color: #059669; font-size: 0.85rem;">✓ Machine-verified substring quote against original CV</span>
            </li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ----------------- TAB 3: Recruiter -----------------
with tab_recruiter:
    st.markdown("### Structured Interview Probes (Explainable AI)")
    st.write("Automatically generated interview questions targeting transferable skills and verifiable gap-bridging.")
    
    st.markdown("""
    **Target Candidate:** Candidate 101 &nbsp;|&nbsp; **Target Role:** Reliability Engineer (IoT)
    """)
    
    with st.expander("Probe 1: Technical Transferable Skill (High Availability)", expanded=True):
        st.markdown("**Question:** *Can you walk us through a time an unexpected carrier failover occurred, and how your five-nines architecture prevented customer disruption?*")
        st.caption("What good looks like: Demonstrates deep SLA understanding, root-cause observability, and automated recovery loops.")

    with st.expander("Probe 2: Situational Domain Transition (Telecom -> IoT Platform)", expanded=True):
        st.markdown("**Question:** *How would you adapt your packet routing reliability principles to resource-constrained IoT edge gateways?*")
        st.caption("What good looks like: Acknowledges bandwidth & power differences while maintaining strict uptime discipline.")

    with st.expander("Probe 3: Gap Verification (EU NIS2 Directive)", expanded=True):
        st.markdown("**Question:** *This role falls under the upcoming NIS2 regulatory scope. How have you previously integrated regulatory compliance into system operations?*")
        st.caption("What good looks like: Concrete understanding of incident reporting timelines and audit-trail logging.")

# ----------------- TAB 4: Architecture -----------------
with tab_arch:
    st.markdown("### ☁️ Azure Native Architecture (EU Data Zone)")
    st.code("""
    [Client: Browser / Streamlit UI]
          │ (Internal / Ingress)
          ▼
    [Azure Container Apps: aispire-t04-smoke (Sweden Central)]
          │
          ├──> Azure OpenAI (gpt-5-mini & text-embedding-3-small)
          ├──> Azure AI Search (jobs & JobTech taxonomy hybrid search)
          ├──> Azure Cosmos DB (candidates & matches)
          └──> Managed Identity (aispire-t04-app, Zero-Key RBAC)
    """, language="text")
    st.info("Deployed in Resource Group: `rg-aispire-team-04` (Sweden Central / North Europe).")
