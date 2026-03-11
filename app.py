import streamlit as st
import requests
import json

# ── Config ───────────────────────────────────────────────────────────────────
AZURE_ENDPOINT = "https://juansesame.eastus.inference.ml.azure.com/score"
try:
    AZURE_KEY = st.secrets["AZURE_KEY"]
except Exception:
    AZURE_KEY = "dxPwTV0Q02oN11AxphklxrfJL3e5URYziPYUaV06u3BS2GHxgEeaJQQJ99CCAAAAAAAAAAAAINFRAZML2RvC"

st.set_page_config(page_title="Persona Simulator", page_icon="👤", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] { background-color: #080b12 !important; color: #d0ddd0; font-family: 'DM Sans', sans-serif; }

.app-header { text-align:center; padding:36px 0 20px; margin-bottom:8px; }
.app-pill { display:inline-block; font-family:'DM Mono',monospace; font-size:10px; letter-spacing:3px; color:#3a7a5a; border:1px solid #1a3a2a; padding:4px 14px; border-radius:20px; margin-bottom:14px; }
.app-title { font-family:'DM Serif Display',serif; font-size:38px; color:#e8eed8; line-height:1.1; margin-bottom:6px; }
.app-sub { font-size:13px; color:#3a5a4a; font-family:'DM Mono',monospace; letter-spacing:1px; }

.user-row { display:flex; justify-content:flex-end; margin:16px 0 4px; }
.persona-row { display:flex; justify-content:flex-start; margin:16px 0 4px; gap:10px; align-items:flex-start; }
.user-bubble { background:linear-gradient(135deg,#0f2040,#0a1830); border:1px solid #1e3a60; border-radius:20px 4px 20px 20px; padding:13px 18px; max-width:75%; color:#90b8e0; font-size:14.5px; line-height:1.65; }
.persona-bubble { background:linear-gradient(135deg,#0a1a10,#081410); border:1px solid #1a3020; border-radius:4px 20px 20px 20px; padding:13px 18px; max-width:100%; color:#c0d8c0; font-size:14.5px; line-height:1.65; }
.avatar { width:36px; height:36px; border-radius:50%; flex-shrink:0; background:linear-gradient(135deg,#0d2a1a,#0a1f30); border:1px solid #2a4a3a; display:flex; align-items:center; justify-content:center; font-size:12px; color:#5a9a7a; font-family:'DM Mono',monospace; }
.msg-label { font-family:'DM Mono',monospace; font-size:9px; color:#2a4a3a; letter-spacing:2.5px; margin-bottom:4px; }
.msg-label-right { font-family:'DM Mono',monospace; font-size:9px; color:#2a3a5a; letter-spacing:2.5px; margin-bottom:4px; text-align:right; }
.persona-tag { display:inline-block; font-family:'DM Mono',monospace; font-size:10px; color:#5a9a7a; background:#0d2a1a; border:1px solid #1a4a2a; border-radius:12px; padding:2px 10px; margin-bottom:8px; }

/* Evaluation panel */
.eval-panel { margin-top:14px; border-top:1px solid #1a2a1a; padding-top:12px; }
.eval-section { margin-bottom:12px; }
.eval-section-title { font-family:'DM Mono',monospace; font-size:9px; letter-spacing:2px; margin-bottom:8px; }
.eval-verdict-high { color:#00c896; }
.eval-verdict-med  { color:#f5a623; }
.eval-verdict-low  { color:#ff7a7a; }
.score-row { display:flex; align-items:center; gap:10px; margin-bottom:10px; }
.score-circle { width:48px; height:48px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-family:'DM Mono',monospace; font-size:13px; font-weight:500; flex-shrink:0; }
.score-high { background:#00c89615; border:1.5px solid #00c89650; color:#00c896; }
.score-med  { background:#f5a62315; border:1.5px solid #f5a62350; color:#f5a623; }
.score-low  { background:#ff5c5c15; border:1.5px solid #ff5c5c50; color:#ff7a7a; }
.verdict-text { font-family:'DM Mono',monospace; font-size:11px; }
.dim-bar-row { display:flex; align-items:center; gap:8px; margin-bottom:5px; }
.dim-label { font-size:10px; color:#4a7a5a; font-family:'DM Mono',monospace; width:180px; flex-shrink:0; }
.dim-bar-bg { flex:1; height:4px; background:#0d1a10; border-radius:2px; }
.dim-bar-fill { height:100%; border-radius:2px; }
.dim-val { font-size:10px; font-family:'DM Mono',monospace; color:#3a6a4a; width:30px; text-align:right; }
.bullets { margin:6px 0 0 0; padding:0; list-style:none; }
.bullet-item { font-size:12px; color:#5a7a6a; padding:3px 0; padding-left:14px; position:relative; line-height:1.5; }
.bullet-item::before { content:"·"; position:absolute; left:0; color:#3a6a4a; }
.bullet-neg { color:#7a5a4a; }
.bullet-neg::before { color:#7a4a3a; }
.eval-note { font-size:12px; color:#4a6a5a; line-height:1.6; margin-top:6px; font-style:italic; }
.rec-badge { display:inline-block; font-family:'DM Mono',monospace; font-size:10px; padding:3px 12px; border-radius:12px; margin-top:6px; }
.rec-use { background:#00c89615; border:1px solid #00c89640; color:#00c896; }
.rec-caution { background:#f5a62315; border:1px solid #f5a62340; color:#f5a623; }
.rec-avoid { background:#ff5c5c15; border:1px solid #ff5c5c40; color:#ff7a7a; }
.human-truth { background:#0a1a14; border-left:2px solid #1a4a2a; padding:8px 12px; border-radius:0 8px 8px 0; font-size:12px; color:#5a8a6a; line-height:1.6; margin-top:6px; }
.risk-badge { display:inline-block; font-family:'DM Mono',monospace; font-size:10px; padding:2px 10px; border-radius:10px; margin-top:4px; }
.risk-low  { background:#00c89615; border:1px solid #00c89640; color:#00c896; }
.risk-med  { background:#f5a62315; border:1px solid #f5a62340; color:#f5a623; }
.risk-high { background:#ff5c5c15; border:1px solid #ff5c5c40; color:#ff7a7a; }

.chat-divider { border:none; border-top:1px solid #111820; margin:24px 0; }
.stTextInput > div > div > input { background:#0d1520 !important; border:1px solid #1e2d40 !important; border-radius:14px !important; color:#c0d0e0 !important; font-size:14px !important; font-family:'DM Sans',sans-serif !important; padding:14px 18px !important; }
.stTextInput > div > div > input:focus { border-color:#2a5a4a !important; box-shadow:none !important; }
.stTextInput > div > div > input::placeholder { color:#2a4a3a !important; }
.stButton > button { background:linear-gradient(135deg,#1a4a3a,#0d3020) !important; border:1px solid #2a5a4a !important; border-radius:14px !important; color:#6ecf9a !important; font-family:'DM Mono',monospace !important; font-size:13px !important; padding:12px 20px !important; width:100% !important; }
.stButton > button:hover { background:linear-gradient(135deg,#225a4a,#1a4030) !important; border-color:#3a7a5a !important; }
.sugg-title { font-family:'DM Mono',monospace; font-size:9px; color:#1a3a2a; letter-spacing:3px; text-align:center; margin:32px 0 14px; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Azure call ────────────────────────────────────────────────────────────────
def call_azure(question):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {AZURE_KEY}"}
    r = requests.post(AZURE_ENDPOINT, headers=headers, json={"Question": question}, timeout=30)
    if r.status_code == 200:
        result = r.json()
        answer_dict  = json.loads(result["Answer"])
        evaluator    = json.loads(result["Evaluator"]) if result.get("Evaluator") else None
        response_text = answer_dict["response"]
        persona_name  = answer_dict.get("persona", "")
        return response_text, persona_name, evaluator
    else:
        raise Exception(f"Error {r.status_code}: {r.text}")

# ── Score color helper ────────────────────────────────────────────────────────
def score_css(val):
    try:
        v = float(val)
        if v >= 0.8: return "score-high"
        if v >= 0.6: return "score-med"
        return "score-low"
    except: return "score-med"

def verdict_css(text):
    t = str(text).lower()
    if any(w in t for w in ["high","authentic","excellent"]): return "eval-verdict-high"
    if any(w in t for w in ["medium","moderate","partial"]): return "eval-verdict-med"
    return "eval-verdict-low"

def bar_color(val):
    try:
        v = float(val)
        if v >= 0.8: return "#00c896"
        if v >= 0.6: return "#f5a623"
        return "#ff7a7a"
    except: return "#3a6a4a"

def rec_css(text):
    t = str(text).lower()
    if "use" in t and "caution" not in t: return "rec-use"
    if "caution" in t: return "rec-caution"
    return "rec-avoid"

def risk_css(text):
    t = str(text).lower()
    if "low" in t: return "risk-low"
    if "high" in t: return "risk-high"
    return "risk-med"

# ── Evaluation renderer ───────────────────────────────────────────────────────
def render_evaluator(evaluator):
    if not evaluator:
        return ""

    html = '<div class="eval-panel">'

    # ── ALIGNMENT AUDIT ──
    align = evaluator.get("ALIGNMENT AUDIT", {})
    if align:
        conf   = align.get("Confidence Score", "")
        verdict = align.get("Verdict", "")
        dims   = align.get("Dimension Scores", {})
        strengths = align.get("Strengths", [])
        misaligns = align.get("Misalignments", [])
        note   = align.get("Audit Note", "")
        rec    = align.get("Recommendation", "")

        html += f'''
        <div class="eval-section">
            <div class="eval-section-title eval-verdict-high">▸ ALIGNMENT AUDIT</div>
            <div class="score-row">
                <div class="score-circle {score_css(conf)}">{conf}</div>
                <div>
                    <div class="verdict-text {verdict_css(verdict)}">{verdict}</div>
                    <div style="font-size:10px;color:#3a5a4a;font-family:'DM Mono',monospace;margin-top:2px;">Confidence Score</div>
                </div>
            </div>'''

        if dims:
            html += '<div style="margin:8px 0;">'
            for dim, val in dims.items():
                pct = int(float(val) * 100)
                html += f'''
                <div class="dim-bar-row">
                    <div class="dim-label">{dim}</div>
                    <div class="dim-bar-bg"><div class="dim-bar-fill" style="width:{pct}%;background:{bar_color(val)};"></div></div>
                    <div class="dim-val">{val}</div>
                </div>'''
            html += '</div>'

        if strengths:
            html += '<ul class="bullets">'
            for s in strengths:
                html += f'<li class="bullet-item">{s}</li>'
            html += '</ul>'

        if misaligns:
            html += '<ul class="bullets" style="margin-top:4px;">'
            for m in misaligns:
                html += f'<li class="bullet-item bullet-neg">{m}</li>'
            html += '</ul>'

        if note:
            html += f'<div class="eval-note">{note}</div>'

        if rec:
            html += f'<div class="rec-badge {rec_css(rec)}">⟶ {rec}</div>'

        html += '</div>'

    # ── INTEGRITY AUDIT ──
    integ = evaluator.get("INTEGRITY AUDIT", {})
    if integ:
        iscore  = integ.get("Integrity Score", "")
        iverdict = integ.get("Verdict", "")
        metrics  = integ.get("Metric Breakdown", {})
        red_flags = integ.get("Behavioral Red Flags", [])
        truth    = integ.get("Human Truth Synthesis", "")
        halluc   = integ.get("Risk of Hallucination", "")

        html += f'''
        <div class="eval-section" style="border-top:1px solid #0d1a10;padding-top:12px;">
            <div class="eval-section-title" style="color:#5a9a7a;">▸ INTEGRITY AUDIT</div>
            <div class="score-row">
                <div class="score-circle {score_css(iscore)}">{iscore}</div>
                <div>
                    <div class="verdict-text {verdict_css(iverdict)}">{iverdict}</div>
                    <div style="font-size:10px;color:#3a5a4a;font-family:'DM Mono',monospace;margin-top:2px;">Integrity Score</div>
                </div>
            </div>'''

        if metrics:
            html += '<div style="margin:8px 0;">'
            for m, val in metrics.items():
                pct = int(float(val) * 100)
                html += f'''
                <div class="dim-bar-row">
                    <div class="dim-label">{m}</div>
                    <div class="dim-bar-bg"><div class="dim-bar-fill" style="width:{pct}%;background:{bar_color(val)};"></div></div>
                    <div class="dim-val">{val}</div>
                </div>'''
            html += '</div>'

        if red_flags:
            html += '<ul class="bullets">'
            for f in red_flags:
                html += f'<li class="bullet-item bullet-neg">{f}</li>'
            html += '</ul>'

        if truth:
            html += f'<div class="human-truth">💡 {truth}</div>'

        if halluc:
            html += f'<div style="margin-top:8px;font-size:10px;color:#3a5a4a;font-family:DM Mono,monospace;">HALLUCINATION RISK &nbsp;<span class="risk-badge {risk_css(halluc)}">{halluc}</span></div>'

        html += '</div>'

    html += '</div>'
    return html

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <div class="app-pill">● BNPP · SYNTHETIC PERSONA ENGINE</div>
    <div class="app-title">Persona Simulator</div>
    <div class="app-sub">you are the bank &nbsp;·&nbsp; ask your customer anything</div>
</div>
""", unsafe_allow_html=True)

# ── Chat messages ─────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="user-row">
            <div>
                <div class="msg-label-right">YOU · BANK</div>
                <div class="user-bubble">{msg["content"]}</div>
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        persona_tag = f'<div class="persona-tag">{msg["persona"]}</div>' if msg.get("persona") else ""
        eval_html   = render_evaluator(msg.get("evaluator"))
        st.markdown(f"""
        <div class="persona-row">
            <div class="avatar">AI</div>
            <div style="flex:1;min-width:0;">
                <div class="msg-label">SYNTHETIC PERSONA</div>
                <div class="persona-bubble">
                    {persona_tag}
                    <div>{msg["content"]}</div>
                    {eval_html}
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

# ── Input ─────────────────────────────────────────────────────────────────────
st.markdown("<hr class='chat-divider'>", unsafe_allow_html=True)
col_in, col_btn = st.columns([5, 1])
with col_in:
    user_input = st.text_input("", placeholder="Ask the persona a marketing question…",
                               label_visibility="collapsed", key="chat_input")
with col_btn:
    send = st.button("Send ↑")

col_clear, _ = st.columns([1, 5])
with col_clear:
    if st.button("↺ Clear"):
        st.session_state.messages = []
        st.rerun()

# ── Send logic ────────────────────────────────────────────────────────────────
def do_send(question):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.spinner("Persona is thinking…"):
        try:
            answer, persona_name, evaluator = call_azure(question)
            st.session_state.messages.append({
                "role": "persona", "content": answer,
                "persona": persona_name, "evaluator": evaluator
            })
        except Exception as e:
            st.session_state.messages.append({
                "role": "persona", "content": f"⚠️ {e}",
                "persona": "", "evaluator": None
            })
    st.rerun()

if send and user_input.strip():
    do_send(user_input.strip())

# ── Suggested questions ───────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown('<div class="sugg-title">SUGGESTED QUESTIONS</div>', unsafe_allow_html=True)
    suggestions = [
        "How do you manage your savings?",
        "Would you switch banks for a better rate?",
        "What banking products interest you most?",
        "How do you feel about digital banking?",
        "Are you planning any major purchases?",
        "What matters most in a bank to you?",
    ]
    c1, c2 = st.columns(2)
    for i, q in enumerate(suggestions):
        with (c1 if i % 2 == 0 else c2):
            if st.button(q, key=f"s_{i}"):
                do_send(q)
