# main.py — Professional Agentic AI Website Builder (Cloud Compatible Version)

import streamlit as st
import os
import base64
import uuid
import json

# Import WebsiteGenerator to combine files for preview
from ai.utils import create_zip_bytes, WebsiteGenerator
from ai.deploy import GitHubDeployer
from agents.manager import ProjectManager
from ai.chatbot import NexaBot 

# -------------------------------------------------------
# 0. Asset Helper & Config
# -------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_logo_path():
    search_dirs = [
        os.path.join(BASE_DIR, "assets"),
        os.path.join(BASE_DIR, "images")
    ]
    valid_exts = [".png", ".jpg", ".jpeg", ".svg", ".ico"]
    for d in search_dirs:
        if os.path.exists(d):
            for file in os.listdir(d):
                if file.lower().startswith("logo.") and any(file.lower().endswith(ext) for ext in valid_exts):
                    return os.path.join(d, file)
    return None

logo_path = get_logo_path()
page_icon = logo_path if logo_path else "⚡"

st.set_page_config(page_title="NexaBuild", page_icon=page_icon, layout="wide", initial_sidebar_state="collapsed")

# --- HOME RESET LOGIC ---
if st.query_params.get("nav") == "home":
    st.session_state.page = "home"
    st.session_state.files = {}
    st.session_state.chat = []
    st.session_state.project_meta = {}
    st.query_params.clear()
    st.rerun()

# -------------------------------------------------------
# 1. CSS & Styling
# -------------------------------------------------------
def load_custom_css():
    st.markdown("""
    <style>
        /* --- Global Variables --- */
        :root {
            --bg-color: #0d1117; 
            --card-bg: #161b22; 
            --border-color: #30363d;
            --neon-cyan: #00f3ff;
            --neon-purple: #bc13fe;
            --text-primary: #c9d1d9;
            --text-white: #ffffff;
            --vscode-bg: #1e1e1e;
            --vscode-fg: #d4d4d4;
        }

        .stApp { background-color: var(--bg-color); color: var(--text-primary); }
        h1, h2, h3 { color: var(--text-white) !important; font-family: 'Inter', sans-serif; }
        
        /* --- Navbar Container --- */
        .nav-container {
            background: rgba(22, 27, 34, 0.8);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid var(--border-color);
            padding: 10px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-radius: 10px;
        }
        .nav-logo {
            font-size: 1.5rem;
            font-weight: bold;
            background: linear-gradient(90deg, var(--neon-cyan), var(--neon-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: flex; align-items: center; gap: 10px;
        }

        /* --- Nav Links --- */
        .nav-links { display: flex; gap: 30px; }
        .nav-links a {
            color: #c9d1d9; text-decoration: none; font-size: 1rem; font-weight: 600;
            transition: all 0.3s ease; display: inline-block;
        }
        .nav-links a:hover {
            color: #00f3ff; text-shadow: 0 0 10px #00f3ff;
            transform: scale(1.2); text-decoration: underline; text-underline-offset: 6px;
        }

        .footer-container {
            margin-top: 50px;
            padding: 30px;
            border-top: 1px solid var(--border-color);
            text-align: center;
            background: var(--card-bg);
            font-size: 0.9rem;
        }
        .footer-link {
            color: var(--neon-cyan);
            text-decoration: none;
            font-weight: bold;
        }

        /* --- BUTTONS (Launch Team & Ask AI) --- */
        /* Force high contrast: Cyan Background, Black Text */
        
        /* 1. Ask AI Popover Button */
        [data-testid="stPopover"] > button {
            background-color: var(--neon-cyan) !important;
            color: #000000 !important;
            border: none !important;
            font-weight: 900 !important;
            box-shadow: 0 0 15px rgba(0, 243, 255, 0.3) !important;
            transition: all 0.3s ease-in-out;
        }
        [data-testid="stPopover"] > button:hover {
            transform: scale(1.05);
            box-shadow: 0 0 25px var(--neon-cyan) !important;
            color: #000000 !important;
        }

        /* 2. Form Submit Button (Launch Team) */
        [data-testid="stFormSubmitButton"] > button {
            background-color: var(--neon-cyan) !important;
            color: #000000 !important;
            border: none !important;
            font-weight: 900 !important;
            width: 100%;
        }
        [data-testid="stFormSubmitButton"] > button:hover {
            box-shadow: 0 0 15px var(--neon-cyan);
            transform: scale(1.02);
        }

        /* 3. Generic Buttons */
        .stButton > button {
            background-color: var(--neon-cyan) !important;
            color: #000000 !important;
            border: none; font-weight: bold;
        }

        /* --- FORM & LABELS FIXES --- */
        
        /* Style the Form Container to look like a card */
        [data-testid="stForm"] {
            background: rgba(255,255,255,0.05);
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #30363d;
        }

        /* Make 'Describe your project' Label White */
        div[data-testid="stWidgetLabel"] p {
            color: #ffffff !important;
            font-size: 1rem !important;
            font-weight: 600 !important;
        }
        div[data-testid="stWidgetLabel"] label {
            color: #ffffff !important;
        }

        /* --- Chat Popup Internals --- */
        div[data-testid="stChatMessageContent"] p { color: #333333 !important; font-weight: 500; }
        div[data-testid="stPopoverBody"] textarea { background-color: #f0f2f6 !important; color: black !important; }
        div[data-testid="stPopoverBody"] button[kind="primary"] { background-color: var(--neon-cyan) !important; border: none !important; }
        div[data-testid="stPopoverBody"] button[kind="primary"] svg { fill: black !important; }

        [data-testid="stSidebar"] { background-color: #010409; border-right: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)
load_custom_css()

# -------------------------------------------------------
# 2. Helper Functions
# -------------------------------------------------------

def sanitize_files(data):
    flat_files = {}
    def recurse(obj, path=""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                recurse(v, f"{path}/{k}" if path else k)
        else:
            if isinstance(obj, (bytes, bytearray)):
                try: content = obj.decode("utf-8")
                except: content = obj.decode("utf-8", "replace")
            elif isinstance(obj, str): content = obj
            else: content = str(obj)
            flat_files[path or f"file_{uuid.uuid4().hex[:8]}"] = content

    recurse(data)
    return flat_files

# Session State
if "files" not in st.session_state: st.session_state.files = {}
if "page" not in st.session_state: st.session_state.page = "home"
if "chat" not in st.session_state: st.session_state.chat = []
if "project_meta" not in st.session_state: st.session_state.project_meta = {}
if "session_id" not in st.session_state: st.session_state.session_id = str(uuid.uuid4())[:8]
if "nexabot_history" not in st.session_state: st.session_state.nexabot_history = []

# -------------------------------------------------------
# 3. UI Components
# -------------------------------------------------------
def render_header():
    logo_html = "⚡ NexaBuild"
    if os.path.exists("images"):
        logo_file = next((f for f in os.listdir("images") if f.lower().startswith("logo.")), None)
        if logo_file:
            try:
                with open(os.path.join("images", logo_file), "rb") as f:
                    encoded_string = base64.b64encode(f.read()).decode()
                ext = logo_file.split('.')[-1].lower()
                mime_type = f"image/{'svg+xml' if ext == 'svg' else ext}"
                logo_html = f'<img src="data:{mime_type};base64,{encoded_string}" style="height: 40px; border-radius: 6px;"> NexaBuild'
            except Exception as e:
                print(f"Error loading logo: {e}")

    c_nav, c_bot = st.columns([6, 1], gap="small")
    
    with c_nav:
        st.markdown(f"""
        <div class="nav-container">
            <div class="nav-logo">{logo_html}</div>
            <div class="nav-links">
                <a href="?nav=home" target="_self">Home</a>
                <a href="#">About</a>
                <a href="mailto:ahmedaqib152@gmail.com">Contact</a>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with c_bot:
        # Chatbot Button
        with st.popover("🤖 Ask AI", use_container_width=True):
            st.caption("Chat with NexaBot")
            for msg in st.session_state.nexabot_history:
                st.chat_message(msg["role"]).write(msg["content"])

            if prompt := st.chat_input("Ask NexaBot..."):
                st.session_state.nexabot_history.append({"role": "user", "content": prompt})
                st.rerun()

            if st.session_state.nexabot_history and st.session_state.nexabot_history[-1]["role"] == "user":
                with st.spinner("Thinking..."):
                    try:
                        bot = NexaBot()
                        history_context = []
                        for m in st.session_state.nexabot_history[:-1]:
                            role_api = "user" if m["role"] == "user" else "model"
                            history_context.append({"role": role_api, "parts": m["content"]})

                        response_text = bot.ask(st.session_state.nexabot_history[-1]["content"], history_context)
                        st.session_state.nexabot_history.append({"role": "assistant", "content": response_text})
                        st.rerun()
                    except Exception as e:
                        st.error(f"AI Error: {e}")

def render_footer():
    st.markdown("""
    <div class="footer-container">
        <p>Built with ❤️ using Gemini AI</p>
        <p>Need help? <a href="mailto:nexabuild@gmail.com" class="footer-link">Contact Support (nexabuild@gmail.com)</a></p>
        <p style="font-size: 0.8rem; color: #666; margin-top: 10px;">© 2025 NexaBuild. All rights reserved.</p>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------------
# 4. Page: Home
# -------------------------------------------------------
def render_home():
    render_header()
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("""
            <div style='text-align: center; margin-bottom: 40px;'>
                <h1 style="font-size: 4rem; font-weight: 900; letter-spacing: -0.03em; line-height: 1.1; margin-bottom:1rem; 
                    color: #00ffff;
                    text-shadow: 0 0 2px #00ffff, 0 0 5px #00ffff, 0 0 10px #00ffff;
                    -webkit-text-stroke: 1px #000;
                    text-stroke: 1px #000;">
                    Build something <br> Unbelievable
                </h1>
                <p style="font-size: 1.25rem; color: #94a3b8; max-width: 600px; margin: 0 auto;">
                    The AI Website Builder that thinks like a developer. <br>
                    From idea to full-stack app in seconds.
                </p>
            </div>
            """, unsafe_allow_html=True)

        
        with st.form("create_form"):
            prompt = st.text_area("Describe your project", height=150,
                                  placeholder="E.g., A Todo app where I can add, delete and save tasks permanently.")
            submitted = st.form_submit_button("🚀 Generate")
        
        if submitted and prompt:
            manager = ProjectManager()
            with st.spinner("Agents working..."):
                try:
                    result = manager.create_website(prompt)
                    if result:
                        clean_files = sanitize_files(result.get("files", {}))
                        st.session_state.files = clean_files
                        st.session_state.project_meta = {"plan": result.get("plan"), "design": result.get("design")}
                        st.session_state.chat.extend(
                            [("user", prompt), ("ai", "Project ready! JavaScript Logic Generated.")])
                        st.session_state.page = "workspace"
                        st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
    render_footer()

# -------------------------------------------------------
# 5. Page: Workspace
# -------------------------------------------------------
def render_workspace():
    # Sanitize session state on load
    if st.session_state.files:
        st.session_state.files = sanitize_files(st.session_state.files)


    render_header()
    st.subheader("🛠️ Developer Workspace")
    st.markdown("---")


    with st.sidebar:
        st.subheader("💬 Team Chat")
        if st.session_state.project_meta:
            with st.expander("Plan"): 
                try:
                    st.json(st.session_state.project_meta.get("plan"))
                except Exception:
                    st.write(st.session_state.project_meta.get("plan"))
        for r, m in st.session_state.chat:
            if r == "user":
                st.info(f"You: {m}")
            else:
                st.success(f"Team: {m}")
        
        chat_input_val = st.chat_input("Changes?") if hasattr(st, "chat_input") else st.text_input("Changes?")
        if chat_input_val:
            st.session_state.chat.append(("user", chat_input_val))
            mgr = ProjectManager()
            with st.spinner("Coding..."):
                try:
                    u = mgr.edit_website(chat_input_val, st.session_state.files)
                    if u:
                        clean_updates = sanitize_files(u)
                        st.session_state.files.update(clean_updates)
                        st.session_state.chat.append(("ai", "Updated."))
                        st.rerun()
                except Exception as e:
                    st.error(f"Error during edit: {e}")

    t1, t2, t3 = st.tabs(["👁️ Preview", "💻 Code", "🚀 Deploy"])
    
    # --- PREVIEW TAB ---
    with t1:
        if st.session_state.files:
            try:
                gen = WebsiteGenerator()
                html_content = gen.combine_to_html(st.session_state.files)
            except Exception as e:
                st.error(f"Error generating preview: {e}")
                html_content = None

            if html_content:
                st.components.v1.html(html_content, height=800, scrolling=True)
        else:
            st.warning("No files generated yet.")

    # --- CODE TAB ---
    with t2:
        col_list, col_editor = st.columns([1, 4])

        with col_list:
            st.markdown("##### Files")
            file_keys = list(st.session_state.files.keys()) if st.session_state.files else []
            if file_keys:
                selected_file = st.radio("Select File", file_keys, label_visibility="collapsed")
            else:
                selected_file = None

        with col_editor:
            if selected_file:
                st.markdown(f"##### Editing: `{selected_file}`")
                new_code = st.text_area(
                    "Code Editor",
                    value=st.session_state.files[selected_file],
                    height=600,
                    label_visibility="collapsed",
                    key=f"editor_{selected_file}"
                )

                if new_code != st.session_state.files[selected_file]:
                    if st.button(f"💾 Save Changes to {selected_file}"):
                        st.session_state.files[selected_file] = new_code
                        st.success("File Saved!")
                        st.rerun()
            else:
                st.info("Select a file to edit.")
    
    # --- DEPLOY TAB ---
    with t3:
        st.markdown("### 📦 Export Project")

        # Download Box
        st.markdown("""
        <div class="glass-card" style="border-left: 4px solid var(--neon-cyan);">
            <h4>  Download Source Code</h4>
            <p>   Get the full source code as a ZIP file to use locally or upload to Netlify/Vercel.</p>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.files:
            zip_bytes = create_zip_bytes(st.session_state.files)
            st.download_button(
                label="⬇️ Download ZIP Package",
                data=zip_bytes,
                file_name="my-website-project.zip",
                mime="application/zip",
                type="primary"
            )

        st.markdown("---")
        st.markdown("### 🐙 GitHub Pages Deploy")

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            repo_name = st.text_input("Repository Name", "my-ai-site")
        with col_d2:
            gh_token = st.text_input("GitHub Token", type="password")

        if st.button("🚀 Deploy to GitHub"):
            if not gh_token:
                st.error("GitHub Token is required.")
            else:
                with st.spinner("Deploying..."):
                    try:
                        deployer = GitHubDeployer(gh_token)
                        res = deployer.deploy_to_github_pages(repo_name, st.session_state.files)
                        st.success(f"Live at: {res['url']}")
                        st.markdown(f"[Open Website]({res['url']})")
                    except Exception as e:
                        st.error(f"Deploy failed: {e}")
    render_footer()

if st.session_state.page == "home":
    render_home()
else:
    render_workspace()
