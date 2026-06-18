"""
BEAT THE RISK — Multiplayer Edition
─────────────────────────────────────────────────────────────────
Çok oyunculu, eşzamanlı kredi risk simülasyonu.
Paylaşılan durum JSONBin.io üzerinde tutulur (kurulum/indirme gerektirmez).

KURULUM (bkz. son satırlardaki yorum / README):
1. https://jsonbin.io üzerinde ücretsiz hesap aç
2. "Create Bin" ile boş bir JSON ({}) oluştur, BIN_ID'yi not al
3. Hesabından "X-Master-Key" değerini al
4. Streamlit Cloud > App > Settings > Secrets içine şunu yapıştır:

    JSONBIN_BIN_ID = "senin-bin-id'in"
    JSONBIN_API_KEY = "senin-master-key'in"

5. Bu dosyayı GitHub reposuna push et, Streamlit Community Cloud'da deploy et.
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
# STYLE (charcoal theme — same as single-player redesign)
# ═══════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300;9..144,500;9..144,600;9..144,700&family=Inter:wght@300;400;500;600&family=Space+Mono:wght@400;500&display=swap');

    :root {
        --ink: #0d0d0f;
        --panel: #16161a;
        --panel-raised: #1c1c21;
        --hairline: rgba(245,240,232,0.09);
        --hairline-bright: rgba(245,240,232,0.16);
        --gold: #c9a961;
        --gold-dim: rgba(201,169,97,0.10);
        --gold-glow: rgba(201,169,97,0.35);
        --cream: #f5f0e8;
        --slate: #8b94a0;
        --slate-dim: #565c66;
        --red: #d4574a;
        --green: #5a9b7e;
        --amber: #c98a3e;
    }
    * { box-sizing: border-box; }
    .stApp { background: var(--ink) !important; font-family: 'Inter', sans-serif !important; }
    #MainMenu, footer, header { visibility: hidden; }
    .stDeployButton { display: none; }
    [data-testid="stToolbar"] { display: none; }
    .block-container { padding: 1.2rem 2.2rem !important; max-width: 1400px !important; margin: 0 auto !important; }

    /* Faint ledger-line texture across the whole app */
    .stApp::before {
        content: '';
        position: fixed; inset: 0; pointer-events: none; z-index: 0;
        background-image: repeating-linear-gradient(
            to bottom, transparent 0, transparent 39px, rgba(245,240,232,0.025) 40px
        );
    }

    /* ═══════════════════════ HEADER ═══════════════════════ */
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
        background: #f5f0e8; color: #B8121E;
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

    /* ═══════════════════════ PANELS ═══════════════════════ */
    .panel {
        background: var(--panel); border: 1px solid var(--hairline); border-radius: 4px; padding: 1.7rem;
    }
    .panel-title {
        font-family: 'Space Mono', monospace; font-size: 9.5px; letter-spacing: 2.2px; text-transform: uppercase;
        color: var(--slate-dim); margin-bottom: 1.1rem; display: flex; align-items: center; gap: 0.5rem;
    }
    .panel-title::after { content: ''; flex: 1; height: 1px; background: var(--hairline); }

    /* ═══════════════════════ DATA GRID ═══════════════════════ */
    .data-grid {
        display: grid; grid-template-columns: 1fr 1fr; gap: 1px; background: var(--hairline);
        border-radius: 3px; overflow: hidden; margin-top: 0.4rem; border: 1px solid var(--hairline);
    }
    .data-cell { background: var(--panel); padding: 1.05rem 1.4rem; }
    .cell-label {
        font-family: 'Space Mono', monospace; font-size: 9px; letter-spacing: 1.6px; text-transform: uppercase;
        color: var(--slate-dim); margin-bottom: 5px;
    }
    .cell-value { font-family: 'Fraunces', serif; font-size: 1.02rem; font-weight: 500; color: var(--cream); font-variant-numeric: tabular-nums; }
    .cell-value.highlight { color: var(--gold); }
    .cell-value.good { color: var(--green); } .cell-value.bad { color: var(--red); }

    /* ═══════════════════════ PD METER ═══════════════════════ */
    .pd-row { display: flex; justify-content: space-between; align-items: baseline; }
    .pd-track { height: 2px; background: var(--hairline-bright); border-radius: 0; overflow: hidden; margin-top: 0.7rem; }
    .pd-fill { height: 100%; }

    /* ═══════════════════════ LEADERBOARD ═══════════════════════ */
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

    /* ═══════════════════════ BUTTONS ═══════════════════════ */
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

    /* ═══════════════════════ TEXT ELEMENTS ═══════════════════════ */
    h1, h2, h3 { font-family: 'Fraunces', serif !important; color: var(--cream) !important; }
    input[type="text"] {
        background: var(--panel-raised) !important; border: 1px solid var(--hairline-bright) !important;
        color: var(--cream) !important; border-radius: 2px !important; font-family: 'Inter', sans-serif !important;
    }
    .stAlert { border-radius: 2px !important; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# GAME CONSTANTS & LOGIC (unchanged from single-player version)
# ═══════════════════════════════════════════════════════════════════════
INITIAL_CAPITAL = 10_000_000
MAX_ROUNDS = 8
RISK_FREE_RATE = 0.05

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
        "round": 0,                 # 0 = lobby, not started
        "max_rounds": MAX_ROUNDS,
        "company_seed": None,
        "company": None,
        "round_defaulted": False,   # the shared fate for the current round (set once when round starts)
        "locked": False,            # host can lock a round to stop late decisions
        "host": None,
        "players": {},              # name -> {capital, portfolio[], decisions:{round: 'approve'/'reject'}}
        "created_at": time.time(),
    }

def ensure_player(state, name):
    if name not in state["players"]:
        state["players"][name] = {"capital": INITIAL_CAPITAL, "portfolio": [], "decisions": {}}
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
        "⚠️ **Paylaşılan veritabanı bağlantısı yapılandırılmamış.**\n\n"
        "Bu uygulamanın çok oyunculu çalışması için Streamlit Cloud'daki **Secrets** "
        "ayarına `JSONBIN_BIN_ID` ve `JSONBIN_API_KEY` eklenmesi gerekiyor.\n\n"
        "Kurulum adımları için kod dosyasının başındaki yorum satırlarına bakın."
    )
    st.stop()

# Fetch remote state (throttled)
def merge_with_defaults(fetched):
    """Ensure all required keys exist, even if the bin was pre-seeded with placeholder content."""
    base = default_game_state()
    if not isinstance(fetched, dict):
        return base
    base.update(fetched)
    # players must be a dict even if missing/None in fetched data
    if not isinstance(base.get("players"), dict):
        base["players"] = {}
    return base

now = time.time()
if st.session_state.remote_state is None or now - st.session_state.last_fetch > 2:
    fetched = remote_read()
    if fetched is not None:
        merged = merge_with_defaults(fetched)
        st.session_state.remote_state = merged
        st.session_state.last_fetch = now
        # If the bin didn't have our keys yet, persist the proper structure now
        if merged != fetched:
            remote_write(merged)
    elif st.session_state.remote_state is None:
        st.error("Sunucuya bağlanılamadı. Lütfen sayfayı yenileyin.")
        st.stop()

game = st.session_state.remote_state

# ═══════════════════════════════════════════════════════════════════════
# LOGIN GATE
# ═══════════════════════════════════════════════════════════════════════
if not st.session_state.player_name:
    st.markdown("""
    <div class="apex-header"><div class="header-left">
        <div class="hsbc-mark">HSBC</div><div class="brand-divider"></div>
        <div class="brand-name">Beat the <b>Risk</b></div>
    </div><span class="round-pill">Lobi</span></div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='panel' style='max-width:440px;margin:3.5rem auto 0;text-align:center;padding:2.4rem 2rem;'>
        <div class='panel-title' style='justify-content:center;'><span style='flex:none;'>Krediye Giriş</span></div>
        <p style='font-family:Inter,sans-serif;font-size:13px;color:var(--slate);margin:0 0 1.4rem;'>
            Risk komitesine katılmak için adınızı girin.
        </p>
    """, unsafe_allow_html=True)
    name_input = st.text_input("Adınızı girin", placeholder="örn. Ahmet K.", label_visibility="collapsed")
    join = st.button("Oyuna Katıl", type="primary", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if join and name_input.strip():
        name = name_input.strip()
        if game["host"] is None:
            game["host"] = name
        ensure_player(game, name)
        remote_write(game)
        st.session_state.player_name = name
        st.session_state.remote_state = game
        st.rerun()
    elif join:
        st.warning("Lütfen bir isim girin.")
    st.stop()

player_name = st.session_state.player_name
ensure_player(game, player_name)
is_host = (game["host"] == player_name)

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
# LOBBY (round 0 — waiting to start)
# ═══════════════════════════════════════════════════════════════════════
if game["round"] == 0:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<div class='panel-title'>Lobi — Oyuncular Bekleniyor</div>", unsafe_allow_html=True)
        for p in game["players"]:
            tag = " <span style='color:var(--gold);'>★ HOST</span>" if p == game["host"] else ""
            st.markdown(f"<div style='font-family:Inter,sans-serif;font-size:14px;padding:7px 0;color:var(--cream);'>· {p}{tag}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<div class='panel-title'>Host Kontrolü</div>", unsafe_allow_html=True)
        if is_host:
            if st.button("Oyunu Başlat", type="primary", use_container_width=True):
                game["round"] = 1
                game["company_seed"] = random.randint(1, 10**9)
                game["company"] = generate_company(game["company_seed"])
                game["round_defaulted"] = compute_round_fate(game["company"], game["company_seed"])
                game["locked"] = False
                remote_write(game)
                st.session_state.remote_state = game
                st.rerun()
        else:
            st.markdown("<div class='waiting-badge'>Host'un oyunu başlatması bekleniyor...</div>", unsafe_allow_html=True)
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
    pd_color = '#2ed573' if pd_val < 0.05 else '#ffa502' if pd_val < 0.10 else '#ff6b35' if pd_val < 0.20 else '#ff4757'
    pd_fill = min(pd_val / 0.4 * 100, 100)

    col_main, col_side = st.columns([1.6, 1], gap="large")

    with col_main:
        st.markdown(f"""
        <div class="panel">
            <div class="panel-title">Kredi Başvurusu · {company['sector']} · {company['size']} Cap</div>
            <div class="data-grid">
                <div class="data-cell"><div class="cell-label">Tutar</div><div class="cell-value highlight">${company['loan_amount']:,.0f}</div></div>
                <div class="data-cell"><div class="cell-label">Vade</div><div class="cell-value">{company['maturity']} ay</div></div>
                <div class="data-cell"><div class="cell-label">Faiz Oranı</div><div class="cell-value highlight">{company['interest_rate']*100:.2f}%</div></div>
                <div class="data-cell"><div class="cell-label">Faaliyet Yılı</div><div class="cell-value">{company['years_in_business']} yıl</div></div>
                <div class="data-cell"><div class="cell-label">Kaldıraç</div><div class="cell-value">{company['leverage']}</div></div>
                <div class="data-cell"><div class="cell-label">Faiz Karşılama</div><div class="cell-value">{company['coverage']}</div></div>
                <div class="data-cell"><div class="cell-label">Karlılık</div><div class="cell-value">{company['profitability']}</div></div>
                <div class="data-cell"><div class="cell-label">Önceki Temerrüt</div><div class="cell-value {'good' if company['previous_defaults']==0 else 'bad'}">{company['previous_defaults']}</div></div>
            </div>
            <div style="margin-top:1.4rem;">
                <div class="pd-row"><span class="cell-label">Temerrüt Olasılığı</span>
                <span style="font-family:'Fraunces',serif;font-weight:600;font-size:1.3rem;color:{pd_color};font-variant-numeric:tabular-nums;">{pd_val*100:.2f}%</span></div>
                <div class="pd-track"><div class="pd-fill" style="width:{pd_fill}%;background:{pd_color};"></div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:1.1rem;'></div>", unsafe_allow_html=True)

        if game["locked"]:
            st.markdown("<div class='locked-badge'>Bu round kilitlendi — sonuçlar host tarafından açıklanacak</div>", unsafe_allow_html=True)
        elif already_decided:
            decision_made = me["decisions"][str(rnd)]
            label = "Onayladınız" if decision_made == "approve" else "Reddettiniz"
            st.markdown(f"<div class='locked-badge'>Kararınız kaydedildi — <b>{label}</b>. Diğer oyuncular bekleniyor.</div>", unsafe_allow_html=True)
        else:
            b1, b2 = st.columns(2)
            with b1:
                approve_clicked = st.button("Onayla", type="primary", use_container_width=True, key=f"app_{rnd}")
            with b2:
                reject_clicked = st.button("Reddet", type="secondary", use_container_width=True, key=f"rej_{rnd}")

            if approve_clicked or reject_clicked:
                decision = "approve" if approve_clicked else "reject"
                # re-fetch latest before writing to minimize race conditions
                latest = remote_read() or game
                latest_me = latest["players"].setdefault(player_name, {"capital": INITIAL_CAPITAL, "portfolio": [], "decisions": {}})
                if str(rnd) not in latest_me["decisions"]:
                    shared_fate = latest.get("round_defaulted", False)
                    outcome, delta = resolve_decision(company, decision, shared_fate)
                    latest_me["decisions"][str(rnd)] = decision
                    latest_me["capital"] += delta
                    latest_me["portfolio"].append({
                        "round": rnd, "sector": company["sector"], "amount": company["loan_amount"],
                        "pd": pd_val, "decision": decision, "outcome": outcome, "delta": delta
                    })
                    latest["players"][player_name] = latest_me
                    remote_write(latest)
                    st.session_state.remote_state = latest
                st.rerun()

    with col_side:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<div class='panel-title'>Canlı Sıralama</div>", unsafe_allow_html=True)
        ranked = sorted(game["players"].items(), key=lambda kv: kv[1]["capital"], reverse=True)
        for i, (pname, pdata) in enumerate(ranked, 1):
            delta = pdata["capital"] - INITIAL_CAPITAL
            cap_cls = "pos" if delta >= 0 else "neg"
            decided = str(rnd) in pdata["decisions"]
            status_html = "<span class='lb-status lb-done'>HAZIR</span>" if decided else "<span class='lb-status lb-waiting'>BEKLİYOR</span>"
            row_cls = "leaderboard-row me" if pname == player_name else "leaderboard-row"
            st.markdown(f"""
            <div class="{row_cls}">
                <span class="lb-rank">{i:02d}</span>
                <span class="lb-name">{pname}</span>
                <span class="lb-cap {cap_cls}">${pdata['capital']:,.0f}</span>
                {status_html}
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        if is_host:
            st.markdown("<div style='height:1.1rem;'></div><div class='panel'>", unsafe_allow_html=True)
            st.markdown("<div class='panel-title'>Host Kontrolü</div>", unsafe_allow_html=True)
            n_decided = sum(1 for p in game["players"].values() if str(rnd) in p["decisions"])
            n_total = len(game["players"])
            st.markdown(f"<div style='font-family:\"Space Mono\",monospace;font-size:12px;color:var(--slate);margin-bottom:0.9rem;'>{n_decided} / {n_total} oyuncu karar verdi</div>", unsafe_allow_html=True)
            next_label = "Sonraki Round" if rnd < MAX_ROUNDS else "Oyunu Bitir"
            if st.button(next_label, type="primary", use_container_width=True):
                if rnd < MAX_ROUNDS:
                    game["round"] += 1
                    game["company_seed"] = random.randint(1, 10**9)
                    game["company"] = generate_company(game["company_seed"])
                    game["round_defaulted"] = compute_round_fate(game["company"], game["company_seed"])
                else:
                    game["round"] = MAX_ROUNDS + 1
                game["locked"] = False
                remote_write(game)
                st.session_state.remote_state = game
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# GAME OVER — final leaderboard
# ═══════════════════════════════════════════════════════════════════════
else:
    st.markdown("""
    <div style='text-align:center;padding:2.5rem 0 1.8rem;'>
        <div class='panel-title' style='justify-content:center;'><span style='flex:none;'>Final Sonuçlar</span></div>
        <h1 style='font-family:Fraunces,serif;font-weight:300;font-style:italic;font-size:3rem;color:var(--cream);margin:0.3rem 0;'>
            Oyun <span style='font-weight:700;font-style:normal;color:var(--gold);'>Tamamlandı</span>
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
        st.markdown(f"""
        <div class="{row_cls}" style="grid-template-columns: 36px 1fr 140px 90px;">
            <span class="lb-rank" style="{rank_style}">{i:02d}</span>
            <span class="lb-name">{pname}</span>
            <span class="lb-cap {cap_cls}">${pdata['capital']:,.0f}</span>
            <span class="lb-cap {cap_cls}">{delta_pct:+.1f}%</span>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if is_host:
        st.markdown("<div style='height:1.3rem;'></div>", unsafe_allow_html=True)
        if st.button("Yeni Oyun Başlat", type="primary", use_container_width=True):
            new_state = default_game_state()
            new_state["host"] = game["host"]
            for pname in game["players"]:
                ensure_player(new_state, pname)
            remote_write(new_state)
            st.session_state.remote_state = new_state
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════
# AUTO-REFRESH (polling) — keeps everyone's screen in sync
# ═══════════════════════════════════════════════════════════════════════
st.markdown("<div style='text-align:center;padding:1.4rem 0 0.4rem;font-family:\"Space Mono\",monospace;font-size:9px;letter-spacing:1.5px;color:var(--slate-dim);'>· otomatik yenileniyor ·</div>", unsafe_allow_html=True)
time.sleep(2.5)
st.rerun()
