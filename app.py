import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pytz

# ── Konfiguration ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Elpris SE3",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ZONE = "SE3"
TZ   = pytz.timezone("Europe/Stockholm")

# ── Tema (ljust/mörkt) ────────────────────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

dark = st.session_state.dark_mode

if dark:
    BG          = "#0f1117"
    CARD_BG     = "#1a1d27"
    CARD_BORDER = "#2a2d3e"
    TEXT_PRI    = "#f0f2ff"
    TEXT_SEC    = "#8b8fa8"
    PLOT_BG     = "rgba(0,0,0,0)"
    GRID_COLOR  = "rgba(255,255,255,0.05)"
    AVG_COLOR   = "rgba(255,255,255,0.3)"
else:
    BG          = "#f0f4ff"
    CARD_BG     = "#ffffff"
    CARD_BORDER = "#dde3f5"
    TEXT_PRI    = "#0f1117"
    TEXT_SEC    = "#5a6080"
    PLOT_BG     = "rgba(0,0,0,0)"
    GRID_COLOR  = "rgba(0,0,0,0.05)"
    AVG_COLOR   = "rgba(0,0,0,0.3)"

BLUE    = "#4c7aff"
GREEN   = "#22c97a"
RED     = "#ff5757"
YELLOW  = "#ffc947"
TEAL    = "#00d4c8"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {{
    font-family: 'DM Sans', sans-serif;
    background-color: {BG} !important;
    color: {TEXT_PRI} !important;
}}
.stApp {{ background-color: {BG} !important; }}
.block-container {{ padding: 1.5rem 2rem 2rem 2rem !important; max-width: 1400px; }}

#MainMenu, footer, header {{ visibility: hidden; }}
.stDeployButton {{ display: none; }}

.card {{
    background: {CARD_BG};
    border: 1px solid {CARD_BORDER};
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
}}
.card-sm {{
    background: {CARD_BG};
    border: 1px solid {CARD_BORDER};
    border-radius: 14px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 1rem;
    height: 100%;
}}
.kpi-value {{
    font-size: 2.2rem;
    font-weight: 600;
    font-family: 'DM Mono', monospace;
    line-height: 1.1;
    color: {TEXT_PRI};
}}
.kpi-label {{
    font-size: 0.75rem;
    font-weight: 500;
    color: {TEXT_SEC};
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.3rem;
}}
.kpi-sub {{
    font-size: 0.78rem;
    color: {TEXT_SEC};
    margin-top: 0.25rem;
}}
.rec-badge {{
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    margin-bottom: 0.5rem;
}}
.rec-good  {{ background: rgba(34,201,122,0.15); color: {GREEN}; border: 1px solid rgba(34,201,122,0.3); }}
.rec-warn  {{ background: rgba(255,201,71,0.15);  color: {YELLOW}; border: 1px solid rgba(255,201,71,0.3); }}
.rec-bad   {{ background: rgba(255,87,87,0.15);   color: {RED};    border: 1px solid rgba(255,87,87,0.3); }}
.alert-high {{
    background: rgba(255,87,87,0.1);
    border: 1px solid rgba(255,87,87,0.3);
    border-left: 4px solid {RED};
    border-radius: 10px;
    padding: 0.8rem 1rem;
    margin-bottom: 1rem;
    color: {TEXT_PRI};
}}
.alert-low {{
    background: rgba(34,201,122,0.1);
    border: 1px solid rgba(34,201,122,0.3);
    border-left: 4px solid {GREEN};
    border-radius: 10px;
    padding: 0.8rem 1rem;
    margin-bottom: 1rem;
    color: {TEXT_PRI};
}}
.dash-title {{
    font-size: 1.5rem;
    font-weight: 600;
    color: {TEXT_PRI};
    margin: 0;
}}
.dash-sub {{
    font-size: 0.82rem;
    color: {TEXT_SEC};
    margin-top: 0.2rem;
}}
.section-title {{
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: {TEXT_SEC};
    margin-bottom: 0.8rem;
}}
.rec-time {{
    font-family: 'DM Mono', monospace;
    font-size: 1.6rem;
    font-weight: 500;
    color: {GREEN};
}}
.rec-cost {{
    font-size: 0.82rem;
    color: {TEXT_SEC};
    margin-top: 0.15rem;
}}
.divider {{ border: none; border-top: 1px solid {CARD_BORDER}; margin: 0.8rem 0; }}
.color-dot {{
    display: inline-block;
    width: 9px; height: 9px;
    border-radius: 50%;
    margin-right: 5px;
    vertical-align: middle;
}}
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=900)
def fetch_prices(date_str: str) -> list:
    url = f"https://www.elprisetjustnu.se/api/v1/prices/{date_str}_{ZONE}.json"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()


def load_data() -> pd.DataFrame:
    now      = datetime.now(TZ)
    tomorrow = now + timedelta(days=1)
    rows     = fetch_prices(now.strftime("%Y/%m-%d"))
    try:
        rows += fetch_prices(tomorrow.strftime("%Y/%m-%d"))
    except Exception:
        pass
    df = pd.DataFrame(rows)
    df["time_start"] = pd.to_datetime(df["time_start"], utc=True).dt.tz_convert(TZ)
    df["ore"]        = (df["SEK_per_kWh"] * 100).round(1)
    return df.sort_values("time_start").reset_index(drop=True)


def find_best_window(df: pd.DataFrame, duration_h: float, from_now_h: float) -> dict | None:
    now    = datetime.now(TZ)
    cutoff = now + timedelta(hours=from_now_h)
    future = df[df["time_start"] >= now].copy()
    future = future[future["time_start"] < cutoff].reset_index(drop=True)
    slots_needed = max(1, int(duration_h))
    if len(future) < slots_needed:
        return None
    best_avg   = float("inf")
    best_start = None
    best_end   = None
    best_cost  = 0.0
    for i in range(len(future) - slots_needed + 1):
        window = future.iloc[i : i + slots_needed]
        avg    = window["ore"].mean()
        if avg < best_avg:
            best_avg   = avg
            best_start = window.iloc[0]["time_start"]
            best_end   = window.iloc[-1]["time_start"] + timedelta(hours=1)
            best_cost  = avg
    return {"start": best_start, "end": best_end, "avg_ore": best_cost}


def price_level(ore: float, p25: float, p75: float) -> str:
    if ore <= p25:
        return "low"
    if ore >= p75:
        return "high"
    return "normal"


def build_chart(df: pd.DataFrame, hours: int, highlight_windows: list = None) -> go.Figure:
    now    = datetime.now(TZ)
    cutoff = now + timedelta(hours=hours)
    sub    = df[(df["time_start"] >= now - timedelta(minutes=30)) &
                (df["time_start"] < cutoff)].copy()
    if sub.empty:
        return None
    avg = sub["ore"].mean()
    colors = []
    for _, row in sub.iterrows():
        t = row["time_start"]
        if now - timedelta(minutes=30) <= t < now + timedelta(hours=1):
            colors.append(YELLOW)
        elif row["ore"] == sub["ore"].min():
            colors.append(GREEN)
        elif row["ore"] == sub["ore"].max():
            colors.append(RED)
        else:
            colors.append(BLUE)
    hover = [
        f"<b>{r['time_start'].strftime('%H:%M')} - {(r['time_start']+timedelta(hours=1)).strftime('%H:%M')}</b>"
        f"<br>{r['ore']:.1f} öre/kWh"
        for _, r in sub.iterrows()
    ]
    fig = go.Figure()
    if highlight_windows:
        for hw in highlight_windows:
            if hw:
                fig.add_vrect(
                    x0=hw["start"], x1=hw["end"],
                    fillcolor="rgba(34,201,122,0.10)",
                    layer="below", line_width=0,
                )
                fig.add_vline(
                    x=hw["start"], line_dash="dot",
                    line_color=GREEN, line_width=1.5,
                )
    fig.add_trace(go.Bar(
        x=sub["time_start"],
        y=sub["ore"],
        marker_color=colors,
        marker_line_width=0,
        hovertext=hover,
        hoverinfo="text",
    ))
    fig.add_hline(
        y=avg,
        line_dash="dot",
        line_color=AVG_COLOR,
        line_width=1.5,
        annotation_text=f"Snitt {avg:.0f} ore",
        annotation_position="top right",
        annotation_font_color=TEXT_SEC,
        annotation_font_size=11,
    )
    fig.update_layout(
        plot_bgcolor=PLOT_BG,
        paper_bgcolor=PLOT_BG,
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(showgrid=False, tickformat="%H:%M", tickfont=dict(size=11, color=TEXT_SEC)),
        yaxis=dict(showgrid=True, gridcolor=GRID_COLOR, ticksuffix=" ore", tickfont=dict(size=11, color=TEXT_SEC), zeroline=False),
        bargap=0.2,
        height=260,
        hoverlabel=dict(bgcolor=CARD_BG, font_size=12, font_color=TEXT_PRI, bordercolor=CARD_BORDER),
        showlegend=False,
    )
    return fig


def rec_badge(level: str) -> str:
    if level == "low":
        return '<span class="rec-badge rec-good">Bra tid</span>'
    if level == "high":
        return '<span class="rec-badge rec-bad">Dyrt</span>'
    return '<span class="rec-badge rec-warn">Normal</span>'


try:
    df = load_data()
except Exception as e:
    st.error(f"Kunde inte hamta elprisdata: {e}")
    st.stop()

now         = datetime.now(TZ)
today_df    = df[df["time_start"].dt.date == now.date()]
current_row = df[df["time_start"] <= now].iloc[-1] if not df[df["time_start"] <= now].empty else None
cur_ore     = current_row["ore"] if current_row is not None else 0.0
all_p25     = today_df["ore"].quantile(0.25) if not today_df.empty else 0
all_p75     = today_df["ore"].quantile(0.75) if not today_df.empty else 100

col_title, col_toggle = st.columns([6, 1])
with col_title:
    st.markdown(f'<p class="dash-title">Elpris Stockholm SE3</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="dash-sub">Uppdateras var 15 min · {now.strftime("%A %d %B %Y, %H:%M")}</p>', unsafe_allow_html=True)
with col_toggle:
    if st.button("Morkt" if not dark else "Ljust", use_container_width=True):
        st.session_state.dark_mode = not dark
        st.rerun()

if current_row is not None:
    lvl = price_level(cur_ore, all_p25, all_p75)
    if lvl == "high":
        st.markdown(f'<div class="alert-high">Högt elpris just nu - {cur_ore:.1f} öre/kWh. Skjut upp energikravande maskiner om möjligt.</div>', unsafe_allow_html=True)
    elif lvl == "low":
        st.markdown(f'<div class="alert-low">Lågt elpris just nu - {cur_ore:.1f} öre/kWh. Bra tillfälle att köra maskiner!</div>', unsafe_allow_html=True)

k1, k2, k3, k4, k5 = st.columns(5)

def kpi_card(label, value, sub="", color=None):
    val_color = color if color else TEXT_PRI
    return f"""
    <div class="card-sm">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value" style="color:{val_color}">{value}</div>
      <div class="kpi-sub">{sub}</div>
    </div>"""

with k1:
    color = GREEN if price_level(cur_ore, all_p25, all_p75) == "low" else (RED if price_level(cur_ore, all_p25, all_p75) == "high" else TEXT_PRI)
    st.markdown(kpi_card("Pris just nu", f"{cur_ore:.1f}", "öre/kWh", color=color), unsafe_allow_html=True)
with k2:
    if not today_df.empty:
        mn = today_df["ore"].min()
        mt = today_df.loc[today_df["ore"].idxmin(), "time_start"].strftime("%H:%M")
        st.markdown(kpi_card("Lägst idag", f"{mn:.1f}", f"öre · kl {mt}", color=GREEN), unsafe_allow_html=True)
with k3:
    if not today_df.empty:
        mx = today_df["ore"].max()
        mxt = today_df.loc[today_df["ore"].idxmax(), "time_start"].strftime("%H:%M")
        st.markdown(kpi_card("Högst idag", f"{mx:.1f}", f"öre · kl {mxt}", color=RED), unsafe_allow_html=True)
with k4:
    if not today_df.empty:
        st.markdown(kpi_card("Snitt idag", f"{today_df['ore'].mean():.1f}", "öre/kWh"), unsafe_allow_html=True)
with k5:
    tomorrow_df = df[df["time_start"].dt.date == (now + timedelta(days=1)).date()]
    if not tomorrow_df.empty:
        st.markdown(kpi_card("Snitt imorgon", f"{tomorrow_df['ore'].mean():.1f}", "öre/kWh"), unsafe_allow_html=True)
    else:
        st.markdown(kpi_card("Imorgon", "-", "Ej tillgangligt"), unsafe_allow_html=True)

st.markdown('<div class="section-title" style="margin-top:0.5rem">Rekommendationer</div>', unsafe_allow_html=True)

DISK_H = 3.5
disk_start_from = now.replace(hour=18, minute=0, second=0, microsecond=0)
if now > disk_start_from:
    disk_start_from = disk_start_from
hours_until_disk = max(0, (disk_start_from - now).total_seconds() / 3600)

disk_future  = df[df["time_start"] >= disk_start_from].copy()
disk_best_12 = find_best_window(disk_future, DISK_H, from_now_h=hours_until_disk + 12)
disk_best_24 = find_best_window(disk_future, DISK_H, from_now_h=hours_until_disk + 24)
tvatt_best_12 = find_best_window(df, 1.0, from_now_h=12)
tvatt_best_24 = find_best_window(df, 1.0, from_now_h=24)

rc1, rc2 = st.columns(2)

with rc1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="kpi-label">Diskmaskin - 3,5 h · klar från kl 18</div>', unsafe_allow_html=True)
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    dc1, dc2 = st.columns(2)
    with dc1:
        st.markdown('<div class="section-title">Bästa tid · 12h</div>', unsafe_allow_html=True)
        if disk_best_12:
            st.markdown(rec_badge(price_level(disk_best_12["avg_ore"], all_p25, all_p75)), unsafe_allow_html=True)
            st.markdown(f'<div class="rec-time">kl {disk_best_12["start"].strftime("%H:%M")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="rec-cost">Klar ~{disk_best_12["end"].strftime("%H:%M")} · {disk_best_12["avg_ore"]:.1f} öre/kWh</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="color:{TEXT_SEC}">Ingen data</div>', unsafe_allow_html=True)
    with dc2:
        st.markdown('<div class="section-title">Bästa tid · 24h</div>', unsafe_allow_html=True)
        if disk_best_24:
            st.markdown(rec_badge(price_level(disk_best_24["avg_ore"], all_p25, all_p75)), unsafe_allow_html=True)
            st.markdown(f'<div class="rec-time">kl {disk_best_24["start"].strftime("%H:%M")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="rec-cost">Klar ~{disk_best_24["end"].strftime("%H:%M")} · {disk_best_24["avg_ore"]:.1f} öre/kWh</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="color:{TEXT_SEC}">Ingen data</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with rc2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="kpi-label">Tvattmaskin - 1 h</div>', unsafe_allow_html=True)
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    tc1, tc2 = st.columns(2)
    with tc1:
        st.markdown('<div class="section-title">Bästa tid · 12h</div>', unsafe_allow_html=True)
        if tvatt_best_12:
            st.markdown(rec_badge(price_level(tvatt_best_12["avg_ore"], all_p25, all_p75)), unsafe_allow_html=True)
            st.markdown(f'<div class="rec-time">kl {tvatt_best_12["start"].strftime("%H:%M")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="rec-cost">Klar ~{tvatt_best_12["end"].strftime("%H:%M")} · {tvatt_best_12["avg_ore"]:.1f} öre/kWh</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="color:{TEXT_SEC}">Ingen data</div>', unsafe_allow_html=True)
    with tc2:
        st.markdown('<div class="section-title">Bästa tid · 24h</div>', unsafe_allow_html=True)
        if tvatt_best_24:
            st.markdown(rec_badge(price_level(tvatt_best_24["avg_ore"], all_p25, all_p75)), unsafe_allow_html=True)
            st.markdown(f'<div class="rec-time">kl {tvatt_best_24["start"].strftime("%H:%M")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="rec-cost">Klar ~{tvatt_best_24["end"].strftime("%H:%M")} · {tvatt_best_24["avg_ore"]:.1f} öre/kWh</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="color:{TEXT_SEC}">Ingen data</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

g1, g2 = st.columns(2)

all_windows_12 = [w for w in [disk_best_12, tvatt_best_12] if w]
all_windows_24 = [w for w in [disk_best_24, tvatt_best_24] if w]

with g1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Kommande 12 timmar</div>', unsafe_allow_html=True)
    fig12 = build_chart(df, 12, highlight_windows=all_windows_12)
    if fig12:
        st.plotly_chart(fig12, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

with g2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Kommande 24 timmar</div>', unsafe_allow_html=True)
    fig24 = build_chart(df, 24, highlight_windows=all_windows_24)
    if fig24:
        st.plotly_chart(fig24, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown(f"""
<div style="font-size:0.75rem;color:{TEXT_SEC};margin-top:-0.5rem;margin-bottom:1rem">
  <span class="color-dot" style="background:{YELLOW}"></span>Nuvarande timme &nbsp;·&nbsp;
  <span class="color-dot" style="background:{GREEN}"></span>Billigast &nbsp;·&nbsp;
  <span class="color-dot" style="background:{RED}"></span>Dyrast &nbsp;·&nbsp;
  <span class="color-dot" style="background:{BLUE}"></span>Övriga
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-title" style="margin-top:0.5rem">Kostnadskalkylator</div>', unsafe_allow_html=True)
st.markdown('<div class="card">', unsafe_allow_html=True)

calc_col1, calc_col2, calc_col3 = st.columns([2, 2, 3])

with calc_col1:
    watt     = st.slider("Effekt (watt)", min_value=500, max_value=3000, value=1200, step=100)
    duration = st.slider("Körtid (timmar)", min_value=0.5, max_value=4.0, value=1.0, step=0.5)

with calc_col2:
    moms         = st.checkbox("Inkludera moms (25%)", value=True)
    nattavgift   = st.number_input("Nätavgift öre/kWh", min_value=0, max_value=100, value=35)
    skatt        = st.checkbox("Skattereduktion (6 öre/kWh)", value=True)

with calc_col3:
    if current_row is not None:
        ore_total = cur_ore + nattavgift
        if moms:
            ore_total *= 1.25
        if skatt:
            ore_total = max(0, ore_total - 6)
        kwh_used   = (watt / 1000) * duration
        total_kr   = (ore_total / 100) * kwh_used
        total_month = total_kr * 30
        st.markdown(f"""
        <div style="padding: 0.8rem 0">
          <div class="kpi-label">Förbrukning</div>
          <div class="kpi-value" style="font-size:1.4rem">{kwh_used:.2f} kWh</div>
          <div style="height:0.8rem"></div>
          <div class="kpi-label">Kostnad per körning (nu)</div>
          <div class="kpi-value" style="font-size:1.8rem;color:{GREEN}">{total_kr:.2f} kr</div>
          <div class="kpi-sub">Totalpris: {ore_total:.1f} öre/kWh</div>
          <div style="height:0.4rem"></div>
          <div class="kpi-sub">Daglig körning: ca {total_month:.1f} kr/månad</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown(f'<div style="text-align:center;font-size:0.72rem;color:{TEXT_SEC};margin-top:1rem">Data från elprisetjustnu.se · SE3 Stockholm</div>', unsafe_allow_html=True)