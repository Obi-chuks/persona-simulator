import streamlit as st
import requests
import json

# ── Config ───────────────────────────────────────────────────────────────────
AZURE_ENDPOINT = "https://juansesame.eastus.inference.ml.azure.com/score"
try:
    AZURE_KEY = st.secrets["AZURE_KEY"]
except Exception:
    AZURE_KEY = "dxPwTV0Q02oN11AxphklxrfJL3e5URYziPYUaV06u3BS2GHxgEeaJQQJ99CCAAAAAAAAAAAAINFRAZML2RvC"

st.set_page_config(page_title="BNP Paribas · Persona Simulator", page_icon="👤", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap');

html, body,
[class*="css"],
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="block-container"],
section.main, .stApp {
    background-color: #f5f6f0 !important;
    color: #1a2a1a !important;
    font-family: 'DM Sans', sans-serif !important;
}
p, span, div, h1, h2, h3, label { color: #1a2a1a !important; }

.app-header { text-align:center; padding:28px 0 16px; margin-bottom:4px; }
.app-pill { display:inline-block; font-family:'DM Mono',monospace; font-size:10px; letter-spacing:3px; color:#006632; border:1px solid #00a04a; padding:4px 14px; border-radius:20px; margin-bottom:12px; }
.app-title { font-family:'DM Serif Display',serif; font-size:36px; color:#003318; line-height:1.1; margin-bottom:4px; }
.app-sub { font-size:12px; color:#5a8a5a; font-family:'DM Mono',monospace; letter-spacing:1px; }

.user-row { display:flex; justify-content:flex-end; margin:14px 0 4px; }
.persona-row { display:flex; justify-content:flex-start; margin:14px 0 4px; gap:10px; align-items:flex-start; }
.user-bubble { background:#e8f0ff; border:1px solid #b8c8e8; border-radius:20px 4px 20px 20px; padding:13px 18px; max-width:75%; color:#1a2a4a !important; font-size:14.5px; line-height:1.65; }
.persona-bubble { background:#ffffff; border:1px solid #d0e8d0; border-radius:4px 20px 20px 20px; padding:13px 18px; max-width:100%; color:#1a2a1a !important; font-size:14.5px; line-height:1.65; box-shadow:0 2px 8px #00000010; }
.avatar { width:36px; height:36px; border-radius:50%; flex-shrink:0; background:linear-gradient(135deg,#006632,#004422); border:1px solid #00a04a; display:flex; align-items:center; justify-content:center; font-size:11px; color:#ffffff !important; font-family:'DM Mono',monospace; }
.msg-label { font-family:'DM Mono',monospace; font-size:9px; color:#5a8a5a; letter-spacing:2.5px; margin-bottom:4px; }
.msg-label-right { font-family:'DM Mono',monospace; font-size:9px; color:#4a6a9a; letter-spacing:2.5px; margin-bottom:4px; text-align:right; }
.persona-tag { display:inline-block; font-family:'DM Mono',monospace; font-size:10px; color:#006632; background:#e8f5ee; border:1px solid #a0d0b0; border-radius:12px; padding:2px 10px; margin-bottom:8px; }

.eval-panel { margin-top:14px; border-top:1px solid #e0ead0; padding-top:12px; }
.eval-section { margin-bottom:12px; }
.eval-section-title { font-family:'DM Mono',monospace; font-size:9px; letter-spacing:2px; margin-bottom:8px; }
.eval-verdict-high { color:#006632 !important; }
.eval-verdict-med  { color:#b87000 !important; }
.eval-verdict-low  { color:#c03030 !important; }
.score-row { display:flex; align-items:center; gap:10px; margin-bottom:10px; }
.score-circle { width:48px; height:48px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-family:'DM Mono',monospace; font-size:13px; font-weight:500; flex-shrink:0; }
.score-high { background:#e8f5ee; border:1.5px solid #00a04a; color:#006632 !important; }
.score-med  { background:#fff5e0; border:1.5px solid #f0a020; color:#b87000 !important; }
.score-low  { background:#ffeaea; border:1.5px solid #e05050; color:#c03030 !important; }
.verdict-text { font-family:'DM Mono',monospace; font-size:11px; }
.dim-bar-row { display:flex; align-items:center; gap:8px; margin-bottom:5px; }
.dim-label { font-size:10px; color:#4a7a5a !important; font-family:'DM Mono',monospace; width:190px; flex-shrink:0; }
.dim-bar-bg { flex:1; height:4px; background:#e0e8e0; border-radius:2px; }
.dim-bar-fill { height:100%; border-radius:2px; }
.dim-val { font-size:10px; font-family:'DM Mono',monospace; color:#4a7a5a !important; width:30px; text-align:right; }
.bullets { margin:6px 0 0 0; padding:0; list-style:none; }
.bullet-item { font-size:12px; color:#2a5a3a !important; padding:3px 0 3px 14px; position:relative; line-height:1.5; }
.bullet-item::before { content:"·"; position:absolute; left:0; color:#00a04a; }
.bullet-neg { color:#6a3030 !important; }
.bullet-neg::before { color:#c05050 !important; }
.eval-note { font-size:12px; color:#4a6a4a !important; line-height:1.6; margin-top:6px; font-style:italic; }
.rec-badge { display:inline-block; font-family:'DM Mono',monospace; font-size:10px; padding:3px 12px; border-radius:12px; margin-top:6px; }
.rec-use     { background:#e8f5ee; border:1px solid #a0d0b0; color:#006632 !important; }
.rec-caution { background:#fff5e0; border:1px solid #f0c060; color:#b87000 !important; }
.rec-avoid   { background:#ffeaea; border:1px solid #f0a0a0; color:#c03030 !important; }
.human-truth { background:#f0f8f2; border-left:3px solid #00a04a; padding:8px 12px; border-radius:0 8px 8px 0; font-size:12px; color:#2a5a3a !important; line-height:1.6; margin-top:6px; }
.risk-badge { display:inline-block; font-family:'DM Mono',monospace; font-size:10px; padding:2px 10px; border-radius:10px; }
.risk-low  { background:#e8f5ee; border:1px solid #a0d0b0; color:#006632 !important; }
.risk-med  { background:#fff5e0; border:1px solid #f0c060; color:#b87000 !important; }
.risk-high { background:#ffeaea; border:1px solid #f0a0a0; color:#c03030 !important; }

.chat-divider { border:none; border-top:1px solid #d8e8d0; margin:20px 0; }
.stTextInput > div > div > input { background:#ffffff !important; border:1px solid #c0d8c0 !important; border-radius:14px !important; color:#1a2a1a !important; font-size:14px !important; padding:14px 18px !important; }
.stTextInput > div > div > input:focus { border-color:#006632 !important; box-shadow:none !important; }
.stTextInput > div > div > input::placeholder { color:#8aaa8a !important; }
.stButton > button { background:linear-gradient(135deg,#006632,#004a24) !important; border:1px solid #00a04a !important; border-radius:14px !important; color:#ffffff !important; font-family:'DM Mono',monospace !important; font-size:13px !important; padding:12px 20px !important; width:100% !important; }
.stButton > button:hover { background:linear-gradient(135deg,#007a3a,#005a2a) !important; }
.sugg-title { font-family:'DM Mono',monospace; font-size:9px; color:#8aaa8a; letter-spacing:3px; text-align:center; margin:28px 0 12px; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Azure call — identical to your working Gradio code ───────────────────────
def call_azure(question):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AZURE_KEY}"
    }
    response = requests.post(
        AZURE_ENDPOINT,
        headers=headers,
        json={"Question": question},
        timeout=30
    )
    if response.status_code == 200:
        result = response.json()

        # Debug: store raw result in session so we can inspect it
        st.session_state["last_raw"] = result

        # Parse Answer — same as your working Gradio code
        answer_dict   = json.loads(result["Answer"])
        response_text = answer_dict["response"]
        persona_name  = answer_dict.get("persona", "")

        # Parse Evaluator — from top-level key
        evaluator = None
        if "Evaluator" in result:
            evaluator = json.loads(result["Evaluator"])

        return response_text, persona_name, evaluator
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")

# ── Helpers ───────────────────────────────────────────────────────────────────
def score_css(val):
    try:
        v = float(val)
        return "score-high" if v >= 0.8 else "score-med" if v >= 0.6 else "score-low"
    except: return "score-med"

def verdict_css(text):
    t = str(text).lower()
    if any(w in t for w in ["high","authentic","excellent"]): return "eval-verdict-high"
    if any(w in t for w in ["medium","moderate","partial"]): return "eval-verdict-med"
    return "eval-verdict-low"

def bar_color(val):
    try:
        v = float(val)
        return "#00a04a" if v >= 0.8 else "#f0a020" if v >= 0.6 else "#e05050"
    except: return "#8aaa8a"

def rec_css(text):
    t = str(text).lower()
    if "caution" in t: return "rec-caution"
    if "avoid" in t or "discard" in t: return "rec-avoid"
    return "rec-use"

def risk_css(text):
    t = str(text).lower()
    return "risk-low" if "low" in t else "risk-high" if "high" in t else "risk-med"

def render_evaluator(evaluator):
    if not evaluator: return ""
    html = '<div class="eval-panel">'

    align = evaluator.get("ALIGNMENT AUDIT", {})
    if align:
        conf      = align.get("Confidence Score", "")
        verdict   = align.get("Verdict", "")
        dims      = align.get("Dimension Scores", {})
        strengths = align.get("Strengths", [])
        misaligns = align.get("Misalignments", [])
        note      = align.get("Audit Note", "")
        rec       = align.get("Recommendation", "")

        html += f'''<div class="eval-section">
            <div class="eval-section-title eval-verdict-high">▸ ALIGNMENT AUDIT</div>
            <div class="score-row">
                <div class="score-circle {score_css(conf)}">{conf}</div>
                <div>
                    <div class="verdict-text {verdict_css(verdict)}">{verdict}</div>
                    <div style="font-size:10px;color:#5a8a5a;font-family:'DM Mono',monospace;margin-top:2px;">Confidence Score</div>
                </div>
            </div>'''
        if dims:
            html += '<div style="margin:8px 0;">'
            for dim, val in dims.items():
                pct = int(float(val) * 100)
                html += f'''<div class="dim-bar-row">
                    <div class="dim-label">{dim}</div>
                    <div class="dim-bar-bg"><div class="dim-bar-fill" style="width:{pct}%;background:{bar_color(val)};"></div></div>
                    <div class="dim-val">{val}</div></div>'''
            html += '</div>'
        if strengths:
            html += '<ul class="bullets">' + ''.join(f'<li class="bullet-item">{s}</li>' for s in strengths) + '</ul>'
        if misaligns:
            html += '<ul class="bullets">' + ''.join(f'<li class="bullet-item bullet-neg">{m}</li>' for m in misaligns) + '</ul>'
        if note:
            html += f'<div class="eval-note">{note}</div>'
        if rec:
            html += f'<div class="rec-badge {rec_css(rec)}">⟶ {rec}</div>'
        html += '</div>'

    integ = evaluator.get("INTEGRITY AUDIT", {})
    if integ:
        iscore   = integ.get("Integrity Score", "")
        iverdict = integ.get("Verdict", "")
        metrics  = integ.get("Metric Breakdown", {})
        flags    = integ.get("Behavioral Red Flags", [])
        truth    = integ.get("Human Truth Synthesis", "")
        halluc   = integ.get("Risk of Hallucination", "")

        html += f'''<div class="eval-section" style="border-top:1px solid #e0ead0;padding-top:12px;">
            <div class="eval-section-title" style="color:#006632;">▸ INTEGRITY AUDIT</div>
            <div class="score-row">
                <div class="score-circle {score_css(iscore)}">{iscore}</div>
                <div>
                    <div class="verdict-text {verdict_css(iverdict)}">{iverdict}</div>
                    <div style="font-size:10px;color:#5a8a5a;font-family:'DM Mono',monospace;margin-top:2px;">Integrity Score</div>
                </div>
            </div>'''
        if metrics:
            html += '<div style="margin:8px 0;">'
            for m, val in metrics.items():
                pct = int(float(val) * 100)
                html += f'''<div class="dim-bar-row">
                    <div class="dim-label">{m}</div>
                    <div class="dim-bar-bg"><div class="dim-bar-fill" style="width:{pct}%;background:{bar_color(val)};"></div></div>
                    <div class="dim-val">{val}</div></div>'''
            html += '</div>'
        if flags:
            html += '<ul class="bullets">' + ''.join(f'<li class="bullet-item bullet-neg">{f}</li>' for f in flags) + '</ul>'
        if truth:
            html += f'<div class="human-truth">💡 {truth}</div>'
        if halluc:
            html += f'<div style="margin-top:8px;font-size:10px;color:#5a7a5a;font-family:DM Mono,monospace;">HALLUCINATION RISK &nbsp;<span class="risk-badge {risk_css(halluc)}">{halluc}</span></div>'
        html += '</div>'

    html += '</div>'
    return html

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <div style="margin-bottom:16px;">
        <svg width="180" height="44" viewBox="0 0 180 44" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="0" y="0" width="6" height="44" rx="2" fill="#00A04A"/>
          <text x="14" y="20" font-family="Arial Black, sans-serif" font-size="15" font-weight="900" fill="#003318" letter-spacing="1">BNP</text>
          <text x="14" y="38" font-family="Arial, sans-serif" font-size="13" font-weight="400" fill="#006632" letter-spacing="2">PARIBAS</text>
          <circle cx="165" cy="22" r="10" fill="#00A04A" opacity="0.15"/>
          <text x="159" y="27" font-family="Arial" font-size="14" fill="#006632">✦</text>
        </svg>
    </div>
    <div class="app-pill">● SYNTHETIC PERSONA ENGINE</div>
    <div class="app-title">Persona Simulator</div>
    <div class="app-sub">you are the bank &nbsp;·&nbsp; ask your customer anything</div>
</div>
<hr style="border:none;border-top:2px solid #00A04A;margin:0 0 20px;opacity:0.3;">
""", unsafe_allow_html=True)

# ── Debug expander (shows raw response — remove before final demo) ────────────
if st.session_state.get("last_raw"):
    with st.expander("🔍 Debug: raw response", expanded=False):
        st.json(st.session_state["last_raw"])

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
        st.session_state.pop("last_raw", None)
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
