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
    page_title=" CODIQ",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# === THE GLITCH-FREE CSS PATCH ===
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    /* 1. SAFE FONT APPLICATION */
    p, h1, h2, h3, h4, h5, label, input, textarea, button, small {
        font-family: 'Inter', sans-serif !important;
        color: #ffffff !important;
    }
    
    /* 2. BACKGROUND */
    .stApp {
        background: radial-gradient(circle at 10% 20%, #001540 0%, #000000 90%);
        background-attachment: fixed;
    }

    /* 3. KILL HEADER */
    header[data-testid="stHeader"] {display: none !important;}
    .stApp > header {display: none !important;}
    div[data-testid="stToolbar"] {visibility: hidden; height: 0%; position: fixed;}
    div[data-testid="stDecoration"] {visibility: hidden; height: 0%;}

    /* 4. OVAL TABS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px; background-color: rgba(0, 0, 0, 0.5);
        padding: 10px 20px; border-radius: 50px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        display: inline-flex; justify-content: center;
        margin: 0 auto;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px; border-radius: 30px !important;
        padding: 0 40px; background-color: transparent;
        border: 1px solid rgba(255,255,255,0.1);
        color: white; font-weight: 600; transition: 0.3s;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #D60000, #ff4d4d) !important;
        border: none; color: white !important;
        box-shadow: 0 0 20px rgba(214, 0, 0, 0.6);
    }
    .stTabs [data-baseweb="tab-highlight"] {display: none;}

    /* 5. INPUTS */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        background-color: rgba(0, 20, 60, 0.4) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(214, 0, 0, 0.5);
        color: white !important; border-radius: 15px;
    }
    .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
        border-color: #ff0000; box-shadow: 0 0 15px rgba(255, 0, 0, 0.2);
    }

    /* 6. BUTTONS */
    div.stButton > button {
        background: linear-gradient(135deg, #D60000 0%, #8a0000 100%) !important;
        border: none !important; color: white !important;
        font-weight: 800 !important; border-radius: 50px !important;
        padding: 0.75rem 2rem; transition: 0.3s;
    }
    div.stButton > button:hover {
        transform: scale(1.05); box-shadow: 0 0 25px rgba(255, 0, 0, 0.6);
    }

    /* FOOTER */
    .footer {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background: rgba(0, 0, 0, 0.9); backdrop-filter: blur(5px);
        border-top: 1px solid #D60000; color: #888; text-align: center;
        padding: 10px; font-size: 10px; letter-spacing: 2px; z-index: 999;
        text-transform: uppercase;
    }
    [data-testid="stSidebar"] {display: none;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. INTELLIGENCE CORE (MEMORY & NAMING)
# ==========================================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def get_api_key():
    try: return st.secrets["GROQ_API_KEY"]
    except: return None

def generate_code_groq(client, user_input, mode="genesis"):
    """
    The Brain: Llama 3.3 (Memory Enabled)
    """
    system_prompt = """
    You are CODIQ, the Supreme AI Architect.
    
    PROTOCOL:
    1. CONTEXT: Remember previous requests. If the user says "Change color to red", apply it to the previous code.
    2. STRUCTURE: Split code using <file name="filename.ext"> ...content... </file>.
    3. NAMING: You MUST provide a suitable filename for the zip inside <zip_name>Project_Name.zip</zip_name> tags.
    4. DEPENDENCIES: Always include 'requirements.txt' if needed.
    """

    # Build Message History
    messages = [{"role": "system", "content": system_prompt}]
    
    # Add History (Memory)
    for msg in st.session_state.chat_history:
        messages.append(msg)
    
    # Add Current User Prompt
    prompt_text = f"ARCHITECT THIS SYSTEM: {user_input}" if mode == "genesis" else f"FIX THIS: {user_input}"
    messages.append({"role": "user", "content": prompt_text})

    with st.status("🧠 CODIQ NEURAL LINK ACTIVE...", expanded=True) as status:
        st.write("🔌 Syncing Memory Banks...")
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=messages,
            temperature=0.1,
            max_tokens=7000,
        )
        
        st.write("⚡ Compiling Logic...")
        time.sleep(0.5)
        st.write("📦 Packaging...")
        status.update(label="ARCHITECTING COMPLETE", state="complete", expanded=False)
        
    return completion.choices[0].message.content

def process_response(raw_text):
    # 1. Extract Zip Name
    name_match = re.search(r'<zip_name>(.*?)</zip_name>', raw_text)
    zip_name = name_match.group(1).strip() if name_match else "Samrion_Project.zip"
    
    # 2. Extract Files
    pattern = r'<file name="(.*?)">(.*?)</file>'
    matches = re.findall(pattern, raw_text, re.DOTALL)
    
    if len(matches) > 0:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for filename, content in matches:
                zf.writestr(filename, content.strip())
        zip_buffer.seek(0)
        return "MULTI", zip_buffer, matches, zip_name
    else:
        return "SINGLE", raw_text, "main.py", zip_name

# ==========================================
# 3. INTERFACE LAYER
# ==========================================
st.title("🧠 CODIQ")
st.markdown("### ULTIMATE INFRASTRUCTURE ARCHITECT")

tab_gen, tab_fix = st.tabs(["✨ GENERATE", "FIX AND OPTIMISE"])

# === TAB 1: GENESIS (WITH MEMORY) ===
with tab_gen:
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.markdown("#### 📡 INPUT TRANSMISSION")
        
        # Show Chat History (Optional, keeps user aware of context)
        if st.session_state.chat_history:
            with st.expander("📜 Neural History (Memory)"):
                for m in st.session_state.chat_history:
                    if m['role'] == 'user':
                        st.caption(f"YOU: {m['content'][:50]}...")
        
        idea_prompt = st.text_area("Define System Parameters...", height=300, 
                                   placeholder="e.g. 'Build a Snake Game'. \n(Later you can say: 'Add a high score system')")
        
        c_btn1, c_btn2 = st.columns([3, 1])
        with c_btn1:
            if st.button("🚀 INITIATE GENERATION", key="btn_gen", use_container_width=True):
                api_key = get_api_key()
                if not api_key: st.error("⚠️ GROQ_API_KEY MISSING")
                elif not idea_prompt: st.toast("⚠️ DATA MISSING", icon="🚫")
                else:
                    client = Groq(api_key=api_key)
                    try:
                        raw_result = generate_code_groq(client, idea_prompt, mode="genesis")
                        mode, data, extra, z_name = process_response(raw_result)
                        
                        # SAVE TO MEMORY
                        st.session_state.chat_history.append({"role": "user", "content": idea_prompt})
                        st.session_state.chat_history.append({"role": "assistant", "content": raw_result})
                        
                        st.session_state['res_mode'] = mode
                        st.session_state['res_data'] = data
                        st.session_state['res_extra'] = extra
                        st.session_state['res_name'] = z_name
                        st.toast("✅ MEMORY UPDATED", icon="🧠")
                    except Exception as e:
                        st.error(f"SYSTEM FAILURE: {e}")
        
        with c_btn2:
            # Clear Memory Button
            if st.button("🧹 RESET", help="Clear AI Memory"):
                st.session_state.chat_history = []
                st.toast("MEMORY WIPED", icon="🧹")

    with c2:
        st.markdown("#### 📦 OUTPUT CONSOLE")
        if 'res_mode' in st.session_state:
            mode = st.session_state['res_mode']
            data = st.session_state['res_data']
            extra = st.session_state['res_extra']
            z_name = st.session_state.get('res_name', "Samrion_Project.zip")
            
            if mode == "MULTI":
                # Dynamic Filename Display
                st.success(f"📂 **{z_name}** READY ({len(extra)} Files)")
                
                st.download_button(
                    label=f"⬇️ DOWNLOAD {z_name}",
                    data=data,
                    file_name=z_name,
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
    st.markdown("####  CODE FIX & OPTIMIZATION")
    broken_code = st.text_area("Inject Broken Kernel...", height=200)
    
    if st.button("", key="btn_fix", use_container_width=True):
         api_key = get_api_key()
         if not api_key: st.error("⚠️ GROQ KEY MISSING")
         else:
            client = Groq(api_key=api_key)
            try:
                # Surgeon doesn't need long-term memory usually
                fix_raw = generate_code_groq(client, broken_code, mode="fix")
                mode, data, extra, z_name = process_response(fix_raw)
                
                if mode == "MULTI":
                    st.toast("✅ FIXED", icon="🛠️")
                    st.download_button(f"⬇️ DOWNLOAD {z_name}", data, z_name, "application/zip", use_container_width=True)
                    for fname, fcontent in extra:
                        with st.expander(f"📄 {fname}"):
                            st.code(fcontent)
                else:
                    st.toast("✅ FIXED", icon="✨")
                    st.code(data, language='python')
            except Exception as e:
                st.error(f"ERROR: {e}")

# FOOTER
st.markdown("""
<div class="footer">
    POWERED BY SAMRION INTELLIGENCE | FOUNDER: NITIN RAJ | SAMRION AI INFRASTRUCTURE
</div>
""", unsafe_allow_html=True)
