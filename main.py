import streamlit as st
import random
from google import genai
from google.genai import types

# --- 1. App Layout Configuration ---
st.set_page_config(page_title="RPG Lore Forge & Sheet Creator", page_icon="📜", layout="wide")

st.title("📜 The RPG Character Forge & Sheet Creator")
st.subheader("Assign stats, describe your traits, and generate an epic backstory with a printable character sheet.")

# --- 2. Pull API Key Securely from Streamlit Secrets ---
try:
    google_api_key = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("🔑 Streamlit Secret missing! Please add 'GEMINI_API_KEY' to your Streamlit App secrets vault.")
    st.stop()

# --- 3. Sidebar: Quick Dice Roller ---
st.sidebar.header("🎲 Quick Dice Roller")
dice_type = st.sidebar.selectbox("Choose a Die", ["d4", "d6", "d8", "d10", "d12", "d20", "d100"])
if st.sidebar.button("Roll Sidebar Die"):
    sides = int(dice_type[1:])
    roll = random.randint(1, sides)
    st.sidebar.success(f"Rolled a {dice_type}: **{roll}**")

# --- 4. Main Layout: Two Working Columns ---
input_col, sheet_col = st.columns([1, 1.2])

# Keep the data saved on screen between interactions
if 'generated_backstory' not in st.session_state:
    st.session_state.generated_backstory = None

with input_col:
    st.header("👤 Character Identity")
    char_name = st.text_input("Character Name", placeholder="e.g., Lyra Swiftwind")
    char_race = st.selectbox("Race / Ancestry", ["Human", "Elf", "Dwarf", "Halfling", "Orc", "Tiefling", "Dragonborn"])
    char_class = st.selectbox("Class", ["Fighter", "Wizard", "Rogue", "Cleric", "Paladin", "Ranger", "Barbarian", "Bard", "Monk"])
    char_alignment = st.selectbox("Alignment", ["Lawful Good", "Neutral Good", "Chaotic Good", "Lawful Neutral", "True Neutral", "Chaotic Neutral", "Lawful Evil", "Neutral Evil", "Chaotic Evil"])
    
    st.markdown("---")
    st.header("🎨 Appearance & Equipment Notes")
    user_visual_desc = st.text_area(
        "Describe your appearance, key gear, or distinct features:", 
        placeholder="e.g., Emerald green eyes, cloaked in a tattered midnight-blue velvet cape, carries twin silver daggers and an old leather-bound journal."
    )
    
    st.markdown("



