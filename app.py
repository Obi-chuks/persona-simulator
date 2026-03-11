import streamlit as st
import requests
import json

# ── Config ───────────────────────────────────────────────────────────────────
AZURE_ENDPOINT = "https://juansesame.eastus.inference.ml.azure.com/score"
try:
    AZURE_KEY = st.secrets["AZURE_KEY"]
except Exception:
    AZURE_KEY = "dxPwTV0Q02oN11AxphklxrfJL3e5URYziPYUaV06u3BS2GHxgEeaJQQJ99CCAAAAAAAAAAAAINFRAZML2RvC"

# ── Page setup ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Persona Simulator", page_icon="👤", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    background-color: #080b12 !important;
    color: #d0ddd0;
    font-family: 'DM Sans', sans-serif;
}

/* ── Header ── */
.app-header {
    text-align: center;
    padding: 36px 0 20px;
    margin-bottom: 8px;
}
.app-pill {
    display: inline-block;
    font-family: 'DM Mono', monospace;
    font-size: 10px; letter-spacing: 3px;
    color: #3a7a5a; border: 1px solid #1a3a2a;
    padding: 4px 14px; border-radius: 20px; margin-bottom: 14px;
}
.app-title {
    font-family: 'DM Serif Display', serif;
    font-size: 38px; color: #e8eed8; line-height: 1.1; margin-bottom: 6px;
}
.app-sub {
    font-size: 13px; color: #3a5a4a;
    font-family: 'DM Mono', monospace; letter-spacing: 1px;
}

/* ── Chat bubbles ── */
.user-row {
    display: flex; justify-content: flex-end;
    margin: 16px 0 4px;
}
.persona-row {
    display: flex; justify-content: flex-start;
    margin: 16px 0 4px; gap: 10px; align-items: flex-start;
}
.user-bubble {
    background: linear-gradient(135deg, #0f2040, #0a1830);
    border: 1px solid #1e3a60;
    border-radius: 20px 4px 20px 20px;
    padding: 13px 18px;
    max-width: 75%;
    color: #90b8e0;
    font-size: 14.5px; line-height: 1.65;
}
.persona-bubble {
    background: linear-gradient(135deg, #0a1a10, #081410);
    border: 1px solid #1a3020;
    border-radius: 4px 20px 20px 20px;
    padding: 13px 18px;
    max-width: 75%;
    color: #c0d8c0;
    font-size: 14.5px; line-height: 1.65;
}
.avatar {
    width: 36px; height: 36px; border-radius: 50%; flex-shrink: 0;
    background: linear-gradient(135deg, #0d2a1a, #0a1f30);
    border: 1px solid #2a4a3a;
    display: flex; align-items: center; justify-content: center;
    font-size: 13px; color: #5a9a7a;
    font-family: 'DM Mono', monospace; font-weight: 500;
}
.msg-label {
    font-family: 'DM Mono', monospace;
    font-size: 9px; color: #2a4a3a;
    letter-spacing: 2.5px; margin-bottom: 4px;
    text-transform: uppercase;
}
.msg-label-right {
    font-family: 'DM Mono', monospace;
    font-size: 9px; color: #2a3a5a;
    letter-spacing: 2.5px; margin-bottom: 4px;
    text-transform: uppercase; text-align: right;
}

/* ── Evaluation badge ── */
.eval-block {
    margin-top: 10px;
    padding: 10px 14px;
    border-radius: 10px;
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    line-height: 1.5;
}
.eval-high {
    background: #00c89610;
    border: 1px solid #00c89630;
    color: #00c896;
}
.eval-med {
    background: #f5a62310;
    border: 1px solid #f5a62330;
    color: #f5a623;
}
.eval-low {
    background: #ff5c5c10;
    border: 1px solid #ff5c5c30;
    color: #ff7a7a;
}
.eval-score {
    font-size: 18px; font-weight: bold;
    display: inline-block; margin-right: 8px;
}
.eval-label { font-size: 10px; letter-spacing: 2px; opacity: 0.8; }
.eval-text { margin-top: 5px; font-size: 11px; opacity: 0.85; font-family: 'DM Sans', sans-serif; }

/* ── Divider ── */
.chat-divider {
    border: none; border-top: 1px solid #111820;
    margin: 24px 0;
}

/* ── Input ── */
.stTextInput > div > div > input {
    background: #0d1520 !important;
    border: 1px solid #1e2d40 !important;
    border-radius: 14px !important;
    color: #c0d0e0 !important;
    font-size: 14px !important;
    font-family: 'DM Sans', sans-serif !important;
    padding: 14px 18px !important;
    transition: border-color 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: #2a5a4a !important;
    box-shadow: 0 0 0 1px #1a3a2a !important;
}
.stTextInput > div > div > input::placeholder { color: #2a4a3a !important; }

.stButton > button {
    background: linear-gradient(135deg, #1a4a3a, #0d3020) !important;
    border: 1px solid #2a5a4a !important;
    border-radius: 14px !important;
    color: #6ecf9a !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 13px !important;
    padding: 12px 20px !important;
    width: 100% !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #225a4a, #1a4030) !important;
    border-color: #3a7a5a !important;
}

/* ── Suggested questions ── */
.sugg-title {
    font-family: 'DM Mono', monospace;
    font-size: 9px; color: #1a3a2a;
    letter-spacing: 3px; text-align: center;
    margin: 32px 0 14px;
}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Azure call ────────────────────────────────────────────────────────────────
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
        answer_dict = json.loads(result["Answer"])
        response_text = answer_dict["response"]
        # Grab evaluation — try multiple possible keys
        evaluation = (answer_dict.get("evaluation") or
                      answer_dict.get("eval") or
                      answer_dict.get("score") or
                      answer_dict.get("quality") or
                      result.get("evaluation") or
                      result.get("Evaluation") or None)
        return response_text, evaluation
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")

# ── Evaluation renderer ───────────────────────────────────────────────────────
def render_eval(evaluation):
    if not evaluation:
        return ""
    raw = str(evaluation)
    lower = raw.lower()

    # Determine quality tier
    if any(w in lower for w in ["high","excellent","very good","bon","élevé","5","4.5","4/5","5/5"]):
        css, icon, label, score = "eval-high", "✦", "HIGH QUALITY", "HQ"
    elif any(w in lower for w in ["medium","moderate","moyen","average","fair","3","3.5","3/5"]):
        css, icon, label, score = "eval-med", "◈", "MODERATE", "MQ"
    else:
        css, icon, label, score = "eval-low", "◇", "LOW QUALITY", "LQ"

    # Truncate long eval text
    display_text = raw if len(raw) < 200 else raw[:200] + "…"

    return f"""
    <div class="eval-block {css}">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
            <span style="font-size:15px;">{icon}</span>
            <span class="eval-label">{label}</span>
        </div>
        <div class="eval-text">{display_text}</div>
    </div>"""

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
        eval_html = render_eval(msg.get("evaluation"))
        st.markdown(f"""
        <div class="persona-row">
            <div class="avatar">AI</div>
            <div style="flex:1;">
                <div class="msg-label">SYNTHETIC PERSONA</div>
                <div class="persona-bubble">
                    {msg["content"]}
                    {eval_html}
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

# ── Input ─────────────────────────────────────────────────────────────────────
st.markdown("<hr class='chat-divider'>", unsafe_allow_html=True)

col_in, col_btn = st.columns([5, 1])
with col_in:
    user_input = st.text_input(
        "", placeholder="Ask the persona a marketing question…",
        label_visibility="collapsed", key="chat_input"
    )
with col_btn:
    send = st.button("Send ↑")

col_clear, _ = st.columns([1, 5])
with col_clear:
    if st.button("↺ Clear"):
        st.session_state.messages = []
        st.rerun()

# ── Send logic ────────────────────────────────────────────────────────────────
if send and user_input.strip():
    st.session_state.messages.append({"role": "user", "content": user_input.strip()})
    with st.spinner("Persona is thinking…"):
        try:
            answer, evaluation = call_azure(user_input.strip())
            st.session_state.messages.append({
                "role": "persona",
                "content": answer,
                "evaluation": evaluation
            })
        except Exception as e:
            st.session_state.messages.append({
                "role": "persona",
                "content": f"⚠️ {e}",
                "evaluation": None
            })
    st.rerun()

# ── Suggested questions (only on empty chat) ──────────────────────────────────
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
                st.session_state.messages.append({"role": "user", "content": q})
                with st.spinner("Persona is thinking…"):
                    try:
                        answer, evaluation = call_azure(q)
                        st.session_state.messages.append({
                            "role": "persona",
                            "content": answer,
                            "evaluation": evaluation
                        })
                    except Exception as e:
                        st.session_state.messages.append({
                            "role": "persona",
                            "content": f"⚠️ {e}",
                            "evaluation": None
                        })
                st.rerun()
