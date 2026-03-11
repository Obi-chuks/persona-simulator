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
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    background-color: #0a0d14 !important;
    color: #c8d8c0;
    font-family: 'Playfair Display', Georgia, serif;
}

/* Header */
.header {
    text-align: center;
    padding: 32px 0 8px;
    border-bottom: 1px solid #1e2535;
    margin-bottom: 24px;
}
.header-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: #3a5a4a;
    letter-spacing: 4px;
    margin-bottom: 8px;
}
.header-title {
    font-size: 32px;
    color: #e8ead0;
    line-height: 1.2;
}
.header-sub {
    font-size: 13px;
    color: #4a6a5a;
    margin-top: 6px;
    font-family: 'JetBrains Mono', monospace;
}

/* Chat bubbles */
.user-row { display: flex; justify-content: flex-end; margin: 10px 0; }
.persona-row { display: flex; justify-content: flex-start; margin: 10px 0; gap: 10px; align-items: flex-start; }

.user-bubble {
    background: #0d1f3c;
    border: 1px solid #1a3a5c;
    border-radius: 18px 4px 18px 18px;
    padding: 12px 16px;
    max-width: 72%;
    color: #a0b8d8;
    font-size: 15px;
    line-height: 1.6;
}
.persona-bubble {
    background: #0e1a14;
    border: 1px solid #1a3a2a;
    border-radius: 4px 18px 18px 18px;
    padding: 12px 16px;
    max-width: 72%;
    color: #c8d8c0;
    font-size: 15px;
    line-height: 1.6;
}
.avatar {
    width: 34px; height: 34px; border-radius: 50%; flex-shrink: 0;
    background: linear-gradient(135deg, #1a3a5c, #0d2a1a);
    border: 1px solid #2a4a3a;
    display: flex; align-items: center; justify-content: center;
    font-size: 14px; color: #7ecfa0;
    font-family: 'JetBrains Mono', monospace;
}
.label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px; color: #3a5a4a;
    letter-spacing: 2px; margin-bottom: 3px;
}

/* Input */
.stTextInput > div > div > input {
    background: #0e1a24 !important;
    border: 1px solid #2a3a4a !important;
    border-radius: 12px !important;
    color: #c0d0e0 !important;
    font-size: 14px !important;
    font-family: 'Playfair Display', serif !important;
    padding: 12px 16px !important;
}
.stTextInput > div > div > input:focus {
    border-color: #3a6a5a !important;
    box-shadow: none !important;
}
.stButton > button {
    background: linear-gradient(135deg, #1a4a3a, #0d3a2a) !important;
    border: 1px solid #2a5a4a !important;
    border-radius: 12px !important;
    color: #7ecfa0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px !important;
    padding: 10px 20px !important;
    width: 100% !important;
}
.stButton > button:hover {
    border-color: #3a7a5a !important;
}

/* Clear button */
.clear-btn > button {
    background: transparent !important;
    border: 1px solid #2a3a4a !important;
    color: #3a5a4a !important;
    font-size: 11px !important;
}

/* Divider */
.input-area {
    position: sticky;
    bottom: 0;
    background: #0a0d14;
    padding: 16px 0 8px;
    border-top: 1px solid #1e2535;
    margin-top: 16px;
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
        return answer_dict["response"]
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header">
    <div class="header-tag">● BNPP · SYNTHETIC PERSONA ENGINE</div>
    <div class="header-title">Persona Simulator</div>
    <div class="header-sub">You are the bank. The persona will answer.</div>
</div>
""", unsafe_allow_html=True)

# ── Chat messages ─────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="user-row">
            <div>
                <div class="label" style="text-align:right;">YOU · BANK</div>
                <div class="user-bubble">{msg["content"]}</div>
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="persona-row">
            <div class="avatar">P</div>
            <div>
                <div class="label">SYNTHETIC PERSONA</div>
                <div class="persona-bubble">{msg["content"]}</div>
            </div>
        </div>""", unsafe_allow_html=True)

# ── Input area ────────────────────────────────────────────────────────────────
st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

col_input, col_send = st.columns([5, 1])
with col_input:
    user_input = st.text_input(
        "", placeholder="Ask the persona a marketing question…",
        label_visibility="collapsed", key="chat_input"
    )
with col_send:
    send = st.button("Send ↑")

# Clear button
col_clear, _ = st.columns([1, 4])
with col_clear:
    with st.container():
        st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
        if st.button("↺ Clear chat"):
            st.session_state.messages = []
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ── Send logic ────────────────────────────────────────────────────────────────
if send and user_input.strip():
    st.session_state.messages.append({"role": "user", "content": user_input.strip()})
    with st.spinner("Persona is thinking…"):
        try:
            answer = call_azure(user_input.strip())
            st.session_state.messages.append({"role": "persona", "content": answer})
        except Exception as e:
            st.session_state.messages.append({"role": "persona", "content": f"⚠️ {e}"})
    st.rerun()

# ── Suggested questions ───────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    st.markdown('<div style="font-family:JetBrains Mono,monospace;font-size:10px;color:#3a5a4a;letter-spacing:2px;margin-bottom:10px;text-align:center;">TRY ASKING</div>', unsafe_allow_html=True)
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
                        answer = call_azure(q)
                        st.session_state.messages.append({"role": "persona", "content": answer})
                    except Exception as e:
                        st.session_state.messages.append({"role": "persona", "content": f"⚠️ {e}"})
                st.rerun()
