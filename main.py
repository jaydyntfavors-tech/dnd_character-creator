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
    
    st.markdown("---")
    st.header("📊 Ability Scores (3-20)")
    str_score = st.slider("Strength (STR)", 3, 20, 10)
    dex_score = st.slider("Dexterity (DEX)", 3, 20, 10)
    con_score = st.slider("Constitution (CON)", 3, 20, 10)
    int_score = st.slider("Intelligence (INT)", 3, 20, 10)
    wis_score = st.slider("Wisdom (WIS)", 3, 20, 10)
    cha_score = st.slider("Charisma (CHA)", 3, 20, 10)

    st.markdown("---")
    st.header("🎲 Instant Stat Check Roller")
    stat_to_roll = st.selectbox("Select Stat for Check", ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"])
    
    if st.button("🎲 Roll d20 Check"):
        stat_mapping = {
            "Strength": str_score, "Dexterity": dex_score, "Constitution": con_score,
            "Intelligence": int_score, "Wisdom": wis_score, "Charisma": cha_score
        }
        score = stat_mapping[stat_to_roll]
        modifier = (score - 10) // 2
        d20_roll = random.randint(1, 20)
        total = d20_roll + modifier
        
        st.info(f"**Roll Result:** d20 ({d20_roll}) + Modifier ({modifier: +d}) = **{total}**")
        if d20_roll == 20: 
            st.balloons()
            st.success("CRITICAL SUCCESS! 🌟")
        elif d20_roll == 1: 
            st.error("CRITICAL FAILURE! 💀")

# --- 5. Backstory Generator & Sheet Rendering Engine ---
with sheet_col:
    st.header("✨ The Grand Chronicle")
    if st.button("📜 Forge Character & Backstory"):
        if not char_name:
            st.warning("Your hero needs a name before their legend can be written!")
            st.stop()
            
        with st.spinner("Consulting the ancient archives..."):
            try:
                # Initialize standard Gemini client
                client = genai.Client(api_key=google_api_key)
                
                system_instruction = (
                    "You are an expert fantasy novelist and experienced tabletop RPG Game Master. "
                    "Write a highly engaging, deep, 4-paragraph character origin story based on the details provided. "
                    "Paragraph 1: Early life and childhood, incorporating their race/ancestry environment.\n"
                    "Paragraph 2: How they became their chosen Class and how their highest ability scores helped them.\n"
                    "Paragraph 3: A turning point, trial, or tragedy that explains their physical appearance, clothing choices, or distinct traits.\n"
                    "Paragraph 4: Their current motivation for setting out into the world on a dangerous campaign adventure.\n"
                    "Make sure high stats reflect outstanding feats, and low stats reflect real struggles or weaknesses."
                )
                
                character_data = (
                    f"Name: {char_name}\n"
                    f"Race: {char_race}\n"
                    f"Class: {char_class}\n"
                    f"Alignment: {char_alignment}\n"
                    f"Physical Details: {user_visual_desc if user_visual_desc else 'Standard appearance'}\n"
                    f"Stats: STR {str_score}, DEX {dex_score}, CON {con_score}, INT {int_score}, WIS {wis_score}, CHA {cha_score}"
                )
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=character_data,
                    config=types.GenerateContentConfig(system_instruction=system_instruction)
                )
                
                st.session_state.generated_backstory = response.text
                st.success(f"The profile for {char_name} has been fully forged!")

            except Exception as e:
                st.error(f"The chronicle spell failed: {e}")

    # --- Display Printable Character Sheet Section ---
    if st.session_state.generated_backstory:
        st.markdown("---")
        
        # Calculate modifiers to print directly on the sheet
        def get_mod(score):
            mod = (score - 10) // 2
            return f"+{mod}" if mod >= 0 else f"{mod}"

        # Traditional print action button using a tiny HTML/JS component
        st.write("🖨️ Need a physical copy?")
        st.components.v1.html(
            """
            <button onclick="window.print()" style="
                background-color: #FF4B4B; 
                color: white; 
                border: none; 
                padding: 8px 16px; 
                border-radius: 4px; 
                cursor: pointer;
                font-weight: bold;">
                Print Character Sheet
            </button>
            """,
            height=50,
        )
            
        # Refactored Markdown string block to prevent breaking the grid compiler
        st.markdown(f"""
# 🛡️ CHARACTER LOG RECORD

**NAME:** {char_name} | **RACE:** {char_race} | **CLASS:** {char_class} | **ALIGNMENT:** {char_alignment}

---

### 📊 PRIMARY ATTRIBUTE SCORES

| Attribute | Core Score | Modifier |
| :--- | :---: | :---: |
| 💪 **STRENGTH (STR)** | {str_score} | {get_mod(str_score)} |
| 🏃‍♂️ **DEXTERITY (DEX)** | {dex_score} | {get_mod(dex_score)} |
| 🛡️ **CONSTITUTION (CON)** | {con_score} | {get_mod(con_score)} |
| 🧠 **INTELLIGENCE (INT)** | {int_score} | {get_mod(int_score)} |
| 🦉 **WISDOM (WIS)** | {wis_score} | {get_mod(wis_score)} |
| ✨ **CHARISMA (CHA)** | {cha_score} | {get_mod(cha_score)} |

---

### 📝 VISUAL DESCRIPTION & INVENTORY NOTES
*{user_visual_desc if user_visual_desc else 'No distinct appearance notes provided.'}*

---

### 📖 CHRONICLES OF ORIGIN (BACKSTORY)
{st.session_state.generated_backstory}

---
*Generated via Ultimate RPG Character Forge*
""")
