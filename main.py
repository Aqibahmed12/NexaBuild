# main.py — Professional Agentic AI Website Builder (Cloud Compatible Version)

import streamlit as st
import os
import sys
import time
import base64
import uuid
import re

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
# 1. MOCK BACKEND SCRIPT (The Cloud Fix)
# -------------------------------------------------------
# This JavaScript intercepts API calls and saves data to the browser's LocalStorage.
# It replaces the need for a Python Flask server.
MOCK_BACKEND_SCRIPT = """
<script>
(function() {
    console.log("⚡ NexaBuild Cloud Mode: Mock Backend Activated");
    const ORIGINAL_FETCH = window.fetch;
    const DB_PREFIX = 'nexabuild_db_';

    window.fetch = async (url, options) => {
        // Only intercept calls to our API
        if (!url.startsWith('/api/')) return ORIGINAL_FETCH(url, options);

        const parts = url.split('/').filter(p => p); // e.g., ['api', 'todos', '123']
        const collection = parts[1];
        const id = parts[2];
        const method = options?.method || 'GET';

        // Simulate network delay
        await new Promise(r => setTimeout(r, 50));

        // Load collection from LocalStorage
        let data = JSON.parse(localStorage.getItem(DB_PREFIX + collection) || '[]');

        // --- 1. GET (List) ---
        if (method === 'GET') {
            return new Response(JSON.stringify(data), {status: 200});
        } 
        
        // --- 2. POST (Create/Update) ---
        if (method === 'POST') {
            const body = JSON.parse(options.body);
            // Generate ID if missing
            const newItem = { ...body, id: body.id || crypto.randomUUID() };
            
            // Upsert logic
            const idx = data.findIndex(d => d.id === newItem.id);
            if (idx >= 0) data[idx] = newItem;
            else data.push(newItem);
            
            localStorage.setItem(DB_PREFIX + collection, JSON.stringify(data));
            return new Response(JSON.stringify({status: "success", id: newItem.id, data: newItem}), {status: 200});
        }

        // --- 3. DELETE ---
        if (method === 'DELETE' && id) {
             data = data.filter(d => d.id !== id);
             localStorage.setItem(DB_PREFIX + collection, JSON.stringify(data));
             return new Response(JSON.stringify({status: "deleted"}), {status: 200});
        }

        return new Response("Not Found", {status: 404});
    };
})();
</script>
"""

# -------------------------------------------------------
# 2. CSS & Styling
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
# 3. Helper Functions
# -------------------------------------------------------

def sanitize_files(data):
    """
    Recursively flattens JSON to fix the 'write() argument must be str' error.
    """
    flat_files = {}
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, str):
                flat_files[key] = value
            elif isinstance(value, dict):
                flat_files.update(sanitize_files(value))
    return flat_files

# Session State
if "files" not in st.session_state: st.session_state.files = {}
if "page" not in st.session_state: st.session_state.page = "home"
if "chat" not in st.session_state: st.session_state.chat = []
if "project_meta" not in st.session_state: st.session_state.project_meta = {}
if "session_id" not in st.session_state: st.session_state.session_id = str(uuid.uuid4())[:8]

# -------------------------------------------------------
# 4. UI Components
# -------------------------------------------------------
def render_header():
    logo_html = "⚡ NexaBuild"
    if logo_path:
        try:
            with open(logo_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            ext = logo_path.split('.')[-1].lower()
            mime = "image/svg+xml" if ext == "svg" else f"image/{ext}"
            logo_html = f'<img src="data:{mime};base64,{b64}" style="height:35px; vertical-align:middle; border-radius: 4px;"> NexaBuild'
        except:
            pass
    st.markdown(
        f"""<div class="nav-container"><div style="font-size:1.5rem; color:white;">{logo_html}</div><div><a href="#" style="color:#00f3ff;">NexaChat</a></div></div>""",
        unsafe_allow_html=True)

def render_footer():
    st.markdown("""
    <div class="footer">
        &copy; 2025 NexaBuild Pro • Built with <a href="#">AI</a> • All rights reserved.
    </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------------
# 5. Page: Home
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
                        # Sanitize files immediately
                        clean_files = sanitize_files(result["files"])
                        st.session_state.files = clean_files
                        st.session_state.project_meta = {"plan": result["plan"], "design": result["design"]}
                        st.session_state.chat.extend(
                            [("user", prompt), ("ai", "Project ready! Mock Backend Attached.")])
                        st.session_state.page = "workspace"
                        st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
    render_footer()

# -------------------------------------------------------
# 6. Page: Workspace
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
                    clean_updates = sanitize_files(u)
                    st.session_state.files.update(clean_updates)
                    st.session_state.chat.append(("ai", "Updated."))
                    st.rerun()

    t1, t2, t3 = st.tabs(["👁️ Preview", "💻 Code", "🚀 Deploy"])
    
    # --- PREVIEW TAB (Cloud Compatible) ---
    with t1:
        if st.session_state.files:
            # 1. Combine HTML, CSS, JS into one string
            gen = WebsiteGenerator()
            html_content = gen.combine_to_html(st.session_state.files)
            
            # 2. Inject Mock Backend Script
            # This ensures API calls work without a backend server
            if "</body>" in html_content:
                html_content = html_content.replace("</body>", f"{MOCK_BACKEND_SCRIPT}</body>")
            else:
                html_content += MOCK_BACKEND_SCRIPT
                
            # 3. Render static HTML
            st.components.v1.html(html_content, height=800, scrolling=True)
        else:
            st.warning("No files generated yet.")

    # --- CODE TAB ---
    with t2:
        c_list, c_edit = st.columns([1, 3])
        with c_list:
            f_sel = st.radio("File", list(st.session_state.files.keys())) if st.session_state.files else None
        with c_edit:
            if f_sel:
                file_content = st.session_state.files[f_sel]
                if not isinstance(file_content, str):
                    file_content = str(file_content)

                new_code = st.text_area("Edit", file_content, height=600, key=f"e_{f_sel}")
                if new_code != str(st.session_state.files[f_sel]) and st.button("Save"):
                    st.session_state.files[f_sel] = new_code
                    st.rerun()
    
    # --- DEPLOY TAB ---
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
