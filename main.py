import streamlit as st
import random
import base64
from io import BytesIO
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel
from google import genai


# --- App Layout Configuration ---
st.set_page_config(page_title="Ultimate Character Forge", page_icon="⚔️", layout="wide")


st.title("⚔️ The Ultimate RPG Character Forge")
st.subheader("Craft your hero's soul, stats, and a custom anime visual, forged by AI.")


st.sidebar.markdown("---")
st.sidebar.header("🎲 Quick Dice Roller")
dice_type = st.sidebar.selectbox("Choose a Die", ["d4", "d6", "d8", "d10", "d12", "d20", "d100"])
if st.sidebar.button("Roll Sidebar Die"):
    sides = int(dice_type[1:])
    roll = random.randint(1, sides)
    st.sidebar.success(f"Rolled a {dice_type}: **{roll}**")


# --- Main Layout: Two Columns ---
# We use two large columns to split inputs from the final character sheet view.
input_col, sheet_col = st.columns([1.2, 1.8])


# Initialize state to store generated content
if 'generated_backstory' not in st.session_state:
    st.session_state.generated_backstory = None
if 'generated_image_b64' not in st.session_state:
    st.session_state.generated_image_b64 = None


with input_col:
    st.header("👤 Character Details")
    
    char_name = st.text_input("Character Name", placeholder="e.g., Elara Sunweaver")
    char_race = st.selectbox("Race", ["Human", "High Elf", "Dwarf", "Halfling", "Orc", "Tiefling", "Dragonborn"])
    char_class = st.selectbox("Class", ["Paladin", "Wizard", "Rogue", "Cleric", "Fighter", "Ranger", "Monk"])
    
    st.markdown("---")
    st.header("🎨 Physical Description (AI-Ready)")
    st.write("Type a concise visual description for the image generator.")
    user_visual_desc = st.text_area(
        "Character Appearance", 
        placeholder="A woman with golden eyes, long silver braided hair, wearing pristine red and gold plate armor and wielding a gleaming longsword. Maintain an anime style."
    )
    
    st.markdown("---")
    st.header("📊 Ability Scores (3-20)")
    str_score = st.slider("Strength (STR)", 3, 20, 10)
    dex_score = st.slider("Dexterity (DEX)", 3, 20, 10)
    con_score = st.slider("Constitution (CON)", 3, 20, 10)
    int_score = st.slider("Intelligence (INT)", 3, 20, 10)
    wis_score = st.slider("Wisdom (WIS)", 3, 20, 10)
    cha_score = st.slider("Charisma (CHA)", 3, 20, 10)


    # Dice roller integration (still useful in the input flow)
    st.markdown("---")
    st.header("🎲 Stat Check Roller")
    stat_to_roll = st.selectbox("Stat to Roll", ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"])
    
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
        if d20_roll == 20: st.balloons(); st.success("CRITICAL SUCCESS! 🌟")
        elif d20_roll == 1: st.error("CRITICAL FAILURE! 💀")


# --- Function to synthesize a mega-prompt for the image generator ---
# This is key: it merges user visual preference with story lore.
def synthesize_image_prompt(base_desc, story_text):
    # This prompt asks the Gemini model to *distill* the backstory into visual keywords.
    # It focuses on capturing character "essence" and "mood."
    gemini_client = genai.Client(api_key=google_api_key)
    
    context_instruction = (
        "You are an expert visual prompt engineer for image generation AI. "
        "Your task is to synthesize the provided physical description (the user's vision) "
        "with key contextual information distilled from the provided character backstory. "
        "Maintain the core description, but add descriptive keywords or atmosphere "
        "that reflects the character's core motivations or tragedies found in the backstory. "
        "DO NOT add extensive new text; focus on powerful keywords and mood enhancement. "
        "Crucially, the user requested an ANIME STYLE. Integrate this as a hard requirement."
    )
    
    prompt_to_distill = (
        f"User's Physical Description: '{base_desc}'\n"
        f"Full Backstory Context: '{story_text}'"
    )
    
    # We ask Gemini to generate the synthesis
    response = gemini_client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt_to_distill,
        config={"system_instruction": context_instruction}
    )
    
    # The output is the mega-prompt: base description + distilled mood
    return response.text.strip()


# --- Execution Logic (Generate Everything at once) ---
with sheet_col:
    if st.button("✨ Complete Character Creation (Lore, Stats, and Custom Anime Visual)"):
        # Validate configuration
        if not google_api_key or not project_id or not location:
            st.error("Please provide both a Gemini API Key, GCP Project ID, and Location in the sidebar to summon the full forge.")
            st.stop()
            
        if not char_name:
            st.warning("Your hero needs a name before their destiny can be forged!")
            st.stop()
            
        if not user_visual_desc:
            st.warning("Please provide a concise appearance description for the image generator.")
            st.stop()
            
        # We start by initializing both clients
        vertexai.init(project=project_id, location=location)
        image_client = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")
        
        with st.spinner("Weaving the threads of fate, forging the form, and generating the anime visual..."):
            try:
                # 1. GENERATE BACKSTORY (using stats)
                gemini_client = genai.Client(api_key=google_api_key)
                
                system_instruction = (
                    "You are an expert fantasy writer and RPG Game Master. "
                    "Write a compelling, concise 3-paragraph character backstory "
                    "based on the name, race, class, and numerical stats provided. "
                    "Ensure the backstory accurately reflects high or low stats."
                )
                
                character_details = (
                    f"Name: {char_name}\n"
                    f"Race: {char_race}\n"
                    f"Class: {char_class}\n"
                    f"Stats: STR {str_score}, DEX {dex_score}, CON {con_score}, "
                    f"INT {int_score}, WIS {wis_score}, CHA {cha_score}"
                )
                
                backstory_response = gemini_client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=character_details,
                    config={"system_instruction": system_instruction}
                )
                st.session_state.generated_backstory = backstory_response.text


                # 2. SYNTHESIZE VISUAL PROMPT (Base description + distilled backstory context)
                synthesized_prompt = synthesize_image_prompt(user_visual_desc, st.session_state.generated_backstory)
                
                # Special debugging check: visualize the mega-prompt
                # st.write(f"*Internal mega-prompt used for generation:* {synthesized_prompt}")


                # 3. GENERATE THE ANIME IMAGE (using the mega-prompt)
                images = image_client.generate_images(
                    prompt=synthesized_prompt,
                    number_of_images=1,
                    # Optional parameters to enhance the anime feel
                    language="en",
                    add_watermark=False,
                    seed=random.randint(0, 10**9), # Add randomness
                )
                
                # Convert the generated image to base64 for Streamlit display
                image_byte_arr = BytesIO()
                images[0].save(image_byte_arr, format='PNG')
                st.session_state.generated_image_b64 = base64.b64encode(image_byte_arr.getvalue()).decode('utf-8')
                
                st.success(f"Forced complete: Lore, Stats, and Custom Anime Visual for {char_name} are ready.")
                
            except Exception as e:
                st.error(f"The magic failed during the final forging phase: {e}")


# --- Display Character Sheet ---
    if st.session_state.generated_backstory and st.session_state.generated_image_b64:
        st.header(f"📜 Character Portfolio: {char_name}")
        
        # We use nested columns within the main right column to display content side-by-side
        final_sheet_col1, final_sheet_col2 = st.columns([1, 1.2])
        
        with final_sheet_col1:
            st.subheader("Stats & Visual")
            
            # Ability Score Summary Table (Clean visualization)
            stat_summary = {
                "STR": str_score, "DEX": dex_score, "CON": con_score,
                "INT": int_score, "WIS": wis_score, "CHA": cha_score
            }
            # We display modifiers next to scores
            st.dataframe(
                data={stat: [score, f"({(score - 10) // 2: +d})"] for stat, score in stat_summary.items()},
                columns=["Score", "Modifier"],
                width=300,
                hide_index=True
            )
            
            # Display the synthesized anime image
            image_data = base64.b64decode(st.session_state.generated_image_b64)
            st.image(image_data, caption=f"AI-Generated Anime Visual for {char_name}", use_container_width=True)
            
        with final_sheet_col2:
            st.subheader("Woven Destiny (Backstory)")
            # Use expander or markdown area for backstory
            with st.expander("Expand Backstory Lore", expanded=True):
                st.markdown(st.session_state.generated_backstory)
