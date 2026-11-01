"""Policy Change Impact Graph helpers.

Reuse diff_two_pdfs output. Classify changes with conservative keyword heuristics.
No fabricated data; empty inputs yield empty results.
"""
import re

CATEGORIES = [
    "Eligibility criteria changed",
    "Benefits or financial assistance changed",
    "Application procedures changed",
    "Deadlines or implementation dates changed",
    "Responsible departments or authorities changed",
    "New provision introduced",
    "Existing provision removed",
    "Wording changed without clearly established substantive impact",
]


def classify_change(change):
    """Return a category string for a diff change dict."""
    ctype = change.get("type", "")
    old = " ".join(change.get("old", []))
    new = " ".join(change.get("new", []))
    text = (old + " " + new).lower()

    if ctype == "insert":
        return "New provision introduced"
    if ctype == "delete":
        return "Existing provision removed"

    if any(k in text for k in ["eligible", "eligibility", "who can", "qualify"]):
        return "Eligibility criteria changed"
    if any(k in text for k in ["benefit", "amount", "financial", "assistance", "grant", "subsidy"]):
        return "Benefits or financial assistance changed"
    if any(k in text for k in ["apply", "application", "procedure", "process", "submit"]):
        return "Application procedures changed"
    if any(k in text for k in ["deadline", "date", "effective", "implementation", "within"]):
        return "Deadlines or implementation dates changed"
    if any(k in text for k in ["department", "authority", "ministry", "office"]):
        return "Responsible departments or authorities changed"
    return "Wording changed without clearly established substantive impact"


def build_impact_table(changes):
    rows = []
    for c in changes or []:
        old_text = " ".join(c.get("old", []))
        new_text = " ".join(c.get("new", []))
        if not old_text and not new_text:
            continue
        rows.append({
            "type": c.get("type", ""),
            "category": classify_change(c),
            "previous": old_text,
            "new": new_text,
        })
    return rows


def build_graph(rows):
    """Build a networkx DiGraph of provision->change->affected group->impact (potential)."""
    try:
        import networkx as nx
    except ImportError:
        return None
    g = nx.DiGraph()
    for i, r in enumerate(rows):
        provision = f"Provision {i+1}"
        change_node = f"Change {i+1}: {r['category']}"
        g.add_node(provision, type="provision")
        g.add_node(change_node, type="change")
        g.add_edge(provision, change_node, relation="changed")
        # potential affected group is inferred generically; label as potential
        affected = "Potentially affected group"
        impact = "Potential impact (not established fact)"
        g.add_node(affected, type="affected_group")
        g.add_node(impact, type="potential_impact")
        g.add_edge(change_node, affected, relation="may affect")
        g.add_edge(affected, impact, relation="potential consequence")
    return g