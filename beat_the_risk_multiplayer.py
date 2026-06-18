"""
BEAT THE RISK — Multiplayer Edition
─────────────────────────────────────────────────────────────────
A synchronous, multiplayer credit risk simulation.
Shared state lives on JSONBin.io (no installs/downloads required).

SETUP:
1. Create a free account at https://jsonbin.io
2. Click "Create Bin" with content like {"initialized": true}, note the BIN_ID
3. Grab your "X-Master-Key" from your account
4. In Streamlit Cloud > App > Settings > Secrets, paste:

    JSONBIN_BIN_ID = "your-bin-id"
    JSONBIN_API_KEY = "your-master-key"

5. Push this file to a GitHub repo and deploy it on Streamlit Community Cloud.
"""

import streamlit as st
import random
import time
import json
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Beat The Risk — Multiplayer",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ═══════════════════════════════════════════════════════════════════════
# STYLE (warm ivory / private-banking theme)
# ═══════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300;9..144,500;9..144,600;9..144,700&family=Inter:wght@300;400;500;600&family=Space+Mono:wght@400;500&display=swap');

    :root {
        --ink: #ece7dd;
        --panel: #f7f4ee;
        --panel-raised: #fffdf9;
        --hairline: rgba(40,35,25,0.10);
        --hairline-bright: rgba(40,35,25,0.18);
        --gold: #9c7a35;
        --gold-dim: rgba(156,122,53,0.09);
        --gold-glow: rgba(156,122,53,0.30);
        --cream: #211d15;
        --slate: #6b6457;
        --slate-dim: #9a9285;
        --red: #b8453a;
        --green: #3f7a5c;
        --amber: #a8732e;
    }
    * { box-sizing: border-box; }
    .stApp { background: var(--ink) !important; font-family: 'Inter', sans-serif !important; }
    #MainMenu, footer, header { visibility: hidden; }
    .stDeployButton { display: none; }
    [data-testid="stToolbar"] { display: none; }
    .block-container { padding: 1.2rem 2.2rem !important; max-width: 1400px !important; margin: 0 auto !important; }

    .stApp::before {
        content: '';
        position: fixed; inset: 0; pointer-events: none; z-index: 0;
        background-image: repeating-linear-gradient(
            to bottom, transparent 0, transparent 39px, rgba(40,35,25,0.025) 40px
        );
    }

    .apex-header {
        background: var(--panel);
        border: 1px solid var(--hairline);
        border-radius: 4px;
        padding: 1.1rem 2rem;
        display: flex; align-items: center; justify-content: space-between;
        margin-bottom: 1.1rem;
        position: relative;
    }
    .apex-header::after {
        content: '';
        position: absolute; left: 2rem; right: 2rem; bottom: -1px; height: 1px;
        background: linear-gradient(90deg, transparent, var(--gold-glow), transparent);
        opacity: 0.5;
    }
    .header-left { display: flex; align-items: center; gap: 1.4rem; }
    .hsbc-mark {
        background: #ffffff; color: #B8121E;
        box-shadow: 0 1px 3px rgba(40,35,25,0.12);
        font-family: 'Fraunces', serif; font-weight: 700; font-size: 13px; letter-spacing: 1.5px;
        padding: 5px 11px; border-radius: 2px;
    }
    .brand-divider { width: 1px; height: 22px; background: var(--hairline-bright); }
    .brand-name {
        font-family: 'Fraunces', serif; font-weight: 600; font-size: 19px; color: var(--cream);
        letter-spacing: 0.5px; font-style: italic;
    }
    .brand-name b { font-style: normal; color: var(--gold); font-weight: 700; }
    .round-pill {
        font-family: 'Space Mono', monospace; font-size: 10.5px; font-weight: 500; color: var(--gold);
        background: var(--gold-dim); border: 1px solid rgba(201,169,97,0.25);
        padding: 5px 13px; border-radius: 2px; letter-spacing: 1.5px; text-transform: uppercase;
    }
    .live-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--green);
        box-shadow: 0 0 6px var(--green); display: inline-block; margin-right: 7px;
        animation: pulse-dot 2.4s ease infinite; }
    @keyframes pulse-dot { 0%,100%{opacity:1;} 50%{opacity:0.45;} }
    .player-tag { font-family: 'Space Mono', monospace; font-size: 10.5px; color: var(--slate);
        letter-spacing: 0.5px; }
    .player-tag .host-star { color: var(--gold); }

    .panel {
        background: var(--panel); border: 1px solid var(--hairline); border-radius: 4px; padding: 1.7rem;
    }
    .panel-title {
        font-family: 'Space Mono', monospace; font-size: 9.5px; letter-spacing: 2.2px; text-transform: uppercase;
        color: var(--slate-dim); margin-bottom: 1.1rem; display: flex; align-items: center; gap: 0.5rem;
    }
    .panel-title::after { content: ''; flex: 1; height: 1px; background: var(--hairline); }

    .data-grid {
        display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1px; background: var(--hairline);
        border-radius: 3px; overflow: hidden; margin-top: 0.4rem; border: 1px solid var(--hairline);
    }
    .data-cell { background: var(--panel); padding: 1.0rem 1.25rem; }
    .cell-label {
        font-family: 'Space Mono', monospace; font-size: 8.5px; letter-spacing: 1.4px; text-transform: uppercase;
        color: var(--slate-dim); margin-bottom: 5px;
    }
    .cell-value { font-family: 'Fraunces', serif; font-size: 0.96rem; font-weight: 500; color: var(--cream); font-variant-numeric: tabular-nums; }
    .cell-value.highlight { color: var(--gold); }
    .cell-value.good { color: var(--green); } .cell-value.bad { color: var(--red); }

    .pd-row { display: flex; justify-content: space-between; align-items: baseline; }
    .pd-track { height: 2px; background: var(--hairline-bright); border-radius: 0; overflow: hidden; margin-top: 0.7rem; }
    .pd-fill { height: 100%; }

    .leaderboard-row {
        display: grid; grid-template-columns: 26px 1fr 110px 84px; gap: 0.9rem; align-items: center;
        padding: 0.65rem 0.4rem; border-bottom: 1px solid var(--hairline);
        font-family: 'Space Mono', monospace; font-size: 11.5px;
    }
    .leaderboard-row:last-child { border-bottom: none; }
    .leaderboard-row.me { background: var(--gold-dim); border-radius: 2px; padding-left: 0.7rem; margin: 0 -0.4rem; }
    .lb-rank { color: var(--slate-dim); }
    .lb-name { color: var(--cream); font-family: 'Inter', sans-serif; font-weight: 500; }
    .lb-cap { text-align: right; font-variant-numeric: tabular-nums; }
    .lb-cap.pos { color: var(--green); } .lb-cap.neg { color: var(--red); }
    .lb-status { text-align: center; font-size: 8.5px; letter-spacing: 1px; padding: 2px 5px; border-radius: 2px; }
    .lb-waiting { color: var(--amber); background: rgba(201,138,62,0.1); }
    .lb-done { color: var(--green); background: rgba(90,155,126,0.1); }
    .lb-streak { color: var(--gold); font-size: 9.5px; margin-left: 4px; }

    .stButton > button {
        font-family: 'Fraunces', serif !important; font-weight: 600 !important; font-size: 13px !important;
        letter-spacing: 1.2px !important; text-transform: uppercase !important; border-radius: 2px !important;
        height: 50px !important; border: 1px solid transparent !important; transition: all 0.25s ease !important;
    }
    .stButton > button[kind="primary"] {
        background: var(--gold) !important; color: var(--ink) !important; box-shadow: none !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: #ddc07f !important; box-shadow: 0 4px 20px var(--gold-glow) !important; transform: translateY(-1px);
    }
    .stButton > button[kind="secondary"] {
        background: transparent !important; color: var(--slate) !important; border: 1px solid var(--hairline-bright) !important;
    }
    .stButton > button[kind="secondary"]:hover {
        border-color: rgba(212,87,74,0.4) !important; color: var(--red) !important; background: rgba(212,87,74,0.05) !important;
    }

    .waiting-badge, .locked-badge {
        font-family: 'Space Mono', monospace; font-size: 11px; letter-spacing: 0.5px;
        padding: 10px 18px; border-radius: 2px; text-align: center;
    }
    .waiting-badge { color: var(--amber); background: rgba(201,138,62,0.08); border: 1px solid rgba(201,138,62,0.2); }
    .locked-badge { color: var(--green); background: rgba(90,155,126,0.08); border: 1px solid rgba(90,155,126,0.2); }

    .streak-banner {
        text-align: center; padding: 1.1rem 1.5rem; border-radius: 4px; margin: 0.8rem 0 0;
        background: linear-gradient(135deg, var(--gold-dim), rgba(156,122,53,0.16));
        border: 1px solid rgba(156,122,53,0.35);
        animation: streak-pop 0.35s ease;
    }
    @keyframes streak-pop { from { opacity: 0; transform: translateY(-6px); } to { opacity: 1; transform: translateY(0); } }
    .streak-title {
        font-family: 'Fraunces', serif; font-weight: 700; font-style: italic; font-size: 1.3rem; color: var(--gold);
        letter-spacing: 0.3px; margin: 0;
    }
    .streak-sub {
        font-family: 'Space Mono', monospace; font-size: 10px; letter-spacing: 1.5px; text-transform: uppercase;
        color: var(--slate); margin-top: 0.3rem;
    }

    h1, h2, h3 { font-family: 'Fraunces', serif !important; color: var(--cream) !important; }
    input[type="text"] {
        background: var(--panel-raised) !important; border: 1px solid var(--hairline-bright) !important;
        color: var(--cream) !important; border-radius: 2px !important; font-family: 'Inter', sans-serif !important;
    }
    .stAlert { border-radius: 2px !important; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# GAME CONSTANTS & LOGIC
# ═══════════════════════════════════════════════════════════════════════
INITIAL_CAPITAL = 10_000_000
MAX_ROUNDS = 8
RISK_FREE_RATE = 0.05
HOST_NAME = "Anıl K"   # this name is always the host — independent of join order or session

STREAK_LEVELS = [
    (3, "Sharp Eye", "3 correct calls in a row"),
    (5, "Risk Whisperer", "5 correct calls in a row"),
]

SECTORS = {
    'Technology': {'base_pd': 0.03, 'beta': 1.3, 'icon': '◈'},
    'Healthcare': {'base_pd': 0.02, 'beta': 0.7, 'icon': '◉'},
    'Energy': {'base_pd': 0.06, 'beta': 1.2, 'icon': '◆'},
    'Real Estate': {'base_pd': 0.05, 'beta': 0.9, 'icon': '◼'},
    'Manufacturing': {'base_pd': 0.04, 'beta': 1.0, 'icon': '◇'},
    'Financial Services': {'base_pd': 0.035, 'beta': 1.1, 'icon': '▣'}
}
LEVERAGE_RATIOS = ['Very Low (<20%)', 'Low (20-40%)', 'Moderate (40-60%)', 'High (60-80%)', 'Very High (>80%)']
COVERAGE_RATIOS = ['Strong (>3x)', 'Good (2-3x)', 'Adequate (1.5-2x)', 'Weak (1-1.5x)', 'Critical (<1x)']
PROFITABILITY = ['Strong (>15%)', 'Good (10-15%)', 'Average (5-10%)', 'Weak (0-5%)', 'Loss Making']

def calculate_pd(c):
    base = SECTORS[c['sector']]['base_pd']
    lev = {'Very Low (<20%)': -0.02, 'Low (20-40%)': 0, 'Moderate (40-60%)': 0.02, 'High (60-80%)': 0.05, 'Very High (>80%)': 0.10}[c['leverage']]
    cov = {'Strong (>3x)': -0.03, 'Good (2-3x)': -0.01, 'Adequate (1.5-2x)': 0.01, 'Weak (1-1.5x)': 0.04, 'Critical (<1x)': 0.08}[c['coverage']]
    prof = {'Strong (>15%)': -0.02, 'Good (10-15%)': 0, 'Average (5-10%)': 0.02, 'Weak (0-5%)': 0.04, 'Loss Making': 0.07}[c['profitability']]
    size = -0.01 if c['size'] == 'Large' else 0.01 if c['size'] == 'Small' else 0
    return round(max(0.01, min(0.40, base + lev + cov + prof + size)), 4)

def derive_financial_metrics(rng, c):
    """Generates additional display metrics (EBITDA, Turnover, Debt-to-Equity,
    Current Ratio, Net Margin, Quick Ratio) consistent with the existing risk
    factors, so the numbers tell a coherent story rather than being random noise."""
    size_mult = {'Small': 1, 'Medium': 3, 'Large': 8}[c['size']]
    turnover = round(rng.uniform(2_000_000, 6_000_000) * size_mult, -3)

    margin_band = {
        'Strong (>15%)': (0.16, 0.24), 'Good (10-15%)': (0.10, 0.15),
        'Average (5-10%)': (0.05, 0.10), 'Weak (0-5%)': (0.00, 0.05),
        'Loss Making': (-0.12, -0.01)
    }[c['profitability']]
    net_margin = round(rng.uniform(*margin_band), 4)
    ebitda = round(turnover * (net_margin + rng.uniform(0.04, 0.08)), -3)

    de_band = {
        'Very Low (<20%)': (0.1, 0.3), 'Low (20-40%)': (0.3, 0.6),
        'Moderate (40-60%)': (0.6, 1.1), 'High (60-80%)': (1.1, 2.0),
        'Very High (>80%)': (2.0, 3.5)
    }[c['leverage']]
    debt_to_equity = round(rng.uniform(*de_band), 2)

    cr_band = {
        'Strong (>3x)': (2.6, 3.4), 'Good (2-3x)': (2.0, 2.6),
        'Adequate (1.5-2x)': (1.4, 2.0), 'Weak (1-1.5x)': (0.9, 1.4),
        'Critical (<1x)': (0.4, 0.9)
    }[c['coverage']]
    current_ratio = round(rng.uniform(*cr_band), 2)
    quick_ratio = round(max(0.2, current_ratio - rng.uniform(0.3, 0.6)), 2)

    return {
        'turnover': turnover, 'ebitda': ebitda, 'net_margin': net_margin,
        'debt_to_equity': debt_to_equity, 'current_ratio': current_ratio, 'quick_ratio': quick_ratio
    }

def generate_company(seed=None):
    rng = random.Random(seed)
    sector = rng.choice(list(SECTORS.keys()))
    size = rng.choice(['Small', 'Medium', 'Large'])
    leverage = rng.choice(LEVERAGE_RATIOS)
    coverage = rng.choice(COVERAGE_RATIOS)
    profitability = rng.choice(PROFITABILITY)
    loan_amount = rng.randint(2_000_000, 5_000_000) if size == 'Large' else rng.randint(1_000_000, 2_000_000) if size == 'Medium' else rng.randint(500_000, 1_000_000)
    maturity = rng.choice([12, 24, 36, 48, 60])
    years = rng.randint(3, 50)
    prev_defaults = rng.choices([0, 1, 2], weights=[0.7, 0.2, 0.1])[0]
    c = {'sector': sector, 'size': size, 'leverage': leverage, 'coverage': coverage, 'profitability': profitability,
         'loan_amount': loan_amount, 'maturity': maturity, 'years_in_business': years, 'previous_defaults': prev_defaults}
    c['pd'] = calculate_pd(c)
    c['interest_rate'] = round(RISK_FREE_RATE + c['pd'] * 2, 4)
    c.update(derive_financial_metrics(rng, c))
    return c

def compute_round_fate(company, company_seed):
    """Single dice roll per round — determines whether THIS company defaults this round.
    Every player who approves shares this same fate. Deterministic given the company_seed."""
    rng = random.Random(company_seed)
    pd_val = company['pd']
    if pd_val < 0.05: threshold = 0.05
    elif pd_val < 0.10: threshold = 0.25
    elif pd_val < 0.15: threshold = 0.45
    elif pd_val < 0.20: threshold = 0.65
    else: threshold = 0.85
    if company['leverage'] in ['High (60-80%)', 'Very High (>80%)']: threshold *= 1.2
    if company['coverage'] in ['Weak (1-1.5x)', 'Critical (<1x)']: threshold *= 1.15
    if company['profitability'] in ['Weak (0-5%)', 'Loss Making']: threshold *= 1.1
    if company['previous_defaults'] > 0: threshold *= (1 + company['previous_defaults'] * 0.15)
    return rng.random() < min(threshold, 0.95)

def resolve_decision(company, decision, defaulted):
    """Applies the round's shared fate to one player's decision."""
    if decision == 'reject':
        return 'rejected', 0
    if defaulted:
        return 'default', -company['loan_amount']
    else:
        return 'repaid', company['loan_amount'] * company['interest_rate']

def was_decision_correct(decision, defaulted):
    """A decision is 'correct' if: approved a loan that didn't default,
    OR rejected a loan that would have defaulted."""
    if decision == 'approve':
        return not defaulted
    else:
        return defaulted

def streak_award(streak_count):
    """Returns (title, subtitle) for the streak level just reached, or None."""
    award = None
    for threshold, title, subtitle in STREAK_LEVELS:
        if streak_count == threshold:
            award = (title, subtitle)
    return award

# ═══════════════════════════════════════════════════════════════════════
# SHARED STATE BACKEND (JSONBin.io)
# ═══════════════════════════════════════════════════════════════════════
def get_secrets():
    try:
        return st.secrets["JSONBIN_BIN_ID"], st.secrets["JSONBIN_API_KEY"]
    except Exception:
        return None, None

JSONBIN_BIN_ID, JSONBIN_API_KEY = get_secrets()
JSONBIN_URL = f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}" if JSONBIN_BIN_ID else None

def remote_read():
    if not JSONBIN_URL:
        return None
    try:
        r = requests.get(JSONBIN_URL + "/latest", headers={"X-Master-Key": JSONBIN_API_KEY}, timeout=5)
        r.raise_for_status()
        return r.json().get("record", {})
    except Exception as e:
        st.session_state["_backend_error"] = str(e)
        return None

def remote_write(data):
    if not JSONBIN_URL:
        return False
    try:
        r = requests.put(JSONBIN_URL, headers={"X-Master-Key": JSONBIN_API_KEY, "Content-Type": "application/json"},
                          data=json.dumps(data), timeout=5)
        r.raise_for_status()
        return True
    except Exception as e:
        st.session_state["_backend_error"] = str(e)
        return False

def default_game_state():
    return {
        "round": 0,
        "max_rounds": MAX_ROUNDS,
        "company_seed": None,
        "company": None,
        "round_defaulted": False,
        "locked": False,
        "host": HOST_NAME,
        "players": {},
        "created_at": time.time(),
    }

def ensure_player(state, name):
    if name not in state["players"]:
        state["players"][name] = {"capital": INITIAL_CAPITAL, "portfolio": [], "decisions": {}, "streak": 0, "best_streak": 0}
    return state

# ═══════════════════════════════════════════════════════════════════════
# SESSION (per-browser identity only — game data lives remotely)
# ═══════════════════════════════════════════════════════════════════════
if "player_name" not in st.session_state:
    st.session_state.player_name = ""
if "last_fetch" not in st.session_state:
    st.session_state.last_fetch = 0
if "remote_state" not in st.session_state:
    st.session_state.remote_state = None
if "show_streak_award" not in st.session_state:
    st.session_state.show_streak_award = None

# ═══════════════════════════════════════════════════════════════════════
# BACKEND CHECK
# ═══════════════════════════════════════════════════════════════════════
if not JSONBIN_URL:
    st.markdown("""
    <div class="apex-header"><div class="header-left">
        <div class="hsbc-mark">HSBC</div><div class="brand-divider"></div>
        <div class="brand-name">Beat the <b>Risk</b></div>
    </div></div>
    """, unsafe_allow_html=True)
    st.error(
        "⚠️ **Shared database connection is not configured.**\n\n"
        "For this app's multiplayer mode to work, you need to add **Secrets** "
        "in Streamlit Cloud: `JSONBIN_BIN_ID` and `JSONBIN_API_KEY`.\n\n"
        "See the comment block at the top of the code file for setup steps."
    )
    st.stop()

def merge_with_defaults(fetched):
    """Ensure all required keys exist, even if the bin was pre-seeded with placeholder content."""
    base = default_game_state()
    if not isinstance(fetched, dict):
        return base
    base.update(fetched)
    if not isinstance(base.get("players"), dict):
        base["players"] = {}
    for p in base["players"].values():
        p.setdefault("streak", 0)
        p.setdefault("best_streak", 0)
    return base

now = time.time()
if st.session_state.remote_state is None or now - st.session_state.last_fetch >= 4:
    fetched = remote_read()
    if fetched is not None:
        merged = merge_with_defaults(fetched)
        st.session_state.remote_state = merged
        st.session_state.last_fetch = now
        st.session_state["_backend_error"] = None
    elif st.session_state.remote_state is None:
        st.error("Could not connect to the server. Please refresh the page.")
        st.stop()
    else:
        err = st.session_state.get("_backend_error", "")
        st.warning(f"⚠️ Could not refresh from the server, showing cached data. ({err[:120]})")

game = st.session_state.remote_state

# ═══════════════════════════════════════════════════════════════════════
# LOGIN GATE
# ═══════════════════════════════════════════════════════════════════════
if not st.session_state.player_name:
    st.markdown("""
    <div class="apex-header"><div class="header-left">
        <div class="hsbc-mark">HSBC</div><div class="brand-divider"></div>
        <div class="brand-name">Beat the <b>Risk</b></div>
    </div><span class="round-pill">Lobby</span></div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='panel' style='max-width:440px;margin:3.5rem auto 0;text-align:center;padding:2.4rem 2rem;'>
        <div class='panel-title' style='justify-content:center;'><span style='flex:none;'>Join the Desk</span></div>
        <p style='font-family:Inter,sans-serif;font-size:13px;color:var(--slate);margin:0 0 1.4rem;'>
            Enter your name to join the risk committee.
        </p>
    """, unsafe_allow_html=True)
    name_input = st.text_input("Enter your name", placeholder="e.g. Alex M.", label_visibility="collapsed")
    join = st.button("Join Game", type="primary", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if join and name_input.strip():
        name = name_input.strip()
        ensure_player(game, name)
        remote_write(game)
        st.session_state.player_name = name
        st.session_state.remote_state = game
        st.rerun()
    elif join:
        st.warning("Please enter a name.")
    st.stop()

player_name = st.session_state.player_name
if player_name not in game["players"]:
    st.session_state.player_name = ""
    st.rerun()
is_host = (player_name == HOST_NAME)
host_present = HOST_NAME in game["players"]

# ═══════════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════════
round_display = game["round"] if game["round"] > 0 else "—"
st.markdown(f"""
<div class="apex-header">
    <div class="header-left">
        <div class="hsbc-mark">HSBC</div>
        <div class="brand-divider"></div>
        <div class="brand-name">Beat the <b>Risk</b></div>
    </div>
    <div style="display:flex;align-items:center;gap:1.1rem;">
        <span class="round-pill"><span class="live-dot"></span>Round {round_display} / {MAX_ROUNDS}</span>
        <span class="player-tag">{player_name} {'<span class=\"host-star\">★ HOST</span>' if is_host else ''}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# HOST PRESENCE GATE
# ═══════════════════════════════════════════════════════════════════════
if not host_present and not is_host:
    st.markdown(f"""
    <div class='panel' style='max-width:480px;margin:3rem auto;text-align:center;padding:2.2rem;'>
        <div class='panel-title' style='justify-content:center;'><span style='flex:none;'>Lobby</span></div>
        <p style='font-family:Inter,sans-serif;font-size:14px;color:var(--slate);margin:0;'>
            <b style='color:var(--cream);'>{HOST_NAME}</b> hasn't joined yet.<br>
            The game will resume once the host joins.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<div style='text-align:center;font-family:\"Space Mono\",monospace;font-size:9px;letter-spacing:1.5px;color:var(--slate-dim);'>· auto-refreshing ·</div>", unsafe_allow_html=True)
    time.sleep(4)
    st.rerun()

# ═══════════════════════════════════════════════════════════════════════
# LOBBY (round 0)
# ═══════════════════════════════════════════════════════════════════════
if game["round"] == 0:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<div class='panel-title'>Lobby — Waiting for Players</div>", unsafe_allow_html=True)
        for p in game["players"]:
            tag = " <span style='color:var(--gold);'>★ HOST</span>" if p == HOST_NAME else ""
            st.markdown(f"<div style='font-family:Inter,sans-serif;font-size:14px;padding:7px 0;color:var(--cream);'>· {p}{tag}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<div class='panel-title'>Host Controls</div>", unsafe_allow_html=True)
        if is_host:
            if st.button("Start Game", type="primary", use_container_width=True):
                latest = remote_read()
                latest = merge_with_defaults(latest) if latest is not None else game
                latest["round"] = 1
                latest["company_seed"] = random.randint(1, 10**9)
                latest["company"] = generate_company(latest["company_seed"])
                latest["round_defaulted"] = compute_round_fate(latest["company"], latest["company_seed"])
                latest["locked"] = False
                ok = remote_write(latest)
                if ok:
                    st.session_state.remote_state = latest
                    st.session_state.last_fetch = time.time()
                    st.rerun()
                else:
                    st.error("Could not start the game — failed to write to the server. Please try again.")
        else:
            st.markdown(f"<div class='waiting-badge'>Waiting for {HOST_NAME} to start the game...</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# ACTIVE ROUND
# ═══════════════════════════════════════════════════════════════════════
elif game["round"] <= MAX_ROUNDS:
    company = game["company"]
    rnd = game["round"]
    me = game["players"][player_name]
    already_decided = str(rnd) in me["decisions"]

    pd_val = company['pd']
    pd_color = '#3f7a5c' if pd_val < 0.05 else '#a8732e' if pd_val < 0.10 else '#c9763a' if pd_val < 0.20 else '#b8453a'
    pd_fill = min(pd_val / 0.4 * 100, 100)

    col_main, col_side = st.columns([1.6, 1], gap="large")

    with col_main:
        st.markdown(f"""
        <div class="panel">
            <div class="panel-title">Credit Application · {company['sector']} · {company['size']} Cap</div>
            <div class="data-grid">
                <div class="data-cell"><div class="cell-label">Loan Amount</div><div class="cell-value highlight">${company['loan_amount']:,.0f}</div></div>
                <div class="data-cell"><div class="cell-label">Maturity</div><div class="cell-value">{company['maturity']} mo</div></div>
                <div class="data-cell"><div class="cell-label">Interest Rate</div><div class="cell-value highlight">{company['interest_rate']*100:.2f}%</div></div>
                <div class="data-cell"><div class="cell-label">Years Operating</div><div class="cell-value">{company['years_in_business']} yrs</div></div>
                <div class="data-cell"><div class="cell-label">Prior Defaults</div><div class="cell-value {'good' if company['previous_defaults']==0 else 'bad'}">{company['previous_defaults']}</div></div>
                <div class="data-cell"><div class="cell-label">Sector</div><div class="cell-value">{company['sector']}</div></div>
                <div class="data-cell"><div class="cell-label">Turnover</div><div class="cell-value">${company['turnover']:,.0f}</div></div>
                <div class="data-cell"><div class="cell-label">EBITDA</div><div class="cell-value">${company['ebitda']:,.0f}</div></div>
                <div class="data-cell"><div class="cell-label">Net Margin</div><div class="cell-value {'good' if company['net_margin']>=0.10 else 'bad' if company['net_margin']<0 else ''}">{company['net_margin']*100:.1f}%</div></div>
                <div class="data-cell"><div class="cell-label">Leverage</div><div class="cell-value">{company['leverage']}</div></div>
                <div class="data-cell"><div class="cell-label">Debt / Equity</div><div class="cell-value {'good' if company['debt_to_equity']<0.6 else 'bad' if company['debt_to_equity']>1.5 else ''}">{company['debt_to_equity']:.2f}x</div></div>
                <div class="data-cell"><div class="cell-label">Interest Coverage</div><div class="cell-value">{company['coverage']}</div></div>
                <div class="data-cell"><div class="cell-label">Current Ratio</div><div class="cell-value {'good' if company['current_ratio']>=2 else 'bad' if company['current_ratio']<1 else ''}">{company['current_ratio']:.2f}x</div></div>
                <div class="data-cell"><div class="cell-label">Quick Ratio</div><div class="cell-value {'good' if company['quick_ratio']>=1.5 else 'bad' if company['quick_ratio']<0.8 else ''}">{company['quick_ratio']:.2f}x</div></div>
                <div class="data-cell"><div class="cell-label">Profitability</div><div class="cell-value">{company['profitability']}</div></div>
            </div>
            <div style="margin-top:1.4rem;">
                <div class="pd-row"><span class="cell-label">Probability of Default</span>
                <span style="font-family:'Fraunces',serif;font-weight:600;font-size:1.3rem;color:{pd_color};font-variant-numeric:tabular-nums;">{pd_val*100:.2f}%</span></div>
                <div class="pd-track"><div class="pd-fill" style="width:{pd_fill}%;background:{pd_color};"></div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:1.1rem;'></div>", unsafe_allow_html=True)

        if st.session_state.show_streak_award:
            title, subtitle = st.session_state.show_streak_award
            st.markdown(f"""
            <div class="streak-banner">
                <p class="streak-title">{title}</p>
                <p class="streak-sub">{subtitle}</p>
            </div>
            """, unsafe_allow_html=True)
            st.session_state.show_streak_award = None
            time.sleep(2)
            st.rerun()

        if game["locked"]:
            st.markdown("<div class='locked-badge'>This round is locked — results will be announced by the host</div>", unsafe_allow_html=True)
        elif already_decided:
            decision_made = me["decisions"][str(rnd)]
            label = "Approved" if decision_made == "approve" else "Rejected"
            st.markdown(f"<div class='locked-badge'>Decision recorded — <b>{label}</b>. Waiting for other players.</div>", unsafe_allow_html=True)
        else:
            b1, b2 = st.columns(2)
            with b1:
                approve_clicked = st.button("Approve", type="primary", use_container_width=True, key=f"app_{rnd}")
            with b2:
                reject_clicked = st.button("Reject", type="secondary", use_container_width=True, key=f"rej_{rnd}")

            if approve_clicked or reject_clicked:
                decision = "approve" if approve_clicked else "reject"
                latest = remote_read() or game
                latest_me = latest["players"].setdefault(player_name, {"capital": INITIAL_CAPITAL, "portfolio": [], "decisions": {}, "streak": 0, "best_streak": 0})
                if str(rnd) not in latest_me["decisions"]:
                    shared_fate = latest.get("round_defaulted", False)
                    outcome, delta = resolve_decision(company, decision, shared_fate)
                    correct = was_decision_correct(decision, shared_fate)

                    latest_me["decisions"][str(rnd)] = decision
                    latest_me["capital"] += delta
                    latest_me["portfolio"].append({
                        "round": rnd, "sector": company["sector"], "amount": company["loan_amount"],
                        "pd": pd_val, "decision": decision, "outcome": outcome, "delta": delta, "correct": correct
                    })

                    if correct:
                        latest_me["streak"] = latest_me.get("streak", 0) + 1
                        latest_me["best_streak"] = max(latest_me.get("best_streak", 0), latest_me["streak"])
                        award = streak_award(latest_me["streak"])
                        if award:
                            st.session_state.show_streak_award = award
                    else:
                        latest_me["streak"] = 0

                    latest["players"][player_name] = latest_me
                    remote_write(latest)
                    st.session_state.remote_state = latest
                st.rerun()

    with col_side:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<div class='panel-title'>Live Leaderboard</div>", unsafe_allow_html=True)
        ranked = sorted(game["players"].items(), key=lambda kv: kv[1]["capital"], reverse=True)
        for i, (pname, pdata) in enumerate(ranked, 1):
            delta = pdata["capital"] - INITIAL_CAPITAL
            cap_cls = "pos" if delta >= 0 else "neg"
            decided = str(rnd) in pdata["decisions"]
            status_html = "<span class='lb-status lb-done'>READY</span>" if decided else "<span class='lb-status lb-waiting'>WAITING</span>"
            streak_html = f"<span class='lb-streak'>🔥{pdata.get('streak', 0)}</span>" if pdata.get("streak", 0) >= 2 else ""
            row_cls = "leaderboard-row me" if pname == player_name else "leaderboard-row"
            st.markdown(f"""
            <div class="{row_cls}">
                <span class="lb-rank">{i:02d}</span>
                <span class="lb-name">{pname}{streak_html}</span>
                <span class="lb-cap {cap_cls}">${pdata['capital']:,.0f}</span>
                {status_html}
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        if is_host:
            st.markdown("<div style='height:1.1rem;'></div><div class='panel'>", unsafe_allow_html=True)
            st.markdown("<div class='panel-title'>Host Controls</div>", unsafe_allow_html=True)
            n_decided = sum(1 for p in game["players"].values() if str(rnd) in p["decisions"])
            n_total = len(game["players"])
            st.markdown(f"<div style='font-family:\"Space Mono\",monospace;font-size:12px;color:var(--slate);margin-bottom:0.9rem;'>{n_decided} / {n_total} players decided</div>", unsafe_allow_html=True)
            next_label = "Next Round" if rnd < MAX_ROUNDS else "End Game"
            if st.button(next_label, type="primary", use_container_width=True):
                latest = remote_read()
                latest = merge_with_defaults(latest) if latest is not None else game
                if rnd < MAX_ROUNDS:
                    latest["round"] = rnd + 1
                    latest["company_seed"] = random.randint(1, 10**9)
                    latest["company"] = generate_company(latest["company_seed"])
                    latest["round_defaulted"] = compute_round_fate(latest["company"], latest["company_seed"])
                else:
                    latest["round"] = MAX_ROUNDS + 1
                latest["locked"] = False
                ok = remote_write(latest)
                if ok:
                    st.session_state.remote_state = latest
                    st.session_state.last_fetch = time.time()
                    st.rerun()
                else:
                    st.error("Could not update the round — failed to write to the server. Please try again.")
            st.markdown("</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# GAME OVER
# ═══════════════════════════════════════════════════════════════════════
else:
    st.markdown("""
    <div style='text-align:center;padding:2.5rem 0 1.8rem;'>
        <div class='panel-title' style='justify-content:center;'><span style='flex:none;'>Final Results</span></div>
        <h1 style='font-family:Fraunces,serif;font-weight:300;font-style:italic;font-size:3rem;color:var(--cream);margin:0.3rem 0;'>
            Game <span style='font-weight:700;font-style:normal;color:var(--gold);'>Complete</span>
        </h1>
    </div>
    """, unsafe_allow_html=True)

    ranked = sorted(game["players"].items(), key=lambda kv: kv[1]["capital"], reverse=True)
    st.markdown("<div class='panel' style='max-width:680px;margin:0 auto;'>", unsafe_allow_html=True)
    for i, (pname, pdata) in enumerate(ranked, 1):
        delta = pdata["capital"] - INITIAL_CAPITAL
        delta_pct = delta / INITIAL_CAPITAL * 100
        cap_cls = "pos" if delta >= 0 else "neg"
        rank_style = "color:var(--gold);font-weight:700;" if i == 1 else ""
        row_cls = "leaderboard-row me" if pname == player_name else "leaderboard-row"
        best_streak = pdata.get("best_streak", 0)
        streak_html = f"<span class='lb-streak'>best streak: {best_streak}</span>" if best_streak >= 2 else ""
        st.markdown(f"""
        <div class="{row_cls}" style="grid-template-columns: 36px 1fr 140px 90px;">
            <span class="lb-rank" style="{rank_style}">{i:02d}</span>
            <span class="lb-name">{pname}{streak_html}</span>
            <span class="lb-cap {cap_cls}">${pdata['capital']:,.0f}</span>
            <span class="lb-cap {cap_cls}">{delta_pct:+.1f}%</span>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if is_host:
        st.markdown("<div style='height:1.3rem;'></div>", unsafe_allow_html=True)
        if st.button("Start New Game", type="primary", use_container_width=True):
            new_state = default_game_state()
            ok = remote_write(new_state)
            if ok:
                st.session_state.remote_state = new_state
                st.session_state.last_fetch = time.time()
                st.session_state.player_name = ""
                st.rerun()
            else:
                st.error("Could not start a new game — failed to write to the server. Please try again.")

# ═══════════════════════════════════════════════════════════════════════
# AUTO-REFRESH (polling)
# ═══════════════════════════════════════════════════════════════════════
st.markdown("<div style='text-align:center;padding:1.4rem 0 0.4rem;font-family:\"Space Mono\",monospace;font-size:9px;letter-spacing:1.5px;color:var(--slate-dim);'>· auto-refreshing ·</div>", unsafe_allow_html=True)
time.sleep(4)
st.rerun()
