"""
Transparency Framework Monitoring Dashboard
Pension Fund — Prototype v1.0
"""

import warnings
warnings.filterwarnings("ignore")

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
from io import BytesIO
from urllib.parse import quote

def _theme_qs():
    """Append &theme=<mode> so the user's theme survives drill-through URL navigation."""
    import streamlit as _st
    return f"&theme={_st.session_state.get('theme_mode', 'cream')}"

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Transparency Framework Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Constants ────────────────────────────────────────────────────────────────
TIER_COLORS = {"Green": "#27ae60", "Amber": "#e67e22", "Red": "#e74c3c"}
TIER_BG = {
    "Green": "background-color:#1a3d2b;color:#4cd484",
    "Amber": "background-color:#3d2a0a;color:#f0a030",
    "Red":   "background-color:#3d1212;color:#f06060",
}
# Cream-mode equivalents (light chip + dark tier text) — dataframes can't read
# CSS var(), so apply_tier_style() picks the palette based on the active theme.
TIER_BG_CREAM = {
    "Green": "background-color:#E6F4EA;color:#1E6F2F",
    "Amber": "background-color:#FFF4E0;color:#B26A0E",
    "Red":   "background-color:#FCE6E6;color:#9B2C2C",
}
# Theme palettes — dark (the original) and cream (FT-style salmon).
# Toggled via st.session_state["theme_mode"]. Helpers use CSS variables
# emitted by _render_theme_css(); plotly figures use LAYOUT()/LEGEND().
THEMES = {
    "dark": {
        # Slate-based palette. All foreground/background pairs verified WCAG AA.
        "bg-page":          "#0B1120",
        "bg-surface":       "#1E293B",
        "bg-track":         "#0F172A",
        "border-default":   "#334155",
        "border-strong":    "#475569",
        "text-primary":     "#F8FAFC",
        "text-soft":        "#E2E8F0",
        "text-muted":       "#CBD5E1",
        "text-subtle":      "#94A3B8",
        "accent":           "#60A5FA",
        "color-ok":         "#4ADE80",
        "color-alert":      "#FBBF24",
        "color-breach":     "#F87171",
        "color-bar-neutral":"#60A5FA",
        "color-amber-fill": "#FBBF24",
        "color-red-fill":   "#F87171",
        "alert-border":     "#F59E0B",
        "breach-border":    "#B91C1C",
        "ok-border":        "#15803D",
        "limit-tick":       "#F8FAFC",
        "investigate-bg":   "#7F1D1D",
        "investigate-text": "#FECACA",
        "alert-text":       "#FBBF24",
        "breach-text":      "#F87171",
        "ok-text":          "#4ADE80",
        "amber-tier":       "#FBBF24",
        "red-tier":         "#F87171",
        "plotly-paper":     "#1E293B",
        "plotly-plot":      "#1E293B",
        "plotly-font":      "#F8FAFC",
        "plotly-grid":      "#334155",
        "plotly-line":      "#475569",
        "plotly-legend-bg": "#0B1120",
        "section-band":     "#60A5FA",
        # ── Pass 29 (Phase A): semantic tokens so every component reads
        # theme-aware colours instead of hardcoded cream pastels.
        # Status pills (Recommended Action Plan / In Progress / Completed).
        "status-rec-fg":      "#FBBF24",
        "status-rec-bg":      "rgba(251,191,36,0.14)",
        "status-rec-border":  "rgba(251,191,36,0.40)",
        "status-prog-fg":     "#60A5FA",
        "status-prog-bg":     "rgba(96,165,250,0.16)",
        "status-prog-border": "rgba(96,165,250,0.40)",
        "status-done-fg":     "#4ADE80",
        "status-done-bg":     "rgba(74,222,128,0.14)",
        "status-done-border": "rgba(74,222,128,0.40)",
        # Soft tier tints (cockpit BREACH/ALERT/OK card backgrounds).
        # Pass 29.1: softer dark-mode tints — the original deep-red #3D1212
        # was overpowering when used as a full card background. The new
        # values keep the tier hue but sit closer to bg-surface (#1E293B)
        # so the bright tier border carries the BREACH signal.
        "tint-breach-bg":     "#2A1A1C",
        "tint-alert-bg":      "#2A2418",
        "tint-ok-bg":         "#1A2A22",
        # Gauge bar inside popup card.
        "gauge-ok-fill":      "#1A3D2B",
        "gauge-alert-fill":   "#3D2A0A",
        "gauge-indicator":    "#F8FAFC",
        "gauge-indicator-halo": "#0B1120",
        # Plotly tier ramp + marker outlines.
        "plotly-marker-border": "#0B1120",
        "tier-red-bright":      "#F87171",
        "tier-amber-bright":    "#FBBF24",
        "tier-amber-soft":      "#F59E0B",
        "tier-green-bright":    "#4ADE80",
        "plotly-hline":         "#94A3B8",
        # Strategic Focus chip palette (missing-fields).
        "chip-violet-bg":     "#A78BFA",
        "chip-teal-fg":       "#5EEAD4",
        "chip-teal-bg":       "rgba(94,234,212,0.15)",
        "chip-teal-border":   "#2DD4BF",
        # Soft accent tint for callout backgrounds (Top opportunity,
        # Integration note, primary-button glow).
        "accent-tint-bg":     "rgba(96,165,250,0.14)",
        "accent-shadow":      "rgba(96,165,250,0.28)",
        # Modal backdrop opacity (dialog popup) — heavier in dark mode so
        # the card visibly floats over the dim dashboard.
        "modal-backdrop":     "rgba(0,0,0,0.50)",
    },
    "cream": {
        # White/slate palette. Semantic ramp; all pairs verified WCAG AA.
        "bg-page":          "#FFFFFF",
        "bg-surface":       "#FFFFFF",
        "bg-track":         "#F1F5F9",
        "border-default":   "#E2E8F0",
        "border-strong":    "#CBD5E1",
        "text-primary":     "#0F172A",
        "text-soft":        "#334155",
        "text-muted":       "#475569",
        "text-subtle":      "#64748B",
        "accent":           "#1D4ED8",
        "color-ok":         "#15803D",
        "color-alert":      "#B45309",
        "color-breach":     "#B91C1C",
        "color-bar-neutral":"#1D4ED8",
        "color-amber-fill": "#B45309",
        "color-red-fill":   "#B91C1C",
        "alert-border":     "#EA580C",
        "breach-border":    "#B91C1C",
        "ok-border":        "#15803D",
        "limit-tick":       "#0F172A",
        "investigate-bg":   "#FEE2E2",
        "investigate-text": "#B91C1C",
        "alert-text":       "#B45309",
        "breach-text":      "#B91C1C",
        "ok-text":          "#15803D",
        "amber-tier":       "#B45309",
        "red-tier":         "#B91C1C",
        "plotly-paper":     "#FFFFFF",
        "plotly-plot":      "#FFFFFF",
        "plotly-font":      "#0F172A",
        "plotly-grid":      "#E2E8F0",
        "plotly-line":      "#CBD5E1",
        "plotly-legend-bg": "#FFFFFF",
        "section-band":     "#1D4ED8",
        # ── Pass 29 (Phase A): semantic tokens — cream palette equivalents.
        # Status pills (Recommended Action Plan / In Progress / Completed).
        "status-rec-fg":      "#B45309",
        "status-rec-bg":      "rgba(180,83,9,0.08)",
        "status-rec-border":  "rgba(180,83,9,0.30)",
        "status-prog-fg":     "#0E5A8A",
        "status-prog-bg":     "rgba(14,90,138,0.10)",
        "status-prog-border": "rgba(14,90,138,0.30)",
        "status-done-fg":     "#15803D",
        "status-done-bg":     "rgba(21,128,61,0.10)",
        "status-done-border": "rgba(21,128,61,0.30)",
        # Soft tier tints (cockpit BREACH/ALERT/OK card backgrounds).
        "tint-breach-bg":     "#FEF2F2",
        "tint-alert-bg":      "#FFFBEB",
        "tint-ok-bg":         "#F0FDF4",
        # Gauge bar inside popup card.
        "gauge-ok-fill":      "#DCFCE7",
        "gauge-alert-fill":   "#FEF3C7",
        "gauge-indicator":    "#0F172A",
        "gauge-indicator-halo": "#FFFFFF",
        # Plotly tier ramp + marker outlines.
        "plotly-marker-border": "#FFFFFF",
        "tier-red-bright":      "#e74c3c",
        "tier-amber-bright":    "#e67e22",
        "tier-amber-soft":      "#f59e0b",
        "tier-green-bright":    "#27ae60",
        "plotly-hline":         "#94A3B8",
        # Strategic Focus chip palette (missing-fields).
        "chip-violet-bg":     "#7C3AED",
        "chip-teal-fg":       "#0F766E",
        "chip-teal-bg":       "rgba(13,148,136,0.10)",
        "chip-teal-border":   "#0D9488",
        # Soft accent tint for callout backgrounds.
        "accent-tint-bg":     "rgba(29,78,216,0.08)",
        "accent-shadow":      "rgba(29,78,216,0.18)",
        # Modal backdrop — fully transparent in cream so the dashboard is
        # plainly visible behind the popup. The dialog card has its own
        # border + drop shadow (from the stDialog rules) which gives it
        # enough visual definition without any backdrop dimming.
        "modal-backdrop":     "transparent",
    },
}

def _theme():
    """Active theme dict — defaults to dark."""
    import streamlit as _st
    return THEMES.get(_st.session_state.get("theme_mode", "dark"), THEMES["dark"])

def LAYOUT():
    """Theme-aware Plotly layout. Every text element gets its colour set
    EXPLICITLY so Plotly's auto-defaults can't paint things grey when the user
    flips theme. Pass 8: tabular numerics on axes use JetBrains Mono for
    alignment; labels/legend use Inter."""
    t = _theme()
    font_color  = t["plotly-font"]
    font_family = "Inter, Segoe UI, Helvetica Neue, system-ui, sans-serif"
    mono_family = "JetBrains Mono, SF Mono, Menlo, monospace"
    base_font   = dict(color=font_color, size=13, family=font_family)
    tick_font   = dict(color=font_color, size=12, family=mono_family)   # tabular numerics
    title_font  = dict(color=font_color, size=13, family=font_family)
    return dict(
        paper_bgcolor=t["plotly-paper"],
        plot_bgcolor=t["plotly-plot"],
        font=base_font,
        # NB: no `title=` here — Plotly renders "undefined" when title.text is unset
        xaxis=dict(
            gridcolor=t["plotly-grid"], linecolor=t["plotly-line"], zerolinecolor=t["plotly-grid"],
            tickfont=tick_font, title=dict(font=title_font),
            color=font_color,
        ),
        yaxis=dict(
            gridcolor=t["plotly-grid"], linecolor=t["plotly-line"], zerolinecolor=t["plotly-grid"],
            tickfont=tick_font, title=dict(font=title_font),
            color=font_color,
        ),
        # NB: NO legend= key on purpose — call sites pass their own legend=dict(...)
        # with orientation/position, plus **DARK_LEGEND which already carries font + bg.
        hoverlabel=dict(font=dict(color=font_color, family=font_family),
                        bgcolor=t["plotly-paper"], bordercolor=t["plotly-grid"]),
        coloraxis=dict(colorbar=dict(tickfont=tick_font, title=dict(font=title_font))),
    )

def LEGEND():
    t = _theme()
    font_family = "Inter, Segoe UI, Helvetica Neue, system-ui, sans-serif"
    return dict(bgcolor=t["plotly-legend-bg"], bordercolor=t["plotly-grid"], borderwidth=1,
                font=dict(color=t["plotly-font"], size=12, family=font_family))

# Backwards-compat: existing call sites use DARK_LAYOUT / DARK_LEGEND as dicts.
# We expose theme-aware proxies via properties on a small class.
class _ThemedLayout(dict):
    def __getitem__(self, k):
        return LAYOUT()[k]
    def keys(self):     return LAYOUT().keys()
    def values(self):   return LAYOUT().values()
    def items(self):    return LAYOUT().items()
    def __iter__(self): return iter(LAYOUT())
    def __len__(self):  return len(LAYOUT())
class _ThemedLegend(dict):
    def __getitem__(self, k):
        return LEGEND()[k]
    def keys(self):     return LEGEND().keys()
    def values(self):   return LEGEND().values()
    def items(self):    return LEGEND().items()
    def __iter__(self): return iter(LEGEND())
    def __len__(self):  return len(LEGEND())
DARK_LAYOUT = _ThemedLayout()
DARK_LEGEND = _ThemedLegend()

# ─── Pass 15: framework-aligned data requirements ────────────────────────────
# Each instrument is classified into a *framework family* (per stakeholder's
# "Core and Important information" deck). Families define two layered field sets:
#   - amber: minimum data set; missing any → holding is Red
#   - green: extra data on top of Amber that elevates the holding to Green
# Critical Company Metrics are collapsed into a single "Critical Company Metric"
# requirement satisfied by ANY of EBITDA / Leverage / Cashflow Coverage.
FRAMEWORK_FAMILIES = {
    # ── Direct investment families ───────────────────────────────────────
    "Listed EQ": {
        "amber": ["Country", "Sector"],
        "green": ["Company Name", "MV", "Critical Company Metric"],
    },
    "Unlisted PE": {
        "amber": ["Country", "Sector", "Asset Type (VC/Buyout/Growth)"],
        "green": ["Company Name", "MV", "Critical Company Metric"],
    },
    "Unlisted Infra": {
        "amber": ["Country", "Sector", "Asset Type (Core/Core+)", "Development Status", "Direct Borrowing"],
        "green": ["Business Model", "Critical Company Metric"],
    },
    "Unlisted RE B&M": {
        "amber": ["Country", "Sector", "Development Status", "Direct Borrowing"],
        "green": ["General Location", "Critical Company Metric"],
    },
    "Credit Single-Asset (public-aligned)": {
        "amber": ["Country", "Sector", "Instrument Type", "OAS", "Spread Duration", "Duration"],
        "green": ["Credit Rating"],
    },
    "Credit Single-Asset (private-aligned)": {
        "amber": ["Country", "Sector", "Instrument Type", "Coupon", "Maturity"],
        "green": ["Credit Rating", "Fixed/Floating"],
    },
    "Structured Credit": {
        "amber": ["Country", "Sector", "Collateral Type", "Tranche", "OAS", "Spread Duration", "Duration"],
        "green": ["Credit Rating", "Attachment", "Detachment", "Credit Enhancement"],
    },
    "Fixed Income Instruments": {
        "amber": ["Country", "Sector", "Asset Type", "Underlying Asset Type", "Risk Sensitivities"],
        "green": ["Issuer Name", "MV", "Notional", "Option Type", "Strike", "Maturity",
                  "Underlying Ticker", "Critical Company Metric"],
    },
    # ── Fund / multiple-asset vehicle families ───────────────────────────
    "Macro Fund": {
        "amber": ["Country (weighted)", "Sector (weighted)", "Fund-Level KRD",
                  "Commodity Delta", "Fund-Level Credit Sector Mix"],
        "green": ["Instrument Name", "MV", "Critical Company Metric"],
    },
    "Equity Long-Only Fund": {
        "amber": ["Country (weighted)", "Sector (weighted)", "Asset Type Mix"],
        "green": ["Company Name", "MV", "Critical Company Metric"],
    },
    "PE Fund": {
        "amber": ["Country (weighted)", "Sector (weighted)", "Asset Type (VC/Buyout/Growth)",
                  "Fund-Level Leverage"],
        "green": ["Company Name", "MV", "Critical Company Metric"],
    },
    "Infra Fund": {
        "amber": ["Country (weighted)", "Sector (weighted)", "Asset Type (Core/Core+)",
                  "Development Status", "Fund-Level Leverage"],
        "green": ["Business Model", "Critical Company Metric"],
    },
    "RE B&M Fund": {
        "amber": ["Country (weighted)", "Sector (weighted)", "Asset Type (Listed/Unlisted)",
                  "Development Status"],
        "green": ["General Location", "Critical Company Metric"],
    },
    "Credit Fund (public-aligned)": {
        "amber": ["Country (weighted)", "Sector (weighted)", "Instrument Type",
                  "IG/HY/Distressed", "Fund-Level Leverage", "OAS", "Spread Duration", "Duration"],
        "green": ["Credit Rating"],
    },
    "Credit Fund (private-aligned)": {
        "amber": ["Country (weighted)", "Sector (weighted)", "Instrument Type",
                  "Fund-Level Leverage", "Coupon", "Maturity"],
        "green": ["Credit Rating", "Fixed/Floating"],
    },
    "Hedge Fund": {
        "amber": ["Country (weighted)", "Sector (weighted)", "Asset Type (EQ/Bonds/FX)",
                  "Hedge Fund Style", "Net & Gross Fund-Level Leverage"],
        "green": ["Instrument Type Mix"],
    },
    "Multi-Asset Fund": {
        "amber": ["Country (weighted)", "Sector (weighted)", "Instrument Type Mix",
                  "Fund-Level Leverage"],
        "green": ["Underlying Holdings"],
    },
}

# Strategy → framework family. Option B (instrument-type aware): the "fund"
# slot is used when the holding's instrument_type == "Fund Investment";
# otherwise the "direct" slot applies (Mandate, Direct Investment, Co-investment).
STRATEGY_FAMILY = {
    "EQ Developed Markets":  {"direct": "Listed EQ",                             "fund": "Equity Long-Only Fund"},
    "EQ Emerging Markets":   {"direct": "Listed EQ",                             "fund": "Equity Long-Only Fund"},
    "FI Active":             {"direct": "Fixed Income Instruments",              "fund": "Macro Fund"},
    "HY Credit":             {"direct": "Credit Single-Asset (public-aligned)",  "fund": "Credit Fund (public-aligned)"},
    "MAARS":                 {"direct": "Macro Fund",                            "fund": "Macro Fund"},
    "EILB":                  {"direct": "Equity Long-Only Fund",                 "fund": "Equity Long-Only Fund"},
    "MA":          {"direct": "Hedge Fund",                            "fund": "Hedge Fund"},
    "Hedge Fund 2":          {"direct": "Hedge Fund",                            "fund": "Hedge Fund"},
    "RE Bricks and Mortar":  {"direct": "Unlisted RE B&M",                       "fund": "RE B&M Fund"},
    "RE Debt":               {"direct": "Credit Single-Asset (private-aligned)", "fund": "Credit Fund (private-aligned)"},
    "PE Active":             {"direct": "Unlisted PE",                           "fund": "PE Fund"},
    "PE Secondaries":        {"direct": "Unlisted PE",                           "fund": "PE Fund"},
    "PE Mezz":               {"direct": "Credit Single-Asset (private-aligned)", "fund": "Credit Fund (private-aligned)"},
    "Infrastructure Active": {"direct": "Unlisted Infra",                        "fund": "Infra Fund"},
    "Infrastructure Debt":   {"direct": "Credit Single-Asset (private-aligned)", "fund": "Credit Fund (private-aligned)"},
    "Multi Asset1":          {"direct": "Multi-Asset Fund",                      "fund": "Multi-Asset Fund"},
}

def _pick_family(strategy_name, instrument_type):
    """Map (Strategy, instrument_type) → framework family. Option B: Fund
    Investments use the fund-equivalent family; everything else uses direct."""
    spec = STRATEGY_FAMILY.get(strategy_name)
    if not spec:
        return FRAMEWORK_FAMILIES["Listed EQ"]   # safest default
    family_name = spec["fund"] if instrument_type == "Fund Investment" else spec["direct"]
    return FRAMEWORK_FAMILIES.get(family_name, FRAMEWORK_FAMILIES["Listed EQ"])

def _gen_missing(strategy_name, instrument_type, tier, rng):
    """Generate (missing_fields_list, missing_tiers) for one synthetic holding.
    - Green tier: nothing missing
    - Amber tier: 1–2 fields drawn ONLY from the Green requirement pool
                  (Amber requirements are satisfied — that's what makes it Amber)
    - Red tier: 2–4 fields with at least 1 from Amber pool (that's what blocks it
                  from Amber tier) and the rest from either pool
    Returns the field list and a parallel tier list ("Amber" or "Green") so the
    chip display can colour-code which tier each missing field is blocking."""
    fam = _pick_family(strategy_name, instrument_type)
    amber_pool = list(fam["amber"])
    green_pool = list(fam["green"])
    if tier == "Green":
        return [], []
    if tier == "Amber":
        # All Amber requirements satisfied; only Green fields can be missing
        n = min(rng.randint(1, 2), len(green_pool))
        miss = rng.sample(green_pool, n) if n > 0 else []
        tiers = ["Green"] * len(miss)
        return miss, tiers
    # Red: at least one Amber-blocker
    n_amber = min(rng.randint(1, 2), len(amber_pool))
    miss_amber = rng.sample(amber_pool, n_amber) if n_amber > 0 else []
    remaining_total = rng.randint(2, 4) - n_amber
    if remaining_total > 0:
        rest_pool = [f for f in green_pool if f not in miss_amber]
        n_green = min(remaining_total, len(rest_pool))
        miss_green = rng.sample(rest_pool, n_green) if n_green > 0 else []
    else:
        miss_green = []
    return (miss_amber + miss_green,
            ["Amber"] * len(miss_amber) + ["Green"] * len(miss_green))

# Pass 15: effort tag per field name. The legacy pool's specific names are gone;
# default to "Medium" for anything not in the explicit overrides. Sort order of
# Strategic Focus's quick-wins still works because every field gets some weight.
_FIELD_EFFORT_DEFAULT = "Medium"
_FIELD_EFFORT = {
    # Low effort — data usually exists internally, just needs ingestion
    "Country": "Low", "Sector": "Low", "Country (weighted)": "Low", "Sector (weighted)": "Low",
    "MV": "Low", "Asset Type": "Low", "Instrument Type": "Low", "Coupon": "Low",
    "Maturity": "Low", "Critical Company Metric": "Low", "Fixed/Floating": "Low",
    "Tranche": "Low", "Hedge Fund Style": "Low",
    # High effort — requires GP cooperation, side-letters, or new agreements
    "Underlying Asset Type": "High", "Risk Sensitivities": "High", "Underlying Ticker": "High",
    "Business Model": "High", "Attachment": "High", "Detachment": "High", "Credit Enhancement": "High",
    "Development Status": "High", "Direct Borrowing": "High",
    "Fund-Level Leverage": "High", "Fund-Level KRD": "High", "Fund-Level Credit Sector Mix": "High",
    "Net & Gross Fund-Level Leverage": "High", "Asset Type Mix": "High", "Underlying Holdings": "High",
    "Instrument Type Mix": "High",
}

# Pass 14: action owners are now TEAMS, not specific named people. Mapping kept
# for the Strategy Detail Action Plans "Group by Owner" cut where the owner is
# resolved per-strategy (each Strategy Group has a default operations team).
OWNERS_BY_STRAT = {
    "EQ Active":          "Strategy Ops – Public Equities",
    "Fixed Income":       "Strategy Ops – Fixed Income",
    "Hedge Fund":         "Strategy Ops – Hedge Funds",
    "Real Estate":        "Strategy Ops – Real Estate",
    "Private Equities":   "Strategy Ops – Private Equity",
    "Infrastructure":     "Strategy Ops – Infrastructure",
    "Multi-Asset":        "Strategy Ops",
}

# Pass 14: Action Tracker templates moved to module scope (was duplicated inside
# _build_synthetic_action_items and inline in generate_all_data). Each row now
# carries: title, breach reason, status, days_offset, last_update_note,
# owner_team (CISD / Deal Team & Legal / Strategy Ops), impact_pp.
# Owner is chosen by the *type of work*, not the strategy group — tech actions
# go to CISD, contract/disclosure to Deal Team & Legal, operational to Strat Ops.
ACTION_TEMPLATES = [
    # title, reason, status, days, note, owner_team, impact_pp
    ("Renegotiate ABC Capital data feed terms",      "Third-party data agreement",     "Planned",     45,  "Vendor contract review in legal queue.",        "Deal Team & Legal", 2.5),
    ("Quarterly look-through pack for {strat}",      "Look-through limitations",       "In Progress", 21,  "Draft template received; awaiting GP sign-off.","Strategy Ops",      1.8),
    ("Standardised reporting template rollout",      "GP reporting cycle (quarterly)", "In Progress", 14,  "3 of 7 managers onboarded; targeting Q-end.",   "Strategy Ops",      1.5),
    ("Backfill missing LTV + DSCR fields ({strat})", "Data availability gap",          "In Progress", 7,   "Risk team running cross-check on legacy book.", "Strategy Ops",      1.2),
    ("Monthly NAV reconciliation workflow",          "GP reporting cycle (quarterly)", "Done",        60,  "Live for 4 strategies; doc on wiki.",           "Strategy Ops",      2.0),
    ("Position-level disclosure ask ({strat})",      "Look-through limitations",       "Planned",     90,  "Pending side-letter discussion.",               "Deal Team & Legal", 2.8),
    ("Automated tier classifier pipeline",           "Data availability gap",          "Done",        30,  "Cron job live; pushes daily to dashboard.",     "CISD",              1.0),
    ("Look-through agreement renewal — {strat}",     "Third-party data agreement",     "Planned",     120, "Renewal window opens next quarter.",            "Deal Team & Legal", 2.2),
    ("Onboarding workflow for new Infra managers",   "Manager onboarding",             "In Progress", 30,  "Onboarding kit drafted; 2 managers in pipeline.","Strategy Ops",     1.4),
    ("T+5 NAV cutoff for {strat}",                   "GP reporting cycle (quarterly)", "Planned",     45,  "GP committed in writing; ops change in flight.","Strategy Ops",      1.6),
    ("Sourcing rationale capture in IC memo",        "Best-sourcing rationale",        "Done",        45,  "Template merged into IC memo as of last quarter.","Deal Team & Legal",0.8),
    ("Look-through API integration ({strat})",       "Look-through limitations",       "In Progress", 14,  "Sandbox env tested; production cutover in 2 wks.","CISD",             3.2),
    ("GP reporting frequency upgrade — {strat}",     "GP reporting cycle (quarterly)", "Planned",     60,  "Awaiting GP capacity confirmation.",            "Strategy Ops",      2.4),
    ("Data warehouse refresh cadence",               "Data availability gap",          "Done",        90,  "Cadence improved from weekly to daily.",        "CISD",              1.1),
    ("Manual data load deprecation",                 "Data availability gap",          "Planned",     30,  "Migration plan in design review.",              "CISD",              0.9),
]

# Pass 14: per-instrument suggested-action pool. Keyed by breach_reason category
# so the Action column in the Instrument list reads like a real punch list
# (varies across rows) instead of "Awaiting next Q-end NAV" on every row.
SUGGESTED_ACTION_POOL = {
    "Third-party data agreement":     ["Renegotiate data feed terms", "Engage Deal Team for contract review", "Pursue side-letter amendment"],
    "GP reporting cycle (quarterly)": ["Awaiting next Q-end NAV", "Work with manager to get the data", "Validate prior-Q NAV; flag if lagged"],
    "Manager onboarding":             ["Complete onboarding workflow", "Push manager to finalise SLA", "Resume onboarding next quarter"],
    "Look-through limitations":       ["Engage manager for look-through", "Escalate look-through ask to GP", "Pursue position-level disclosure"],
    "Data availability gap":          ["Backfill missing fields", "Cross-check with risk team", "Auto-pull via new API integration"],
    "Best-sourcing rationale":        ["Capture rationale in IC memo", "Update sourcing notes", "Document GP-level constraint"],
}
REGIONS          = ["Europe", "North America", "Asia Pacific", "EM", "Global"]
SECTORS          = ["Technology", "Healthcare", "Financials", "Real Estate",
                    "Energy", "Industrials", "Consumer", "Infrastructure"]
SUB_ASSET_CLASSES = {
    "Private Equity":  ["Buyout", "Growth", "Venture", "Secondaries"],
    "Infrastructure":  ["Core", "Core Plus", "Value-Add", "Greenfield"],
    "Real Estate":     ["Core", "Core Plus", "Value-Add", "Opportunistic"],
    "Private Credit":  ["Senior Secured", "Unitranche", "Mezzanine", "Distressed"],
    "Hedge Funds":     ["Long/Short Equity", "Global Macro", "Event Driven", "Relative Value"],
    "Co-investments":  ["Direct Co-invest", "Syndicated", "Club Deal"],
    "Public Equity":   ["Large Cap", "SMID Cap", "EM Equity", "Factor"],
    "Fixed Income":    ["Investment Grade", "High Yield", "EM Debt", "Sovereign"],
}

# ─── Custom CSS ───────────────────────────────────────────────────────────────
def _render_theme_css():
    """Inject CSS variables and theme-aware Streamlit chrome rules. Called
    once early in main(). Helpers reference var(--name) so a session_state
    flip re-skins the whole dashboard without restarting."""
    t = _theme()
    vars_block = "\n".join(f"  --{k}: {v};" for k, v in t.items())
    is_cream = st.session_state.get("theme_mode", "dark") == "cream"
    hover_card = "#EAF2FB" if is_cream else "#293251"
    hover_card_border = t["border-strong"]
    investigate_hover_bg = "#F5C1C1" if is_cream else "#992525"
    # Pass 29.18: dialog CSS now applies in BOTH cream and dark modes. Streamlit
    # Cloud was ignoring config.toml's `base = "light"` for the dialog element
    # and rendering it dark even in cream mode. Forcing var(--bg-surface) etc.
    # gives the modal the right colours regardless of what Cloud's default
    # would have been. Backdrop opacity is theme-aware: transparent in cream
    # (so the dashboard stays visible) and ~50% black in dark (so the modal
    # visibly floats).
    _backdrop = "transparent" if is_cream else "rgba(0,0,0,0.50)"
    dialog_css = f"""
/* === Modal dialog chrome — both themes (Pass 29.18) === */
[data-baseweb="modal"] {{ background: transparent !important; }}
[data-baseweb="modal-backdrop"] {{ background: {_backdrop} !important; }}
div[role="dialog"], [data-testid="stDialog"] {{
  background-color: var(--bg-surface) !important;
  color: var(--text-primary) !important;
  border: 1px solid var(--border-strong) !important;
  border-radius: 10px !important;
  box-shadow: 0 12px 36px rgba(0,0,0,0.30) !important;
}}
div[role="dialog"] h1, div[role="dialog"] h2, div[role="dialog"] h3,
[data-testid="stDialog"] h1, [data-testid="stDialog"] h2, [data-testid="stDialog"] h3
  {{ color: var(--text-primary) !important; }}
div[role="dialog"] [data-testid="stMarkdownContainer"],
[data-testid="stDialog"] [data-testid="stMarkdownContainer"]
  {{ color: var(--text-primary); }}
div[role="dialog"] [data-testid="baseButton-headerNoPadding"],
div[role="dialog"] button[kind="headerNoPadding"]
  {{ color: var(--text-soft) !important; }}
div[role="dialog"] [data-testid="baseButton-headerNoPadding"]:hover
  {{ color: var(--text-primary) !important; }}
"""
    investigate_hover_text = t["color-breach"] if is_cream else "#FFD5D5"
    css = f"""
<style>
:root {{
{vars_block}
}}
html, body, [data-testid=\"stAppViewContainer\"] {{ background-color: var(--bg-page); color: var(--text-primary); }}
[data-testid=\"stSidebar\"] {{ background-color: var(--bg-surface) !important; border-right:1px solid var(--border-default); }}
[data-testid=\"stSidebar\"] * {{ color: var(--text-soft) !important; }}
[data-testid=\"stSidebar\"] hr {{ border-color: var(--border-default); }}
[data-testid=\"stMetricValue\"]  {{ font-size:1.4rem !important; color: var(--text-primary) !important; }}
[data-testid=\"stMetricLabel\"]  {{ color: var(--text-muted) !important; }}
[data-testid=\"stMetricDelta\"]  {{ font-size:0.8rem !important; }}
@import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap");
html, body, .stApp, [class*="css-"], [data-testid="stAppViewContainer"], [data-testid="stMarkdownContainer"] {{ font-family: "Inter", "Segoe UI", "Helvetica Neue", system-ui, -apple-system, sans-serif !important; font-feature-settings: "cv02","cv03","cv04","cv11"; -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; }}
body, .stApp {{ font-size: 15px !important; line-height: 1.55; }}
h1 {{ font-size: 2.25rem !important; font-weight: 800 !important; letter-spacing: -0.02em; line-height: 1.15; color: var(--text-primary); }}
h2 {{ font-size: 1.625rem !important; font-weight: 700 !important; letter-spacing: -0.015em; line-height: 1.25; color: var(--text-primary); }}
h3 {{ font-size: 1.25rem !important; font-weight: 700 !important; letter-spacing: -0.01em; line-height: 1.3; color: var(--text-primary); }}
.section-title {{ font-size: 0.78rem !important; font-weight: 700 !important; color: var(--text-muted); margin-bottom: 4px; letter-spacing: 0.10em; text-transform: uppercase; }}
.kpi-number, .tabular {{ font-family: "JetBrains Mono", "SF Mono", "Menlo", monospace !important; font-variant-numeric: tabular-nums !important; font-feature-settings: "tnum" 1, "lnum" 1; letter-spacing: -0.01em; }}
.kpi-number {{ font-weight: 800 !important; }}
.metric-label {{ font-size: 11px; font-weight: 600; color: var(--text-subtle); letter-spacing: 0.08em; text-transform: uppercase; }}
/* Streamlit dataframe — force theme-aware chrome (was white in dark mode) */
/* Themed HTML tables — used by render_themed_table() for full CSS control */
.themed-table-wrap {{ overflow-x: auto; border:1px solid var(--border-strong); border-radius:6px; background-color: var(--bg-surface); margin-bottom:14px; }}
.themed-table {{ width:100%; border-collapse: collapse; font-size:13px; color: var(--text-primary); background-color: var(--bg-surface); }}
.themed-table thead th {{ background-color: var(--bg-track) !important; color: var(--text-primary) !important; font-weight: 800; padding: 10px 12px; text-align: left; border-bottom: 2px solid var(--accent); border-right: 1px solid var(--text-subtle); letter-spacing: 0.08em; font-size: 13px; text-transform: uppercase; position: sticky; top: 0; }}
.themed-table thead th:last-child {{ border-right: none; }}
.themed-table tbody td {{ padding: 8px 14px; border-bottom: 1px solid var(--text-subtle); border-right: 1px solid var(--text-subtle); color: var(--text-primary); }}
.themed-table tbody td:last-child {{ border-right: none; }}
.themed-table tbody tr:last-child td {{ border-bottom: none; }}
.themed-table tbody tr:nth-child(even) td {{ background-color: var(--bg-track); }}
.themed-table tbody tr:hover td {{ background-color: var(--bg-track) !important; filter: brightness(1.05); }}
/* Right-align numeric columns automatically (kpi-number-friendly) */
.themed-table tbody td:has(> span.kpi-number), .themed-table td.numeric {{ text-align: right; font-variant-numeric: tabular-nums; }}
[data-testid=\"stDataFrame\"], [data-testid=\"stDataFrameResizable\"] {{ border:1px solid var(--border-default) !important; border-radius:6px; background-color: var(--bg-surface) !important; }}
[data-testid=\"stDataFrame\"] > div, [data-testid=\"stDataFrame\"] > div > div, [data-testid=\"stDataFrame\"] [class*=\"glideDataEditor\"], [data-testid=\"stDataFrame\"] canvas {{ background-color: var(--bg-surface) !important; color: var(--text-primary) !important; }}
/* Header row */
[data-testid=\"stDataFrame\"] [role=\"columnheader\"], [data-testid=\"stDataFrame\"] thead th, [data-testid=\"stDataFrame\"] [data-testid=\"stDataFrameColumnHeader\"] {{ background-color: var(--bg-track) !important; color: var(--text-soft) !important; font-weight: 700 !important; border-bottom: 1px solid var(--border-default) !important; }}
/* Body rows */
[data-testid=\"stDataFrame\"] [role=\"row\"], [data-testid=\"stDataFrame\"] [role=\"gridcell\"], [data-testid=\"stDataFrame\"] [role=\"rowheader\"], [data-testid=\"stDataFrame\"] tbody td, [data-testid=\"stDataFrame\"] tbody tr {{ background-color: var(--bg-surface) !important; color: var(--text-primary) !important; border-color: var(--border-default) !important; }}
/* Scrollbars + outer chrome */
[data-testid=\"stDataFrame\"] [class*=\"scrollableArea\"], [data-testid=\"stDataFrame\"] [data-testid=\"stDataFrameToolbar\"] {{ background-color: var(--bg-surface) !important; }}
[data-testid=\"stExpander\"], [data-testid=\"stExpander\"] > div, [data-testid=\"stExpander\"] > details {{ background-color: var(--bg-surface) !important; border-radius:6px !important; }}
[data-testid=\"stExpander\"] {{ border:1px solid var(--border-default) !important; overflow:hidden; }}
/* Expander header bar (summary): full background match to bg-surface in BOTH themes */
[data-testid=\"stExpander\"] details > summary, [data-testid=\"stExpander\"] [data-testid=\"stExpanderDetails\"], [data-testid=\"stExpander\"] [data-testid=\"stExpanderToggleIcon\"], [data-testid=\"stExpander\"] summary > div {{ background-color: var(--bg-surface) !important; color: var(--text-primary) !important; }}
[data-testid=\"stExpander\"] details {{ border-radius:6px; }}
[data-testid=\"stExpander\"] details > summary {{ padding: 8px 12px; }}
{dialog_css}
[data-testid=\"stAlert\"]     {{ border-radius:6px !important; }}
[data-baseweb=\"select\"]     {{ background-color: var(--bg-surface) !important; }}
[data-testid=\"stSelectbox\"] {{ max-width: 340px; }}
[data-baseweb=\"select\"] > div {{ background-color: var(--bg-surface) !important; border:1px solid var(--border-strong) !important; border-radius:6px !important; cursor:pointer !important; }}
[data-baseweb=\"select\"] > div:hover {{ border-color: var(--accent) !important; }}
/* Standardised dropdown indicator: accent-blue chevron so users see it as a control */
[data-baseweb=\"select\"] svg {{ fill: var(--accent) !important; color: var(--accent) !important; width: 18px !important; height: 18px !important; }}
hr {{ border-color: var(--border-default) !important; }}
::-webkit-scrollbar {{ width:6px; height:6px; }}
::-webkit-scrollbar-track {{ background: var(--bg-page); }}
::-webkit-scrollbar-thumb {{ background: var(--border-strong); border-radius:3px; }}
::-webkit-scrollbar-thumb:hover {{ background: var(--accent); }}
a.card-link {{ display:block; text-decoration:none; color:inherit; cursor:pointer; }}
a.card-link .exposure-card {{ transition: background 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease, transform 0.15s ease; }}
a.card-link:hover .exposure-card {{ background: {hover_card} !important; border-color: var(--accent) !important; box-shadow: 0 6px 16px rgba(0,0,0,0.14) !important; transform: translateY(-2px); }}
a.card-link:active .exposure-card {{ transform: translateY(0); box-shadow: 0 2px 6px rgba(0,0,0,0.10) !important; filter: brightness(0.97); }}
a.card-link:focus .exposure-card, a.card-link:focus-visible .exposure-card {{ outline: 2px solid var(--accent); outline-offset: 2px; }}
details > summary {{ list-style:none; cursor:pointer; outline:none; }}
details > summary::-webkit-details-marker {{ display:none; }}
details > summary::marker {{ display:none; }}
details > summary .chev {{ display:inline-block; transition: transform 0.18s ease; }}
details[open] > summary .chev {{ transform: rotate(180deg); }}
details.cockpit > summary {{ margin:-4px -6px; padding:4px 6px; border-radius:5px; transition: background 0.15s; }}
details > summary:hover {{ background: {hover_card} !important; }}
[data-testid=\"stExpander\"] summary:hover {{ background: {hover_card} !important; }}
section[data-testid=\"stSidebar\"] {{ display:none !important; }}
[data-testid=\"collapsedControl\"] {{ display:none !important; }}
.stTabs [data-baseweb=\"tab-list\"] {{ gap:2px; border-bottom:1px solid var(--border-default); }}
.stTabs [data-baseweb=\"tab\"] {{ font-size:15px; font-weight:500; padding:10px 20px; color: var(--text-muted); }}
.stTabs [aria-selected=\"true\"] {{ color: var(--text-primary) !important; }}
div[role=\"radiogroup\"] {{ gap:4px; border-bottom:1px solid var(--border-default); flex-wrap:wrap; margin-bottom:14px; }}
div[role=\"radiogroup\"] > label {{ margin:0 !important; padding:9px 18px; cursor:pointer; border-bottom:2px solid transparent; }}
div[role=\"radiogroup\"] > label:hover {{ background: var(--bg-surface); }}
div[role=\"radiogroup\"] > label > div:first-child {{ display:none !important; }}
div[role=\"radiogroup\"] > label p {{ font-size:15px !important; font-weight:500; color: var(--text-muted); }}
div[role=\"radiogroup\"] > label:has(input:checked) {{ border-bottom:2px solid var(--accent); }}
div[role=\"radiogroup\"] > label:has(input:checked) p {{ color: var(--text-primary); }}
a.investigate-btn:hover {{ background: {investigate_hover_bg} !important; color: {investigate_hover_text} !important; }}
/* === Sticky tab navigation === */
/* === Sticky tab nav (Pass 9.3) ===
   `position: sticky` on the radio itself often fails because it lives 4-5
   levels deep inside flex containers. Apply sticky to the OUTER element
   container that Streamlit creates around the keyed widget — sticky on a
   higher-level wrapper survives the nested layout. The `.st-key-active_page`
   class is the auto-generated key Streamlit adds for our `key="active_page"`
   radio, so it uniquely targets the nav (not other radios). */
header[data-testid="stHeader"] {{ display: none !important; height: 0 !important; }}
[data-testid="stToolbar"], [data-testid="stDecoration"] {{ display: none !important; }}
.block-container {{ padding-top: 1rem !important; }}

/* Sticky applied to MULTIPLE wrapper layers — at least one will be the
   correct positioning context. */
/* === Sticky nav v3 (Pass 9.5) ===
   `position: fixed` instead of sticky — fixed is positioned relative to the
   viewport, so width: 100% naturally spans full screen. Add padding-top on
   block-container so the page content starts BELOW the fixed bar (not under it).
   Inner div centers the radio at the same content width as the rest of the page. */
.st-key-active_page,
[data-testid="element-container"]:has([data-testid="stRadio"]) {{
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    right: 0 !important;
    width: 100vw !important;
    z-index: 9999 !important;
    background: var(--bg-page) !important;
    padding: 10px 0 6px 0 !important;
    margin: 0 !important;
    border-bottom: 1px solid var(--border-default);
    box-shadow: 0 4px 12px rgba(0,0,0,0.10);
}}
/* Re-centre the radio's inner content to match block-container width */
.st-key-active_page > div, .st-key-active_page [role="radiogroup"],
[data-testid="element-container"]:has([data-testid="stRadio"]) [role="radiogroup"] {{
    max-width: 1400px !important;
    margin: 0 auto !important;
    padding: 0 5rem !important;
}}
/* Reserve vertical space for the fixed nav so page content doesn't slide under it */
.block-container {{ padding-top: 4.5rem !important; }}
/* === Clickable cockpit widgets (Pass 4 UX): whole card is the drill-through === */
a.cockpit-link {{ display:block; text-decoration:none; color:inherit; cursor:pointer; transition: background 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease, transform 0.15s ease; }}
a.cockpit-link:hover {{ background: {hover_card} !important; border-color: var(--accent) !important; box-shadow: 0 6px 18px rgba(14,90,138,0.18); transform: translateY(-2px); }}
a.cockpit-link:active {{ transform: translateY(0); box-shadow: inset 0 0 0 2px var(--accent), 0 2px 6px rgba(0,0,0,0.12); background: {hover_card} !important; filter: brightness(0.96); }}
a.cockpit-link:focus, a.cockpit-link:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; }}
a.cockpit-link:visited {{ /* browser-tracked: subtle accent border for visited widgets */ }}
/* Universal hover on Streamlit expanders + native widgets */
[data-testid="stExpander"] {{ transition: border-color 0.15s ease, box-shadow 0.15s ease; }}
[data-testid="stExpander"]:hover {{ border-color: var(--accent) !important; box-shadow: 0 4px 12px rgba(0,0,0,0.10) !important; }}
[data-testid="stExpander"]:focus-within {{ border-color: var(--accent) !important; }}
[data-baseweb="select"] > div:hover {{ box-shadow: 0 0 0 2px rgba(79,142,247,0.18) !important; }}
[data-baseweb="select"] > div:focus-within {{ border-color: var(--accent) !important; box-shadow: 0 0 0 2px rgba(79,142,247,0.25) !important; }}
[data-testid="stButton"] button {{ transition: all 0.15s ease; }}
[data-testid="stButton"] button:active, [data-testid="stDownloadButton"] button:active {{ transform: translateY(1px); }}
.cockpit-static {{ transition: background 0.15s, border-color 0.15s, box-shadow 0.15s; }}
.cockpit-static:hover {{ background: {hover_card}; border-color: var(--accent); }}
.st-key-toggle_widgets {{ display:flex !important; justify-content:flex-end !important; margin-bottom:-6px !important; }}
.st-key-toggle_widgets button {{ padding:3px 12px !important; min-height:0 !important; height:30px !important; font-size:12px !important; line-height:1 !important; }}
/* === Cream-theme coverage for Streamlit-native widgets === */
[data-testid=\"stButton\"] button, [data-testid=\"stDownloadButton\"] button, [data-testid=\"stFormSubmitButton\"] button {{ background-color: var(--bg-surface) !important; color: var(--text-primary) !important; border: 1px solid var(--border-strong) !important; }}
[data-testid=\"stButton\"] button:hover, /* Action Plans export: keep the icon-only button compact and flush right within its column */
[class*=\"st-key-ap_export_\"] {{ display:flex !important; justify-content:flex-end !important; }}
[class*=\"st-key-ap_export_\"] button {{ min-width:40px !important; width:40px !important; padding:6px 8px !important; font-size:16px !important; line-height:1 !important; }}
[data-testid=\"stDownloadButton\"] button:hover, [data-testid=\"stFormSubmitButton\"] button:hover {{ background-color: {hover_card} !important; border-color: var(--accent) !important; color: var(--text-primary) !important; }}
[data-baseweb=\"menu\"], [data-baseweb=\"menu\"] ul, [data-baseweb=\"popover\"], [data-baseweb=\"select\"] [role=\"listbox\"], div[data-baseweb=\"select\"] *, [data-baseweb=\"select\"] input {{ background-color: var(--bg-surface) !important; color: var(--text-primary) !important; }}
/* The hover/selected option in dropdown lists — force accent tint, no cream */
[data-baseweb=\"menu\"] li, [data-baseweb=\"menu\"] [role=\"option\"] {{ background-color: var(--bg-surface) !important; color: var(--text-primary) !important; }}
[data-baseweb=\"menu\"] li:hover, [data-baseweb=\"menu\"] [role=\"option\"]:hover, [data-baseweb=\"menu\"] li[aria-selected=\"true\"], [data-baseweb=\"menu\"] [role=\"option\"][aria-selected=\"true\"] {{ background-color: {hover_card} !important; color: var(--text-primary) !important; }}
[data-baseweb=\"menu\"] li, [data-baseweb=\"menu\"] [role=\"option\"] {{ color: var(--text-primary) !important; background-color: var(--bg-surface) !important; }}
[data-baseweb=\"menu\"] li:hover, [data-baseweb=\"menu\"] [role=\"option\"]:hover, [data-baseweb=\"menu\"] li[aria-selected=\"true\"], [data-baseweb=\"menu\"] [role=\"option\"][aria-selected=\"true\"] {{ background-color: {hover_card} !important; color: var(--text-primary) !important; }}
[data-baseweb=\"tag\"] {{ background-color: var(--bg-track) !important; color: var(--text-primary) !important; border-color: var(--border-strong) !important; }}
[data-baseweb=\"tag\"] span {{ color: var(--text-primary) !important; }}
[data-baseweb=\"input\"], [data-baseweb=\"input\"] input, [data-baseweb=\"textarea\"] textarea {{ background-color: var(--bg-surface) !important; color: var(--text-primary) !important; }}
[data-testid=\"stExpander\"] details > summary, [data-testid=\"stExpander\"] details > summary p, [data-testid=\"stExpander\"] details > summary span {{ color: var(--text-primary) !important; }}
[data-testid=\"stExpander\"] details > summary svg {{ fill: var(--text-soft) !important; color: var(--text-soft) !important; }}
[data-testid=\"stCaptionContainer\"] p, [data-testid=\"stCaptionContainer\"], .stCaption {{ color: var(--text-muted) !important; }}
[data-testid=\"stWidgetLabel\"], [data-testid=\"stToggle\"] label, [data-testid=\"stCheckbox\"] label, label[data-baseweb=\"form-control-label\"] {{ color: var(--text-primary) !important; }}
[data-testid=\"stMarkdownContainer\"] p {{ color: var(--text-primary); }}
.stTabs [data-baseweb=\"tab-list\"] {{ background-color: transparent !important; }}
</style>
"""
    st.markdown(css, unsafe_allow_html=True)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def fmt_mv(v):  return f"£{v/1000:.1f}B" if v >= 1000 else f"£{v:.0f}M"
def fmt_pct(v): return f"{v*100:.1f}%"

def render_themed_table(df_or_styler, *, extra_classes="", max_height=None):
    """Render a DataFrame or pandas Styler via to_html() so it picks up our
    theme via CSS. Optional max_height (in px) caps visible height and enables
    vertical scroll — sticky headers stay anchored at the top of the scroll area."""
    import pandas as pd
    cls = f"themed-table {extra_classes}".strip()
    if hasattr(df_or_styler, "to_html") and not isinstance(df_or_styler, pd.DataFrame):
        html = df_or_styler.set_table_attributes(f'class="{cls}"').to_html()
    else:
        html = df_or_styler.to_html(classes=cls, border=0, index=False, justify="left")
    style_attr = f"max-height:{max_height}px;overflow-y:auto;" if max_height else ""
    st.markdown(
        f'<div class="themed-table-wrap" style="{style_attr}">{html}</div>',
        unsafe_allow_html=True,
    )


def apply_tier_style(styler, col):
    _pal = TIER_BG_CREAM if st.session_state.get("theme_mode", "dark") == "cream" else TIER_BG
    def _c(v): return _pal.get(v, "")
    try:    return styler.map(_c, subset=[col])
    except: return styler.applymap(_c, subset=[col])

# ─── Strategy Taxonomy ───────────────────────────────────────────────────────
# Two-level taxonomy:
#   - Strategy Group (top-level container, has owner)
#   - Strategy       (where the Red / Amber (= Red+Amber combined) thresholds live)
#
# Internal field names retain the v1 spelling for backwards compatibility:
#   - strategy_id / strategy_name      -> Strategy Group
#   - sub_strategy_id / sub_strategy_name -> Strategy
#
# 7 groups, 16 strategies. Only "PE Active" is engineered to breach.
STRATEGY_META = [
    # (sid, name (Strategy Group), owner)
    ("G01", "EQ Active",        "Alice Chen"),
    ("G02", "Fixed Income",     "Henry Park"),
    ("G03", "Hedge Fund",       "Eva Martinez"),
    ("G04", "Real Estate",      "Carol White"),
    ("G05", "Private Equities", "Frank Brown"),
    ("G06", "Infrastructure",   "Bob Smith"),
    ("G07", "Multi-Asset",      "Sarah Kim"),
]

# Strategy Status panel grouping: each Strategy Group is classed Public or Private.
# (This is a display grouping for the panel only — the strategy_id -> Strategy Group
#  link is retained in the data for Strategy Detail drill-through.)
PRODUCT_GROUPING = {
    "EQ Active":        "Public",
    "Fixed Income":     "Public",
    "Hedge Fund":       "Public",
    "Multi-Asset":      "Public",   # Multi Asset1
    "Private Equities": "Private",
    "Infrastructure":   "Private",
    "Real Estate":      "Private",
}

# Sub-strategies (= new "Strategy") — thresholds live HERE now.
# Format per child: (sub_id, sub_name, thr_red, thr_amber, thr_cum)
# Pass 18: proposed policy limits applied from the stakeholder spreadsheet.
# Tuple shape: (sub_id, sub_name, thr_red, thr_amber, thr_cum).
# thr_amber is kept equal to thr_cum since the dashboard reports Red and the
# cumulative Amber + Red — we don't track Amber-tier-only as a separate limit.
# Multi Asset left unchanged (no mapping provided in the spreadsheet).
# Pass 25.12: every Strategy-level Red limit and Amber+Red limit carries a
# flat +5pp buffer so utilisation never goes infinite against a 0% limit.
# Total Portfolio aggregate limits (TOTAL_PORTFOLIO_RED_LIMIT = 5%,
# TOTAL_PORTFOLIO_CUM_LIMIT = 25%) are NOT buffered.
SUB_STRATEGY_META = {
    # Format: (sub_strategy_id, name, threshold_red, threshold_amber, threshold_cum)
    # Each value = spreadsheet limit + 0.05 buffer, capped at 1.0.
    "G01": [
        ("S01a", "EQ Developed Markets", 0.05, 0.20, 0.20),     # was 0.00 / 0.15
        ("S01b", "EQ Emerging Markets",  0.05, 0.10, 0.10),     # was 0.00 / 0.05
    ],
    "G02": [
        ("S02a", "FI Active",            0.05, 0.18, 0.18),     # was 0.00 / 0.13
        ("S02b", "HY Credit",            0.05, 0.63, 0.63),     # was 0.00 / 0.58
        ("S02c", "MAARS",                0.05, 0.05, 0.05),     # was 0.00 / 0.00
        ("S02d", "EILB",                 0.05, 0.08, 0.08),     # was 0.00 / 0.03
    ],
    "G03": [
        # HF1 takes MA data: spreadsheet was A+R 100% / Red 25% → buffered to 100% / 30%
        # (A+R buffered to 105% but capped at 100% per user instruction)
        ("S03a", "MA",                   0.30, 1.00, 1.00),
        # Pass 29.14: HF2 mapped to SOG. Spreadsheet was Red 60% / A+R 60%
        # → buffered to Red 65% / A+R 65%.
        ("S03b", "Hedge Fund 2",         0.65, 0.65, 0.65),
    ],
    "G04": [
        ("S04a", "RE Bricks and Mortar", 0.05, 0.16, 0.16),     # was 0.00 / 0.11
        ("S04b", "RE Debt",              0.05, 0.07, 0.07),     # was 0.00 / 0.02
    ],
    "G05": [
        ("S05a", "PE Active",            0.14, 0.70, 0.70),     # was 0.09 / 0.65
        ("S05b", "PE Secondaries",       0.05, 0.50, 0.50),     # was 0.00 / 0.45
        ("S05c", "PE Mezz",              0.05, 0.45, 0.45),     # was 0.00 / 0.40
    ],
    "G06": [
        ("S06a", "Infrastructure Active", 0.05, 0.29, 0.29),    # was 0.00 / 0.24
        ("S06b", "Infrastructure Debt",   0.05, 0.45, 0.45),    # was 0.00 / 0.40
    ],
    "G07": [
        # Pass 29.14: Multi Asset1 mapped to Antares. Spreadsheet was
        # Red 0% / A+R 0% → buffered to Red 5% / A+R 5%.
        ("S07a", "Multi Asset1",         0.05, 0.05, 0.05),
    ],
}

# Pass 18.1: tier mix tuned against the real proposed limits applied in Pass 18.
# Result: only PE Secondaries breaches; Infra Active sits in ALERT; nothing
# else over its threshold.  Strategies with 0% Red limit have zero Red in the
# data (no more 999% spikes).  Tight cumulative limits (MAARS 0%, RE Debt 2%,
# EILB 3%) get fully Green tier-mix to absorb multinomial sampling variance.
# [green, amber, red] proportions.
TIER_MIX = {
    "EQ Developed Markets":         [0.93, 0.04, 0.03],
    "EQ Emerging Markets":          [0.97, 0.01, 0.02],
    "FI Active":                    [0.96, 0.01, 0.03],
    "HY Credit":                    [0.45, 0.10, 0.45],
    "MAARS":                        [0.88, 0.00, 0.12],
    "EILB":                         [1.00, 0.00, 0.00],
    "MA":                 [0.00, 0.55, 0.45],
    "Hedge Fund 2":                 [0.78, 0.13, 0.09],
    "RE Bricks and Mortar":         [0.62, 0.38, 0.00],
    "RE Debt":                      [0.99, 0.01, 0.00],
    "PE Active":                    [0.15, 0.80, 0.05],
    "PE Secondaries":               [0.32, 0.55, 0.13],
    "PE Mezz":                      [0.30, 0.35, 0.35],
    "Infrastructure Active":        [0.33, 0.66, 0.01],
    "Infrastructure Debt":          [0.25, 0.70, 0.05],
    "Multi Asset1":                 [0.92, 0.07, 0.01],
}

# Pass 25.0: Driver-of-gap + action status/plan from the framework spreadsheet.
# Single source of truth for the cockpit "Key drivers" chips, A.I. Observations
# "Active breaches" rewrite, and Action Tracker Kanban cards.
# action_status ∈ {"No initiative", "Planned / TBD", "In progress", "N/A"}
STRATEGY_REAL_DATA = {
    "EQ Developed Markets": {
        "driver":   "Opaque LO funds; non-core PE without fundamental metrics",
        "chips":    ["LO funds", "non-core PE", "fundamentals"],
        "status":   "No initiative",
        "action":   "",
    },
    "EQ Emerging Markets": {
        "driver":   "Opaque LO funds",
        "chips":    ["LO funds"],
        "status":   "No initiative",
        "action":   "",
    },
    "FI Active": {
        "driver":   "No lookthrough on macro / credit EFMs",
        "chips":    ["UPC", "macro EFMs", "credit EFMs"],
        "status":   "No initiative",
        "action":   "",
    },
    "HY Credit": {
        "driver":   "Missing fund-level metrics (country-sector, tranche type etc.)",
        "chips":    ["fund metrics", "country-sector", "tranche type"],
        "status":   "No initiative",
        "action":   "",
    },
    "MAARS": {
        # Pass 29.12: status flipped N/A → "In progress" because the sleeve
        # is actively being wound down ("EFM sleeve to be closed" is the
        # tracked initiative). Treating it as N/A excluded it from the
        # Kanban and broke the AI Observations breach math.
        "driver":   "No lookthrough on macro EFMs",
        "chips":    ["UPC", "macro EFMs"],
        "status":   "In progress",
        "action":   "EFM sleeve to be closed",
    },
    "EILB": {
        "driver":   "",
        "chips":    [],
        "status":   "N/A",
        "action":   "",
    },
    "MA": {  # Pass 29.9: was "Hedge Fund 1" in earlier dashboard versions
        "driver":   "Missing metrics",
        "chips":    ["metrics"],
        "status":   "In progress",
        "action":   "Engaging data vendor to collect fund-level data from managers' PDF reports",
    },
    "Hedge Fund 2": {  # no spreadsheet mapping — leave as no initiative
        "driver":   "Missing metrics",
        "chips":    ["metrics"],
        "status":   "No initiative",
        "action":   "",
    },
    "RE Bricks and Mortar": {
        "driver":   "Missing metrics",
        "chips":    ["metrics"],
        "status":   "No initiative",
        "action":   "",
    },
    "RE Debt": {  # maps to RE Credit in spreadsheet
        "driver":   "",
        "chips":    [],
        "status":   "N/A",
        "action":   "",
    },
    "PE Active": {
        "driver":   "Missing metrics",
        "chips":    ["metrics"],
        "status":   "In progress",
        "action":   "Existing initiative to improve DICI cashflow coverage metrics",
    },
    "PE Secondaries": {  # maps to PSL
        "driver":   "CI vehicles w/o lookthrough; DICIs with missing T&Cs, fundamental metrics",
        "chips":    ["CI: UPC", "DICI: T&Cs", "fundamentals"],
        "status":   "No initiative",
        "action":   "",
    },
    "PE Mezz": {
        "driver":   "CI vehicles w/o lookthrough; DICIs with missing T&Cs, fundamental metrics",
        "chips":    ["CI: UPC", "DICI: T&Cs", "fundamentals"],
        "status":   "No initiative",
        "action":   "",
    },
    "Infrastructure Active": {
        "driver":   "Fund route",
        "chips":    ["fund route"],
        "status":   "In progress",
        "action":   "Engaging external parties to collect operating metrics from larger subset of DICIs, in phases. Target: 80% coverage, TBD",
    },
    "Infrastructure Debt": {
        "driver":   "Fund route",
        "chips":    ["fund route"],
        "status":   "Planned / TBD",
        "action":   "TBD — prioritisation of Infra Active data collection",
    },
    "Multi Asset1": {  # unchanged — no spreadsheet mapping
        "driver":   "Missing metrics",
        "chips":    ["metrics"],
        "status":   "No initiative",
        "action":   "",
    },
}

# Pass 25.4: exposure targets taken verbatim from the framework spreadsheet.
# Format: sub_strategy_name -> (cum_pct, red_pct).  Used by the post-processor
# in generate_all_data to override the multinomial-sampled values with exact
# numbers so the dashboard matches the spreadsheet within ±0.1%.
# Strategies set to None retain their TIER_MIX-driven multinomial values.
EXPOSURE_TARGETS = {
    "EQ Developed Markets":   (0.17, 0.06),
    "EQ Emerging Markets":    (0.04, 0.02),
    "FI Active":              (0.05, 0.05),
    "HY Credit":              (0.54, 0.54),
    "MAARS":                  (0.11, 0.11),
    "EILB":                   (0.00, 0.00),
    "MA":           (1.00, 0.50),
    "Hedge Fund 2":           None,           # no spreadsheet mapping
    "RE Bricks and Mortar":   (0.40, 0.00),
    "RE Debt":                (0.02, 0.00),
    "PE Active":              (0.74, 0.12),
    "PE Secondaries":         (0.59, 0.15),
    "PE Mezz":                (0.67, 0.34),
    "Infrastructure Active":  (0.67, 0.03),
    "Infrastructure Debt":    (0.81, 0.09),
    "Multi Asset1":           None,           # no spreadsheet mapping
}

# Pass 25.13: per-Strategy portfolio MV share. Solved via LP to make the
# Total Portfolio land on Red 2.7% and Amber + Red 19.2% with the
# strategy-level exposures locked by EXPOSURE_TARGETS. Each value is the
# strategy's fraction of the TOTAL portfolio MV.
STRATEGY_MV_WEIGHTS = {
    "EQ Developed Markets":  0.1144,
    "EQ Emerging Markets":   0.0667,
    "FI Active":             0.1564,
    "HY Credit":             0.0038,
    "MAARS":                 0.0048,
    "EILB":                  0.0932,
    "MA":          0.0039,
    "Hedge Fund 2":          0.0302,
    "RE Bricks and Mortar":  0.1284,
    "RE Debt":               0.0835,
    "PE Active":             0.0048,
    "PE Secondaries":        0.0047,
    "PE Mezz":               0.0043,
    "Infrastructure Active": 0.0815,
    "Infrastructure Debt":   0.0048,
    "Multi Asset1":          0.2147,
}


# ── Total Portfolio aggregate limits (Pass 24.1) ─────────────────────────
# Hard-coded policy limits at the TOTAL portfolio level. Used by the two
# headline exposure cards + the footnote on Total Portfolio. Separate from
# the per-Strategy thresholds in SUB_STRATEGY_META, which the cockpit
# widgets and Strategy Detail page use.
TOTAL_PORTFOLIO_RED_LIMIT = 0.05    # 5% — Red exposure cap on the total portfolio
TOTAL_PORTFOLIO_CUM_LIMIT = 0.25    # 25% — Amber + Red cumulative cap

# Product / Instrument-Type pools — keyed by Strategy Group name.
PRODUCT_BY_STRATEGY = {
    "EQ Active":        ["Public"],
    "Fixed Income":     ["Public"],
    "Hedge Fund":       ["Private"],
    "Real Estate":      ["Private"],
    "Private Equities": ["Private"],
    "Infrastructure":   ["Private"],
    "Multi-Asset":      ["Public", "Private"],
}
INSTRUMENT_BY_STRATEGY = {
    "EQ Active":        ["Mandate", "Direct Investment"],
    "Fixed Income":     ["Mandate", "Direct Investment"],
    "Hedge Fund":       ["Fund Investment", "Mandate"],
    "Real Estate":      ["Fund Investment", "Direct Investment", "Co-investment"],
    "Private Equities": ["Fund Investment", "Co-investment"],
    "Infrastructure":   ["Fund Investment", "Direct Investment", "Co-investment"],
    "Multi-Asset":      ["Fund Investment", "Mandate"],
}

# ─── Synthetic Data ───────────────────────────────────────────────────────────


# ═══════════════════════════════════════════════════════════════════════════════
# Excel data loader (Pass 12) — drop a data_template.xlsx beside app.py and the
# dashboard will use that instead of generated synthetic data. Lets users test
# the dashboard with real data on another laptop without code changes.
# ═══════════════════════════════════════════════════════════════════════════════
def _load_data_from_excel(filepath):
    """Load raw data from an Excel template and re-apply the same derived/aggregate
    computations as the synthetic generator, so the rest of the app sees an
    identical dataset structure regardless of source."""
    import pandas as _pd
    import random as _random
    xl = _pd.ExcelFile(filepath)
    strategies_df     = _pd.read_excel(xl, "Strategies")
    sub_strategies_df = _pd.read_excel(xl, "Sub_Strategies")
    portfolios_df     = _pd.read_excel(xl, "Portfolios")
    instruments_df    = _pd.read_excel(xl, "Instruments")
    history_df        = _pd.read_excel(xl, "History")
    sub_history_df    = _pd.read_excel(xl, "Sub_History")
    audit_df          = _pd.read_excel(xl, "Audit")

    # Pass 29.9: backward compat — existing data_template.xlsx files use the
    # legacy "Hedge Fund 1" sub-strategy name. Normalise to "MA" at load time
    # so the rest of the codebase (which now keys on "MA") works transparently.
    _LEGACY_RENAME = {"Hedge Fund 1": "MA"}
    for _df in (sub_strategies_df, portfolios_df, instruments_df, sub_history_df):
        if "sub_strategy_name" in _df.columns:
            _df["sub_strategy_name"] = _df["sub_strategy_name"].replace(_LEGACY_RENAME)

    # Reconstruct list columns. Older templates stored them as |-separated
    # strings; newer regens may have written Python list repr strings. Handle both.
    import ast as _ast
    def _to_list(s):
        if s is None or (isinstance(s, float) and pd.isna(s)) or s == "":
            return []
        if isinstance(s, list):
            return s
        s = str(s).strip()
        if not s or s in ("[]", "—", "nan"):
            return []
        # list-repr path: try literal_eval first
        if s.startswith("[") and s.endswith("]"):
            try:
                v = _ast.literal_eval(s)
                return list(v) if isinstance(v, (list, tuple)) else [str(v)]
            except (ValueError, SyntaxError):
                pass
        # pipe-separated fallback (original Pass 12 format)
        return [x.strip() for x in s.split("|") if x.strip()]
    for _df in (portfolios_df, instruments_df):
        if "missing_fields_list" in _df.columns:
            _df["missing_fields_list"] = _df["missing_fields_list"].apply(_to_list)
        if "missing_fields_list" not in _df.columns and "missing_fields" in _df.columns:
            _df["missing_fields_list"] = _df["missing_fields"].apply(
                lambda s: [] if (s in (None, "", "—") or (isinstance(s, float) and pd.isna(s))) else [x.strip() for x in str(s).split(",")]
            )
        if "missing_count" not in _df.columns and "missing_fields_list" in _df.columns:
            _df["missing_count"] = _df["missing_fields_list"].apply(len)
        # Pass 15: missing_tiers parallel list. Excel templates may not carry it
        # — back-fill by treating every missing field as a Green-tier blocker
        # (conservative: no false-positive "Amber blocker" chips). Cell format
        # is pipe-separated like missing_fields_list.
        if "missing_tiers" in _df.columns:
            _df["missing_tiers"] = _df["missing_tiers"].apply(_to_list)
        if "missing_tiers" not in _df.columns and "missing_fields_list" in _df.columns:
            _df["missing_tiers"] = _df["missing_fields_list"].apply(lambda lst: ["Green"] * len(lst or []))

    # ── Derived columns on portfolios_df + instruments_df ──────────────────
    def _asset_type(row):
        bucket = "DICIs" if row["instrument_type"] in ("Direct Investment", "Co-investment") else "Fund Investments"
        return f'{row["product_type"]} {bucket}'
    portfolios_df["asset_type"] = portfolios_df.apply(_asset_type, axis=1)

    INVESTMENT_LARGE_MV = 200.0
    def _invbucket(itype, ptype, mv):
        if itype == "Fund Investment": return "FI"
        if itype in ("Direct Investment", "Mandate"): prefix = "DI"
        elif itype == "Co-investment": prefix = "CI"
        else: return "Other"
        if ptype == "Private":
            return f"{prefix} Large" if (mv or 0) > INVESTMENT_LARGE_MV else f"{prefix} Small"
        return prefix
    portfolios_df["investment_bucket"]  = portfolios_df.apply(
        lambda r: _invbucket(r["instrument_type"], r["product_type"], r["mv"]), axis=1)
    instruments_df["investment_bucket"] = instruments_df.apply(
        lambda r: _invbucket(r["instrument_type"], r["product_type"], r["mv"]), axis=1)

    # Sourcing rationale (synthetic narrative — Pass 3c)
    _SOURCING_RATIONALES = {
        ("Fund Investment",   "Private"): ["Top-quartile IRR manager; quarterly NAV cycle accepted at IC.","Strategic GP relationship; look-through agreement in renewal.","Long-vintage fund — disclosure tightens as positions exit.","Specialist sector exposure unavailable in more transparent vehicles."],
        ("Co-investment",     "Private"): ["Co-invest alongside top-tier GP — disclosure governed by side letter.","One-off deal with attractive entry economics; reduced reporting accepted.","Strategic allocation approved at IC; full disclosure planned post-close."],
        ("Direct Investment", "Private"): ["Direct stake in private company; quarterly board pack is the disclosure cadence.","Long-dated infrastructure asset; annual independent valuation.","Real-asset holding — third-party valuer constraints limit look-through."],
        ("Mandate",           "Public"): ["Separately-managed account — custodian provides month-end positions only.","Custom mandate; daily look-through pending custodian system upgrade."],
        ("Mandate",           "Private"): ["Mandate-style allocation to private credit; quarterly book provided.","Strategic mandate with named manager; SLA refresh in progress."],
        ("Fund Investment",   "Public"): ["Commingled fund — monthly transparency report meets policy.","ETF wrapper — daily holdings via custodian feed (data plumbing pending)."],
        ("Direct Investment", "Public"): ["Direct holding; transparency limited by exchange-disclosure rules."],
        ("Co-investment",     "Public"): ["Public co-invest; disclosure on standard issuer cadence."],
    }
    def _rationale(itype, ptype, tier, inst_id):
        if tier == "Green": return ""
        pool = _SOURCING_RATIONALES.get((itype, ptype), [])
        if not pool: return ""
        h = sum(ord(c) for c in str(inst_id)) % len(pool)
        return pool[h]
    instruments_df["sourcing_rationale"] = instruments_df.apply(
        lambda r: _rationale(r["instrument_type"], r["product_type"], r["tier"], r["instrument_id"]), axis=1)

    # Per-(instrument, field) synthetic age
    def _field_ages(row):
        out = {}
        for f in row["missing_fields_list"]:
            h = sum(ord(c) for c in (str(row["instrument_id"]) + f)) % 180
            out[f] = 14 + h
        return out
    instruments_df["field_age_days"] = instruments_df.apply(_field_ages, axis=1)

    # ── Aggregates: strat_agg + sub_strat_agg (matches the synthetic path) ─
    # Per-strategy_id totals
    tier_mv = (portfolios_df.groupby(["strategy_id","tier"])["mv"].sum().unstack(fill_value=0))
    for t in ("Green","Amber","Red"):
        if t not in tier_mv.columns: tier_mv[t] = 0
    total_mv = tier_mv.sum(axis=1).rename("total_mv")
    pct = tier_mv.div(total_mv, axis=0).rename(columns={"Green":"Green_pct","Amber":"Amber_pct","Red":"Red_pct"})
    strat_agg = (strategies_df.set_index("strategy_id").join(total_mv).join(pct).reset_index())
    strat_agg["cum_pct"] = strat_agg["Amber_pct"] + strat_agg["Red_pct"]
    # Group-level thresholds = MV-weighted avg of children thresholds
    child_thr = (sub_strategies_df.groupby("strategy_id").agg(
        threshold_red=("threshold_red","mean"),
        threshold_amber=("threshold_amber","mean"),
        threshold_cum=("threshold_cum","mean")).reset_index())
    strat_agg = strat_agg.merge(child_thr, on="strategy_id", how="left")

    # Per-sub_strategy_id totals
    sub_tier_mv = (portfolios_df.groupby(["sub_strategy_id","tier"])["mv"].sum().unstack(fill_value=0))
    for t in ("Green","Amber","Red"):
        if t not in sub_tier_mv.columns: sub_tier_mv[t] = 0
    sub_total_mv = sub_tier_mv.sum(axis=1).rename("total_mv")
    sub_pct = sub_tier_mv.div(sub_total_mv, axis=0).rename(columns={"Green":"Green_pct","Amber":"Amber_pct","Red":"Red_pct"})
    sub_strat_agg = (sub_strategies_df.set_index("sub_strategy_id").join(sub_total_mv).join(sub_pct).reset_index())
    sub_strat_agg["name"] = sub_strat_agg["sub_strategy_name"]
    sub_strat_agg["cum_pct"] = sub_strat_agg["Amber_pct"] + sub_strat_agg["Red_pct"]
    # Pass 18: handle 0/0 and x/0 explicitly so the UI never shows nan% or inf%.
    def _util(numer, denom):
        ratio = numer / denom.replace(0, _pd.NA)
        ratio = ratio.where(~((numer > 0) & (denom == 0)), 9.99)  # x / 0  → 999%
        return ratio.fillna(0.0)
    sub_strat_agg["red_utilisation"]   = _util(sub_strat_agg["Red_pct"],   sub_strat_agg["threshold_red"])
    sub_strat_agg["amber_utilisation"] = _util(sub_strat_agg["Amber_pct"], sub_strat_agg["threshold_amber"])
    sub_strat_agg["cum_utilisation"] = _util(sub_strat_agg["cum_pct"], sub_strat_agg["threshold_cum"])
    for col in ("red_utilisation","amber_utilisation","cum_utilisation"):
        sub_strat_agg[col] = sub_strat_agg[col].fillna(0)
    sub_strat_agg["red_breach"]   = sub_strat_agg["Red_pct"]   > sub_strat_agg["threshold_red"]
    sub_strat_agg["amber_breach"] = sub_strat_agg["Amber_pct"] > sub_strat_agg["threshold_amber"]
    sub_strat_agg["cum_breach"]   = sub_strat_agg["cum_pct"]   > sub_strat_agg["threshold_cum"]
    sub_strat_agg["any_breach"]   = sub_strat_agg["red_breach"] | sub_strat_agg["cum_breach"]
    sub_strat_agg["red_variance"]   = (sub_strat_agg["Red_pct"]   - sub_strat_agg["threshold_red"]).clip(lower=0)
    sub_strat_agg["amber_variance"] = (sub_strat_agg["Amber_pct"] - sub_strat_agg["threshold_amber"]).clip(lower=0)
    sub_strat_agg["cum_variance"]   = (sub_strat_agg["cum_pct"]   - sub_strat_agg["threshold_cum"]).clip(lower=0)

    # Transparency rating + breach reason / suggested action (Pass 3a)
    def _rating(g):
        if g >= 80: return "High"
        if g >= 50: return "Medium"
        return "Low"
    _green_pct = (1 - sub_strat_agg["cum_pct"]) * 100
    sub_strat_agg["transparency_rating"] = _green_pct.apply(_rating)
    sub_strat_agg["green_pct"]           = _green_pct.round(1)

    # Pass 24: top missing-field tags per Strategy. Tally missing fields across
    # all instruments in each Strategy and surface the top 4 most-frequent names
    # in the cockpit widget as "key drivers" of intransparency. Falls back to
    # the empty list when a Strategy has no missing fields.
    from collections import Counter as _Counter
    def _top_missing(sid):
        s = instruments_df[instruments_df["sub_strategy_id"] == sid]
        c = _Counter()
        for lst in s["missing_fields_list"]:
            if isinstance(lst, list):
                c.update(lst)
        return [n for n, _ in c.most_common(4)]
    sub_strat_agg["top_missing_fields"] = sub_strat_agg["sub_strategy_id"].apply(_top_missing)

    # Pass 17.18: count months in the past 12 where each Strategy crossed
    # either its Red or Amber + Red limit. Reads sub_history_df + the
    # thresholds already on sub_strat_agg. Defaults to 0 when no history.
    if sub_history_df is not None and len(sub_history_df) > 0:
        _thr_lookup = sub_strat_agg.set_index("sub_strategy_id")[["threshold_red", "threshold_cum"]]
        _hist_m = sub_history_df.merge(_thr_lookup, left_on="sub_strategy_id",
                                       right_index=True, how="left")
        _hist_m["had_breach"] = (
            (_hist_m["red_pct"] > _hist_m["threshold_red"]) |
            ((_hist_m["red_pct"] + _hist_m["amber_pct"]) > _hist_m["threshold_cum"])
        )
        _bc = _hist_m.groupby("sub_strategy_id")["had_breach"].sum().astype(int)
        sub_strat_agg["breaches_last_12mo"] = sub_strat_agg["sub_strategy_id"].map(_bc).fillna(0).astype(int)
    else:
        sub_strat_agg["breaches_last_12mo"] = 0
    _BR = [("Third-party data agreement","Renegotiate data feed terms"),
           ("GP reporting cycle (quarterly)","Awaiting next Q-end NAV"),
           ("Manager onboarding","Complete onboarding workflow"),
           ("Look-through limitations","Engage manager for look-through"),
           ("Data availability gap","Backfill missing fields")]
    def _assign_reason(sid, has):
        if not has: return ("","")
        return _BR[sum(ord(c) for c in str(sid)) % len(_BR)]
    _ra = [_assign_reason(r["sub_strategy_id"], bool(r["red_breach"] or r["cum_breach"]))
           for _, r in sub_strat_agg.iterrows()]
    sub_strat_agg["breach_reason"]    = [t[0] for t in _ra]
    sub_strat_agg["suggested_action"] = [t[1] for t in _ra]

    # Pass 25.2: real spreadsheet data — driver-of-gap + action status + plan text.
    sub_strat_agg["breach_driver"]    = sub_strat_agg["sub_strategy_name"].map(
        lambda n: STRATEGY_REAL_DATA.get(n, {}).get("driver", "")
    )
    sub_strat_agg["driver_chips"]     = sub_strat_agg["sub_strategy_name"].map(
        lambda n: list(STRATEGY_REAL_DATA.get(n, {}).get("chips", []))
    )
    sub_strat_agg["action_status"]    = sub_strat_agg["sub_strategy_name"].map(
        lambda n: STRATEGY_REAL_DATA.get(n, {}).get("status", "")
    )
    sub_strat_agg["action_plan_text"] = sub_strat_agg["sub_strategy_name"].map(
        lambda n: STRATEGY_REAL_DATA.get(n, {}).get("action", "")
    )

    # Pass 20: synthesize stress_loss_stagflation if the Excel template doesn't carry it
    if "stress_loss_stagflation" not in instruments_df.columns:
        import random as _r
        _seed_bak = _r.getstate(); _r.seed(20260605)
        def _stress(t):
            if t == "Green": return round(-(0.08 + _r.uniform(0, 0.07)), 4)
            if t == "Amber": return round(-(0.15 + _r.uniform(0, 0.15)), 4)
            return round(-(0.30 + _r.uniform(0, 0.25)), 4)
        instruments_df["stress_loss_stagflation"] = instruments_df["tier"].apply(_stress)
        _r.setstate(_seed_bak)
    # Pass 16.1: drop-then-map to survive Excel templates that already carry these columns.
    instruments_df = instruments_df.drop(columns=["strategy_total_mv", "mv_pct_of_strategy"], errors="ignore")
    _strat_totals_map = portfolios_df.groupby("strategy_id")["mv"].sum().to_dict()
    instruments_df["strategy_total_mv"]  = instruments_df["strategy_id"].map(_strat_totals_map)
    instruments_df["mv_pct_of_strategy"] = instruments_df["mv"] / instruments_df["strategy_total_mv"] * 100

    # Action items — Pass 29.9: same STRATEGY_REAL_DATA-based rebuild that the
    # synthetic path uses, so the Kanban shows the right "In Progress" cards
    # regardless of whether the dashboard loaded from Excel or generated fresh.
    action_items_df = _build_action_items_from_real_data(sub_strategies_df)

    return (strategies_df, sub_strategies_df, portfolios_df, instruments_df,
            strat_agg, sub_strat_agg, history_df, sub_history_df, audit_df, action_items_df)


def _build_synthetic_action_items(strategies_df, sub_strategies_df):
    """Generate the 15 mock action items the Action Tracker tab uses.
    Pass 14: owner is now a TEAM (CISD / Deal Team & Legal / Strategy Ops),
    derived from the action template, plus an impact_pp estimate."""
    import pandas as _pd
    import random as _random
    _now = datetime.now()
    rows = []
    names = list(strategies_df["name"])
    _seed = _random.getstate(); _random.seed(2026_06_01)
    for i, (title_tpl, reason, status, days, note, owner_team, impact_pp) in enumerate(ACTION_TEMPLATES):
        sname = names[i % len(names)]
        kids = sub_strategies_df[sub_strategies_df["strategy_id"]==
            strategies_df.set_index("name").loc[sname, "strategy_id"]]
        kid = kids.iloc[0]["sub_strategy_name"] if len(kids) else sname
        title = title_tpl.replace("{strat}", kid)
        if status == "Done":
            tgt = (_now - timedelta(days=days)).date()
            upd = (_now - timedelta(days=days - 5)).date()
        else:
            tgt = (_now + timedelta(days=days)).date()
            upd = (_now - timedelta(days=_random.randint(1, 14))).date()
        rows.append({"action_id": f"A{i+1:03d}","title":title,"strategy_group":sname,
                     "strategy_name":kid,"owner_team":owner_team,"impact_pp":impact_pp,
                     "status":status,"linked_reason":reason,"target_date":tgt,
                     "last_update":upd,"last_update_note":note})
    _random.setstate(_seed)
    return _pd.DataFrame(rows)


def _build_action_items_from_real_data(sub_strategies_df):
    """Pass 29.9: Kanban action items built from STRATEGY_REAL_DATA. Called
    by BOTH the synthetic-data path (generate_all_data) and the Excel-loader
    path (_load_data_from_excel) so the Action Tracker tab shows the right
    "In Progress" / "Recommended Action Plan" cards regardless of source.
    Originally lived inline in generate_all_data (Pass 25.7) — extracted
    here to fix the Excel-loader path which was still using the older
    template-based _build_synthetic_action_items list."""
    _now = datetime.now()
    _action_rows = []
    _OWNER_BY_GROUP = {
        "EQ Active":        "Strategy Ops",
        "Fixed Income":     "Strategy Ops",
        "Hedge Fund":       "Deal Team & Legal",
        "Real Estate":      "Deal Team & Legal",
        "Private Equities": "Deal Team & Legal",
        "Infrastructure":   "Deal Team & Legal",
        "Multi-Asset":      "CISD",
    }
    # Pass 27.8: 3-column Kanban — Recommended Action Plan / In Progress / Completed.
    # "No initiative" + "Planned / TBD" both map to "Recommended Action Plan".
    # "In progress" → "In Progress". "N/A" → excluded from the board.
    _STATUS_MAP = {
        "No initiative":  "Recommended Action Plan",
        "Planned / TBD":  "Recommended Action Plan",
        "In progress":    "In Progress",
    }
    _DAYS_BY_STATUS = {
        "Recommended Action Plan":  120,
        "In Progress":              60,
        "Completed":                -30,
    }
    _idx = 1
    for _, sub in sub_strategies_df.iterrows():
        sub_name = sub["sub_strategy_name"]
        real = STRATEGY_REAL_DATA.get(sub_name)
        if real is None:
            continue
        raw_status = real.get("status", "")
        # Pass 29.10: skip "No initiative" entirely — those strategies don't
        # have a tracked action yet, so a placeholder card on the Kanban
        # ("No active initiative yet…") is noise. The "8 need a Recommended
        # Action Plan" callout on Total Portfolio's A.I. Observations still
        # surfaces them so they aren't lost. N/A is also skipped (closed
        # sleeves / no exposure to track). Only Planned/TBD + In progress
        # produce cards from the spreadsheet.
        if raw_status in ("", "N/A", "No initiative"):
            continue
        new_status   = _STATUS_MAP.get(raw_status, raw_status)
        driver_text  = real.get("driver", "") or "—"
        action_text  = real.get("action", "") or ""
        owner_team   = _OWNER_BY_GROUP.get(sub["strategy_name"], "Strategy Ops")
        days_offset  = _DAYS_BY_STATUS.get(new_status, 90)
        if not action_text and raw_status == "Planned / TBD":
            action_text = "Planned — scope and timing TBD."
        _action_rows.append({
            "action_id":         f"A{_idx:03d}",
            "title":             f"{sub_name} — improve transparency",
            "strategy_group":    sub["strategy_name"],
            "strategy_name":     sub_name,
            "owner_team":        owner_team,
            "impact_pp":         0.0,
            "status":            new_status,
            "linked_reason":     driver_text,
            "target_date":       (_now + timedelta(days=days_offset)).date(),
            "last_update":       (_now - timedelta(days=14)).date(),
            "last_update_note":  action_text,
        })
        _idx += 1
    # Pass 29.10: the 3 sample "Completed" cards were demo-only filler. User
    # asked to remove them — Completed column will be empty until production
    # backs the dashboard with Jira/Dataquest history.
    return pd.DataFrame(_action_rows)


def _tier_mix_signature():
    """Stable signature of TIER_MIX values — feeds into the cache key so any
    edit to TIER_MIX invalidates the cached output without needing a manual
    "Clear cache" click."""
    import hashlib
    blob = repr(sorted(TIER_MIX.items())).encode("utf-8")
    return hashlib.md5(blob).hexdigest()[:10]


@st.cache_data
def generate_all_data(_tier_mix_sig: str = ""):
    # The _tier_mix_sig argument is part of the cache key — pass
    # _tier_mix_signature() at the call site so TIER_MIX edits propagate.
    # Excel-template short-circuit (Pass 12): if data_template.xlsx exists
    # in cwd, load raw data from it instead of generating synthetic data.
    import os as _os
    _EXCEL_PATH = "data_template.xlsx"
    if _os.path.exists(_EXCEL_PATH):
        try:
            return _load_data_from_excel(_EXCEL_PATH)
        except Exception as _e:
            import streamlit as _st
            _st.warning(f"Could not load {_EXCEL_PATH}: {_e}. Falling back to synthetic data.")

    np.random.seed(42);  random.seed(42)

    strategies_df = pd.DataFrame(STRATEGY_META, columns=[
        "strategy_id","name","owner"])
    # Backward-compat alias for downstream filters/heatmap that still read asset_class
    strategies_df["asset_class"] = strategies_df["name"]

    # Build Strategy table (= sub-strategies internally). Thresholds live HERE now.
    # Each child tuple is (sub_id, sub_name, thr_red, thr_amber, thr_cum).
    sub_rows = []
    for sid, subs in SUB_STRATEGY_META.items():
        strow = strategies_df[strategies_df["strategy_id"] == sid].iloc[0]
        for sub_id, sub_name, thr_red, thr_amber, thr_cum in subs:
            sub_rows.append({
                "sub_strategy_id":   sub_id,
                "sub_strategy_name": sub_name,
                "strategy_id":       sid,
                "strategy_name":     strow["name"],
                "owner":             strow["owner"],
                "threshold_red":     thr_red,
                "threshold_amber":   thr_amber,
                "threshold_cum":     thr_cum,
            })
    sub_strategies_df = pd.DataFrame(sub_rows)

    # Per-sub-strategy deterministic seeds so TIER_MIX tweaks for one strategy
    # don't cascade and change every downstream strategy's data
    SUB_SEEDS = {sid: 100 + i * 7
                 for i, sid in enumerate(sub_strategies_df["sub_strategy_id"])}

    port_rows, instr_rows, audit_rows = [], [], []

    # Generate portfolios per sub-strategy (instead of per strategy)
    for _, sub in sub_strategies_df.iterrows():
        np.random.seed(SUB_SEEDS[sub["sub_strategy_id"]])
        random.seed(SUB_SEEDS[sub["sub_strategy_id"]])
        n_ports  = random.randint(18, 28)   # larger sample -> tier mix tracks TIER_MIX more faithfully
        total_mv = round(random.uniform(400, 2200), 1)
        p_wts    = np.random.dirichlet(np.ones(n_ports) * 2)
        sname    = sub["strategy_name"]       # Strategy Group name (for PRODUCT/INSTRUMENT_BY pools)
        sub_name = sub["sub_strategy_name"]    # Strategy name (TIER_MIX is keyed here now)
        tier_p   = TIER_MIX.get(sub_name, [0.60, 0.30, 0.10])

        # Deterministic tier counts (multinomial) so TIER_MIX proportions are respected
        tier_counts = np.random.multinomial(n_ports, tier_p)
        tier_pool   = (["Green"] * tier_counts[0] +
                       ["Amber"] * tier_counts[1] +
                       ["Red"]   * tier_counts[2])
        np.random.shuffle(tier_pool)

        for pi, pw in enumerate(p_wts):
            pmv  = round(total_mv * pw, 2)
            tier = tier_pool[pi]
            pid  = f"P{sub['sub_strategy_id']}{pi+1:02d}"
            upd  = datetime.now() - timedelta(days=random.randint(0, 90))
            sect = random.choice(SECTORS)
            reg  = random.choice(REGIONS)

            product_type    = random.choice(PRODUCT_BY_STRATEGY.get(sname, ["Public", "Private"]))
            instrument_type = random.choice(INSTRUMENT_BY_STRATEGY.get(sname, ["Fund Investment", "Direct Investment"]))
            # Pass 15: framework-aligned missing fields. We pass sub_name (the leaf
            # Strategy like "PE Active") because STRATEGY_FAMILY is keyed there.
            miss, miss_tiers = _gen_missing(sub_name, instrument_type, tier, random)
            port_rows.append({
                "portfolio_id":      pid,
                "portfolio_name":    f"{sub['sub_strategy_name']} F{pi+1}",
                "sub_strategy_id":   sub["sub_strategy_id"],
                "sub_strategy_name": sub["sub_strategy_name"],
                "sub_asset_class":   sub["sub_strategy_name"],
                "strategy_id":       sub["strategy_id"],
                "strategy_name":     sname,
                "asset_class":       sname,
                "owner":             sub["owner"],
                "product_type":      product_type,
                "instrument_type":   instrument_type,
                "mv":                pmv, "tier": tier,
                "threshold_amber":   sub["threshold_amber"],
                "threshold_red":     sub["threshold_red"],
                "threshold_cum":     sub["threshold_cum"],
                "missing_fields":    ", ".join(miss) if miss else "—",
                "missing_fields_list": miss, "missing_count": len(miss),
                "missing_tiers":     miss_tiers,
                "region": reg, "sector": sect, "last_updated": upd,
                "comment": "",
            })

            # Audit trail: 3 historical tier changes per portfolio
            prev_tiers = ["Green", "Amber", "Red"]
            for days_ago in sorted(random.sample(range(10, 365), 3), reverse=True):
                prev = random.choice(prev_tiers)
                audit_rows.append({
                    "portfolio_id":      pid,
                    "portfolio_name":    f"{sub['sub_strategy_name']} F{pi+1}",
                    "strategy_name":     sname,
                    "sub_strategy_name": sub["sub_strategy_name"],
                    "changed_at": datetime.now() - timedelta(days=days_ago),
                    "previous_tier": prev,
                    "new_tier": tier,
                    "changed_by": random.choice(["System", sub["owner"], "Risk Team"]),
                    "reason": random.choice([
                        "Updated financials received", "NAV confirmed by manager",
                        "Missing LTV data resolved", "Annual review reclassification",
                        "Threshold breach escalation", "Manager engagement completed",
                    ]),
                })

            # Instruments under this portfolio
            # Tier of each instrument INHERITS from the parent portfolio so that
            # sum of Amber/Red instrument MV == sum of Amber/Red portfolio MV.
            # This makes the Action Plan's Impact reconcile with the card utilisation.
            # Missing-fields logic still varies per tier (Green = none, Amber = 1-2, Red = 2-4).
            n_inst = random.randint(3, 7)
            i_wts  = np.random.dirichlet(np.ones(n_inst) * 2)
            for ii, iw in enumerate(i_wts):
                imv   = round(pmv * iw, 2)
                itier = tier
                # Pass 15: framework-aligned missing fields
                im, im_tiers = _gen_missing(sub_name, instrument_type, itier, random)
                # Pass 20: per-instrument stress loss under Stagflation scenario.
                # Negative %, varies by tier (more opaque → more conservative)
                # + random noise per instrument. No tier override at runtime —
                # the number stored here is the number that's used.
                if itier == "Green":
                    _stress = -(0.08 + random.uniform(0, 0.07))    # -8 to -15%
                elif itier == "Amber":
                    _stress = -(0.15 + random.uniform(0, 0.15))    # -15 to -30%
                else:  # Red
                    _stress = -(0.30 + random.uniform(0, 0.25))    # -30 to -55%
                instr_rows.append({
                    "instrument_id":     f"I{pid}{ii+1:02d}",
                    "instrument_name":   f"{sname[:10]} Co. {ii+1}",
                    "portfolio_id":      pid,
                    "portfolio_name":    f"{sub['sub_strategy_name']} F{pi+1}",
                    "sub_strategy_id":   sub["sub_strategy_id"],
                    "sub_strategy_name": sub["sub_strategy_name"],
                    "sub_asset_class":   sub["sub_strategy_name"],
                    "strategy_id":       sub["strategy_id"],
                    "strategy_name":     sname,
                    "asset_class":       sname,
                    "asset_type": random.choice(["Equity","Debt","Real Asset","Fund","Direct"]),
                    "instrument_type": instrument_type,
                    "product_type":    product_type,
                    "mv": imv, "tier": itier,
                    "missing_fields": ", ".join(im) if im else "—",
                    "missing_fields_list": im,
                    "missing_tiers":     im_tiers,
                    "stress_loss_stagflation": round(_stress, 4),
                    "region": reg, "sector": sect,
                    "last_updated": datetime.now() - timedelta(days=random.randint(0, 120)),
                })

    portfolios_df  = pd.DataFrame(port_rows)
    # Asset type — Public/Private × DICI/Fund-Investment matrix used by the Breakdown 'Cut by'.
    # DICIs = Direct + Co-investment; Fund Investments = Fund + Mandate.
    def _asset_type(row):
        bucket = 'DICIs' if row['instrument_type'] in ('Direct Investment', 'Co-investment') else 'Fund Investments'
        return f"{row['product_type']} {bucket}"
    portfolios_df['asset_type'] = portfolios_df.apply(_asset_type, axis=1)
    instruments_df = pd.DataFrame(instr_rows)
    audit_df       = pd.DataFrame(audit_rows)

    # ── Pass 25.4: exact-exposure post-processor ─────────────────────────────
    # Override portfolio tiers + MVs so each strategy's MV-weighted A+R% and Red%
    # exactly match the spreadsheet targets. Bypasses multinomial variance.
    # Skips strategies whose EXPOSURE_TARGETS entry is None.
    def _enforce_exact_exposures(portfolios_df, instruments_df):
        import numpy as _np
        for sub_name, target in EXPOSURE_TARGETS.items():
            if target is None:
                continue
            cum_target, red_target = target
            green_target = max(0.0, 1.0 - cum_target)
            amber_target = max(0.0, cum_target - red_target)

            mask = portfolios_df["sub_strategy_name"] == sub_name
            if not mask.any():
                continue
            idx = portfolios_df.index[mask].tolist()
            n   = len(idx)
            total_strategy_mv = float(portfolios_df.loc[idx, "mv"].sum())
            if total_strategy_mv <= 0:
                continue

            # Decide how many portfolios per tier. Floor by 1 if the target > 0.
            n_red = max(1, int(round(n * red_target)))   if red_target   > 0 else 0
            n_green = max(1, int(round(n * green_target))) if green_target > 0 else 0
            n_amber = n - n_red - n_green
            if n_amber < 0:  # rounding overshoot — pull one off the largest tier
                if n_red >= n_green: n_red -= 1
                else: n_green -= 1
                n_amber = 0
            if amber_target == 0:
                # No Amber wanted — re-balance into Green / Red.
                if n_amber > 0:
                    if n_green >= n_red: n_green += n_amber
                    else: n_red += n_amber
                    n_amber = 0
            elif n_amber == 0 and amber_target > 0:
                # Need at least 1 Amber.
                if n_green > 1:
                    n_green -= 1; n_amber = 1
                elif n_red > 1:
                    n_red -= 1; n_amber = 1

            # Sort portfolio rows in this strategy by their CURRENT MV (desc),
            # then assign the n_red largest to Red, next n_amber to Amber, rest Green.
            sub_df = portfolios_df.loc[idx].sort_values("mv", ascending=False)
            sorted_idx = sub_df.index.tolist()
            red_idx   = sorted_idx[:n_red]
            amber_idx = sorted_idx[n_red:n_red + n_amber]
            green_idx = sorted_idx[n_red + n_amber:]

            # Set tier labels.
            for i in red_idx:   portfolios_df.at[i, "tier"] = "Red"
            for i in amber_idx: portfolios_df.at[i, "tier"] = "Amber"
            for i in green_idx: portfolios_df.at[i, "tier"] = "Green"

            # Scale MVs within each tier so the MV-weighted percentages exactly
            # hit (red_target, amber_target, green_target). Each tier's
            # portfolios get a uniform multiplier.
            for tier_name, tier_idx, tier_target in [
                ("Red",   red_idx,   red_target),
                ("Amber", amber_idx, amber_target),
                ("Green", green_idx, green_target),
            ]:
                if not tier_idx:
                    continue
                want_mv = tier_target * total_strategy_mv
                cur_mv  = float(portfolios_df.loc[tier_idx, "mv"].sum())
                if cur_mv > 0:
                    scale = want_mv / cur_mv
                else:
                    # All MVs were zero — distribute evenly (rare).
                    scale = 0
                    per = want_mv / len(tier_idx)
                    for i in tier_idx:
                        portfolios_df.at[i, "mv"] = round(per, 2)
                if scale:
                    for i in tier_idx:
                        portfolios_df.at[i, "mv"] = round(portfolios_df.at[i, "mv"] * scale, 2)

            # Propagate the tier + MV scaling into the instruments. Each
            # instrument inherits its portfolio's tier; MVs scale uniformly per
            # portfolio so the per-portfolio MV stays consistent.
            new_pf_mv_lookup = dict(zip(portfolios_df.loc[idx, "portfolio_id"],
                                        portfolios_df.loc[idx, "mv"]))
            new_tier_lookup  = dict(zip(portfolios_df.loc[idx, "portfolio_id"],
                                        portfolios_df.loc[idx, "tier"]))
            inst_mask = instruments_df["portfolio_id"].isin(new_pf_mv_lookup.keys())
            for pid, new_mv in new_pf_mv_lookup.items():
                pmask = instruments_df["portfolio_id"] == pid
                if not pmask.any():
                    continue
                cur_pf_mv = float(instruments_df.loc[pmask, "mv"].sum())
                if cur_pf_mv > 0:
                    instr_scale = new_mv / cur_pf_mv
                    instruments_df.loc[pmask, "mv"] = (instruments_df.loc[pmask, "mv"] * instr_scale).round(2)
                instruments_df.loc[pmask, "tier"] = new_tier_lookup[pid]
        return portfolios_df, instruments_df

    portfolios_df, instruments_df = _enforce_exact_exposures(portfolios_df, instruments_df)

    # ── Pass 25.13: Total Portfolio MV-share post-processor ─────────────────
    # Scale each strategy's total MV so the AUM-weighted portfolio Red% and
    # Amber+Red% match the targets (2.7% / 19.2%). Within-strategy splits set
    # by enforce_exact_exposures are preserved.
    def _apply_portfolio_weights(portfolios_df, instruments_df):
        try:
            total_target = float(portfolios_df["mv"].sum())   # keep portfolio £ size constant
        except Exception:
            total_target = 100000.0
        for sub_name, share in STRATEGY_MV_WEIGHTS.items():
            mask = portfolios_df["sub_strategy_name"] == sub_name
            if not mask.any():
                continue
            cur_mv  = float(portfolios_df.loc[mask, "mv"].sum())
            want_mv = total_target * float(share)
            if cur_mv <= 0:
                continue
            scale = want_mv / cur_mv
            portfolios_df.loc[mask, "mv"] = (portfolios_df.loc[mask, "mv"] * scale).round(2)
            pids = portfolios_df.loc[mask, "portfolio_id"].tolist()
            i_mask = instruments_df["portfolio_id"].isin(pids)
            instruments_df.loc[i_mask, "mv"] = (instruments_df.loc[i_mask, "mv"] * scale).round(2)
        return portfolios_df, instruments_df
    portfolios_df, instruments_df = _apply_portfolio_weights(portfolios_df, instruments_df)


    # Compute instrument MV % of parent strategy (exposure only)
    strat_totals = portfolios_df.groupby("strategy_id")["mv"].sum().rename("strategy_total_mv")
    instruments_df = instruments_df.merge(strat_totals, on="strategy_id")
    instruments_df["mv_pct_of_strategy"] = instruments_df["mv"] / instruments_df["strategy_total_mv"] * 100

    # ── Strategy-level aggregates ────────────────────────────────────────────
    tier_mv = (portfolios_df.groupby(["strategy_id","tier"])["mv"]
               .sum().unstack(fill_value=0))
    for c in ["Green","Amber","Red"]:
        if c not in tier_mv.columns: tier_mv[c] = 0.0
    tier_mv["total_mv"] = tier_mv.sum(axis=1)
    tier_mv["Green_pct"] = tier_mv["Green"] / tier_mv["total_mv"]
    tier_mv["Amber_pct"] = tier_mv["Amber"] / tier_mv["total_mv"]
    tier_mv["Red_pct"]   = tier_mv["Red"]   / tier_mv["total_mv"]
    tier_mv = tier_mv.reset_index()

    strat_agg = strategies_df.merge(
        tier_mv[["strategy_id","Green_pct","Amber_pct","Red_pct","total_mv"]], on="strategy_id")
    strat_agg["cum_pct"] = strat_agg["Amber_pct"] + strat_agg["Red_pct"]
    # Group-level "thresholds" are MV-weighted aggregates of child Strategy thresholds.
    # Populated below from sub_strat_agg once that exists.

    # ── Sub-strategy-level aggregates ────────────────────────────────────────
    sub_tier_mv = (portfolios_df.groupby(["sub_strategy_id","tier"])["mv"]
                   .sum().unstack(fill_value=0))
    for c in ["Green","Amber","Red"]:
        if c not in sub_tier_mv.columns: sub_tier_mv[c] = 0.0
    sub_tier_mv["total_mv"] = sub_tier_mv.sum(axis=1)
    sub_tier_mv["Green_pct"] = sub_tier_mv["Green"] / sub_tier_mv["total_mv"]
    sub_tier_mv["Amber_pct"] = sub_tier_mv["Amber"] / sub_tier_mv["total_mv"]
    sub_tier_mv["Red_pct"]   = sub_tier_mv["Red"]   / sub_tier_mv["total_mv"]
    sub_tier_mv = sub_tier_mv.reset_index()

    sub_strat_agg = sub_strategies_df.merge(
        sub_tier_mv[["sub_strategy_id","Green_pct","Amber_pct","Red_pct","total_mv"]],
        on="sub_strategy_id")
    sub_strat_agg["cum_pct"] = sub_strat_agg["Amber_pct"] + sub_strat_agg["Red_pct"]
    # Pass 18: clean utilisation div — when limit is 0% (some real policy limits are
    # 0%, meaning the Strategy must be fully Green) and exposure is also 0 we want
    # to show 0% utilisation, not NaN. When limit is 0% and exposure > 0 we cap at
    # 999% so the display reads as a clear breach without rendering "inf%".
    def _util(numer, denom):
        ratio = numer / denom.replace(0, np.nan)
        ratio = ratio.where(~((numer > 0) & (denom == 0)), 9.99)  # x / 0  → 999%
        return ratio.fillna(0.0)
    sub_strat_agg["red_utilisation"]   = _util(sub_strat_agg["Red_pct"],   sub_strat_agg["threshold_red"])
    sub_strat_agg["amber_utilisation"] = _util(sub_strat_agg["Amber_pct"], sub_strat_agg["threshold_amber"])
    sub_strat_agg["cum_utilisation"]   = _util(sub_strat_agg["cum_pct"],   sub_strat_agg["threshold_cum"])
    sub_strat_agg["red_breach"]   = sub_strat_agg["Red_pct"]   > sub_strat_agg["threshold_red"]
    sub_strat_agg["amber_breach"] = sub_strat_agg["Amber_pct"] > sub_strat_agg["threshold_amber"]
    sub_strat_agg["cum_breach"]   = sub_strat_agg["cum_pct"]   > sub_strat_agg["threshold_cum"]
    sub_strat_agg["any_breach"]   = sub_strat_agg["red_breach"] | sub_strat_agg["cum_breach"]   # Amber-tier-only breach intentionally NOT counted
    sub_strat_agg["name"]         = sub_strat_agg["sub_strategy_name"]

    # Roll children up into the Strategy-Group aggregates (strat_agg). MV-weighted
    # thresholds + Group "any_breach" if any child Strategy breaches.
    def _mv_weighted_thr(df, col):
        tm = df["total_mv"].sum()
        return (df[col] * df["total_mv"]).sum() / tm if tm > 0 else 0.0
    group_rows = []
    for sid in strat_agg["strategy_id"]:
        children = sub_strat_agg[sub_strat_agg["strategy_id"] == sid]
        any_b = bool(children["any_breach"].any())
        any_red = bool(children["red_breach"].any())
        any_amb = bool(children["amber_breach"].any())
        any_cum = bool(children["cum_breach"].any())
        thr_r = _mv_weighted_thr(children, "threshold_red")
        thr_a = _mv_weighted_thr(children, "threshold_amber")
        thr_c = _mv_weighted_thr(children, "threshold_cum")
        group_rows.append((sid, thr_r, thr_a, thr_c, any_red, any_amb, any_cum, any_b))
    _g = pd.DataFrame(group_rows, columns=[
        "strategy_id", "threshold_red", "threshold_amber", "threshold_cum",
        "red_breach", "amber_breach", "cum_breach", "any_breach"])
    strat_agg = strat_agg.merge(_g, on="strategy_id")
    strat_agg["amber_variance"]  = strat_agg["Amber_pct"] - strat_agg["threshold_amber"]
    strat_agg["red_variance"]    = strat_agg["Red_pct"]   - strat_agg["threshold_red"]
    strat_agg["cum_variance"]    = strat_agg["cum_pct"]   - strat_agg["threshold_cum"]
    # Pass 18: same 0/0 + x/0 handling at the Strategy Group level
    def _util_g(numer, denom):
        ratio = numer / denom.replace(0, pd.NA)
        ratio = ratio.where(~((numer > 0) & (denom == 0)), 9.99)
        return ratio.fillna(0.0)
    strat_agg["red_utilisation"]   = _util_g(strat_agg["Red_pct"],   strat_agg["threshold_red"])
    strat_agg["amber_utilisation"] = _util_g(strat_agg["Amber_pct"], strat_agg["threshold_amber"])
    strat_agg["cum_utilisation"] = _util_g(strat_agg["cum_pct"], strat_agg["threshold_cum"])
    strat_agg = strat_agg.fillna({"red_utilisation": 0, "amber_utilisation": 0, "cum_utilisation": 0})

    # Historical data (12 months, strategy-level).
    # Anchored to CURRENT snapshot: month 0 (today) equals strat_agg exactly,
    # so the rightmost bar in the trend chart reconciles with the top exposure cards.
    # Older months walk backwards with mild positive drift + noise (simulates improvement).
    np.random.seed(9999); random.seed(9999)
    current_map = {
        r["strategy_id"]: (float(r["Amber_pct"]), float(r["Red_pct"]))
        for _, r in strat_agg.iterrows()
    }
    mv_map = dict(zip(strat_agg["strategy_id"], strat_agg["total_mv"]))
    hist_rows = []
    today = datetime.now()
    for _, s in strategies_df.iterrows():
        sid = s["strategy_id"]
        cur_a, cur_r = current_map.get(sid, (0.0, 0.0))
        for mo in range(0, 12):                           # 0 = current month, 11 = oldest
            dt = today.replace(day=1) - timedelta(days=30*mo)
            if mo == 0:
                ba, br = cur_a, cur_r                      # exact match to top-panel snapshot
            else:
                drift = mo * 0.004                         # older months ~0.4pp/mo more non-transparent
                ba = max(0.0, min(0.95, cur_a + drift + random.uniform(-0.015, 0.025)))
                br = max(0.0, min(0.30, cur_r + drift * 0.5 + random.uniform(-0.005, 0.012)))
            bg = max(0.0, 1 - ba - br)
            hist_rows.append({
                "date": dt, "strategy_id": sid,
                "strategy_name": s["name"], "asset_class": s["name"],
                "green_pct": bg, "amber_pct": ba, "red_pct": br,
                "non_transparent_pct": ba + br,
                "mv": mv_map.get(sid, 0.0),
            })
    history_df = pd.DataFrame(hist_rows)

    # Per-Strategy (sub-strategy) monthly history — same anchored-to-current + drift
    # pattern as the Group history, so a single Strategy's trend can be shown.
    np.random.seed(4242); random.seed(4242)
    sub_current_map = {
        r["sub_strategy_id"]: (float(r["Amber_pct"]), float(r["Red_pct"]))
        for _, r in sub_strat_agg.iterrows()
    }
    sub_mv_map = dict(zip(sub_strat_agg["sub_strategy_id"], sub_strat_agg["total_mv"]))
    sub_hist_rows = []
    # Pass 18.2: per-strategy threshold caps so older months don't accidentally
    # breach when the current snapshot is clean.  Strategies currently in breach
    # keep the unconstrained drift (so PE Secondaries shows a real breach
    # history); strategies currently OK are clamped to 90% of their limits.
    sub_thr_map = {
        r["sub_strategy_id"]: (float(r["threshold_red"]),
                                float(r["threshold_cum"]),
                                bool(r["red_breach"]),
                                bool(r["cum_breach"]))
        for _, r in sub_strat_agg.iterrows()
    }
    for _, ss in sub_strat_agg.iterrows():
        ssid = ss["sub_strategy_id"]
        cur_a, cur_r = sub_current_map.get(ssid, (0.0, 0.0))
        thr_red, thr_cum, cur_red_breach, cur_cum_breach = sub_thr_map.get(
            ssid, (1.0, 1.0, False, False))
        # Caps used for non-breaching strategies — leave 10% headroom.
        red_cap = thr_red * 0.9 if not cur_red_breach else 1.0
        cum_cap = thr_cum * 0.9 if not cur_cum_breach else 1.0
        for mo in range(0, 12):
            dt = today.replace(day=1) - timedelta(days=30*mo)
            if mo == 0:
                ba, br = cur_a, cur_r
            else:
                drift = mo * 0.004
                ba = max(0.0, min(0.95, cur_a + drift + random.uniform(-0.015, 0.025)))
                br = max(0.0, min(0.30, cur_r + drift * 0.5 + random.uniform(-0.005, 0.012)))
                # Clamp to thresholds (for currently-OK strategies)
                if not cur_red_breach:
                    br = min(br, red_cap)
                if not cur_cum_breach:
                    cum_sum = ba + br
                    if cum_sum > cum_cap and cum_sum > 0:
                        scale = cum_cap / cum_sum
                        ba *= scale
                        br *= scale
            bg = max(0.0, 1 - ba - br)
            sub_hist_rows.append({
                "date": dt,
                "strategy_id": ss["strategy_id"],
                "sub_strategy_id": ssid,
                "sub_strategy_name": ss["sub_strategy_name"],
                "green_pct": bg, "amber_pct": ba, "red_pct": br,
                "non_transparent_pct": ba + br,
                "mv": sub_mv_map.get(ssid, 0.0),
            })
    sub_history_df = pd.DataFrame(sub_hist_rows)

    # ── action_items_df: rebuilt from STRATEGY_REAL_DATA (Pass 25.7) ──────────
    # Pass 29.9: extracted into a helper so both the Excel-loader and the
    # synthetic-data paths produce the same Kanban content.
    action_items_df = _build_action_items_from_real_data(sub_strategies_df)

    # ── transparency_rating: High / Medium / Low per Strategy ─────────────────
    # Based on Green % = 100 - non-transparent %. Stakeholders asked for an
    # at-a-glance rating in addition to the breach traffic-light.
    def _rating(green_pct):
        if green_pct >= 80: return "High"
        if green_pct >= 50: return "Medium"
        return "Low"
    _green_pct = (1 - sub_strat_agg["cum_pct"]) * 100
    sub_strat_agg["transparency_rating"] = _green_pct.apply(_rating)
    sub_strat_agg["green_pct"]           = _green_pct.round(1)

    # Pass 24: top missing-field tags per Strategy (Excel-loader path).
    from collections import Counter as _Counter
    def _top_missing_xl(sid):
        s = instruments_df[instruments_df["sub_strategy_id"] == sid]
        c = _Counter()
        for lst in s["missing_fields_list"]:
            if isinstance(lst, list):
                c.update(lst)
        return [n for n, _ in c.most_common(4)]
    sub_strat_agg["top_missing_fields"] = sub_strat_agg["sub_strategy_id"].apply(_top_missing_xl)

    # Pass 17.18: count months in the past 12 where each Strategy crossed
    # either its Red or Amber + Red limit. Reads sub_history_df + the
    # thresholds already on sub_strat_agg. Defaults to 0 when no history.
    if sub_history_df is not None and len(sub_history_df) > 0:
        _thr_lookup = sub_strat_agg.set_index("sub_strategy_id")[["threshold_red", "threshold_cum"]]
        _hist_m = sub_history_df.merge(_thr_lookup, left_on="sub_strategy_id",
                                       right_index=True, how="left")
        _hist_m["had_breach"] = (
            (_hist_m["red_pct"] > _hist_m["threshold_red"]) |
            ((_hist_m["red_pct"] + _hist_m["amber_pct"]) > _hist_m["threshold_cum"])
        )
        _bc = _hist_m.groupby("sub_strategy_id")["had_breach"].sum().astype(int)
        sub_strat_agg["breaches_last_12mo"] = sub_strat_agg["sub_strategy_id"].map(_bc).fillna(0).astype(int)
    else:
        sub_strat_agg["breaches_last_12mo"] = 0
    # ── breach_reason + suggested_action (synthetic, deterministic) ──────────
    # Per-Strategy driver-of-intransparency context. Assignment is deterministic
    # (hash of sub_strategy_id) so it doesn't reshuffle on rerun. Only breaching
    # strategies (red OR cum) get a reason; non-breaching ones stay blank.
    _BREACH_REASONS = [
        ("Third-party data agreement",     "Renegotiate data feed terms"),
        ("GP reporting cycle (quarterly)", "Awaiting next Q-end NAV"),
        ("Manager onboarding",             "Complete onboarding workflow"),
        ("Look-through limitations",       "Engage manager for look-through"),
        ("Data availability gap",          "Backfill missing fields"),
    ]
    def _assign_reason(sub_id, has_breach):
        if not has_breach:
            return ("", "")
        h = sum(ord(c) for c in str(sub_id)) % len(_BREACH_REASONS)
        return _BREACH_REASONS[h]
    _ra = [_assign_reason(r["sub_strategy_id"], bool(r["red_breach"] or r["cum_breach"]))
           for _, r in sub_strat_agg.iterrows()]
    sub_strat_agg["breach_reason"]    = [t[0] for t in _ra]
    sub_strat_agg["suggested_action"] = [t[1] for t in _ra]

    # Pass 25.2: real spreadsheet data — driver-of-gap + action status + plan text.
    sub_strat_agg["breach_driver"]    = sub_strat_agg["sub_strategy_name"].map(
        lambda n: STRATEGY_REAL_DATA.get(n, {}).get("driver", "")
    )
    sub_strat_agg["driver_chips"]     = sub_strat_agg["sub_strategy_name"].map(
        lambda n: list(STRATEGY_REAL_DATA.get(n, {}).get("chips", []))
    )
    sub_strat_agg["action_status"]    = sub_strat_agg["sub_strategy_name"].map(
        lambda n: STRATEGY_REAL_DATA.get(n, {}).get("status", "")
    )
    sub_strat_agg["action_plan_text"] = sub_strat_agg["sub_strategy_name"].map(
        lambda n: STRATEGY_REAL_DATA.get(n, {}).get("action", "")
    )

    # ── investment_bucket: 5-cut DQ dimension ──────────────────────────────────
    # Mandate folded into DI; Large/Small split only for PRIVATE investments
    # using a USD 200M MV threshold (synthetic data is in £M; same numeric scale).
    # Public DI / Public CI (if any) get no size split.
    INVESTMENT_LARGE_MV = 200.0   # £M threshold
    def _invbucket(itype, ptype, mv):
        if itype == "Fund Investment":
            return "FI"
        if itype in ("Direct Investment", "Mandate"):
            prefix = "DI"
        elif itype == "Co-investment":
            prefix = "CI"
        else:
            return "Other"
        if ptype == "Private":
            return f"{prefix} Large" if (mv or 0) > INVESTMENT_LARGE_MV else f"{prefix} Small"
        return prefix
    portfolios_df["investment_bucket"]  = portfolios_df.apply(
        lambda r: _invbucket(r["instrument_type"], r["product_type"], r["mv"]), axis=1)
    instruments_df["investment_bucket"] = instruments_df.apply(
        lambda r: _invbucket(r["instrument_type"], r["product_type"], r["mv"]), axis=1)

    # ── sourcing_rationale (Pass 3c): why is this Amber/Red holding still held? ─
    # Pool varies by instrument_type x product_type so the narrative reads true to
    # the underlying vehicle. Only assigned to Amber + Red holdings; Green left blank.
    _SOURCING_RATIONALES = {
        ("Fund Investment",   "Private"): [
            "Top-quartile IRR manager; quarterly NAV cycle accepted at IC.",
            "Strategic GP relationship; look-through agreement in renewal.",
            "Long-vintage fund — disclosure tightens as positions exit.",
            "Specialist sector exposure unavailable in more transparent vehicles.",
        ],
        ("Co-investment",     "Private"): [
            "Co-invest alongside top-tier GP — disclosure governed by side letter.",
            "One-off deal with attractive entry economics; reduced reporting accepted.",
            "Strategic allocation approved at IC; full disclosure planned post-close.",
        ],
        ("Direct Investment", "Private"): [
            "Direct stake in private company; quarterly board pack is the disclosure cadence.",
            "Long-dated infrastructure asset; annual independent valuation.",
            "Real-asset holding — third-party valuer constraints limit look-through.",
        ],
        ("Mandate",           "Public"): [
            "Separately-managed account — custodian provides month-end positions only.",
            "Custom mandate; daily look-through pending custodian system upgrade.",
        ],
        ("Mandate",           "Private"): [
            "Mandate-style allocation to private credit; quarterly book provided.",
            "Strategic mandate with named manager; SLA refresh in progress.",
        ],
        ("Fund Investment",   "Public"): [
            "Commingled fund — monthly transparency report meets policy.",
            "ETF wrapper — daily holdings via custodian feed (data plumbing pending).",
        ],
        ("Direct Investment", "Public"): [
            "Direct holding; transparency limited by exchange-disclosure rules.",
        ],
        ("Co-investment",     "Public"): [
            "Public co-invest; disclosure on standard issuer cadence.",
        ],
    }
    def _assign_rationale(itype, ptype, tier, inst_id):
        if tier == "Green": return ""
        pool = _SOURCING_RATIONALES.get((itype, ptype), [])
        if not pool: return ""
        h = sum(ord(c) for c in str(inst_id)) % len(pool)
        return pool[h]
    instruments_df["sourcing_rationale"] = instruments_df.apply(
        lambda r: _assign_rationale(r["instrument_type"], r["product_type"], r["tier"], r["instrument_id"]),
        axis=1,
    )

    # Per-(instrument, missing_field) age in days — synthetic but deterministic.
    # Drives the "average days missing" stat in the Action Plans focus panel.
    def _field_ages(row):
        out = {}
        for f in row["missing_fields_list"]:
            h = sum(ord(c) for c in (str(row["instrument_id"]) + f)) % 180
            out[f] = 14 + h     # 14 to 193 days
        return out
    instruments_df["field_age_days"] = instruments_df.apply(_field_ages, axis=1)

    return (strategies_df, sub_strategies_df, portfolios_df, instruments_df,
            strat_agg, sub_strat_agg, history_df, sub_history_df, audit_df,
            action_items_df)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — Portfolio Overview
# ═══════════════════════════════════════════════════════════════════════════════

def _bullet_html(val, thr, scale_max, color):
    """Render one bullet bar (track + fill + threshold tick) as an HTML snippet."""
    fill_pct = min(val / scale_max, 1.0) * 100 if scale_max else 0
    tick_pct = min(thr / scale_max, 1.0) * 100 if scale_max else 0
    breach   = val > thr
    fill     = "var(--color-breach)" if breach else color
    return (
        '<div style="position:relative;width:100%;height:10px;background:var(--bg-track);border-radius:2px;">'
        f'<div style="position:absolute;left:0;top:0;height:100%;width:{fill_pct:.1f}%;background:{fill};border-radius:2px;"></div>'
        f'<div style="position:absolute;left:calc({tick_pct:.1f}% - 1px);top:-4px;width:2px;height:18px;background:var(--limit-tick);"></div>'
        '</div>'
    )

def _bullet_label(val, thr, util=False):
    breach = val > thr
    color  = "var(--breach-text)" if breach else "var(--text-muted)"
    weight = "500" if breach else "400"
    text   = (f"{val/thr*100:.0f}%" if thr > 0 else "—") if util else f"{val:.0f} / {thr:.0f}"
    return f'<div style="font-size:11px;color:{color};font-weight:{weight};text-align:right;white-space:nowrap;">{text}</div>'

def _status_dot(any_breach):
    if any_breach:
        return ('<div style="width:18px;height:18px;border-radius:50%;background:var(--investigate-bg);color:var(--investigate-text);'
                'font-size:11px;font-weight:500;display:flex;align-items:center;justify-content:center;">!</div>')
    return '<div style="width:8px;height:8px;border-radius:50%;background:var(--color-ok);margin-left:5px;"></div>'


# Pass 24.2: deterministic color palette for the cockpit "Key drivers" chips.
# Each distinct field name (e.g. "Company Name", "Critical Company Metric") gets
# its own color so the user can spot the same driver across multiple Strategies.
# Palette deliberately excludes greens/ambers/reds so it doesn't clash with the
# tier colour code.
TAG_PALETTE = [
    "#4F46E5",   # indigo
    "#9333EA",   # purple
    "#DB2777",   # pink
    "#0284C7",   # sky blue
    "#92400E",   # warm brown
    "#475569",   # slate
    "#BE185D",   # rose
]
def _tag_color(name: str) -> str:
    """Deterministic color for a given field-name string. Uses MD5 to get an
    even spread across the palette (a naive sum-of-ords clustered too many
    field names onto the same hue)."""
    import hashlib as _hashlib
    h = int(_hashlib.md5(str(name).encode("utf-8")).hexdigest(), 16)
    return TAG_PALETTE[h % len(TAG_PALETTE)]


def _cockpit_widget_html(row, expanded=True, show_investigate=True):
    """Cockpit widget. The entire card is a single clickable link that drills
    through to Strategy Detail (when show_investigate=True). All info is shown
    inline — no expand/collapse — because the panel-level toggle is gone.

    The `expanded` parameter is retained for back-compat but ignored: cards now
    always show their full body content.
    """
    any_breach = bool(row["any_breach"])

    red_util = row["red_utilisation"]   * 100
    amb_util = row["amber_utilisation"] * 100
    cum_util = row["cum_utilisation"]   * 100
    max_util = max(red_util, cum_util)

    # Three-state traffic light: OK (<80%), Alert (>=80%, not breaching), Breach (>100%)
    # Pass 26: subtle background tint so ALERT and BREACH stand out at a glance.
    # Pass 29: bg_tint reads from theme tokens so the soft tier tints flip
    # dark in dark mode (cream pastels were illegible on dark page chrome).
    if any_breach:
        pill_text, pill_color, light_color = "BREACH", "var(--breach-text)", "var(--color-breach)"
        border_color, border_width = "var(--color-red-fill)", "2px"
        bg_tint = "var(--tint-breach-bg)"
    elif max_util >= 80:
        pill_text, pill_color, light_color = "ALERT", "var(--alert-text)", "var(--color-alert)"
        border_color, border_width = "var(--alert-border)", "2px"
        bg_tint = "var(--tint-alert-bg)"
    else:
        pill_text, pill_color, light_color = "OK", "var(--ok-text)", "var(--color-ok)"
        border_color, border_width = "var(--color-ok)", "2px"
        bg_tint = "var(--bg-surface)"  # default surface — OK

    def _row(label, util, expo=None, limit=None):
        if util > 100:
            color, weight = "var(--breach-text)", "600"
        elif util >= 80:
            color, weight = "var(--color-alert)", "600"
        else:
            color, weight = "var(--text-primary)", "500"
        # Pass 14.2: hover reveals exposure / limit so users can see the source
        # numbers behind the utilisation %  (e.g. "2.0% / 17.0%" for an 11% util)
        if expo is not None and limit is not None:
            tip_attr = f' title="Exposure / Limit: {expo:.0f}% / {limit:.0f}%"'
            cursor   = "cursor:help;"
        else:
            tip_attr = ""
            cursor   = ""
        return (
            f'<div style="display:flex;justify-content:space-between;align-items:baseline;font-size:14px;padding:5px 0;">'
            f'<span style="color:var(--text-muted);">{label}</span>'
            f'<span class="kpi-number"{tip_attr} style="color:{color};font-size:22px;{cursor}">{util:.0f}<span style="font-size:14px;font-weight:600;opacity:0.7;">%</span></span>'
            f'</div>'
        )

    # Pass 24.5: container styling adapts to expanded state.
    #  expanded   → min-height:230px + flex column (so the breach footer docks to the bottom)
    #  collapsed  → tight padding, no min-height, so all 16 cards fit above the fold
    if expanded:
        container_style = (f'background:{bg_tint};border:{border_width} solid {border_color};'
                           f'border-radius:8px;padding:10px 12px;'
                           f'display:flex;flex-direction:column;min-height:230px;')
    else:
        # Pass 25.11: min-height on the collapsed state so cards with single-line
        # Strategy names match the height of cards whose names wrap to 2 lines
        # (e.g. EQ Developed Markets). 56px ≈ 2 lines of 14.5px/1.3 + 16px padding.
        container_style = (f'background:{bg_tint};border:{border_width} solid {border_color};'
                           f'border-radius:8px;padding:8px 12px;'
                           f'display:flex;flex-direction:column;justify-content:center;'
                           f'min-height:56px;')

    # Header row — always visible (name + status pill). The body (util rows +
    # footer + driver chip) is shown only when `expanded` is True, so the
    # Expand-all / Collapse-all button can compact the panel for fast scanning.
    # Blue ↗ arrow signals the widget is a clickable drill-through (standardised
    # affordance — same indicator as the exposure cards above).
    _click_arrow = (' <span style="color:var(--accent);font-size:13px;font-weight:700;vertical-align:middle;">\u2197</span>'
                    if show_investigate else "")
    # Pass 27.4: header gets a min-height equal to 2 lines of the strategy name
    # so cards with 2-line titles (EQ Developed Markets, RE Bricks and Mortar, etc.)
    # don't push the rest of the card down relative to 1-line titles. Everything
    # below (util rows, chips, status pill, breach footer) now starts at the same
    # Y position on every card in the grid.
    header = (
        f'<div style="display:flex;justify-content:space-between;align-items:center;'
        f'min-height:42px;">'
        f'<div style="font-size:14.5px;font-weight:600;color:var(--text-primary);line-height:1.3;min-width:0;flex:1 1 auto;">{row["name"]}{_click_arrow}</div>'
        f'<div style="display:flex;align-items:center;gap:5px;flex-shrink:0;margin-left:8px;">'
        f'<div style="width:8px;height:8px;border-radius:50%;background:{light_color};"></div>'
        f'<span title="Limit status: BREACH = utilisation > 100%, ALERT = 80 to 100%, OK = < 80%. Measures policy compliance against this Strategy&#8217;s own Red and Amber limits." '
        f'style="font-size:11.5px;color:{pill_color};font-weight:800;letter-spacing:0.06em;cursor:help;">{pill_text}</span>'
        f'</div></div>'
    )
    # Pass 25.4: render short driver-of-gap tag chips (UPC, fund metrics, T&Cs etc.)
    # with stable per-tag colors via _tag_color() hash. Same chip text always gets
    # the same color across strategies so the user can spot recurring drivers.
    # Status pill below the chip row.
    _chips_list = row.get("driver_chips", []) or []
    _status     = str(row.get("action_status", "") or "").strip()
    # Pass 28.5 / 29: short pill format "Action Plan: <STATE>". Colours now
    # come from theme tokens so they flip between cream and dark modes.
    # Pass 29.20: drop "Action Plan:" prefix — the surrounding "Action Status"
    # header already supplies the noun, so the pill becomes just the state
    # (e.g. "IN PROGRESS" after the CSS uppercase transform).
    _STATUS_DISPLAY = {
        "No initiative":  ("TBD",         "var(--status-rec-fg)"),
        "Planned / TBD":  ("TBD",         "var(--status-rec-fg)"),
        "In progress":    ("In Progress", "var(--status-prog-fg)"),
        "Completed":      ("Completed",   "var(--status-done-fg)"),
    }
    _disp_status, _status_color = _STATUS_DISPLAY.get(_status, ("", "var(--text-muted)"))

    if isinstance(_chips_list, list) and len(_chips_list) > 0:
        _chips_html = "".join(
            f'<span style="display:inline-block;border:1px solid {_tag_color(c)};color:{_tag_color(c)};'
            f'background:transparent;padding:2px 8px;border-radius:10px;font-size:11px;'
            f'font-weight:600;margin:0 4px 4px 0;white-space:nowrap;">{c}</span>'
            for c in _chips_list[:4]
        )
    else:
        _chips_html = ('<span style="font-size:11.5px;color:var(--text-subtle);font-style:italic;">'
                       'No driver recorded.</span>')

    if _disp_status:
        _status_pill = (
            f'<div style="margin-top:4px;font-size:10.5px;letter-spacing:0.04em;'
            f'text-transform:uppercase;font-weight:700;color:{_status_color};">'
            f'\u2022 {_disp_status}</div>'
        )
    else:
        _status_pill = ""

    _drivers_block = (
        f'<div style="margin-top:10px;padding-top:8px;border-top:1px solid var(--border-default);">'
        f'<div>{_chips_html}</div>'
        f'{_status_pill}'
        f'</div>'
    )

    if expanded:
        # Pass 25.5: layout = util rows + chips-only block (flex:1) + bottom-docked
        # status pill + breach-count footer. This aligns the status pill at the
        # same vertical position on every widget regardless of chip wrap.

        # The _drivers_block as built above already includes chips + status pill,
        # but for bottom-alignment we want to split them. Use chips-only here.
        _chips_only_block = (
            f'<div style="margin-top:10px;padding-top:8px;border-top:1px solid var(--border-default);">'
            f'<div>{_chips_html}</div>'
            f'</div>'
        )

        body = (
            f'<div style="margin-top:10px;padding-top:8px;border-top:1px solid var(--border-default);'
            f'flex:1;display:flex;flex-direction:column;">'
            f'{_row("Red util %",   red_util, float(row.get("Red_pct", 0))*100, float(row.get("threshold_red", 0))*100)}'
            f'{_row("Amber + Red util %", cum_util, float(row.get("cum_pct", 0))*100, float(row.get("threshold_cum", 0))*100)}'
            f'{_chips_only_block}'
            # Bottom-docked: status pill + breach-count footer
            f'<div style="margin-top:auto;padding-top:8px;">'
            f'  {_status_pill}'
            f'  <div style="margin-top:6px;padding-top:6px;border-top:1px dashed var(--border-default);font-size:12px;color:var(--text-muted);line-height:1.45;">'
            f'    No. of breaches past 1 year: <b style="color:var(--text-primary);">{int(row.get("breaches_last_12mo", 0))}</b>'
            f'  </div>'
            f'</div>'
            f'</div>'
        )
    else:
        # Pass 24.5b: collapsed view shows just the header (name + status pill).
        # The status pill alone (OK / ALERT / BREACH) is enough for triage.
        body = ""
    inner = header + body

    if show_investigate:
        try:
            target_group = str(row["strategy_name"])
        except (KeyError, IndexError):
            target_group = str(row["name"])
        if any_breach:
            _bp = []
            if bool(row.get("red_breach", False)): _bp.append(("Red",   float(row.get("red_variance", 0))))
            if bool(row.get("cum_breach", False)): _bp.append(("Amber", float(row.get("cum_variance", 0))))
            _bp.sort(key=lambda t: -t[1])
            focus_tier = _bp[0][0] if _bp else "Amber"
        else:
            focus_tier = "Amber"
        # Pass 27: card click sets ?preview=<sub_name>. The Total Portfolio page
        # picks that up and opens an st.dialog with the enlarged preview card.
        # From inside the dialog, an "Open full Strategy Detail" button drills
        # through to the Strategy Detail page (keeping the previous flow alive).
        sub_name = str(row.get("sub_strategy_name") or row.get("name") or "")
        href = f"?preview={quote(sub_name)}{_theme_qs()}"
        return (
            f'<a class="cockpit-link" href="{href}" target="_self" '
            f'aria-label="Preview {row["name"]}" '
            f'style="{container_style}">'
            f'{inner}'
            f'</a>'
        )
    return f'<div class="cockpit-static" style="{container_style}">{inner}</div>'




def _total_exposure_card_html(label, util_pct, value_pct, limit_pct, color, breach, href=None, tooltip=None):
    """Top-row exposure card. Two-column layout (pass 7.2): label + shorter
    bar on the left, status pill + util% + limit% stacked on the right.
    Bar fill is accent-blue at neutral util so it's clearly visible (was a
    near-invisible blue-grey before)."""
    if breach:
        fill_color = "var(--color-red-fill)"
    elif util_pct >= 80:
        fill_color = "var(--color-amber-fill)"
    else:
        fill_color = "var(--accent)"      # strong blue — clearly visible
    fill_w     = min(util_pct, 100.0)
    used_color = "var(--breach-text)" if breach else "var(--text-primary)"
    overshoot_badge = (
        f' <span style="color:var(--breach-text);font-weight:500;">· +{util_pct - 100:.0f}% over limit</span>'
        if breach else ""
    )
    info = (f' <span title="{tooltip}" style="color:var(--text-subtle);cursor:help;font-size:13px;">ⓘ</span>'
            if tooltip else "")
    if breach:
        st_text, st_dot, st_color = "BREACH", "var(--color-breach)", "var(--breach-text)"
        border_color = "var(--color-red-fill)"
    elif util_pct >= 80:
        st_text, st_dot, st_color = "ALERT", "var(--color-alert)", "var(--alert-text)"
        border_color = "var(--alert-border)"
    else:
        st_text, st_dot, st_color = "OK", "var(--color-ok)", "var(--ok-text)"
        border_color = "var(--color-ok)"
    click_hint = (' <span style="color:var(--accent);font-size:13px;font-weight:700;">↗</span>' if href else "")
    inner = (
        f'<div class="exposure-card" style="background:var(--bg-surface);border:2px solid {border_color};'
        f'border-radius:8px;padding:14px 18px;display:flex;align-items:center;gap:24px;">'
        # Left column: label + shorter bar
        f'<div style="flex:1 1 auto;min-width:0;">'
        f'<div style="font-size:18px;font-weight:700;color:var(--text-primary);margin-bottom:8px;line-height:1.2;">{label}{info}{click_hint}</div>'
        f'<div style="position:relative;height:8px;background:var(--bg-track);border-radius:3px;max-width:280px;">'
        f'<div style="position:absolute;left:0;top:0;height:100%;width:{fill_w:.1f}%;background:{fill_color};border-radius:3px;transition:width 0.25s ease;"></div>'
        f'<div style="position:absolute;right:-1px;top:-3px;width:2px;height:14px;background:var(--limit-tick);"></div>'
        f'</div>'
        f'</div>'
        # Right column: status pill + util% + limit% stacked, right-aligned
        f'<div style="flex:0 0 auto;text-align:right;display:flex;flex-direction:column;gap:4px;align-items:flex-end;">'
        f'<div style="display:flex;align-items:center;gap:6px;">'
        f'<div style="width:8px;height:8px;border-radius:50%;background:{st_dot};"></div>'
        f'<span style="font-size:13px;font-weight:800;letter-spacing:0.06em;color:{st_color};">{st_text}</span>'
        f'</div>'
        f'<div style="font-size:13px;color:{used_color};font-variant-numeric:tabular-nums;line-height:1.2;">'
        f'<span class="kpi-number" style="font-size:22px;">{util_pct:.0f}<span style="font-size:13px;font-weight:600;opacity:0.7;">%</span></span> <span class="metric-label">used</span></div>'
        f'<div style="font-size:12px;color:var(--text-muted);font-variant-numeric:tabular-nums;line-height:1.2;">'
        f'<span style="color:var(--text-primary);font-weight:500;">{value_pct:.0f}%</span> / {limit_pct:.0f}% limit{overshoot_badge}</div>'
        f'</div>'
        f'</div>'
    )
    if href:
        return f'<a href="{href}" class="card-link" target="_self">{inner}</a>'
    return inner

# Neutral contributor palette for the Breakdown panel. Deliberately NOT red/amber/green
# so it cannot be confused with the Red/Amber tier semantics used by exposure cards.
# Pass 10.2: gradient compressed to all-dark range so WHITE text works on every
# segment (WCAG AA verified). Visual rank still encoded (darkest = top contributor).
_BREAKDOWN_GRADIENT   = ["#172554", "#1E3A8A", "#1E40AF", "#1D4ED8", "#2563EB"]  # blue 950→600
_BREAKDOWN_AMBER_ONLY = ["#2E1065", "#4C1D95", "#5B21B6", "#6D28D9", "#7C3AED"]  # violet 950→700

# Map kept for the 3 Focus-on values; same neutral ramp for the two limit-relevant
# cuts (Red, Amber=R+A) and a separate purple ramp for the analysis-only "Amber only".
TIER_PALETTES = {
    "Red":        _BREAKDOWN_GRADIENT,
    "Amber":      _BREAKDOWN_GRADIENT,
    "Amber only": _BREAKDOWN_AMBER_ONLY,
}
OTHERS_COLOR = "#475569"  # slate-600 — neutral grey, dark enough for white text (was slate-400)

TIER_TOOLTIPS = {
    # Parallel format across all three: "Tier" describes the transparency/risk
    # characteristic; "Limit Metric" describes what the displayed figure measures.
    # Disambiguates the overloaded "Amber" label (tier vs combined limit).
    "Red":        "Tier: Red \u2014 Poor systematic risk, the least transparent tier.\nLimit Metric: Figures show Red utilisation against the Red limit.",
    "Amber":      "Tier: Amber \u2014 Good understanding of systematic risk but no name-level information.\nLimit Metric: Figures show cumulative utilisation against the cumulative limit (Red + Amber).",
    "Amber only": "Tier: Amber only \u2014 Pure Amber tier in isolation.\nLimit Metric: Figures show the Amber tier alone (no policy limit attached).",
}


def _build_stacked_bar(segments, palette, total_pct):
    """Single horizontal bar whose width represents total_pct.
    Every top-N segment gets at least its percentage as an inline label;
    the "+ N others" segment shows its label only when wide enough.
    Hovering any segment reveals the full label via the title attribute.
    """
    if total_pct <= 0:
        return ('<div style="height:36px;background:var(--bg-surface);border:1px solid var(--border-default);'
                'border-radius:4px;display:flex;align-items:center;justify-content:center;'
                'color:var(--text-subtle);font-size:11px;">No contributions</div>')

    html = ('<div style="display:flex;height:36px;border:1px solid var(--border-default);'
            'border-radius:4px;overflow:hidden;">')
    for i, s in enumerate(segments):
        seg_pct   = s["contrib_pct"] / total_pct * 100 if total_pct > 0 else 0
        is_others = s.get("is_others", False)
        color     = OTHERS_COLOR if is_others else palette[min(i, len(palette) - 1)]
        # Palette is now all-dark (Pass 10.2) so white text passes WCAG AA on
        # every segment — no per-segment colour flips needed.
        txt_color = "#FFFFFF"

        # Decide inline label text + font size.
        if is_others:
            # "+ N others" segment: only label when it can fit a readable chunk
            label    = f'{s["label"]} \u00b7 {s["contrib_pct"]:.2f}%' if seg_pct >= 12 else ""
            font_sz  = "11px"
        else:
            # Top-N segment: ALWAYS show at least the contribution; expand to full label if wide
            if seg_pct >= 15:
                label   = f'{s["label"]} \u00b7 {s["contrib_pct"]:.2f}%'
                font_sz = "11px"
            elif seg_pct >= 9:
                label   = f'{s["contrib_pct"]:.2f}%'
                font_sz = "11px"
            else:
                label   = f'{s["contrib_pct"]:.2f}%'
                font_sz = "10px"

        title_attr = f'{s["label"]} \u00b7 {s["contrib_pct"]:.2f}%'
        html += (
            f'<div title="{title_attr}" style="width:{seg_pct:.2f}%;background:{color};'
            f'display:flex;align-items:center;justify-content:center;padding:0 4px;'
            f'font-size:{font_sz};font-weight:500;color:{txt_color};overflow:hidden;'
            f'white-space:nowrap;">{label}</div>'
        )
    html += '</div>'
    return html


def _build_legend(segments, palette):
    parts = []
    for i, s in enumerate(segments):
        color = OTHERS_COLOR if s.get("is_others") else palette[min(i, len(palette)-1)]
        parts.append(
            f'<span><span style="display:inline-block;width:8px;height:8px;background:{color};'
            f'border-radius:1px;margin-right:5px;vertical-align:middle;"></span>'
            f'{s["label"]} {s["contrib_pct"]:.2f}%</span>'
        )
    return ('<div style="display:flex;flex-wrap:wrap;gap:14px;font-size:13px;color:var(--text-muted);'
            'margin-top:10px;margin-bottom:16px;">' + ' '.join(parts) + '</div>')


def _breakdown_row_html(label, contrib_pct, share_pct, count, max_contrib, tier_color, muted=False):
    """One row of the Breakdown panel.
    contrib_pct = this bucket\'s contribution to the top-panel tier % (e.g. 0.85 means 0.85pp of 1.23%).
    share_pct   = this bucket\'s share within the tier total (sums to 100% across rows).
    """
    bar_width = (contrib_pct / max_contrib * 100) if max_contrib > 0 else 0
    label_color  = "var(--text-subtle)" if muted else "var(--text-primary)"
    label_weight = "400"     if muted else ("500" if share_pct >= 50 else "400")
    val_color    = "var(--text-subtle)" if muted else "var(--text-primary)"
    return (
        f'<div style="display:grid;grid-template-columns:130px 1fr 140px 50px;gap:10px;align-items:center;padding:9px 0;border-bottom:1px solid var(--border-default);font-size:13px;">'
        f'<div style="color:{label_color};font-weight:{label_weight};overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="{label}">{label}</div>'
        f'<div style="position:relative;height:10px;background:var(--bg-track);border-radius:2px;">'
        f'<div style="position:absolute;left:0;top:0;height:100%;width:{bar_width:.1f}%;background:{tier_color};border-radius:2px;"></div>'
        f'</div>'
        f'<div style="font-size:12px;text-align:right;color:{val_color};font-variant-numeric:tabular-nums;"><span style="font-weight:500;">{contrib_pct:.0f}%</span> <span style="color:var(--text-subtle);">\u00b7 {share_pct:.0f}% of tier</span></div>'
        f'<div style="font-size:11px;text-align:right;color:var(--text-muted);font-variant-numeric:tabular-nums;">{count}</div>'
        f'</div>'
    )


_RATING_COLORS = {
    "High":   ("var(--color-ok)",       "#FFFFFF"),
    "Medium": ("#E67E22",                "#FFFFFF"),
    "Low":    ("var(--color-red-fill)", "#FFFFFF"),
}

def _rating_badge(rating: str, green_pct=None) -> str:
    """Self-labelled transparency pill. Reads 'Transparency: HIGH' so it can't be
    confused with the policy-limit traffic light (OK / ALERT / BREACH) sitting
    on the right side of the same widget."""
    if not rating: return ""
    bg, fg = _RATING_COLORS.get(rating, ("var(--text-muted)", "#FFFFFF"))
    title = ("Transparency rating = % of this Strategy in Green (transparent) tier. "
             "High = 80% or more Green; Medium = 50-80%; Low = under 50%. "
             "This rates ABSOLUTE transparency and is independent of the policy limit.")
    if green_pct is not None:
        try: title += f" Current: {float(green_pct):.0f}% Green."
        except Exception: pass
    return (f'<span title="{title}" style="background:{bg};color:{fg};padding:2px 9px;'
            f'border-radius:10px;font-size:10px;font-weight:600;letter-spacing:0.04em;'
            f'text-transform:uppercase;margin-left:10px;vertical-align:middle;cursor:help;">'
            f'Transparency: {rating}</span>')

def _reason_chip(reason: str) -> str:
    if not reason: return ""
    return (f'<div style="display:inline-block;background:var(--bg-track);color:var(--text-muted);'
            f'padding:3px 9px;border-radius:4px;font-size:11px;margin-top:8px;'
            f'border:1px solid var(--border-default);"><b>Driver:</b> {reason}</div>')


def _section_band(title, subtitle=""):
    """A labelled section divider with a coloured left accent."""
    sub = (f'<div style="font-size:13px;color:var(--text-muted);margin-top:2px;">{subtitle}</div>'
           if subtitle else "")
    return (
        f'<div style="border-left:3px solid var(--section-band);padding-left:12px;margin:10px 0 16px;">'
        f'<div style="font-size:20px;font-weight:600;color:var(--text-primary);letter-spacing:0.02em;">{title}</div>'
        f'{sub}</div>'
    )


def _ai_observations_html(strat_agg, sub_strat_agg, portfolios_df, history_df, sub_history_df, instruments_df):
    """A.I. Observations (Pass 24.3). Two buckets: always-visible (Portfolio
    overview + Top contributors — sized to match the stacked exposure cards
    on the left) and collapsed (Watch list + Active breaches + Biggest
    leverage opportunity — behind a chevron summary). Top improvers removed."""
    always_sections = []
    more_sections   = []

    # ── Portfolio overview (always-visible) ──────────────────────────────────
    if history_df is not None and len(history_df) and "date" in history_df.columns:
        def _aw(g):
            mv = g["mv"].sum()
            return (g["non_transparent_pct"] * g["mv"]).sum() / mv if mv > 0 else 0
        hagg = (history_df.groupby("date").apply(_aw).reset_index(name="ntp").sort_values("date"))
        hagg["ntp"] = hagg["ntp"] * 100
        if len(hagg) >= 2:
            cur  = float(hagg.iloc[-1]["ntp"])
            prev = float(hagg.iloc[-2]["ntp"])
            delta = cur - prev
            cur_green = 100 - cur
            if abs(delta) < 0.05:
                direction, arrow_color, arrow = "held steady", "var(--text-muted)", "\u2192"
            elif delta < 0:
                direction, arrow_color, arrow = "improved", "var(--color-ok)", "\u25BC"
            else:
                direction, arrow_color, arrow = "worsened", "var(--breach-text)", "\u25B2"
            if direction == "held steady":
                lead = (f'Intransparency exposure held steady month-over-month '
                        f'(<span class="kpi-number">{cur:.0f}%</span> vs <span class="kpi-number">{prev:.0f}%</span> last month).')
            else:
                lead = (f'Intransparency exposure {direction} by '
                        f'<span class="kpi-number" style="color:{arrow_color};font-size:15px;">{arrow} {abs(delta):.0f}%</span>'
                        f' month-over-month (<span class="kpi-number">{cur:.0f}%</span> vs '
                        f'<span class="kpi-number">{prev:.0f}%</span> last month).')
            always_sections.append(
                f'<div style="margin-bottom:4px;">'
                f'<div class="metric-label" style="margin-bottom:2px;">Portfolio overview</div>'
                f'<div style="font-size:14px;color:var(--text-soft);line-height:1.5;">'
                f'{lead}'
                f'</div></div>'
            )

    # ── Per-strategy detractors → Watch list (collapsed) ─────────────────────
    if sub_history_df is not None and len(sub_history_df) and "date" in sub_history_df.columns:
        dates = sorted(sub_history_df["date"].unique())
        if len(dates) >= 2:
            latest_d, prev_d = dates[-1], dates[-2]
            cur_s  = sub_history_df[sub_history_df["date"] == latest_d].set_index("sub_strategy_id")["non_transparent_pct"]
            prev_s = sub_history_df[sub_history_df["date"] == prev_d].set_index("sub_strategy_id")["non_transparent_pct"]
            strat_delta = ((cur_s - prev_s) * 100).dropna().sort_values()
            name_map = dict(zip(sub_strat_agg["sub_strategy_id"], sub_strat_agg["sub_strategy_name"]))
            detractors = strat_delta.tail(2).iloc[::-1]
            dpart = []
            for sid, d in detractors.items():
                if d > 0.05:
                    dpart.append(f'<b>{name_map.get(sid, sid)}</b> (<span class="kpi-number" style="color:var(--breach-text);">{d:+.2f}%</span>)')
            if dpart:
                more_sections.append(
                    f'<div style="margin-bottom:6px;">'
                    f'<div class="metric-label" style="margin-bottom:2px;color:var(--breach-text);">Watch list</div>'
                    f'<div style="font-size:14px;color:var(--text-soft);line-height:1.5;">'
                    f'Transparency deteriorated most in {", ".join(dpart)}.'
                    f'</div></div>'
                )

    # ── Top contributors (always-visible) ────────────────────────────────────
    ar_inst = portfolios_df[portfolios_df["tier"].isin(["Amber","Red"])]
    if len(ar_inst):
        _tot_mv  = float(portfolios_df["mv"].sum())
        _by_strat = (ar_inst.groupby("sub_strategy_name")["mv"].sum() / _tot_mv * 100
                     if _tot_mv > 0 else None)
        if _by_strat is not None and len(_by_strat):
            _top = _by_strat.sort_values(ascending=False).head(4)
            _bits = [
                f'<b>{name}</b> (<span class="kpi-number" style="color:var(--breach-text);">{v:.0f}%</span>)'
                for name, v in _top.items() if v > 0.005
            ]
            if _bits:
                always_sections.append(
                    f'<div style="margin-bottom:6px;">'
                    f'<div class="metric-label" style="margin-bottom:2px;color:var(--breach-text);">Top contributors</div>'
                    f'<div style="font-size:14px;color:var(--text-soft);line-height:1.5;">'
                    f'The biggest drivers of current Amber + Red exposure are '
                    f'{", ".join(_bits)}.'
                    f'</div></div>'
                )

    # ── Active breaches + initiative status (collapsed) ────────────────────
    # Pass 25.6: surface the spreadsheet narrative — total breaches, how many
    # have no current initiative, and call out the highest-impact strategy that
    # IS being actively remediated (Infra Active for the meeting demo).
    breaching = sub_strat_agg[sub_strat_agg["any_breach"]]
    if len(breaching) > 0:
        n_total = len(breaching)
        in_prog  = breaching[breaching["action_status"] == "In progress"]
        # Pass 28.4: "No initiative" + "Planned / TBD" both fold into the
        # Kanban "Recommended Action Plan" bucket — collapse them in the
        # narrative too so the count reconciles with the Action Tracker tab.
        rec_plan = breaching[breaching["action_status"].isin(
            ["No initiative", "Planned / TBD"]
        )]
        # Pass 29.11: account for the third bucket — breaching strategies whose
        # action status is "N/A" (closed sleeve, no remediation needed). Without
        # this the narrative read "11 in breach. 3 In Progress. 7 need a plan"
        # which didn't add up (3+7=10, not 11).
        na_status = breaching[~breaching["action_status"].isin(
            ["In progress", "No initiative", "Planned / TBD"]
        )]

        # In Progress first (positive signal), Recommended Action Plan last.
        body_b = (
            f'<b>{n_total}</b> {"strategy" if n_total==1 else "strategies"} in breach.'
        )
        if len(in_prog) > 0:
            ip_names = ", ".join(f'<b>{n}</b>' for n in in_prog["sub_strategy_name"].tolist())
            body_b += (
                f' <b style="color:var(--status-prog-fg);">{len(in_prog)}</b> '
                f'{"strategy" if len(in_prog)==1 else "strategies"} '
                f'<b>In Progress</b>: {ip_names}.'
            )
        if len(rec_plan) > 0:
            body_b += (
                f' <b style="color:var(--status-rec-fg);">{len(rec_plan)}</b> '
                f'{"needs" if len(rec_plan)==1 else "need"} a '
                f'<b>Recommended Action Plan</b>.'
            )
        if len(na_status) > 0:
            na_names = ", ".join(f'<b>{n}</b>' for n in na_status["sub_strategy_name"].tolist())
            body_b += (
                f' <span style="color:var(--text-muted);"><b>{len(na_status)}</b> '
                f'marked <b>N/A</b> ({na_names} — closed sleeve / no remediation needed).</span>'
            )

        # Pass 27.5: Active breaches is the most actionable summary — keep it
        # always-visible. Watch list + Biggest leverage opportunity remain
        # behind the chevron.
        always_sections.append(
            f'<div style="margin-bottom:4px;">'
            f'<div class="metric-label" style="margin-bottom:2px;color:var(--breach-text);">Active breaches</div>'
            f'<div style="font-size:14px;color:var(--text-soft);line-height:1.5;">{body_b}</div></div>'
        )

    # ── Biggest leverage opportunity (collapsed) ─────────────────────────────
    ar = instruments_df[instruments_df["tier"].isin(["Amber","Red"])]
    if len(ar):
        field_counts = {}
        for _, r in ar.iterrows():
            for f in (r.get("missing_fields_list") or []):
                field_counts[f] = field_counts.get(f, 0) + 1
        if field_counts:
            top_field, top_n = max(field_counts.items(), key=lambda kv: kv[1])
            _tot_port_mv = float(instruments_df["mv"].sum())
            _affected_mv = float(ar[ar["missing_fields_list"].apply(
                lambda lst: top_field in (lst or []))]["mv"].sum())
            _impact_pct = (_affected_mv / _tot_port_mv * 100) if _tot_port_mv > 0 else 0.0
            more_sections.append(
                f'<div style="margin-bottom:0;">'
                f'<div class="metric-label" style="margin-bottom:2px;color:var(--accent);">Biggest leverage opportunity</div>'
                f'<div style="font-size:14px;color:var(--text-soft);line-height:1.5;">'
                f'<b>{top_field}</b> \u2014 missing on <span class="kpi-number">{top_n}</span> instruments. '
                f'Resolving it could reduce Amber + Red exposure by up to '
                f'<b style="color:var(--accent);"><span class="kpi-number">{_impact_pct:.0f}%</span></b>.'
                f'</div></div>'
            )

    # ── Build body: always-visible + collapsed details wrapper ───────────────
    if not always_sections and not more_sections:
        body = '<div style="font-size:14px;color:var(--text-muted);">No notable observations this period.</div>'
    else:
        body = "".join(always_sections)
        if more_sections:
            more_count = len(more_sections)
            tooltip = f"Show {more_count} more observation" + ("" if more_count == 1 else "s")
            body += (
                # Tight chevron: tiny font + line-height:0 so the row collapses
                # to nearly zero height. Negative margin on the inner div pulls
                # the next section up to sit flush with the chevron.
                f'<details class="ai-more" style="margin:0;padding:0;">'
                f'<summary title="{tooltip}" style="cursor:pointer;list-style:none;'
                f'color:var(--accent);user-select:none;display:inline-flex;align-items:center;'
                f'margin:0;padding:0;font-size:12px;line-height:0;height:14px;">'
                f'<span class="ai-chevron" style="display:inline-block;transition:transform 0.18s ease;font-weight:700;">\u25B8</span>'
                f'</summary>'
                f'<div style="margin-top:-2px;">{"".join(more_sections)}</div>'
                f'</details>'
            )

    return (
        # Pass 29.13: tightened panel padding-top (14→10) and header bottom
        # gap (8→6) to bring the AI panel height down by ~6px so it aligns
        # with the stacked exposure cards on the left.
        f'<div style="background:var(--bg-surface);'
        f'border:1px solid var(--border-default);border-left:4px solid var(--accent);'
        f'border-radius:8px;padding:10px 20px 4px 20px;margin-bottom:24px;'
        f'display:flex;flex-direction:column;min-height:215px;height:100%;'
        f'box-sizing:border-box;">'
        f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">'
        f'<div style="font-size:11px;font-weight:800;color:var(--accent);letter-spacing:0.14em;text-transform:uppercase;">A.I. Observations</div>'
        f'<div style="background:var(--accent);color:#FFFFFF;font-size:9px;font-weight:700;padding:2px 7px;border-radius:8px;letter-spacing:0.06em;">AUTO</div>'
        f'<div style="flex:1;height:1px;background:var(--border-default);"></div>'
        f'<div style="font-size:11px;color:var(--text-subtle);">Generated from current data</div>'
        f'</div>'
        f'<style>'
        f'details.ai-more > summary::-webkit-details-marker {{ display:none; }}'
        f'details.ai-more[open] > summary .ai-chevron {{ transform: rotate(90deg); }}'
        f'</style>'
        f'{body}'
        f'</div>'
    )



def _gauge_bar_html(label: str, current_pct: float,
                    exposure_pct: float = None, limit_pct: float = None) -> str:
    """Pass 27.1: gauge bar capped at 100% — bar shows OK (0-80%) + ALERT
    (80-100%) zones only. If util > 100% the indicator pins to the right edge;
    the number above the bar still shows the actual util (e.g. 106%). Status
    word in {OK / Alert / Breach}.

    Pass 29.19: if exposure_pct + limit_pct are supplied, render a small
    "X.X% / Y.Y% limit" sub-line directly under the right-aligned util % so
    the user can see what's actually being measured against the limit without
    leaving the popup."""
    pos_pct = max(0.0, min(current_pct, 100.0))
    # Pass 29: status text + bar zones + indicator all read from theme tokens.
    if current_pct > 100:
        status, color = "Breach", "var(--breach-text)"
    elif current_pct >= 80:
        status, color = "Alert",  "var(--alert-text)"
    else:
        status, color = "OK",     "var(--ok-text)"
    # Zones on the 0-100 bar:
    #   OK     0 -> 80%   (var(--gauge-ok-fill))
    #   ALERT  80 -> 100% (var(--gauge-alert-fill))
    bar_bg = (
        "linear-gradient(to right, "
        "var(--gauge-ok-fill) 0%, var(--gauge-ok-fill) 80%, "
        "var(--gauge-alert-fill) 80%, var(--gauge-alert-fill) 100%)"
    )
    # Pass 29.19: optional exposure / limit sub-line beneath the util %.
    if exposure_pct is not None and limit_pct is not None:
        sub_html = (
            f'<div style="font-size:10px;font-weight:600;color:var(--text-subtle);'
            f'font-variant-numeric:tabular-nums;line-height:1.2;margin-top:1px;'
            f'text-align:right;letter-spacing:0.02em;">'
            f'{exposure_pct:.0f}% / {limit_pct:.0f}% limit'
            f'</div>'
        )
    else:
        sub_html = ""
    return (
        f'<div style="margin-bottom:14px;">'
        f'<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;">'
        f'<div style="padding-top:2px;">'
        f'<span style="font-size:14px;font-weight:800;color:var(--text-primary);">{label}</span>'
        f'<span style="font-size:13px;font-weight:700;color:{color};margin-left:8px;">{status}</span>'
        f'</div>'
        f'<div style="display:flex;flex-direction:column;align-items:flex-end;">'
        f'<div style="font-size:18px;font-weight:800;color:{color};font-variant-numeric:tabular-nums;line-height:1;">{current_pct:.0f}%</div>'
        f'{sub_html}'
        f'</div>'
        f'</div>'
        f'<div style="position:relative;height:18px;border-radius:4px;background:{bar_bg};border:1px solid var(--border-default);">'
        f'<div style="position:absolute;top:-2px;bottom:-2px;left:80%;width:0;border-left:1px dashed var(--text-subtle);"></div>'
        f'<div style="position:absolute;top:-5px;bottom:-5px;left:{pos_pct}%;width:4px;background:var(--gauge-indicator);border-radius:2px;transform:translateX(-50%);box-shadow:0 0 0 1px var(--gauge-indicator-halo);"></div>'
        f'</div>'
        f'<div style="position:relative;height:14px;font-size:10px;color:var(--text-subtle);margin-top:4px;letter-spacing:0.04em;text-transform:uppercase;font-weight:600;">'
        f'<span style="position:absolute;left:0;">0%</span>'
        f'<span style="position:absolute;left:80%;transform:translateX(-50%);">80%</span>'
        f'<span style="position:absolute;right:0;">100%</span>'
        f'</div>'
        f'</div>'
    )

def _render_preview_dialog(row, sub_history_df):
    """Pass 27: enlarged-card preview opened from a cockpit click. Built with
    @st.dialog so it appears as a real modal with the X close handled by
    Streamlit. The 'Open full Strategy Detail' button drills through to the
    Strategy Detail page using the same query-param flow that the cards used
    to do directly."""
    sub_name = str(row.get("sub_strategy_name") or row.get("name") or "")
    @st.dialog(f"📋  {sub_name}")
    def _dialog():
        # Pass 29.16: re-inject every theme token scoped to the dialog so the
        # popup is immune to whatever Streamlit Cloud does to the CSS cascade
        # inside @st.dialog. Local renders fine because the :root variables
        # inherit transparently, but on Cloud some elements ignored them and
        # rendered cream-mode colours mid-dark-mode dashboard.
        _t = _theme()
        _scoped_vars = ";".join(f"--{k}: {v}" for k, v in _t.items())
        st.markdown(
            f"<style>div[role='dialog'], [data-testid='stDialog'] "
            f"{{ {_scoped_vars}; }}</style>",
            unsafe_allow_html=True,
        )
        # ── Status pill in the header area ──────────────────────────────
        red_u = float(row.get("red_utilisation", 0)) * 100
        cum_u = float(row.get("cum_utilisation", 0)) * 100
        any_breach = bool(row.get("any_breach"))
        # Pass 29: state pill bg reads from theme tokens.
        if any_breach:
            state_label, state_bg, state_fg = "BREACH", "var(--tint-breach-bg)", "var(--breach-text)"
        elif max(red_u, cum_u) >= 80:
            state_label, state_bg, state_fg = "ALERT", "var(--tint-alert-bg)", "var(--alert-text)"
        else:
            state_label, state_bg, state_fg = "OK", "var(--tint-ok-bg)", "var(--ok-text)"
        sgroup = str(row.get("strategy_name", ""))
        st.markdown(
            f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">'
            f'<div style="font-size:13px;color:var(--text-soft);">Strategy Group: <b>{sgroup}</b></div>'
            f'<div style="background:{state_bg};color:{state_fg};border:1px solid {state_fg};'
            f'padding:4px 14px;border-radius:14px;font-size:12px;font-weight:800;'
            f'letter-spacing:0.06em;">{state_label}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        # ── Two Risk Posture gauges ────────────────────────────────────
        # Pass 29.19: surface exposure / limit % under each util gauge so the
        # user can read what's actually being measured against the limit.
        # The aggregate row uses uppercase "Red_pct" for the red exposure
        # fraction and "cum_pct" for amber+red; both are fractions of MV.
        # threshold_red / threshold_cum are also fractions.
        red_exp_pct  = float(row.get("Red_pct",       row.get("red_pct", 0.0))) * 100
        red_lim_pct  = float(row.get("threshold_red", 0.0)) * 100
        cum_exp_pct  = float(row.get("cum_pct",       0.0)) * 100
        cum_lim_pct  = float(row.get("threshold_cum", 0.0)) * 100
        st.markdown(
            _gauge_bar_html("Red Utilisation %", red_u,
                            exposure_pct=red_exp_pct, limit_pct=red_lim_pct),
            unsafe_allow_html=True,
        )
        st.markdown(
            _gauge_bar_html("Amber + Red Utilisation %", cum_u,
                            exposure_pct=cum_exp_pct, limit_pct=cum_lim_pct),
            unsafe_allow_html=True,
        )

        # ── Driver of gap ──────────────────────────────────────────────
        driver_text = str(row.get("breach_driver", "") or "").strip()
        chips_list  = row.get("driver_chips", []) or []
        if driver_text or chips_list:
            chips_html = "".join(
                f'<span style="display:inline-block;border:1px solid {_tag_color(c)};color:{_tag_color(c)};'
                f'background:transparent;padding:3px 10px;border-radius:10px;font-size:12px;'
                f'font-weight:600;margin:0 6px 6px 0;white-space:nowrap;">{c}</span>'
                for c in chips_list[:4]
            )
            st.markdown(
                f'<div style="margin-top:10px;padding:10px 14px;background:var(--bg-track);border-radius:6px;">'
                f'<div style="font-size:11px;font-weight:800;color:var(--text-muted);'
                f'text-transform:uppercase;letter-spacing:0.10em;margin-bottom:4px;">Driver of gap</div>'
                f'<div style="font-size:14px;color:var(--text-soft);margin-bottom:8px;">{driver_text or "—"}</div>'
                f'<div>{chips_html}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # ── Action status + plan text ─────────────────────────────────
        # Pass 28.5 / 29: short pill format "Action Plan: <STATE>" with
        # theme-aware colours.
        # Pass 29.20: drop "Action Plan:" prefix — the "Action Status" header
        # above the pill already supplies the noun, so the pill is now just
        # the state value on its own.
        status = str(row.get("action_status", "") or "")
        plan   = str(row.get("action_plan_text", "") or "")
        _STATUS_DISPLAY = {
            "No initiative":  ("TBD",         "var(--status-rec-fg)"),
            "Planned / TBD":  ("TBD",         "var(--status-rec-fg)"),
            "In progress":    ("In Progress", "var(--status-prog-fg)"),
            "Completed":      ("Completed",   "var(--status-done-fg)"),
        }
        disp_status, st_color = _STATUS_DISPLAY.get(status, ("—", "var(--text-muted)"))
        st.markdown(
            f'<div style="margin-top:10px;padding:10px 14px;background:var(--bg-track);border-radius:6px;">'
            f'<div style="font-size:11px;font-weight:800;color:var(--text-muted);'
            f'text-transform:uppercase;letter-spacing:0.10em;margin-bottom:4px;">Action status</div>'
            f'<div style="font-size:13px;font-weight:800;color:{st_color};text-transform:uppercase;'
            f'letter-spacing:0.06em;margin-bottom:6px;">• {disp_status}</div>'
            f'<div style="font-size:14px;color:var(--text-soft);line-height:1.55;">{plan or "—"}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # ── 12-month utilisation sparkline ────────────────────────────
        try:
            sid = row.get("sub_strategy_id")
            if sid and sub_history_df is not None and len(sub_history_df):
                hist = sub_history_df[sub_history_df["sub_strategy_id"] == sid].copy()
                if len(hist):
                    hist = hist.sort_values("date").tail(12).copy()
                    thr_r = float(row.get("threshold_red", 0))
                    thr_c = float(row.get("threshold_cum", 0))
                    # Pass 27.1: red_pct / amber_pct in sub_history_df are FRACTIONS
                    # (0-1). Divide by threshold (also fraction) and multiply by 100
                    # to get utilisation %. The previous /100 zeroed out the series.
                    hist["red_util"] = (hist["red_pct"]              / thr_r * 100) if thr_r > 0 else 0
                    hist["cum_util"] = ((hist["red_pct"] + hist["amber_pct"]) / thr_c * 100) if thr_c > 0 else 0
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=hist["date"], y=hist["red_util"],
                                              name="Red util %", mode="lines+markers",
                                              line=dict(color=_theme()["tier-red-bright"], width=2.5),
                                              marker=dict(size=6, color=_theme()["tier-red-bright"]),
                                              hovertemplate="<b>%{x|%b %Y}</b><br>Red util: %{y:.1f}%<extra></extra>"))
                    fig.add_trace(go.Scatter(x=hist["date"], y=hist["cum_util"],
                                              name="Amber + Red util %", mode="lines+markers",
                                              line=dict(color=_theme()["tier-amber-bright"], width=2.5),
                                              marker=dict(size=6, color=_theme()["tier-amber-bright"]),
                                              hovertemplate="<b>%{x|%b %Y}</b><br>Amber + Red util: %{y:.1f}%<extra></extra>"))
                    fig.add_hline(y=100, line_dash="dash", line_color=_theme()["plotly-hline"], line_width=1)
                    fig.update_layout(**DARK_LAYOUT, height=215, margin=dict(l=0,r=0,t=28,b=2),
                                       showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.02, **DARK_LEGEND),
                                       xaxis_title="", yaxis_title="")
                    fig.update_yaxes(tickformat=".0f", ticksuffix="%")
                    st.markdown(
                        f'<div style="margin-top:8px;margin-bottom:4px;font-size:11px;font-weight:800;color:var(--text-muted);'
                        f'text-transform:uppercase;letter-spacing:0.10em;">12-month utilisation trend</div>',
                        unsafe_allow_html=True,
                    )
                    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        except Exception:
            pass  # sparkline is a nice-to-have; never let it block the dialog

        # ── Breach count footer ────────────────────────────────────────
        n_br = int(row.get("breaches_last_12mo", 0))
        st.markdown(
            f'<div style="margin-top:-24px;padding-top:6px;border-top:1px dashed var(--border-default);'
            f'font-size:13px;color:var(--text-muted);">'
            f'No. of breaches past 1 year: <b style="color:var(--text-primary);">{n_br}</b>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # ── Drill-through button ──────────────────────────────────────
        st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
        # Pass 27.1: thicker accent-coloured border so the drill-through CTA
        # stands out as the primary action in the dialog.
        st.markdown("""
        <style>
        /* Strip the gap below the plotly chart inside this dialog */
        div[data-testid="stDialog"] div[data-testid="stPlotlyChart"] {
          margin-bottom: -20px !important;
          margin-left:   -8px  !important;
          margin-right:  -8px  !important;
        }
        div[data-testid="stDialog"] div[data-testid="element-container"]:has(> div[data-testid="stPlotlyChart"]) {
          margin-bottom: 0 !important;
          padding-left:  0 !important;
          padding-right: 0 !important;
        }
        /* Modal body padding adjustment — let the chart go edge-to-edge */
        div[data-testid="stDialog"] .stPlotlyChart > div {
          padding-left:  0 !important;
          padding-right: 0 !important;
        }
        div[data-testid="stDialog"] button[kind="primary"] {
          border: 2.5px solid var(--accent) !important;
          font-weight: 700 !important;
          letter-spacing: 0.04em !important;
          box-shadow: 0 2px 4px var(--accent-shadow) !important;
        }
        div[data-testid="stDialog"] button[kind="primary"]:hover {
          border-color: var(--accent) !important;
          filter: brightness(1.05);
          box-shadow: 0 4px 10px var(--accent-shadow) !important;
        }
        </style>
        """, unsafe_allow_html=True)
        if st.button("Open full Strategy Detail \u2197", key=f"preview_drill_{sub_name}",
                      use_container_width=True, type="primary"):
            st.session_state.pop("preview_strategy",      None)
            st.session_state.pop("preview_just_clicked",  None)
            st.query_params["goto"]    = "strategy"
            st.query_params["name"]    = sgroup
            st.query_params["sdstrat"] = sgroup
            st.query_params["sdscope"] = sub_name
            st.query_params["sdfocus"] = "Amber"
            st.rerun()
    _dialog()


def page_portfolio_overview(strat_agg, sub_strat_agg, portfolios_df, history_df, sub_history_df, instruments_df):
    # Pass 27: handle ?preview=<sub_name> URL param — sets session-state then
    # clears the URL so refresh doesn't re-trigger the dialog. The "just_clicked"
    # guard ensures the dialog is only opened ONCE per click (st.dialog's X close
    # doesn't trigger a rerun, so without a guard the dialog would re-open on the
    # next interaction).
    _preview_param = st.query_params.get("preview")
    if _preview_param:
        st.session_state["preview_strategy"]      = _preview_param
        st.session_state["preview_just_clicked"]  = True
        try:
            del st.query_params["preview"]
        except Exception:
            pass
    if st.session_state.get("preview_just_clicked"):
        st.session_state["preview_just_clicked"] = False
        _pname = st.session_state.get("preview_strategy")
        if _pname:
            _row = sub_strat_agg[sub_strat_agg["sub_strategy_name"] == _pname]
            if len(_row):
                _render_preview_dialog(_row.iloc[0], sub_history_df)

    _render_page_title("Intransparency Monitoring Dashboard", show_stats=True)
    st.markdown(
        '<p style="font-size:14px;color:var(--text-muted);font-weight:500;letter-spacing:0.01em;margin-top:2px;margin-bottom:18px;">'
        'Direct Investments, Co-investments and Fund Investments</p>',
        unsafe_allow_html=True,
    )

    # Drill-through from clickable cards: read URL query param, promote to
    # session_state, then clear the URL so future reruns don't keep forcing it.
    try:
        qp_focus = st.query_params.get("focus")
    except Exception:
        qp_focus = None
    if qp_focus in ("Red", "Amber"):
        st.session_state["focus_tier"]       = qp_focus
        st.session_state["breakdown_expand"] = True
        st.session_state["trend_expand"]     = True
        st.session_state["_scroll_to_details"] = True  # consumed below to trigger scroll script
        try:
            del st.query_params["focus"]
        except Exception:
            pass

    # Panel expand/collapse persists via the URL (?exp=1/0). Clicking an exposure-card
    # link triggers a full-page reload that resets st.session_state, so storing the
    # state in the URL is what stops the Strategy status panel re-expanding on a click.
    qp_exp = st.query_params.get("exp")
    if qp_exp in ("0", "1"):
        st.session_state["widgets_expanded"] = (qp_exp == "1")
    elif "widgets_expanded" not in st.session_state:
        st.session_state["widgets_expanded"] = False

    # Cockpit panel renders one widget per Strategy (= sub_strategy internally).
    # Total-portfolio aggregates now roll up across the 16 Strategies (which is where
    # the thresholds live in the new taxonomy).
    df = sub_strat_agg
    pf = portfolios_df

    # ── Computed metrics ─────────────────────────────────────────────────────
    total_mv = df["total_mv"].sum()
    w_amber  = (df["Amber_pct"]*df["total_mv"]).sum()/total_mv if total_mv else 0
    w_red    = (df["Red_pct"]  *df["total_mv"]).sum()/total_mv if total_mv else 0
    w_cum    = w_amber + w_red
    n_breaches   = int(df["any_breach"].sum())
    breach_names = df[df["any_breach"]]["name"].tolist()

    # Total-portfolio thresholds — policy limits set at the portfolio level
    # (Pass 24.1). Hard-coded via TOTAL_PORTFOLIO_RED_LIMIT / TOTAL_PORTFOLIO_CUM_LIMIT.
    if total_mv > 0:
        thr_red_tot   = TOTAL_PORTFOLIO_RED_LIMIT
        thr_cum_tot   = TOTAL_PORTFOLIO_CUM_LIMIT
        thr_amber_tot = max(0.0, thr_cum_tot - thr_red_tot)   # derived
    else:
        thr_amber_tot = thr_red_tot = thr_cum_tot = 0.0

    util_red_tot   = (w_red   / thr_red_tot   * 100) if thr_red_tot   > 0 else 0
    util_amber_tot = (w_amber / thr_amber_tot * 100) if thr_amber_tot > 0 else 0
    util_cum_tot   = (w_cum   / thr_cum_tot   * 100) if thr_cum_tot   > 0 else 0

    t_red_breach   = w_red   > thr_red_tot   + 1e-6
    t_amber_breach = w_amber > thr_amber_tot + 1e-6
    t_cum_breach   = w_cum   > thr_cum_tot   + 1e-6
    t_any_breach   = t_red_breach or t_amber_breach or t_cum_breach

    # Trend data — full 12 months, AUM-weighted
    hf = history_df
    def _aum_weighted(group, col):
        mv_total = group["mv"].sum()
        return (group[col] * group["mv"]).sum() / mv_total if mv_total > 0 else 0
    hagg = (
        hf.groupby("date")
          .apply(lambda g: _aum_weighted(g, "non_transparent_pct"))
          .reset_index(name="non_transparent_pct")
    )
    hagg["non_transparent_pct"] *= 100

    # Breach summary still used below the Strategy Status panel band.
    if n_breaches == 0:
        breach_part = f"all {len(df)} strategies within tolerance"
        breach_color = "var(--ok-text)"
    else:
        names_label = ", ".join(breach_names)
        verb = "is" if n_breaches == 1 else "are"
        breach_part = f"{n_breaches} of {len(df)} strategies {verb} in breach ({names_label})"
        breach_color = "var(--breach-text)"

    # Section band kept short — the descriptive subtitle and the "within limit" status
    # line were duplicating info already in the portfolio context card above.
    st.markdown(_section_band("Total Portfolio – Intransparency Limits Utilisation"), unsafe_allow_html=True)

    # ── Portfolio transparency context (now below the section band) ──────────
    # Limit-utilisation line first, transparency composition second.
    _tot_mv = float(portfolios_df["mv"].sum())
    if _tot_mv > 0:
        _w_cum_pct  = float((portfolios_df["tier"].isin(["Amber", "Red"]).astype(int) * portfolios_df["mv"]).sum()) / _tot_mv * 100
        _w_green_pct = 100 - _w_cum_pct
        # Pass 24.1: use the same hard-coded portfolio limit the cards use
        _thr_cum_tot = TOTAL_PORTFOLIO_CUM_LIMIT
        _util_total = (_w_cum_pct / 100) / _thr_cum_tot if _thr_cum_tot > 0 else 0
        _rt_status = "within risk tolerance" if _util_total <= 1.0 else "above risk tolerance"
        _rt_color  = "var(--color-ok)" if _util_total <= 1.0 else "var(--color-red-fill)"
        # Plain footnote treatment under the section band.
        st.markdown(
            f'<div style="font-size:14px;color:var(--text-soft);line-height:1.6;margin:-8px 0 14px 0;padding-left:15px;">'
            f'Total intransparency at <b style="color:var(--text-primary);">{_util_total*100:.0f}%</b> of the portfolio limit \u2014 '
            f'<b style="color:{_rt_color};">{_rt_status}</b>.<br/>'
            f'Portfolio is <b style="color:var(--text-primary);">{_w_green_pct:.0f}%</b> transparent (Green); '
            f'<b style="color:var(--text-primary);">{_w_cum_pct:.0f}%</b> intransparent (Amber + Red).'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── Section A: Exposure cards (left, stacked) + A.I. Observations (right) ──
    # Pass 24: users found the wide elongated exposure cards too dominant.
    # Stack Red + Amber + Red on the left, put A.I. Observations on the right.
    card_specs = [
        ("Red exposure",   util_red_tot, w_red*100, thr_red_tot*100, "#e74c3c", t_red_breach, "Red"),
        ("Amber + Red exposure", util_cum_tot, w_cum*100, thr_cum_tot*100, "#e67e22", t_cum_breach, "Amber"),
    ]
    exp_q = "1" if st.session_state["widgets_expanded"] else "0"

    # Pass 27.6: further shrink exposure column → 0.65 / 1.35 so AI panel
    # has comfortable text width for the 3 always-visible commentaries.
    # Pass 27.7: stretch both columns so their bottoms align. We tag the inner
    # exposure stack with a unique class and use CSS to force its column +
    # ancestor wrappers to flex-grow to full height, then make each card flex:1
    # so the stack fills the available height proportionally.
    st.markdown("""
    <style>
    .expo-stack { flex: 1 1 auto; }
    .expo-stack .exposure-card { flex: 1 1 0; }
    /* Force the column wrapping .expo-stack and its ancestors to stretch */
    div[data-testid="stVerticalBlock"]:has(.expo-stack) {
      height: 100%;
      display: flex !important;
      flex-direction: column !important;
    }
    div[data-testid="stHorizontalBlock"]:has(.expo-stack) > div {
      display: flex !important;
      flex-direction: column !important;
    }
    div[data-testid="stHorizontalBlock"]:has(.expo-stack) > div > div[data-testid="stVerticalBlock"] {
      flex: 1 1 auto !important;
    }
    </style>
    """, unsafe_allow_html=True)
    _expo_col, _ai_col = st.columns([0.65, 1.35], gap="small", vertical_alignment="top")
    with _expo_col:
        stacked_html = '<div class="expo-stack" style="display:flex;flex-direction:column;gap:12px;height:100%;margin-bottom:24px;">'
        for (lbl, util, val, thr, color, breach, tier_key) in card_specs:
            stacked_html += _total_exposure_card_html(
                lbl, util, val, thr, color, breach,
                href=f"?focus={tier_key}&exp={exp_q}{_theme_qs()}#tp-details",
                tooltip=TIER_TOOLTIPS.get(tier_key),
            )
        stacked_html += '</div>'
        st.markdown(stacked_html, unsafe_allow_html=True)

    with _ai_col:
        st.markdown(_ai_observations_html(strat_agg, sub_strat_agg, portfolios_df,
                                           history_df, sub_history_df, instruments_df),
                    unsafe_allow_html=True)

    st.markdown('<div style="height:14px;"></div>', unsafe_allow_html=True)
    st.markdown(_section_band("Active Strategies – Intransparency Limits Utilisation", "Each Strategy\'s utilisation against its own limits."), unsafe_allow_html=True)
    # Pass 27.9: breach summary text and Expand-all button live on the SAME row
    # so the button aligns vertically with the "11 of 16 strategies..." sentence.
    # Pass 26.1: bump button border thickness so it stands out more.
    st.markdown("""
    <style>
    div[data-testid="stHorizontalBlock"] div.st-key-toggle_widgets button {
      border: 2px solid var(--text-primary) !important;
    }
    div[data-testid="stHorizontalBlock"] div.st-key-toggle_widgets button:hover {
      border-color: var(--accent) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    try:
        _txt_col, _btn_col = st.columns([8, 1.1], vertical_alignment="center")
    except TypeError:
        _txt_col, _btn_col = st.columns([8, 1.1])
    with _txt_col:
        st.markdown(
            f'<p style="font-size:13.5px;color:{breach_color};margin:0;">{breach_part}</p>',
            unsafe_allow_html=True,
        )
    with _btn_col:
        btn_label = "Collapse all" if st.session_state["widgets_expanded"] else "Expand all"
        if st.button(btn_label, key="toggle_widgets", use_container_width=True):
            st.session_state["widgets_expanded"] = not st.session_state["widgets_expanded"]
            st.query_params["exp"] = "1" if st.session_state["widgets_expanded"] else "0"
            st.rerun()
    expanded = st.session_state["widgets_expanded"]
    # Group the 16 Strategy widgets into two flat sections: Public vs Private.
    # PRODUCT_GROUPING maps each Strategy Group -> Public/Private; the strategy_id ->
    # Strategy Group link is retained in the data for Strategy Detail drill-through.
    def _product_section(title, product):
        group_ids = [g["strategy_id"] for _, g in strat_agg.iterrows()
                     if PRODUCT_GROUPING.get(str(g["name"])) == product]
        children = df[df["strategy_id"].isin(group_ids)]
        if children.empty:
            return ""
        any_child_breach = bool(children["any_breach"].any())
        accent = "var(--color-breach)" if any_child_breach else "var(--text-subtle)"
        n = len(children)
        head = (
            '<div style="display:flex;align-items:center;gap:10px;margin:16px 0 8px;">'
            '<div style="font-size:20px;color:var(--text-soft);font-weight:600;letter-spacing:0.06em;text-transform:uppercase;">'
            + title +
            '</div>'
            '<div style="flex:1;height:1px;background:' + accent + ';opacity:0.25;"></div>'
            '<div style="font-size:11px;color:var(--text-subtle);">'
            + str(n) + ' ' + ("strategy" if n == 1 else "strategies") + '</div></div>'
        )
        grid = '<div style="display:grid;grid-template-columns:repeat(auto-fill, minmax(240px, 1fr));gap:10px;margin-bottom:4px;">'
        for _, row in children.iterrows():
            grid += _cockpit_widget_html(row, expanded=expanded)
        grid += '</div>'
        return head + grid

    cockpit_html = _product_section("Public Strategies", "Public") + _product_section("Private Strategies", "Private")
    # Negative top margin tightens the gap between the toggle button and the widgets.
    st.markdown('<div style="margin-top:-14px;">' + cockpit_html + '</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:26px;"></div>', unsafe_allow_html=True)
    # Pass 17.5 + 17.6: anchor target + JS scroll-into-view.  Streamlit clears the
    # URL hash on rerun (the native href="#tp-details" stops working), so we use a
    # components iframe with a script that scrolls the parent doc when the
    # _scroll_to_details flag is set on this render.
    st.markdown('<div id="tp-details" style="scroll-margin-top:80px;"></div>', unsafe_allow_html=True)
    st.markdown(_section_band("Details", "Total portfolio trend over time and exposure contribution breakdown."), unsafe_allow_html=True)
    if st.session_state.pop("_scroll_to_details", False):
        import streamlit.components.v1 as _components
        _components.html(
            """<script>
            (function() {
              let tries = 0;
              const fire = () => {
                const el = window.parent.document.getElementById("tp-details");
                if (el) {
                  el.scrollIntoView({behavior: "smooth", block: "start"});
                  return;
                }
                if (++tries < 40) { setTimeout(fire, 100); }
              };
              setTimeout(fire, 200);
            })();
            </script>""",
            height=0,
        )

    # ── Section C: Trend (expander, collapsed by default) ───────────────────
    # Trend follows the same tier the exposure cards set (focus_tier), so a card
    # click focuses the Trend just like the Breakdown. Amber / no-click = full chart.
    trend_tier   = st.session_state.get("focus_tier", "Amber")
    # Pass 29.8: promote one-shot navigation flag to a sticky open state so
    # internal widget toggles (View, Cut by) don't collapse the expander on
    # rerun. Without this, the first toggle re-evaluates expanded=False and
    # snaps the panel closed.
    if st.session_state.pop("trend_expand", False):
        st.session_state["_tp_trend_open"] = True
    trend_expand = st.session_state.get("_tp_trend_open", False)
    with st.expander("📈 Total Portfolio Trend", expanded=trend_expand):
        # Pass 16: view toggle — Intransparency (existing) vs Utilisation (new)
        view_mode = st.radio(
            "View", ["Intransparency", "Utilisation"],
            horizontal=True, key="tp_trend_view", label_visibility="collapsed",
        )

        if view_mode == "Intransparency":
            st.markdown(
                f'<p class="section-title" style="margin-top:0.5rem;">Intransparency Trend</p>',
                unsafe_allow_html=True
            )
            st.caption("AUM-weighted total portfolio. Use the legend to toggle Amber, Red, and Total intransparency on or off.")

            hagg_stack = (
                hf.groupby("date")
                  .apply(lambda g: pd.Series({
                      "amber_pct": _aum_weighted(g, "amber_pct") * 100,
                      "red_pct":   _aum_weighted(g, "red_pct")   * 100,
                  }))
                  .reset_index()
            )

            amber_vis = True if trend_tier in ("Amber", "Amber only") else "legendonly"
            red_vis   = True if trend_tier in ("Red",   "Amber") else "legendonly"
            total_vis = True if trend_tier == "Amber" else "legendonly"
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Bar(
                x=hagg_stack["date"], y=hagg_stack["amber_pct"],
                name="Amber", marker_color=_theme()["tier-amber-bright"], visible=amber_vis,
                hovertemplate="<b>%{x|%b %Y}</b><br>Amber: %{y:.1f}%<extra></extra>",
            ))
            fig_trend.add_trace(go.Bar(
                x=hagg_stack["date"], y=hagg_stack["red_pct"],
                name="Red", marker_color=_theme()["tier-red-bright"], visible=red_vis,
                hovertemplate="<b>%{x|%b %Y}</b><br>Red: %{y:.1f}%<extra></extra>",
            ))
            fig_trend.add_trace(go.Scatter(
                x=hagg["date"], y=hagg["non_transparent_pct"],
                mode="lines+markers", name="Total intransparency", visible=total_vis,
                line=dict(color=_theme()["tier-red-bright"], width=2.5),
                marker=dict(size=8, color=_theme()["tier-red-bright"], line=dict(color=_theme()["plotly-marker-border"], width=1.5)),
                hovertemplate="<b>%{x|%b %Y}</b><br>Total: %{y:.1f}%<extra></extra>",
            ))
            fig_trend.update_layout(
                **DARK_LAYOUT, barmode="stack",
                yaxis_title="<b>% intransparency</b>", height=320,
                margin=dict(l=20,r=20,t=10,b=20),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, **DARK_LEGEND),
            )
            fig_trend.update_xaxes(tickformat="%b %Y", dtick="M1", tickangle=-30)
            fig_trend.update_yaxes(title_font=dict(size=14), tickfont=dict(size=12))
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.markdown(
                f'<p class="section-title" style="margin-top:0.5rem;">Utilisation Trend</p>',
                unsafe_allow_html=True
            )
            st.caption(f"AUM-weighted portfolio utilisation against the combined limit. The dashed line marks the 100% policy limit.")

            # Pass 18.4: use sub_history_df + sub_strat_agg thresholds so the most
            # recent point exactly matches the Total Portfolio utilisation cards
            # at the top of the page. (strat_agg thresholds use simple .mean()
            # aggregation across children, which doesn't match the cards' MV-weighted formula.)
            _shf_t = sub_history_df.merge(
                sub_strat_agg[["sub_strategy_id","threshold_red","threshold_cum"]],
                on="sub_strategy_id", how="left")
            def _util_for(g):
                mv = g["mv"].sum()
                if mv <= 0: return pd.Series({"red_util": 0.0, "cum_util": 0.0})
                w_red = (g["red_pct"]   * g["mv"]).sum() / mv
                w_amb = (g["amber_pct"] * g["mv"]).sum() / mv
                w_thr_red = (g["threshold_red"] * g["mv"]).sum() / mv
                w_thr_cum = (g["threshold_cum"] * g["mv"]).sum() / mv
                return pd.Series({
                    "red_util": (w_red / w_thr_red * 100) if w_thr_red > 0 else 0.0,
                    "cum_util": ((w_red + w_amb) / w_thr_cum * 100) if w_thr_cum > 0 else 0.0,
                })
            hagg_util = _shf_t.groupby("date").apply(_util_for).reset_index()
            # Pass 17.8: add BOTH series so the legend toggle works the same way
            # as the Intransparency view. The clicked tier starts fully visible;
            # the other line starts as legendonly (one click to show).
            red_vis_u = True if trend_tier == "Red" else "legendonly"
            cum_vis_u = True if trend_tier != "Red" else "legendonly"

            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(
                x=hagg_util["date"], y=hagg_util["red_util"],
                mode="lines+markers", name="Red util %", visible=red_vis_u,
                line=dict(color=_theme()["tier-red-bright"], width=2.5),
                marker=dict(size=8, color=_theme()["tier-red-bright"], line=dict(color=_theme()["plotly-marker-border"], width=1.5)),
                hovertemplate="<b>%{x|%b %Y}</b><br>Red util: %{y:.1f}%<extra></extra>",
            ))
            fig_trend.add_trace(go.Scatter(
                x=hagg_util["date"], y=hagg_util["cum_util"],
                mode="lines+markers", name="Amber + Red util %", visible=cum_vis_u,
                line=dict(color=_theme()["tier-amber-bright"], width=2.5),
                marker=dict(size=8, color=_theme()["tier-amber-bright"], line=dict(color=_theme()["plotly-marker-border"], width=1.5)),
                hovertemplate="<b>%{x|%b %Y}</b><br>Amber + Red util: %{y:.1f}%<extra></extra>",
            ))
            fig_trend.add_hline(y=100, line_dash="dash", line_color=_theme()["plotly-hline"],
                                annotation_text="Limit (100%)",
                                annotation_position="bottom right",
                                annotation_font_size=11)
            fig_trend.update_layout(**DARK_LAYOUT, height=320,
                                    yaxis_title="<b>% of limit used</b>",
                                    margin=dict(l=20,r=20,t=10,b=20),
                                    legend=dict(orientation="h", yanchor="bottom", y=1.02, **DARK_LEGEND))
            fig_trend.update_xaxes(tickformat="%b %Y", dtick="M1", tickangle=-30)
            fig_trend.update_yaxes(title_font=dict(size=14), tickfont=dict(size=12))
            st.plotly_chart(fig_trend, use_container_width=True)

    # ── Section D: Breakdown panel (drill-through from Top cards) ────────────
    # Pass 29.8: sticky promotion — see Trend section above for the same fix.
    if st.session_state.pop("breakdown_expand", False):
        st.session_state["_tp_breakdown_open"] = True
    expand_breakdown = st.session_state.get("_tp_breakdown_open", False)
    focus_default    = st.session_state.get("focus_tier", "Red")

    with st.expander("📊 Total Portfolio Exposure breakdown", expanded=expand_breakdown):
        st.markdown(
            '<div style="font-size:13px;color:var(--text-muted);margin:2px 0 10px;">'
            'Tier exposure by contributor '
            '<span title="Where is the exposure coming from?" '
            'style="color:var(--text-subtle);cursor:help;font-size:13px;">ⓘ</span></div>',
            unsafe_allow_html=True,
        )
        bc1, bc2 = st.columns(2)
        with bc1:
            tier_options = ["Red", "Amber", "Amber only"]
            # Pass 17.4: display labels — internal values unchanged so palettes/tooltips/URL
            # focus param all still work.  "Amber" (= R+A cumulative) → "Amber + Red";
            # "Amber only" (= pure Amber tier) → "Amber".
            _tier_labels = {"Red": "Red", "Amber": "Amber + Red", "Amber only": "Amber"}
            tier = st.selectbox("Focus on",
                                tier_options,
                                index=tier_options.index(focus_default) if focus_default in tier_options else 0,
                                format_func=lambda v: _tier_labels.get(v, v),
                                key="bd_focus")
        with bc2:
            cut_label = st.selectbox("Cut by",
                                     ["Strategy", "Investment Type"],
                                     key="bd_cut")
        # Pass 17.14: display label used in summary line, empty state, and column header.
        _tier_disp = _tier_labels.get(tier, tier)

        cut_map = {
            "Strategy":                   "sub_strategy_name",
            "Investment Type":            "instrument_type",
            # Hidden cuts (data preserved in case we re-expose them later):
            # "Asset type":               "asset_type",
            # "Investment Bucket":        "investment_bucket",
        }
        cut_col = cut_map[cut_label]

        tier_filter = pf["tier"].isin(["Amber", "Red"]) if tier == "Amber" else (pf["tier"] == "Amber" if tier == "Amber only" else pf["tier"] == "Red")
        tier_pf = pf[tier_filter]
        total_tier_mv  = float(tier_pf["mv"].sum())
        total_tier_pct = (total_tier_mv / total_mv * 100) if total_mv > 0 else 0
        n_contrib      = int(tier_pf["portfolio_id"].nunique())

        # Compute breakdown for selected cut
        all_cuts = pf[cut_col].dropna().unique()
        tier_grouped = (
            tier_pf.groupby(cut_col)
                   .agg(mv=("mv", "sum"), count=("portfolio_id", "count"))
                   .reset_index()
        )
        full = pd.DataFrame({cut_col: all_cuts}).merge(tier_grouped, on=cut_col, how="left").fillna(0)
        full["count"]        = full["count"].astype(int)
        full["pct_of_tier"]  = (full["mv"] / total_tier_mv * 100) if total_tier_mv > 0 else 0
        full["contrib_pct"]  = (full["mv"] / total_mv * 100) if total_mv > 0 else 0
        full = full.sort_values("contrib_pct", ascending=False)

        non_zero  = full[full["contrib_pct"] > 0]
        zero_cuts = full[full["contrib_pct"] == 0]

        # Summary line
        st.markdown(
            f'<p style="font-size:14px;color:var(--text-soft);margin:6px 0 12px;">'
            f'The bar below is <span style="color:var(--text-primary);font-weight:500;">{total_tier_pct:.0f}%</span> '
            f'\u2014 the {_tier_disp} exposure shown in the top panel '
            f'(<span style="color:var(--text-primary);">{n_contrib}</span> portfolios contributing).</p>',
            unsafe_allow_html=True,
        )

        if total_tier_mv == 0:
            st.info(f"No portfolios are currently in the {_tier_disp} tier.")
        else:
            # Build stacked bar: top 5 segments + "+ N others" if more contributors exist
            TOP_N    = 5
            palette  = TIER_PALETTES.get(tier, TIER_PALETTES["Red"])
            top_rows = non_zero.head(TOP_N)
            rest     = non_zero.iloc[TOP_N:]

            segments = [{"label": str(r[cut_col]), "contrib_pct": float(r["contrib_pct"])}
                        for _, r in top_rows.iterrows()]
            if len(rest) > 0:
                segments.append({
                    "label": f"+ {len(rest)} other{'s' if len(rest) > 1 else ''}",
                    "contrib_pct": float(rest["contrib_pct"].sum()),
                    "is_others": True,
                })

            st.markdown(_build_stacked_bar(segments, palette, total_tier_pct), unsafe_allow_html=True)
            st.markdown(_build_legend(segments, palette),                   unsafe_allow_html=True)

            # Detail table — all non-zero contributors individually, zero contributors muted
            table_html = (
                '<table style="width:100%;border-collapse:collapse;font-size:15px;margin-top:8px;">'
                # Header row: solid background tint, bold + uppercase + tracked so it
                # reads as a header and not just another row.
                '<thead><tr style="background-color:var(--bg-track);border-bottom:2px solid var(--accent);'
                'color:var(--text-primary);font-weight:800;text-align:left;font-size:13px;'
                'letter-spacing:0.08em;text-transform:uppercase;">'
                f'<th style="padding:10px 12px;border-radius:6px 0 0 0;">{cut_label}</th>'
                f'<th style="padding:10px 12px;text-align:right;">Contribution to TP</th>'
                f'<th style="padding:10px 12px;text-align:right;">Share of {_tier_disp}</th>'
                f'<th style="padding:10px 12px;text-align:left;border-radius:0 6px 0 0;">Issue tags</th>'
                '</tr></thead><tbody>'
            )
            # Pass 26.2 / 28.2: render the spreadsheet drivers as inline chips.
            # When Cut by = Strategy, the chips come straight from
            # STRATEGY_REAL_DATA[strategy]. For other cuts (Investment Type,
            # Asset type), we aggregate chips across every sub-strategy that
            # contributes Amber/Red MV to this row's bucket, ranked by how many
            # of those strategies the chip appears in (most common first).
            def _row_chips(name):
                if cut_col == "sub_strategy_name":
                    contrib_strats = [str(name)]
                else:
                    contrib_strats = (
                        tier_pf[tier_pf[cut_col] == name]["sub_strategy_name"]
                        .dropna().astype(str).unique().tolist()
                    )
                chip_counts = {}
                chip_order  = []
                for s in contrib_strats:
                    meta = STRATEGY_REAL_DATA.get(s, {}) or {}
                    for c in (meta.get("chips") or []):
                        if c not in chip_counts:
                            chip_counts[c] = 0
                            chip_order.append(c)
                        chip_counts[c] += 1
                chips = sorted(chip_order,
                               key=lambda c: (-chip_counts[c], chip_order.index(c)))
                if not chips:
                    return '<span style="font-size:11.5px;color:var(--text-subtle);font-style:italic;">—</span>'
                return "".join(
                    f'<span style="display:inline-block;border:1px solid {_tag_color(c)};color:{_tag_color(c)};'
                    f'background:transparent;padding:2px 8px;border-radius:10px;font-size:11px;'
                    f'font-weight:600;margin:0 4px 4px 0;white-space:nowrap;">{c}</span>'
                    for c in chips[:3]
                )
            for _, r in non_zero.iterrows():
                wt = "400"  # uniform weight; the contribution % column already encodes magnitude
                table_html += (
                    f'<tr style="border-bottom:1px solid var(--border-default);">'
                    f'<td style="padding:9px 12px;color:var(--text-primary);font-weight:{wt};">{r[cut_col]}</td>'
                    f'<td style="padding:9px 12px;text-align:right;color:var(--text-primary);font-variant-numeric:tabular-nums;font-weight:500;">{r["contrib_pct"]:.2f}%</td>'
                    f'<td style="padding:9px 12px;text-align:right;color:var(--text-soft);font-variant-numeric:tabular-nums;">{r["pct_of_tier"]:.0f}%</td>'
                    f'<td style="padding:9px 12px;text-align:left;">{_row_chips(r[cut_col])}</td>'
                    f'</tr>'
                )
            # The "(no contribution)" catch-all row was removed — it was making the
            # table unnecessarily long with no actionable info. Zero-contributors
            # are simply omitted now.
            table_html += '</tbody></table>'
            st.markdown(table_html, unsafe_allow_html=True)



# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — Strategy Detail
# ═══════════════════════════════════════════════════════════════════════════════

def page_strategy_detail(strat_agg, sub_strat_agg, portfolios_df, instruments_df, history_df, sub_history_df):
    # ── Picker ──────────────────────────────────────────────────────────────
    sel = st.selectbox("Select Strategy Group", strat_agg["name"].tolist(), key="sd_sel")
    grow = strat_agg[strat_agg["name"] == sel].iloc[0]
    sid = grow["strategy_id"]
    owner = grow["owner"]

    children = sub_strat_agg[sub_strat_agg["strategy_id"] == sid].copy()
    n_child = len(children)
    n_breach = int(children["any_breach"].sum())
    breaching_names = children[children["any_breach"]]["sub_strategy_name"].tolist()

    # ── Drill-through: a clicked card carries ?sdfocus=<tier> (+ &sdstrat=<group>).
    #    Promote the tier to session, flag the Details panels to auto-open, then
    #    clear the consumed params. (main() already used sdstrat to keep us here.)
    qpf = st.query_params.get("sdfocus")
    qps = st.query_params.get("sdsub")
    if qpf in ("Red", "Amber"):
        st.session_state["sd_focus_tier"]       = qpf
        st.session_state["sd_breakdown_expand"] = True
        st.session_state["sd_trend_expand"]     = True
        st.session_state["_scroll_to_sd_details"] = True  # consumed below
        if qps:
            st.session_state["sd_scope"] = qps
    for _k in ("sdfocus", "sdstrat", "sdsub"):
        try:
            del st.query_params[_k]
        except Exception:
            pass
    st.session_state.setdefault("sd_focus_tier", "Amber")
    sd_focus = st.session_state["sd_focus_tier"]

    # ── Title + status subtitle ─────────────────────────────────────────────
    _render_page_title(f"Strategy Group · {sel}")
    if n_breach == 0:
        status_html = f'<span style="color:var(--color-ok);">All {n_child} strateg{"y" if n_child==1 else "ies"} within tolerance.</span>'
    else:
        names = ", ".join(breaching_names)
        _verb = "is" if n_breach == 1 else "are"
        status_html = (
            f'<span style="color:var(--color-breach);">{n_breach} of {n_child} '
            f'strateg{"y" if n_child==1 else "ies"} {_verb} in breach ({names}).</span>'
        )
    st.markdown(
        f'<p style="font-size:14px;margin-top:-4px;margin-bottom:14px;">'
        f'<span style="color:var(--text-soft);">Strategy Group owner: '
        f'<span style="color:var(--text-primary);font-weight:500;">{owner}</span></span> &middot; {status_html}</p>',
        unsafe_allow_html=True,
    )

    # ── Section A: per-Strategy exposure cards (clickable drill-through) ──────
    # No Strategy-Group aggregate: limits live at the Strategy level, so each
    # Strategy is shown against its OWN Red / Amber (= Red+Amber combined) limits.
    st.markdown(_section_band(
        f"{sel} – Intransparency Limits Utilisation per Strategy",
        "Each Strategy is shown against its own Red and Amber limits. Click any card to focus the breakdown and trend below."),
        unsafe_allow_html=True)
    for _, sr in children.iterrows():
        s_name = sr["sub_strategy_name"]
        s_max = max(float(sr["red_utilisation"]), float(sr["amber_utilisation"]), float(sr["cum_utilisation"])) * 100
        if bool(sr["any_breach"]):
            s_state, s_color = "BREACH", "var(--color-breach)"
        elif s_max >= 80:
            s_state, s_color = "ALERT", "var(--color-alert)"
        else:
            s_state, s_color = "OK", "var(--color-ok)"
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:10px;margin:16px 0 8px;">'
            f'<div style="font-size:14px;font-weight:500;color:var(--text-primary);">{s_name}</div>'
            f'<div style="display:flex;align-items:center;gap:5px;">'
            f'<div style="width:8px;height:8px;border-radius:50%;background:{s_color};"></div>'
            f'<span style="font-size:12px;font-weight:600;color:{s_color};letter-spacing:0.03em;">{s_state}</span></div>'
            f'<div style="flex:1;height:1px;background:var(--border-default);"></div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        card_specs = [
            ("Red exposure",   float(sr["red_utilisation"])*100, float(sr["Red_pct"])*100, float(sr["threshold_red"])*100, "#e74c3c", bool(sr["red_breach"]), "Red"),
            ("Amber + Red exposure", float(sr["cum_utilisation"])*100, float(sr["cum_pct"])*100, float(sr["threshold_cum"])*100, "#e67e22", bool(sr["cum_breach"]), "Amber"),
        ]
        block = '<div style="display:grid;grid-template-columns:repeat(2, 1fr);gap:12px;margin-bottom:6px;">'
        for (lbl, util, val, thr, color, breach, tier_key) in card_specs:
            block += _total_exposure_card_html(
                lbl, util, val, thr, color, breach,
                href=f"?sdfocus={tier_key}&sdstrat={quote(str(sel))}&sdsub={quote(str(s_name))}{_theme_qs()}",
                tooltip=TIER_TOOLTIPS.get(tier_key),
            )
        block += '</div>'
        st.markdown(block, unsafe_allow_html=True)

    # ── Section B: Details (Trend + Breakdown) ──────────────────────────────
    st.markdown('<div style="height:22px;"></div>', unsafe_allow_html=True)
    # Pass 17.7: anchor + components iframe scrolls the page to this section on
    # card click (same pattern as Total Portfolio in 17.6).
    st.markdown('<div id="sd-details" style="scroll-margin-top:80px;"></div>', unsafe_allow_html=True)
    st.markdown(_section_band(
        "Details",
        "Trend over time and exposure contribution breakdown. Use Scope to view the whole group or a single Strategy."),
        unsafe_allow_html=True)
    if st.session_state.pop("_scroll_to_sd_details", False):
        import streamlit.components.v1 as _components
        _components.html(
            """<script>
            (function() {
              let tries = 0;
              const fire = () => {
                const el = window.parent.document.getElementById("sd-details");
                if (el) {
                  el.scrollIntoView({behavior: "smooth", block: "start"});
                  return;
                }
                if (++tries < 40) { setTimeout(fire, 100); }
              };
              setTimeout(fire, 200);
            })();
            </script>""",
            height=0,
        )

    # Scope: whole group, or narrow to a single Strategy (set by a clicked card).
    scope_opts = ["Whole group"] + children["sub_strategy_name"].tolist()
    if st.session_state.get("sd_scope") not in scope_opts:
        st.session_state["sd_scope"] = "Whole group"
    sc1, _sc2 = st.columns([1, 2])
    with sc1:
        scope = st.selectbox("Scope", scope_opts, key="sd_scope")
    if scope == "Whole group":
        sh = history_df[history_df["strategy_id"] == sid].sort_values("date")
        scope_pf = portfolios_df[portfolios_df["strategy_id"] == sid]
        scope_name = f"{sel} (whole group)"
    else:
        _ssid = children[children["sub_strategy_name"] == scope]["sub_strategy_id"].iloc[0]
        sh = sub_history_df[sub_history_df["sub_strategy_id"] == _ssid].sort_values("date")
        scope_pf = portfolios_df[(portfolios_df["strategy_id"] == sid) &
                                 (portfolios_df["sub_strategy_name"] == scope)]
        scope_name = scope

    # Trend — follows the clicked tier; Pass 16 adds Utilisation view toggle
    # Pass 29.8: sticky promotion — see Total Portfolio Trend for the rationale.
    if st.session_state.pop("sd_trend_expand", False):
        st.session_state["_sd_trend_open"] = True
    sd_trend_expand = st.session_state.get("_sd_trend_open", False)
    with st.expander("📈 Strategy Trend", expanded=sd_trend_expand):
        sd_view_mode = st.radio(
            "View", ["Intransparency", "Utilisation"],
            horizontal=True, key=f"sd_trend_view_{sel}", label_visibility="collapsed",
        )

        if sd_view_mode == "Intransparency":
            st.markdown(
                f'<p class="section-title" style="margin-top:0.5rem;">Intransparency Trend</p>',
                unsafe_allow_html=True)
            if sd_focus in ("Red", "Amber"):
                st.caption(f"{scope_name} — monthly {sd_focus} trend shown by default. Use the chart legend to toggle the other series on or off.")
            else:
                st.caption(f"{scope_name} — monthly trend. Stacked bars show the Amber / Red composition; the line traces total intransparency %. Click a Red or Amber card above to focus a single tier.")
            amber_vis = True if sd_focus in ("Amber", "Amber only") else "legendonly"
            red_vis   = True if sd_focus in ("Red",   "Amber") else "legendonly"
            total_vis = True if sd_focus == "Amber" else "legendonly"
            fig_st = go.Figure()
            fig_st.add_trace(go.Bar(x=sh["date"], y=sh["amber_pct"]*100, name="Amber",
                                    marker_color=_theme()["tier-amber-bright"], visible=amber_vis,
                                    hovertemplate="<b>%{x|%b %Y}</b><br>Amber: %{y:.1f}%<extra></extra>"))
            fig_st.add_trace(go.Bar(x=sh["date"], y=sh["red_pct"]*100, name="Red",
                                    marker_color=_theme()["tier-red-bright"], visible=red_vis,
                                    hovertemplate="<b>%{x|%b %Y}</b><br>Red: %{y:.1f}%<extra></extra>"))
            fig_st.add_trace(go.Scatter(x=sh["date"], y=sh["non_transparent_pct"]*100,
                                        mode="lines+markers", name="Total intransparency", visible=total_vis,
                                        line=dict(color=_theme()["tier-red-bright"], width=2.5),
                                        marker=dict(size=8, color=_theme()["tier-red-bright"], line=dict(color=_theme()["plotly-marker-border"], width=1.5)),
                                        hovertemplate="<b>%{x|%b %Y}</b><br>Total: %{y:.1f}%<extra></extra>"))
            fig_st.update_layout(**DARK_LAYOUT, barmode="stack", yaxis_title="<b>% intransparency</b>", height=320,
                                 margin=dict(l=20, r=20, t=10, b=20),
                                 legend=dict(orientation="h", yanchor="bottom", y=1.02, **DARK_LEGEND))
            fig_st.update_xaxes(tickformat="%b %Y", dtick="M1", tickangle=-30)
            fig_st.update_yaxes(title_font=dict(size=14), tickfont=dict(size=12))
            st.plotly_chart(fig_st, use_container_width=True)
        else:
            st.markdown(
                f'<p class="section-title" style="margin-top:0.5rem;">Utilisation Trend</p>',
                unsafe_allow_html=True)
            st.caption(f"{scope_name} — utilisation against the combined limit. The dashed line marks the 100% policy limit.")
            _thr = children.set_index("sub_strategy_id")[["threshold_red","threshold_cum"]]
            if "sub_strategy_id" in sh.columns:
                _sh_t = sh.merge(_thr, left_on="sub_strategy_id", right_index=True, how="left")
            else:
                _thr_red_grp = float((children["threshold_red"] * children["total_mv"]).sum() / max(children["total_mv"].sum(), 1e-9))
                _thr_cum_grp = float((children["threshold_cum"] * children["total_mv"]).sum() / max(children["total_mv"].sum(), 1e-9))
                _sh_t = sh.copy()
                _sh_t["threshold_red"] = _thr_red_grp
                _sh_t["threshold_cum"] = _thr_cum_grp
            def _util_sd(g):
                mv = g["mv"].sum()
                if mv <= 0: return pd.Series({"red_util": 0.0, "cum_util": 0.0})
                w_red = (g["red_pct"]   * g["mv"]).sum() / mv
                w_amb = (g["amber_pct"] * g["mv"]).sum() / mv
                w_thr_red = (g["threshold_red"] * g["mv"]).sum() / mv
                w_thr_cum = (g["threshold_cum"] * g["mv"]).sum() / mv
                return pd.Series({
                    "red_util": (w_red / w_thr_red * 100) if w_thr_red > 0 else 0.0,
                    "cum_util": ((w_red + w_amb) / w_thr_cum * 100) if w_thr_cum > 0 else 0.0,
                })
            sh_util = _sh_t.groupby("date").apply(_util_sd).reset_index()
            red_vis_u = True if sd_focus == "Red" else "legendonly"
            cum_vis_u = True if sd_focus != "Red" else "legendonly"
            fig_st = go.Figure()
            fig_st.add_trace(go.Scatter(
                x=sh_util["date"], y=sh_util["red_util"],
                mode="lines+markers", name="Red util %", visible=red_vis_u,
                line=dict(color=_theme()["tier-red-bright"], width=2.5),
                marker=dict(size=8, color=_theme()["tier-red-bright"], line=dict(color=_theme()["plotly-marker-border"], width=1.5)),
                hovertemplate="<b>%{x|%b %Y}</b><br>Red util: %{y:.1f}%<extra></extra>",
            ))
            fig_st.add_trace(go.Scatter(
                x=sh_util["date"], y=sh_util["cum_util"],
                mode="lines+markers", name="Amber + Red util %", visible=cum_vis_u,
                line=dict(color=_theme()["tier-amber-bright"], width=2.5),
                marker=dict(size=8, color=_theme()["tier-amber-bright"], line=dict(color=_theme()["plotly-marker-border"], width=1.5)),
                hovertemplate="<b>%{x|%b %Y}</b><br>Amber + Red util: %{y:.1f}%<extra></extra>",
            ))
            fig_st.add_hline(y=100, line_dash="dash", line_color=_theme()["plotly-hline"],
                             annotation_text="Limit (100%)",
                             annotation_position="bottom right",
                             annotation_font_size=11)
            fig_st.update_layout(**DARK_LAYOUT, height=320,
                                 yaxis_title="<b>% of limit used</b>",
                                 margin=dict(l=20, r=20, t=10, b=20),
                                 legend=dict(orientation="h", yanchor="bottom", y=1.02, **DARK_LEGEND))
            fig_st.update_xaxes(tickformat="%b %Y", dtick="M1", tickangle=-30)
            fig_st.update_yaxes(title_font=dict(size=14), tickfont=dict(size=12))
            st.plotly_chart(fig_st, use_container_width=True)


    # Breakdown — group-scoped, 4 cuts, in an expander with an info tooltip
    # Pass 29.8: sticky promotion — see Total Portfolio Trend for the rationale.
    if st.session_state.pop("sd_breakdown_expand", False):
        st.session_state["_sd_breakdown_open"] = True
    sd_breakdown_expand = st.session_state.get("_sd_breakdown_open", False)
    with st.expander("\U0001f4ca Strategy Exposure breakdown", expanded=sd_breakdown_expand):
        st.markdown(
            '<div style="font-size:13px;color:var(--text-muted);margin:2px 0 10px;">'
            'Tier exposure by contributor '
            '<span title="Where in the book is the exposure coming from?" '
            'style="color:var(--text-subtle);cursor:help;font-size:13px;">ⓘ</span></div>',
            unsafe_allow_html=True,
        )
        bc1, bc2 = st.columns(2)
        with bc1:
            tier_options = ["Red", "Amber", "Amber only"]
            _tier_labels_sd = {"Red": "Red", "Amber": "Amber + Red", "Amber only": "Amber"}
            tier = st.selectbox("Focus on", tier_options,
                                index=tier_options.index(sd_focus) if sd_focus in tier_options else 0,
                                format_func=lambda v: _tier_labels_sd.get(v, v),
                                key="sd_bd_focus")
        _tier_disp = _tier_labels_sd.get(tier, tier)  # Pass 17.16: in scope for summary + column header
        with bc2:
            cut_label = st.selectbox(
                "Cut by",
                ["Portfolio", "Investment Type"],
                key="sd_cut",
            )
        cut_map = {
            "Portfolio":                  "portfolio_name",
            "Investment Type":            "instrument_type",
            # Hidden cuts (data preserved in backend for future revisit):
            # "Strategy":                 "sub_strategy_name",   # removed: redundant when on Strategy Detail; revisit after 4-level hierarchy is in
            # "Asset type":               "asset_type",
            # "Investment Bucket":        "investment_bucket",
        }
        cut_col = cut_map[cut_label]

        sd_pf = scope_pf
        tier_filter = sd_pf["tier"].isin(["Amber", "Red"]) if tier == "Amber" else (sd_pf["tier"] == "Amber" if tier == "Amber only" else sd_pf["tier"] == "Red")
        tier_pf = sd_pf[tier_filter]
        strat_total_mv = float(sd_pf["mv"].sum())
        total_tier_mv = float(tier_pf["mv"].sum())
        total_tier_pct = (total_tier_mv / strat_total_mv * 100) if strat_total_mv > 0 else 0
        n_contrib = int(tier_pf["portfolio_id"].nunique())

        all_cuts = sd_pf[cut_col].dropna().unique()
        grouped = tier_pf.groupby(cut_col).agg(mv=("mv", "sum"), count=("portfolio_id", "count")).reset_index()
        full = pd.DataFrame({cut_col: all_cuts}).merge(grouped, on=cut_col, how="left").fillna(0)
        full["count"] = full["count"].astype(int)
        full["pct_of_tier"] = (full["mv"] / total_tier_mv * 100) if total_tier_mv > 0 else 0
        full["contrib_pct"] = (full["mv"] / strat_total_mv * 100) if strat_total_mv > 0 else 0
        full = full.sort_values("contrib_pct", ascending=False)
        non_zero  = full[full["contrib_pct"] > 0]
        zero_cuts = full[full["contrib_pct"] == 0]

        st.markdown(
            f'<p style="font-size:14px;color:var(--text-soft);margin:6px 0 12px;">'
            f'The bar below is <span style="color:var(--text-primary);font-weight:500;">{total_tier_pct:.0f}%</span> '
            f"&mdash; {scope_name}'s {_tier_disp} exposure "
            f'(<span style="color:var(--text-primary);">{n_contrib}</span> portfolios contributing).</p>',
            unsafe_allow_html=True)

        if total_tier_mv == 0:
            st.info(f"No portfolios are currently in the {_tier_disp} tier within {scope_name}.")
        else:
            TOP_N = 5
            palette = TIER_PALETTES.get(tier, TIER_PALETTES["Red"])
            top = non_zero.head(TOP_N)
            rest = non_zero.iloc[TOP_N:]
            segments = [{"label": str(r[cut_col]), "contrib_pct": float(r["contrib_pct"])} for _, r in top.iterrows()]
            if len(rest) > 0:
                segments.append({"label": f"+ {len(rest)} other" + ("s" if len(rest) > 1 else ""),
                                 "contrib_pct": float(rest["contrib_pct"].sum()), "is_others": True})
            st.markdown(_build_stacked_bar(segments, palette, total_tier_pct), unsafe_allow_html=True)
            st.markdown(_build_legend(segments, palette), unsafe_allow_html=True)

            table_html = (
                '<table style="width:100%;border-collapse:collapse;font-size:15px;margin-top:8px;">'
                # Header row: solid background tint, bold + uppercase + tracked so it
                # reads as a header and not just another row.
                '<thead><tr style="background-color:var(--bg-track);border-bottom:2px solid var(--accent);'
                'color:var(--text-primary);font-weight:800;text-align:left;font-size:13px;'
                'letter-spacing:0.08em;text-transform:uppercase;">'
                f'<th style="padding:10px 12px;border-radius:6px 0 0 0;">{cut_label}</th>'
                f'<th style="padding:10px 12px;text-align:right;">Contribution to TP</th>'
                f'<th style="padding:10px 12px;text-align:right;">Share of {_tier_disp}</th>'
                f'<th style="padding:10px 12px;text-align:left;border-radius:0 6px 0 0;">Issue tags</th>'
                '</tr></thead><tbody>'
            )
            # Pass 26.2 / 28.2: render the spreadsheet drivers as inline chips.
            # When Cut by = Strategy, the chips come straight from
            # STRATEGY_REAL_DATA[strategy]. For other cuts (Portfolio,
            # Investment Type, Asset type), we aggregate chips across every
            # sub-strategy that contributes Amber/Red MV to this row's bucket,
            # ranked by how many of those strategies the chip appears in.
            def _row_chips(name):
                if cut_col == "sub_strategy_name":
                    contrib_strats = [str(name)]
                else:
                    contrib_strats = (
                        tier_pf[tier_pf[cut_col] == name]["sub_strategy_name"]
                        .dropna().astype(str).unique().tolist()
                    )
                chip_counts = {}
                chip_order  = []
                for s in contrib_strats:
                    meta = STRATEGY_REAL_DATA.get(s, {}) or {}
                    for c in (meta.get("chips") or []):
                        if c not in chip_counts:
                            chip_counts[c] = 0
                            chip_order.append(c)
                        chip_counts[c] += 1
                chips = sorted(chip_order,
                               key=lambda c: (-chip_counts[c], chip_order.index(c)))
                if not chips:
                    return '<span style="font-size:11.5px;color:var(--text-subtle);font-style:italic;">—</span>'
                return "".join(
                    f'<span style="display:inline-block;border:1px solid {_tag_color(c)};color:{_tag_color(c)};'
                    f'background:transparent;padding:2px 8px;border-radius:10px;font-size:11px;'
                    f'font-weight:600;margin:0 4px 4px 0;white-space:nowrap;">{c}</span>'
                    for c in chips[:3]
                )
            for _, r in non_zero.iterrows():
                wt = "400"  # uniform weight; the contribution % column already encodes magnitude
                table_html += (
                    f'<tr style="border-bottom:1px solid var(--border-default);">'
                    f'<td style="padding:9px 12px;color:var(--text-primary);font-weight:{wt};">{r[cut_col]}</td>'
                    f'<td style="padding:9px 12px;text-align:right;color:var(--text-primary);font-variant-numeric:tabular-nums;font-weight:500;">{r["contrib_pct"]:.2f}%</td>'
                    f'<td style="padding:9px 12px;text-align:right;color:var(--text-soft);font-variant-numeric:tabular-nums;">{r["pct_of_tier"]:.0f}%</td>'
                    f'<td style="padding:9px 12px;text-align:left;">{_row_chips(r[cut_col])}</td>'
                    f'</tr>'
                )
            # The "(no contribution)" catch-all row was removed — see TP version above.
            table_html += '</tbody></table>'
            st.markdown(table_html, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════
    # Section C: ACTION PLANS — redesigned in Pass 11
    # Two clear sub-cards: Strategic focus (where to invest effort)
    # + Instrument-level actions (which specific names to chase).
    # ══════════════════════════════════════════════════════════════════════
    st.markdown('<div style="height:22px;"></div>', unsafe_allow_html=True)

    # ── Headline: breach summary for this group ───────────────────────────
    breaching = children[children["any_breach"]]
    n_br = len(breaching)
    if n_br > 0:
        names = ", ".join(breaching["sub_strategy_name"].tolist())
        driver = breaching.iloc[0].get("breach_reason") or ""
        suggested = breaching.iloc[0].get("suggested_action") or ""
        headline_bits = [f"{n_br} strateg{'y' if n_br==1 else 'ies'} breaching Amber + Red limit ({names})"]
        if driver:    headline_bits.append(f"driver: <b>{driver}</b>")
        if suggested: headline_bits.append(f"suggested action: <b>{suggested}</b>")
        headline_html = " &middot; ".join(headline_bits)
        headline_icon = '<span style="color:var(--breach-text);font-size:18px;">\u26A0</span>'
    else:
        headline_html = "All strategies within tolerance — no breach actions required."
        headline_icon = '<span style="color:var(--ok-text);font-size:18px;">\u2713</span>'

    # Scope chip — reflects the Scope dropdown picked in the Details section.
    _ap_scope_now = st.session_state.get("sd_scope", "Whole group")
    _scope_label = sel if _ap_scope_now == "Whole group" else _ap_scope_now
    scope_chip = (
        f'<span style="display:inline-block;font-size:11px;font-weight:700;letter-spacing:0.08em;'
        f'text-transform:uppercase;color:var(--accent);background:var(--accent-tint-bg);'
        f'border:1px solid var(--accent);padding:3px 9px;border-radius:10px;margin-left:8px;'
        f'vertical-align:middle;" title="Set the scope via the Scope dropdown in the Details section above.">'
        f'Scope: {_scope_label}</span>'
    )
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;flex-wrap:wrap;">'
        f'{headline_icon}'
        f'<span style="font-size:20px;font-weight:700;color:var(--text-primary);">Action plans for {sel}</span>'
        f'{scope_chip}'
        f'</div>'
        f'<p style="font-size:13px;color:var(--text-muted);margin:0 0 18px 30px;">{headline_html}</p>',
        unsafe_allow_html=True,
    )

    # ── Compute the Amber+Red instrument slice + impact ───────────────────
    # Action Plans honours the Scope dropdown set in the Details section above
    # (Pass 11.3): if user narrowed to a specific Strategy, this filters too.
    ap_scope = st.session_state.get("sd_scope", "Whole group")
    inst_all = instruments_df[(instruments_df["strategy_id"] == sid) &
                              (instruments_df["tier"].isin(["Amber", "Red"]))].copy()
    if ap_scope != "Whole group":
        inst_all = inst_all[inst_all["sub_strategy_name"] == ap_scope]
    if inst_all.empty:
        st.info("No Amber or Red instruments in this Strategy Group — nothing to action.")
    else:
        strat_mv_map  = dict(zip(children["sub_strategy_id"], children["total_mv"]))
        strat_thr_map = dict(zip(children["sub_strategy_id"], children["threshold_cum"]))
        def _impact(row):
            smv = float(strat_mv_map.get(row["sub_strategy_id"], 0) or 0)
            thr = float(strat_thr_map.get(row["sub_strategy_id"], 0) or 0)
            if smv <= 0 or thr <= 0: return 0.0
            return (float(row["mv"]) / smv) / thr * 100
        inst_all["impact"] = inst_all.apply(_impact, axis=1)
        _reason_map = dict(zip(children["sub_strategy_id"], children["breach_reason"]))
        _action_map = dict(zip(children["sub_strategy_id"], children["suggested_action"]))
        inst_all["breach_reason"]    = inst_all["sub_strategy_id"].map(_reason_map).fillna("")
        # Pass 14 (item 5): per-instrument varied action — pick from the pool
        # keyed on breach_reason; deterministic by instrument_id hash so the
        # column reads as a real punch list, not "Awaiting next Q-end NAV" x N.
        def _pick_action(r):
            reason = r["breach_reason"] or ""
            default = _action_map.get(r["sub_strategy_id"], "") or ""
            pool = SUGGESTED_ACTION_POOL.get(reason)
            if not pool:
                return default
            iid = str(r.get("instrument_id", r.get("instrument_name", "")))
            return pool[sum(ord(c) for c in iid) % len(pool)]
        inst_all["suggested_action"] = inst_all.apply(_pick_action, axis=1)

        # ════════════════════════════════════════════════════════════════
        # CARD 1 — STRATEGIC FOCUS
        # ════════════════════════════════════════════════════════════════
        # Label + Group-by on one compact row, hugging the table below.
        st.markdown(
            '<p style="font-size:11px;font-weight:700;letter-spacing:0.12em;'
            'text-transform:uppercase;color:var(--text-muted);margin:14px 0 4px 0;">'
            'Strategic focus</p>',
            unsafe_allow_html=True,
        )
        _sf_c1, _sf_spacer = st.columns([2, 5])
        with _sf_c1:
            ap_cut = st.selectbox(
                "Group by",
                ["Missing Field", "Investment Type", "Portfolio"],
                key=f"ap_cut_{sid}",
                label_visibility="collapsed",
            )
        weight_eff = False   # toggle dropped per pass 11.1 — kept var for downstream branches

        # Aggregate per Group-by cut
        agg_rows = []
        if ap_cut == "Missing Field":
            for _, r in inst_all.iterrows():
                fields = list(r.get("missing_fields_list") or [])
                if not fields: continue
                share = float(r["impact"]) / max(len(fields), 1)
                for f in fields:
                    agg_rows.append({"bucket": f, "impact_share": share,
                                     "instrument_id": r["instrument_id"],
                                     "is_solo": (len(fields) == 1)})
        else:
            for _, r in inst_all.iterrows():
                if   ap_cut == "Investment Type":   bucket = r.get("instrument_type") or "Unknown"
                elif ap_cut == "Portfolio":         bucket = r.get("portfolio_name") or "Unknown"
                else:                                bucket = "Unassigned"
                agg_rows.append({"bucket": bucket, "impact_share": float(r["impact"]),
                                 "instrument_id": r["instrument_id"], "is_solo": False})
        agg_src = pd.DataFrame(agg_rows) if agg_rows else pd.DataFrame(
            columns=["bucket","impact_share","instrument_id","is_solo"])

        if agg_src.empty:
            st.info("Not enough data to aggregate — try a different group-by.")
        else:
            grouped = agg_src.groupby("bucket").agg(
                impact=("impact_share", "sum"),
                n=("instrument_id", "nunique"),
                quick_wins=("is_solo", "sum"),
            ).reset_index().sort_values("impact", ascending=False)
            if ap_cut == "Missing Field":
                grouped["effort"] = grouped["bucket"].map(_FIELD_EFFORT).fillna("Medium")
            else:
                grouped["effort"] = ""

            # Top opportunity callout
            top_row = grouped.iloc[0]
            top_label = str(top_row["bucket"])
            top_imp   = float(top_row["impact"])
            top_n     = int(top_row["n"])
            st.markdown(
                f'<div style="background:var(--accent-tint-bg);border-left:3px solid var(--accent);'
                f'padding:12px 16px;border-radius:4px;margin:10px 0 14px;">'
                f'<p style="font-size:11px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;'
                f'color:var(--accent);margin:0 0 4px 0;">\u2605 Top opportunity</p>'
                f'<p style="font-size:14px;color:var(--text-primary);margin:0;">'
                f'Fix <b>{top_label}</b> across <b>{top_n}</b> instruments \u2192 '
                f'<b style="color:var(--accent);">\u2212{top_imp:.0f}%</b> on Amber + Red utilisation'
                f'</p></div>',
                unsafe_allow_html=True,
            )

            # Pass 17.9: aligned column name "Impact (%)" with the Instrument-level
            # Actions table — same computation (summed per bucket). Format locks 2dp.
            disp_cols = {
                "Missing Field":     {"bucket":"Field","impact":"Impact (%)","n":"# instruments","effort":"Effort"},
                "Investment Type":   {"bucket":"Investment Type","impact":"Impact (%)","n":"# instruments"},
                "Portfolio":         {"bucket":"Portfolio","impact":"Impact (%)","n":"# instruments"},
            }[ap_cut]
            keep_cols = [c for c in disp_cols.keys() if c in grouped.columns]
            tbl = grouped[keep_cols].copy()
            tbl["impact"] = tbl["impact"].round(2)
            tbl = tbl.rename(columns=disp_cols)
            # Pass 17.11: replace pandas index with a 1-based running rank.
            # Reset_index then insert a narrow "#" column at position 0 so the
            # numbers refresh sequentially every time the user switches Group by.
            tbl = tbl.reset_index(drop=True)
            tbl.insert(0, "#", range(1, len(tbl) + 1))
            styled_tbl = (
                tbl.style
                   .hide(axis="index")
                   .format({"Impact (%)": "{:.2f}"})
                   .set_table_styles([
                       # Narrow the rank column so it doesn't waste space
                       {"selector": "th.col0, td.col0", "props": "width:48px;text-align:center;color:var(--text-muted);font-weight:600;"},
                   ])
            )
            render_themed_table(styled_tbl)

            # Cumulative impact footer
            cumul = grouped["impact"].cumsum().tolist()
            footer_bits = []
            for n_top in (1, 3, 5):
                if n_top <= len(cumul):
                    footer_bits.append(f"top {n_top} \u2192 <b style=\"color:var(--accent);\">\u2212{cumul[n_top-1]:.0f}%</b>")
            footer = " &middot; ".join(footer_bits)
            st.markdown(
                f'<p style="font-size:12px;color:var(--text-muted);margin:8px 0 0 0;">'
                f'<b>Cumulative impact:</b> fix {footer}'
                f'</p>',
                unsafe_allow_html=True,
            )

            # Stash the filter mapping so the Instrument card below can use the cut value
            _last_cut = ap_cut
            _grouped_bucket_list = grouped["bucket"].astype(str).tolist()

        st.markdown(
            '<div style="height:32px;margin:24px 0 8px 0;border-top:2px solid var(--border-strong);"></div>',
            unsafe_allow_html=True,
        )

        # ════════════════════════════════════════════════════════════════
        # CARD 2 — INSTRUMENT-LEVEL ACTIONS
        # ════════════════════════════════════════════════════════════════
        # Build display dataframe
        inst = inst_all.copy()

        # Pass 14 (item 4) + Pass 15: chip strip with N-missing count badge AND
        # per-chip colour by tier: red = blocks Amber-tier, amber = blocks Green-tier.
        # Uses missing_tiers (parallel list to missing_fields_list).
        def _missing_chips(lst, tiers=None):
            # Pass 17.20: chip colours decoupled from Red/Amber tier palette — the
            # tier system already uses those colours for limits / exposure, and
            # reusing them for "missing field" was reading as urgency / breach.
            # Now: indigo accent for the count badge, slate for each field chip.
            # tiers list kept in the tooltip so the Amber-blocker vs Green-blocker
            # distinction is still discoverable on hover.
            lst = list(lst or [])
            if not lst:
                return ""
            tiers = list(tiers or []) + ["Green"] * max(0, len(lst) - len(list(tiers or [])))
            n = len(lst)
            # Pass 17.21: solid violet count badge + outlined teal field chips —
            # both colours completely outside the dashboard's existing palette
            # (red/amber for tiers, blue for accents) so they read as their own
            # visual category and pop against the table background in both themes.
            # Pass 29: violet/teal palette now comes from theme tokens so the
            # chips re-skin between cream and dark mode.
            count_chip = (
                f'<span style="background:var(--chip-violet-bg);color:#FFFFFF;font-size:11px;'
                f'padding:2px 8px;border-radius:10px;font-weight:700;margin-right:6px;'
                f'letter-spacing:0.02em;">'
                f'{n} missing</span>'
            )
            def _one(f, t):
                tip = "Blocks Amber tier" if t == "Amber" else "Blocks Green tier"
                return (f'<span title="{tip}" style="background:var(--chip-teal-bg);'
                        f'color:var(--chip-teal-fg);border:1.5px solid var(--chip-teal-border);font-size:11px;'
                        f'padding:1px 7px;border-radius:10px;margin-right:4px;'
                        f'display:inline-block;cursor:help;font-weight:500;">{f}</span>')
            field_chips = "".join(_one(f, t) for f, t in zip(lst, tiers))
            return count_chip + field_chips

        inst["_missing_chips_html"] = inst.apply(
            lambda r: _missing_chips(r.get("missing_fields_list"), r.get("missing_tiers")),
            axis=1,
        )

        disp_base = inst[["instrument_name", "portfolio_name", "sub_strategy_name",
                          "instrument_type", "tier", "_missing_chips_html",
                          "breach_reason", "suggested_action", "sourcing_rationale",
                          "impact"]].copy()
        impact_col = "Impact (%)"
        disp_base.columns = ["Instrument", "Portfolio", "Strategy", "Type",
                             "Tier", "Missing Fields", "Reason", "Action",
                             "Sourcing Rationale", impact_col]

        # Title row — full width
        st.markdown(
            '<p style="font-size:18px;font-weight:700;color:var(--text-primary);margin:6px 0 2px 0;">'
            'Instrument-level Actions</p>'
            f'<p style="font-size:12px;color:var(--text-muted);margin:0 0 8px 0;">'
            f'{len(disp_base)} Amber + Red holdings \u00b7 scroll for more</p>',
            unsafe_allow_html=True,
        )

        # Controls row — Filter + Sort + small Export icon, flush right, close to the table
        _ic1, _ic2, _ic3 = st.columns([3, 3, 1])
        with _ic1:
            try:
                filter_opts = ["(All)"] + _grouped_bucket_list
            except NameError:
                filter_opts = ["(All)"]
            ap_filter = st.selectbox(f"Filter by {ap_cut}", filter_opts, key=f"ap_filter_{sid}_{ap_cut}")
        with _ic2:
            _isort_col = st.selectbox("Sort by", disp_base.columns.tolist(),
                                       index=int(disp_base.columns.get_loc(impact_col)),
                                       key=f"inst_sort_col_{sid}")
        with _ic3:
            group_amber_red = instruments_df[
                (instruments_df["strategy_id"] == sid) &
                (instruments_df["tier"].isin(["Amber", "Red"]))
            ][[
                "strategy_name", "sub_strategy_name", "portfolio_name",
                "instrument_name", "instrument_type", "product_type",
                "investment_bucket", "tier", "mv", "missing_fields",
                "sourcing_rationale", "last_updated",
            ]].copy()
            group_amber_red.columns = [
                "Strategy Group", "Strategy", "Portfolio", "Instrument",
                "Instrument Type", "Product Type", "Investment Bucket",
                "Tier", "MV (\u00A3M)", "Missing Fields",
                "Sourcing Rationale", "Last Updated",
            ]
            group_amber_red["Last Updated"] = pd.to_datetime(group_amber_red["Last Updated"]).dt.strftime("%Y-%m-%d")
            csv_bytes = group_amber_red.to_csv(index=False).encode("utf-8")
            _grp_label = str(children.iloc[0].get("strategy_name", "group")) if len(children) else "group"
            st.markdown('<div style="height:28px;"></div>', unsafe_allow_html=True)
            st.download_button(
                "\u2B07",
                data=csv_bytes,
                file_name=f"amber_red_instruments_{_grp_label.replace(' ', '_')}.csv",
                mime="text/csv",
                key=f"ap_export_{sid}",
                help=f"Export {len(group_amber_red)} Amber + Red instruments as CSV.",
                use_container_width=False,
            )
        _isort_asc = False

        # Apply filter from the toolbar (uses the same Group-by dimension)
        if ap_filter != "(All)":
            if ap_cut == "Missing Field":
                inst = inst[inst["missing_fields_list"].apply(lambda lst: ap_filter in (lst or []))]
            elif ap_cut == "Investment Type":
                inst = inst[inst["instrument_type"] == ap_filter]
            elif ap_cut == "Portfolio":
                inst = inst[inst["portfolio_name"] == ap_filter]
            # rebuild disp from filtered inst — re-derive the chip column
            inst["_missing_chips_html"] = inst.apply(
                lambda r: _missing_chips(r.get("missing_fields_list"), r.get("missing_tiers")),
                axis=1,
            )
            disp_base = inst[["instrument_name", "portfolio_name", "sub_strategy_name",
                              "instrument_type", "tier", "_missing_chips_html",
                              "breach_reason", "suggested_action", "sourcing_rationale",
                              "impact"]].copy()
            disp_base.columns = ["Instrument", "Portfolio", "Strategy", "Type",
                                 "Tier", "Missing Fields", "Reason", "Action",
                                 "Sourcing Rationale", impact_col]

        # Sort + render. Pass 14 (item 4): Missing Fields cells carry HTML chips —
        # Styler must NOT escape them.
        # Pass 17.13: prepend a 1-based "#" running rank so the first column
        # shows clean sequential numbering instead of the bold black pandas
        # index. Numbers refresh on every sort / filter / group change.
        disp_base = disp_base.sort_values(by=_isort_col, ascending=_isort_asc, kind="stable").reset_index(drop=True)
        disp_base.insert(0, "#", range(1, len(disp_base) + 1))
        try:
            styled = apply_tier_style(disp_base.style, "Tier").format(
                {impact_col: "{:.2f}", "Missing Fields": lambda v: v},
                escape=None,
            )
        except TypeError:
            # Older pandas without escape= param: fall back, chips still render
            # because to_html() doesn't escape Styler output by default.
            styled = apply_tier_style(disp_base.style, "Tier").format({impact_col: "{:.2f}"})
        # Hide the pandas default index + narrow the # rank column so it doesn't
        # waste space and matches the Strategic Focus aggregation table layout.
        styled = styled.hide(axis="index").set_table_styles([
            {"selector": "th.col0, td.col0", "props": "width:48px;text-align:center;color:var(--text-muted);font-weight:600;"},
        ], overwrite=False)
        render_themed_table(styled, max_height=600)
        st.caption("Impact = % drop in this Strategy\u2019s Amber + Red utilisation if the holding is resolved to Green.")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — Instrument Detail
# ═══════════════════════════════════════════════════════════════════════════════

def page_instrument_detail(instruments_df):
    st.title("🏦 Instrument / Investment Detail")

    # Scoped to the Strategy Group selected on the Strategy Detail tab (shared key).
    groups = list(dict.fromkeys(instruments_df["strategy_name"].tolist()))
    if st.session_state.get("sd_sel") not in groups:
        st.session_state["sd_sel"] = groups[0]
    gcol, _gsp = st.columns([1, 2])
    with gcol:
        grp = st.selectbox("Strategy Group", groups, key="sd_sel",
                           help="Inherited from the Strategy Detail tab — change it here or there.")
    st.caption(f"Holding-level transparency view for {grp} — filter by Strategy, analyse, and export.")

    scoped = instruments_df[instruments_df["strategy_name"] == grp]
    child_opts = list(dict.fromkeys(scoped["sub_strategy_name"].tolist()))

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        sel_subs = st.multiselect("Strategy", child_opts, default=child_opts, key=f"id_sub_{grp}",
                                  help="One or more Strategies within this Group.")
    with c2:
        tier_f = st.multiselect("Tier", ["Green", "Amber", "Red"],
                                default=["Amber", "Red"], key="id_tier")
    with c3:
        all_fields = sorted({f for lst in scoped["missing_fields_list"] for f in lst})
        miss_f = st.multiselect("Missing Field", all_fields, key="id_miss")
    with c4:
        asset_types = ["All"] + sorted(scoped["asset_type"].unique())
        sel_at = st.selectbox("Asset Type", asset_types, key="id_at")

    df = scoped.copy()
    if sel_subs:        df = df[df["sub_strategy_name"].isin(sel_subs)]
    if tier_f:          df = df[df["tier"].isin(tier_f)]
    if miss_f:          df = df[df["missing_fields_list"].apply(lambda l: any(f in l for f in miss_f))]
    if sel_at != "All": df = df[df["asset_type"] == sel_at]

    col_m1, col_m2 = st.columns(2)
    col_m1.metric("Instruments", str(len(df)))
    tier_counts = df["tier"].value_counts().to_dict()
    col_m2.markdown(
        '<div style="background:var(--bg-surface);border-radius:6px;padding:0.85rem 1rem;height:72px;">'
        '<div style="color:var(--text-muted);font-size:13px;margin-bottom:6px;">Tier breakdown (filtered)</div>'
        '<div style="font-size:15px;font-weight:500;color:var(--text-primary);">'
        f'<span style="color:var(--color-ok);">●</span> {tier_counts.get("Green",0)} &nbsp;'
        f'<span style="color:var(--amber-tier);">●</span> {tier_counts.get("Amber",0)} &nbsp;'
        f'<span style="color:var(--red-tier);">●</span> {tier_counts.get("Red",0)}'
        '</div></div>',
        unsafe_allow_html=True
    )

    disp = df[["instrument_name", "portfolio_name", "sub_strategy_name",
               "asset_type", "tier", "mv_pct_of_strategy",
               "missing_fields", "region", "sector", "last_updated"]].copy()
    disp.columns = ["Instrument", "Fund", "Strategy", "Type", "Tier",
                    "MV % of Group", "Missing Fields", "Region", "Sector", "Last Updated"]
    disp["MV % of Group"] = disp["MV % of Group"].round(2)
    disp["Last Updated"]  = disp["Last Updated"].dt.strftime("%Y-%m-%d")

    st.dataframe(apply_tier_style(disp.style, "Tier"),
                 use_container_width=True, height=460)

    buf = BytesIO()
    disp.to_excel(buf, index=False, engine="openpyxl")
    buf.seek(0)
    st.download_button(
        label="📥 Export to Excel",
        data=buf,
        file_name=f"instrument_detail_{grp.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — Data Quality
# ═══════════════════════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE — Action Tracker (Pass 3b)
# ═══════════════════════════════════════════════════════════════════════════════

_STATUS_STYLE = {
    # Pass 27.8 / 29: 3-column Kanban — colours read from theme tokens so the
    # whole board flips between cream and dark modes automatically.
    "Recommended Action Plan": ("var(--status-rec-fg)",  "var(--status-rec-bg)",  "var(--status-rec-border)"),
    "In Progress":             ("var(--status-prog-fg)", "var(--status-prog-bg)", "var(--status-prog-border)"),
    "Completed":               ("var(--status-done-fg)", "var(--status-done-bg)", "var(--status-done-border)"),
    # Legacy aliases kept for any back-compat callsite — map onto same tokens.
    "No initiative":           ("var(--status-rec-fg)",  "var(--status-rec-bg)",  "var(--status-rec-border)"),
    "Planned / TBD":           ("var(--status-rec-fg)",  "var(--status-rec-bg)",  "var(--status-rec-border)"),
    "In progress":             ("var(--status-done-fg)", "var(--status-done-bg)", "var(--status-done-border)"),
    "Planned":                 ("var(--text-muted)", "var(--bg-track)", "var(--border-default)"),
    "Done":                    ("var(--color-ok)",   "var(--status-done-bg)", "var(--status-done-border)"),
}

def _action_card_html(row):
    """Pass 14: owner is a team (no names); add Est. impact chip;
    overdue colour-coding splits Amber (<60d past) vs Red (>=60d past)."""
    fg, bg, br = _STATUS_STYLE.get(row["status"], _STATUS_STYLE["Planned"])
    days = (row["target_date"] - datetime.now().date()).days
    if row["status"] == "Done":
        right_text = f"Closed {abs(days)}d ago" if days < 0 else "Closed today"
        right_color = "var(--text-subtle)"
    elif days < 0:
        # Split overdue into Amber (<60d past) vs Red (>=60d past)
        right_text = f"Overdue {abs(days)}d"
        right_color = ("var(--breach-text)" if abs(days) >= 60 else "var(--alert-text)")
    elif days <= 14:
        right_text = f"Due in {days}d"
        right_color = "var(--alert-text)"
    else:
        right_text = f"Due in {days}d"
        right_color = "var(--text-muted)"

    # Estimated impact chip \u2014 green emphasis since these are improvements.
    # Pass 29: bg/border use done-status tokens so the chip dims in dark mode.
    impact = float(row.get("impact_pp", 0) or 0)
    impact_chip = (
        f'<span style="background:var(--status-done-bg);color:var(--status-done-fg);padding:2px 8px;'
        f'border-radius:10px;font-size:10px;font-weight:700;letter-spacing:0.04em;'
        f'text-transform:uppercase;border:1px solid var(--status-done-border);">'
        f'\u2212{impact:.0f}%</span>'
    ) if impact > 0 else ""

    return (
        f'<div style="background:{bg};border:1px solid {br};border-radius:8px;padding:12px 14px;margin-bottom:10px;">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;gap:6px;margin-bottom:6px;flex-wrap:wrap;">'
        f'<div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;">'
        f'<span style="background:{bg};color:{fg};border:1px solid {br};padding:2px 8px;border-radius:10px;font-size:10px;'
        f'font-weight:700;letter-spacing:0.04em;text-transform:uppercase;">{row["status"]}</span>'
        f'{impact_chip}'
        f'</div>'
        f'<span style="font-size:11px;color:{right_color};font-weight:600;">{right_text}</span>'
        f'</div>'
        f'<div style="font-size:13px;font-weight:600;color:var(--text-primary);line-height:1.4;margin-bottom:6px;">{row["title"]}</div>'
        f'<div style="font-size:11px;color:var(--text-muted);margin-bottom:4px;">'
        f'<b>Strategy:</b> {row["strategy_name"]} \u00b7 <b>Owner:</b> {row["owner_team"]}'
        f'</div>'
        f'<div style="font-size:11px;color:var(--text-soft);margin-bottom:4px;">Target completion date: {row["target_date"].strftime("%d %b %Y")}</div>'
        f'<div style="font-size:11px;color:var(--text-subtle);font-style:italic;padding-top:6px;border-top:1px dashed var(--border-default);margin-top:6px;line-height:1.5;">'
        f'Update ({row["last_update"].strftime("%d %b")}): {row["last_update_note"]}'
        f'</div>'
        f'</div>'
    )


def _most_improved_widget(sub_history_df, sub_strat_agg):
    """Top strategies by green_pct improvement over last 3 months."""
    if sub_history_df is None or sub_history_df.empty: return ""
    # Latest snapshot
    latest_date = sub_history_df["date"].max()
    earlier_date = latest_date - pd.Timedelta(days=90)
    latest = sub_history_df[sub_history_df["date"] == latest_date].set_index("sub_strategy_id")
    earlier = sub_history_df.iloc[(sub_history_df["date"] - earlier_date).abs().argsort()].drop_duplicates("sub_strategy_id").set_index("sub_strategy_id")
    # Use green = 100 - non_transparent_pct (the series already in percent)
    latest_green  = 100 - latest["non_transparent_pct"]
    earlier_green = 100 - earlier["non_transparent_pct"].reindex(latest_green.index)
    delta = (latest_green - earlier_green).dropna().sort_values(ascending=False)
    if delta.empty: return ""
    top3 = delta.head(3)
    # Map back to strategy name
    name_map = dict(zip(sub_strat_agg["sub_strategy_id"], sub_strat_agg["sub_strategy_name"]))
    cards = []
    for sid, d in top3.items():
        name = name_map.get(sid, sid)
        cur_green = float(latest_green.loc[sid])
        cards.append(
            f'<div style="flex:1;min-width:220px;background:rgba(39,174,96,0.08);border:1px solid rgba(39,174,96,0.3);'
            f'border-radius:8px;padding:14px 16px;">'
            f'<div style="font-size:10px;font-weight:600;color:var(--color-ok);letter-spacing:0.05em;'
            f'text-transform:uppercase;margin-bottom:4px;">\u2B50 Most Improved</div>'
            f'<div style="font-size:15px;font-weight:600;color:var(--text-primary);margin-bottom:4px;">{name}</div>'
            f'<div style="font-size:13px;color:var(--text-muted);">'
            f'Green % up <b style="color:var(--color-ok);">+{d:.0f}%</b> over last 3 months '
            f'<span style="color:var(--text-subtle);">(now {cur_green:.0f}% Green)</span>'
            f'</div>'
            f'</div>'
        )
    return (
        '<div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:18px;">' +
        "".join(cards) + '</div>'
    )


def page_action_tracker(action_items_df, sub_strat_agg, sub_history_df):
    _render_page_title("\U0001F3AF Action Tracker")
    st.caption("Transparency improvement workflow — initiatives owned by asset-department leads, with status and timelines.")

    # ── Filters ──────────────────────────────────────────────────────────────
    f1, f2, _f3 = st.columns([1, 1, 2])
    with f1:
        groups = ["All"] + sorted(action_items_df["strategy_group"].unique().tolist())
        f_group = st.selectbox("Strategy Group", groups, key="at_filter_group")
    with f2:
        owners = ["All"] + sorted(action_items_df["owner_team"].unique().tolist())
        f_owner = st.selectbox("Owner team", owners, key="at_filter_owner")

    aif = action_items_df.copy()
    if f_group != "All": aif = aif[aif["strategy_group"] == f_group]
    if f_owner != "All": aif = aif[aif["owner_team"]    == f_owner]

    if aif.empty:
        st.info("No action items match the current filters.")
        return

    # ── Kanban board ─────────────────────────────────────────────────────────
    # Pass 28.1: section subtitle now mirrors the Kanban column counts 1:1 and
    # ties back to the 'Active breaches' summary on Total Portfolio. Previously
    # the subtitle just read "{N} initiatives across the portfolio" which the
    # user couldn't reconcile against either the Kanban columns or the AI obs.
    # Pass 29.10: subtitle rewritten. Pass 28.1 promised a 1:1 reconciliation
    # with the TP "Active breaches" line, but Pass 29.10 removed the "No
    # initiative" placeholder cards from the Kanban — so the board now only
    # shows actively-tracked items. The breaching strategies without a plan
    # still surface on the A.I. Observations panel. Subtitle now explains
    # that split honestly instead of claiming a reconciliation that no
    # longer holds.
    _n_rec  = int((aif["status"] == "Recommended Action Plan").sum())
    _n_prog = int((aif["status"] == "In Progress").sum())
    _n_open = _n_rec + _n_prog
    _breach_names    = set(sub_strat_agg[sub_strat_agg["any_breach"]]["sub_strategy_name"]) \
                       if "any_breach" in sub_strat_agg.columns else set()
    _n_breaching     = len(_breach_names)
    _tracked_breach  = set(aif[aif["status"] != "Completed"]["strategy_name"]) & _breach_names
    _n_no_plan       = max(0, _n_breaching - len(_tracked_breach))
    _no_plan_html    = (
        f' <span style="color:var(--breach-text);"><b>{_n_no_plan}</b> additional '
        f'breaching {"strategy has" if _n_no_plan==1 else "strategies have"} '
        f'no tracked initiative yet</span> '
        f'(see the <b>Active breaches</b> summary on Total Portfolio).'
    ) if _n_no_plan > 0 else ""
    _sub_html = (
        f'<b>{_n_open}</b> initiative{"" if _n_open==1 else "s"} tracked — '
        f'<b>{_n_prog}</b> In Progress, <b>{_n_rec}</b> Recommended Action Plan.'
        f'{_no_plan_html}'
    )
    st.markdown(_section_band("Action Plan Board", _sub_html), unsafe_allow_html=True)
    # Pass 19.1: planned integration note — actions are read-only in the
    # prototype; production deployment will sync with the team's tracker.
    st.markdown(
        '<div style="background:var(--accent-tint-bg);border-left:3px solid var(--accent);'
        'border-radius:4px;padding:10px 14px;margin:-4px 0 14px 0;font-size:13px;'
        'color:var(--text-soft);line-height:1.5;">'
        '<b style="color:var(--accent);">ⓘ Integration note</b> &nbsp;·&nbsp; '
        'Action items are read-only in this prototype. In production the board will link '
        'to the team’s existing tracker (<b>Jira</b> or <b>Dataquest</b>) — cards will '
        'sync status, owner, target date, and updates directly from the source of truth, '
        'and new actions will be created from there.'
        '</div>',
        unsafe_allow_html=True,
    )
    # Pass 27.8: 3-column Kanban — Recommended Action Plan / In Progress / Completed.
    statuses = ["Recommended Action Plan", "In Progress", "Completed"]
    col_a, col_b, col_c = st.columns(3)
    for col, status in zip([col_a, col_b, col_c], statuses):
        with col:
            n_in_col = int((aif["status"] == status).sum())
            fg = _STATUS_STYLE[status][0]
            st.markdown(
                f'<div style="margin-bottom:10px;padding-bottom:8px;border-bottom:2px solid {fg};">'
                f'<span style="font-size:14px;font-weight:600;color:{fg};letter-spacing:0.02em;">{status}</span>'
                f'<span style="font-size:12px;color:var(--text-muted);margin-left:8px;">{n_in_col} items</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
            col_items = aif[aif["status"] == status].sort_values("target_date")
            for _, row in col_items.iterrows():
                st.markdown(_action_card_html(row), unsafe_allow_html=True)
            if col_items.empty:
                st.caption("(none)")

    # ── Tabular fallback / export ────────────────────────────────────────────
    with st.expander("\U0001F4CB Full list view (sortable + export)", expanded=False):
        disp = aif[["action_id","title","strategy_group","strategy_name","owner_team","impact_pp",
                    "status","linked_reason","target_date","last_update","last_update_note"]].copy()
        disp["impact_pp"] = disp["impact_pp"].apply(lambda v: f"−{float(v):.1f}%")
        disp.columns = ["ID","Title","Strategy Group","Strategy","Owner Team","Est. impact","Status",
                        "Linked driver","Target","Last update","Update note"]
        st.dataframe(disp, use_container_width=True, height=360)
        csv = disp.to_csv(index=False).encode("utf-8")
        st.download_button("\u2B07 Export action plan list (CSV)", data=csv,
                           file_name="action_plan_list.csv", mime="text/csv",
                           key="at_export")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE — Data Quality
# ═══════════════════════════════════════════════════════════════════════════════

def page_data_quality(portfolios_df, instruments_df, audit_df):
    _render_page_title("\U0001F4CB Data Quality & Operational View")

    # Scoped to the Strategy Group selected on the Strategy Detail tab (shared key).
    groups = list(dict.fromkeys(portfolios_df["strategy_name"].tolist()))
    if st.session_state.get("sd_sel") not in groups:
        st.session_state["sd_sel"] = groups[0]
    gcol, _gsp = st.columns([1, 2])
    with gcol:
        grp = st.selectbox("Strategy Group", groups, key="sd_sel",
                           help="Inherited from the Strategy Detail tab — change it here or there.")
    st.caption(f"Operational data quality for {grp}, drillable to its Strategies.")

    pf  = portfolios_df[portfolios_df["strategy_name"] == grp]
    ins = instruments_df[instruments_df["strategy_name"] == grp]
    aud0 = audit_df[audit_df["strategy_name"] == grp]

    tab1, tab2, tab3 = st.tabs(["Missing Data", "Data Freshness", "Audit Trail"])

    # ── Tab 1: Missing Data ───────────────────────────────────────────────────
    with tab1:
        col_l, col_r = st.columns(2)
        miss_records = [
            {"field": f, "strategy": r["sub_strategy_name"], "tier": r["tier"]}
            for _, r in ins.iterrows() for f in r["missing_fields_list"]
        ]
        miss_df = pd.DataFrame(miss_records) if miss_records else pd.DataFrame(
            columns=["field", "strategy", "tier"])

        with col_l:
            st.markdown('<p class="section-title">Missing Fields by Type & Tier</p>', unsafe_allow_html=True)
            if not miss_df.empty:
                cnt = miss_df.groupby(["field", "tier"]).size().reset_index(name="count")
                fig = px.bar(cnt, x="field", y="count", color="tier",
                              color_discrete_map=TIER_COLORS,
                              labels={"field": "Missing Field", "count": "Occurrences"})
                fig.update_layout(**DARK_LAYOUT, height=320,
                                   margin=dict(l=10, r=10, t=10, b=60), xaxis_tickangle=-30,
                                   legend=dict(orientation="h", yanchor="bottom", y=1.02, **DARK_LEGEND))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(f"No missing fields recorded in {grp}.")

        with col_r:
            st.markdown('<p class="section-title">Missing Fields by Strategy</p>', unsafe_allow_html=True)
            sm = (ins.groupby("sub_strategy_name")["missing_fields_list"]
                  .apply(lambda x: sum(len(l) for l in x))
                  .reset_index(name="missing_count").sort_values("missing_count"))
            if not sm.empty and sm["missing_count"].sum() > 0:
                _t = _theme()
                fig_sm = px.bar(sm, x="missing_count", y="sub_strategy_name", orientation="h",
                                 color="missing_count",
                                 color_continuous_scale=[_t["tier-green-bright"], _t["tier-amber-bright"], _t["tier-red-bright"]],
                                 labels={"missing_count": "Count", "sub_strategy_name": ""})
                fig_sm.update_layout(**DARK_LAYOUT, height=320, margin=dict(l=10, r=10, t=10, b=10),
                                      showlegend=False, coloraxis_showscale=False)
                st.plotly_chart(fig_sm, use_container_width=True)
            else:
                st.info("No missing fields to break down.")

        # ── Missing fields by Investment Bucket (DI Large/Small, CI Large/Small, FI) ──
        st.markdown('<p class="section-title">Missing Fields by Investment Bucket</p>', unsafe_allow_html=True)
        st.caption("DI = Direct Investment (incl. Mandates); CI = Co-investment; FI = Fund Investment. Large = private exposure > USD 200M; Small = private \u2264 USD 200M.")
        _bucket_order = ["DI Large", "DI Small", "CI Large", "CI Small", "FI", "DI", "CI", "Other"]
        ib_rows = []
        for _, r in ins.iterrows():
            for f in r["missing_fields_list"]:
                ib_rows.append({"investment_bucket": r["investment_bucket"], "tier": r["tier"], "field": f})
        ib_df = pd.DataFrame(ib_rows) if ib_rows else pd.DataFrame(columns=["investment_bucket","tier","field"])
        if not ib_df.empty:
            ib_cnt = ib_df.groupby(["investment_bucket","tier"]).size().reset_index(name="count")
            # Order by canonical bucket sequence, then drop empties
            present = [b for b in _bucket_order if b in ib_cnt["investment_bucket"].unique()]
            ib_cnt["investment_bucket"] = pd.Categorical(ib_cnt["investment_bucket"], categories=present, ordered=True)
            ib_cnt = ib_cnt.sort_values("investment_bucket")
            fig_ib = px.bar(ib_cnt, x="investment_bucket", y="count", color="tier",
                            color_discrete_map=TIER_COLORS,
                            labels={"investment_bucket": "Investment Bucket", "count": "Missing-field occurrences"})
            fig_ib.update_layout(**DARK_LAYOUT, height=300,
                                 margin=dict(l=10, r=10, t=10, b=40),
                                 legend=dict(orientation="h", yanchor="bottom", y=1.02, **DARK_LEGEND))
            st.plotly_chart(fig_ib, use_container_width=True)
        else:
            st.info(f"No missing fields recorded for {grp} \u2014 nothing to bucket.")

        st.markdown('<p class="section-title">Data Completeness Trend</p>', unsafe_allow_html=True)
        random.seed(7)
        dates = pd.date_range(end=datetime.now(), periods=12, freq="MS")
        comp  = [62 + i*2.8 + random.gauss(0, 1.2) for i in range(12)]
        comp_df = pd.DataFrame({"date": dates, "completeness": comp})
        fig_c = px.line(comp_df, x="date", y="completeness", markers=True,
                         labels={"completeness": "Completeness (%)", "date": ""},
                         color_discrete_sequence=[_theme()["tier-green-bright"]])
        fig_c.add_hline(y=90, line_dash="dot", line_color=_theme()["tier-amber-bright"],
                         annotation_text="Target 90%", annotation_position="bottom right")
        fig_c.update_layout(**DARK_LAYOUT, height=230, margin=dict(l=20, r=20, t=10, b=20))
        st.plotly_chart(fig_c, use_container_width=True)

    # ── Tab 2: Data Freshness ─────────────────────────────────────────────────
    with tab2:
        st.markdown('<p class="section-title">Freshness by Strategy</p>', unsafe_allow_html=True)
        fresh_s = pf.groupby("sub_strategy_name").agg(
            latest=("last_updated", "max"), n_ports=("portfolio_id", "count"),
            avg_miss=("missing_count", "mean"),
        ).reset_index()
        fresh_s["days_since"] = (datetime.now() - fresh_s["latest"]).dt.days
        fresh_s["status"] = fresh_s["days_since"].apply(
            lambda d: "🟢 Fresh" if d <= 30 else "🟠 Stale" if d <= 60 else "🔴 Overdue")
        fd = fresh_s[["sub_strategy_name", "n_ports", "latest", "days_since", "avg_miss", "status"]].copy()
        fd.columns = ["Strategy", "# Portfolios", "Last Refresh", "Days Since", "Avg Missing", "Status"]
        fd["Last Refresh"] = fd["Last Refresh"].dt.strftime("%Y-%m-%d")
        fd["Avg Missing"]  = fd["Avg Missing"].round(1)
        st.dataframe(fd, use_container_width=True)

        st.markdown("---")
        st.markdown('<p class="section-title">Freshness by Investment Bucket</p>', unsafe_allow_html=True)
        st.caption("DI = Direct Investment (incl. Mandates); CI = Co-investment; FI = Fund Investment. Large = private exposure > USD 200M; Small = private \u2264 USD 200M.")
        if "investment_bucket" in pf.columns and len(pf):
            fresh_ib = pf.groupby("investment_bucket").agg(
                latest=("last_updated", "max"),
                n_ports=("portfolio_id", "count"),
                avg_miss=("missing_count", "mean"),
                total_mv=("mv", "sum"),
            ).reset_index()
            fresh_ib["days_since"] = (datetime.now() - fresh_ib["latest"]).dt.days
            fresh_ib["status"] = fresh_ib["days_since"].apply(
                lambda d: "\U0001F7E2 Fresh" if d <= 30 else "\U0001F7E0 Stale" if d <= 60 else "\U0001F534 Overdue")
            _order = ["DI Large", "DI Small", "CI Large", "CI Small", "FI", "DI", "CI", "Other"]
            present = [b for b in _order if b in fresh_ib["investment_bucket"].unique()]
            fresh_ib["investment_bucket"] = pd.Categorical(fresh_ib["investment_bucket"], categories=present, ordered=True)
            fresh_ib = fresh_ib.sort_values("investment_bucket")
            fib = fresh_ib[["investment_bucket", "n_ports", "total_mv", "latest", "days_since", "avg_miss", "status"]].copy()
            fib.columns = ["Bucket", "# Portfolios", "Total MV (\u00A3M)", "Last Refresh", "Days Since", "Avg Missing", "Status"]
            fib["Last Refresh"] = pd.to_datetime(fib["Last Refresh"]).dt.strftime("%Y-%m-%d")
            fib["Avg Missing"]  = fib["Avg Missing"].round(1)
            fib["Total MV (\u00A3M)"] = fib["Total MV (\u00A3M)"].round(0)
            st.dataframe(fib, use_container_width=True)
        else:
            st.info("Investment bucket data not available.")

        st.markdown("---")
        st.markdown('<p class="section-title">Freshness by Portfolio</p>', unsafe_allow_html=True)
        fresh_p = pf[["sub_strategy_name", "portfolio_name", "tier",
                      "missing_count", "last_updated"]].copy()
        fresh_p["days_since"] = (datetime.now() - fresh_p["last_updated"]).dt.days
        fresh_p["status"] = fresh_p["days_since"].apply(
            lambda d: "🟢 Fresh" if d <= 30 else "🟠 Stale" if d <= 60 else "🔴 Overdue")
        fresh_p["last_updated"] = fresh_p["last_updated"].dt.strftime("%Y-%m-%d")
        fresh_p.columns = ["Strategy", "Portfolio", "Tier", "Missing Fields", "Last Updated", "Days Since", "Status"]
        sub_opts = ["All"] + list(dict.fromkeys(pf["sub_strategy_name"].tolist()))
        strat_filter = st.selectbox("Filter by Strategy", sub_opts, key="dq_sf")
        fp_disp = fresh_p if strat_filter == "All" else fresh_p[fresh_p["Strategy"] == strat_filter]
        st.dataframe(apply_tier_style(fp_disp.style, "Tier"), use_container_width=True, height=350)

    # ── Tab 3: Audit Trail ────────────────────────────────────────────────────
    with tab3:
        st.markdown('<p class="section-title">Tier Classification Change Log</p>', unsafe_allow_html=True)
        st.caption("Simulated history of transparency tier reclassifications")

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            sub_opts2 = ["All"] + list(dict.fromkeys(aud0["sub_strategy_name"].tolist()))
            at_strat = st.selectbox("Strategy", sub_opts2, key="at_s")
        with col_f2:
            at_tier = st.multiselect("New Tier", ["Green", "Amber", "Red"], key="at_t")

        aud = aud0.copy()
        if at_strat != "All": aud = aud[aud["sub_strategy_name"] == at_strat]
        if at_tier:           aud = aud[aud["new_tier"].isin(at_tier)]
        aud_disp = aud.sort_values("changed_at", ascending=False)[
            ["changed_at", "sub_strategy_name", "portfolio_name", "previous_tier", "new_tier", "changed_by", "reason"]
        ].copy()
        aud_disp["changed_at"] = aud_disp["changed_at"].dt.strftime("%Y-%m-%d")
        aud_disp.columns = ["Date", "Strategy", "Portfolio", "Previous Tier", "New Tier", "Changed By", "Reason"]
        if aud_disp.empty:
            st.info(f"No tier changes recorded for {grp}.")
        else:
            st.dataframe(apply_tier_style(aud_disp.style, "New Tier"),
                         use_container_width=True, height=420)
            buf = BytesIO()
            aud_disp.to_excel(buf, index=False, engine="openpyxl")
            buf.seek(0)
            st.download_button("📥 Export Audit Log", buf,
                                file_name=f"audit_trail_{grp.replace(' ', '_')}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — What-If Simulator
# ═══════════════════════════════════════════════════════════════════════════════

def page_whatif(sub_strat_agg, instruments_df, portfolios_df):
    """Pass 20.6: Stress Loss Simulator (Stagflation), polished dark + cream.
    Slider per Strategy = Assumed Amber + Red share for the simulation. Two
    quick-action buttons pre-fill all sliders at once (policy / current actuals).
    No mode toggle — the slider value IS the assumed share, full stop."""
    # Dark-mode card polish. Streamlit's default bordered container is too
    # subtle on a near-black background. Light/cream mode already looks fine
    # so we only inject the override when theme=dark.
    if st.session_state.get("theme_mode") == "dark":
        st.markdown("""
        <style>
        [data-testid="stVerticalBlockBorderWrapper"] {
          background: var(--bg-surface) !important;
          border: 1px solid var(--border-default) !important;
          border-radius: 10px !important;
          transition: border-color 0.15s ease, box-shadow 0.15s ease;
        }
        [data-testid="stVerticalBlockBorderWrapper"]:hover {
          border-color: var(--border-strong) !important;
          box-shadow: 0 2px 10px rgba(0,0,0,0.35);
        }
        [data-testid="stVerticalBlockBorderWrapper"] > div > div {
          padding: 4px 2px !important;
        }
        </style>
        """, unsafe_allow_html=True)
    _render_page_title("\U0001F52E What-If Simulator — Stress Loss")
    st.caption(
        "Stagflation scenario. Each slider sets the **assumed Amber + Red share** for that Strategy. "
        "Drag a slider or use the quick-action buttons to model a scenario."
    )

    # ── Per-instrument baseline + tier averages ─────────────────────────────
    inst = instruments_df.copy()
    inst["stress_contribution"] = inst["mv"] * inst["stress_loss_stagflation"]
    total_mv = float(inst["mv"].sum())
    baseline_loss_pct = inst["stress_contribution"].sum() / total_mv if total_mv > 0 else 0

    _g_all  = inst[inst["tier"] == "Green"]
    _ar_all = inst[inst["tier"].isin(["Amber","Red"])]
    port_avg_g  = (_g_all["mv"]  * _g_all["stress_loss_stagflation"]).sum()  / _g_all["mv"].sum()  if _g_all["mv"].sum()  > 0 else baseline_loss_pct
    port_avg_ar = (_ar_all["mv"] * _ar_all["stress_loss_stagflation"]).sum() / _ar_all["mv"].sum() if _ar_all["mv"].sum() > 0 else baseline_loss_pct

    # Pre-compute current Amber + Red share per sub_strategy_id (needed for the quick
    # actions and for the "(current X%)" hint on each card).
    _cur_ar = {}
    for _sid in sub_strat_agg["sub_strategy_id"].unique():
        _si = inst[inst["sub_strategy_id"] == _sid]
        _smv = float(_si["mv"].sum())
        _amv = float(_si[_si["tier"].isin(["Amber","Red"])]["mv"].sum()) if _smv > 0 else 0
        _cur_ar[_sid] = (_amv / _smv) if _smv > 0 else 0.0

    # ── Top toolbar: two quick actions + reset ──────────────────────────────
    rc1, rc2, _rc3 = st.columns([1.3, 1.3, 2])
    with rc1:
        if st.button("\U0001F4CB  Assume all at policy limit",
                      key="wi_apply_policy", use_container_width=True,
                      help="Worst case: every Strategy fills its current policy limit."):
            for _, _r in sub_strat_agg.iterrows():
                st.session_state[f"wi_lim_pct_{_r['sub_strategy_id']}"] = int(round(float(_r['threshold_cum'])*100))
            st.rerun()
    with rc2:
        if st.button("\U0001F4CD  Assume all at current actuals",
                      key="wi_apply_current", use_container_width=True,
                      help="No-change scenario: every Strategy stays at its current Amber + Red %."):
            for _sid, _share in _cur_ar.items():
                st.session_state[f"wi_lim_pct_{_sid}"] = int(round(_share * 100))
            st.rerun()

    # ── Per-Strategy limit cards — compact Kanban grid ──────────────────────
    st.markdown(_section_band("Assumed Amber + Red share per Strategy",
                              "One card per Strategy. Slider = the Amber + Red share fed into the stress-loss math."),
                unsafe_allow_html=True)

    # Theme-aware group tints. Light saturated palette pops on dark bg;
    # darker palette is needed on cream so the text is legible.
    _theme = st.session_state.get("theme_mode", "cream")
    if _theme == "dark":
        _group_tints = {
            "Equity":         "#60A5FA",
            "Fixed Income":   "#22D3EE",
            "Hedge Funds":    "#A78BFA",
            "Real Estate":    "#FBBF24",
            "Private Equity": "#F472B6",
            "Infrastructure": "#4ADE80",
            "Multi-Asset":    "#94A3B8",
        }
    else:
        _group_tints = {
            "Equity":         "#1D4ED8",
            "Fixed Income":   "#0891B2",
            "Hedge Funds":    "#7C3AED",
            "Real Estate":    "#B45309",
            "Private Equity": "#BE185D",
            "Infrastructure": "#15803D",
            "Multi-Asset":    "#475569",
        }
    sorted_strats = sub_strat_agg.sort_values(
        ["strategy_name", "sub_strategy_name"]
    ).reset_index(drop=True)

    proposed_shares = {}                # sub_strategy_id -> assumed Amber + Red fraction
    cols_per_row = 4
    n = len(sorted_strats)
    for i in range(0, n, cols_per_row):
        cols = st.columns(cols_per_row, gap="small")
        for j in range(cols_per_row):
            if i + j >= n:
                break
            r = sorted_strats.iloc[i + j]
            sid             = r["sub_strategy_id"]
            current_lim_pct = int(round(float(r["threshold_cum"]) * 100))
            current_actual  = _cur_ar.get(sid, 0.0) * 100
            tint            = _group_tints.get(r["strategy_name"], "#64748B")
            # Default slider position: current policy limit
            default_pct = current_lim_pct
            with cols[j]:
                with st.container(border=True):
                    st.markdown(
                        f'<div style="padding:4px 6px;">'
                        f'<div style="font-size:10px;font-weight:800;color:{tint};'
                        f'text-transform:uppercase;letter-spacing:0.8px;margin-bottom:4px;">'
                        f'{r["strategy_name"]}</div>'
                        f'<div style="font-size:15px;font-weight:700;color:var(--text-primary);'
                        f'line-height:1.25;margin-bottom:8px;">{r["sub_strategy_name"]}</div>'
                        f'<div style="font-size:11px;color:var(--text-subtle);margin-bottom:4px;'
                        f'padding-top:6px;border-top:1px solid var(--border-default);">'
                        f'Current Amber + Red: <b style="color:var(--text-primary);">{current_actual:.0f}%</b>'
                        f'  ·  Policy: <b style="color:var(--text-primary);">{current_lim_pct}%</b>'
                        f'</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    new_share_pct = st.slider(
                        "Assumed Amber + Red %",
                        min_value=0,
                        max_value=100,
                        value=int(default_pct),
                        step=1,
                        format="%d%%",
                        key=f"wi_lim_pct_{sid}",
                        label_visibility="collapsed",
                        help=(f"Assumed Amber + Red share for {r['sub_strategy_name']} in this scenario. "
                              f"Current actual: {current_actual:.0f}%. Policy: {current_lim_pct}%."),
                    )
                    proposed_shares[sid] = new_share_pct / 100.0

    # ── Compute simulated stress loss per Strategy ──────────────────────────
    rows = []
    for _, r in sub_strat_agg.iterrows():
        sid = r["sub_strategy_id"]
        s_inst = inst[inst["sub_strategy_id"] == sid]
        s_mv = float(s_inst["mv"].sum())
        if s_mv <= 0:
            continue

        g_inst  = s_inst[s_inst["tier"] == "Green"]
        ar_inst = s_inst[s_inst["tier"].isin(["Amber","Red"])]
        g_mv  = float(g_inst["mv"].sum())
        ar_mv = float(ar_inst["mv"].sum())

        avg_g  = (g_inst["mv"]  * g_inst["stress_loss_stagflation"]).sum()  / g_mv  if g_mv  > 0 else port_avg_g
        avg_ar = (ar_inst["mv"] * ar_inst["stress_loss_stagflation"]).sum() / ar_mv if ar_mv > 0 else port_avg_ar

        current_ar_share = ar_mv / s_mv
        target_ar_share  = max(0.0, min(1.0, proposed_shares.get(sid, float(r["threshold_cum"]))))

        current_loss_per_mv = current_ar_share * avg_ar + (1 - current_ar_share) * avg_g
        sim_loss_per_mv     = target_ar_share  * avg_ar + (1 - target_ar_share)  * avg_g

        rows.append({
            "Strategy":         r["sub_strategy_name"],
            "Strategy Group":   r["strategy_name"],
            "MV":               s_mv,
            "current_ar":       current_ar_share,
            "target_ar":        target_ar_share,
            "current_loss":     current_loss_per_mv,
            "sim_loss":         sim_loss_per_mv,
            "current_contrib":  current_loss_per_mv * s_mv,
            "sim_contrib":      sim_loss_per_mv     * s_mv,
        })

    sim_df = pd.DataFrame(rows)
    if sim_df.empty:
        st.warning("No data to simulate.")
        return

    sim_baseline_pct = sim_df["current_contrib"].sum() / sim_df["MV"].sum()
    sim_new_pct      = sim_df["sim_contrib"].sum()     / sim_df["MV"].sum()
    delta_pct        = sim_new_pct - sim_baseline_pct

    # ── Headline tiles ──────────────────────────────────────────────────────
    st.markdown(_section_band("Portfolio Stress Loss — Stagflation",
                              "Bottom-up: each instrument carries its own stress loss; no tier override."),
                unsafe_allow_html=True)

    hp1, hp2, hp3 = st.columns(3)
    with hp1:
        st.markdown(
            f'<div style="background:var(--bg-surface);border:1px solid var(--border-default);'
            f'border-left:4px solid var(--text-muted);border-radius:8px;padding:14px 18px;">'
            f'<div class="metric-label">Current</div>'
            f'<div class="kpi-number" style="font-size:32px;color:var(--text-primary);font-weight:800;">'
            f'{sim_baseline_pct*100:.0f}%</div>'
            f'<div style="font-size:11px;color:var(--text-subtle);">of portfolio MV (baseline)</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with hp2:
        st.markdown(
            f'<div style="background:var(--bg-surface);border:1px solid var(--border-default);'
            f'border-left:4px solid var(--accent);border-radius:8px;padding:14px 18px;">'
            f'<div class="metric-label">Simulated</div>'
            f'<div class="kpi-number" style="font-size:32px;color:var(--text-primary);font-weight:800;">'
            f'{sim_new_pct*100:.0f}%</div>'
            f'<div style="font-size:11px;color:var(--text-subtle);">of portfolio MV (assumed scenario)</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with hp3:
        worse = delta_pct < 0
        delta_color = "var(--breach-text)" if worse else "var(--color-ok)"
        delta_arrow = "\u25BC" if worse else "\u25B2"
        verdict     = "worse" if worse else ("better" if delta_pct > 0 else "unchanged")
        st.markdown(
            f'<div style="background:var(--bg-surface);border:1px solid var(--border-default);'
            f'border-left:4px solid {delta_color};border-radius:8px;padding:14px 18px;">'
            f'<div class="metric-label">\u0394 vs current</div>'
            f'<div class="kpi-number" style="font-size:32px;color:{delta_color};font-weight:800;">'
            f'{delta_arrow} {abs(delta_pct)*100:.0f}% pts</div>'
            f'<div style="font-size:11px;color:var(--text-subtle);">{verdict} stress loss</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.caption(
        "Stress losses are negative (e.g. -13.32% means a 13.32% portfolio loss under the scenario). "
        "A more negative simulated number = worse outcome."
    )

    # ── Per-Strategy contribution chart ─────────────────────────────────────
    st.markdown('<div style="height:18px;"></div>', unsafe_allow_html=True)
    st.markdown(_section_band("Per-Strategy stress loss",
                              "Loss as % of Strategy MV. Sorted by absolute delta \u2014 biggest movers at the top."),
                unsafe_allow_html=True)

    chart_df = sim_df.copy()
    chart_df["delta"] = chart_df["sim_loss"] - chart_df["current_loss"]
    chart_df = chart_df.reindex(chart_df["delta"].abs().sort_values(ascending=True).index)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=chart_df["current_loss"] * 100,
        y=chart_df["Strategy"],
        orientation="h",
        name="Current",
        marker_color=_theme()["text-subtle"],
        hovertemplate="<b>%{y}</b><br>Current: %{x:.2f}%<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        x=chart_df["sim_loss"] * 100,
        y=chart_df["Strategy"],
        orientation="h",
        name="Simulated",
        marker_color=_theme()["accent"],
        hovertemplate="<b>%{y}</b><br>Simulated: %{x:.2f}%<extra></extra>",
    ))
    fig.update_layout(
        **DARK_LAYOUT,
        barmode="group",
        height=max(360, 28 * len(chart_df)),
        margin=dict(l=20, r=20, t=10, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, **DARK_LEGEND),
        xaxis_title="<b>Stress loss (% of Strategy MV)</b>",
    )
    fig.update_xaxes(tickformat=".1f")
    st.plotly_chart(fig, use_container_width=True)

    # ── Detail table ────────────────────────────────────────────────────────
    with st.expander("Detail table", expanded=False):
        disp = sim_df[["Strategy", "Strategy Group", "current_ar", "target_ar",
                        "current_loss", "sim_loss"]].copy()
        disp.columns = ["Strategy", "Strategy Group", "Current Amber + Red share", "Assumed Amber + Red share",
                        "Current loss %", "Sim loss %"]
        disp["Current Amber + Red share"] = (disp["Current Amber + Red share"] * 100).round(1).astype(str) + "%"
        disp["Assumed Amber + Red share"] = (disp["Assumed Amber + Red share"] * 100).round(1).astype(str) + "%"
        disp["Current loss %"]    = (disp["Current loss %"]    * 100).round(2).astype(str) + "%"
        disp["Sim loss %"]        = (disp["Sim loss %"]        * 100).round(2).astype(str) + "%"
        st.dataframe(disp, use_container_width=True, hide_index=True)


def page_glossary():
    """Compact reference for every tier, status, threshold and metric used elsewhere."""
    _render_page_title("Glossary")
    st.caption("Definitions for every tier, status, and metric used across the dashboard.")

    def _section_card(title, rows):
        html = (
            f'<div style="background:var(--bg-surface);border:1px solid var(--border-default);'
            f'border-left:4px solid var(--accent);border-radius:8px;'
            f'padding:18px 22px;margin-bottom:18px;">'
            f'<div style="font-size:11px;font-weight:800;color:var(--accent);'
            f'letter-spacing:0.14em;text-transform:uppercase;margin-bottom:14px;">{title}</div>'
        )
        for term, definition in rows:
            html += (
                f'<div style="display:grid;grid-template-columns:200px 1fr;gap:14px;'
                f'padding:10px 0;border-top:1px solid var(--border-default);font-size:14px;'
                f'line-height:1.55;">'
                f'<div style="font-weight:700;color:var(--text-primary);">{term}</div>'
                f'<div style="color:var(--text-soft);">{definition}</div>'
                f'</div>'
            )
        html += '</div>'
        st.markdown(html, unsafe_allow_html=True)

    # Single combined Intransparency Tiers card: data-requirements view +
    # risk-modelling view + the information-needed table from the framework deck.
    # Pass 29.15: use HTML entities (&#10003; / &#10007;) instead of the raw
    # ✓ / ✗ Unicode glyphs so the source file is pure ASCII. Some upload paths
    # (GitHub web UI / Streamlit Cloud) re-encode the file and mangle multi-
    # byte UTF-8 characters, producing "unterminated string literal" errors.
    _ok_badge = '<span style="color:var(--color-ok);font-weight:800;">&#10003;</span>'
    _no_badge = '<span style="color:var(--breach-text);font-weight:800;">&#10007;</span>'

    def _subsection(title, color_var, items):
        """Render a sub-section inside a tier row — an uppercase title in the
        given accent colour followed by a bulleted list of items."""
        bullets = "".join(
            f'<li style="margin-bottom:2px;">{x}</li>' for x in items
        )
        return (
            f'<div style="font-size:11px;color:{color_var};text-transform:uppercase;'
            f'letter-spacing:0.08em;font-weight:700;margin-top:8px;margin-bottom:2px;">{title}</div>'
            f'<ul style="margin:0;padding-left:18px;color:var(--text-soft);'
            f'line-height:1.45;">{bullets}</ul>'
        )

    def _tier_row(data_def, name_badge, sys_badge, risk_summary, info_items, mgmt_items):
        return (
            # Top: the one-line data definition
            f'<div style="margin-bottom:6px;">{data_def}</div>'
            # Risk modelling view (check/cross badges)
            f'<div style="font-size:11px;color:var(--text-subtle);text-transform:uppercase;'
            f'letter-spacing:0.08em;font-weight:700;margin-top:8px;">Risk modelling view</div>'
            f'<div style="margin-top:2px;">Name-level {name_badge} · Systematic {sys_badge} '
            f'<span style="color:var(--text-soft);">— {risk_summary}</span></div>'
            # Core & important information
            f'{_subsection("Core &amp; important information", "var(--accent)", info_items)}'
            # Risk assessment & portfolio management
            f'{_subsection("Risk assessment &amp; portfolio management", "var(--accent)", mgmt_items)}'
        )

    _green_info = [
        "Instrument name and Market Value",
        "Key instrument attributes (asset type, development status, coupon, maturity)",
        ("Critical company metrics, updated recurring: 1× Earnings (e.g. EBITDA), "
         "1× Leverage (e.g. LTV), 1× Cashflow Coverage (e.g. ICR)"),
    ]
    _green_mgmt = [
        "In-depth beyond MTM stress — assess portfolio quality and likelihood of impairment.",
        ("Assure Risk / Audit Comm on private-credit quality; brief GEC on name-level "
         "sanctions exposure; size high-risk exposures under stress."),
        "<b>Portfolio mgmt: name-level actions possible where there is conviction.</b>",
    ]

    _amber_info = [
        "Country and sector exposure",
        "High-level asset-type mix (e.g. VC vs buyout, 1L vs 2L loans, Core vs Core+)",
        ("High-level mix of attributes and risk sensitivities (e.g. weighted-average "
         "duration, OAS, coupon, development status)"),
    ]
    _amber_mgmt = [
        "High-level macro scenario analysis (e.g. HHT, stagflation) — captures MTM impacts only.",
        "Assumes all constituents in a country / sector are equally affected in stress.",
        "<b>Portfolio mgmt: country / sector overlays possible; name-level actions not possible.</b>",
    ]

    _red_info = [
        "<i>No reliable instrument- or portfolio-level information available.</i>",
    ]
    _red_mgmt = [
        "Very high level — wide cone of inaccuracy for exposure and scenario analysis.",
        ("Must assume non-transparent holdings mirror industry country / sector "
         "exposure and perform in line with industry beta in stress."),
        "<b>Portfolio mgmt: not possible to a large extent.</b>",
    ]

    _section_card("Intransparency Tiers", [
        ("Green",
         _tier_row(
             "Fully transparent. All Amber and Green data requirements are satisfied.",
             _ok_badge, _ok_badge,
             "good understanding of both systematic and name-level risk.",
             _green_info, _green_mgmt)),
        ("Amber",
         _tier_row(
             "Amber data requirements satisfied; one or more Green requirements missing.",
             _no_badge, _ok_badge,
             "good understanding of systematic risk, but poor understanding of name-level risk.",
             _amber_info, _amber_mgmt)),
        ("Red",
         _tier_row(
             "At least one Amber data requirement missing.",
             _no_badge, _no_badge,
             "poor understanding of both systematic and name-level risk.",
             _red_info, _red_mgmt)),
    ])

    _section_card("Exposure cards", [
        ("Red exposure",
         "% of portfolio MV in the Red tier, measured against the Red policy limit."),
        ("Amber + Red exposure",
         "% of portfolio MV in the Amber + Red tiers combined, measured against the cumulative policy limit."),
    ])

    # Pass 28.3 / 29: Action status pills synced with the 3-column Kanban on
    # the Action Tracker tab; colours pull from theme tokens so the Glossary
    # follows light/dark mode.
    _section_card("Action status", [
        ("Recommended Action Plan",
         '<b style="color:var(--status-rec-fg);">Recommended Action Plan</b> — no active '
         'initiative yet. Either there is no remediation work under way, or '
         'scope / owner / sequencing is still being worked out. Highest-priority '
         'backlog items for the next planning cycle.'),
        ("In Progress",
         '<b style="color:var(--status-prog-fg);">In Progress</b> — active initiative under way '
         '(e.g. data vendor engaged, external parties onboarding).'),
        ("Completed",
         '<b style="color:var(--status-done-fg);">Completed</b> — initiative closed; the '
         'underlying data gap has been remediated.'),
    ])

    _section_card("Utilisation status", [
        ("Utilisation",
         "Current exposure ÷ policy limit."),
        ("OK",
         "Utilisation <b>&lt; 80%</b>. <span style=\"color:var(--color-ok);font-weight:700;\">Green</span> border."),
        ("ALERT",
         "Utilisation <b>80% to 100%</b>. <span style=\"color:var(--color-alert);font-weight:700;\">Amber</span> border."),
        ("BREACH",
         "Utilisation <b>&gt; 100%</b>. <span style=\"color:var(--breach-text);font-weight:700;\">Red</span> border."),
    ])

    _section_card("Action plan metrics", [
        ("Impact (%)",
         "Drop in this Strategy’s Amber + Red utilisation if the holding is resolved to Green."),
        ("Cumulative impact",
         "Sum of Impact for the top N opportunities."),
        ("Owner team",
         "<b>Strategy Ops</b>, <b>Deal Team & Legal</b>, or <b>CISD</b>."),
        ("Estimated impact",
         "Per-action % reduction in Amber + Red utilisation."),
        ("Overdue chip",
         "<span style=\"color:var(--alert-text);font-weight:700;\">Amber</span> if &lt; 60 days past target; <span style=\"color:var(--breach-text);font-weight:700;\">red</span> if 60+ days past."),
    ])

    st.markdown(
        '<p style="text-align:center;color:var(--text-subtle);font-size:11px;font-style:italic;'
        'margin-top:24px;">Definitions track the current policy framework — please flag any drift to the Risk team.</p>',
        unsafe_allow_html=True,
    )


# ===========================================================================
# Main
# ===========================================================================

def _render_page_title(title: str, *, show_stats: bool = False, font_size: int = 38):
    """Render the page title in a row with the theme toggle on the right.
    show_stats=True puts stats + toggle in the same right-side column so they
    sit on the exact same baseline (sibling columns drift)."""
    try:
        if show_stats:
            # Title left, stats+toggle right. Both right-side widgets live in
            # the SAME column via a nested sub-column row so their baseline matches.
            title_col, right_col = st.columns([7, 3], vertical_alignment="center")
        else:
            title_col, right_col = st.columns([9, 1], vertical_alignment="center")
    except TypeError:
        if show_stats:
            title_col, right_col = st.columns([7, 3])
        else:
            title_col, right_col = st.columns([9, 1])

    with title_col:
        st.markdown(
            f'<h1 style="font-size:{font_size}px;font-weight:700;color:var(--text-primary);'
            f'margin:0;padding:0;line-height:1.1;">{title}</h1>',
            unsafe_allow_html=True,
        )

    with right_col:
        if show_stats:
            # Nested sub-cols inside the right column so stats and toggle share
            # the same row baseline. The toggle widget brings its own vertical
            # centering; setting the stats vertical_alignment to "center" matches.
            try:
                meta_sub, toggle_sub = st.columns([3, 2], vertical_alignment="center")
            except TypeError:
                meta_sub, toggle_sub = st.columns([3, 2])
            with meta_sub:
                n_groups = int(st.session_state.get("_meta_n_groups", 0))
                n_ports  = int(st.session_state.get("_meta_n_portfolios", 0))
                # Pass 24.11: transform-translateY to nudge stats up to match the
                # toggle widget's visual baseline (Streamlit's toggle chrome offsets it
                # ~4-5px lower than where plain text would center).
                st.markdown(
                    f'<div style="text-align:right;font-size:12px;color:var(--text-subtle);'
                    f'padding:0;margin:0;line-height:1;transform:translateY(-6px);">'
                    f'\u00b7 <strong style="color:var(--text-primary);font-weight:600;">{n_groups}</strong> strategy groups '
                    f'\u00b7 <strong style="color:var(--text-primary);font-weight:600;">{n_ports}</strong> portfolios</div>',
                    unsafe_allow_html=True,
                )
            with toggle_sub:
                _render_theme_toggle()
        else:
            _render_theme_toggle()


def _render_theme_toggle():
    """Render the Light/Dark theme toggle. Extracted so it can be reused in
    nested column layouts (e.g. Total Portfolio's title row)."""
    is_cream = st.session_state["theme_mode"] == "cream"
    new_cream = st.toggle("Light", value=is_cream, key="theme_toggle",
                          help="Switch between light (white) and dark theme")
    new_mode = "cream" if new_cream else "dark"
    if new_mode != st.session_state["theme_mode"]:
        st.session_state["theme_mode"] = new_mode
        st.query_params["theme"] = new_mode
        st.rerun()



def main():
    (strategies_df, sub_strategies_df, portfolios_df, instruments_df,
     strat_agg, sub_strat_agg, history_df, sub_history_df, audit_df,
     action_items_df) = generate_all_data(_tier_mix_signature())

    # Theme — must be initialised BEFORE any markdown/plot helper renders.
    # Theme persistence (Pass 10): read ?theme= from URL so it survives any
    # full-page navigation (clicking an exposure card / strategy widget triggers
    # a hard reload that resets session_state).
    try:
        _qt = st.query_params.get("theme")
    except Exception:
        _qt = None
    if _qt in ("dark", "cream"):
        st.session_state["theme_mode"] = _qt
    if "theme_mode" not in st.session_state:
        st.session_state["theme_mode"] = "cream"
    _render_theme_css()

    # Pass 24.8: top brand bar removed entirely per user feedback.
    # Stash meta counts so the per-page title helper can show "N strategy groups · N portfolios".
    st.session_state["_meta_n_groups"]     = len(strat_agg)
    st.session_state["_meta_n_portfolios"] = len(portfolios_df)


    PAGES = ["Total Portfolio", "Strategy Detail", "Action Tracker",
             "Data Quality", "What-If Simulator", "Glossary"]

    if "active_page" not in st.session_state:
        st.session_state["active_page"] = "Total Portfolio"

    # Deep-link: "Investigate breach" buttons carry ?goto=strategy&name=<Group>
    # plus optional &sdfocus=<Tier>&sdstrat=<Group>. We promote the page nav and the
    # selected Group here, but we do NOT clear sdfocus/sdstrat — page_strategy_detail
    # reads them at the top and clears once consumed (so the focused card is set).
    if st.query_params.get("goto") == "strategy":
        st.session_state["active_page"] = "Strategy Detail"
        _nm = st.query_params.get("name")
        if _nm:
            st.session_state["sd_sel"] = _nm     # preselect the Strategy Group
        _sc = st.query_params.get("sdscope")
        if _sc:
            st.session_state["sd_scope"] = _sc   # narrow Scope dropdown to clicked Strategy
        # Clear navigation keys (goto + name + sdscope). Leave sdfocus + sdstrat
        # for page_strategy_detail to consume.
        for _k in ("goto", "name", "sdscope"):
            try:
                del st.query_params[_k]
            except Exception:
                pass
    elif st.query_params.get("sdfocus"):
        # Strategy Detail exposure-card drill-through — keep the user on Strategy Detail
        # (a full page reload from the <a href> resets session state, so reconstruct it here)
        st.session_state["active_page"] = "Strategy Detail"
        _s = st.query_params.get("sdstrat")
        if _s:
            st.session_state["sd_sel"] = _s
        # sdfocus/sdstrat left in the URL for page_strategy_detail to consume + clear

        # Tab-styled horizontal nav, session-state controlled (so it can be switched in code)
    active = st.radio(
        "Navigation", PAGES,
        key="active_page",
        horizontal=True,
        label_visibility="collapsed",
    )

    if   active == "Total Portfolio":   page_portfolio_overview(strat_agg, sub_strat_agg, portfolios_df, history_df, sub_history_df, instruments_df)
    elif active == "Strategy Detail":   page_strategy_detail(strat_agg, sub_strat_agg, portfolios_df, instruments_df, history_df, sub_history_df)
    elif active == "Action Tracker":    page_action_tracker(action_items_df, sub_strat_agg, sub_history_df)
    elif active == "Data Quality":      page_data_quality(portfolios_df, instruments_df, audit_df)
    elif active == "What-If Simulator": page_whatif(sub_strat_agg, instruments_df, portfolios_df)
    elif active == "Glossary":          page_glossary()

if __name__ == "__main__":
    main()
