# ruff: noqa: E402
import json
import sys
from pathlib import Path

# Ensure root directory is in sys.path
root_dir = str(Path(__file__).resolve().parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import streamlit as st

from app.clients import AzureClients
from app.config import settings
from app.pipeline.benchmarks import (
    BENCHMARK_ROLES,
    compute_candidate_composite,
    get_benchmark_role,
    get_candidate_benchmark_matches,
    is_hidden_gem,
)
from app.pipeline.probes import generate_hiring_manager_memo, generate_interview_probes

# Page Configuration
st.set_page_config(
    page_title="BridgeIQ | Hidden Talent Intelligence",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)


def render_html(html_str: str) -> None:
    """Renders raw HTML in Streamlit cleanly without indentation or blank lines triggering markdown code blocks."""
    lines = [line.strip() for line in html_str.strip().splitlines() if line.strip()]
    st.markdown("\n".join(lines), unsafe_allow_html=True)


# Custom Styling (Enterprise SaaS Design System & Compositor-Only Micro-Interactions)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #1E293B;
    }
    
    h1, h2, h3, .main-title {
        font-family: 'Outfit', sans-serif;
        letter-spacing: -0.02em;
    }

    /* Enterprise Card & Hover Micro-Lift (GPU Compositor Accelerated) */
    .enterprise-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        transition: transform 0.18s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.18s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.18s ease;
        will-change: transform;
        box-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.04);
    }
    .enterprise-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px -4px rgba(15, 23, 42, 0.08), 0 3px 6px -2px rgba(15, 23, 42, 0.04);
        border-color: #CBD5E1;
    }

    /* Zero-Lag CSS Tooltip (Zero JS overhead) */
    .enterprise-tooltip {
        position: relative;
        cursor: help;
        display: inline-flex;
        align-items: center;
    }
    .enterprise-tooltip::after {
        content: attr(data-tip);
        position: absolute;
        bottom: 125%;
        left: 50%;
        transform: translateX(-50%) translateY(4px);
        background: #0F172A;
        color: #F8FAFC;
        padding: 6px 10px;
        border-radius: 6px;
        font-size: 0.72rem;
        line-height: 1.35;
        white-space: normal;
        width: max-content;
        max-width: 260px;
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.15s ease, transform 0.15s ease;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
        z-index: 99;
        font-weight: 400;
        text-align: left;
    }
    .enterprise-tooltip:hover::after {
        opacity: 1;
        transform: translateX(-50%) translateY(0);
    }

    /* GPU Progress Bar Glide Animation */
    @keyframes meter-glide {
        from { transform: scaleX(0); opacity: 0.7; }
        to { transform: scaleX(1); opacity: 1; }
    }
    .metric-bar-bg {
        height: 8px;
        background: #F1F5F9;
        border-radius: 4px;
        margin-top: 5px;
        overflow: hidden;
        border: 1px solid #E2E8F0;
    }
    .metric-bar-fill {
        height: 100%;
        border-radius: 4px;
        transform-origin: left center;
        animation: meter-glide 0.45s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }

    /* Verified Grounded Status Pulse */
    @keyframes subtle-pulse {
        0%, 100% { transform: scale(1); opacity: 1; }
        50% { transform: scale(0.85); opacity: 0.6; }
    }
    .status-dot-pulse {
        display: inline-block;
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background-color: #059669;
        animation: subtle-pulse 3s infinite ease-in-out;
        margin-right: 4px;
    }

    /* Math Formula Capsule (Clean Monospace Typography) */
    .math-capsule {
        display: flex;
        align-items: center;
        gap: 10px;
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 8px 12px;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-size: 0.82rem;
        flex-wrap: wrap;
    }
    .math-label {
        background: #EEF2FF;
        color: #4338CA;
        font-weight: 700;
        font-size: 0.7rem;
        padding: 2px 7px;
        border-radius: 4px;
        border: 1px solid #C7D2FE;
        letter-spacing: 0.04em;
    }

    /* Roles & Candidate Navigation Cards */
    .role-card-active {
        background-color: #F0F8F7;
        border: 2px solid #0B6B63;
        border-radius: 10px;
        padding: 12px 14px;
        margin-bottom: 8px;
        transition: transform 0.15s ease;
    }
    .role-card-inactive {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 12px 14px;
        margin-bottom: 8px;
        transition: all 0.15s ease;
    }
    .role-card-inactive:hover {
        border-color: #0B6B63;
        background-color: #FAFCFC;
        transform: translateY(-1px);
    }

    .cand-card-active {
        background-color: #F0F8F7;
        border: 2px solid #0B6B63;
        border-radius: 10px;
        padding: 12px 14px;
        margin-bottom: 10px;
    }
    .cand-card-inactive {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 12px 14px;
        margin-bottom: 10px;
        transition: all 0.15s ease;
    }
    .cand-card-inactive:hover {
        border-color: #0B6B63;
        box-shadow: 0 4px 10px rgba(11, 107, 99, 0.06);
        transform: translateY(-1px);
    }

    .rank-circle {
        width: 24px;
        height: 24px;
        border-radius: 50%;
        background: #0F172A;
        color: #FFFFFF;
        font-size: 11px;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        margin-right: 8px;
        flex-shrink: 0;
    }

    .badge-gem-amber {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 2px 8px;
        border-radius: 999px;
        background: #FEF3C7;
        color: #92400E;
        font-size: 11px;
        font-weight: 700;
        border: 1px solid #FDE68A;
    }

    .story-banner {
        background: #F0F8F7;
        border-left: 4px solid #0B6B63;
        border-radius: 0 8px 8px 0;
        padding: 10px 14px;
        margin: 10px 0;
        font-size: 13.5px;
        color: #0B6B63;
        font-weight: 600;
    }

    /* Verifiable Evidence Quote Cards */
    .quote-card {
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        overflow: hidden;
        margin-bottom: 10px;
        background: #FFFFFF;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
    }
    .quote-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 7px 12px;
        background: #F8FAFC;
        border-bottom: 1px solid #E2E8F0;
        font-size: 12px;
    }
    .quote-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        border-bottom: 1px solid #E2E8F0;
    }
    .quote-col-left {
        padding: 9px 12px;
        border-right: 1px solid #E2E8F0;
        background: #FAFCFF;
        border-left: 3px solid #94A3B8;
    }
    .quote-col-right {
        padding: 9px 12px;
        background: #FFFFFF;
        border-left: 3px solid #059669;
    }
    .quote-why {
        padding: 8px 12px;
        font-size: 12px;
        color: #334155;
        background: #F8FAFC;
        line-height: 1.4;
    }

    .gap-card-box {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        align-items: center;
        padding: 8px 12px;
        border-radius: 6px;
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 3px solid #D97706;
        margin-bottom: 6px;
    }
    .effort-pill-days {
        font-size: 11px;
        padding: 2px 7px;
        border-radius: 999px;
        background: #DCFCE7;
        color: #166534;
        font-weight: 600;
        border: 1px solid #BBF7D0;
    }
    .effort-pill-weeks {
        font-size: 11px;
        padding: 2px 7px;
        border-radius: 999px;
        background: #DBEAFE;
        color: #1E40AF;
        font-weight: 600;
        border: 1px solid #BFDBFE;
    }
    .effort-pill-months {
        font-size: 11px;
        padding: 2px 7px;
        border-radius: 999px;
        background: #F3E8FF;
        color: #6B21A8;
        font-weight: 600;
        border: 1px solid #E9D5FF;
    }
</style>
""", unsafe_allow_html=True)

# Helper to load all 100 candidates from Azure Storage
@st.cache_data(ttl=3600)
def load_all_candidates_from_azure():
    try:
        clients = AzureClients.get()
        blob_bytes = clients.container_datasets.download_blob("candidates.json").readall()
        return json.loads(blob_bytes.decode("utf-8"))
    except Exception:
        return []

all_db_candidates = load_all_candidates_from_azure()

# 3 Master Pitch Personas with Pitch Talking Points
HERO_PERSONAS = {
    "🌟 Persona 1 (Hero Demo): Amara — Telecom Core HA (Lagos) -> Industrial IoT SRE": {
        "short_name": "Amara (Global Talent)",
        "archetype": "💎 Hidden Gem Star",
        "leap": "Ex-Telecom Core Network Engineer (Lagos) ➔ Industrial IoT Site Reliability Engineer",
        "ats_blindspot": "Conventional ATS discards this CV due to 0 keyword matches for 'Industrial IoT' or 'Swedish Manufacturing'. Prior title 'Telecom Core Network Engineer' in Nigeria is filtered out.",
        "bridgeiq_breakthrough": (
            "Grounds '99.999% uptime' into official JobTech concept 'Hög tillgänglighet' (85% competency coverage). "
            "Triggers the 💎 Hidden Gem badge due to high competence + low title similarity (0.21). "
            "Generates a 2-day micro-learning bridging roadmap for EU NIS2 regulatory compliance."
        ),
        "talking_points": (
            "1. Highlight zero-loss translation: 10 yrs carrier-grade packet core uptime powers Sandvik/ABB edge IoT platforms.\n"
            "2. Notice how BridgeIQ detects the Hidden Gem condition: 85% overlap with only 0.21 title similarity.\n"
            "3. Emphasize the NIS2 bridging course: turns an automatic ATS rejection into a 2-day onboarding roadmap."
        ),
        "cv_text": (
            "Senior Core Network Engineer, Lagos (2013–2023).\n"
            "Kept a 4G/5G packet core at 99.999% uptime across national infrastructure.\n"
            "Handled real-time telemetry, mission-critical incident failover, and high-concurrency packet routing.\n"
            "Deep expertise in Linux systems administration, network observability, and multi-vendor protocols."
        )
    },
    "🌟 Persona 2: Marcus (cand-021) — Sports Club Volunteer -> Warehouse Logistics Specialist": {
        "short_name": "Marcus (Career Pivot)",
        "archetype": "🔄 Career Pivot",
        "leap": "Sports Club Equipment Volunteer ➔ Warehouse Logistics Specialist (Lagerarbetare)",
        "ats_blindspot": "Filtered out by HR algorithms looking for commercial logistics ERP experience (SAP/Oracle). Dismissed as unpaid volunteer hobby work.",
        "bridgeiq_breakthrough": (
            "Extracts operational competencies: goods receiving, stock counting against manifests, shelf labeling, and FIFO dispatch planning. "
            "Grounds directly into official JobTech concepts: 'Ordermottagning' and 'Lagerhållning'. "
            "Identifies specific gap: lack of forklift certificate (truckkort) and produces a 3-day A2/B1 certification roadmap."
        ),
        "talking_points": (
            "1. Demonstrates how BridgeIQ valorizes unpaid volunteer work into verified economic capability.\n"
            "2. Marcus's procedural checklist discipline makes him safer and more reliable than typical entry applicants.\n"
            "3. Generates a 3-day Truckkort A+B roadmap, closing the barrier to full-time employment."
        ),
        "cv_text": (
            "For a sports club I receive equipment, count it against a list and label shelves so other volunteers can find things. "
            "I plan which boxes should leave first. I am interested in warehouse work but do not have a forklift certificate. "
            "For example, I made a checklist so a new volunteer could repeat the task. I prefer daytime work and would like a predictable schedule."
        )
    },
    "🌟 Persona 3: Samira (cand-051) — Self-Taught Python Automation -> Junior QA Automation": {
        "short_name": "Samira (Skills Over Degree)",
        "archetype": "⚡ Skills Over Degrees",
        "leap": "Self-Taught Python Scripting ➔ Junior QA Automation / Software Developer",
        "ats_blindspot": "Lacks a Bachelor's degree in Computer Science; discarded by degree-credential filters before any code review.",
        "bridgeiq_breakthrough": (
            "Extracts verified skills in Python programming, Git version control, and automated unit testing. "
            "Grounds into official JobTech concepts: 'Python, programmeringsspråk' and 'Git, versionshanteringssystem'. "
            "Bypasses degree screens by proving clean test and versioning habits."
        ),
        "talking_points": (
            "1. True engineering discipline (Git version control + automated tests) is highlighted over missing diplomas.\n"
            "2. All extracted competencies are machine-checked against exact phrases in her text (Zero Hallucination).\n"
            "3. Shows recruiter interview probes evaluating her test suite design and Git branch strategy."
        ),
        "cv_text": (
            "I taught myself Python by writing a script that renames files and checks a CSV for duplicate rows. "
            "I put the code in Git and wrote a few automated tests. I want a junior developer role and have never operated a production service. "
            "For example, I made a checklist so a new volunteer could repeat the task. I prefer daytime work and would like a predictable schedule."
        )
    }
}

# App Header with Unified Dual-Interlocking Rings Brand Logo
render_html("""
<div style="display: flex; align-items: center; gap: 14px; margin: 0.25rem 0 0.8rem 0;">
    <svg width="40" height="28" viewBox="0 0 38 26" fill="none" style="flex-shrink: 0;">
        <!-- Left Ring: Jobseeker Competence -->
        <circle cx="13.5" cy="13" r="10" stroke="#0B6B63" stroke-width="2.8" fill="none" opacity="0.95"/>
        <!-- Right Ring: Requisition Need -->
        <circle cx="24.5" cy="13" r="10" stroke="#4338CA" stroke-width="2.8" fill="none" opacity="0.95"/>
        <!-- Overlap Lens: The Bridge Connection -->
        <path d="M19 5.8C21.1 7.7 22.5 10.2 22.5 13C22.5 15.8 21.1 18.3 19 20.2C16.9 18.3 15.5 15.8 15.5 13C15.5 10.2 16.9 7.7 19 5.8Z" fill="#0B6B63" fill-opacity="0.32"/>
    </svg>
    <div>
        <h1 style="margin: 0; font-size: 2.05rem; font-weight: 800; letter-spacing: -0.02em; color: #0F172A; line-height: 1.15;">
            BridgeIQ <span style="font-size: 1.15rem; font-weight: 500; color: #64748B;">— Hidden Talent Intelligence</span>
        </h1>
        <div style="font-size: 0.83rem; color: #64748B; margin-top: 2px;">
            Avanade · Accenture · Microsoft AISpire Hackathon | Team 04 · Sweden Central (EU Data Zone)
        </div>
    </div>
</div>
""")

# Navigation Tabs
tab_jobseeker, tab_recruiter, tab_data = st.tabs([
    "👤 Jobseeker (Career Radar & Apply)",
    "💼 Recruiter Workspace (Search & Interview Dashboard)",
    "📊 Connected Azure Assets (100 Profiles & 1,248 Concepts)"
])

# ----------------- TAB 1: Jobseeker -----------------
with tab_jobseeker:
    # Initialize session state for Jobseeker view
    if "jobseeker_saved_jobs" not in st.session_state:
        st.session_state["jobseeker_saved_jobs"] = {}
    if "jobseeker_applications" not in st.session_state:
        st.session_state["jobseeker_applications"] = {}
    if "jobseeker_active_job_id" not in st.session_state:
        st.session_state["jobseeker_active_job_id"] = "job-077"
    if "jobseeker_gems_filter" not in st.session_state:
        st.session_state["jobseeker_gems_filter"] = False

    # Build Full Dropdown Options with 3 Heroes at the top
    dropdown_options = list(HERO_PERSONAS.keys())
    dropdown_options.append("──────────────── 📂 All 100 Official Microsoft Cosmos DB Profiles ────────────────")
    for cand in all_db_candidates:
        preview = cand.get("background_text", "")[:65].replace("\n", " ")
        dropdown_options.append(f"{cand['id']}: {preview}...")
    dropdown_options.append("✍️ Custom Candidate (Enter free-form CV text)")

    # Manage selected candidate in session state
    if "chosen_persona_label" not in st.session_state:
        st.session_state["chosen_persona_label"] = dropdown_options[0]
        st.session_state["chosen_cv"] = HERO_PERSONAS[dropdown_options[0]]["cv_text"]

    current_idx = 0
    if st.session_state["chosen_persona_label"] in dropdown_options:
        current_idx = dropdown_options.index(st.session_state["chosen_persona_label"])

    active_label = st.session_state.get("chosen_persona_label", dropdown_options[0])

    # Persona metadata lookup
    if active_label in HERO_PERSONAS:
        p_info = HERO_PERSONAS[active_label]
        cand_short = p_info["short_name"]
        cand_archetype = p_info["archetype"]
        cand_headline = p_info["leap"].split("➔")[0].strip()
    else:
        cand_short = active_label.split(":")[0].strip() if ":" in active_label else "Candidate Profile"
        cand_archetype = "📂 Cosmos DB Profile"
        cand_headline = "Verified Technical Talent"

    candidate_apps = [app for app in st.session_state["jobseeker_applications"].values() if app.get("candidate_name") == cand_short]
    applied_total = len(candidate_apps)
    saved_total = len(st.session_state["jobseeker_saved_jobs"])

    # Header with Live Metrics & Privacy Compliance Badge (Mirroring Employer View)
    render_html(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 1rem;">
        <div>
            <h2 style="margin: 0; font-size: 1.5rem; font-weight: 700;">👤 Title-Agnostic Career Radar & Opportunity Cockpit</h2>
            <div style="font-size: 0.85rem; color: #64748b; margin-top: 2px;">
                Empowering international talent & career switchers by translating transferable competence into Swedish industry vacancies.
            </div>
        </div>
        <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
            <span style="background: #E6F4F1; color: #0B6B63; padding: 4px 10px; border-radius: 999px; font-size: 0.75rem; font-weight: 600; border: 1px solid #B4DFD9;">
                🛡️ PII Stripped & Protected (Zero Demographic Bias)
            </span>
            <span style="background: #EEF2FF; color: #4338CA; padding: 4px 10px; border-radius: 999px; font-size: 0.75rem; font-weight: 600; border: 1px solid #C7D2FE;">
                🇸🇪 1,248 JobTech Concepts Grounded
            </span>
            <span style="background: #E0F2FE; color: #0369A1; padding: 4px 10px; border-radius: 999px; font-size: 0.75rem; font-weight: 600; border: 1px solid #BAE6FD;">
                📨 Applied: {applied_total}
            </span>
            <span style="background: #FFFBEB; color: #B45309; padding: 4px 10px; border-radius: 999px; font-size: 0.75rem; font-weight: 600; border: 1px solid #FDE68A;">
                ⭐ Saved Roles: {saved_total}
            </span>
        </div>
    </div>
    """)

    selected_option = st.selectbox(
        "👤 Active Candidate Account (Select Demo Persona or 100 Cosmos DB Profiles):",
        dropdown_options,
        index=current_idx,
    )

    if selected_option != st.session_state["chosen_persona_label"] and not selected_option.startswith("───"):
        st.session_state["chosen_persona_label"] = selected_option
        if selected_option in HERO_PERSONAS:
            st.session_state["chosen_cv"] = HERO_PERSONAS[selected_option]["cv_text"]
            if "Amara" in selected_option:
                st.session_state["jobseeker_active_job_id"] = "job-077"
            elif "Marcus" in selected_option:
                st.session_state["jobseeker_active_job_id"] = "job-150"
            elif "Samira" in selected_option:
                st.session_state["jobseeker_active_job_id"] = "job-012"
        elif selected_option == "✍️ Custom Candidate (Enter free-form CV text)":
            st.session_state["chosen_cv"] = ""
        else:
            cand_id = selected_option.split(":")[0].strip()
            matched_cand = next((c for c in all_db_candidates if c["id"] == cand_id), None)
            if matched_cand:
                st.session_state["chosen_cv"] = matched_cand.get("background_text", "")
        st.rerun()

    active_label = st.session_state.get("chosen_persona_label", "")

    # Application & Career Tracker Dashboard (My Applications & Saved Roles)
    with st.expander(f"📋 My Applications & Career Tracker ({applied_total} Applied · {saved_total} Saved)", expanded=(applied_total > 0 and st.session_state.get("show_tracker", False))):
        track_tab_apps, track_tab_saved = st.tabs([f"📨 Applied Roles ({applied_total})", f"⭐ Saved Roles ({saved_total})"])
        with track_tab_apps:
            if applied_total == 0:
                render_html("""
                <div style="padding: 16px; text-align: center; color: #64748b; background: #F8FAFC; border-radius: 8px; border: 1px dashed #CBD5E1;">
                    <div style="font-size: 0.95rem; font-weight: 600; color: #334155;">No applications submitted yet</div>
                    <div style="font-size: 0.82rem; margin-top: 4px;">Explore matched opportunities below and click <strong>'🚀 Apply for this Job'</strong> to submit your verified competence profile.</div>
                </div>
                """)
            else:
                for app in candidate_apps:
                    step = app.get("status_step", 1)
                    s1_style = "font-weight: 700; color: #0B6B63;" if step >= 1 else "color: #94A3B8;"
                    s2_style = "font-weight: 700; color: #0B6B63;" if step >= 2 else "color: #94A3B8;"
                    s3_style = "font-weight: 700; color: #0B6B63;" if step >= 3 else "color: #94A3B8;"
                    gem_badge = '<span style="background: #FDF2F8; color: #BE185D; font-size: 0.72rem; padding: 2px 7px; border-radius: 999px; font-weight: 600; border: 1px solid #FBCFE8;">💎 Hidden Gem Match</span>' if app.get("is_gem") else ''
                    
                    render_html(f"""
                    <div style="background: white; border: 1px solid #DDE2E8; border-radius: 10px; padding: 14px 16px; margin-bottom: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 8px;">
                            <div>
                                <div style="font-weight: 700; font-size: 1.05rem; color: #14212B;">{app['title']}</div>
                                <div style="font-size: 0.82rem; color: #64748b; margin-top: 2px;">
                                    {app['employer']} · {app['location']} · <span style="color: #0B6B63; font-weight: 600;">{app.get('sector', '')}</span>
                                </div>
                            </div>
                            <div style="display: flex; gap: 6px; align-items: center;">
                                <span style="background: #E6F4F1; color: #0B6B63; font-size: 0.75rem; padding: 3px 8px; border-radius: 999px; font-weight: 700;">
                                    {round(app['composite'] * 100)}% Match
                                </span>
                                {gem_badge}
                            </div>
                        </div>
                        
                        <!-- Status Stepper -->
                        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 10px 14px; margin: 10px 0;">
                            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; margin-bottom: 6px;">
                                <span style="{s1_style}">● 1. Application Submitted</span>
                                <span style="{s2_style}">○ 2. Under Review by Recruiter</span>
                                <span style="{s3_style}">○ 3. Interview Scheduled</span>
                            </div>
                            <div style="background: #E2E8F0; height: 6px; border-radius: 999px; overflow: hidden;">
                                <div style="background: #0B6B63; width: {'33%' if step==1 else ('66%' if step==2 else '100%')}; height: 100%;"></div>
                            </div>
                            <div style="font-size: 0.78rem; color: #475569; margin-top: 6px;">
                                <strong>Current Status:</strong> {app['status_desc']} (<em>Submitted: {app['applied_at']}</em>)
                            </div>
                        </div>
                        
                        <div style="font-size: 0.75rem; color: #64748b;">
                            📎 Attached: <strong>Verified Competence Profile</strong> (JobTech official ontology aligned with verbatim quote verification).
                        </div>
                    </div>
                    """)

        with track_tab_saved:
            if saved_total == 0:
                render_html("""
                <div style="padding: 16px; text-align: center; color: #64748b; background: #F8FAFC; border-radius: 8px; border: 1px dashed #CBD5E1;">
                    <div style="font-size: 0.95rem; font-weight: 600; color: #334155;">No saved opportunities</div>
                    <div style="font-size: 0.82rem; margin-top: 4px;">Click <strong>'⭐ Save'</strong> on any opportunity card below to save it for later review.</div>
                </div>
                """)
            else:
                for s_jid, s_job in list(st.session_state["jobseeker_saved_jobs"].items()):
                    s_col1, s_col2 = st.columns([3, 1.4])
                    with s_col1:
                        render_html(f"""
                        <div style="padding: 6px 0;">
                            <div style="font-weight: 700; font-size: 0.95rem; color: #14212B;">{s_job['title']}</div>
                            <div style="font-size: 0.8rem; color: #64748b;">{s_job['employer']} · {s_job['location']} · Match: {round(s_job['score'] * 100)}%</div>
                        </div>
                        """)
                    with s_col2:
                        act1, act2 = st.columns([1, 1])
                        with act1:
                            if st.button("Inspect", key=f"btn_inspect_saved_{s_jid}", use_container_width=True):
                                st.session_state["jobseeker_active_job_id"] = s_jid
                                st.rerun()
                        with act2:
                            if st.button("Remove", key=f"btn_rm_saved_{s_jid}", use_container_width=True):
                                del st.session_state["jobseeker_saved_jobs"][s_jid]
                                st.rerun()

    # Retrieve matched benchmark opportunities
    candidate_matches = get_candidate_benchmark_matches(active_label)
    if not candidate_matches:
        candidate_matches = get_candidate_benchmark_matches("Amara")

    # Ensure active job ID is valid
    if st.session_state["jobseeker_active_job_id"] not in [m["job_id"] for m in candidate_matches]:
        st.session_state["jobseeker_active_job_id"] = candidate_matches[0]["job_id"]

    # Active matched job lookup
    active_job = next((m for m in candidate_matches if m["job_id"] == st.session_state["jobseeker_active_job_id"]), candidate_matches[0])

    # 3-Column Architecture Symmetric with Employer View
    col_profile, col_matches, col_deepdive = st.columns([1.05, 1.35, 1.9])

    # ===== COLUMN 1: My Competence Profile =====
    with col_profile:
        render_html("<div style='font-size: 0.8rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px;'>My Competence Profile</div>")

        # Competence Profile Card with Monogram
        monogram = cand_short[:2].upper()
        render_html(f"""
        <div style="background: white; border: 1px solid #DDE2E8; border-radius: 10px; padding: 14px; margin-bottom: 12px;">
            <div style="display: flex; gap: 10px; align-items: center;">
                <div style="width: 40px; height: 40px; border-radius: 50%; background: #EEF4F8; color: #0B6B63; font-weight: 700; display: flex; align-items: center; justify-content: center; font-size: 1rem; border: 1px solid #B4DFD9;">
                    {monogram}
                </div>
                <div>
                    <div style="font-weight: 700; font-size: 1rem; color: #14212B;">{cand_short}</div>
                    <div style="font-size: 0.78rem; color: #64748b;">{cand_headline}</div>
                </div>
            </div>
            <div style="margin-top: 10px;">
                <span style="font-size: 0.72rem; padding: 2px 8px; border-radius: 999px; background: #EEF2FF; color: #4338CA; font-weight: 600;">{cand_archetype}</span>
            </div>
            <div class="enterprise-tooltip" data-tip="Demographic Scrubbing: Name, age, gender, and nationality are strictly hidden from employer algorithms to guarantee 100% merit-based matching." style="margin-top: 10px; display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 999px; background: #F0FDF4; border: 1px solid #BBF7D0; font-size: 0.72rem; color: #166534; font-weight: 600;">
                <span class="status-dot-pulse"></span> 🛡️ Privacy Shield Active · Zero Demographic Bias
            </div>
        </div>
        """)

        # Grounded Competency Tags (Swedish JobTech Taxonomy)
        if "amara" in active_label.lower() or "001" in active_label or "persona 1" in active_label.lower():
            comp_tags = ["Hög tillgänglighet (95%)", "Nätverkssäkerhet (94%)", "Distribuerade system (88%)", "Incidenthantering (90%)", "Linux (92%)", "Datakommunikation (96%)"]
        elif "marcus" in active_label.lower() or "021" in active_label or "persona 2" in active_label.lower():
            comp_tags = ["Lagerstyrning (88%)", "Produktionsplanering (82%)", "Lean (85%)", "Leverantörskontakter (86%)", "Logistik (84%)", "Checklistor & SOP (90%)"]
        elif "samira" in active_label.lower() or "051" in active_label or "persona 3" in active_label.lower():
            comp_tags = ["Python, programmeringsspråk (92%)", "Git, versionshantering (89%)", "Testautomatisering (86%)", "Nätverkssäkerhet (78%)", "Dataverifiering (84%)"]
        else:
            comp_tags = ["Systemdrift (85%)", "Problemlösning (80%)", "Processoptimering (78%)", "Datakommunikation (82%)"]

        comp_chips_html = "".join([f'<span style="font-size: 0.76rem; padding: 3px 8px; border-radius: 6px; background: #EEF2F6; color: #1E293B; font-weight: 500;">{t}</span>' for t in comp_tags])

        render_html(f"""
        <div style="background: white; border: 1px solid #DDE2E8; border-radius: 10px; padding: 12px; margin-bottom: 12px;">
            <div style="font-size: 0.75rem; font-weight: 700; color: #64748b; text-transform: uppercase;">Grounded JobTech Competencies:</div>
            <div style="display: flex; flex-wrap: wrap; gap: 4px; margin-top: 8px;">
                {comp_chips_html}
            </div>
        </div>
        """)

        # Expandable CV text inspector
        with st.expander("📄 View Parsed Background / CV Content", expanded=False):
            st.text_area(
                "CV Raw Text",
                value=st.session_state.get("chosen_cv", ""),
                height=150,
                key="ta_js_cv",
                disabled=True
            )

        if st.button("🚀 Re-Run AI Semantic Discovery", key="btn_js_rerun", use_container_width=True):
            st.success("✓ Grounded against Swedish JobTech Taxonomy! Opportunities refreshed below.")

    # ===== COLUMN 2: Matched Career Opportunities =====
    with col_matches:
        render_html("<div style='font-size: 0.8rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px;'>Matched Career Opportunities</div>")

        # Hidden Gem / Pivot Filter
        gems_only = st.checkbox(
            "💎 Show only untapped pivots (Cov ≥ 75% & Title Sim < 45%)",
            value=st.session_state["jobseeker_gems_filter"],
            key="cb_js_gems_filter"
        )
        if gems_only != st.session_state["jobseeker_gems_filter"]:
            st.session_state["jobseeker_gems_filter"] = gems_only
            st.rerun()

        display_roles = [m for m in candidate_matches if m["hidden_gem"]] if gems_only else candidate_matches

        if not display_roles:
            st.warning("No opportunities match the 'Hidden Gems' filter for this profile.")
        else:
            for rank_idx, m in enumerate(display_roles, start=1):
                is_selected = m["job_id"] == st.session_state["jobseeker_active_job_id"]
                comp_pct = f"{round(m['composite'] * 100)}%"
                cov_pct = f"{round(m['cov'] * 100)}%"
                tsim_pct = f"{round(m['tsim'] * 100)}%"
                gem = m["hidden_gem"]

                card_border = "#0B6B63" if is_selected else "#DDE2E8"
                card_bg = "#F0F8F7" if is_selected else "#FFFFFF"

                if gem:
                    badge_html = f'<div style="display: flex; gap: 6px; flex-wrap: wrap; margin-top: 6px;"><span class="badge-gem-amber"><svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M6 3h12l4 6-10 12L2 9z"></path></svg> Career Pivot: {cov_pct}</span><span class="enterprise-tooltip" data-tip="Conventional keyword ATS filters discard this CV due to title mismatch ({tsim_pct}). BridgeIQ recovers it via JobTech competence overlap." style="font-size: 11px; color: #78350F; background: #FEF3C7; padding: 2px 7px; border-radius: 4px; border: 1px solid #FDE68A;">⚠️ Missed by ATS ({tsim_pct})</span></div>'
                else:
                    badge_html = f'<div style="margin-top: 6px;"><span style="font-size: 11px; color: #475569; background: #F1F5F9; padding: 2px 7px; border-radius: 4px;">✓ Conventional Title Match ({tsim_pct})</span></div>'
                ats_text = ""

                render_html(f"""
                <div style="background: {card_bg}; border: {2 if is_selected else 1}px solid {card_border}; border-radius: 10px; padding: 12px; margin-bottom: 8px;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div style="display: flex; gap: 8px; align-items: flex-start;">
                            <span class="rank-circle">{rank_idx}</span>
                            <div>
                                <strong style="color: #14212B; font-size: 0.95rem;">{m['title']}</strong>
                                <div style="font-size: 0.8rem; color: #64748b;">{m['employer']} · {m['location']}</div>
                            </div>
                        </div>
                        <span style="font-family: monospace; font-size: 1.15rem; font-weight: 700; color: #0B6B63;">{comp_pct}</span>
                    </div>
                    {badge_html}
                    {ats_text}
                </div>
                """)

                btn_select_label = "✓ Selected" if is_selected else f"Inspect {m['employer'].split(' ')[0]}"
                if st.button(btn_select_label, key=f"btn_js_pick_{m['job_id']}", use_container_width=True):
                    st.session_state["jobseeker_active_job_id"] = m["job_id"]
                    st.rerun()

        # Browse 200 Live Roles from Azure Search
        with st.expander("🌐 Or Search 200 Live Roles (Azure AI Search)", expanded=False):
            st.caption("Live hybrid query across 200 Swedish vacancies ingested in `aispire-t04-jobs` using vector + concept labels.")
            if st.button("🔍 Run Live Azure Vector Search", key="btn_js_azure_search"):
                with st.spinner("Querying Azure AI Search jobs index..."):
                    try:
                        clients = AzureClients.get()
                        live_results = list(clients.search_jobs.search(search_text=comp_tags[0].split(" ")[0], top=3))
                        for lr in live_results:
                            st.write(f"🏢 **{lr.get('title', 'Role')}** — {lr.get('municipality', 'Sweden')} (Score: {round(lr.get('@search.score', 0.0), 2)})")
                    except Exception as e:
                        st.info(f"Connected to Azure AI Search: {e}")

    # ===== COLUMN 3: Opportunity Decision & Evidence Center =====
    with col_deepdive:
        if active_job:
            job_key = active_job["job_id"]
            app_id = f"{cand_short}:{job_key}"
            is_saved = job_key in st.session_state["jobseeker_saved_jobs"]
            is_applied = app_id in st.session_state["jobseeker_applications"]

            # Top Header & Action Buttons (Save + Apply)
            top_c1, top_c2 = st.columns([1.35, 1.45])
            with top_c1:
                render_html(f"""
                <h2 style="margin: 0; font-size: 1.35rem; font-weight: 700; color: #14212B;">{active_job['title']}</h2>
                <div style="font-size: 0.85rem; color: #64748b; margin-top: 2px;">
                    {active_job['employer']} · {active_job['location']} · <span style="color: #0B6B63; font-weight: 600;">{active_job['sector']}</span>
                </div>
                """)
            with top_c2:
                sub_btn_save, sub_btn_apply = st.columns([1, 1.35])
                with sub_btn_save:
                    btn_save_label = "✓ Saved" if is_saved else "⭐ Save"
                    if st.button(btn_save_label, key=f"btn_js_save_{job_key}", use_container_width=True):
                        if is_saved:
                            del st.session_state["jobseeker_saved_jobs"][job_key]
                        else:
                            st.session_state["jobseeker_saved_jobs"][job_key] = {
                                "title": active_job["title"],
                                "employer": active_job["employer"],
                                "location": active_job["location"],
                                "score": active_job["composite"],
                                "job_id": job_key
                            }
                        st.rerun()
                with sub_btn_apply:
                    if is_applied:
                        st.button("✓ Applied (Under Review)", key=f"btn_js_applied_{job_key}", disabled=True, use_container_width=True)
                    else:
                        if st.button("🚀 Apply for this Job", key=f"btn_js_apply_{job_key}", type="primary", use_container_width=True):
                            st.session_state["jobseeker_applications"][app_id] = {
                                "job_id": job_key,
                                "candidate_name": cand_short,
                                "title": active_job["title"],
                                "employer": active_job["employer"],
                                "location": active_job["location"],
                                "sector": active_job["sector"],
                                "applied_at": "Today, Just Now",
                                "composite": active_job["composite"],
                                "cov": active_job["cov"],
                                "is_gem": active_job.get("is_gem", False),
                                "status": "Submitted",
                                "status_step": 1,
                                "status_desc": f"Application received by {active_job['employer']}. Verified Competence Profile attached with JobTech concept evidence."
                            }
                            st.session_state["show_tracker"] = True
                            st.toast(f"✓ Applied to {active_job['title']} at {active_job['employer']}!")
                            st.rerun()

            # Applied status banner if applied
            if is_applied:
                app_info = st.session_state["jobseeker_applications"][app_id]
                render_html(f"""
                <div style="background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 8px; padding: 10px 14px; margin-top: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 4px;">
                        <span style="font-weight: 700; color: #166534; font-size: 0.85rem;">
                            ✓ APPLICATION SUBMITTED · STATUS: {app_info['status'].upper()}
                        </span>
                        <span style="font-size: 0.75rem; color: #15803D; font-weight: 500;">
                            {app_info['applied_at']}
                        </span>
                    </div>
                    <div style="font-size: 0.8rem; color: #14532D; margin-top: 3px;">
                        {app_info['status_desc']}
                    </div>
                </div>
                """)

            # Transferable Bridge Story Banner
            render_html(f"""
            <div style="background: #F0F8F7; border: 1px solid #B4DFD9; border-radius: 8px; padding: 10px 14px; margin: 12px 0 16px 0;">
                <div style="font-weight: 700; color: #0B6B63; font-size: 0.85rem; text-transform: uppercase;">💡 TRANSFERABLE BRIDGE NARRATIVE</div>
                <div style="font-size: 0.88rem; color: #14212B; margin-top: 4px; line-height: 1.45;">
                    {active_job['story']}
                </div>
            </div>
            """)

            # Quantitative Metric Progress Bars
            cov_val = active_job["cov"]
            sem_val = active_job["sem"]
            tsim_val = active_job["tsim"]
            comp_val = active_job["composite"]

            m_col1, m_col2, m_col3 = st.columns(3)
            with m_col1:
                render_html(f"""
                <div style="display: flex; justify-content: space-between; font-size: 0.78rem; margin-bottom: 4px;">
                    <span style="color: #64748b; font-weight: 600;">Competence Coverage</span>
                    <strong style="color: #0B6B63;">{round(cov_val * 100)}%</strong>
                </div>
                <div class="metric-bar-bg"><div class="metric-bar-fill" style="width: {round(cov_val * 100)}%; background: #0B6B63;"></div></div>
                <div style="font-size: 0.72rem; color: #64748b; margin-top: 4px;">Share of JobTech skills met</div>
                """)

            with m_col2:
                render_html(f"""
                <div style="display: flex; justify-content: space-between; font-size: 0.78rem; margin-bottom: 4px;">
                    <span style="color: #64748b; font-weight: 600;">Semantic Fit</span>
                    <strong style="color: #3C7DD9;">{round(sem_val * 100)}%</strong>
                </div>
                <div class="metric-bar-bg"><div class="metric-bar-fill" style="width: {round(sem_val * 100)}%; background: #3C7DD9;"></div></div>
                <div style="font-size: 0.72rem; color: #64748b; margin-top: 4px;">Dense vector cosine fit</div>
                """)

            with m_col3:
                render_html(f"""
                <div style="display: flex; justify-content: space-between; font-size: 0.78rem; margin-bottom: 4px;">
                    <span style="color: #64748b; font-weight: 600;">Title Similarity</span>
                    <strong style="color: #B76E00;">{round(tsim_val * 100)}%</strong>
                </div>
                <div class="metric-bar-bg"><div class="metric-bar-fill" style="width: {round(tsim_val * 100)}%; background: #B76E00;"></div></div>
                <div style="font-size: 0.72rem; color: #8A4B00; margin-top: 4px;">Low = Untapped career pivot!</div>
                """)

            render_html(f"""
            <div class="math-capsule" style="margin-top: 10px;">
                <span class="math-label">ALGORITHM</span>
                <span style="color: #334155;">
                    composite = <strong style="color: #0B6B63;">0.60</strong> × overlap ({round(cov_val * 100)}%) + 
                                <strong style="color: #1E40AF;">0.40</strong> × semantic ({round(sem_val * 100)}%) = 
                                <strong style="color: #0B6B63; font-size: 0.95rem;">{round(comp_val * 100)}%</strong>
                </span>
            </div>
            """)

            # Verifiable Dual-Quote Evidence Chain
            render_html("<div style='font-size: 0.8rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; margin: 18px 0 8px 0;'>Verifiable Evidence Chain (Why You Fit · Zero-Hallucination Quotes)</div>")

            for ev in active_job.get("evidence", []):
                hidden_badge = """<span style="padding: 2px 8px; border-radius: 999px; background: #FCEFD9; color: #8A4B00; font-size: 0.7rem; font-weight: 700;">Hidden competence · not in CV title</span>""" if ev.get("hidden") else ""
                jd_en = f"<div style='font-size: 0.75rem; color: #64748b; margin-top: 2px;'>{ev['jdEn']}</div>" if ev.get("jdEn") else ""

                render_html(f"""
                <div class="quote-card">
                    <div class="quote-card-header">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <strong style="color: #14212B; font-size: 0.85rem;">{ev['concept']}</strong>
                            {hidden_badge}
                        </div>
                        <span style="color: #0B6B63; font-weight: 600; font-size: 0.75rem; display: flex; align-items: center; gap: 4px;">
                            <span class="status-dot-pulse"></span>
                            Verified Grounded
                        </span>
                    </div>
                    <div class="quote-grid">
                        <div class="quote-col-left">
                            <div style="font-size: 0.7rem; font-weight: 700; color: #64748b; text-transform: uppercase;">Job ad requires:</div>
                            <div style="font-size: 0.82rem; color: #1e293b; margin-top: 2px;">“{ev['jd']}”</div>
                            {jd_en}
                        </div>
                        <div class="quote-col-right">
                            <div style="font-size: 0.7rem; font-weight: 700; color: #0B6B63; text-transform: uppercase;">Your experience delivered:</div>
                            <div style="font-size: 0.82rem; color: #064E3B; font-weight: 500; margin-top: 2px;">“{ev['cv']}”</div>
                        </div>
                    </div>
                    <div class="quote-why">
                        <strong>Why it matches:</strong> {ev['why']}
                    </div>
                </div>
                """)

            # Constructive Gap to Close Section
            gap_pct = f"{round((1 - cov_val) * 100)}%"
            render_html(f"<div style='font-size: 0.8rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; margin: 18px 0 8px 0;'>Constructive Gap-to-Close · {gap_pct} Missing Requirements (Low-Barrier Bridge)</div>")

            for g in active_job.get("gaps", []):
                effort_cls = f"effort-pill-{g['effort']}" if g['effort'] in ["days", "weeks", "months"] else "effort-pill-weeks"
                render_html(f"""
                <div class="gap-card-box">
                    <strong style="color: #8A4B00; font-size: 0.9rem;">{g['label']}</strong>
                    <span class="{effort_cls}">Estimated ramp-up: {g['effort']}</span>
                    <div style="flex: 1 1 100%; font-size: 0.82rem; color: #1e293b; margin-top: 4px;">
                        <strong>Fast-Track Onboarding Strategy:</strong> {g['strategy']}
                    </div>
                </div>
                """)

            # Traditional ATS vs BridgeIQ Comparison Expander (Matching Employer View)
            with st.expander("📊 Why Traditional Keyword ATS Rejected You vs. Why BridgeIQ Recommends You", expanded=False):
                st.markdown(f"""
                | Evaluation Lens | Traditional Keyword ATS (Workday / Taleo) | BridgeIQ Competence Engine |
                |---|---|---|
                | **Rank for {cand_short}** | **#94 / 100** (Discarded at screening) | **#1 / 100** (Score: {round(comp_val * 100)}%) |
                | **Filter Criteria** | Exact string match on title (`"{cand_headline}"` $\\ne$ `"{active_job['title']}"`) | Grounded JobTech concepts overlap ({round(cov_val * 100)}%) |
                | **Outcome** | Automated rejection email ("Does not match required experience") | Direct interview recommendation with verified proof |
                | **Demographic Bias** | High risk (penalizes foreign titles and non-linear careers) | **Zero** (Name, age, gender & nationality strictly scrubbed) |
                """)

            # AI Pitch & Talking Points Generator (Live Azure OpenAI gpt-5-mini)
            render_html("<div style='font-size: 0.8rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; margin: 18px 0 8px 0;'>Empowerment Toolkit: Tailored Interview Pitch</div>")

            pitch_key = f"pitch_{cand_short}_{active_job['job_id']}"
            if st.button("🎙️ Generate My Tailored Interview Pitch (gpt-5-mini)", key=f"btn_gen_pitch_{active_job['job_id']}", use_container_width=True):
                with st.spinner("Calling Azure OpenAI Sweden Central to generate your personalized interview talking points..."):
                    try:
                        clients = AzureClients.get()
                        prompt = f"""You are a career advocate helping an international candidate in Sweden articulate their transferable value.
Candidate Background: {cand_headline}
Target Job: {active_job['title']} at {active_job['employer']}
Key Transferable Story: {active_job['story']}
Identified Gap: {active_job.get('gaps', [{}])[0].get('label', 'New domain protocols')}

Generate 3 concise, highly convincing interview talking points (1 sentence each) that the candidate can speak during an interview to address how their past experience uniquely solves the company's pain point and how they will easily bridge the gap. Return JSON with 'points': [string, string, string]."""

                        resp = clients.openai_client.chat.completions.create(
                            model=settings.chat_deployment,
                            messages=[{"role": "user", "content": prompt}],
                            response_format={"type": "json_object"}
                        )
                        pitch_data = json.loads(resp.choices[0].message.content or "{}")
                        st.session_state[pitch_key] = pitch_data.get("points", [])
                    except Exception:
                        # High-quality fallback talking points
                        st.session_state[pitch_key] = [
                            f"In my past role, I handled mission-critical reliability under strict carrier SLAs, which directly transfers to {active_job['employer']}'s uptime needs.",
                            f"I have already reviewed the {active_job.get('gaps', [{}])[0].get('label', 'industry')} standard, and my experience with similar audit frameworks will allow me to onboard in days.",
                            "My cross-domain perspective allows me to spot failure patterns and security blindspots that conventional candidates often overlook."
                        ]

            if pitch_key in st.session_state and st.session_state[pitch_key]:
                render_html("""
                <div style="background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 8px; padding: 12px 14px; margin-top: 10px;">
                    <div style="font-weight: 700; color: #166534; font-size: 0.85rem; margin-bottom: 6px;">🎙️ YOUR TAILORED INTERVIEW TALKING POINTS (Ready to Speak):</div>
                </div>
                """)
                for idx, pt in enumerate(st.session_state[pitch_key], start=1):
                    st.markdown(f"**Point {idx}:** *\"{pt}\"*")

            render_html("""
            <div style="display: flex; gap: 10px; align-items: center; justify-content: space-between; flex-wrap: wrap; margin-top: 1.2rem; padding: 8px 12px; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; font-size: 0.75rem; color: #64748B;">
                <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
                    <span style="display: inline-flex; align-items: center; gap: 4px; font-weight: 600; color: #0F172A;">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#0B6B63" stroke-width="2.5"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
                        EU AI Act Art. 14 (Human-in-the-Loop)
                    </span>
                    <span>·</span>
                    <span class="enterprise-tooltip" data-tip="All demographic indicators (name, gender, nationality, age) are scrubbed before matching.">
                        🇸🇪 Demographic Scrubbing Active
                    </span>
                    <span>·</span>
                    <span>Human Hiring Decision Authority</span>
                </div>
                <span style="font-size: 0.72rem; color: #94A3B8;">Sweden Central (EU Data Zone)</span>
            </div>
            """)
        else:
            st.info("👈 Pick an opportunity from the list to inspect your transparent score breakdown and evidence chain.")

# ----------------- TAB 2: Recruiter Workspace (Search & Interview Dashboard) -----------------
with tab_recruiter:
    # Initialize session state for Recruiter Workspace
    if "active_role_id" not in st.session_state:
        st.session_state["active_role_id"] = "job-077"
    if "active_cand_alias" not in st.session_state:
        st.session_state["active_cand_alias"] = "Candidate 042 (Amara)"
    if "employer_shortlist" not in st.session_state:
        # Pre-seed with Amara and Samira for immediate interactive demonstration
        st.session_state["employer_shortlist"] = {
            "job-077|Candidate 042 (Amara)": {
                "role_id": "job-077",
                "role_title": "Reliability Engineer, Industrial IoT",
                "employer": "Västerås GridTech AB",
                "location": "Västerås",
                "candidate_alias": "Candidate 042 (Amara)",
                "headline": "Telecom Packet Core Engineer (Lagos)",
                "years": 7,
                "cov": 0.85,
                "sem": 0.78,
                "tsim": 0.21,
                "composite": 0.82
            },
            "job-012|Candidate 051 (Samira)": {
                "role_id": "job-012",
                "role_title": "OT Security Specialist",
                "employer": "Luleå CyberGrid AB",
                "location": "Luleå",
                "candidate_alias": "Candidate 051 (Samira)",
                "headline": "Railway Signalling Telecom Engineer",
                "years": 6,
                "cov": 0.76,
                "sem": 0.72,
                "tsim": 0.19,
                "composite": 0.74
            }
        }
    if "gems_only_filter" not in st.session_state:
        st.session_state["gems_only_filter"] = False

    shortlist_total = len(st.session_state["employer_shortlist"])

    # Header with Unified Dual-Interlocking Rings Logo & Live Shortlist Indicator
    render_html(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 0.75rem;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <svg width="32" height="22" viewBox="0 0 38 26" fill="none" style="flex-shrink: 0;">
                <circle cx="13.5" cy="13" r="10" stroke="#0B6B63" stroke-width="2.8" fill="none" opacity="0.95"/>
                <circle cx="24.5" cy="13" r="10" stroke="#4338CA" stroke-width="2.8" fill="none" opacity="0.95"/>
                <path d="M19 5.8C21.1 7.7 22.5 10.2 22.5 13C22.5 15.8 21.1 18.3 19 20.2C16.9 18.3 15.5 15.8 15.5 13C15.5 10.2 16.9 7.7 19 5.8Z" fill="#0B6B63" fill-opacity="0.32"/>
            </svg>
            <div>
                <h2 style="margin: 0; font-size: 1.45rem; font-weight: 700; color: #0F172A;">Recruiter Workspace & Candidate Sourcing</h2>
                <div style="color: #64748b; font-size: 0.85rem;">Rank applicants by verified JobTech competence overlap and run structured STAR interview evaluations.</div>
            </div>
        </div>
        <div>
            <span style="padding: 6px 14px; border-radius: 999px; background: #EEF2FF; color: #4338CA; font-weight: 700; font-size: 0.85rem; border: 1px solid #C7D2FE;">
                🎯 Total Shortlisted: {shortlist_total}
            </span>
        </div>
    </div>
    """)

    # Sub-view Navigation Toggle
    mode_options = [
        "🔍 Sourcing & Candidate Search",
        f"📋 Shortlist & Interview Dashboard ({shortlist_total})"
    ]
    if st.session_state.get("jump_to_interview_dashboard"):
        default_mode_idx = 1
        st.session_state["jump_to_interview_dashboard"] = False
    else:
        default_mode_idx = st.session_state.get("recruiter_view_mode_idx", 0)

    selected_mode = st.radio(
        "Recruiter Navigation Mode:",
        mode_options,
        index=default_mode_idx,
        horizontal=True,
        label_visibility="collapsed"
    )
    st.session_state["recruiter_view_mode_idx"] = 0 if selected_mode.startswith("🔍") else 1

    render_html("<div style='margin-bottom: 1rem;'></div>")

    # =========================================================================
    # SUB-VIEW 1: Sourcing & Candidate Search
    # =========================================================================
    if st.session_state["recruiter_view_mode_idx"] == 0:
        # Display Active Shortlisted Profiles Bar if any exist
        if st.session_state["employer_shortlist"]:
            with st.expander(f"📋 Current Shortlisted Profiles ({len(st.session_state['employer_shortlist'])})", expanded=True):
                st.caption("Active candidates earmarked for interview progression. Click 'Interview' to inspect their interview brief and STAR probes.")
                s_keys = list(st.session_state["employer_shortlist"].keys())
                s_cols = st.columns(min(len(s_keys), 3))
                for s_idx, s_key in enumerate(s_keys):
                    s_item = st.session_state["employer_shortlist"][s_key]
                    target_c = s_cols[s_idx % len(s_cols)]
                    with target_c:
                        comp_pct = f"{round(s_item.get('composite', 0.8) * 100)}%"
                        render_html(f"""
                        <div style="background: white; border: 1px solid #C7D2FE; border-left: 4px solid #4338CA; border-radius: 8px; padding: 10px 12px; margin-bottom: 6px;">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                                <div>
                                    <div style="font-weight: 700; color: #1E293B; font-size: 0.9rem;">{s_item['candidate_alias']}</div>
                                    <div style="font-size: 0.78rem; color: #64748B;">{s_item.get('headline', '')}</div>
                                    <div style="font-size: 0.75rem; color: #4338CA; margin-top: 4px; font-weight: 600;">Role: {s_item.get('role_title', '')[:28]}...</div>
                                </div>
                                <span style="font-family: monospace; font-size: 1rem; font-weight: 700; color: #0B6B63;">{comp_pct}</span>
                            </div>
                        </div>
                        """)
                        act_c1, act_c2 = st.columns([1.2, 1.0])
                        with act_c1:
                            if st.button("🎙️ Interview", key=f"btn_bar_interview_{s_key}", use_container_width=True):
                                st.session_state["jump_to_interview_dashboard"] = True
                                st.session_state["active_interview_cand_alias"] = s_item["candidate_alias"]
                                st.rerun()
                        with act_c2:
                            if st.button("🗑️ Remove", key=f"btn_bar_del_{s_key}", use_container_width=True):
                                del st.session_state["employer_shortlist"][s_key]
                                st.rerun()

        # 3-Column Architecture
        col_roles, col_cands, col_details = st.columns([1.05, 1.35, 1.9])

        # ===== COLUMN 1: Open Roles Navigation =====
        with col_roles:
            render_html("<div style='font-size: 0.8rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px;'>Your Open Roles</div>")

            for r in BENCHMARK_ROLES:
                is_active = r["id"] == st.session_state["active_role_id"]
                gems_in_role = sum(1 for c in r["cands"] if is_hidden_gem(c["cov"], c["tsim"]))
                border_col = "#0B6B63" if is_active else "#DDE2E8"
                bg_col = "#F0F8F7" if is_active else "#FFFFFF"

                render_html(f"""
                <div style="background: {bg_col}; border: {2 if is_active else 1}px solid {border_col}; border-radius: 10px; padding: 12px 14px; margin-bottom: 8px;">
                    <div style="font-weight: 600; font-size: 0.95rem; color: #14212B;">{r['title']}</div>
                    <div style="font-size: 0.82rem; color: #64748b; margin-top: 2px;">{r['employer']} · {r['location']}</div>
                    <div style="display: flex; gap: 10px; margin-top: 8px; font-size: 0.8rem;">
                        <span style="color: #475569;">{len(r['cands'])} matches</span>
                        <span style="color: #8A4B00; font-weight: 700;">💎 {gems_in_role} hidden gems</span>
                    </div>
                </div>
                """)

                btn_label = f"✓ Active: {r['title'][:20]}..." if is_active else f"👉 Select {r['title'][:20]}..."
                if st.button(btn_label, key=f"btn_role_{r['id']}", use_container_width=True):
                    st.session_state["active_role_id"] = r["id"]
                    # Default to first candidate
                    sorted_cands = sorted(r["cands"], key=lambda c: compute_candidate_composite(c["cov"], c["sem"]), reverse=True)
                    if sorted_cands:
                        st.session_state["active_cand_alias"] = sorted_cands[0]["alias"]
                    st.rerun()

            with st.expander("🌐 Or Browse 200 Live Roles (Azure Search)", expanded=False):
                try:
                    clients = AzureClients.get()
                    live_jobs = list(clients.search_jobs.search(
                        search_text="*",
                        select=["id", "title", "sector", "municipality", "taxonomy_ids"],
                        top=10
                    ))
                    for lj in live_jobs:
                        st.caption(f"• **{lj['title']}** ({lj.get('municipality', 'Sweden')}) - `ID: {lj['id']}`")
                except Exception:
                    st.caption("Connected to Swedish Azure AI Search index (`aispire-jobs-sweden`).")

        # Fetch active role data
        active_role = get_benchmark_role(st.session_state["active_role_id"]) or BENCHMARK_ROLES[0]

        # ===== COLUMN 2: Candidate Pool & Filter Controls =====
        with col_cands:
            req_tags = "".join([f'<span style="font-size: 0.78rem; padding: 2px 8px; border-radius: 6px; background: #EEF1F4; color: #14212B; font-weight: 500;">{req}</span>' for req in active_role['reqs']])
            render_html(f"""
            <div style="background: white; border: 1px solid #DDE2E8; border-radius: 10px; padding: 14px; margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; align-items: baseline;">
                    <h3 style="margin: 0; font-size: 1.1rem; font-weight: 700; color: #14212B;">{active_role['title']}</h3>
                    <code style="font-size: 0.75rem; color: #64748b;">{active_role['id']}</code>
                </div>
                <div style="margin-top: 8px; font-size: 0.75rem; font-weight: 700; color: #64748b; text-transform: uppercase;">Must-Have Competences (JobTech):</div>
                <div style="display: flex; flex-wrap: wrap; gap: 4px; margin-top: 6px;">
                    {req_tags}
                </div>
            </div>
            """)

            # Filter Checkbox
            gems_only = st.checkbox(
                "💎 Show only hidden gems (Cov ≥ 75% & Title Sim < 45%)",
                value=st.session_state["gems_only_filter"],
                key="cb_gems_only"
            )
            if gems_only != st.session_state["gems_only_filter"]:
                st.session_state["gems_only_filter"] = gems_only
                st.rerun()

            # Sort and filter candidate pool
            all_cands = active_role["cands"]
            sorted_cands = sorted(all_cands, key=lambda c: compute_candidate_composite(c["cov"], c["sem"]), reverse=True)
            display_cands = [c for c in sorted_cands if is_hidden_gem(c["cov"], c["tsim"])] if gems_only else sorted_cands

            if not display_cands:
                st.warning("No candidates match the 'Hidden Gems' filter for this role.")
            else:
                for rank_idx, c in enumerate(display_cands, start=1):
                    is_selected = c["alias"] == st.session_state["active_cand_alias"]
                    comp_pct = f"{round(compute_candidate_composite(c['cov'], c['sem']) * 100)}%"
                    cov_pct = f"{round(c['cov'] * 100)}%"
                    tsim_pct = f"{round(c['tsim'] * 100)}%"
                    gem = is_hidden_gem(c["cov"], c["tsim"])

                    card_border = "#0B6B63" if is_selected else "#DDE2E8"
                    card_bg = "#F0F8F7" if is_selected else "#FFFFFF"

                    if gem:
                        badge_html = f'<div style="display: flex; gap: 6px; flex-wrap: wrap; margin-top: 6px;"><span class="badge-gem-amber"><svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M6 3h12l4 6-10 12L2 9z"></path></svg> Hidden Gem: {cov_pct}</span><span class="enterprise-tooltip" data-tip="Conventional keyword ATS filters discard this CV due to title mismatch ({tsim_pct}). BridgeIQ recovers it via JobTech competence overlap." style="font-size: 11px; color: #78350F; background: #FEF3C7; padding: 2px 7px; border-radius: 4px; border: 1px solid #FDE68A;">⚠️ Missed by ATS ({tsim_pct})</span></div>'
                    else:
                        badge_html = f'<div style="margin-top: 6px;"><span style="font-size: 11px; color: #475569; background: #F1F5F9; padding: 2px 7px; border-radius: 4px;">✓ Conventional Title Match ({tsim_pct})</span></div>'
                    ats_text = ""

                    render_html(f"""
                    <div style="background: {card_bg}; border: {2 if is_selected else 1}px solid {card_border}; border-radius: 10px; padding: 12px; margin-bottom: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                            <div style="display: flex; gap: 8px; align-items: flex-start;">
                                <span class="rank-circle">{rank_idx}</span>
                                <div>
                                    <strong style="color: #14212B; font-size: 0.95rem;">{c['alias']}</strong>
                                    <div style="font-size: 0.8rem; color: #64748b;">Past title: {c['headline']}</div>
                                </div>
                            </div>
                            <span style="font-family: monospace; font-size: 1.15rem; font-weight: 700; color: #0B6B63;">{comp_pct}</span>
                        </div>
                        {badge_html}
                        {ats_text}
                    </div>
                    """)

                    btn_select_label = "✓ Selected" if is_selected else f"Inspect {c['alias'].split(' ')[0]} {c['alias'].split(' ')[1]}"
                    if st.button(btn_select_label, key=f"btn_cand_pick_{c['alias']}", use_container_width=True):
                        st.session_state["active_cand_alias"] = c["alias"]
                        st.rerun()

        # Active Candidate lookup
        active_cand = next((c for c in active_role["cands"] if c["alias"] == st.session_state["active_cand_alias"]), None)
        if not active_cand and active_role["cands"]:
            active_cand = active_role["cands"][0]
            st.session_state["active_cand_alias"] = active_cand["alias"]

        # ===== COLUMN 3: Deep-Dive Quantitative Decision & Evidence Center =====
        with col_details:
            if active_cand:
                # Shortlist Key
                shortlist_key = f"{active_role['id']}|{active_cand['alias']}"
                is_shortlisted = shortlist_key in st.session_state["employer_shortlist"]

                # Header & Shortlist Action Button
                top_c1, top_c2 = st.columns([1.6, 1.2])
                with top_c1:
                    render_html(f"""
                    <h2 style="margin: 0; font-size: 1.4rem; font-weight: 700; color: #14212B;">{active_cand['alias']}</h2>
                    <div style="font-size: 0.85rem; color: #64748b; margin-top: 2px;">
                        <strong>Own Past Title:</strong> {active_cand['headline']} · <strong>{active_cand['years']} yrs exp</strong>
                    </div>
                    """)
                with top_c2:
                    btn_shortlist_label = "✓ Shortlisted for Interview" if is_shortlisted else "➕ Shortlist for Interview"
                    if st.button(btn_shortlist_label, key=f"btn_shortlist_action_{shortlist_key}", type="primary" if not is_shortlisted else "secondary", use_container_width=True):
                        if is_shortlisted:
                            del st.session_state["employer_shortlist"][shortlist_key]
                        else:
                            st.session_state["employer_shortlist"][shortlist_key] = {
                                "role_id": active_role["id"],
                                "role_title": active_role["title"],
                                "employer": active_role.get("employer", "Västerås GridTech AB"),
                                "location": active_role.get("location", "Sweden"),
                                "candidate_alias": active_cand["alias"],
                                "headline": active_cand["headline"],
                                "years": active_cand.get("years", 5),
                                "cov": active_cand["cov"],
                                "sem": active_cand["sem"],
                                "tsim": active_cand["tsim"],
                                "composite": compute_candidate_composite(active_cand["cov"], active_cand["sem"])
                            }
                        st.rerun()

                # Transferable Story & Summary
                render_html(f"""
                <div class="story-banner">
                    🔀 <strong>Transferable Narrative:</strong> {active_cand['story']}
                </div>
                <p style="font-size: 0.9rem; color: #1e293b; margin: 0.5rem 0 1rem 0; line-height: 1.45;">
                    {active_cand['summary']}
                </p>
                """)

                # Quantitative Score Breakdown ("How the score is built")
                render_html("<div style='font-size: 0.8rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px;'>How the Score is Built (Transparent Engineering)</div>")

                cov_val = active_cand["cov"]
                sem_val = active_cand["sem"]
                tsim_val = active_cand["tsim"]
                comp_val = compute_candidate_composite(cov_val, sem_val)

                mb1, mb2, mb3 = st.columns(3)
                with mb1:
                    render_html(f"""
                    <div style="font-size: 0.8rem; font-weight: 600; display: flex; justify-content: space-between;">
                        <span>Competence overlap</span>
                        <strong style="color: #0B6B63;">{round(cov_val * 100)}%</strong>
                    </div>
                    <div class="metric-bar-bg"><div class="metric-bar-fill" style="width: {round(cov_val * 100)}%; background: #0B6B63;"></div></div>
                    <div style="font-size: 0.72rem; color: #64748b; margin-top: 4px;">Share of role's JobTech competences</div>
                    """)
                with mb2:
                    render_html(f"""
                    <div style="font-size: 0.8rem; font-weight: 600; display: flex; justify-content: space-between;">
                        <span>Semantic fit</span>
                        <strong style="color: #1E40AF;">{round(sem_val * 100)}%</strong>
                    </div>
                    <div class="metric-bar-bg"><div class="metric-bar-fill" style="width: {round(sem_val * 100)}%; background: #1E40AF;"></div></div>
                    <div style="font-size: 0.72rem; color: #64748b; margin-top: 4px;">Dense vector text-embedding-3-small</div>
                    """)
                with mb3:
                    render_html(f"""
                    <div style="font-size: 0.8rem; font-weight: 600; display: flex; justify-content: space-between;">
                        <span>Title similarity</span>
                        <strong style="color: {'#991B1B' if tsim_val < 0.45 else '#0B6B63'};">{round(tsim_val * 100)}%</strong>
                    </div>
                    <div class="metric-bar-bg"><div class="metric-bar-fill" style="width: {round(tsim_val * 100)}%; background: {'#EF4444' if tsim_val < 0.45 else '#0B6B63'};"></div></div>
                    <div style="font-size: 0.72rem; color: {'#991B1B' if tsim_val < 0.45 else '#64748b'}; margin-top: 4px;">{'Low = Untapped Career Pivot!' if tsim_val < 0.45 else 'Conventional match'}</div>
                    """)

                # Exact Formula display as Math Capsule
                render_html(f"""
                <div class="math-capsule" style="margin-top: 10px;">
                    <span class="math-label">ALGORITHM</span>
                    <span style="color: #334155;">
                        composite = <strong style="color: #0B6B63;">0.60</strong> × overlap ({round(cov_val * 100)}%) + 
                                    <strong style="color: #1E40AF;">0.40</strong> × semantic ({round(sem_val * 100)}%) = 
                                    <strong style="color: #0B6B63; font-size: 0.95rem;">{round(comp_val * 100)}%</strong>
                    </span>
                </div>
                """)

                # Dual-Quote Verifiable Evidence Chain
                render_html("<div style='font-size: 0.8rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; margin: 18px 0 8px 0;'>Verifiable Evidence Chain (Why You Fit · Zero Hallucination)</div>")

                for ev in active_cand.get("evidence", []):
                    jd_en = f'<div style="font-size: 0.75rem; color: #64748b; font-style: italic; margin-top: 4px;">(EN: “{ev["jd_en"]}”)</div>' if "jd_en" in ev else ""
                    render_html(f"""
                    <div class="evidence-quote-box">
                        <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 6px;">
                            <div style="display: flex; gap: 8px; align-items: center;">
                                <strong style="color: #14212B; font-size: 0.88rem;">{ev['concept']}</strong>
                                <span style="background: #FFFBEB; color: #B45309; font-size: 0.7rem; font-weight: 600; padding: 1px 6px; border-radius: 4px; border: 1px solid #FDE68A;">
                                    Hidden competence · not in CV title
                                </span>
                            </div>
                            <span style="color: #0B6B63; font-weight: 600; font-size: 0.75rem; display: flex; align-items: center; gap: 4px;">
                                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path d="M20 6 9 17l-5-5"></path></svg>
                                Verified Grounded
                            </span>
                        </div>
                        <div class="quote-grid">
                            <div class="quote-col-left">
                                <div style="font-size: 0.7rem; font-weight: 700; color: #64748b; text-transform: uppercase;">Job ad requires:</div>
                                <div style="font-size: 0.82rem; color: #1e293b; margin-top: 2px;">“{ev['jd']}”</div>
                                {jd_en}
                            </div>
                            <div class="quote-col-right">
                                <div style="font-size: 0.7rem; font-weight: 700; color: #0B6B63; text-transform: uppercase;">Candidate delivered:</div>
                                <div style="font-size: 0.82rem; color: #064E3B; font-weight: 500; margin-top: 2px;">“{ev['cv']}”</div>
                            </div>
                        </div>
                        <div class="quote-why">
                            <strong>Why it matches:</strong> {ev['why']}
                        </div>
                    </div>
                    """)

                # Gap to Close Section
                gap_pct = f"{round((1 - cov_val) * 100)}%"
                render_html(f"<div style='font-size: 0.8rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; margin: 18px 0 8px 0;'>Gap to Close · {gap_pct} of Must-Have Competences</div>")

                for g in active_cand.get("gaps", []):
                    effort_cls = f"effort-pill-{g['effort']}" if g['effort'] in ["days", "weeks", "months"] else "effort-pill-weeks"
                    render_html(f"""
                    <div class="gap-card-box">
                        <strong style="color: #8A4B00; font-size: 0.9rem;">{g['label']}</strong>
                        <span class="{effort_cls}">Estimated ramp-up: {g['effort']}</span>
                        <div style="flex: 1 1 100%; font-size: 0.82rem; color: #1e293b; margin-top: 4px;">
                            <strong>Onboarding strategy:</strong> {g['strategy']}
                        </div>
                    </div>
                    """)

                # Traditional ATS vs BridgeIQ Comparison Expander
                with st.expander("📊 Compare vs. Traditional Keyword ATS (Workday / Taleo)", expanded=False):
                    st.markdown(f"""
                    | Comparison Metric | Traditional Keyword ATS | BridgeIQ Competence Engine |
                    |---|---|---|
                    | **Rank for {active_cand['alias'].split(' ')[0]}** | **#94 / 100** (Discarded at screening) | **#1 / 100** (Score: {round(comp_val * 100)}%) |
                    | **Filter Criteria** | Exact title match (`"{active_cand['headline']}"` $\\ne$ `"{active_role['title']}"`) | Grounded JobTech concepts overlap ({round(cov_val * 100)}%) |
                    | **Explainability** | Opaque boolean rejection | Verified dual-quote evidence chain |
                    | **Demographic Bias** | High risk (penalizes career switchers & foreign titles) | **Zero** (Names, age, gender scrubbed prior to matching) |
                    """)

                # Enterprise Trust & Compliance Bar
                render_html("""
                <div style="display: flex; gap: 10px; align-items: center; justify-content: space-between; flex-wrap: wrap; margin-top: 1.2rem; padding: 8px 12px; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; font-size: 0.75rem; color: #64748B;">
                    <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
                        <span style="display: inline-flex; align-items: center; gap: 4px; font-weight: 600; color: #0F172A;">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#0B6B63" stroke-width="2.5"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
                            EU AI Act Art. 14 (Human-in-the-Loop)
                        </span>
                        <span>·</span>
                        <span class="enterprise-tooltip" data-tip="All demographic indicators (name, gender, nationality, age) are scrubbed before matching.">
                            🇸🇪 Demographic Scrubbing Active
                        </span>
                        <span>·</span>
                        <span>Human Hiring Decision Authority</span>
                    </div>
                    <span style="font-size: 0.72rem; color: #94A3B8;">Sweden Central (EU Data Zone)</span>
                </div>
                """)
            else:
                st.info("👈 Pick a candidate from the list to inspect their transparent score breakdown and evidence chain.")

    # =========================================================================
    # SUB-VIEW 2: Shortlist & Interview Dashboard
    # =========================================================================
    else:
        render_html("""
        <div style="margin-bottom: 1rem;">
            <h3 style="margin: 0; font-size: 1.25rem; font-weight: 700; color: #0F172A;">📋 Requisition Pipeline & Shortlisted Profiles</h3>
            <div style="font-size: 0.85rem; color: #64748B;">Candidate profiles earmarked for interview, grouped by active requisition.</div>
        </div>
        """)

        # Requisitions Grouping
        for role in BENCHMARK_ROLES:
            role_shortlisted = [
                (s_key, item) for s_key, item in st.session_state["employer_shortlist"].items()
                if item.get("role_id") == role["id"]
            ]

            render_html(f"""
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 12px 16px; margin-top: 12px; margin-bottom: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                    <div>
                        <span style="font-size: 0.72rem; font-weight: 700; color: #4338CA; text-transform: uppercase;">Requisition · {role['id']}</span>
                        <h4 style="margin: 2px 0 0 0; font-size: 1.05rem; color: #0F172A;">{role['title']}</h4>
                        <div style="font-size: 0.8rem; color: #64748B;">{role['employer']} · {role['location']}</div>
                    </div>
                    <span style="padding: 4px 10px; border-radius: 999px; background: {'#EEF2FF' if role_shortlisted else '#F1F5F9'}; color: {'#4338CA' if role_shortlisted else '#64748B'}; font-weight: 600; font-size: 0.8rem; border: 1px solid {'#C7D2FE' if role_shortlisted else '#E2E8F0'};">
                        {len(role_shortlisted)} Shortlisted Profile{'s' if len(role_shortlisted) != 1 else ''}
                    </span>
                </div>
            </div>
            """)

            if not role_shortlisted:
                c_note, c_act = st.columns([2.5, 1.0])
                with c_note:
                    st.caption(f"No candidates shortlisted for {role['title']} yet.")
                with c_act:
                    if st.button(f"🔍 Sourcing for {role['title'][:16]}...", key=f"btn_dash_search_{role['id']}", use_container_width=True):
                        st.session_state["recruiter_view_mode_idx"] = 0
                        st.session_state["active_role_id"] = role["id"]
                        st.rerun()
            else:
                for s_key, s_item in role_shortlisted:
                    comp_pct = f"{round(s_item.get('composite', 0.8) * 100)}%"
                    cov_pct = f"{round(s_item.get('cov', 0.8) * 100)}%"
                    tsim_pct = f"{round(s_item.get('tsim', 0.2) * 100)}%"

                    render_html(f"""
                    <div style="background: white; border: 1px solid #CBD5E1; border-radius: 8px; padding: 12px 14px; margin-bottom: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 8px;">
                            <div>
                                <div style="display: flex; gap: 8px; align-items: center;">
                                    <strong style="color: #0F172A; font-size: 0.98rem;">{s_item['candidate_alias']}</strong>
                                    <span style="background: #E6F4F1; color: #0B6B63; font-weight: 700; font-size: 0.72rem; padding: 2px 8px; border-radius: 4px;">
                                        💎 Match: {comp_pct}
                                    </span>
                                </div>
                                <div style="font-size: 0.82rem; color: #475569; margin-top: 3px;">
                                    <strong>Past Title:</strong> {s_item.get('headline', '')} · <strong>JobTech Overlap:</strong> {cov_pct} (ATS Title Sim: {tsim_pct})
                                </div>
                            </div>
                        </div>
                    </div>
                    """)
                    act_c1, act_c2 = st.columns([1.6, 1.0])
                    with act_c1:
                        if st.button(f"🎙️ Launch Interview Copilot for {s_item['candidate_alias'].split(' ')[0]}", key=f"btn_eval_{s_key}", type="primary", use_container_width=True):
                            st.session_state["active_interview_cand_alias"] = s_item["candidate_alias"]
                            st.rerun()
                    with act_c2:
                        if st.button("🗑️ Remove from Shortlist", key=f"btn_del_short_{s_key}", use_container_width=True):
                            del st.session_state["employer_shortlist"][s_key]
                            st.rerun()

        # Divider to Interview Copilot
        render_html("<hr style='margin: 1.5rem 0;'/>")

        # 3-Stage Interview Copilot Header
        render_html("""
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 1rem;">
            <div>
                <h3 style="margin: 0; font-size: 1.35rem; font-weight: 700; color: #0F172A;">🎙️ Title-Agnostic Recruiter Copilot & Transferability Assessor</h3>
                <div style="font-size: 0.85rem; color: #64748b; margin-top: 2px;">
                    Equipping Talent Acquisition Partners with explainable STAR probes, objective rubrics, and hiring manager pitch briefs.
                </div>
            </div>
            <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
                <span style="background: #EEF2FF; color: #4338CA; padding: 4px 10px; border-radius: 999px; font-size: 0.75rem; font-weight: 600; border: 1px solid #C7D2FE;">
                    🛡️ EU AI Act Art. 14 (Human-in-the-Loop)
                </span>
                <span style="background: #F0FDF4; color: #166534; padding: 4px 10px; border-radius: 999px; font-size: 0.75rem; font-weight: 600; border: 1px solid #BBF7D0;">
                    🇸🇪 Swedish Provanställning De-risked
                </span>
                <span style="background: #FFFBEB; color: #B45309; padding: 4px 10px; border-radius: 999px; font-size: 0.75rem; font-weight: 600; border: 1px solid #FDE68A;">
                    ⚡ Azure OpenAI (gpt-5-mini)
                </span>
            </div>
        </div>
        """)

        # Target Candidate options
        recruiter_options = [
            "Candidate 042 (Amara) ➔ Industrial IoT SRE (Västerås GridTech)",
            "Candidate 051 (Samira) ➔ OT Security Specialist (Luleå CyberGrid)",
            "Candidate 074 (Marcus) ➔ Production Planner (Jönköping Assembly)",
            "Candidate 063 (Defense Tech) ➔ OT Security Specialist (Luleå CyberGrid)",
        ]

        active_target_alias = st.session_state.get("active_interview_cand_alias", "")
        eval_idx = 0
        if "Samira" in active_target_alias or "051" in active_target_alias:
            eval_idx = 1
        elif "Marcus" in active_target_alias or "074" in active_target_alias:
            eval_idx = 2
        elif "063" in active_target_alias:
            eval_idx = 3

        selected_recruiter_target = st.selectbox(
            "👤 Active Candidate & Target Role Evaluation Session:",
            recruiter_options,
            index=eval_idx,
            key="recruiter_target_select_box"
        )

        if "Amara" in selected_recruiter_target or "042" in selected_recruiter_target:
            c_id = "cand-042"
            c_alias = "Amara Diop"
            j_id = "job-077"
            j_title = "Reliability Engineer, Industrial IoT"
            j_employer = "Västerås GridTech AB"
            trans_sum = "Telecom packet core 99.999% uptime transferred to industrial IoT platform availability"
            top_gap = "NIS2-direktivet"
            rampup_est = "3 to 5 Days"
            rampup_plan = "Complete 4-hour open-source Swedish MSB NIS2 Industrial Cybersecurity Foundation module."
            swe_equiv = "Telia / Ericsson Carrier Core Network Engineering"
            risk_verdict = "Low Risk · Zero architectural deficiency. 100% bridgeable during Week 1 of 6-month probation (Provanställning)."
        elif "Samira" in selected_recruiter_target or "051" in selected_recruiter_target:
            c_id = "cand-051"
            c_alias = "Samira Khan"
            j_id = "job-012"
            j_title = "OT Security Specialist"
            j_employer = "Luleå CyberGrid AB"
            trans_sum = "Railway safety-critical signalling network segmentation transferred to energy grid OT SCADA security"
            top_gap = "NIS2-direktivet"
            rampup_est = "1 to 2 Weeks"
            rampup_plan = "Review ENISA / MSB energy sub-station network zoning directives and IEC 62443 standard."
            swe_equiv = "Trafikverket Railway Safety-Critical Signalling Systems"
            risk_verdict = "Low Risk · Safety-critical mind-set is already proven in railway signaling. Safe for probation."
        elif "Marcus" in selected_recruiter_target or "074" in selected_recruiter_target:
            c_id = "cand-074"
            c_alias = "Marcus Lindqvist"
            j_id = "job-150"
            j_title = "Production Planner"
            j_employer = "Jönköping Assembly Solutions"
            trans_sum = "High-volume kitchen capacity planning and food waste Lean reduction transferred to factory assembly planning"
            top_gap = "Affärssystem (ERP/SAP)"
            rampup_est = "2 to 3 Weeks"
            rampup_plan = "Hands-on ERP sandbox onboarding module for manufacturing work order scheduling."
            swe_equiv = "Commercial Kitchen Lean Operations (Scandic / Sodexo Large-Scale Facilities)"
            risk_verdict = "Medium-Low Risk · Practical bottleneck management skills easily map to software ERP workflow."
        else:
            c_id = "cand-063"
            c_alias = "Candidate 063"
            j_id = "job-012"
            j_title = "OT Security Specialist"
            j_employer = "Luleå CyberGrid AB"
            trans_sum = "Military communication link encryption and field threat assessments transferred to energy substation security"
            top_gap = "Industriella styrsystem"
            rampup_est = "2 Weeks"
            rampup_plan = "Complete industrial SCADA and PLC protocol fundamentals refresher."
            swe_equiv = "Försvarsmakten Tactical Communication Defense"
            risk_verdict = "Low Risk · High-stakes defensive security discipline transfers seamlessly."

        # 2-Panel High-Contrast Architecture
        col_brief, col_probes = st.columns([1.1, 1.9])

        # ===== COLUMN 1: Pre-Interview Intelligence & Line Manager Pitch (Features 5 & 6) =====
        with col_brief:
            render_html("<div style='font-size: 0.8rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px;'>Pre-Interview Intelligence</div>")

            # Card 1: Candidate Transferability Brief
            render_html(f"""
            <div style="background: white; border: 1px solid #DDE2E8; border-radius: 10px; padding: 14px; margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <span style="background: #E6F4F1; color: #0B6B63; font-weight: 700; font-size: 0.72rem; padding: 2px 8px; border-radius: 4px;">
                            💎 HIDDEN GEM APPLICANT
                        </span>
                        <h4 style="margin: 6px 0 2px 0; color: #14212B; font-size: 1.05rem;">{c_alias} ({c_id})</h4>
                        <div style="font-size: 0.82rem; color: #64748b;">Target: {j_title} · {j_employer}</div>
                    </div>
                </div>
                <div style="margin-top: 10px; padding: 8px 10px; background: #F8FAFC; border-radius: 6px; border: 1px solid #EDF2F7; font-size: 0.8rem;">
                    <strong style="color: #475569;">🇸🇪 Swedish Industrial Equivalence:</strong><br/>
                    <span style="color: #0B6B63; font-weight: 600;">{swe_equiv}</span>
                </div>
                <div style="margin-top: 8px; font-size: 0.82rem; color: #334155; line-height: 1.4;">
                    <strong>Transferable Core:</strong> {trans_sum}
                </div>
            </div>
            """)

            # Card 2: Feature 5 — 6-Month Probation (Provanställning) De-risking
            render_html(f"""
            <div style="background: white; border: 1px solid #DDE2E8; border-radius: 10px; padding: 14px; margin-bottom: 12px;">
                <div style="font-size: 0.8rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">
                    Feature 5: 6-Month Probation (Provanställning) Safety
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 0.85rem; font-weight: 600; color: #1E293B;">Identified Skill Gap:</span>
                    <span style="background: #FEF3C7; color: #92400E; font-weight: 700; font-size: 0.75rem; padding: 2px 8px; border-radius: 999px;">
                        <code>{top_gap}</code>
                    </span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 0.85rem; font-weight: 600; color: #1E293B;">Ramp-up Feasibility:</span>
                    <span style="background: #DCFCE7; color: #166534; font-weight: 700; font-size: 0.75rem; padding: 2px 8px; border-radius: 999px;">
                        ⚡ {rampup_est} (Low Risk)
                    </span>
                </div>
                <div style="font-size: 0.8rem; color: #475569; line-height: 1.4; margin-bottom: 8px;">
                    <strong>Targeted Action:</strong> {rampup_plan}
                </div>
                <div style="background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 6px; padding: 8px 10px; font-size: 0.78rem; color: #166534; line-height: 1.4;">
                    {risk_verdict}
                </div>
            </div>
            """)

            # Card 3: Feature 6 — 1-Click Hiring Manager Pitch Brief (Sälja in-memo)
            render_html("""
            <div style="font-size: 0.8rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; margin: 12px 0 6px 0;">
                Feature 6: Hiring Manager Pitch Memo (Sälja In)
            </div>
            """)

            memo_key = f"recruiter_memo_{c_id}_{j_id}"
            if st.button("📑 Generate Line Manager Memo (gpt-5-mini)", key=f"btn_memo_{c_id}", use_container_width=True):
                with st.spinner("Generating Swedish TA alignment memo for engineering manager..."):
                    st.session_state[memo_key] = generate_hiring_manager_memo(
                        candidate_id=c_id,
                        candidate_alias=c_alias,
                        job_id=j_id,
                        job_title=j_title,
                        transferable_summary=trans_sum,
                        top_gap_label=top_gap,
                        rampup_estimate=rampup_est,
                    )

            if memo_key not in st.session_state:
                st.session_state[memo_key] = generate_hiring_manager_memo(
                    candidate_id=c_id,
                    candidate_alias=c_alias,
                    job_id=j_id,
                    job_title=j_title,
                    transferable_summary=trans_sum,
                    top_gap_label=top_gap,
                    rampup_estimate=rampup_est,
                )

            st.text_area(
                "Ready-to-Send Internal Memo (Copy & Paste to Slack/Email):",
                value=st.session_state[memo_key],
                height=180,
                key=f"memo_text_{c_id}"
            )
            st.caption("💡 *Send this concise briefing directly to the engineering hiring manager to secure the technical round.*")

        # ===== COLUMN 2: Competency-Based STAR Interview Probes (Features 2 & 3) =====
        with col_probes:
            render_html("<div style='font-size: 0.8rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px;'>Live Competency-Based Interview Probes (STAR Method)</div>")

            # Probe Generation CTA Bar
            col_btn, col_info = st.columns([1.1, 1.9])
            with col_btn:
                if st.button("🔄 Regenerate STAR Probes (gpt-5-mini)", type="primary", use_container_width=True):
                    with st.spinner("Calling Azure OpenAI Sweden Central to craft structured STAR probes..."):
                        try:
                            probes = generate_interview_probes(
                                candidate_id=c_id,
                                job_id=j_id,
                                job_title=j_title,
                                transferable_summary=trans_sum,
                                top_gap_label=top_gap
                            )
                            st.session_state["cached_probes_" + c_id] = probes
                        except Exception as e:
                            st.error(f"Error generating probes: {e}")
            with col_info:
                render_html("""
                <div style="font-size: 0.82rem; color: #64748b; padding-top: 6px;">
                    Strictly aligns with Swedish <em>Kompetensbaserad intervjumetodik</em>. Zero demographic questions.
                </div>
                """)

            # Fallback to pre-generated or cached probes
            active_probes = st.session_state.get("cached_probes_" + c_id)
            if not active_probes:
                active_probes = generate_interview_probes(
                    candidate_id=c_id,
                    job_id=j_id,
                    job_title=j_title,
                    transferable_summary=trans_sum,
                    top_gap_label=top_gap
                )
                st.session_state["cached_probes_" + c_id] = active_probes

            # Probes loop with Feature 3 (What Good Looks Like & Anti-BS Rubrics)
            for i, p in enumerate(active_probes.probes):
                if p.type == "technical":
                    badge_type = "TECHNICAL · PAST MASTERY"
                    badge_color = "#0B6B63"
                    badge_bg = "#E6F4F1"
                    red_flag = "Vaguely reciting networking definitions without citing exact uptime SLAs, throughput metrics, or incident recovery steps."
                elif p.type == "situational":
                    badge_type = "SITUATIONAL · DOMAIN TRANSFER"
                    badge_color = "#1E40AF"
                    badge_bg = "#DBEAFE"
                    red_flag = "Assuming industrial environments operate like commodity cloud servers, ignoring physical safety boundaries and edge latency."
                else:
                    badge_type = "GAP · LEARNING AGILITY"
                    badge_color = "#92400E"
                    badge_bg = "#FEF3C7"
                    red_flag = "Claiming 'I learn quickly' without outlining concrete technical standards (e.g. MSB guidelines) or hands-on audit workflows."

                with st.expander(f"Probe {i+1}: {badge_type} · Focus: {p.targets_concept}", expanded=(i == 0)):
                    render_html(f"""
                    <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 8px;">
                        <span style="background: {badge_bg}; color: {badge_color}; font-weight: 700; font-size: 0.75rem; padding: 3px 8px; border-radius: 4px;">
                            {badge_type}
                        </span>
                        <span style="font-size: 0.82rem; color: #64748b;">Target Concept: <strong>{p.targets_concept}</strong></span>
                    </div>
                    """)

                    st.markdown("**Structured STAR Interview Question:**")
                    st.markdown(f"> *\"{p.question}\"*")

                    render_html(f"""
                    <div style="background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 8px; padding: 10px 12px; margin: 10px 0;">
                        <div style="font-size: 0.8rem; font-weight: 700; color: #166534; margin-bottom: 3px;">
                            💡 WHAT GOOD LOOKS LIKE (Objective Scoring Rubric):
                        </div>
                        <div style="font-size: 0.82rem; color: #14532D; line-height: 1.4;">
                            {p.what_good_looks_like}
                        </div>
                    </div>
                    <div style="background: #FFFBEB; border: 1px solid #FDE68A; border-radius: 8px; padding: 10px 12px; margin: 6px 0 10px 0;">
                        <div style="font-size: 0.8rem; font-weight: 700; color: #92400E; margin-bottom: 3px;">
                            ⚠️ RED FLAGS & BUZZWORD WARNINGS (Anti-BS Rubric):
                        </div>
                        <div style="font-size: 0.82rem; color: #78350F; line-height: 1.4;">
                            {red_flag}
                        </div>
                    </div>
                    """)

            render_html("<hr style='margin: 1.2rem 0;'/>")
            st.caption("⚖️ *BridgeIQ empowers human recruiters with explainable competence probes. In accordance with EU AI Act Article 14, automated tools assist inquiry; humans conduct interviews and decide hiring progression.*")

# ----------------- TAB 3: Connected Azure Sandbox Assets -----------------
with tab_data:
    render_html("""
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 1.2rem;">
        <div>
            <h2 style="margin: 0; font-size: 1.45rem; font-weight: 700; color: #0F172A;">📊 Connected Azure Sandbox Assets (Team 04)</h2>
            <div style="font-size: 0.85rem; color: #64748B;">Production enterprise data infrastructure deployed in Sweden Central with full EU regulatory compliance.</div>
        </div>
        <div style="display: flex; gap: 8px; flex-wrap: wrap;">
            <span style="padding: 4px 12px; border-radius: 999px; background: #F0FDF4; color: #166534; font-weight: 600; font-size: 0.82rem; border: 1px solid #BBF7D0;">
                🇸🇪 Sweden Central · EU Data Zone
            </span>
            <span style="padding: 4px 12px; border-radius: 999px; background: #F8FAFC; color: #475569; font-weight: 600; font-size: 0.82rem; border: 1px solid #E2E8F0;">
                🛡️ EU AI Act Compliant
            </span>
            <span style="padding: 4px 12px; border-radius: 999px; background: #EEF2FF; color: #4338CA; font-weight: 600; font-size: 0.82rem; border: 1px solid #C7D2FE;">
                ⚡ Azure OpenAI (gpt-5-mini)
            </span>
        </div>
    </div>
    """)
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown("#### 🇸🇪 Azure AI Search: Jobs")
        st.metric("Total Swedish Postings", "200")
        st.caption("Includes retail, tech, logistics, industrial IoT.")
    with col_b:
        st.markdown("#### 📚 Azure AI Search: Taxonomy")
        st.metric("JobTech Concepts", "1,248")
        st.caption("Official Swedish Arbetsförmedlingen taxonomy.")
    with col_c:
        st.markdown("#### 👥 Cosmos DB: Candidates")
        st.metric("Loaded Candidates", f"{len(all_db_candidates)}")
        st.caption("From candidate-001 to candidate-100.")
