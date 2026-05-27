import streamlit as str
import random
from google import genai
from google.genai import types

# --- 1. App Layout Configuration ---
st.set_page_config(page_title="Ultimate Character Forge", page_icon="⚔️", layout="wide")

st.title("⚔️ The Ultimate RPG Character Forge")
st.subheader("Craft your hero's soul, stats, and a custom anime visual, forged by AI.")

# --- 2. Pull API Key Securely from Streamlit Secrets ---
# Ensure you have GEMINI_API_KEY saved in your Streamlit App Dashboard Settings!
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

# --- 4. Main Layout: Two Large Working Columns ---
input_col, sheet_col = st.columns([1.2, 1.8])

# Maintain persistence for generated content across button clicks
if 'generated_backstory' not in st.session_state:
    st.session_state.generated_backstory = None
if 'generated_image_obj' not in st.session_state:
    st.session_state.generated_image_obj = None

with input_col:
    st.header("👤 Character Details")
    char_name = st.text_input("Character Name", placeholder="e.g., Elara Sunweaver")
    char_race = st.selectbox("Race", ["Human", "High Elf", "Dwarf", "Halfling", "Orc", "Tiefling", "Dragonborn"])
    char_class = st.selectbox("Class", ["Paladin", "Wizard", "Rogue", "Cleric", "Fighter", "Ranger", "Monk"])
    
    st.markdown("---")
    st.header("🎨 Physical Description & Visual Keynotes")
    st.write("Describe your character's physical traits. The AI will cross-reference this description with your backstory details.")
    user_visual_desc = st.text_area(
        "Character Appearance", 
        placeholder="e.g., A warrior with short silver hair, serious gold eyes, wearing worn dark iron plate armor, holding a broken claymore."
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

# --- 5. Background Engine Context Compiler ---
def synthesize_image_prompt(client, base_desc, story_text):
    """Uses Gemini 2.5 Flash to synthesize the user's explicit physical choices with narrative lore details."""
    context_instruction = (
        "You are an expert visual prompt engineer for an image generation AI model. "
        "Your task is to merge the user's physical character description with core themes, "
        "mood, and dynamic elements extracted from their backstory text. "
        "Focus on creating a unified, atmospheric artistic description. "
        "CRITICAL REQUIREMENT: The final output must enforce a modern, high-quality anime illustration style."
    )
    
    prompt_to_distill = (
        f"User Appearance Request: '{base_desc}'\n"
        f"Backstory Context: '{story_text}'"
    )
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt_to_distill,
        config=types.GenerateContentConfig(system_instruction=context_instruction)
    )
    return response.text.strip()

# --- 6. Execution & Portfolio Display ---
with sheet_col:
    if st.button("✨ Complete Character Creation (Lore, Stats, and Custom Anime Visual)"):
        if not char_name:
            st.warning("Your hero needs a name before their destiny can be forged!")
            st.stop()
            
        if not user_visual_desc:
            st.warning("Please provide a physical appearance description to help the image generator.")
            st.stop()
            
        with st.spinner("Weaving lore, aligning stars, and rendering your anime character portal..."):
            try:
                # Initialize unified Gemini client
                client = genai.Client(api_key=google_api_key)
                
                # Step A: Generate Backstory Narrative
                system_instruction = (
                    "You are an expert fantasy author and RPG Game Master. "
                    "Write an epic, cohesive 3-paragraph character origin story "
                    "based on the name, race, class, and statistics provided. "
                    "Ensure high stats translate to achievements and low stats reveal clear physical or developmental traits."
                )
                
                character_data_packet = (
                    f"Name: {char_name}\nRace: {char_race}\nClass: {char_class}\n"
                    f"Attributes: STR {str_score}, DEX {dex_score}, CON {con_score}, "
                    f"INT {int_score}, WIS {wis_score}, CHA {cha_score}"
                )
                
                backstory_response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=character_data_packet,
                    config=types.GenerateContentConfig(system_instruction=system_instruction)
                )
                st.session_state.generated_backstory = backstory_response.text

                # Step B: Synthesize Custom Visual Prompt
                mega_prompt = synthesize_image_prompt(client, user_visual_desc, st.session_state.generated_backstory)

                # Step C: Generate Anime Artwork using Imagen 3 via unified client
                image_response = client.models.generate_images(
                    model='imagen-3.0-generate-002',
                    prompt=mega_prompt,
                    config=types.GenerateImagesConfig(
                        number_of_images=1,
                        aspect_ratio="1:1",
                        output_mime_type="image/png"
                    )
                )
                
                # Extract the PIL image directly out of response wrappers
                st.session_state.generated_image_obj = image_response.generated_images[0].image
                st.success(f"Character Generation Complete! Meet {char_name}.")

            except Exception as e:
                st.error(f"The magic spell backfired: {e}")

    # Display Rendered Character Sheet Screen if data exists
    if st.session_state.generated_backstory and st.session_state.generated_image_obj:
        st.header(f"📜 Character Record Portfolio: {char_name}")
        st.markdown("---")
        
        final_sheet_col1, final_sheet_col2 = st.columns([1, 1.2])
        
        with final_sheet_col1:
            st.subheader("🛡️ Attributes & Visual Frame")
            
            # Print a neat dataframe tracking baseline metrics
            stat_summary = {
                "STR": str_score, "DEX": dex_score, "CON": con_score,
                "INT": int_score, "WIS": wis_score, "CHA": cha_score
            }
            st.dataframe(
                data={stat: [score, f"({(score - 10) // 2: +d})"] for stat, score in stat_summary.items()},
                columns=["Score", "Modifier"],
                width=300,
                hide_index=True
            )
            
            # Directly pass PIL image wrapper straight into st.image
            st.image(st.session_state.generated_image_obj, caption=f"Anime Avatar - {char_name} ({char_race} {char_class})", use_container_width=True)
            
        with final_sheet_col2:
            st.subheader("📖 Chronicles of Destiny")
            with st.expander("Read Origin Backstory", expanded=True):
                st.markdown(st.session_state.generated_backstory)

            with st.expander("Expand Backstory Lore", expanded=True):
                st.markdown(st.session_state.generated_backstory)
