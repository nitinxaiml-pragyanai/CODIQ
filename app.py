import streamlit as st
import io
import zipfile
import re
import time
from groq import Groq

# ==========================================
# 1. CONFIGURATION & CODIQ OMEGA THEME
# ==========================================
st.set_page_config(
    page_title="SAMRION CODIQ",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# === THE ULTRA-MODERN CSS PATCH ===
st.markdown("""
<style>
    /* 1. GLOBAL FONT & COLOR */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    .stApp, p, h1, h2, h3, h4, h5, label, span, div, li, button, small {
        font-family: 'Inter', sans-serif !important;
        color: #ffffff !important;
    }

    /* 2. BACKGROUND: DEEP ROYAL UNIVERSE */
    .stApp {
        background: radial-gradient(circle at 10% 20%, #001540 0%, #000000 90%);
        background-attachment: fixed;
    }

    /* 3. REMOVE THE WHITE HEADER (GITHUB BAR) */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    .stApp > header {
        display: none !important;
    }

    /* 4. OVAL TABS (THE PILL DESIGN) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        background-color: rgba(0, 0, 0, 0.4);
        padding: 10px 15px;
        border-radius: 50px; /* Fully Oval Container */
        border: 1px solid rgba(255, 255, 255, 0.1);
        width: fit-content;
        margin: 0 auto; /* Center the tabs */
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        border-radius: 50px !important; /* Oval Buttons */
        padding: 0 30px;
        background-color: transparent;
        border: 1px solid rgba(255,255,255,0.1);
        color: white;
        font-weight: 600;
        transition: 0.3s;
    }
    
    /* Active Tab Style (Glowing Red/Pink) */
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #D60000, #ff4d4d) !important;
        border: none;
        color: white !important;
        box-shadow: 0 0 15px rgba(214, 0, 0, 0.5);
    }

    /* 5. GLASS INPUTS */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        background-color: rgba(0, 20, 60, 0.4) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(214, 0, 0, 0.5);
        color: white !important;
        border-radius: 15px;
    }
    .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
        border-color: #ff0000;
        box-shadow: 0 0 15px rgba(255, 0, 0, 0.2);
    }

    /* 6. NEON BUTTONS */
    div.stButton > button {
        background: linear-gradient(135deg, #D60000 0%, #8a0000 100%) !important;
        border: none !important;
        color: white !important;
        font-weight: 800 !important;
        border-radius: 50px !important; /* Oval Buttons */
        padding: 0.75rem 2rem;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 25px rgba(255, 0, 0, 0.6);
    }

    /* FOOTER */
    .footer {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background: rgba(0, 0, 0, 0.9);
        backdrop-filter: blur(5px);
        border-top: 1px solid #D60000;
        color: #888; text-align: center;
        padding: 10px; font-size: 10px; letter-spacing: 2px; z-index: 999;
        text-transform: uppercase;
    }
    
    /* Remove Sidebar completely */
    [data-testid="stSidebar"] {display: none;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. INTELLIGENCE CORE (GROQ ENGINE)
# ==========================================
def get_api_key():
    try: return st.secrets["GROQ_API_KEY"]
    except: return None

def generate_code_groq(client, prompt, mode="genesis"):
    """
    The Brain: Llama 3.3 70B (via Groq)
    """
    system_prompt = """
    You are CODIQ, the Supreme AI Architect.
    
    PROTOCOL:
    1. ANALYZE: Determine if the user needs a single script or a full project.
    2. SINGLE FILE: Output Python code.
    3. MULTI-FILE: Split code using XML tags: <file name="filename.ext"> ...content... </file>
    
    CRITICAL RULE: Always include 'requirements.txt' if libraries are used.
    """

    if mode == "genesis":
        user_message = f"ARCHITECT THIS SYSTEM: {prompt}"
    else:
        user_message = f"REFACTOR & FIX THIS CODE: {prompt}"

    # Thinking Effect
    with st.status("🧠 CODIQ NEURAL LINK ACTIVE...", expanded=True) as status:
        st.write("🔌 Establishing Uplink...")
        
        # === UPGRADED MODEL HERE ===
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.1,
            max_tokens=7000,
        )
        
        st.write("⚡ Compiling Logic Gates...")
        time.sleep(0.5)
        st.write("📦 Packaging Modules...")
        status.update(label="ARCHITECTING COMPLETE", state="complete", expanded=False)
        
    return completion.choices[0].message.content

def process_response(raw_text):
    """Parses Llama's output to extract files"""
    pattern = r'<file name="(.*?)">(.*?)</file>'
    matches = re.findall(pattern, raw_text, re.DOTALL)
    
    if len(matches) > 0:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for filename, content in matches:
                zf.writestr(filename, content.strip())
        zip_buffer.seek(0)
        return "MULTI", zip_buffer, matches
    else:
        return "SINGLE", raw_text, "main.py"

# ==========================================
# 3. INTERFACE LAYER
# ==========================================
st.title("🧠 SAMRION CODIQ")
st.markdown("### ULTIMATE INFRASTRUCTURE ARCHITECT")

# TABS (Ovals)
tab_gen, tab_fix = st.tabs(["✨ GENESIS PROTOCOL", "🚑 SURGEON PROTOCOL"])

# === TAB 1: GENESIS ===
with tab_gen:
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.markdown("#### 📡 INPUT TRANSMISSION")
        idea_prompt = st.text_area("Define System Parameters...", height=300, 
                                   placeholder="e.g. 'Build a Snake Game in Python with a scoreboard.'")
        
        if st.button("🚀 INITIATE GENERATION", key="btn_gen", use_container_width=True):
            api_key = get_api_key()
            if not api_key:
                st.error("⚠️ CRITICAL: GROQ_API_KEY MISSING IN SECRETS")
            elif not idea_prompt:
                st.toast("⚠️ DATA MISSING", icon="🚫")
            else:
                client = Groq(api_key=api_key)
                try:
                    raw_result = generate_code_groq(client, idea_prompt, mode="genesis")
                    mode, data, extra = process_response(raw_result)
                    
                    st.session_state['res_mode'] = mode
                    st.session_state['res_data'] = data
                    st.session_state['res_extra'] = extra
                    st.toast("✅ GENERATION COMPLETE", icon="⚡")
                except Exception as e:
                    st.error(f"SYSTEM FAILURE: {e}")

    with c2:
        st.markdown("#### 📦 OUTPUT CONSOLE")
        if 'res_mode' in st.session_state:
            mode = st.session_state['res_mode']
            data = st.session_state['res_data']
            extra = st.session_state['res_extra']
            
            if mode == "MULTI":
                st.success(f"📂 **PROJECT BUNDLE READY** ({len(extra)} Files)")
                st.download_button(
                    label="⬇️ DOWNLOAD REPO (.ZIP)",
                    data=data,
                    file_name="Samrion_Project.zip",
                    mime="application/zip",
                    use_container_width=True
                )
                
                for fname, fcontent in extra:
                    lang = "python"
                    if fname.endswith(".html"): lang = "html"
                    if fname.endswith(".css"): lang = "css"
                    if fname.endswith(".js"): lang = "javascript"
                    
                    with st.expander(f"📄 {fname}"):
                        st.code(fcontent, language=lang)
            else:
                st.success("📋 **SINGLE SCRIPT GENERATED**")
                st.code(data, language='python')

# === TAB 2: SURGEON ===
with tab_fix:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 🩺 CODE REPAIR & OPTIMIZATION")
    broken_code = st.text_area("Inject Broken Kernel...", height=200)
    
    if st.button("🚑 REFACTOR & HEAL", key="btn_fix", use_container_width=True):
         api_key = get_api_key()
         if not api_key:
            st.error("⚠️ GROQ KEY MISSING")
         else:
            client = Groq(api_key=api_key)
            try:
                fix_raw = generate_code_groq(client, broken_code, mode="fix")
                mode, data, extra = process_response(fix_raw)
                
                if mode == "MULTI":
                    st.toast("✅ REPAIRED", icon="🛠️")
                    st.download_button("⬇️ DOWNLOAD FIXED ZIP", data, "Fixed_Project.zip", "application/zip", use_container_width=True)
                    for fname, fcontent in extra:
                        with st.expander(f"📄 {fname}"):
                            st.code(fcontent)
                else:
                    st.toast("✅ REPAIRED", icon="✨")
                    st.code(data, language='python')
            except Exception as e:
                st.error(f"ERROR: {e}")

# FOOTER
st.markdown("""
<div class="footer">
    POWERED BY SAMRION INTELLIGENCE | FOUNDER: NITIN RAJ | SAMRION AI INFRASTRUCTURE
</div>
""", unsafe_allow_html=True)
