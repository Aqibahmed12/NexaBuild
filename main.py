# main.py — Professional Agentic AI Website Builder (Universal Backend Version)

import streamlit as st
import os
import sys
import time
import subprocess
import signal
import shutil
import base64
import socket
import uuid
import re
import atexit  # Ensures server process is killed on exit

from ai.utils import create_zip_bytes
from ai.deploy import GitHubDeployer
from agents.manager import ProjectManager

# -------------------------------------------------------
# 0. Asset Helper & Config
# -------------------------------------------------------
# Get the absolute path of the folder containing main.py to avoid path errors
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

st.set_page_config(page_title="NexaBuild Pro", page_icon=page_icon, layout="wide", initial_sidebar_state="collapsed")


# -------------------------------------------------------
# 1. CSS & Styling
# -------------------------------------------------------
def load_custom_css():
    st.markdown("""
    <style>
        :root { 
            --bg-color: #0d1117; 
            --card-bg: #161b22; 
            --neon-cyan: #00f3ff; 
            --vscode-bg: #1e1e1e; 
        }
        .stApp { background-color: var(--bg-color); color: #c9d1d9; }
        textarea { 
            background-color: var(--vscode-bg) !important; 
            color: #d4d4d4 !important; 
            font-family: 'Consolas', monospace !important; 
            border: 1px solid #30363d !important; 
        }
        .nav-container { 
            border-bottom: 1px solid #30363d; 
            padding: 15px; 
            margin-bottom: 20px; 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            background: rgba(22, 27, 34, 0.95);
            position: sticky;
            top: 0;
            z-index: 999;
        }
        .stButton > button { 
            background: var(--neon-cyan) !important; 
            color: #000000 !important; 
            border: none; 
            font-weight: bold; 
        }
        .server-indicator { 
            padding: 5px 10px; 
            border-radius: 4px; 
            font-weight: bold; 
            font-size: 0.8rem; 
        }
        .on { background: rgba(0, 255, 0, 0.2); color: #00ff00; }
        .off { background: rgba(255, 0, 0, 0.2); color: #ff4444; }
        .footer {
            background: rgba(22, 27, 34, 0.95);
            padding: 15px;
            text-align: center;
            border-top: 1px solid #30363d;
            color: #94a3b8;
            font-size: 0.9rem;
        }
        .footer a { color: var(--neon-cyan); text-decoration: none; }
    </style>
    """, unsafe_allow_html=True)


load_custom_css()


# -------------------------------------------------------
# 2. Helper Functions (Sanitization & Server)
# -------------------------------------------------------

def sanitize_files(data):
    """
    Recursively flattens JSON to fix the 'write() argument must be str' error.
    Extracts real file content if the AI wrapped it in {"files": ...} or folders.
    """
    flat_files = {}
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, str):
                # This is a valid file
                flat_files[key] = value
            elif isinstance(value, dict):
                # This is a wrapper/folder -> extract files from inside it
                flat_files.update(sanitize_files(value))
    return flat_files


if "files" not in st.session_state: st.session_state.files = {}
if "page" not in st.session_state: st.session_state.page = "home"
if "chat" not in st.session_state: st.session_state.chat = []
if "project_meta" not in st.session_state: st.session_state.project_meta = {}
if "session_id" not in st.session_state: st.session_state.session_id = str(uuid.uuid4())[:8]
if "server_pid" not in st.session_state: st.session_state.server_pid = None
if "server_port" not in st.session_state: st.session_state.server_port = None

PREVIEW_DIR = os.path.join(BASE_DIR, f"live_preview_{st.session_state.session_id}")


def get_free_port():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


def kill_server():
    if st.session_state.server_pid:
        try:
            if sys.platform == "win32":
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(st.session_state.server_pid)])
            else:
                os.kill(st.session_state.server_pid, signal.SIGTERM)
        except:
            pass
        st.session_state.server_pid = None
        st.session_state.server_port = None


# Register cleanup on script exit
atexit.register(kill_server)


def start_universal_server(files):
    """Deploys the Universal Backend and starts it."""
    kill_server()

    # --- FIX: Ensure files are flat strings before writing ---
    safe_files = sanitize_files(files)
    # ---------------------------------------------------------

    if os.path.exists(PREVIEW_DIR):
        try:
            shutil.rmtree(PREVIEW_DIR)
        except:
            pass
    os.makedirs(PREVIEW_DIR, exist_ok=True)

    for name, content in safe_files.items():
        if name == "app.py": continue
        path = os.path.join(PREVIEW_DIR, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            print(f"Skipping file {name} due to error: {e}")

    template_path = os.path.join(BASE_DIR, "ai", "server_template.py")
    target_app_path = os.path.join(PREVIEW_DIR, "app.py")
    if os.path.exists(template_path):
        shutil.copy(template_path, target_app_path)
    else:
        st.error(f"Critical Error: Missing {template_path}. Cannot start backend.")
        return False

    port = get_free_port()
    st.session_state.server_port = port
    env = os.environ.copy()
    env["PORT"] = str(port)
    try:
        process = subprocess.Popen(
            [sys.executable, "app.py"],
            cwd=PREVIEW_DIR,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
        )
        st.session_state.server_pid = process.pid
        time.sleep(2)
        return True
    except Exception as e:
        st.error(f"Failed to start server: {e}")
        return False


# -------------------------------------------------------
# 3. UI Components
# -------------------------------------------------------
def render_header():
    logo_html = "⚡ NexaBuild"
    if logo_path:
        try:
            with open(logo_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            ext = logo_path.split('.')[-1].lower()
            mime = "image/svg+xml" if ext == "svg" else f"image/{ext}"
            logo_html = f'<img src="data:{mime};base64,{b64}" style="height:35px; vertical-align:middle; border-radius: 4px;"> NexaBuild <b>Pro</b>'
        except:
            pass
    st.markdown(
        f"""<div class="nav-container"><div style="font-size:1.5rem; color:white;">{logo_html}</div><div><a href="#" style="color:#00f3ff;">Upgrade</a></div></div>""",
        unsafe_allow_html=True)


def render_footer():
    st.markdown("""
    <div class="footer">
        &copy; 2025 NexaBuild Pro • Built with <a href="#">AI</a> • All rights reserved.
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
            submitted = st.form_submit_button("🚀 Launch Team", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        if submitted and prompt:
            manager = ProjectManager()
            with st.spinner("Agents working..."):
                try:
                    result = manager.create_website(prompt)
                    if result:
                        # --- FIX: Sanitize immediately on creation ---
                        clean_files = sanitize_files(result["files"])
                        st.session_state.files = clean_files
                        st.session_state.project_meta = {"plan": result["plan"], "design": result["design"]}
                        st.session_state.chat.extend(
                            [("user", prompt), ("ai", "Project ready! Universal Backend Attached.")])
                        st.session_state.page = "workspace"
                        start_universal_server(clean_files)
                        st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
    render_footer()


# -------------------------------------------------------
# 5. Page: Workspace
# -------------------------------------------------------
def render_workspace():
    # --- FIX: Auto-sanitize session state on load (fixes existing corrupt sessions) ---
    if st.session_state.files:
        st.session_state.files = sanitize_files(st.session_state.files)
    # ----------------------------------------------------------------------------------

    render_header()
    c1, c2 = st.columns([3, 1])
    with c1:
        st.subheader("🛠️ Developer Workspace")
    with c2:
        if st.button("🏠 New Project"):
            kill_server()
            st.session_state.page, st.session_state.files, st.session_state.chat = "home", {}, []
            st.rerun()
    st.markdown("---")

    with st.sidebar:
        st.subheader("💬 Chat")
        if st.session_state.project_meta:
            with st.expander("Plan"): st.json(st.session_state.project_meta.get("plan"))
        for r, m in st.session_state.chat:
            if r == "user":
                st.info(f"You: {m}")
            else:
                st.success(f"Team: {m}")
        if i := st.chat_input("Changes?"):
            st.session_state.chat.append(("user", i))
            mgr = ProjectManager()
            with st.spinner("Coding..."):
                if u := mgr.edit_website(i, st.session_state.files):
                    # --- FIX: Sanitize updates too ---
                    clean_updates = sanitize_files(u)
                    st.session_state.files.update(clean_updates)
                    st.session_state.chat.append(("ai", "Updated."))
                    if st.session_state.server_pid: start_universal_server(st.session_state.files)
                    st.rerun()

    t1, t2, t3 = st.tabs(["👁️ Preview", "💻 Code", "🚀 Deploy"])
    with t1:
        c_ctrl, c_stat = st.columns([1, 3])
        with c_ctrl:
            if st.button("🔄 Restart Server"):
                start_universal_server(st.session_state.files)
                st.rerun()
        with c_stat:
            if st.session_state.server_pid:
                st.markdown(
                    f"<span class='server-indicator on'>● Universal Backend Active (Port {st.session_state.server_port})</span>",
                    unsafe_allow_html=True)
            else:
                st.markdown("<span class='server-indicator off'>● Server Offline</span>", unsafe_allow_html=True)
        st.markdown("---")
        if st.session_state.server_pid:
            st.components.v1.iframe(f"http://localhost:{st.session_state.server_port}", height=800, scrolling=True)
        else:
            st.warning("Server is offline. Click 'Restart Server' to boot up the Universal Backend.")
    with t2:
        c_list, c_edit = st.columns([1, 3])
        with c_list:
            f_sel = st.radio("File", list(st.session_state.files.keys())) if st.session_state.files else None
        with c_edit:
            if f_sel:
                # Check if content is actually a string before displaying
                file_content = st.session_state.files[f_sel]
                if not isinstance(file_content, str):
                    file_content = str(file_content)

                new_code = st.text_area("Edit", file_content, height=600, key=f"e_{f_sel}")
                if new_code != str(st.session_state.files[f_sel]) and st.button("Save"):
                    st.session_state.files[f_sel] = new_code
                    start_universal_server(st.session_state.files)
                    st.rerun()
    with t3:
        if st.session_state.files:
            st.download_button("⬇️ ZIP", create_zip_bytes(st.session_state.files), "site.zip", "application/zip")
            repo = st.text_input("Repo Name", "nexa-site")
            tok = st.text_input("GitHub Token", type="password")
            if st.button("Deploy"):
                try:
                    st.success(
                        f"Live: {GitHubDeployer(tok).deploy_to_github_pages(repo, st.session_state.files)['url']}")
                except Exception as e:
                    st.error(f"Error: {e}")
    render_footer()


if st.session_state.page == "home":
    render_home()
else:
    render_workspace()