"""SupportPilot dashboard — `streamlit run app.py`.

Pages: Support desk · Tickets & approvals · Live operations · Customer intelligence · Knowledge base · Data explorer ·
Settings. Every page labels where its data is stored (support database, company system, analytics warehouse, files).
"""
import hmac

import streamlit as st

import agents as A
from agents.shared_agent import get_secret
from telegram_bot import start_in_background as start_telegram
from ui import data_explorer, desk, intelligence, knowledge, live_ops, operations, settings
from ui.common import workspace
from ui.style import inject_theme

st.set_page_config(
    page_title="SupportPilot — Autonomous AI Customer Support",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_theme()

# Optional login: set SUPPORTPILOT_DASHBOARD_PASSWORD whenever anyone but you can reach the dashboard.
_pw = get_secret("SUPPORTPILOT_DASHBOARD_PASSWORD")
if _pw and not st.session_state.get("dash_ok"):
    st.markdown("""
    <div style="max-width: 440px; margin: 4rem auto; padding: 2rem; border-radius: 18px; border: 1px solid rgba(99, 102, 241, 0.25); background: var(--secondary-background-color); box-shadow: 0 10px 30px rgba(0,0,0,0.08); text-align: center;">
        <div style="font-size: 40px; margin-bottom: 10px;">⚡</div>
        <h2 style="margin: 0; font-weight: 800; letter-spacing: -0.02em;">SupportPilot</h2>
        <p style="opacity: 0.7; font-size: 0.9rem; margin-top: 4px; margin-bottom: 24px;">Please authenticate to access the enterprise dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    with st.container():
        entered = st.text_input("Dashboard Password", type="password", placeholder="Enter access token...")
        if entered and hmac.compare_digest(entered.encode(), _pw.encode()):
            st.session_state["dash_ok"] = True
            st.rerun()
        elif entered:
            st.error("Invalid authentication credentials.")
    st.stop()

store = workspace()
# one long-polling Telegram bot per server process (de-duplicated); None until TELEGRAM_BOT_TOKEN is set
st.session_state["_tg_bot"] = start_telegram(store, use_llm=A.llm_enabled())

with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 0.85rem; padding-bottom: 0.85rem; border-bottom: 1px solid rgba(148, 163, 184, 0.15);">
        <div style="width: 38px; height: 38px; border-radius: 10px; background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%); display: flex; align-items: center; justify-content: center; font-size: 20px; color: white; box-shadow: 0 4px 14px rgba(79, 70, 229, 0.35);">⚡</div>
        <div>
            <div style="font-weight: 800; font-size: 1.15rem; letter-spacing: -0.02em; line-height: 1.15;">SupportPilot</div>
            <div style="font-size: 0.72rem; opacity: 0.6; text-transform: uppercase; letter-spacing: 0.06em; font-weight: 700; color: #818cf8;">Agentic Support Desk</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    lm = A.llm.status()
    is_llm = lm.get("mode") != "fallback"
    pending = len(A.approvals.pending(store))

    st.markdown(f"""
    <div style="background: rgba(148, 163, 184, 0.05); border: 1px solid rgba(148, 163, 184, 0.14); border-radius: 12px; padding: 10px 12px; margin-bottom: 1rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <span style="font-size: 0.73rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; opacity: 0.65;">Tenant</span>
            <span style="font-size: 0.78rem; font-weight: 700; color: #38bdf8;">{store.tenant.get('name', 'demostore')}</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <span style="font-size: 0.73rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; opacity: 0.65;">Data Source</span>
            <span style="font-size: 0.78rem; opacity: 0.85;">{'🏢 Simulated Adapter' if store.adapter.simulated else '🏢 Live Adapter'}</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 0.73rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; opacity: 0.65;">AI Engine</span>
            <span style="font-size: 0.78rem; font-weight: 600; color: {'#818cf8' if is_llm else '#f59e0b'};">{'🧠 ' + lm['model'].split('/')[-1] if is_llm else '⚙️ Rules Engine'}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.toggle(
        "Enable LLM Mode",
        value=A.llm_enabled(),
        disabled=not A.llm_enabled(),
        key="use_llm",
        help="When disabled, uses deterministic policy rules. Actions and approvals are always verified by policy and data.",
    )

    if pending:
        st.markdown(f"""
        <div style="background: rgba(245, 158, 11, 0.12); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 10px; padding: 8px 12px; margin-top: 8px; display: flex; align-items: center; gap: 8px; color: #f59e0b; font-weight: 600; font-size: 0.82rem;">
            <span>⏳</span> <span>{pending} action(s) need approval</span>
        </div>
        """, unsafe_allow_html=True)

nav = st.navigation({
    "Operations": [
        st.Page(desk.page, title="Support Desk", icon=":material/forum:", url_path="desk", default=True),
        st.Page(operations.page, title="Tickets & Approvals", icon=":material/confirmation_number:", url_path="tickets"),
    ],
    "Analytics & AI": [
        st.Page(live_ops.page, title="Live Operations", icon=":material/monitoring:", url_path="operations"),
        st.Page(intelligence.page, title="Customer Intelligence", icon=":material/insights:", url_path="intelligence"),
    ],
    "Data & Systems": [
        st.Page(knowledge.page, title="Knowledge Base", icon=":material/menu_book:", url_path="knowledge"),
        st.Page(data_explorer.page, title="Data Explorer", icon=":material/database:", url_path="data"),
        st.Page(settings.page, title="System Settings", icon=":material/settings:", url_path="settings"),
    ],
})
nav.run()
