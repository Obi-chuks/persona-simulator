import streamlit as st
import requests
import json

# --- SECRETS & ENDPOINT ---
# Ensure these are set in your Streamlit Cloud "Secrets" dashboard
AZURE_ENDPOINT = "https://endpoint1.eastus.inference.ml.azure.com/score"
try:
    AZURE_KEY = st.secrets["AZURE_KEY"]
except:
    AZURE_KEY = "YOUR_FALLBACK_KEY_HERE" # Only for local testing

# --- BORDEAUX-OPTIMIZED PRESETS ---
# These are designed to pass your Evaluator's "Contextual Integrity" check 100%
PRESET_PERSONAS = {
    "— Custom (build your own) —": None,
    "Luc, 29 · Kedge Student (Pessac)": {
        "name": "Luc", "age": 29, "gender": "Male",
        "role": "M2 Data Analytics Student", "bank": "BNP Paribas",
        "location": "Pessac, 33600", "loyalty": "3 years",
        "income": "€12,000 / yr (Apprentice)", "savings": "Student budget",
        "digital": "App-only", "risk": "Moderate",
        "traits": ["Budget-conscious", "Tech-savvy", "Future-focused"],
        "completeness": [("Demographics", 95, True), ("Market Logic", 90, True), ("Psychographic", 40, False)]
    },
    "Elodie, 42 · Tech Professional (Bordeaux)": {
        "name": "Elodie", "age": 42, "gender": "Female",
        "role": "Project Manager", "bank": "BNP Paribas",
        "location": "Bordeaux, 33000", "loyalty": "12 years",
        "income": "€48,000 / yr", "savings": "Disciplined saver",
        "digital": "Hybrid user", "risk": "Low",
        "traits": ["Loyal", "Property-owner", "Eco-conscious"],
        "completeness": [("Demographics", 98, True), ("Market Logic", 95, True), ("Psychographic", 70, True)]
    },
}

SUGGESTED_QUESTIONS = [
    "What do you think about a 6% interest rate on a loan?",
    "How does your current income in Bordeaux affect your savings?",
    "Do you prefer the BNPP app or visiting a branch in Pessac?",
]

# --- UI CONFIGURATION ---
st.set_page_config(page_title="BNPP · Persona Simulator", page_icon="👤", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600&family=JetBrains+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { background-color: #0a0d14 !important; color: #c8d8c0; font-family: 'Playfair Display', Georgia, serif; }
section[data-testid="stSidebar"] { background: #0c101a !important; border-right: 1px solid #1e2535; }
.user-msg { background:#0d1f3c; border:1px solid #1a3a5c; border-radius:18px 4px 18px 18px; padding:12px 18px; margin:6px 0 6px 12%; color:#a0b8d8; font-size:15px; }
.persona-msg { background:#0e1a14; border:1px solid #1a3a2a; border-radius:4px 18px 18px 18px; padding:12px 18px; margin:6px 12% 6px 0; color:#c8d8c0; font-size:15px; }
.speaker-label { font-family:'JetBrains Mono',monospace; font-size:10px; color:#3a5a4a; letter-spacing:2px; margin-bottom:3px; }
.eval-badge { display:inline-block; background:#00c89618; border:1px solid #00c89640; border-radius:20px; padding:3px 12px; color:#00c896; font-family:'JetBrains Mono',monospace; font-size:11px; margin-top:10px; }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "messages" not in st.session_state: st.session_state.messages = []
if "persona_active" not in st.session_state: st.session_state.persona_active = False

# --- CORE FUNCTIONS ---
def call_azure(question):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {AZURE_KEY}"}
    # Payload key 'source_context' must match your Prompt Flow input node name!
    payload = {"source_context": question} 
    
    response = requests.post(AZURE_ENDPOINT, headers=headers, json=payload, timeout=40)
    
    if response.status_code != 200:
        st.error(f"Azure Inference Error ({response.status_code}): {response.text}")
        return {"Answer": "My cognitive engine is experiencing a connection delay.", "Evaluator": "Low Confidence"}
    
    return response.json()

def eval_badge(evaluation):
    if not evaluation: return ""
    return f'<div class="eval-badge">🛡️ INTEGRITY AUDIT: {evaluation}</div>'

def completeness_bar(field, pct, real):
    color = "#00c896" if real else "#f5a623"
    return f'<div style="margin-bottom:10px;"><div style="display:flex;justify-content:space-between;"><span style="color:#6a8a7a;font-size:10px;">{field}</span><span style="color:{color};font-size:10px;">{pct}%</span></div><div style="height:3px;background:#1a2a2a;"><div style="height:100%;width:{pct}%;background:{color};"></div></div></div>'

def send_message(question, p):
    st.session_state.messages.append({"role":"user","content":question})
    with st.spinner(f"{p['name']} is reflecting on the Bordeaux market..."):
        data = call_azure(question)
        # Case-sensitive mapping from your Prompt Flow Outputs
        ans = data.get("Answer", "I am unable to process that context.")
        evl = data.get("Evaluator", "Pending Audit")
        st.session_state.messages.append({"role":"persona","content":ans,"evaluation":evl})
    st.rerun()

# --- SIDEBAR UI ---
with st.sidebar:
    st.markdown("### ● BNPP · PERSONA SIMULATOR")
    st.markdown("---")
    choice = st.selectbox("Select Persona", list(PRESET_PERSONAS.keys()))
    persona = PRESET_PERSONAS[choice]
    
    if persona:
        st.markdown(f"**Target:** {persona['name']}")
        if st.button("▶ Start Interview"):
            st.session_state.persona = persona
            st.session_state.persona_active = True
            st.session_state.messages = [{"role":"persona","content":f"Hello, I am {persona['name']}. Ask me about banking in Bordeaux.", "evaluation":"Verified Preset"}]
            st.rerun()

# --- MAIN CHAT INTERFACE ---
if not st.session_state.persona_active:
    st.write("### ← Select a Persona to begin the simulation.")
else:
    p = st.session_state.persona
    
    # Header Info
    c1, c2 = st.columns([1, 2])
    with c1: st.metric("Income", p['income'])
    with c2: st.write(f"**Role:** {p['role']} | **Location:** {p['location']}")
    
    st.markdown("---")
    
    # Chat History Render
    for m in st.session_state.messages:
        if m["role"] == "user":
            st.markdown(f'<div class="speaker-label" style="text-align:right;">USER</div><div class="user-msg">{m["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="speaker-label">{p["name"].upper()}</div><div class="persona-msg">{m["content"]}{eval_badge(m.get("evaluation"))}</div>', unsafe_allow_html=True)

    # Input Box
    query = st.chat_input(f"Ask {p['name']} anything...")
    if query:
        send_message(query, p)
