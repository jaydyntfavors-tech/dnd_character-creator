  import random
import streamlit as st
from google import genai


# --- App Layout Configuration ---
st.set_page_config(page_title="RPG Character Creator", page_icon="🎲", layout="wide")


st.title("⚔️ Tabletop Character Creator & Dice Roller")
st.subheader("Build your adventurer, roll the dice, and let AI weave your lore.")


# --- Sidebar: API Configuration & Quick Roller ---
st.sidebar.header("⚙️ Configuration")
api_key = st.sidebar.text_input("Enter Gemini API Key:", type="password")


st.sidebar.markdown("---")
st.sidebar.header("🎲 Quick Dice Roller")
dice_type = st.sidebar.selectbox("Choose a Die", ["d4", "d6", "d8", "d10", "d12", "d20", "d100"])
if st.sidebar.button("Roll Sidebar Die"):
    sides = int(dice_type[1:])
    roll = random.randint(1, sides)
    st.sidebar.success(f"Rolled a {dice_type}: **{roll}**")


# --- Main Layout: Two Columns ---
col1, col2 = st.columns([1, 1])


with col1:
    st.header("👤 Character Identity")
    char_name = st.text_input("Character Name", placeholder="e.g., Thorgar Ironbreaker")
    char_race = st.selectbox("Race / Ancestry", ["Human", "Elf", "Dwarf", "Halfling", "Orc", "Tiefling", "Dragonborn"])
    char_class = st.selectbox("Class", ["Warrior", "Mage", "Rogue", "Cleric", "Paladin", "Ranger", "Barbarian"])
    
    st.markdown("---")
    st.header("📊 Ability Scores")
    
    # Standard 6 D&D Ability Scores
    str_score = st.slider("Strength (STR)", 3, 20, 10)
    dex_score = st.slider("Dexterity (DEX)", 3, 20, 10)
    con_score = st.slider("Constitution (CON)", 3, 20, 10)
    int_score = st.slider("Intelligence (INT)", 3, 20, 10)
    wis_score = st.slider("Wisdom (WIS)", 3, 20, 10)
    cha_score = st.slider("Charisma (CHA)", 3, 20, 10)


with col2:
    st.header("⚔️ Stat Checks & Saving Throws")
    st.write("Select a stat to roll a standard d20 check with a mock modifier.")
    
    stat_to_roll = st.selectbox("Choose Stat to Roll", ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"])
    
    # Map selected stat to the slider values
    stat_mapping = {
        "Strength": str_score, "Dexterity": dex_score, "Constitution": con_score,
        "Intelligence": int_score, "Wisdom": wis_score, "Charisma": cha_score
    }
    
    if st.button("🎲 Roll d20 Check"):
        score = stat_mapping[stat_to_roll]
        # Calculate standard D&D modifier: (Score - 10) // 2
        modifier = (score - 10) // 2
        d20_roll = random.randint(1, 20)
        total = d20_roll + modifier
        
        st.info(f"**Roll Result:** d20 ({d20_roll}) + Modifier ({modifier: +d}) = **{total}**")
        if d20_roll == 20:
            st.balloons()
            st.success("CRITICAL SUCCESS! 🌟")
        elif d20_roll == 1:
            st.error("CRITICAL FAILURE! 💀")


    st.markdown("---")
    st.header("🧙‍♂️ AI Backstory Generator")
    st.write("Click below to have the GenAI analyze your stats and write a unique character origin story.")
    
    if st.button("✨ Conjure Backstory"):
        if not api_key:
            st.error("Please provide a Gemini API key in the sidebar to summon the Lore Weaver.")
        elif not char_name:
            st.warning("Your hero needs a name before their story can be written!")
        else:
            with st.spinner("Weaving the threads of fate..."):
                try:
                    # Initialize the Google GenAI client
                    client = genai.Client(api_key=api_key)
                    
                    system_instruction = (
                        "You are an expert fantasy writer and RPG Game Master. "
                        "Your job is to write a compelling, concise 3-paragraph character backstory "
                        "based on the name, race, class, and numerical stats provided. "
                        "Ensure the backstory accurately reflects high or low stats (e.g., if Strength is 18, "
                        "they are physically imposing; if Intelligence is 5, they struggle with book-learning)."
                    )
                    
                    character_details = (
                        f"Name: {char_name}\n"
                        f"Race: {char_race}\n"
                        f"Class: {char_class}\n"
                        f"Stats: STR {str_score}, DEX {dex_score}, CON {con_score}, "
                        f"INT {int_score}, WIS {wis_score}, CHA {cha_score}"
                    )
                    
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=character_details,
                        config={"system_instruction": system_instruction}
                    )
                    
                    st.success(f"📜 The Chronicles of {char_name}")
