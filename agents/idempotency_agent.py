"""Agent: Idempotency & Duplicate Request Guard.

Detects when a customer submits the exact same query or an issue for an order
that has already been processed. Prevents duplicate ticket creation and duplicate
actions (refunds, replacements, etc.), and informs the customer of the existing ticket.
"""
from __future__ import annotations

import re


def _normalize_text(text: str) -> str:
    """Normalize text for fuzzy duplicate matching."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return " ".join(text.split())


def find_processed_ticket(store, customer_id, order_id=None, intent=None, service_id=None):
    """Check if an order_id or service_id has already been processed under an existing ticket."""
    if not customer_id:
        return None

    # Retrieve all tickets for this customer, newest first
    tickets = sorted(
        store.list("tickets", customer_id=customer_id),
        key=lambda t: t.get("created_at", ""),
        reverse=True,
    )

    for t in tickets:
        t_slots = t.get("slots") or {}
        t_meta = t.get("meta") or {}
        t_order_id = t_slots.get("order_id") or t_meta.get("order_id")
        t_intent = t.get("intent")

        # 1. Direct Order ID match
        if order_id:
            matches_order = (
                t_order_id == order_id
                or order_id in t.get("title", "")
                or order_id in (t.get("description") or "")
            )
            if matches_order:
                # Same order and same issue intent
                if not intent or intent == t_intent:
                    return t

        # 2. Service ID match (e.g. broadband)
        if service_id:
            matches_service = (
                t_slots.get("service_id") == service_id
                or service_id in t.get("title", "")
            )
            if matches_service:
                if not intent or intent == t_intent:
                    return t

    return None


def check_duplicate(store, ctx, issue, text, investigation):
    """Evaluates whether the incoming query is an idempotent duplicate.

    Returns:
        dict: {
            "is_duplicate": bool,
            "order_id": str | None,
            "ticket": dict | None,
            "ticket_id": str | None,
            "status": str | None,
            "team": str | None,
            "resolution_note": str | None,
        }
    """
    if not ctx or not issue:
        return {"is_duplicate": False}

    cid = ctx.get("customer_id")
    intent = issue.get("intent")
    slots = dict(issue.get("slots") or {})
    facts = dict((investigation or {}).get("facts") or {})

    # Extract order_id from slots, facts, or investigation steps
    order_id = slots.get("order_id") or facts.get("order_id")
    service_id = slots.get("service_id") or facts.get("service_id")

    # If missing from slots, check if explicitly mentioned in user text
    if not order_id and text:
        m = re.search(r"\b(ORD\d{4,8})\b", text, re.IGNORECASE)
        if m:
            order_id = m.group(1).upper()

    # Search for an existing ticket that already processed this order/intent
    existing = find_processed_ticket(store, cid, order_id=order_id, intent=intent, service_id=service_id)

    # Also check if within the active conversation, this exact issue already generated a ticket
    if not existing and issue.get("ticket_id"):
        t = store.get("tickets", issue["ticket_id"])
        if t:
            existing = t

    # Also check if exact text matches previous user messages in recent tickets
    if not existing and cid and text:
        norm_current = _normalize_text(text)
        recent_tickets = sorted(
            store.list("tickets", customer_id=cid),
            key=lambda x: x.get("created_at", ""),
            reverse=True,
        )[:5]
        for t in recent_tickets:
            t_desc = _normalize_text(t.get("description") or "")
            if t_desc and (norm_current == t_desc or (len(norm_current) > 20 and norm_current in t_desc)):
                if t.get("intent") == intent:
                    existing = t
                    if not order_id:
                        order_id = t.get("slots", {}).get("order_id")
                    break

    if not existing:
        return {"is_duplicate": False}

    status = existing.get("status", "Opened")
    tid = existing.get("id")
    target_oid = order_id or existing.get("slots", {}).get("order_id") or "your order"

    # Gather prior actions/resolution details to inform the customer
    actions_taken = existing.get("actions_taken") or []
    diagnosis = existing.get("diagnosis") or existing.get("resolution") or ""
    res_details = ""
    if actions_taken:
        clean_actions = [a.split("—")[0].strip() for a in actions_taken if "notify" not in a.lower()]
        if clean_actions:
            res_details = f"Previous action taken: {', '.join(clean_actions)}."
    elif diagnosis:
        res_details = f"Previous resolution: {diagnosis}."

    return {
        "is_duplicate": True,
        "order_id": target_oid,
        "ticket": existing,
        "ticket_id": tid,
        "status": status,
        "team": existing.get("team", "Support"),
        "resolution_note": res_details,
    }
