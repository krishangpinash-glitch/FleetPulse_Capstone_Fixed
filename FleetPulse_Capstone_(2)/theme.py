"""Look and feel for FleetPulse: animated CSS, KPI cards, service cards, gauge, chart styling."""
import math

import plotly.graph_objects as go
import streamlit as st

TEAL = "#2dd4bf"
COLORWAY = [TEAL, "#60a5fa", "#a78bfa", "#fbbf24", "#f472b6", "#34d399"]

CSS = """
<style>
@property --num { syntax: '<integer>'; initial-value: 0; inherits: false; }
.stApp { background: radial-gradient(1200px 600px at 10% -10%, #12305a 0%, transparent 60%),
         radial-gradient(900px 500px at 100% 0%, #0f3d44 0%, transparent 55%), #0b1220; }
.block-container { animation: fadeUp .6s ease both; padding-top: 2rem; }
[data-testid="stSidebar"] { background: rgba(17,28,51,.75); backdrop-filter: blur(10px); border-right: 1px solid rgba(45,212,191,.15); }
@keyframes fadeUp { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: none; } }
@keyframes shift { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
@keyframes float { 0%,100% { transform: translateY(0) rotate(-3deg); } 50% { transform: translateY(-10px) rotate(3deg); } }
@keyframes shine { from { transform: translateX(-120%); } to { transform: translateX(220%); } }
@keyframes count { from { --num: 0; } to { --num: var(--n); } }
@keyframes fill { from { width: 0; } }
@keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(248,113,113,.6); } 70% { box-shadow: 0 0 0 12px rgba(248,113,113,0); } 100% { box-shadow: 0 0 0 0 rgba(248,113,113,0); } }
.hero { position: relative; overflow: hidden; padding: 28px 32px; margin-bottom: 22px; border-radius: 20px;
  background: linear-gradient(120deg, #0f766e, #1d4ed8, #7c3aed, #0f766e); background-size: 300% 300%;
  animation: shift 10s ease infinite; box-shadow: 0 10px 40px rgba(45,212,191,.18); }
.hero::after { content: ''; position: absolute; top: 0; left: 0; width: 35%; height: 100%;
  background: linear-gradient(100deg, transparent, rgba(255,255,255,.18), transparent); animation: shine 4.5s ease-in-out infinite; }
.hero h1 { margin: 0; font-size: 2.2rem; color: #fff; }
.hero p { margin: 6px 0 0; color: rgba(255,255,255,.85); }
.hero .truck { position: absolute; right: 30px; top: 14px; font-size: 3.4rem; animation: float 3.5s ease-in-out infinite; }
.kpi { padding: 18px 20px; margin-bottom: 14px; border-radius: 16px; background: rgba(255,255,255,.04);
  border: 1px solid rgba(255,255,255,.08); backdrop-filter: blur(8px); animation: fadeUp .7s ease both;
  transition: transform .25s ease, box-shadow .25s ease, border-color .25s ease; }
.kpi:hover { transform: translateY(-6px) scale(1.02); border-color: rgba(45,212,191,.6); box-shadow: 0 12px 30px rgba(45,212,191,.2); }
.kpi .lbl { font-size: .8rem; letter-spacing: .08em; text-transform: uppercase; color: #94a3b8; }
.kpi .val { font-size: 2rem; font-weight: 700; color: #f8fafc; margin-top: 4px; }
.kpi.bad .val { color: #f87171; } .kpi.ok .val { color: #2dd4bf; }
.count { animation: count 1.4s ease-out forwards; counter-reset: num var(--num); }
.count::after { content: counter(num); }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 14px; margin-bottom: 18px; }
.vcard { padding: 16px; border-radius: 16px; background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.08);
  animation: fadeUp .6s ease both; transition: transform .25s, box-shadow .25s; }
.vcard:hover { transform: translateY(-5px) rotate(-.4deg); box-shadow: 0 12px 28px rgba(0,0,0,.4); }
.vtop { display: flex; justify-content: space-between; align-items: center; }
.vtype { color: #94a3b8; font-size: .85rem; margin: 2px 0 10px; }
.pill { font-size: .72rem; padding: 3px 10px; border-radius: 999px; font-weight: 600; }
.pill.ok { background: rgba(45,212,191,.18); color: #2dd4bf; } .pill.warn { background: rgba(251,191,36,.18); color: #fbbf24; }
.pill.bad { background: rgba(248,113,113,.2); color: #f87171; animation: pulse 1.8s infinite; } .pill.na { background: rgba(148,163,184,.2); color: #cbd5e1; }
.bar { height: 9px; border-radius: 9px; background: rgba(255,255,255,.08); overflow: hidden; }
.bar i { display: block; height: 100%; border-radius: 9px; animation: fill 1.4s ease-out both; }
.ok .bar i { background: linear-gradient(90deg, #14b8a6, #2dd4bf); } .warn .bar i { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.bad .bar i { background: linear-gradient(90deg, #ef4444, #f87171); } .na .bar i { background: #64748b; }
.vdetail { margin-top: 8px; font-size: .82rem; color: #cbd5e1; }
.stButton > button, .stDownloadButton > button { border-radius: 12px; transition: transform .2s, box-shadow .2s; }
.stButton > button:hover, .stDownloadButton > button:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(45,212,191,.3); }
</style>
"""


def inject():
    st.markdown("\n".join(l for l in CSS.splitlines() if l.strip()), unsafe_allow_html=True)


def hero(title, sub="Fuel efficiency, service health and cost per kilometre in one place"):
    st.markdown(f'<div class="hero"><span class="truck">🚛</span><h1>{title}</h1><p>{sub}</p></div>', unsafe_allow_html=True)


def kpi(label, value, prefix="", suffix="", decimals=0, icon="", tone="", delay=0.0):
    """Animated KPI card. Whole numbers count up from 0; text/decimals fade in; None shows 'Not available'."""
    if value is None:
        body = '<span style="font-size:1.1rem;color:#94a3b8">Not available</span>'
    elif isinstance(value, str):
        body = value
    elif decimals == 0:
        body = f'{prefix}<span class="count" style="--n:{int(value)}"></span>{suffix}'
    else:
        body = f"{prefix}{value:,.{decimals}f}{suffix}"
    st.markdown(f'<div class="kpi {tone}" style="animation-delay:{delay}s"><div class="lbl">{icon} {label}</div>'
                f'<div class="val">{body}</div></div>', unsafe_allow_html=True)


LABEL = {"Overdue": "🔴 Overdue", "Due soon": "🟠 Due soon", "Up to date": "🟢 Up to date", "Unknown": "⚪ Unknown"}
TONE = {"Overdue": "bad", "Due soon": "warn", "Up to date": "ok", "Unknown": "na"}


def service_cards(items):
    """items: list of (reg, type, status, percent_of_interval_used, detail_text)."""
    cards = "".join(
        f'<div class="vcard {TONE[s]}" style="animation-delay:{i * 0.08}s"><div class="vtop"><b>{reg}</b>'
        f'<span class="pill {TONE[s]}">{LABEL[s]}</span></div><div class="vtype">{vt}</div>'
        f'<div class="bar"><i style="width:{min(max(p, 0), 100):.0f}%"></i></div><div class="vdetail">{d}</div></div>'
        for i, (reg, vt, s, p, d) in enumerate(items))
    st.markdown(f'<div class="grid">{cards}</div>', unsafe_allow_html=True)


def style(fig, height=None):
    """Dark transparent look, smooth transitions, zoomable range slider on line charts."""
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      colorway=COLORWAY, font=dict(family="Segoe UI, Inter, sans-serif"),
                      margin=dict(l=10, r=10, t=50, b=10), transition=dict(duration=600, easing="cubic-in-out"))
    if height:
        fig.update_layout(height=height)
    if any(t.type == "scatter" for t in fig.data):
        fig.update_xaxes(rangeslider_visible=True)
        fig.update_layout(hovermode="x unified")
    return fig


def gauge(value):
    top = max(30, math.ceil(value / 10) * 10 + 10)
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=value, number={"suffix": " km/L", "valueformat": ".2f"},
        title={"text": "Fleet average mileage"},
        gauge={"axis": {"range": [0, top]}, "bar": {"color": TEAL}, "steps": [
            {"range": [0, top * .33], "color": "rgba(248,113,113,.25)"},
            {"range": [top * .33, top * .66], "color": "rgba(251,191,36,.25)"},
            {"range": [top * .66, top], "color": "rgba(45,212,191,.25)"}]}))
    return style(fig, 300)
