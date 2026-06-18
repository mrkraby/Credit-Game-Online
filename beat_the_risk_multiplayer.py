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
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:wght@300;400;500&display=swap');

    :root {
        --void: #141414; --surface: #1c1c1c; --panel: #222222;
        --border: rgba(255,255,255,0.07); --border-bright: rgba(255,255,255,0.13);
        --accent: #e8ff47; --accent-dim: rgba(232,255,71,0.08); --accent-glow: rgba(232,255,71,0.25);
        --red: #ff4757; --green: #2ed573; --orange: #ffa502; --blue: #1e90ff;
        --text: #ededed; --muted: #6b7280; --subtle: #333333;
    }
    * { box-sizing: border-box; }
    .stApp { background: var(--void) !important; font-family: 'DM Sans', sans-serif !important; }
    #MainMenu, footer, header { visibility: hidden; }
    .stDeployButton { display: none; }
    [data-testid="stToolbar"] { display: none; }
    .block-container { padding: 1rem 2rem !important; max-width: 100% !important; }

    .apex-header {
        background: var(--surface); border: 1px solid var(--border); border-radius: 14px;
        padding: 1rem 2rem; display: flex; align-items: center; justify-content: space-between;
        margin-bottom: 1.2rem;
    }
    .header-left { display: flex; align-items: center; gap: 1.5rem; }
    .hsbc-mark { background: #DB0011; color: white; font-family: 'Syne', sans-serif; font-weight: 800;
        font-size: 13px; letter-spacing: 2px; padding: 5px 12px; border-radius: 4px; }
    .brand-name { font-family: 'Syne', sans-serif; font-weight: 800; font-size: 17px; color: var(--text);
        letter-spacing: 2.5px; text-transform: uppercase; }
    .brand-name span { color: var(--accent); }
    .round-pill { font-family: 'DM Mono', monospace; font-size: 11px; font-weight: 500; color: var(--accent);
        background: var(--accent-dim); border: 1px solid rgba(232,255,71,0.2); padding: 5px 14px;
        border-radius: 100px; letter-spacing: 1px; text-transform: uppercase; }
    .live-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--green);
        box-shadow: 0 0 8px var(--green); display: inline-block; margin-right: 6px;
        animation: pulse-dot 2s ease infinite; }
    @keyframes pulse-dot { 0%,100%{opacity:1;} 50%{opacity:0.5;} }

    .panel { background: var(--panel); border: 1px solid var(--border); border-radius: 14px; padding: 1.5rem; }
    .panel-title { font-family: 'DM Mono', monospace; font-size: 10px; letter-spacing: 2px;
        text-transform: uppercase; color: var(--muted); margin-bottom: 1rem; }

    .data-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1px; background: var(--border); border-radius: 10px; overflow: hidden; margin-top: 1rem; }
    .data-cell { background: var(--panel); padding: 1rem 1.3rem; }
    .cell-label { font-family: 'DM Mono', monospace; font-size: 9px; letter-spacing: 1.5px; text-transform: uppercase; color: var(--muted); margin-bottom: 4px; }
    .cell-value { font-family: 'Syne', sans-serif; font-size: 0.95rem; font-weight: 600; color: var(--text); }
    .cell-value.highlight { color: var(--accent); }
    .cell-value.good { color: var(--green); } .cell-value.bad { color: var(--red); }

    .pd-track { height: 4px; background: var(--subtle); border-radius: 4px; overflow: hidden; margin-top: 0.6rem; }
    .pd-fill { height: 100%; border-radius: 4px; }

    .leaderboard-row { display: grid; grid-template-columns: 28px 1fr 100px 90px; gap: 0.8rem; align-items: center;
        padding: 0.6rem 0.8rem; border-bottom: 1px solid var(--border); font-family: 'DM Mono', monospace; font-size: 12px; }
    .leaderboard-row.me { background: var(--accent-dim); border-radius: 6px; }
    .lb-rank { color: var(--muted); }
    .lb-name { color: var(--text); font-weight: 500; }
    .lb-cap { color: var(--text); text-align: right; }
    .lb-cap.pos { color: var(--green); } .lb-cap.neg { color: var(--red); }
    .lb-status { text-align: center; font-size: 9px; letter-spacing: 1px; padding: 2px 6px; border-radius: 4px; }
    .lb-waiting { color: var(--orange); background: rgba(255,165,2,0.1); }
    .lb-done { color: var(--green); background: rgba(46,213,115,0.1); }

    .stButton > button { font-family: 'Syne', sans-serif !important; font-weight: 700 !important; font-size: 12px !important;
        letter-spacing: 2px !important; text-transform: uppercase !important; border-radius: 8px !important; height: 48px !important; border: none !important; }
    .stButton > button[kind="primary"] { background: var(--accent) !important; color: var(--void) !important; }
    .stButton > button[kind="primary"]:hover { background: #f0ff6e !important; }
    .stButton > button[kind="secondary"] { background: transparent !important; color: var(--muted) !important; border: 1px solid var(--border-bright) !important; }

    .waiting-badge { font-family: 'DM Mono', monospace; font-size: 11px; color: var(--orange); background: rgba(255,165,2,0.08);
        border: 1px solid rgba(255,165,2,0.2); padding: 8px 16px; border-radius: 8px; text-align: center; }
    .locked-badge { font-family: 'DM Mono', monospace; font-size: 11px; color: var(--green); background: rgba(46,213,115,0.08);
        border: 1px solid rgba(46,213,115,0.2); padding: 8px 16px; border-radius: 8px; text-align: center; }
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

def resolve_decision(company, decision, player_seed):
    """Returns (outcome, capital_delta) for an approve/reject decision. Deterministic per player+round via seed."""
    if decision == 'reject':
        return 'rejected', 0
    rng = random.Random(player_seed)
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
    defaulted = rng.random() < min(threshold, 0.95)
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
        <div class="hsbc-mark">HSBC</div><div class="brand-name">BEAT THE <span>RISK</span></div>
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
now = time.time()
if st.session_state.remote_state is None or now - st.session_state.last_fetch > 2:
    fetched = remote_read()
    if fetched is not None:
        st.session_state.remote_state = fetched if fetched else default_game_state()
        st.session_state.last_fetch = now
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
        <div class="hsbc-mark">HSBC</div><div class="brand-name">BEAT THE <span>RISK</span></div>
    </div><span class="round-pill">MULTIPLAYER LOBBY</span></div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='panel' style='max-width:420px;margin:3rem auto;text-align:center;'>", unsafe_allow_html=True)
    st.markdown("<div class='panel-title'>Oyuna Katıl</div>", unsafe_allow_html=True)
    name_input = st.text_input("Adınızı girin", placeholder="örn. Ahmet K.", label_visibility="collapsed")
    join = st.button("OYUNA KATIL →", type="primary", use_container_width=True)
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
        <div class="brand-name">BEAT THE <span>RISK</span></div>
    </div>
    <div style="display:flex;align-items:center;gap:1rem;">
        <span class="round-pill"><span class="live-dot"></span>ROUND {round_display} / {MAX_ROUNDS}</span>
        <span style="font-family:'DM Mono',monospace;font-size:11px;color:var(--muted);">{player_name} {'★ HOST' if is_host else ''}</span>
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
            tag = " ★ HOST" if p == game["host"] else ""
            st.markdown(f"<div style='font-family:DM Mono,monospace;padding:6px 0;color:var(--text);'>● {p}{tag}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("<div class='panel-title'>Host Kontrolü</div>", unsafe_allow_html=True)
        if is_host:
            if st.button("🚀 OYUNU BAŞLAT", type="primary", use_container_width=True):
                game["round"] = 1
                game["company_seed"] = random.randint(1, 10**9)
                game["company"] = generate_company(game["company_seed"])
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
            <div class="panel-title">{SECTORS[company['sector']]['icon']} Kredi Başvurusu — {company['sector']} ({company['size']} Cap)</div>
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
            <div style="margin-top:1.2rem;">
                <div style="display:flex;justify-content:space-between;"><span class="cell-label">TEMERRÜT OLASILIĞI (PD)</span>
                <span style="font-family:'Syne',sans-serif;font-weight:800;color:{pd_color};">{pd_val*100:.2f}%</span></div>
                <div class="pd-track"><div class="pd-fill" style="width:{pd_fill}%;background:{pd_color};"></div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if game["locked"]:
            st.markdown("<div class='locked-badge'>🔒 Bu round kilitlendi. Sonuçlar host tarafından açıklanacak.</div>", unsafe_allow_html=True)
        elif already_decided:
            decision_made = me["decisions"][str(rnd)]
            st.markdown(f"<div class='locked-badge'>✓ Kararınız kaydedildi: <b>{decision_made.upper()}</b>. Diğer oyuncular bekleniyor...</div>", unsafe_allow_html=True)
        else:
            b1, b2 = st.columns(2)
            with b1:
                approve_clicked = st.button("✓ ONAYLA", type="primary", use_container_width=True, key=f"app_{rnd}")
            with b2:
                reject_clicked = st.button("✗ REDDET", type="secondary", use_container_width=True, key=f"rej_{rnd}")

            if approve_clicked or reject_clicked:
                decision = "approve" if approve_clicked else "reject"
                # re-fetch latest before writing to minimize race conditions
                latest = remote_read() or game
                latest_me = latest["players"].setdefault(player_name, {"capital": INITIAL_CAPITAL, "portfolio": [], "decisions": {}})
                if str(rnd) not in latest_me["decisions"]:
                    player_seed = hash((player_name, rnd, latest.get("company_seed"))) % (2**31)
                    outcome, delta = resolve_decision(company, decision, player_seed)
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
        st.markdown("<div class='panel-title'>🏆 Canlı Sıralama</div>", unsafe_allow_html=True)
        ranked = sorted(game["players"].items(), key=lambda kv: kv[1]["capital"], reverse=True)
        for i, (pname, pdata) in enumerate(ranked, 1):
            delta = pdata["capital"] - INITIAL_CAPITAL
            cap_cls = "pos" if delta >= 0 else "neg"
            decided = str(rnd) in pdata["decisions"]
            status_html = "<span class='lb-status lb-done'>HAZIR</span>" if decided else "<span class='lb-status lb-waiting'>BEKLİYOR</span>"
            row_cls = "leaderboard-row me" if pname == player_name else "leaderboard-row"
            st.markdown(f"""
            <div class="{row_cls}">
                <span class="lb-rank">#{i}</span>
                <span class="lb-name">{pname}</span>
                <span class="lb-cap {cap_cls}">${pdata['capital']:,.0f}</span>
                {status_html}
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        if is_host:
            st.markdown("<br><div class='panel'>", unsafe_allow_html=True)
            st.markdown("<div class='panel-title'>Host Kontrolü</div>", unsafe_allow_html=True)
            n_decided = sum(1 for p in game["players"].values() if str(rnd) in p["decisions"])
            n_total = len(game["players"])
            st.markdown(f"<div style='font-family:DM Mono,monospace;font-size:12px;color:var(--muted);margin-bottom:0.8rem;'>{n_decided}/{n_total} oyuncu karar verdi</div>", unsafe_allow_html=True)
            next_label = "SONRAKI ROUND →" if rnd < MAX_ROUNDS else "OYUNU BİTİR 🏁"
            if st.button(next_label, type="primary", use_container_width=True):
                if rnd < MAX_ROUNDS:
                    game["round"] += 1
                    game["company_seed"] = random.randint(1, 10**9)
                    game["company"] = generate_company(game["company_seed"])
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
    st.markdown("<div style='text-align:center;padding:2rem 0;'>", unsafe_allow_html=True)
    st.markdown("<div class='panel-title'>FİNAL SONUÇLAR</div>", unsafe_allow_html=True)
    st.markdown("<h1 style='font-family:Syne;color:var(--text);'>GAME <span style='color:var(--accent);'>OVER</span></h1>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    ranked = sorted(game["players"].items(), key=lambda kv: kv[1]["capital"], reverse=True)
    st.markdown("<div class='panel' style='max-width:700px;margin:0 auto;'>", unsafe_allow_html=True)
    for i, (pname, pdata) in enumerate(ranked, 1):
        delta = pdata["capital"] - INITIAL_CAPITAL
        delta_pct = delta / INITIAL_CAPITAL * 100
        cap_cls = "pos" if delta >= 0 else "neg"
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"#{i}"
        row_cls = "leaderboard-row me" if pname == player_name else "leaderboard-row"
        st.markdown(f"""
        <div class="{row_cls}" style="grid-template-columns: 40px 1fr 140px 90px;">
            <span class="lb-rank">{medal}</span>
            <span class="lb-name">{pname}</span>
            <span class="lb-cap {cap_cls}">${pdata['capital']:,.0f}</span>
            <span class="lb-cap {cap_cls}">{delta_pct:+.1f}%</span>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if is_host:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("↺ YENİ OYUN BAŞLAT", type="primary", use_container_width=True):
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
st.markdown("<div style='text-align:center;padding:1rem 0;font-family:DM Mono,monospace;font-size:9px;color:var(--muted);'>otomatik yenileniyor...</div>", unsafe_allow_html=True)
time.sleep(2.5)
st.rerun()
