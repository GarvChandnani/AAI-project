"""SupportPilot Modern Design System & UI Components.

Provides enterprise SaaS styling, modern typography, glassmorphism card elevation,
custom chat bubble aesthetics, and top-tier web application chrome.
"""
from __future__ import annotations

import streamlit as st


MODERN_CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">

<style>
/* ==========================================================================
   GLOBAL RESET & TYPOGRAPHY
   ========================================================================== */
:root {
    --sp-primary: #4f46e5;
    --sp-primary-light: #6366f1;
    --sp-primary-dark: #3730a3;
    --sp-primary-glow: rgba(99, 102, 241, 0.25);
    
    --sp-accent: #0ea5e9;
    --sp-accent-glow: rgba(14, 165, 233, 0.25);
    
    --sp-success: #10b981;
    --sp-success-bg: rgba(16, 185, 129, 0.12);
    --sp-warning: #f59e0b;
    --sp-warning-bg: rgba(245, 158, 11, 0.12);
    --sp-danger: #ef4444;
    --sp-danger-bg: rgba(239, 68, 68, 0.12);
    
    --sp-card-radius: 14px;
    --sp-btn-radius: 10px;
}

html, body, [class*="css"], [class*="st-"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    letter-spacing: -0.011em;
}

code, pre, [data-testid="stCodeBlock"] * {
    font-family: 'JetBrains Mono', ui-monospace, monospace !important;
}

/* ==========================================================================
   APP CHROME & STREAMLIT OVERRIDES
   ========================================================================== */
/* Hide default distracting Streamlit chrome */
[data-testid="stToolbar"] {
    opacity: 0.15 !important;
    transition: opacity 0.2s ease !important;
}
[data-testid="stToolbar"]:hover {
    opacity: 1 !important;
}
[data-testid="stDecoration"] {
    display: none !important;
}
#MainMenu, footer {
    visibility: hidden !important;
}

.block-container {
    padding-top: 1.25rem !important;
    padding-bottom: 4rem !important;
    max-width: 1480px !important;
}

/* ==========================================================================
   SIDEBAR MODERN SAAS STYLING
   ========================================================================== */
[data-testid="stSidebar"] {
    border-right: 1px solid rgba(148, 163, 184, 0.15) !important;
    box-shadow: 2px 0 16px rgba(0, 0, 0, 0.04) !important;
}

[data-testid="stSidebarNav"] {
    padding-top: 0.75rem !important;
}

[data-testid="stSidebarNav"] ul {
    gap: 3px !important;
}

[data-testid="stSidebarNav"] a {
    border-radius: 10px !important;
    padding: 0.6rem 0.85rem !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

[data-testid="stSidebarNav"] a:hover {
    transform: translateX(3px) !important;
}

[data-testid="stSidebarNav"] a[aria-current="page"] {
    background: linear-gradient(90deg, rgba(79, 70, 229, 0.12) 0%, rgba(99, 102, 241, 0.06) 100%) !important;
    border-left: 3px solid #6366f1 !important;
    font-weight: 600 !important;
}

/* ==========================================================================
   METRIC TILES (SaaS KPI CARDS)
   ========================================================================== */
[data-testid="stMetric"] {
    background: var(--secondary-background-color) !important;
    border: 1px solid rgba(148, 163, 184, 0.18) !important;
    border-radius: var(--sp-card-radius) !important;
    padding: 1.1rem 1.25rem !important;
    box-shadow: 0 2px 8px -2px rgba(0, 0, 0, 0.04), 0 1px 3px rgba(0, 0, 0, 0.02) !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    position: relative !important;
    overflow: hidden !important;
}

[data-testid="stMetric"]::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #6366f1, #0ea5e9);
    opacity: 0.85;
}

[data-testid="stMetric"]:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 10px 24px -4px rgba(0, 0, 0, 0.08), 0 4px 8px -2px rgba(0, 0, 0, 0.04) !important;
    border-color: rgba(99, 102, 241, 0.35) !important;
}

[data-testid="stMetricLabel"] {
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    opacity: 0.75 !important;
}

[data-testid="stMetricValue"] {
    font-size: 1.85rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.03em !important;
    margin-top: 0.2rem !important;
}

/* ==========================================================================
   CHAT MESSAGES & BUBBLES (INTERCOM / CRISP AESTHETICS)
   ========================================================================== */
[data-testid="stChatMessage"] {
    border-radius: 16px !important;
    padding: 1rem 1.2rem !important;
    margin-bottom: 0.85rem !important;
    border: 1px solid rgba(148, 163, 184, 0.15) !important;
    box-shadow: 0 2px 6px -1px rgba(0, 0, 0, 0.03) !important;
    transition: all 0.2s ease !important;
}

[data-testid="stChatMessage"]:hover {
    box-shadow: 0 4px 12px -2px rgba(0, 0, 0, 0.06) !important;
}

[data-testid="stChatInput"] {
    border-radius: 24px !important;
    border: 1px solid rgba(99, 102, 241, 0.3) !important;
    box-shadow: 0 4px 14px -2px rgba(0, 0, 0, 0.06) !important;
    transition: all 0.2s ease !important;
}

[data-testid="stChatInput"]:focus-within {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2) !important;
}

/* ==========================================================================
   BUTTONS & INPUTS
   ========================================================================== */
.stButton > button {
    border-radius: var(--sp-btn-radius) !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 0.5rem 1.1rem !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    border: 1px solid rgba(148, 163, 184, 0.25) !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%) !important;
    color: #ffffff !important;
    border: none !important;
    box-shadow: 0 4px 14px -2px rgba(79, 70, 229, 0.35) !important;
}

.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #4338ca 0%, #2563eb 100%) !important;
    box-shadow: 0 6px 18px -2px rgba(79, 70, 229, 0.45) !important;
}

/* ==========================================================================
   TABS & EXPANDERS
   ========================================================================== */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px !important;
    border-bottom: 1px solid rgba(148, 163, 184, 0.18) !important;
    padding-bottom: 4px !important;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px 8px 0 0 !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    padding: 0.6rem 1.2rem !important;
    transition: all 0.2s ease !important;
}

[data-testid="stExpander"] {
    border: 1px solid rgba(148, 163, 184, 0.18) !important;
    border-radius: var(--sp-card-radius) !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02) !important;
    overflow: hidden !important;
}

[data-testid="stExpander"] summary {
    font-weight: 600 !important;
    padding: 0.75rem 1rem !important;
}

/* ==========================================================================
   DATAFRAMES & TABLES
   ========================================================================== */
[data-testid="stDataFrame"] {
    border: 1px solid rgba(148, 163, 184, 0.18) !important;
    border-radius: var(--sp-card-radius) !important;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.02) !important;
    overflow: hidden !important;
}

/* ==========================================================================
   CUSTOM WEB CARDS & HERO COMPONENTS
   ========================================================================== */
.sp-top-nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.85rem 1.5rem;
    margin-bottom: 1.5rem;
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.06) 0%, rgba(14, 165, 233, 0.04) 100%);
    border: 1px solid rgba(99, 102, 241, 0.18);
    border-radius: 16px;
    backdrop-filter: blur(10px);
}

.sp-brand-badge {
    display: flex;
    align-items: center;
    gap: 12px;
}

.sp-logo-glow {
    width: 38px;
    height: 38px;
    border-radius: 10px;
    background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 20px;
    box-shadow: 0 4px 14px rgba(79, 70, 229, 0.35);
}

.sp-status-pulse {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: #10b981;
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
    animation: sp-pulse 2s infinite;
}

@keyframes sp-pulse {
    0% {
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
    }
    70% {
        box-shadow: 0 0 0 8px rgba(16, 185, 129, 0);
    }
    100% {
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
    }
}

.sp-pill-tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}

.sp-provenance {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 8px;
    font-size: 0.8rem;
    background: rgba(148, 163, 184, 0.08);
    border: 1px solid rgba(148, 163, 184, 0.15);
    margin: 4px 0 10px 0;
}
</style>
"""


def inject_theme():
    """Injects the global modern SaaS design system into the Streamlit session."""
    st.markdown(MODERN_CSS, unsafe_allow_html=True)


def render_top_bar(store, current_page: str = ""):
    """Renders a sleek top navigation banner with brand identity and live system telemetry."""
    import agents as A

    lm = A.llm.status()
    is_llm = lm.get("mode") == "llm"
    model_name = lm.get("model", "Rules Engine")
    tenant_name = store.tenant.get("name", "Demo Store")
    simulated = store.adapter.simulated

    badge_html = f"""
    <div class="sp-top-nav">
        <div class="sp-brand-badge">
            <div class="sp-logo-glow">⚡</div>
            <div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 1.18rem; font-weight: 800; letter-spacing: -0.02em;">SupportPilot</span>
                    <span class="sp-pill-tag" style="background: rgba(79, 70, 229, 0.15); color: #6366f1; border: 1px solid rgba(99, 102, 241, 0.3);">
                        AI AGENT DESK
                    </span>
                    {f'<span style="font-size: 0.85rem; opacity: 0.5;">/ {current_page}</span>' if current_page else ''}
                </div>
                <div style="font-size: 0.8rem; opacity: 0.65; margin-top: 1px;">
                    Enterprise Multi-Agent Customer Experience & Autonomous Resolution System
                </div>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 14px; flex-wrap: wrap;">
            <div class="sp-pill-tag" style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.25); color: #10b981;">
                <span class="sp-status-pulse"></span>
                <span>SYSTEM ONLINE</span>
            </div>
            <div class="sp-pill-tag" style="background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.25); color: #818cf8;">
                <span>{'🧠 ' + model_name if is_llm else '⚙️ Deterministic Rules'}</span>
            </div>
            <div class="sp-pill-tag" style="background: rgba(14, 165, 233, 0.1); border: 1px solid rgba(14, 165, 233, 0.25); color: #38bdf8;">
                <span>🏢 {tenant_name} ({'Simulated' if simulated else 'Live'})</span>
            </div>
        </div>
    </div>
    """
    st.markdown(badge_html, unsafe_allow_html=True)


def render_provenance_badge(kind: str, detail: str = "", store=None):
    """Renders a sleek modern data provenance pill tag instead of raw text."""
    from .common import rel, workspace
    store = store or workspace()

    if kind == "support":
        label = f"🗄️ <strong>Support Database</strong> · <code>{rel(store.path)}</code>"
        if detail:
            label += f" → <code>{detail}</code>"
    elif kind == "company":
        sim = " (simulated)" if store.adapter.simulated else ""
        label = f"🏢 <strong>{store.adapter.name}{sim}</strong> · Live adapter"
        if detail:
            label += f" → <code>{detail}</code>"
    elif kind == "warehouse":
        label = f"📊 <strong>Analytics Warehouse</strong> · <code>{rel(detail)}</code>"
    elif kind == "files":
        label = f"📄 <strong>Knowledge Files</strong> · <code>{detail or 'docs/help-center/'}</code>"
    elif kind == "platform":
        from agents.tenancy import get_registry
        label = f"🔐 <strong>Platform Registry</strong> · <code>{rel(get_registry().store.path)}</code>"
        if detail:
            label += f" → <code>{detail}</code>"
    else:
        label = f"ℹ️ <strong>Data</strong> · {detail}"

    st.markdown(f'<div class="sp-provenance">{label}</div>', unsafe_allow_html=True)
