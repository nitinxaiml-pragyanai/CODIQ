import streamlit as st
import anthropic
import zipfile
import io
import re
import time

# ==========================================
# 1. CONFIGURATION & ROYAL THEME
# ==========================================
st.set_page_config(
    page_title="SAMRION CODIQ",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# === THE ROYAL BLUE & RED CSS PATCH (CLEAN MODE) ===
st.markdown("""
<style>
    /* GLOBAL FONT & COLOR */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    .stApp, p, h1, h2, h3, h4, h5, label, span, div, li, button, small {
        font-family: 'Inter', sans-serif !important;
        color: #ffffff !important;
    }

    /* BACKGROUND: DEEP ROYAL UNIVERSE */
    .stApp {
        background: radial-gradient(circle at 10% 20%, #001540 0%, #000000 90%);
        background-attachment: fixed;
    }

    /* GLASSMOPRHISM INPUTS */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        background-color: rgba(0, 20, 60, 0.4) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(214, 0, 0, 0.5);
        color: white !important;
        border-radius: 12px;
        transition: border 0.3s ease;
    }
    .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
        border: 1px solid #ff0000;
        box-shadow: 0 0 15px rgba(255, 0, 0, 0.2);
    }

    /* LEGENDARY BUTTONS (NEON RED GLOW) */
    div.stButton > button {
        background: linear-gradient(135deg, #D60000 0%, #8a0000 100%) !important;
        border: 1px solid #ff4d4d !important;
        color: white !important;
        font-weight: 800 !important;
        letter-spacing: 1px;
        border-radius: 8px !important;
        padding: 0.75rem 1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(214, 0, 0, 0.3);
    }
    div.stButton > button:hover {
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 0 30px rgba(255, 0, 0, 0.6);
        background: linear-gradient(135deg, #ff1a1a 0%, #b30000 100%) !important;
    }
    
    /* CUSTOM TABS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px; background-color: rgba(0,0,0,0.3); padding: 10px; border-radius: 15px; border: 1px solid #333;
    }
    .stTabs [aria-selected="true"] {
        background-color: #D60000 !important; color: white !important;
    }

    /* REMOVE SIDEBAR COMPLETELY */
    [data-testid="stSidebar"] { display: none; }
    
    /* FOOTER */
    .footer {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background: rgba(0, 0, 0, 0.9); backdrop-filter: blur(5px);
        border-top: 1px solid #D60000;
        color: #888; text-align: center; padding: 10px;
        font-size: 10px; letter-spacing: 2px; z-index: 999;
        text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. INTELLIGENCE CORE
# ==========================================
def get_api_key():
    try: return st.secrets["ANTHROPIC_API_KEY"]
    except: return None

def generate_code_sonnet(client, prompt, mode="genesis"):
    """
    The Brain: Claude 3.5 Sonnet.
    """
    system_prompt = """
    You are CODIQ, the Supreme AI Architect for Samrion.
    
    PROTOCOL:
    1. ANALYZE: Determine if the user needs a single script or a full project structure.
    2. SINGLE FILE: Just output the Python code block.
    3. MULTI-FILE PROJECT: You MUST split code into multiple files using these XML tags:
    
    <file name="filename.ext">
    ... content ...
    </file>
    
    CRITICAL RULE: Always include a 'requirements.txt' if external libraries are used.
    
    STYLE GUIDE:
    - Use production-grade error handling.
    - If UI is needed, use Streamlit with a 'Dark Blue' aesthetic.
    - Add comments explaining complex logic.
    """

    if mode == "genesis":
        user_message = f"ARCHITECT THIS SYSTEM: {prompt}"
    else:
        user_message = f"REFACTOR & FIX THIS KERNEL: {prompt}"

    # Streaming the response for "Thinking" effect
    with st.status("🧠 CODIQ NEURAL LINK ACTIVE...", expanded=True) as status:
        st.write("🔌 Establishing Uplink...")
        message = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=4000,
            temperature=0.2,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )
        st.write("⚡ Compiling Logic Gates...")
        time.sleep(0.5)
        st.write("📦 Packaging Modules...")
        status.update(label="ARCHITECTING COMPLETE", state="complete", expanded=False)
        
    return message.content[0].text

def process_response(raw_text):
    """
    The Sorter: Decides if it's a snippet or a zip bundle.
    """
    pattern = r'<file name="(.*?)">(.*?)</file>'
    matches = re.findall(pattern, raw_text, re.DOTALL)
    
    if len(matches) > 1:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for filename, content in matches:
                zf.writestr(filename, content.strip())
        zip_buffer.seek(0)
        return "MULTI", zip_buffer, matches
    elif len(matches) == 1:
        filename, content = matches[0]
        return "SINGLE", content.strip(), filename
    else:
        # Fallback if no tags found
        return "SINGLE", raw_text, "main.py"

# ==========================================
# 3. INTERFACE LAYER
# ==========================================
st.title("🧠 SAMRION CODIQ")
st.markdown("### ULTIMATE INFRASTRUCTURE ARCHITECT")

# Tabs
tab_gen, tab_fix = st.tabs(["✨ GENESIS PROTOCOL", "🚑 SURGEON PROTOCOL"])

# === TAB 1: GENESIS ===
with tab_gen:
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.markdown("#### 📡 INPUT TRANSMISSION")
        idea_prompt = st.text_area("Define System Parameters...", height=300, 
                                   placeholder="e.g. 'Build a Full-Stack Streamlit Dashboard for Crypto Tracking with API integration. I need a requirements file and a separate config file.'")
        
        if st.button("🚀 INITIATE GENERATION", key="btn_gen", use_container_width=True):
            api_key = get_api_key()
            if not api_key:
                st.toast("⚠️ CRITICAL: API KEY MISSING IN SECRETS", icon="🔒")
            elif not idea_prompt:
                st.toast("⚠️ DATA MISSING: INPUT PARAMETERS", icon="🚫")
            else:
                client = anthropic.Anthropic(api_key=api_key)
                try:
                    raw_result = generate_code_sonnet(client, idea_prompt, mode="genesis")
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
                st.info(f"📂 **PROJECT BUNDLE DETECTED** ({len(extra)} Files)")
                st.download_button(
                    label="⬇️ DOWNLOAD REPO (.ZIP)",
                    data=data,
                    file_name="Samrion_Project.zip",
                    mime="application/zip",
                    use_container_width=True
                )
                
                # Preview Files
                for fname, fcontent in extra:
                    # Dynamic Language Detection
                    lang = "python"
                    if fname.endswith(".html"): lang = "html"
                    if fname.endswith(".css"): lang = "css"
                    if fname.endswith(".js"): lang = "javascript"
                    if fname.endswith(".txt"): lang = "text"
                    if fname.endswith(".json"): lang = "json"
                    
                    with st.expander(f"📄 {fname}"):
                        st.code(fcontent, language=lang)
            else:
                st.success("📋 **SINGLE SCRIPT GENERATED**")
                # Handle single file preview
                if isinstance(extra, str): # Filename
                    st.caption(f"File: {extra}")
                st.code(data, language='python')

# === TAB 2: SURGEON ===
with tab_fix:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 🩺 CODE REPAIR & OPTIMIZATION")
    broken_code = st.text_area("Inject Broken Kernel...", height=200, placeholder="Paste your error-filled code here...")
    
    if st.button("🚑 REFACTOR & HEAL", key="btn_fix", use_container_width=True):
         api_key = get_api_key()
         if not api_key:
            st.toast("⚠️ ACCESS DENIED: CHECK SECRETS", icon="🔒")
         else:
            client = anthropic.Anthropic(api_key=api_key)
            try:
                fix_raw = generate_code_sonnet(client, broken_code, mode="fix")
                mode, data, extra = process_response(fix_raw)
                
                if mode == "MULTI":
                    st.toast("✅ REPAIRED & SPLIT", icon="🛠️")
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
    POWERED BY SAMRION INTELLIGENCE | FOUNDER: NITIN RAJ | MIRZAPUR INFRASTRUCTURE
</div>
""", unsafe_allow_html=True)
