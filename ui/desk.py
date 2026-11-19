"""Support desk: talk to SupportPilot as a customer (web chat) or watch the live Telegram bot."""
from __future__ import annotations

import pandas as pd
import streamlit as st

import agents as A
from agent_flow import render_flow
from agents.shared_agent import fmt_ts

from .common import ACTION_ICON, customers, step_lines, theme, where, workspace
from .style import render_top_bar

EXAMPLES = [
    "",
    "My order was delivered but I received the wrong item",
    "My payment failed but money was deducted",
    "I can't login, it says my account is locked",
    "Where is my order? It's late",
    "I paid for Premium but my subscription is still not activated",
    "My internet is not working since morning",
    "There's a transaction I did not make",
    "I want a refund for my laptop, order ORD12353",
    "What are the delivery charges for cash on delivery?",
    "I want to talk to a human",
]

QUICK_CHIPS = [
    ("📦 Wrong item", "My order was delivered but I received the wrong item"),
    ("💳 Payment failed", "My payment failed but money was deducted"),
    ("🔒 Account locked", "I can't login, it says my account is locked"),
    ("⚡ Internet down", "My internet is not working since morning"),
    ("🚚 Order late", "Where is my order? It's late"),
    ("💰 Laptop refund", "I want a refund for my laptop, order ORD12353"),
]


def _state():
    ss = st.session_state
    for k, v in dict(conv_id=None, customer_id=None, channel="web", turns=[], pending=None).items():
        ss.setdefault(k, v)
    return ss


def _new():
    st.session_state.conv_id, st.session_state.turns = None, []


def _on_customer():
    st.session_state.customer_id = st.session_state.desk_customer
    _new()


def _on_example():
    text = st.session_state.get("desk_example")
    if text:
        st.session_state.pending = text
        st.session_state.desk_example = ""


def _on_submit():
    if st.session_state.get("chat_box"):
        st.session_state.pending = st.session_state.chat_box


def _on_rating(key):
    value = st.session_state.get(key)
    if value is not None:
        st.session_state.pending = str(value + 1)


def _sources(store, turn):
    """Where this reply's facts came from: KB articles, company-system reads, actions, LLM."""
    run = store.get("workflow_runs", turn.get("run_id")) if turn.get("run_id") else None
    arts = [a for a in turn.get("articles", []) if a.get("audience", "customer") == "customer"][:3]
    if arts:
        st.markdown("**Knowledge Citations**")
        for a in arts:
            st.caption(f"📄 {a['id']} · {a['title']} — v{a.get('version', 1)} in database `kb_articles` "
                       f"(source `{a.get('source', '')}`)")
    reads = [c for c in (run or {}).get("tool_calls", []) if c["kind"] == "read"]
    if reads:
        st.markdown(f"**Company Records Read** · {store.adapter.name}" + (" (simulated)" if store.adapter.simulated else ""))
        st.dataframe(pd.DataFrame([dict(Tool=c["tool"].split(".", 1)[1], Query=", ".join(f"{k}={v}" for k, v in c["args"].items()),
                                        Result=c["status"] if c["status"] != "ok" else (
                                            f"{c['result'].get('count')} record(s)" if "count" in c["result"] else "found"))
                                   for c in reads]), hide_index=True, width="stretch", height=min(38 * (len(reads) + 1), 260))
    acts = [a for a in turn.get("actions", []) if a["action"] != "notify_customer"]
    if acts:
        st.markdown("**Actions Executed**")
        for a in acts:
            au = a.get("authorization") or {}
            st.caption(f"{ACTION_ICON.get(a['status'], '•')} {a['label']} — {a['status']} · policy: {au.get('outcome')} "
                       f"({au.get('rule')}) · executed in {a.get('adapter')}{' (simulated)' if a.get('simulated') else ''}")
    lm = turn.get("llm") or {}
    st.caption(f"🧠 LLM: **{lm.get('mode', '—')}** — {lm.get('reason', '')} · saved as workflow run "
               f"**{turn.get('run_id', '—')}** in `workflow_runs`")


def _chat(store, use_llm):
    ss = _state()
    ids, labels = customers(store)

    # Top Control Bar (Customer & Channel Setup)
    c1, c2, c3, c4 = st.columns([2.4, 1.2, 2.4, 1.1], vertical_alignment="bottom")
    c1.selectbox(
        "Active Customer Session",
        ids,
        format_func=lambda c: "Guest (not logged in)" if c is None else labels.get(c, c),
        key="desk_customer",
        index=ids.index(ss.customer_id) if ss.customer_id in ids else 0,
        on_change=_on_customer,
        help="Simulate the customer profile communicating with SupportPilot",
    )
    c2.selectbox("Channel", list(A.CHANNELS), format_func=lambda c: A.CHANNELS[c], key="channel")
    c3.selectbox(
        "Select Demo Scenario",
        EXAMPLES,
        key="desk_example",
        on_change=_on_example,
        format_func=lambda t: "Choose a test scenario…" if not t else t,
    )
    c4.button("New Chat", icon=":material/add_comment:", on_click=_new, width="stretch")

    # Quick interactive scenario pills
    st.markdown(
        "<div style='font-size: 0.74rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; opacity: 0.65; margin: 8px 0 4px 0;'>⚡ Quick Scenarios (1-Click Demo)</div>",
        unsafe_allow_html=True,
    )
    chip_cols = st.columns(len(QUICK_CHIPS))
    for col, (label, prompt) in zip(chip_cols, QUICK_CHIPS):
        if col.button(label, key=f"chip_{label}", use_container_width=True):
            ss.pending = prompt
            st.rerun()

    error = None
    if ss.pending:
        text, ss.pending = ss.pending, None
        try:
            turn = A.handle_message(store, text, ss.conv_id, ss.customer_id, ss.channel, use_llm=use_llm)
            ss.conv_id = turn["conversation_id"]
            if turn["conversation"] and turn["conversation"].get("customer_id") and not ss.customer_id:
                ss.customer_id = turn["conversation"]["customer_id"]
            turn.pop("conversation", None)
            ss.turns.append(dict(text=text, result=turn))
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
    if error:
        st.error(error)

    conv = store.get("conversations", ss.conv_id) if ss.conv_id else None
    last = ss.turns[-1]["result"] if ss.turns else None

    # Get customer info for display
    cust_record = store.get("customers", ss.customer_id) if ss.customer_id else None
    cust_name = cust_record.get("name", "Guest User") if cust_record else "Guest User"
    cust_tier = (cust_record.get("tier", "Standard") + " Member") if cust_record else "Unauthenticated"
    cust_initial = cust_name[0].upper() if cust_name else "G"
    channel_name = A.CHANNELS.get(ss.channel, ss.channel)

    left, right = st.columns([1.18, 1.02], gap="large")

    with left:
        # Sleek Customer Session Header Card
        st.markdown(f"""
        <div style="display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; background: rgba(99, 102, 241, 0.06); border: 1px solid rgba(99, 102, 241, 0.18); border-radius: 12px; margin-bottom: 8px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 34px; height: 34px; border-radius: 50%; background: linear-gradient(135deg, #4f46e5, #06b6d4); display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: 14px; box-shadow: 0 2px 8px rgba(79, 70, 229, 0.3);">
                    {cust_initial}
                </div>
                <div>
                    <div style="font-weight: 700; font-size: 0.9rem; line-height: 1.2;">{cust_name}</div>
                    <div style="font-size: 0.74rem; opacity: 0.7;">{cust_tier} · {channel_name}</div>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 6px;">
                <span class="sp-status-pulse"></span>
                <span style="font-size: 0.75rem; font-weight: 700; color: #10b981; letter-spacing: 0.02em;">AGENT READY</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        box = st.container(height=580, border=True)
        with box:
            msgs = (conv or {}).get("messages", [])
            if not msgs:
                st.markdown("""
                <div style="padding: 2.5rem 1rem; text-align: center; opacity: 0.75;">
                    <div style="font-size: 36px; margin-bottom: 8px;">💬</div>
                    <div style="font-weight: 700; font-size: 1rem; margin-bottom: 4px;">Welcome to SupportPilot Desk</div>
                    <div style="font-size: 0.85rem; max-width: 360px; margin: 0 auto; opacity: 0.8;">
                        Click one of the quick scenario pills above or type a message below to test autonomous issue resolution.
                    </div>
                </div>
                """, unsafe_allow_html=True)

            for m in msgs:
                with st.chat_message(
                    "user" if m["role"] == "user" else "assistant",
                    avatar=":material/person:" if m["role"] == "user" else ":material/support_agent:",
                ):
                    st.markdown(m["text"])
                    meta = m.get("meta") or {}
                    if m["role"] == "assistant" and meta.get("ticket_id"):
                        st.markdown(f"""
                        <div style="margin-top: 6px; display: inline-flex; align-items: center; gap: 6px; padding: 2px 8px; border-radius: 6px; font-size: 0.75rem; background: rgba(99, 102, 241, 0.12); color: #818cf8; font-weight: 600;">
                            <span>🎫 Ticket: {meta['ticket_id']}</span>
                            <span>·</span>
                            <span>{meta.get('decision', 'Resolved')}</span>
                        </div>
                        """, unsafe_allow_html=True)

        if conv and conv.get("awaiting") == "csat":
            k = f"fb_{conv['id']}_{len(conv['messages'])}"
            st.caption("⭐ Rate your experience with SupportPilot AI:")
            st.feedback("stars", key=k, on_change=_on_rating, args=(k,))

        st.chat_input("Type your message to SupportPilot…", key="chat_box", on_submit=_on_submit)
        if conv:
            where("support", f"conversations / {conv['id']}", store)

    with right:
        if not last:
            st.markdown("""
            <div style="border: 2px dashed rgba(99, 102, 241, 0.25); border-radius: 16px; padding: 3.5rem 1.5rem; text-align: center; background: rgba(99, 102, 241, 0.02); height: 630px; display: flex; flex-direction: column; justify-content: center; align-items: center;">
                <div style="font-size: 48px; margin-bottom: 14px;">🧭</div>
                <h3 style="margin: 0; font-weight: 800; letter-spacing: -0.02em;">Agent Execution Intelligence</h3>
                <p style="opacity: 0.7; font-size: 0.88rem; max-width: 400px; margin: 10px auto 22px auto; line-height: 1.55;">
                    Every customer turn runs through an orchestrated pipeline of specialized AI agents. Their reasoning, database lookups, policy decisions, and automated actions will be visualized right here.
                </p>
                <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 8px; max-width: 400px;">
                    <span class="sp-pill-tag" style="background: rgba(99, 102, 241, 0.1); color: #818cf8;">🧠 Intent Classifier</span>
                    <span class="sp-pill-tag" style="background: rgba(14, 165, 233, 0.1); color: #38bdf8;">👤 Context Gatherer</span>
                    <span class="sp-pill-tag" style="background: rgba(16, 185, 129, 0.1); color: #34d399;">📚 Knowledge Matcher</span>
                    <span class="sp-pill-tag" style="background: rgba(245, 158, 11, 0.1); color: #fbbf24;">⚡ Policy Engine</span>
                    <span class="sp-pill-tag" style="background: rgba(239, 68, 68, 0.1); color: #f87171;">🛡️ Safety Reviewer</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            return

        render_flow(ss.turns[-1]["text"], last, theme=theme(), height=700, store=store)

        with st.expander("Where this answer came from", icon=":material/source:", expanded=True):
            _sources(store, last)

        with st.expander("Decision details", icon=":material/rule:"):
            u, d = last.get("understanding") or {}, last.get("decision")
            if u:
                st.markdown(f"**Understood:** {u.get('label', u.get('intent'))} · priority {u.get('priority')} · "
                            f"{u.get('emotion')} · confidence {u.get('confidence', 0):.0%} · read by {u.get('source', 'rules')}")
            if last.get("investigation"):
                step_lines(last["investigation"]["steps"])
                st.markdown(f"**Diagnosis:** {last['investigation']['diagnosis']}")
            if isinstance(d, dict):
                st.markdown(f"**Decision:** {d['decision']} — confidence {d['confidence']:.0%} vs threshold {d['threshold']:.0%}")
                for r in d.get("reasons", []):
                    st.caption("• " + r)
            if last.get("review"):
                st.caption("Reviewer: " + " · ".join(f"{'✅' if c['passed'] else '❌'} {c['check']}" for c in last["review"]["checks"]))
            if last.get("ticket"):
                st.markdown(A.render_ticket(store.get("tickets", last["ticket"]["id"]) or last["ticket"]))


TG_SETUP = """
**Connect a Telegram bot:** create one with **@BotFather** (`/newbot`), put the token in `.env` or Streamlit secrets as
`TELEGRAM_BOT_TOKEN`, and restart the app. Customers then chat with SupportPilot from the Telegram app.
"""


def _telegram(store, bot):
    @st.fragment(run_every="3s")
    def live():
        if not bot:
            st.info("No Telegram bot connected.", icon=":material/link_off:")
            st.markdown(TG_SETUP)
            return
        status = store.get("meta", "telegram") or {}
        user = status.get("username") or bot.username
        with st.container(horizontal=True, vertical_alignment="center"):
            if status.get("running") and user:
                st.badge(f"Connected · @{user}", icon=":material/check_circle:", color="green")
                st.link_button("Open bot in Telegram", f"https://t.me/{user}", icon=":material/open_in_new:")
            else:
                st.badge("Connecting…" if not status.get("error") else "Not connected", color="orange")
            if status.get("last_poll"):
                st.caption(f"Last checked {fmt_ts(status['last_poll'])}")
        if status.get("error"):
            st.caption(f"⚠️ Last error: {status['error']}")
        chats = sorted(store.list("telegram_chats"), key=lambda c: c.get("updated_at", ""), reverse=True)
        if not chats:
            st.info(f"Open t.me/{user or 'your_bot'}, press Start and describe an issue — it appears here live.",
                    icon=":material/smartphone:")
            return

        def label(c):
            who = (store.get("customers", c["customer_id"]) or {}).get("name") if c.get("customer_id") else "guest"
            return f"{c.get('first_name', 'Telegram user')} (as {who})"

        left, right = st.columns([1, 1.15], gap="large")
        with left:
            chat = st.selectbox("Telegram chat", chats, format_func=label)
            conv = store.get("conversations", chat["conv_id"]) if chat.get("conv_id") else None
            with st.container(height=560, border=True):
                for m in (conv or {}).get("messages", []):
                    with st.chat_message("user" if m["role"] == "user" else "assistant",
                                         avatar=":material/smartphone:" if m["role"] == "user" else ":material/support_agent:"):
                        st.markdown(m["text"])
            where("support", "telegram_chats, conversations", store)
        with right:
            turns = sorted(store.list("telegram_turns", chat_id=chat["chat_id"]), key=lambda t: t["seq"])
            if turns:
                turn = st.selectbox("Message", turns[::-1], format_func=lambda t: f"{fmt_ts(t['ts'])} · {t['text'][:60]}")
                render_flow(turn["text"], turn["result"], theme=theme(), height=760, store=store, ts=turn["ts"])
    live()


def page():
    store = workspace()
    render_top_bar(store, "Live Support Desk")
    use_llm = st.session_state.get("use_llm", A.llm_enabled())
    web, tg = st.tabs([":material/forum: Web Chat Interface", ":material/send: Telegram Live Channel"])
    with web:
        _chat(store, use_llm)
    with tg:
        _telegram(store, st.session_state.get("_tg_bot"))
