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
    "Green": "background-color:#E3F0E4;color:#2E7036",
    "Amber": "background-color:#F7E9D5;color:#B86F1A",
    "Red":   "background-color:#FBE4E4;color:#8B2331",
}
# Theme palettes — dark (the original) and cream (FT-style salmon).
# Toggled via st.session_state["theme_mode"]. Helpers use CSS variables
# emitted by _render_theme_css(); plotly figures use LAYOUT()/LEGEND().
THEMES = {
    "dark": {
        "bg-page":          "#0E1117",
        "bg-surface":       "#161B27",
        "bg-track":         "#0E1117",
        "border-default":   "#1F2740",
        "border-strong":    "#2A3352",
        "text-primary":     "#E0E4EF",
        "text-muted":       "#8892AA",
        "text-subtle":      "#5F6A82",
        "text-soft":        "#A8B4CC",
        "accent":           "#4F8EF7",
        "color-ok":         "#27AE60",
        "color-alert":      "#E6B800",
        "color-breach":     "#A32D2D",
        "color-bar-neutral":"#5C6E8C",
        "color-amber-fill": "#E6B800",
        "color-red-fill":   "#A32D2D",
        "alert-border":     "#7A5C00",
        "breach-border":    "#A32D2D",
        "ok-border":        "#1F2740",
        "limit-tick":       "#E0E4EF",
        "investigate-bg":   "#7A1F1F",
        "investigate-text": "#F5B0B0",
        "alert-text":       "#F0A030",
        "breach-text":      "#F06060",
        "ok-text":          "#27AE60",
        "amber-tier":       "#E67E22",
        "red-tier":         "#E74C3C",
        "plotly-paper":     "#161B27",
        "plotly-plot":      "#161B27",
        "plotly-font":      "#C8CFE0",
        "plotly-grid":      "#1F2740",
        "plotly-line":      "#2A3352",
        "plotly-legend-bg": "#0E1117",
        "section-band":     "#4F8EF7",
    },
    "cream": {
        "bg-page":          "#FFF1E5",
        "bg-surface":       "#FFFFFF",
        "bg-track":         "#F5EADD",
        "border-default":   "#E8DBC7",
        "border-strong":    "#D5C2A4",
        "text-primary":     "#1B1B1B",
        "text-muted":       "#6B5F4F",
        "text-subtle":      "#A89580",
        "text-soft":        "#3A352D",
        "accent":           "#0E5A8A",
        "color-ok":         "#2E7036",
        "color-alert":      "#B86F1A",
        "color-breach":     "#8B2331",
        "color-bar-neutral":"#9AA4B5",
        "color-amber-fill": "#B86F1A",
        "color-red-fill":   "#8B2331",
        "alert-border":     "#B86F1A",
        "breach-border":    "#8B2331",
        "ok-border":        "#E8DBC7",
        "limit-tick":       "#1B1B1B",
        "investigate-bg":   "#FBE4E4",
        "investigate-text": "#8B2331",
        "alert-text":       "#B86F1A",
        "breach-text":      "#8B2331",
        "ok-text":          "#2E7036",
        "amber-tier":       "#B86F1A",
        "red-tier":         "#8B2331",
        "plotly-paper":     "#FFFFFF",
        "plotly-plot":      "#FFFFFF",
        "plotly-font":      "#1B1B1B",
        "plotly-grid":      "#E8DBC7",
        "plotly-line":      "#D5C2A4",
        "plotly-legend-bg": "#FFF1E5",
        "section-band":     "#0E5A8A",
    },
}

def _theme():
    """Active theme dict — defaults to dark."""
    import streamlit as _st
    return THEMES.get(_st.session_state.get("theme_mode", "dark"), THEMES["dark"])

def LAYOUT():
    t = _theme()
    return dict(
        paper_bgcolor=t["plotly-paper"],
        plot_bgcolor=t["plotly-plot"],
        font=dict(color=t["plotly-font"], size=12),
        xaxis=dict(gridcolor=t["plotly-grid"], linecolor=t["plotly-line"], zerolinecolor=t["plotly-grid"]),
        yaxis=dict(gridcolor=t["plotly-grid"], linecolor=t["plotly-line"], zerolinecolor=t["plotly-grid"]),
    )

def LEGEND():
    t = _theme()
    return dict(bgcolor=t["plotly-legend-bg"], bordercolor=t["plotly-grid"], borderwidth=1)

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

MISSING_FIELDS   = ["EBITDA", "LTV", "ICR", "NAV", "Cash Flow",
                    "Leverage Ratio", "ESG Score", "Audited Financials"]
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
    hover_card = "#FFF8EB" if is_cream else "#1B2233"
    hover_card_border = t["border-strong"]
    investigate_hover_bg = "#F5C1C1" if is_cream else "#992525"
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
.section-title {{ font-size:1.05rem; font-weight:600; color: var(--text-soft); margin-bottom:4px; letter-spacing:0.02em; }}
[data-testid=\"stDataFrame\"] {{ border:1px solid var(--border-default) !important; border-radius:6px; }}
[data-testid=\"stExpander\"]  {{ background-color: var(--bg-surface) !important; border:1px solid var(--border-default) !important; border-radius:6px !important; }}
[data-testid=\"stAlert\"]     {{ border-radius:6px !important; }}
[data-baseweb=\"select\"]     {{ background-color: var(--bg-surface) !important; }}
[data-testid=\"stSelectbox\"] {{ max-width: 340px; }}
[data-baseweb=\"select\"] > div {{ background-color: var(--bg-surface) !important; border:1px solid var(--border-strong) !important; border-radius:6px !important; cursor:pointer !important; }}
[data-baseweb=\"select\"] > div:hover {{ border-color: var(--accent) !important; }}
[data-baseweb=\"select\"] svg {{ fill: var(--text-soft) !important; color: var(--text-soft) !important; }}
hr {{ border-color: var(--border-default) !important; }}
::-webkit-scrollbar {{ width:6px; height:6px; }}
::-webkit-scrollbar-track {{ background: var(--bg-page); }}
::-webkit-scrollbar-thumb {{ background: var(--border-strong); border-radius:3px; }}
::-webkit-scrollbar-thumb:hover {{ background: var(--accent); }}
a.card-link {{ display:block; text-decoration:none; color:inherit; cursor:pointer; }}
a.card-link .exposure-card {{ transition: background 0.15s, border-color 0.15s, box-shadow 0.15s; }}
a.card-link:hover .exposure-card {{ background: {hover_card} !important; }}
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
.st-key-toggle_widgets {{ display:flex !important; justify-content:flex-end !important; margin-bottom:-6px !important; }}
.st-key-toggle_widgets button {{ padding:3px 12px !important; min-height:0 !important; height:30px !important; font-size:12px !important; line-height:1 !important; }}
</style>
"""
    st.markdown(css, unsafe_allow_html=True)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def fmt_mv(v):  return f"£{v/1000:.1f}B" if v >= 1000 else f"£{v:.0f}M"
def fmt_pct(v): return f"{v*100:.1f}%"

def apply_tier_style(styler, col):
    _pal = TIER_BG_CREAM if st.session_state.get("theme_mode", "dark") == "cream" else TIER_BG
    def _c(v): return _pal.get(v, "")
    try:    return styler.map(_c, subset=[col])
    except: return styler.applymap(_c, subset=[col])

# ─── Strategy Taxonomy ───────────────────────────────────────────────────────
# Two-level taxonomy:
#   - Strategy Group (top-level container, has owner)
#   - Strategy       (where the Red / Amber / Cumulative thresholds live)
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
    ("G07", "Others",           "Sarah Kim"),
]

# Strategy Status panel grouping: each Strategy Group is classed Public or Private.
# (This is a display grouping for the panel only — the strategy_id -> Strategy Group
#  link is retained in the data for Strategy Detail drill-through.)
PRODUCT_GROUPING = {
    "EQ Active":        "Public",
    "Fixed Income":     "Public",
    "Hedge Fund":       "Public",
    "Others":           "Public",   # Multi Asset
    "Private Equities": "Private",
    "Infrastructure":   "Private",
    "Real Estate":      "Private",
}

# Sub-strategies (= new "Strategy") — thresholds live HERE now.
# Format per child: (sub_id, sub_name, thr_red, thr_amber, thr_cum)
SUB_STRATEGY_META = {
    "G01": [
        ("S01a", "EQ Developed Markets", 0.05, 0.10, 0.15),
        ("S01b", "EQ Emerging Markets",  0.05, 0.12, 0.17),
    ],
    "G02": [
        ("S02a", "FI Active",            0.05, 0.10, 0.15),
        ("S02b", "HY Credit",            0.05, 0.15, 0.20),
        ("S02c", "MAARS",                0.05, 0.15, 0.20),
        ("S02d", "EILB",                 0.05, 0.10, 0.15),
    ],
    "G03": [
        ("S03a", "Hedge Fund 1",         0.10, 0.25, 0.35),
        ("S03b", "Hedge Fund 2",         0.10, 0.25, 0.35),
    ],
    "G04": [
        ("S04a", "RE Bricks and Mortar", 0.08, 0.20, 0.28),
        ("S04b", "RE Debt",              0.05, 0.15, 0.20),
    ],
    "G05": [
        ("S05a", "PE Active",            0.05, 0.25, 0.30),
        ("S05b", "PE Secondaries",       0.05, 0.25, 0.30),
        ("S05c", "PE Mezz",              0.05, 0.30, 0.35),
    ],
    "G06": [
        ("S06a", "Infrastructure Active", 0.05, 0.25, 0.30),
        ("S06b", "Infrastructure Debt",   0.05, 0.20, 0.25),
    ],
    "G07": [
        ("S07a", "Multi Asset",          0.05, 0.20, 0.25),
    ],
}

# Engineered tier mix per Strategy (= sub_strategy). Only "PE Active" breaches.
# [green, amber, red] proportions.
TIER_MIX = {
    # Comfortable margin under each Strategy's own thresholds. Small-sample
    # multinomial draws can spike tier proportions; values below are tuned
    # to keep all strategies safely OK except PE Active.
    "EQ Developed Markets":   [1.00, 0.00, 0.00],
    "EQ Emerging Markets":    [0.99, 0.01, 0.00],
    "FI Active":              [1.00, 0.00, 0.00],
    "HY Credit":              [0.98, 0.02, 0.00],
    "MAARS":                  [0.99, 0.01, 0.00],
    "EILB":                   [1.00, 0.00, 0.00],
    "Hedge Fund 1":           [0.92, 0.07, 0.01],
    "Hedge Fund 2":           [0.92, 0.07, 0.01],
    "RE Bricks and Mortar":   [0.93, 0.06, 0.01],
    "RE Debt":                [0.96, 0.04, 0.00],
    "PE Active":              [0.81, 0.18, 0.01],   # BREACH — modest, all three checks 105–120% util
    "PE Secondaries":         [0.88, 0.11, 0.01],
    "PE Mezz":                [0.85, 0.13, 0.02],
    "Infrastructure Active":  [0.82, 0.18, 0.00],   # ALERT — Amber util ~97%, no breach
    "Infrastructure Debt":    [0.96, 0.04, 0.00],
    "Multi Asset":            [0.93, 0.06, 0.01],
}

# Product / Instrument-Type pools — keyed by Strategy Group name.
PRODUCT_BY_STRATEGY = {
    "EQ Active":        ["Public"],
    "Fixed Income":     ["Public"],
    "Hedge Fund":       ["Private"],
    "Real Estate":      ["Private"],
    "Private Equities": ["Private"],
    "Infrastructure":   ["Private"],
    "Others":           ["Public", "Private"],
}
INSTRUMENT_BY_STRATEGY = {
    "EQ Active":        ["Mandate", "Direct Investment"],
    "Fixed Income":     ["Mandate", "Direct Investment"],
    "Hedge Fund":       ["Fund Investment", "Mandate"],
    "Real Estate":      ["Fund Investment", "Direct Investment", "Co-investment"],
    "Private Equities": ["Fund Investment", "Co-investment"],
    "Infrastructure":   ["Fund Investment", "Direct Investment", "Co-investment"],
    "Others":           ["Fund Investment", "Mandate"],
}

# ─── Synthetic Data ───────────────────────────────────────────────────────────

def _tier_mix_signature():
    """Stable signature of TIER_MIX values — feeds into the cache key so any
    edit to TIER_MIX invalidates the cached output without needing a manual
    "Clear cache" click."""
    import hashlib
    blob = repr(sorted(TIER_MIX.items())).encode("utf-8")
    return hashlib.md5(blob).hexdigest()[:10]


@st.cache_data
def generate_all_data(_tier_mix_sig: str = ""):
    """The _tier_mix_sig argument is part of the cache key — pass
    _tier_mix_signature() at the call site so TIER_MIX edits propagate."""
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

            miss = ([] if tier == "Green"
                    else random.sample(MISSING_FIELDS, random.randint(1, 2)) if tier == "Amber"
                    else random.sample(MISSING_FIELDS, random.randint(2, 4)))

            product_type    = random.choice(PRODUCT_BY_STRATEGY.get(sname, ["Public", "Private"]))
            instrument_type = random.choice(INSTRUMENT_BY_STRATEGY.get(sname, ["Fund Investment", "Direct Investment"]))
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
                im = ([] if itier=="Green"
                      else random.sample(MISSING_FIELDS, random.randint(1,2)) if itier=="Amber"
                      else random.sample(MISSING_FIELDS, random.randint(2,4)))
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
                    "region": reg, "sector": sect,
                    "last_updated": datetime.now() - timedelta(days=random.randint(0, 120)),
                })

    portfolios_df  = pd.DataFrame(port_rows)
    # Asset type — Public/Private × DICI/Fund-Investment matrix used by the Breakdown 'Cut by'.
    # DICIs = Direct + Co-investment; Fund Investments = Fund + Mandate.
    def _asset_type(row):
        bucket = 'DICIs' if row['instrument_type'] in ('Direct', 'Co-investment') else 'Fund Investments'
        return f"{row['product_type']} {bucket}"
    portfolios_df['asset_type'] = portfolios_df.apply(_asset_type, axis=1)
    instruments_df = pd.DataFrame(instr_rows)
    audit_df       = pd.DataFrame(audit_rows)

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
    sub_strat_agg["red_utilisation"]   = sub_strat_agg["Red_pct"]   / sub_strat_agg["threshold_red"]
    sub_strat_agg["amber_utilisation"] = sub_strat_agg["Amber_pct"] / sub_strat_agg["threshold_amber"]
    sub_strat_agg["cum_utilisation"]   = sub_strat_agg["cum_pct"]   / sub_strat_agg["threshold_cum"]
    sub_strat_agg["red_breach"]   = sub_strat_agg["Red_pct"]   > sub_strat_agg["threshold_red"]
    sub_strat_agg["amber_breach"] = sub_strat_agg["Amber_pct"] > sub_strat_agg["threshold_amber"]
    sub_strat_agg["cum_breach"]   = sub_strat_agg["cum_pct"]   > sub_strat_agg["threshold_cum"]
    sub_strat_agg["any_breach"]   = sub_strat_agg["red_breach"] | sub_strat_agg["amber_breach"] | sub_strat_agg["cum_breach"]
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
    strat_agg["red_utilisation"]   = strat_agg["Red_pct"]   / strat_agg["threshold_red"].replace(0, pd.NA)
    strat_agg["amber_utilisation"] = strat_agg["Amber_pct"] / strat_agg["threshold_amber"].replace(0, pd.NA)
    strat_agg["cum_utilisation"]   = strat_agg["cum_pct"]   / strat_agg["threshold_cum"].replace(0, pd.NA)
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
    for _, ss in sub_strat_agg.iterrows():
        ssid = ss["sub_strategy_id"]
        cur_a, cur_r = sub_current_map.get(ssid, (0.0, 0.0))
        for mo in range(0, 12):
            dt = today.replace(day=1) - timedelta(days=30*mo)
            if mo == 0:
                ba, br = cur_a, cur_r
            else:
                drift = mo * 0.004
                ba = max(0.0, min(0.95, cur_a + drift + random.uniform(-0.015, 0.025)))
                br = max(0.0, min(0.30, cur_r + drift * 0.5 + random.uniform(-0.005, 0.012)))
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

    return (strategies_df, sub_strategies_df, portfolios_df, instruments_df,
            strat_agg, sub_strat_agg, history_df, sub_history_df, audit_df)


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


def _cockpit_widget_html(row, expanded=True, show_investigate=True):
    """Collapsible cockpit widget. Click the summary (name + status pill) to expand or
    collapse its utilisation rows individually. The Expand/Collapse all button sets the
    panel-wide default; individual toggles persist within a session and reset to that
    default on a full page reload (e.g. clicking an exposure card)."""
    any_breach = bool(row["any_breach"])

    red_util = row["red_utilisation"]   * 100
    amb_util = row["amber_utilisation"] * 100
    cum_util = row["cum_utilisation"]   * 100
    max_util = max(red_util, amb_util, cum_util)

    # Three-state traffic light: OK (<90%), Alert (>=90%, not breaching), Breach (>100%)
    if any_breach:
        pill_text, pill_color, light_color = "BREACH", "var(--breach-text)", "var(--color-breach)"
        border_color, border_width = "var(--color-red-fill)", "2px"
    elif max_util >= 90:
        pill_text, pill_color, light_color = "ALERT", "var(--alert-text)", "var(--color-alert)"
        border_color, border_width = "var(--alert-border)", "2px"
    else:
        pill_text, pill_color, light_color = "OK", "var(--ok-text)", "var(--color-ok)"
        border_color, border_width = "var(--ok-border)", "1px"

    def _row(label, util):
        if util > 100:
            color, weight = "var(--breach-text)", "600"
        elif util >= 90:
            color, weight = "var(--color-alert)", "600"
        else:
            color, weight = "var(--text-primary)", "500"
        return (
            f'<div style="display:flex;justify-content:space-between;align-items:baseline;font-size:14px;padding:5px 0;">'
            f'<span style="color:var(--text-muted);">{label}</span>'
            f'<span style="color:{color};font-weight:{weight};font-size:19px;font-variant-numeric:tabular-nums;">{util:.0f}%</span>'
            f'</div>'
        )

    investigate = ""
    if any_breach and show_investigate:
        # Send the PARENT Strategy Group to ?goto=strategy. sub_strat_agg rows have
        # strategy_name = Group name; strat_agg rows fall back to their own name.
        try:
            target_group = str(row["strategy_name"])  # parent Strategy Group
        except (KeyError, IndexError):
            target_group = str(row["name"])
        # Pick the breaching tier with the largest variance over its limit so the
        # Strategy Detail page can auto-focus the most painful card.
        _breach_priorities = []
        if bool(row.get("red_breach",   False)): _breach_priorities.append(("Red",        float(row.get("red_variance",   0))))
        if bool(row.get("amber_breach", False)): _breach_priorities.append(("Amber",      float(row.get("amber_variance", 0))))
        if bool(row.get("cum_breach",   False)): _breach_priorities.append(("Cumulative", float(row.get("cum_variance",   0))))
        _breach_priorities.sort(key=lambda t: -t[1])
        worst_tier = _breach_priorities[0][0] if _breach_priorities else "Red"
        investigate = (
            f'<a href="?goto=strategy&name={quote(target_group)}&sdfocus={worst_tier}&sdstrat={quote(target_group)}" '
            f'target="_self" class="investigate-btn" '
            f'style="display:block;text-align:center;margin-top:12px;padding:9px;border-radius:6px;'
            f'background:var(--investigate-bg);color:var(--investigate-text);font-size:14px;font-weight:500;text-decoration:none;">'
            f'Investigate breach \u2192</a>'
        )

    open_attr = "open" if expanded else ""
    return (
        f'<details class="cockpit" {open_attr} style="background:var(--bg-surface);border:{border_width} solid {border_color};border-radius:6px;padding:12px 14px;">'
        f'<summary style="display:flex;justify-content:space-between;align-items:center;list-style:none;">'
        f'<div style="font-size:16px;font-weight:500;color:var(--text-primary);">{row["name"]}</div>'
        f'<div style="display:flex;align-items:center;gap:6px;">'
        f'<div style="width:8px;height:8px;border-radius:50%;background:{light_color};"></div>'
        f'<span style="font-size:13px;color:{pill_color};font-weight:500;">{pill_text}</span>'
        f'<span class="chev" style="font-size:12px;color:var(--text-muted);margin-left:2px;">\u25bc</span>'
        f'</div></summary>'
        f'<div style="margin-top:10px;padding-top:8px;border-top:1px solid var(--border-default);">'
        f'{_row("Red util %",   red_util)}'
        f'{_row("Amber util %", amb_util)}'
        f'{_row("Cumulative util %", cum_util)}'
        f'{investigate}'
        f'</div>'
        f'</details>'
    )



def _total_exposure_card_html(label, util_pct, value_pct, limit_pct, color, breach, href=None, tooltip=None):
    """Top-row exposure card. If href is set, the whole card becomes a clickable link."""
    # Three-state bar fill: encode utilisation state, not tier identity. The
    # tier name is already in the card label ("Red exposure" / "Amber exposure"),
    # so colouring the bar the same colour as the tier doubles the signal and
    # makes a low-util bar read as alarming. Bar colour now means: neutral when
    # comfortably under limit, amber when within 10pp of limit, red on breach.
    if breach:
        fill_color = "var(--color-red-fill)"   # dark red — breach (same as cockpit Breach)
    elif util_pct >= 90:
        fill_color = "var(--color-amber-fill)"   # amber — alert (same as cockpit Alert state)
    else:
        fill_color = "var(--color-bar-neutral)"   # neutral blue-grey — comfortably within limit
    fill_w     = min(util_pct, 100.0)
    used_color = "var(--breach-text)" if breach else "var(--text-soft)"
    overshoot_badge = (
        f' <span style="color:var(--breach-text);font-weight:500;">\u00b7 +{util_pct - 100:.0f}% over limit</span>'
        if breach else ""
    )
    info = (f' <span title="{tooltip}" style="color:var(--text-subtle);cursor:help;font-size:13px;">\u24d8</span>'
            if tooltip else "")
    if breach:
        st_text, st_dot, st_color = "BREACH", "var(--color-breach)", "var(--breach-text)"
    elif util_pct >= 90:
        st_text, st_dot, st_color = "ALERT", "var(--color-alert)", "var(--alert-text)"
    else:
        st_text, st_dot, st_color = "OK", "var(--color-ok)", "var(--ok-text)"
    status_pill = (
        f'<div style="display:flex;align-items:center;gap:6px;">'
        f'<div style="width:8px;height:8px;border-radius:50%;background:{st_dot};"></div>'
        f'<span style="font-size:13px;font-weight:600;letter-spacing:0.03em;color:{st_color};">{st_text}</span>'
        f'</div>'
    )
    click_hint = (' <span style="color:var(--accent);font-size:13px;font-weight:700;">\u2197</span>'
                  if href else "")
    inner = (
        f'<div class="exposure-card" style="background:var(--bg-surface);border:1px solid var(--border-default);border-radius:8px;padding:14px 16px;">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">'
        f'<div style="font-size:15px;font-weight:500;color:var(--text-primary);">{label}{info}{click_hint}</div>'
        f'{status_pill}'
        f'</div>'
        f'<div style="position:relative;height:6px;background:var(--bg-track);border-radius:2px;margin-bottom:8px;">'
        f'<div style="position:absolute;left:0;top:0;height:100%;width:{fill_w:.1f}%;background:{fill_color};border-radius:2px;"></div>'
        f'<div style="position:absolute;right:-1px;top:-3px;width:2px;height:12px;background:var(--limit-tick);"></div>'
        f'</div>'
        f'<div style="display:flex;justify-content:space-between;align-items:baseline;">'
        f'<div style="font-size:13px;color:{used_color};font-variant-numeric:tabular-nums;"><span style="font-weight:600;font-size:19px;">{util_pct:.0f}%</span> used</div>'
        f'<div style="font-size:13px;color:var(--text-muted);font-variant-numeric:tabular-nums;"><span style="color:var(--text-primary);">{value_pct:.1f}%</span> / {limit_pct:.1f}% limit{overshoot_badge}</div>'
        f'</div>'
        f'</div>'
    )
    if href:
        return f'<a href="{href}" class="card-link" target="_self">{inner}</a>'
    return inner


TIER_PALETTES = {
    "Red":        ["var(--color-red-fill)", "#C0392B", "#D85A30", "#E24B4A"],
    "Amber":      ["#BA7517", "#D17616", "#EF9F27", "#FAC775"],
    "Cumulative": ["var(--color-red-fill)", "#C0392B", "#BA7517", "#D17616"],
}
OTHERS_COLOR = "#5f6a82"

TIER_TOOLTIPS = {
    "Red":        "Red = Poor systematic risk \u2014 the least transparent tier.",
    "Amber":      "Amber = Good understanding of systematic risk but no name-level information.",
    "Cumulative": "Cumulative = Amber + Red combined (total non-transparent exposure).",
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
        txt_color = "#e0e4ef" if is_others else "#ffffff"

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
        f'<div style="display:grid;grid-template-columns:160px 1fr 150px 60px;gap:10px;align-items:center;padding:9px 0;border-bottom:1px solid var(--border-default);font-size:13px;">'
        f'<div style="color:{label_color};font-weight:{label_weight};">{label}</div>'
        f'<div style="position:relative;height:10px;background:var(--bg-track);border-radius:2px;">'
        f'<div style="position:absolute;left:0;top:0;height:100%;width:{bar_width:.1f}%;background:{tier_color};border-radius:2px;"></div>'
        f'</div>'
        f'<div style="font-size:12px;text-align:right;color:{val_color};font-variant-numeric:tabular-nums;"><span style="font-weight:500;">{contrib_pct:.2f}%</span> <span style="color:var(--text-subtle);">\u00b7 {share_pct:.0f}% of tier</span></div>'
        f'<div style="font-size:11px;text-align:right;color:var(--text-muted);font-variant-numeric:tabular-nums;">{count}</div>'
        f'</div>'
    )


def _section_band(title, subtitle=""):
    """A labelled section divider with a coloured left accent."""
    sub = (f'<div style="font-size:13px;color:var(--text-muted);margin-top:2px;">{subtitle}</div>'
           if subtitle else "")
    return (
        f'<div style="border-left:3px solid var(--section-band);padding-left:12px;margin:10px 0 16px;">'
        f'<div style="font-size:20px;font-weight:600;color:var(--text-primary);letter-spacing:0.02em;">{title}</div>'
        f'{sub}</div>'
    )


def page_portfolio_overview(strat_agg, sub_strat_agg, portfolios_df, history_df):
    st.title("Intransparency monitoring dashboard")

    # Drill-through from clickable cards: read URL query param, promote to
    # session_state, then clear the URL so future reruns don't keep forcing it.
    try:
        qp_focus = st.query_params.get("focus")
    except Exception:
        qp_focus = None
    if qp_focus in ("Red", "Amber", "Cumulative"):
        st.session_state["focus_tier"]       = qp_focus
        st.session_state["breakdown_expand"] = True
        st.session_state["trend_expand"]     = True
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

    # AUM-weighted total-portfolio thresholds
    if total_mv > 0:
        thr_amber_tot = (df["threshold_amber"] * df["total_mv"]).sum() / total_mv
        thr_red_tot   = (df["threshold_red"]   * df["total_mv"]).sum() / total_mv
        thr_cum_tot   = (df["threshold_cum"]   * df["total_mv"]).sum() / total_mv
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

    # ── Subtitle ─────────────────────────────────────────────────────────────
    portfolio_part = (
        "Cumulative Intransparency exposure remained within their respective limits."
        if not t_any_breach else
        "Cumulative Intransparency exposure breached one or more limits."
    )
    portfolio_color = "var(--text-soft)" if not t_any_breach else "var(--breach-text)"

    if n_breaches == 0:
        breach_part = f"all {len(df)} strategies within tolerance"
        breach_color = "var(--ok-text)"
    else:
        names_label = ", ".join(breach_names)
        breach_part = f"{n_breaches} of {len(df)} strateg{'y' if n_breaches==1 else 'ies'} breaching ({names_label})"
        breach_color = "var(--breach-text)"

    st.markdown(_section_band("Total Portfolio", "Aggregate exposure vs limits. Limits are MV-weighted across the 16 strategies; click a card to drill into its breakdown below."), unsafe_allow_html=True)
    st.markdown(
        f'<p style="font-size:13.5px;color:{portfolio_color};margin:-6px 0 12px;">{portfolio_part}</p>',
        unsafe_allow_html=True,
    )

    # ── Section A: Total portfolio exposure cards (clickable drill-through) ──
    card_specs = [
        ("Red exposure",   util_red_tot,   w_red*100,   thr_red_tot*100,   "#e74c3c", t_red_breach,   "Red"),
        ("Amber exposure", util_amber_tot, w_amber*100, thr_amber_tot*100, "#e67e22", t_amber_breach, "Amber"),
        ("Cumulative",     util_cum_tot,   w_cum*100,   thr_cum_tot*100,   "#888780", t_cum_breach,   "Cumulative"),
    ]
    # Carry the current panel state in the card link so the full-page reload it
    # triggers doesn't reset the Strategy status panel back to expanded.
    exp_q = "1" if st.session_state["widgets_expanded"] else "0"
    cards_html = '<div style="display:grid;grid-template-columns:repeat(3, 1fr);gap:12px;margin-bottom:20px;">'
    for (lbl, util, val, thr, color, breach, tier_key) in card_specs:
        cards_html += _total_exposure_card_html(
            lbl, util, val, thr, color, breach,
            href=f"?focus={tier_key}&exp={exp_q}",
            tooltip=TIER_TOOLTIPS.get(tier_key),
        )
    cards_html += '</div>'
    st.markdown(cards_html, unsafe_allow_html=True)

    st.markdown(_section_band("Strategy status panel", "Each shows utilisation against that Strategy's own Red, Amber, and Cumulative thresholds."), unsafe_allow_html=True)
    st.markdown(
        f'<p style="font-size:13.5px;color:{breach_color};margin:-6px 0 12px;">{breach_part}</p>',
        unsafe_allow_html=True,
    )

    # ── Section B: Strategy status panel (cockpit grid) ──────────────────────
    _, btn_col = st.columns([8, 1.1])
    with btn_col:
        btn_label = "Collapse all" if st.session_state["widgets_expanded"] else "Expand all"
        if st.button(btn_label, key="toggle_widgets", use_container_width=True):
            new_state = not st.session_state["widgets_expanded"]
            st.session_state["widgets_expanded"] = new_state
            st.query_params["exp"] = "1" if new_state else "0"
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
            '<div style="font-size:13px;color:var(--text-soft);font-weight:600;letter-spacing:0.06em;text-transform:uppercase;">'
            + title +
            '</div>'
            '<div style="flex:1;height:1px;background:' + accent + ';opacity:0.25;"></div>'
            '<div style="font-size:11px;color:var(--text-subtle);">'
            + str(n) + ' ' + ("strategy" if n == 1 else "strategies") + '</div></div>'
        )
        grid = '<div style="display:grid;grid-template-columns:repeat(4, minmax(0, 1fr));gap:10px;margin-bottom:4px;">'
        for _, row in children.iterrows():
            grid += _cockpit_widget_html(row, expanded=expanded)
        grid += '</div>'
        return head + grid

    cockpit_html = _product_section("Public Strategies", "Public") + _product_section("Private Strategies", "Private")
    # Negative top margin tightens the gap between the toggle button and the widgets.
    st.markdown('<div style="margin-top:-14px;">' + cockpit_html + '</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:26px;"></div>', unsafe_allow_html=True)
    st.markdown(_section_band("Details", "Total portfolio trend over time and exposure contribution breakdown."), unsafe_allow_html=True)

    # ── Section C: Trend (expander, collapsed by default) ───────────────────
    # Trend follows the same tier the exposure cards set (focus_tier), so a card
    # click focuses the Trend just like the Breakdown. Cumulative / no-click = full chart.
    trend_tier   = st.session_state.get("focus_tier", "Cumulative")
    trend_expand = st.session_state.pop("trend_expand", False)
    _trend_titles = {
        "Red":        "Red (no transparency) exposure trend",
        "Amber":      "Amber (partial transparency) exposure trend",
        "Cumulative": "Non-transparent exposure trend (Amber + Red)",
    }
    with st.expander("📈 Total Portfolio Trend", expanded=trend_expand):
        st.markdown(
            f'<p class="section-title" style="margin-top:0.5rem;">{_trend_titles.get(trend_tier, _trend_titles["Cumulative"])}</p>',
            unsafe_allow_html=True
        )
        if trend_tier in ("Red", "Amber"):
            st.caption(f"AUM-weighted total portfolio — {trend_tier} shown by default. Use the chart legend to toggle the other series on or off.")
        else:
            st.caption("AUM-weighted total portfolio. Stacked bars show the Amber/Red composition each month; the line traces the overall trajectory. Click a Red or Amber card above to focus on a single tier.")

        hagg_stack = (
            hf.groupby("date")
              .apply(lambda g: pd.Series({
                  "amber_pct": _aum_weighted(g, "amber_pct") * 100,
                  "red_pct":   _aum_weighted(g, "red_pct")   * 100,
              }))
              .reset_index()
        )

        # Always add all three series (same order as the full view) so the legend
        # and its click-to-toggle interactivity are identical across tiers. Non-focused
        # series start hidden via visible="legendonly" — present in the legend, one click away.
        amber_vis = True if trend_tier in ("Amber", "Cumulative") else "legendonly"
        red_vis   = True if trend_tier in ("Red",   "Cumulative") else "legendonly"
        total_vis = True if trend_tier == "Cumulative" else "legendonly"
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Bar(
            x=hagg_stack["date"], y=hagg_stack["amber_pct"],
            name="Amber", marker_color="#e67e22", visible=amber_vis,
            hovertemplate="<b>%{x|%b %Y}</b><br>Amber: %{y:.1f}%<extra></extra>",
        ))
        fig_trend.add_trace(go.Bar(
            x=hagg_stack["date"], y=hagg_stack["red_pct"],
            name="Red", marker_color="#e74c3c", visible=red_vis,
            hovertemplate="<b>%{x|%b %Y}</b><br>Red: %{y:.1f}%<extra></extra>",
        ))
        fig_trend.add_trace(go.Scatter(
            x=hagg["date"], y=hagg["non_transparent_pct"],
            mode="lines+markers", name="Total non-transparent", visible=total_vis,
            line=dict(color="#c0392b", width=2.5),
            marker=dict(size=8, color="#c0392b", line=dict(color="#0e1117", width=1.5)),
            hovertemplate="<b>%{x|%b %Y}</b><br>Total: %{y:.1f}%<extra></extra>",
        ))
        fig_trend.update_layout(
            **DARK_LAYOUT, barmode="stack",
            yaxis_title="% non-transparent", height=320,
            margin=dict(l=20,r=20,t=10,b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, **DARK_LEGEND),
        )
        fig_trend.update_xaxes(tickformat="%b %Y", dtick="M1", tickangle=-30)
        st.plotly_chart(fig_trend, use_container_width=True)

    # ── Section D: Breakdown panel (drill-through from Top cards) ────────────
    expand_breakdown = st.session_state.pop("breakdown_expand", False)
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
            tier_options = ["Red", "Amber", "Cumulative"]
            tier = st.selectbox("Focus on",
                                tier_options,
                                index=tier_options.index(focus_default) if focus_default in tier_options else 0,
                                key="bd_focus")
        with bc2:
            cut_label = st.selectbox("Cut by",
                                     ["Strategy", "Asset type", "Instrument Type"],
                                     key="bd_cut")

        cut_map = {
            "Strategy":                   "sub_strategy_name",    # internal: sub_strategy_name = Strategy
            "Asset type":                 "asset_type",
            "Instrument Type":             "instrument_type",
        }
        cut_col = cut_map[cut_label]

        tier_filter = pf["tier"].isin(["Amber", "Red"]) if tier == "Cumulative" else (pf["tier"] == tier)
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
            f'The bar below is <span style="color:var(--text-primary);font-weight:500;">{total_tier_pct:.2f}%</span> '
            f'\u2014 the {tier.lower()} exposure shown in the top panel '
            f'(<span style="color:var(--text-primary);">{n_contrib}</span> portfolios contributing).</p>',
            unsafe_allow_html=True,
        )

        if total_tier_mv == 0:
            st.info(f"No portfolios are currently in the {tier.lower()} tier.")
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
                '<thead><tr style="border-bottom:1px solid var(--border-default);color:var(--text-subtle);font-weight:400;text-align:left;font-size:13px;">'
                f'<th style="padding:8px 0;">{cut_label}</th>'
                f'<th style="padding:8px 0;text-align:right;">Contributes</th>'
                f'<th style="padding:8px 0;text-align:right;">Share of {tier}</th>'
                f'<th style="padding:8px 0;text-align:right;">Portfolios</th>'
                '</tr></thead><tbody>'
            )
            for _, r in non_zero.iterrows():
                wt = "500" if r["pct_of_tier"] >= 50 else "400"
                table_html += (
                    f'<tr style="border-bottom:1px solid var(--border-default);">'
                    f'<td style="padding:9px 0;color:var(--text-primary);font-weight:{wt};">{r[cut_col]}</td>'
                    f'<td style="padding:9px 0;text-align:right;color:var(--text-primary);font-variant-numeric:tabular-nums;font-weight:500;">{r["contrib_pct"]:.2f}%</td>'
                    f'<td style="padding:9px 0;text-align:right;color:var(--text-soft);font-variant-numeric:tabular-nums;">{r["pct_of_tier"]:.0f}%</td>'
                    f'<td style="padding:9px 0;text-align:right;color:var(--text-soft);font-variant-numeric:tabular-nums;">{int(r["count"])}</td>'
                    f'</tr>'
                )
            if len(zero_cuts) > 0:
                zero_labels = ", ".join(str(z) for z in zero_cuts[cut_col].tolist())
                table_html += (
                    f'<tr style="color:var(--text-subtle);">'
                    f'<td style="padding:9px 0;font-size:11px;font-style:italic;">{zero_labels} (no contribution)</td>'
                    f'<td style="padding:9px 0;text-align:right;font-variant-numeric:tabular-nums;">0.00%</td>'
                    f'<td style="padding:9px 0;text-align:right;font-variant-numeric:tabular-nums;">0%</td>'
                    f'<td style="padding:9px 0;text-align:right;font-variant-numeric:tabular-nums;">0</td>'
                    f'</tr>'
                )
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
    if qpf in ("Red", "Amber", "Cumulative"):
        st.session_state["sd_focus_tier"]       = qpf
        st.session_state["sd_breakdown_expand"] = True
        st.session_state["sd_trend_expand"]     = True
        if qps:
            st.session_state["sd_scope"] = qps
    for _k in ("sdfocus", "sdstrat", "sdsub"):
        try:
            del st.query_params[_k]
        except Exception:
            pass
    st.session_state.setdefault("sd_focus_tier", "Cumulative")
    sd_focus = st.session_state["sd_focus_tier"]

    # ── Title + status subtitle ─────────────────────────────────────────────
    st.title(f"Strategy Group · {sel}")
    if n_breach == 0:
        status_html = f'<span style="color:var(--color-ok);">All {n_child} strateg{"y" if n_child==1 else "ies"} within tolerance.</span>'
    else:
        names = ", ".join(breaching_names)
        status_html = (
            f'<span style="color:var(--color-breach);">{n_breach} of {n_child} strateg'
            f'{"y" if n_child==1 else "ies"} breaching ({names}).</span>'
        )
    st.markdown(
        f'<p style="font-size:14px;margin-top:-4px;margin-bottom:14px;">'
        f'<span style="color:var(--text-soft);">Strategy Group owner: '
        f'<span style="color:var(--text-primary);font-weight:500;">{owner}</span></span> &middot; {status_html}</p>',
        unsafe_allow_html=True,
    )

    # ── Section A: per-Strategy exposure cards (clickable drill-through) ──────
    # No Strategy-Group aggregate: limits live at the Strategy level, so each
    # Strategy is shown against its OWN Red / Amber / Cumulative limits.
    st.markdown(_section_band(
        f"{sel} — exposure vs limits per Strategy",
        "Each Strategy is shown against its own Red, Amber, and Cumulative limits. Click any card to focus the breakdown and trend below."),
        unsafe_allow_html=True)
    for _, sr in children.iterrows():
        s_name = sr["sub_strategy_name"]
        s_max = max(float(sr["red_utilisation"]), float(sr["amber_utilisation"]), float(sr["cum_utilisation"])) * 100
        if bool(sr["any_breach"]):
            s_state, s_color = "BREACH", "var(--color-breach)"
        elif s_max >= 90:
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
            ("Red exposure",   float(sr["red_utilisation"])*100,   float(sr["Red_pct"])*100,   float(sr["threshold_red"])*100,   "#e74c3c", bool(sr["red_breach"]),   "Red"),
            ("Amber exposure", float(sr["amber_utilisation"])*100, float(sr["Amber_pct"])*100, float(sr["threshold_amber"])*100, "#e67e22", bool(sr["amber_breach"]), "Amber"),
            ("Cumulative",     float(sr["cum_utilisation"])*100,   float(sr["cum_pct"])*100,   float(sr["threshold_cum"])*100,   "#888780", bool(sr["cum_breach"]),   "Cumulative"),
        ]
        block = '<div style="display:grid;grid-template-columns:repeat(3, 1fr);gap:12px;margin-bottom:6px;">'
        for (lbl, util, val, thr, color, breach, tier_key) in card_specs:
            block += _total_exposure_card_html(
                lbl, util, val, thr, color, breach,
                href=f"?sdfocus={tier_key}&sdstrat={quote(str(sel))}&sdsub={quote(str(s_name))}",
                tooltip=TIER_TOOLTIPS.get(tier_key),
            )
        block += '</div>'
        st.markdown(block, unsafe_allow_html=True)

    # ── Section B: Details (Trend + Breakdown) ──────────────────────────────
    st.markdown('<div style="height:22px;"></div>', unsafe_allow_html=True)
    st.markdown(_section_band(
        "Details",
        "Trend over time and exposure contribution breakdown. Use Scope to view the whole group or a single Strategy."),
        unsafe_allow_html=True)

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

    # Trend — follows the clicked tier, full interactive legend
    sd_trend_expand = st.session_state.pop("sd_trend_expand", False)
    _trend_titles = {
        "Red":        "Red (no transparency) exposure trend",
        "Amber":      "Amber (partial transparency) exposure trend",
        "Cumulative": "Non-transparent exposure trend (Amber + Red)",
    }
    with st.expander("\U0001f4c8 Strategy Trend", expanded=sd_trend_expand):
        st.markdown(
            f'<p class="section-title" style="margin-top:0.5rem;">{_trend_titles.get(sd_focus, _trend_titles["Cumulative"])}</p>',
            unsafe_allow_html=True)
        if sd_focus in ("Red", "Amber"):
            st.caption(f"{scope_name} — monthly {sd_focus} trend shown by default. Use the chart legend to toggle the other series on or off.")
        else:
            st.caption(f"{scope_name} — monthly trend. Stacked bars show the Amber / Red composition; the line traces total non-transparent %. Click a Red or Amber card above to focus a single tier.")
        amber_vis = True if sd_focus in ("Amber", "Cumulative") else "legendonly"
        red_vis   = True if sd_focus in ("Red",   "Cumulative") else "legendonly"
        total_vis = True if sd_focus == "Cumulative" else "legendonly"
        fig_st = go.Figure()
        fig_st.add_trace(go.Bar(x=sh["date"], y=sh["amber_pct"]*100, name="Amber",
                                marker_color="#e67e22", visible=amber_vis,
                                hovertemplate="<b>%{x|%b %Y}</b><br>Amber: %{y:.1f}%<extra></extra>"))
        fig_st.add_trace(go.Bar(x=sh["date"], y=sh["red_pct"]*100, name="Red",
                                marker_color="#e74c3c", visible=red_vis,
                                hovertemplate="<b>%{x|%b %Y}</b><br>Red: %{y:.1f}%<extra></extra>"))
        fig_st.add_trace(go.Scatter(x=sh["date"], y=sh["non_transparent_pct"]*100,
                                    mode="lines+markers", name="Total non-transparent", visible=total_vis,
                                    line=dict(color="#c0392b", width=2.5),
                                    marker=dict(size=8, color="#c0392b", line=dict(color="#0e1117", width=1.5)),
                                    hovertemplate="<b>%{x|%b %Y}</b><br>Total: %{y:.1f}%<extra></extra>"))
        fig_st.update_layout(**DARK_LAYOUT, barmode="stack", yaxis_title="% non-transparent", height=320,
                             margin=dict(l=20, r=20, t=10, b=20),
                             legend=dict(orientation="h", yanchor="bottom", y=1.02, **DARK_LEGEND))
        fig_st.update_xaxes(tickformat="%b %Y", dtick="M1", tickangle=-30)
        st.plotly_chart(fig_st, use_container_width=True)

    # Breakdown — group-scoped, 4 cuts, in an expander with an info tooltip
    sd_breakdown_expand = st.session_state.pop("sd_breakdown_expand", False)
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
            tier_options = ["Red", "Amber", "Cumulative"]
            tier = st.selectbox("Focus on", tier_options,
                                index=tier_options.index(sd_focus) if sd_focus in tier_options else 0,
                                key="sd_bd_focus")
        with bc2:
            cut_label = st.selectbox(
                "Cut by",
                ["Strategy", "Portfolio", "Asset type", "Instrument Type"],
                key="sd_cut",
            )
        cut_map = {
            "Strategy":                   "sub_strategy_name",
            "Portfolio":                  "portfolio_name",
            "Asset type":                 "asset_type",
            "Instrument Type":            "instrument_type",
        }
        cut_col = cut_map[cut_label]

        sd_pf = scope_pf
        tier_filter = sd_pf["tier"].isin(["Amber", "Red"]) if tier == "Cumulative" else (sd_pf["tier"] == tier)
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
            f'The bar below is <span style="color:var(--text-primary);font-weight:500;">{total_tier_pct:.2f}%</span> '
            f"&mdash; {scope_name}'s {tier.lower()} exposure "
            f'(<span style="color:var(--text-primary);">{n_contrib}</span> portfolios contributing).</p>',
            unsafe_allow_html=True)

        if total_tier_mv == 0:
            st.info(f"No portfolios are currently in the {tier.lower()} tier within {scope_name}.")
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
                '<thead><tr style="border-bottom:1px solid var(--border-default);color:var(--text-subtle);font-weight:400;text-align:left;font-size:13px;">'
                f'<th style="padding:8px 0;">{cut_label}</th>'
                f'<th style="padding:8px 0;text-align:right;">Contributes</th>'
                f'<th style="padding:8px 0;text-align:right;">Share of {tier}</th>'
                f'<th style="padding:8px 0;text-align:right;">Portfolios</th>'
                '</tr></thead><tbody>'
            )
            for _, r in non_zero.iterrows():
                wt = "500" if r["pct_of_tier"] >= 50 else "400"
                table_html += (
                    f'<tr style="border-bottom:1px solid var(--border-default);">'
                    f'<td style="padding:9px 0;color:var(--text-primary);font-weight:{wt};">{r[cut_col]}</td>'
                    f'<td style="padding:9px 0;text-align:right;color:var(--text-primary);font-variant-numeric:tabular-nums;font-weight:500;">{r["contrib_pct"]:.2f}%</td>'
                    f'<td style="padding:9px 0;text-align:right;color:var(--text-soft);font-variant-numeric:tabular-nums;">{r["pct_of_tier"]:.0f}%</td>'
                    f'<td style="padding:9px 0;text-align:right;color:var(--text-soft);font-variant-numeric:tabular-nums;">{int(r["count"])}</td>'
                    f'</tr>'
                )
            if len(zero_cuts) > 0:
                zl = ", ".join(str(z) for z in zero_cuts[cut_col].tolist())
                table_html += (
                    f'<tr style="color:var(--text-subtle);">'
                    f'<td style="padding:9px 0;font-size:13px;font-style:italic;">{zl} (no contribution)</td>'
                    f'<td style="padding:9px 0;text-align:right;">0.00%</td>'
                    f'<td style="padding:9px 0;text-align:right;">0%</td>'
                    f'<td style="padding:9px 0;text-align:right;">0</td>'
                    f'</tr>'
                )
            table_html += '</tbody></table>'
            st.markdown(table_html, unsafe_allow_html=True)

    # ── Section C: Recommended action plans (bottom) ────────────────────────
    st.markdown('<div style="height:22px;"></div>', unsafe_allow_html=True)
    st.markdown(_section_band(
        "Recommended action plans",
        "Non-transparent instruments scoped to the breaching Strategy by default. "
        "Impact = percentage-point drop in that Strategy's cumulative utilisation if the holding is resolved to Green."),
        unsafe_allow_html=True)

    breaching_children = children[children["any_breach"]]["sub_strategy_name"].tolist()
    all_children = children["sub_strategy_name"].tolist()
    default_strats = breaching_children if breaching_children else all_children
    sel_strats = st.multiselect(
        "Strategy",
        options=all_children,
        default=default_strats,
        help="Scope the action plan to specific Strategies. Default is whichever Strategy(ies) are currently breaching.",
        key=f"ap_strats_{sid}",
    )

    inst = instruments_df[(instruments_df["strategy_id"] == sid) &
                          (instruments_df["tier"].isin(["Amber", "Red"]))].copy()
    if sel_strats:
        inst = inst[inst["sub_strategy_name"].isin(sel_strats)]

    if inst.empty:
        st.info("No Amber or Red instruments in the selected Strategies — nothing to action.")
    else:
        strat_mv_map  = dict(zip(children["sub_strategy_id"], children["total_mv"]))
        strat_thr_map = dict(zip(children["sub_strategy_id"], children["threshold_cum"]))
        def _impact(row):
            smv = float(strat_mv_map.get(row["sub_strategy_id"], 0) or 0)
            thr = float(strat_thr_map.get(row["sub_strategy_id"], 0) or 0)
            if smv <= 0 or thr <= 0:
                return 0.0
            return (float(row["mv"]) / smv) / thr * 100
        inst["impact"] = inst.apply(_impact, axis=1)
        inst = inst.sort_values("impact", ascending=False)
        disp = inst[["instrument_name", "portfolio_name", "sub_strategy_name",
                     "instrument_type", "tier", "missing_fields", "impact"]].copy()
        impact_col = "Est. Impact to Utilisation (%) ⓘ"
        disp.columns = ["Instrument", "Portfolio", "Strategy", "Instrument Type",
                        "Tier", "Missing Fields", impact_col]
        scope_label = ", ".join(sel_strats) if sel_strats and len(sel_strats) <= 3 else f"{len(sel_strats)} Strateg" + ("y" if len(sel_strats)==1 else "ies")
        st.caption(
            f"{len(disp)} non-transparent instruments across {scope_label}, highest impact first. "
            "Hover the ⓘ in the “Est. Impact to Utilisation (%)” column header for the full definition."
        )
        styled = apply_tier_style(disp.style, "Tier").format({impact_col: "{:.1f}"})
        st.dataframe(
            styled, use_container_width=True, height=440,
            column_config={
                impact_col: st.column_config.Column(
                    impact_col,
                    help=("Percentage-point drop in THIS instrument's parent Strategy's cumulative "
                          "utilisation if the holding were resolved to Green. Calculated as the "
                          "instrument's share of its parent Strategy's MV divided by that Strategy's "
                          "cumulative threshold — higher means a bigger lever to pull."),
                )
            },
        )


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

def page_data_quality(portfolios_df, instruments_df, audit_df):
    st.title("📋 Data Quality & Operational View")

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
                fig_sm = px.bar(sm, x="missing_count", y="sub_strategy_name", orientation="h",
                                 color="missing_count",
                                 color_continuous_scale=["#27ae60", "#e67e22", "#e74c3c"],
                                 labels={"missing_count": "Count", "sub_strategy_name": ""})
                fig_sm.update_layout(**DARK_LAYOUT, height=320, margin=dict(l=10, r=10, t=10, b=10),
                                      showlegend=False, coloraxis_showscale=False)
                st.plotly_chart(fig_sm, use_container_width=True)
            else:
                st.info("No missing fields to break down.")

        st.markdown('<p class="section-title">Data Completeness Trend</p>', unsafe_allow_html=True)
        random.seed(7)
        dates = pd.date_range(end=datetime.now(), periods=12, freq="MS")
        comp  = [62 + i*2.8 + random.gauss(0, 1.2) for i in range(12)]
        comp_df = pd.DataFrame({"date": dates, "completeness": comp})
        fig_c = px.line(comp_df, x="date", y="completeness", markers=True,
                         labels={"completeness": "Completeness (%)", "date": ""},
                         color_discrete_sequence=["#27ae60"])
        fig_c.add_hline(y=90, line_dash="dot", line_color="orange",
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

def page_whatif(strat_agg):
    st.title("🔮 What-If Simulator (WIP)")
    st.caption("Adjust thresholds and tier reclassification to see the impact on breach status and cumulative utilisation.")

    sel = st.selectbox("Select Strategy Group", strat_agg["name"].tolist(), key="wi_sel")
    row = strat_agg[strat_agg["name"] == sel].iloc[0]

    st.markdown("---")
    col_in, col_out = st.columns(2)

    with col_in:
        st.subheader("Adjust Parameters (Strategy Group)")
        st.markdown("**Threshold Adjustments**")
        new_red_thr   = st.slider("Red Threshold (%)",         1, 20, int(row["threshold_red"]  *100), 1) / 100
        new_amber_thr = st.slider("Amber Threshold (%)",       1, 50, int(row["threshold_amber"]*100), 1) / 100
        new_cum_thr   = st.slider("Cumulative Threshold (%)",  1, 60, int(row["threshold_cum"]  *100), 1) / 100

        st.markdown("**Tier Reclassification (simulate uplift)**")
        a2g = st.slider("Reclassify Amber → Green (%pt)", 0, 30, 0, 1) / 100
        r2a = st.slider("Reclassify Red → Amber (%pt)",   0, 15, 0, 1) / 100

    sim_amber = max(0.0, row["Amber_pct"] - a2g + r2a)
    sim_red   = max(0.0, row["Red_pct"]   - r2a)
    sim_green = max(0.0, 1.0 - sim_amber - sim_red)
    sim_cum   = sim_amber + sim_red

    cur_rb  = row["Red_pct"]   > row["threshold_red"]
    cur_ab  = row["Amber_pct"] > row["threshold_amber"]
    cur_cb  = row["cum_pct"]   > row["threshold_cum"]
    sim_rb  = sim_red   > new_red_thr
    sim_ab  = sim_amber > new_amber_thr
    sim_cb  = sim_cum   > new_cum_thr

    cur_util = row["cum_pct"] / row["threshold_cum"] if row["threshold_cum"] > 0 else 0
    sim_util = sim_cum        / new_cum_thr           if new_cum_thr > 0 else 0

    with col_out:
        st.subheader("Simulated Outcome")
        mc1, mc2 = st.columns(2)
        with mc1:
            st.markdown("**Current**")
            st.metric("Red",   fmt_pct(row["Red_pct"]))
            st.metric("Amber", fmt_pct(row["Amber_pct"]))
            st.metric("Cumulative util.", f"{cur_util*100:.0f}%")
            st.markdown("Breach status")
            st.error("🔴 Red breach")        if cur_rb else st.success("🔴 Red OK")
            st.error("🟠 Amber breach")      if cur_ab else st.success("🟠 Amber OK")
            st.error("⛔ Cumulative breach") if cur_cb else st.success("⛔ Cumulative OK")
        with mc2:
            st.markdown("**Simulated**")
            st.metric("Red",   fmt_pct(sim_red),
                       delta=f"{(sim_red-row['Red_pct'])*100:+.1f}%pt", delta_color="inverse")
            st.metric("Amber", fmt_pct(sim_amber),
                       delta=f"{(sim_amber-row['Amber_pct'])*100:+.1f}%pt", delta_color="inverse")
            st.metric("Cumulative util.", f"{sim_util*100:.0f}%",
                       delta=f"{(sim_util-cur_util)*100:+.0f}%pt", delta_color="inverse")
            st.markdown("Breach status")
            st.error("🔴 Red breach")        if sim_rb else st.success("🔴 Red OK")
            st.error("🟠 Amber breach")      if sim_ab else st.success("🟠 Amber OK")
            st.error("⛔ Cumulative breach") if sim_cb else st.success("⛔ Cumulative OK")

    st.markdown("---")
    st.markdown('<p class="section-title">Tier Composition: Before vs After</p>', unsafe_allow_html=True)
    fig_cmp = go.Figure()
    for tier, cv, sv, color in [
        ("Green", row["Green_pct"]*100, sim_green*100, "#27ae60"),
        ("Amber", row["Amber_pct"]*100, sim_amber*100, "#e67e22"),
        ("Red",   row["Red_pct"]  *100, sim_red  *100, "#e74c3c"),
    ]:
        fig_cmp.add_trace(go.Bar(
            name=tier, x=["Current","Simulated"], y=[cv,sv],
            marker_color=color, text=[f"{cv:.1f}%",f"{sv:.1f}%"], textposition="auto",
        ))
    fig_cmp.add_hline(y=new_cum_thr*100,   line_dash="dot", line_color="#888780",
                       annotation_text=f"Cum limit {fmt_pct(new_cum_thr)}")
    fig_cmp.add_hline(y=new_amber_thr*100, line_dash="dot", line_color="#e67e22",
                       annotation_text=f"Amber limit {fmt_pct(new_amber_thr)}")
    fig_cmp.add_hline(y=new_red_thr*100,   line_dash="dot", line_color="#e74c3c",
                       annotation_text=f"Red limit {fmt_pct(new_red_thr)}")
    fig_cmp.update_layout(**DARK_LAYOUT, barmode="stack", yaxis_title="% of Strategy",
                           height=350, margin=dict(l=10,r=10,t=30,b=10))
    st.plotly_chart(fig_cmp, use_container_width=True)

    st.markdown("---")
    st.markdown('<p class="section-title">Cross-Strategy Sensitivity (each strategy uses its own thresholds)</p>',
                unsafe_allow_html=True)
    st.caption("Same reclassification deltas applied to every strategy. Thresholds stay at each strategy\'s configured limit.")

    s_rows = []
    for _, sr in strat_agg.iterrows():
        s_amber = max(0.0, sr["Amber_pct"] - a2g + r2a)
        s_red   = max(0.0, sr["Red_pct"]   - r2a)
        s_cum   = s_amber + s_red
        s_rb = s_red   > sr["threshold_red"]
        s_ab = s_amber > sr["threshold_amber"]
        s_cb = s_cum   > sr["threshold_cum"]
        s_util = s_cum / sr["threshold_cum"] if sr["threshold_cum"] > 0 else 0
        flags = []
        if s_rb: flags.append("R")
        if s_ab: flags.append("A")
        if s_cb: flags.append("Cum")
        s_rows.append({
            "Strategy":         sr["name"],
            "Sim Red":          fmt_pct(s_red),
            "Sim Amber":        fmt_pct(s_amber),
            "Sim Cum":          fmt_pct(s_cum),
            "Sim Util":         f"{s_util*100:.0f}%",
            "Sim Status":       " + ".join(flags) if flags else "OK",
        })
    s_disp = pd.DataFrame(s_rows)
    st.dataframe(s_disp, use_container_width=True)


# ===========================================================================
# Main
# ===========================================================================

def main():
    (strategies_df, sub_strategies_df, portfolios_df, instruments_df,
     strat_agg, sub_strat_agg, history_df, sub_history_df, audit_df) = generate_all_data(_tier_mix_signature())

    # Theme — must be initialised BEFORE any markdown/plot helper renders.
    if "theme_mode" not in st.session_state:
        st.session_state["theme_mode"] = "dark"
    _render_theme_css()

    # Top bar: brand on the left, meta + theme toggle on the right.
    bc_left, bc_right = st.columns([3, 2])
    with bc_left:
        st.markdown(
            f'<div style="margin-bottom:6px;padding-top:4px;">'
            f'<span style="font-size:14px;color:var(--text-soft);font-weight:500;">Transparency Framework \u00b7 Pension Fund</span></div>',
            unsafe_allow_html=True,
        )
    with bc_right:
        meta_col, toggle_col = st.columns([4, 1])
        with meta_col:
            st.markdown(
                f'<div style="text-align:right;font-size:11px;color:var(--text-subtle);padding-top:8px;">'
                f'Data as of <strong style="color:var(--text-primary);font-weight:500;">{datetime.now().strftime("%d %b %Y")}</strong> '
                f'\u00b7 <strong style="color:var(--text-primary);font-weight:500;">{len(strat_agg)}</strong> strategy groups '
                f'\u00b7 <strong style="color:var(--text-primary);font-weight:500;">{len(portfolios_df)}</strong> portfolios</div>',
                unsafe_allow_html=True,
            )
        with toggle_col:
            is_cream = st.session_state["theme_mode"] == "cream"
            new_cream = st.toggle("Cream", value=is_cream, key="theme_toggle",
                                  help="Switch between cream (light, print-friendly) and dark theme")
            new_mode = "cream" if new_cream else "dark"
            if new_mode != st.session_state["theme_mode"]:
                st.session_state["theme_mode"] = new_mode
                st.rerun()


    PAGES = ["Total Portfolio", "Strategy Detail", "Instrument Detail",
             "Data Quality", "What-If Simulator (WIP)"]

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
        # Clear only goto + name (the navigation keys). Leave sdfocus + sdstrat
        # for page_strategy_detail to consume.
        for _k in ("goto", "name"):
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

    if   active == "Total Portfolio":   page_portfolio_overview(strat_agg, sub_strat_agg, portfolios_df, history_df)
    elif active == "Strategy Detail":   page_strategy_detail(strat_agg, sub_strat_agg, portfolios_df, instruments_df, history_df, sub_history_df)
    elif active == "Instrument Detail": page_instrument_detail(instruments_df)
    elif active == "Data Quality":      page_data_quality(portfolios_df, instruments_df, audit_df)
    elif active == "What-If Simulator (WIP)": page_whatif(strat_agg)

if __name__ == "__main__":
    main()
