"""
BridgeIQ Enterprise Design Tokens & Theme System
Standardized across all views to eliminate color drift and guarantee WCAG AA compliance.
"""

from html import escape

TOKENS = {
    # Nordic Enterprise Colors
    "emerald": "#0B6B63",      # Main competence / Brand focus
    "emerald_light": "#F0FDF4",# Active pill background
    "emerald_border": "#BBF7D0",# Active pill border
    "emerald_cv": "#059669",   # Candidate CV delivery border (contrast 3.77:1)
    
    "indigo": "#1E40AF",       # Semantic vector embedding (WCAG AA 8.72:1)
    "indigo_light": "#EEF2FF", # Indigo badge background
    "indigo_border": "#C7D2FE",# Indigo badge border
    
    "amber": "#92400E",        # Hidden Gem / Skill gaps (WCAG AA 7.09:1)
    "amber_light": "#FEF3C7",  # Amber badge background
    "amber_border": "#FDE68A", # Amber badge border
    
    "red": "#991B1B",          # Risk / Rejection
    "red_light": "#FEF2F2",
    
    # Neutral Slates
    "slate_900": "#0F172A",    # Dark slate header / text
    "slate_700": "#334155",    # Body text
    "slate_600": "#475569",    # Secondary body text
    "slate_500": "#64748B",    # Muted captions / JD border (contrast 4.76:1)
    "slate_200": "#E2E8F0",    # Fine hairline borders
    "slate_100": "#F1F5F9",    # Neutral pills
    "slate_50": "#F8FAFC",     # Light background
}

def safe_text(text: str) -> str:
    """HTML escape dynamic text to prevent layout injection."""
    if not text:
        return ""
    return escape(str(text))

def nordic_quote(text: str) -> str:
    """Format quote using Nordic/standard double quotes rather than Chinese curly quotes."""
    clean = str(text).strip(" \t\n\r\"'“”")
    return f'"{clean}"'
