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

# -------------------------------------------------------
# 1. CSS & Styling
# -------------------------------------------------------
def load_custom_css():
    st.markdown("""
    <style>
        /* --- Global Variables --- */
        :root {
            --bg-color: #0d1117; /* GitHub Dark Dimmed */
            --card-bg: #161b22;
            --border-color: #30363d;
            --neon-cyan: #00f3ff;
            --neon-purple: #bc13fe;
            --text-primary: #c9d1d9;
            --text-white: #ffffff;
            --vscode-bg: #1e1e1e;
            --vscode-fg: #d4d4d4;
        }

        /* --- Main Background --- */
        .stApp {
            background-color: var(--bg-color);
            color: var(--text-primary);
        }

        /* --- Typography --- */
        h1, h2, h3 {
            color: var(--text-white) !important;
            font-family: 'Inter', sans-serif;
            font-weight: 700;
        }
        p, div, span {
            color: var(--text-primary);
            font-family: 'Inter', sans-serif;
        }

        /* --- Navbar/Footer Styling --- */
        .nav-container {
            background: rgba(22, 27, 34, 0.8);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid var(--border-color);
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .nav-logo {
            font-size: 1.5rem;
            font-weight: bold;
            background: linear-gradient(90deg, var(--neon-cyan), var(--neon-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .nav-links a {
            color: var(--text-primary);
            text-decoration: none;
            margin-left: 20px;
            font-size: 0.9rem;
            transition: color 0.3s;
        }
        .nav-links a:hover {
            color: var(--neon-cyan);
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

        /* --- VS Code Style Editor (Text Area) --- */
        textarea {
            background-color: var(--vscode-bg) !important;
            color: var(--vscode-fg) !important;
            font-family: 'Consolas', 'Courier New', monospace !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 4px !important;
            padding: 10px !important;
        }
        /* Fix specific Streamlit Text Area Wrapper */
        .stTextArea > div > div {
            background-color: var(--vscode-bg);
            border: 1px solid var(--border-color);
        }

        /* --- Chat Input & Standard Inputs --- */
        .stTextInput input, .stChatInput textarea {
            background-color: #0d1117 !important;
            color: white !important;
            border: 1px solid var(--border-color) !important;
        }

        /* --- Buttons (High Visibility) --- */
        .stButton > button {
            background: var(--neon-cyan) !important;
            color: #000000 !important; /* Black text for contrast */
            border: none;
            font-weight: bold;
            transition: transform 0.2s;
        }
        .stButton > button:hover {
            transform: scale(1.02);
            box-shadow: 0 0 10px var(--neon-cyan);
        }

        /* Secondary Button Style (if needed) */
        div[data-testid="stHorizontalBlock"] button {
            background: #21262d !important;
            color: var(--neon-cyan) !important;
            border: 1px solid var(--border-color) !important;
        }
        div[data-testid="stHorizontalBlock"] button:hover {
            border-color: var(--neon-cyan) !important;
        }

        /* --- Glass Cards --- */
        .glass-card {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }

        /* --- Sidebar --- */
        [data-testid="stSidebar"] {
            background-color: #010409;
            border-right: 1px solid #30363d;
        }
    </style>
    """, unsafe_allow_html=True)
load_custom_css()

# -------------------------------------------------------
# 2. Helper Functions
# -------------------------------------------------------

def sanitize_files(data):
    """
    Recursively flattens a nested dict of files (folders -> files) into a single dict
    mapping "path/to/file" -> "file contents as str".
    """
    flat_files = {}

    def recurse(obj, path=""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                new_path = f"{path}/{k}" if path else k
                recurse(v, new_path)
        else:
            # Convert non-string content to string safely
            if isinstance(obj, (bytes, bytearray)):
                try:
                    content = obj.decode("utf-8")
                except Exception:
                    content = obj.decode("utf-8", "replace")
            elif isinstance(obj, str):
                content = obj
            else:
                try:
                    content = json.dumps(obj)
                except Exception:
                    content = str(obj)
            # if path is empty generate a unique name
            key = path or f"file_{uuid.uuid4().hex[:8]}"
            flat_files[key] = content

    if isinstance(data, dict):
        recurse(data, "")
    else:
        recurse(data, "")

    return flat_files

# Session State
if "files" not in st.session_state: st.session_state.files = {}
if "page" not in st.session_state: st.session_state.page = "home"
if "chat" not in st.session_state: st.session_state.chat = []
if "project_meta" not in st.session_state: st.session_state.project_meta = {}
if "session_id" not in st.session_state: st.session_state.session_id = str(uuid.uuid4())[:8]

# -------------------------------------------------------
# 3. UI Components
# -------------------------------------------------------
def render_header():
    # Default text logo
    logo_html = "⚡ NexaBuild"

    # Check for logo in images directory
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

    st.markdown(f"""
    <div class="nav-container">
        <div class="nav-logo">{logo_html}</div>
        <div class="nav-links">
            <a href="#">Home</a>
            <a href="#">Features</a>
            <a href="#">About</a>
            <a href="mailto:@gmail.com" style="color: var(--neon-cyan); border: 1px solid var(--neon-cyan); padding: 5px 10px; border-radius: 5px;">Contact Us</a>
        </div>
    </div>
    """, unsafe_allow_html=True)


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
        st.markdown(
            "<div style='background: rgba(255,255,255,0.05); padding: 20px; border-radius: 10px; border: 1px solid #30363d;'>",
            unsafe_allow_html=True)
        with st.form("create_form"):
            prompt = st.text_area("Describe your project", height=150,
                                  placeholder="E.g., A Todo app where I can add, delete and save tasks permanently.")
            submitted = st.form_submit_button("🚀 Launch Team")
        st.markdown("</div>", unsafe_allow_html=True)

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
    c1, c2 = st.columns([3, 1])
    with c1:
        st.subheader("🛠️ Developer Workspace")
    with c2:
        if st.button("🏠 New Project"):
            st.session_state.page, st.session_state.files, st.session_state.chat = "home", {}, []
            st.rerun()
    st.markdown("---")

    with st.sidebar:
        st.subheader("💬 Chat")
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
    
    # --- PREVIEW TAB (Pure Static) ---
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
        c_list, c_edit = st.columns([1, 3])
        with c_list:
            file_keys = list(st.session_state.files.keys()) if st.session_state.files else []
            f_sel = None
            if file_keys:
                try:
                    f_sel = st.radio("File", file_keys)
                except Exception:
                    f_sel = st.selectbox("File", file_keys)
        with c_edit:
            if f_sel:
                file_content = st.session_state.files.get(f_sel, "")
                if not isinstance(file_content, str):
                    file_content = str(file_content)

                new_code = st.text_area("Edit", file_content, height=600, key=f"e_{f_sel}")
                if new_code != str(st.session_state.files.get(f_sel, "")) and st.button("Save", key=f"save_{f_sel}"):
                    st.session_state.files[f_sel] = new_code
                    st.rerun()
    
    # --- DEPLOY TAB ---
    with t3:
        if st.session_state.files:
            try:
                zip_bytes = create_zip_bytes(st.session_state.files)
                st.download_button("⬇️ ZIP", zip_bytes, "site.zip", "application/zip")
            except Exception as e:
                st.error(f"Error creating ZIP: {e}")

            repo = st.text_input("Repo Name", "nexa-site")
            tok = st.text_input("GitHub Token", type="password")
            if st.button("Deploy"):
                try:
                    result = GitHubDeployer(tok).deploy_to_github_pages(repo, st.session_state.files)
                    url = result.get("url") if isinstance(result, dict) else str(result)
                    st.success(f"Live: {url}")
                except Exception as e:
                    st.error(f"Error: {e}")
    render_footer()

if st.session_state.page == "home":
    render_home()
else:
    render_workspace()
