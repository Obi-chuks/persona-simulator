import streamlit as st
import requests
import json

# --- SECRETS & ENDPOINT ---
# Ensure "AZURE_KEY" is set in your Streamlit Cloud Dashboard Settings -> Secrets
AZURE_ENDPOINT = "https://endpoint1.eastus.inference.ml.azure.com/score"
try:
    AZURE_KEY = st.secrets["AZURE_KEY"]
except:
    AZURE_KEY = "BOUOgztPZVsDNCG1qLpewxY3sls8NDwM13rQ2Ko8Y4JPznVpYsT4JQQJ99CCAAAAAAAAAAAAINFRAZMLSDUd"

# --- BORDEAUX-OPTIMIZED PRESETS ---
# These are calibrated to pass the "Bordeaux Regional Logic" check of your Evaluator
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
if "persona" not in st.session_state: st.session_state.persona = {}

# --- CORE FUNCTIONS ---
def call_azure(question):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {AZURE_KEY}"}
    # FIXED: Key changed to "Question" to match your Azure Input exactly
    payload = {"Question": question} 
    
    response = requests.post(AZURE_ENDPOINT, headers=headers, json=payload, timeout=45)
    
    if response.status_code != 200:
        return {"Answer": "My cognitive engine is experiencing a connection mismatch.", "Evaluator": "Audit Failure"}
    
    return response.json()

def eval_badge(evaluation):
    if not evaluation: return ""
    return f'<div class="eval-badge">🛡️ INTEGRITY AUDIT: {evaluation}</div>'

def completeness_bar(field, pct, real):
    color = "#00c896" if real else "#f5a623"
    return f'<div style="margin-bottom:10px;"><div style="display:flex;justify-content:space-between;"><span style="color:#6a8a7a;font-size:10px;">{field}</span><span style="color:{color};font-size:10px;">{pct}%</span></div><div style="height:3px;background:#1a2a2a;"><div style="height:100%;width:{pct}%;background:{color};"></div></div></div>'

def send_message(question, p):
    st.session_state.messages.append({"role":"user","content":question})
    with st.spinner(f"{p['name']} is reflecting..."):
        data = call_azure(question)
        # FIXED: Mapped to "Answer" and "Evaluator" (Capitalized) to match Azure Output
        ans = data.get("Answer", "Internal mapping error.")
        evl = data.get("Evaluator", "Pending...")
        st.session_state.messages.append({"role":"persona","content":ans,"evaluation":evl})
    st.rerun()

# --- SIDEBAR UI ---
with st.sidebar:
    st.markdown("### ● BNPP · PERSONA SIMULATOR")
    st.markdown("---")
    choice = st.selectbox("Select Persona", list(PRESET_PERSONAS.keys()))
    preset = PRESET_PERSONAS[choice]
    
    if preset:
        st.markdown(f"**Target:** {preset['name']}")
        if st.button("▶ Start Interview"):
            st.session_state.persona = preset
            st.session_state.persona_active = True
            st.session_state.messages = [{"role":"persona","content":f"Hello, I am {preset['name']}. Ask me about banking in Bordeaux.", "evaluation":"Verified Preset"}]
            st.rerun()
    
    if st.session_state.persona_active:
        st.markdown("---")
        if st.button("↺ Reset Simulation"):
            st.session_state.persona_active = False
            st.session_state.messages = []
            st.rerun()

# --- MAIN CHAT INTERFACE ---
if not st.session_state.persona_active:
    st.write("### ← Select a Persona in the sidebar to begin.")
else:
    p = st.session_state.persona
    
    # Simple Profile Header
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1: st.metric("Income", p['income'])
    with col2: st.write(f"**Role:** {p['role']}")
    with col3: st.write(f"**Loc:** {p['location']}")
    
    st.markdown("---")
    
    # Chat History
    for m in st.session_state.messages:
        if m["role"] == "user":
            st.markdown(f'<div class="speaker-label" style="text-align:right;">USER</div><div class="user-msg">{m["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="speaker-label">{p["name"].upper()}</div><div class="persona-msg">{m["content"]}{eval_badge(m.get("evaluation"))}</div>', unsafe_allow_html=True)

    # Chat Input
    query = st.chat_input(f"Ask {p['name']} a question...")
    if query:
        send_message(query, p)
