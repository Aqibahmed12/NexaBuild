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
    # Note: CSS carefully scopes rules to avoid breaking Streamlit core.
    # Adjusted z-index layering so the popover (NexaBot) sits above the custom header,
    # and added neon glow border to the chat box inside the popover.
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

            /* Layering: keep nav beneath popovers but above page content */
            --streamlit-header-height: 56px; /* adjust if your Streamlit topbar is taller */
            --nav-vertical-offset: calc(var(--streamlit-header-height) + 12px);
            --nav-height: 64px;
            --max-content-width: 1200px;

            --nav-z: 1050;
            --popover-z: 2150;
        }

        /* --- App base and spacing --- */
        .stApp {
            background-color: var(--bg-color);
            color: var(--text-primary);
            /* Add top padding so the fixed header does not overlap content */
            padding-top: calc(var(--nav-vertical-offset) + var(--nav-height) + 12px);
        }

        /* Constrain main content for a balanced layout */
        .block-container {
            max-width: var(--max-content-width);
            margin-left: auto;
            margin-right: auto;
            padding-left: 20px;
            padding-right: 20px;
        }

        h1, h2, h3 { color: var(--text-white) !important; font-family: 'Inter', sans-serif; }

        /* --- Header (sticky/fixed) --- */
        .nav-container {
            position: fixed;
            top: var(--nav-vertical-offset);
            left: 50%;
            transform: translateX(-50%);
            width: calc(100% - 40px);
            max-width: var(--max-content-width);
            z-index: var(--nav-z);
            height: var(--nav-height);
            background: linear-gradient(180deg, rgba(22,27,34,0.98), rgba(16,20,24,0.9));
            backdrop-filter: blur(8px);
            border: 1px solid var(--border-color);
            padding: 12px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-radius: 12px;
            box-shadow: 0 6px 24px rgba(0,0,0,0.6);
        }

        /* Logo */
        .nav-logo {
            font-size: 1.25rem;
            font-weight: 800;
            background: linear-gradient(90deg, var(--neon-cyan), var(--neon-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        /* Nav Links */
        .nav-links { display: flex; gap: 22px; align-items: center; }
        .nav-links a {
            color: #c9d1d9; text-decoration: none; font-size: 0.95rem; font-weight: 700;
            transition: all 0.25s ease; display: inline-block;
            padding: 6px 10px; border-radius: 8px;
        }
        .nav-links a:hover {
            color: #000;
            background: var(--neon-cyan);
            text-decoration: none;
            transform: translateY(-2px) scale(1.03);
            box-shadow: 0 8px 30px rgba(0,243,255,0.12);
        }

        /* --- Footer --- */
        .footer-container {
            margin-top: 60px;
            padding: 30px;
            border-top: 1px solid var(--border-color);
            text-align: center;
            background: var(--card-bg);
            font-size: 0.95rem;
            border-radius: 10px;
        }
        .footer-link {
            color: var(--neon-cyan);
            text-decoration: none;
            font-weight: bold;
        }

        /* --- Buttons & Popover Button Styling (NexaBot) --- */
        /* Broadened selectors to match different Streamlit versions and renderings */
        button[data-testid="stPopoverOpenButton"],
        button[aria-label*="NexaBot"],
        [data-testid="stPopover"] > button,
        button[title*="NexaBot"] {
            background-color: var(--neon-cyan) !important;
            color: #000 !important;
            border: none !important;
            font-weight: 800 !important;
            padding: 8px 14px !important;
            border-radius: 10px !important;
            transition: all 0.18s ease-in-out !important;
            box-shadow: 0 8px 30px rgba(0,243,255,0.08) !important;
            position: relative !important;
            z-index: calc(var(--popover-z) + 2) !important; /* ensure button itself is above header */
        }

        /* Make sure inner text / icon colors stick */
        button[data-testid="stPopoverOpenButton"] span,
        button[aria-label*="NexaBot"] span,
        button[data-testid="stPopoverOpenButton"] svg,
        button[aria-label*="NexaBot"] svg,
        [data-testid="stPopover"] > button span,
        [data-testid="stPopover"] > button svg {
            color: #000 !important;
            fill: #000 !important;
        }

        /* Hover effect: glow + slight scale */
        button[data-testid="stPopoverOpenButton"]:hover,
        button[aria-label*="NexaBot"]:hover,
        [data-testid="stPopover"] > button:hover {
            transform: translateY(-2px) scale(1.06) !important;
            box-shadow: 0 0 48px rgba(0,243,255,0.28) !important;
        }

        /* --- Popover container and body layering --- */
        /* Ensure the opened popover panel floats above the nav */
        div[data-testid="stPopover"] {
            position: relative !important;
            z-index: calc(var(--popover-z) + 3) !important;
        }
        /* Body is typically appended under same node; ensure content has very high z-index */
        div[data-testid="stPopoverBody"] {
            position: relative !important;
            z-index: calc(var(--popover-z) + 4) !important;
            background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(250,250,250,0.96));
            color: #000;
            border-radius: 12px;
            padding: 12px !important;
            /* Small offset so the body shows below the open button and above the nav visually */
            margin-top: 8px !important;
            box-shadow: 0 12px 60px rgba(0,0,0,0.45), 0 0 30px rgba(0,243,255,0.12);
            border: 1px solid rgba(0,243,255,0.12);
        }

        /* --- Neon glowing border for the central chat box inside the popover --- */
        /* This targets the chat message container and chat box area in the popover */
        div[data-testid="stPopoverBody"] .stChat,
        div[data-testid="stPopoverBody"] div[data-testid="stChatMessageContent"],
        div[data-testid="stPopoverBody"] .stChatMessage,
        div[data-testid="stPopoverBody"] .stChatMessageBlock,
        div[data-testid="stPopoverBody"] .stChatInput {
            border-radius: 12px !important;
        }

        /* Apply neon glow border to the main area (middle chat box) */
        div[data-testid="stPopoverBody"] > div:first-child,
        div[data-testid="stPopoverBody"] .stChatMessageBlock,
        div[data-testid="stPopoverBody"] .stChat {
            box-shadow:
                0 2px 0 rgba(0,0,0,0.6) inset,
                0 6px 30px rgba(0,0,0,0.6),
                0 0 20px rgba(0,243,255,0.14),
                0 0 6px rgba(0,243,255,0.28);
            border: 1px solid rgba(0,243,255,0.28);
            background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(250,250,250,0.96));
        }

        /* Chat message text inside popover — keep readable */
        div[data-testid="stPopoverBody"] div[data-testid="stChatMessageContent"] p {
            color: #001019 !important;
            font-weight: 500 !important;
        }

        /* Chat input area: neon focus glow */
        div[data-testid="stPopoverBody"] textarea:focus,
        div[data-testid="stPopoverBody"] input:focus {
            outline: none !important;
            box-shadow: 0 0 24px rgba(0,243,255,0.32) !important;
            border: 1px solid rgba(0,243,255,0.4) !important;
        }

        /* --- Generic Buttons, Forms & Sidebar --- */
        .stButton > button,
        [data-testid="stFormSubmitButton"] > button {
            background-color: var(--neon-cyan) !important;
            color: #000 !important;
            border: none !important;
            font-weight: 800 !important;
            padding: 8px 14px !important;
            border-radius: 10px !important;
            transition: all 0.18s ease-in-out !important;
            box-shadow: 0 6px 18px rgba(0,243,255,0.06);
        }

        .stButton > button:hover,
        [data-testid="stFormSubmitButton"] > button:hover {
            transform: translateY(-2px) scale(1.03) !important;
            box-shadow: 0 0 30px rgba(0,243,255,0.18) !important;
        }

        /* --- Form & Label Styling --- */
        [data-testid="stForm"] {
            background: rgba(255,255,255,0.03);
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #262b30;
        }

        div[data-testid="stWidgetLabel"] p,
        div[data-testid="stWidgetLabel"] label {
            color: #ffffff !important;
            font-weight: 600 !important;
        }

        /* Sidebar: keep readable and consistent */
        [data-testid="stSidebar"] {
            background-color: #010409;
            border-right: 1px solid #1f2937;
            color: var(--text-primary);
            padding-top: calc(var(--nav-height) / 2);
        }
        [data-testid="stSidebar"] .stMarkdown, 
        [data-testid="stSidebar"] label, 
        [data-testid="stSidebar"] p {
            color: var(--vscode-fg) !important;
        }
        [data-testid="stSidebar"] input, 
        [data-testid="stSidebar"] textarea, 
        [data-testid="stSidebar"] select {
            background-color: #0f1720 !important;
            color: var(--vscode-fg) !important;
            border: 1px solid #25303a !important;
        }

        /* Tabs & workspace spacing adjustments */
        .stTabs, .css-1v3fvcr {
            margin-top: 8px;
        }
        .stApp .stTabs [role="tablist"] { gap: 8px; }

        /* Make preview iframe area nicely spaced and centered */
        .stApp .stComponentsPlaceholder, .stApp iframe {
            border-radius: 8px;
            overflow: hidden;
        }

        /* Balance column paddings across the app */
        .row-widget.stRadio, .row-widget.stMultiselect, .row-widget.stTextArea {
            padding-top: 6px;
            padding-bottom: 6px;
        }
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
                logo_html = f'<img src="data:{mime_type};base64,{encoded_string}" style="height: 36px; border-radius: 6px; margin-right:8px;"> NexaBuild'
            except Exception as e:
                print(f"Error loading logo: {e}")

    # Use two columns: main nav and the chatbot button column (kept small)
    c_nav, c_bot = st.columns([6, 1], gap="small")
    
    with c_nav:
        # Render fixed header markup. The CSS above makes .nav-container fixed and prevents overlap.
        st.markdown(f"""
        <div class="nav-container">
            <div style="display:flex; align-items:center; gap:12px;">
                <div class="nav-logo">{logo_html}</div>
            </div>
            <div class="nav-links">
                <a href="?nav=home" target="_self">Home</a>
                <a href="#">About</a>
                <a href="mailto:ahmedaqib152@gmail.com">Contact</a>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with c_bot:
        # Chatbot Button
        # Keep behavior intact; styling targets the popover open button using robust selectors.
        with st.popover("🤖 NexaBot", use_container_width=True):
            st.caption("Hey Buddy! Do you need help? Ask NexaBot")
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
        <p>Made with ❤️ by the NexaBuild team</p>
        <p>If you need help, look at the top-right corner — NexaBot is always ready for you</p>
        <p>Need help? <a href="mailto:ahmedaqib152@gmail.com" class="footer-link">Contact Support (nexabuild@gmail.com)</a></p>
        <p style="font-size: 0.8rem; color: #9ca3af; margin-top: 10px;">© 2025 NexaBuild. All rights reserved</p>
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
                <h1 style="font-size: 3.5rem; font-weight: 900; letter-spacing: -0.03em; line-height: 1.05; margin-bottom:1rem; 
                    color: #00ffff;
                    text-shadow: 0 0 2px #00ffff, 0 0 5px #00ffff, 0 0 10px #00ffff;
                    -webkit-text-stroke: 0.8px #000;
                    text-stroke: 0.8px #000;">
                    Build something <br> Unbelievable
                </h1>
                <p style="font-size: 1.05rem; color: #94a3b8; max-width: 720px; margin: 0 auto;">
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
                # Keep iframe nicely padded and scrollable
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
        <div class="glass-card" style="border-left: 4px solid var(--neon-cyan); padding:14px; border-radius:8px; background: rgba(255,255,255,0.02);">
            <h4 style="margin-bottom:6px;">Download Source Code</h4>
            <p style="margin-top:0; color:#9aa6b2;">Get the full source code as a ZIP file to use locally or upload to Netlify/Vercel.</p>
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
