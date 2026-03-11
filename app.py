import streamlit as st
import requests
import json

AZURE_ENDPOINT = "https://endpoint1.eastus.inference.ml.azure.com/score"
AZURE_KEY = st.secrets["AZURE_KEY"]

PRESET_PERSONAS = {
    "— Custom (build your own) —": None,
    "Marie, 34 · Urban Professional": {
        "name": "Marie", "age": 34, "gender": "Female",
        "role": "Marketing Manager", "bank": "BNP Paribas",
        "location": "Paris, 75008", "loyalty": "8 years",
        "income": "€52,000 / yr", "savings": "Active saver",
        "digital": "Heavy app user", "risk": "Moderate",
        "traits": ["Loyal customer", "Digital-savvy", "Career-focused", "Urban lifestyle"],
        "completeness": [("Demographics", 95, True), ("Behavior", 72, False),
                         ("Preferences", 58, False), ("Life Events", 40, False)],
    },
    "Jean-Pierre, 58 · Risk-Averse Retiree": {
        "name": "Jean-Pierre", "age": 58, "gender": "Male",
        "role": "Retired Engineer", "bank": "Société Générale",
        "location": "Lyon, 69001", "loyalty": "22 years",
        "income": "€38,000 / yr", "savings": "Conservative saver",
        "digital": "Branch preferred", "risk": "Low",
        "traits": ["Long-term loyal", "Branch loyal", "Risk-averse", "Pension-focused"],
        "completeness": [("Demographics", 98, True), ("Behavior", 80, True),
                         ("Preferences", 45, False), ("Life Events", 60, True)],
    },
    "Camille, 27 · Digital-Native Student": {
        "name": "Camille", "age": 27, "gender": "Female",
        "role": "Graduate Student", "bank": "Revolut + BNP Paribas",
        "location": "Bordeaux, 33000", "loyalty": "2 years",
        "income": "€14,000 / yr", "savings": "Minimal savings",
        "digital": "App-only user", "risk": "High (speculative)",
        "traits": ["Digital-native", "Budget-conscious", "Mobile-first", "Side-hustle mindset"],
        "completeness": [("Demographics", 80, True), ("Behavior", 50, False),
                         ("Preferences", 65, False), ("Life Events", 25, False)],
    },
}

SUGGESTED_QUESTIONS = [
    "How do you manage your savings?",
    "Do you use your bank's mobile app?",
    "Are you planning a major purchase?",
    "How loyal are you to your current bank?",
    "What financial product would interest you most?",
    "How do you feel about financial risk?",
]

st.set_page_config(page_title="BNPP · Persona Simulator", page_icon="👤", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600&family=JetBrains+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { background-color: #0a0d14 !important; color: #c8d8c0; font-family: 'Playfair Display', Georgia, serif; }
section[data-testid="stSidebar"] { background: #0c101a !important; border-right: 1px solid #1e2535; }
section[data-testid="stSidebar"] * { color: #a0b8a8 !important; }
.user-msg { background:#0d1f3c; border:1px solid #1a3a5c; border-radius:18px 4px 18px 18px; padding:12px 18px; margin:6px 0 6px 12%; color:#a0b8d8; font-size:15px; line-height:1.6; }
.persona-msg { background:#0e1a14; border:1px solid #1a3a2a; border-radius:4px 18px 18px 18px; padding:12px 18px; margin:6px 12% 6px 0; color:#c8d8c0; font-size:15px; line-height:1.6; }
.speaker-label { font-family:'JetBrains Mono',monospace; font-size:10px; color:#3a5a4a; letter-spacing:2px; margin-bottom:3px; }
.eval-high { display:inline-block; background:#00c89618; border:1px solid #00c89640; border-radius:20px; padding:3px 12px; color:#00c896; font-family:'JetBrains Mono',monospace; font-size:11px; margin-top:5px; }
.eval-med  { display:inline-block; background:#f5a62318; border:1px solid #f5a62340; border-radius:20px; padding:3px 12px; color:#f5a623; font-family:'JetBrains Mono',monospace; font-size:11px; margin-top:5px; }
.eval-low  { display:inline-block; background:#ff5c5c18; border:1px solid #ff5c5c40; border-radius:20px; padding:3px 12px; color:#ff5c5c; font-family:'JetBrains Mono',monospace; font-size:11px; margin-top:5px; }
.stTextInput > div > div > input { background:#0e1a24 !important; border:1px solid #2a3a4a !important; border-radius:12px !important; color:#c0d0e0 !important; font-size:14px !important; }
.stButton > button { background:linear-gradient(135deg,#1a4a3a,#0d3a2a) !important; border:1px solid #2a5a4a !important; border-radius:10px !important; color:#7ecfa0 !important; font-family:'JetBrains Mono',monospace !important; font-size:12px !important; width:100% !important; }
</style>
""", unsafe_allow_html=True)

if "messages"       not in st.session_state: st.session_state.messages = []
if "persona_active" not in st.session_state: st.session_state.persona_active = False
if "persona"        not in st.session_state: st.session_state.persona = {}

def call_azure(question):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {AZURE_KEY}"}
    r = requests.post(AZURE_ENDPOINT, headers=headers, json={"Question": question}, timeout=30)
    r.raise_for_status()
    return r.json()

def eval_badge(evaluation):
    if not evaluation: return ""
    text = str(evaluation); lower = text.lower()
    if any(w in lower for w in ["high","excellent","good","bon"]):
        css, label = "eval-high", "✦ High Quality"
    elif any(w in lower for w in ["medium","moderate","moyen"]):
        css, label = "eval-med", "◈ Medium"
    else:
        css, label = "eval-low", "◇ Low Quality"
    return f'<div class="{css}">{label} · {text[:80]}</div>'

def completeness_bar(field, pct, real):
    color = "#00c896" if real else "#f5a623"
    dot   = "●" if real else "◌"
    return f'<div style="margin-bottom:10px;"><div style="display:flex;justify-content:space-between;margin-bottom:3px;"><span style="color:#6a8a7a;font-size:10px;font-family:JetBrains Mono,monospace;">{field}</span><span style="color:{color};font-size:10px;font-family:JetBrains Mono,monospace;">{pct}% {dot}</span></div><div style="height:3px;background:#1a2a2a;border-radius:2px;"><div style="height:100%;width:{pct}%;background:{color};border-radius:2px;"></div></div></div>'

def start_chat(persona):
    st.session_state.persona = persona
    st.session_state.persona_active = True
    intro = f"Hello! I'm {persona['name']}, {persona['age']} years old, working as a {persona['role']} based in {persona['location']}. I've been banking with {persona['bank']} for {persona['loyalty']}. Feel free to ask me anything about my financial habits, lifestyle, or banking experience!"
    st.session_state.messages = [{"role":"persona","content":intro,"evaluation":None}]

def send_message(question, p):
    st.session_state.messages.append({"role":"user","content":question,"evaluation":None})
    with st.spinner(f"{p.get('name','Persona')} is thinking…"):
        try:
            data = call_azure(question)
            response   = data.get("Response") or data.get("response") or data.get("answer") or data.get("output") or json.dumps(data)
            evaluation = data.get("evaluation") or data.get("Evaluation")
            st.session_state.messages.append({"role":"persona","content":response,"evaluation":evaluation})
        except Exception as e:
            st.session_state.messages.append({"role":"persona","content":f"⚠️ Azure error: {e}","evaluation":None})
    st.rerun()

# ── SIDEBAR ──
with st.sidebar:
    st.markdown('<div style="font-family:JetBrains Mono,monospace;font-size:10px;color:#3a5a4a;letter-spacing:3px;padding:16px 0 12px;">● BNPP · PERSONA SIMULATOR</div>', unsafe_allow_html=True)
    st.markdown("---")
    preset_choice = st.selectbox("Select Persona", list(PRESET_PERSONAS.keys()))
    chosen_preset = PRESET_PERSONAS[preset_choice]
    is_custom = chosen_preset is None
    st.markdown("---")
    defaults = chosen_preset if chosen_preset else {
        "name":"","age":35,"gender":"Female","role":"","bank":"BNP Paribas",
        "location":"","loyalty":"","income":"","savings":"","digital":"","risk":"Moderate",
        "traits":[],"completeness":[("Demographics",80,True),("Behavior",50,False),("Preferences",50,False),("Life Events",40,False)]
    }
    name     = st.text_input("Name",           value=defaults["name"],    disabled=not is_custom)
    age      = st.number_input("Age",           value=int(defaults["age"]),min_value=18,max_value=90,disabled=not is_custom)
    gender   = st.selectbox("Gender",           ["Female","Male","Non-binary","Other"], index=["Female","Male","Non-binary","Other"].index(defaults["gender"]) if defaults["gender"] in ["Female","Male","Non-binary","Other"] else 0, disabled=not is_custom)
    role     = st.text_input("Occupation",      value=defaults["role"],    disabled=not is_custom)
    bank     = st.text_input("Bank",            value=defaults["bank"],    disabled=not is_custom)
    location = st.text_input("Location",        value=defaults["location"],disabled=not is_custom)
    loyalty  = st.text_input("Bank loyalty",    value=defaults["loyalty"], disabled=not is_custom)
    income   = st.text_input("Annual income",   value=defaults["income"],  disabled=not is_custom)
    savings  = st.text_input("Savings habit",   value=defaults["savings"], disabled=not is_custom)
    digital  = st.text_input("Digital usage",   value=defaults["digital"], disabled=not is_custom)
    risk_opts = ["Low","Moderate","High (speculative)"]
    risk     = st.selectbox("Risk profile",     risk_opts, index=risk_opts.index(defaults["risk"]) if defaults["risk"] in risk_opts else 1, disabled=not is_custom)
    traits   = [t.strip() for t in st.text_input("Traits (comma-separated)", value="").split(",") if t.strip()] if is_custom else defaults["traits"]
    st.markdown("---")
    persona_name = name.strip() if is_custom else (chosen_preset or {}).get("name","")
    if st.button("▶  Start Interview", disabled=not persona_name):
        start_chat({
            "name":     name     if is_custom else chosen_preset["name"],
            "age":      age      if is_custom else chosen_preset["age"],
            "gender":   gender,
            "role":     role     if is_custom else chosen_preset["role"],
            "bank":     bank     if is_custom else chosen_preset["bank"],
            "location": location if is_custom else chosen_preset["location"],
            "loyalty":  loyalty  if is_custom else chosen_preset["loyalty"],
            "income":   income   if is_custom else chosen_preset["income"],
            "savings":  savings  if is_custom else chosen_preset["savings"],
            "digital":  digital  if is_custom else chosen_preset["digital"],
            "risk":     risk     if is_custom else chosen_preset["risk"],
            "traits":   traits   if is_custom else chosen_preset["traits"],
            "completeness": defaults["completeness"],
        })
        st.rerun()
    if st.session_state.persona_active:
        st.markdown("---")
        if st.button("↺  Reset / Change Persona"):
            st.session_state.messages=[]; st.session_state.persona_active=False; st.session_state.persona={}; st.rerun()

# ── MAIN ──
if not st.session_state.persona_active:
    st.markdown('<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:70vh;text-align:center;gap:20px;"><div style="font-family:JetBrains Mono,monospace;font-size:11px;color:#3a5a4a;letter-spacing:4px;">BNPP · SYNTHETIC PERSONA ENGINE</div><div style="font-size:42px;color:#e8ead0;line-height:1.2;">Persona<br/>Simulator</div><div style="color:#5a7a6a;font-size:15px;max-width:420px;line-height:1.7;">Select a preset persona or build your own in the sidebar, then interview them to gather reliable synthetic marketing insights.</div><div style="font-family:JetBrains Mono,monospace;font-size:11px;color:#2a4a3a;border:1px solid #1a3a2a;padding:8px 20px;border-radius:20px;margin-top:8px;">← Choose a persona in the sidebar to begin</div></div>', unsafe_allow_html=True)
else:
    p = st.session_state.persona
    col_av, col_info, col_score = st.columns([1,2,2])
    with col_av:
        trait_pills = " ".join([f'<span style="background:#0d2a1a;border:1px solid #1a3a2a;color:#5a9a7a;font-size:10px;padding:3px 8px;border-radius:10px;font-family:JetBrains Mono,monospace;display:inline-block;margin:2px;">{t}</span>' for t in p.get("traits",[])])
        st.markdown(f'<div style="text-align:center;padding:16px 8px;"><div style="width:68px;height:68px;border-radius:50%;background:linear-gradient(135deg,#1a3a5c,#0d2a1a);border:2px solid #2a4a3a;margin:0 auto 10px;display:flex;align-items:center;justify-content:center;font-size:26px;color:#7ecfa0;">{p["name"][0].upper()}</div><div style="font-size:20px;color:#e8ead0;">{p["name"]}</div><div style="font-size:11px;color:#5a7a6a;font-family:JetBrains Mono,monospace;margin-top:4px;">{p["age"]} · {p["gender"]}</div><div style="margin-top:10px;">{trait_pills}</div></div>', unsafe_allow_html=True)
    with col_info:
        st.markdown('<div style="color:#3a5a4a;font-size:10px;font-family:JetBrains Mono,monospace;letter-spacing:2px;margin-bottom:10px;">PROFILE</div>', unsafe_allow_html=True)
        for label, key in [("Role","role"),("Bank","bank"),("Location","location"),("Loyalty","loyalty"),("Income","income"),("Savings","savings"),("Digital","digital"),("Risk","risk")]:
            val = p.get(key,"—") or "—"
            st.markdown(f'<div style="margin-bottom:8px;"><span style="color:#3a5a4a;font-size:10px;font-family:JetBrains Mono,monospace;letter-spacing:1px;">{label.upper()}&nbsp;&nbsp;</span><span style="color:#a0b8a8;font-size:13px;">{val}</span></div>', unsafe_allow_html=True)
    with col_score:
        st.markdown('<div style="color:#3a5a4a;font-size:10px;font-family:JetBrains Mono,monospace;letter-spacing:2px;margin-bottom:10px;">COMPLETENESS SCORE</div>', unsafe_allow_html=True)
        for (field,pct,real) in p.get("completeness",[]):
            st.markdown(completeness_bar(field,pct,real), unsafe_allow_html=True)
        st.markdown('<div style="display:flex;gap:14px;margin-top:6px;"><span style="font-size:10px;color:#3a6a5a;font-family:JetBrains Mono,monospace;">● Real data</span><span style="font-size:10px;color:#6a5a2a;font-family:JetBrains Mono,monospace;">◌ Synthetic</span></div>', unsafe_allow_html=True)
    st.markdown('<hr style="border-color:#1e2535;margin:12px 0 16px;">', unsafe_allow_html=True)
    chat_html = ""
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            chat_html += f'<div class="speaker-label" style="text-align:right;">YOU</div><div class="user-msg">{msg["content"]}</div>'
        else:
            chat_html += f'<div class="speaker-label">{p.get("name","PERSONA").upper()} · SIMULATED PERSONA</div><div class="persona-msg">{msg["content"]}{eval_badge(msg.get("evaluation"))}</div>'
    st.markdown(f'<div style="min-height:160px;">{chat_html}</div>', unsafe_allow_html=True)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    col_in, col_btn = st.columns([5,1])
    with col_in:
        user_input = st.text_input("", placeholder=f"Ask {p.get('name','the persona')} a question…", label_visibility="collapsed", key="chat_input")
    with col_btn:
        if st.button("Send ↑") and user_input.strip():
            send_message(user_input.strip(), p)
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.markdown('<div style="color:#3a5a4a;font-size:10px;font-family:JetBrains Mono,monospace;letter-spacing:2px;margin-bottom:8px;">SUGGESTED QUESTIONS</div>', unsafe_allow_html=True)
    cols = st.columns(3)
    for i, q in enumerate(SUGGESTED_QUESTIONS):
        with cols[i%3]:
            if st.button(q, key=f"sugg_{i}"):
                send_message(q, p)
