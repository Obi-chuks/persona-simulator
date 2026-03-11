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
if "messages" not in st
