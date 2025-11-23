# main.py — Professional Agentic AI Website Builder (Cloud Compatible Version)
# UI/CSS/JS changes only — no backend or logic modifications.

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
# 1. CSS, JS & Styling (UI only)
# -------------------------------------------------------
def load_custom_css_and_js():
    # CSS: header sticky, popover and button styles, neon glow for chat box
    # JS: Makes the NexaBot popover open button movable via double-click/double-tap then drag.
    st.markdown(
    """
    <style>
    :root{
        --bg-color:#0d1117;
        --card-bg:#161b22;
        --border-color:#30363d;
        --neon-cyan:#00f3ff;
        --neon-purple:#bc13fe;
        --text-primary:#c9d1d9;
        --text-white:#ffffff;
        --streamlit-header-height:56px; /* adjust if needed */
        --nav-offset: calc(var(--streamlit-header-height) + 12px);
        --nav-height: 64px;
        --nav-z: 1050;
        --popover-z: 2150;
        --max-content-width:1200px;
    }

    /* Global app and spacing - add top padding for sticky header */
    .stApp {
        background-color: var(--bg-color);
        color: var(--text-primary);
        padding-top: calc(var(--nav-offset) + var(--nav-height) + 12px);
    }
    .block-container{
        max-width: var(--max-content-width);
        margin-left:auto; margin-right:auto; padding-left:20px; padding-right:20px;
    }
    h1,h2,h3{ color:var(--text-white) !important; font-family: 'Inter', sans-serif; }

    /* Sticky Header */
    .nav-container{
        position: fixed;
        top: var(--nav-offset);
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
        display:flex; align-items:center; justify-content:space-between;
        border-radius:12px;
        box-shadow:0 6px 24px rgba(0,0,0,0.6);
    }
    .nav-logo{
        font-size:1.25rem; font-weight:800;
        background:linear-gradient(90deg,var(--neon-cyan),var(--neon-purple));
        -webkit-background-clip:text; -webkit-text-fill-color:transparent;
        display:flex; gap:10px; align-items:center;
    }
    .nav-links{ display:flex; gap:22px; align-items:center; }
    .nav-links a{
        color:#c9d1d9; text-decoration:none; font-size:0.95rem; font-weight:700;
        padding:6px 10px; border-radius:8px; transition:all 0.25s ease;
    }
    .nav-links a:hover{
        color:#000; background:var(--neon-cyan); transform:translateY(-2px) scale(1.03);
        box-shadow:0 8px 30px rgba(0,243,255,0.12);
    }

    /* Buttons: generic consistency */
    .stButton>button,
    [data-testid="stFormSubmitButton"] > button,
    button[data-testid="stPopoverOpenButton"],
    button[aria-label*="NexaBot"],
    button[title*="NexaBot"]{
        background-color: var(--neon-cyan) !important;
        color: #000 !important;
        border:none !important;
        font-weight:800 !important;
        padding:8px 14px !important;
        border-radius:10px !important;
        transition: all 0.18s ease-in-out !important;
        box-shadow: 0 6px 18px rgba(0,243,255,0.06) !important;
    }
    .stButton>button:hover,
    [data-testid="stFormSubmitButton"] > button:hover,
    button[data-testid="stPopoverOpenButton"]:hover,
    button[aria-label*="NexaBot"]:hover{
        transform:translateY(-2px) scale(1.03) !important;
        box-shadow:0 0 30px rgba(0,243,255,0.18) !important;
    }

    /* Ensure the popover button (and inner svg/text) adopt our colors */
    button[data-testid="stPopoverOpenButton"] span,
    button[aria-label*="NexaBot"] span,
    button[data-testid="stPopoverOpenButton"] svg,
    button[aria-label*="NexaBot"] svg,
    [data-testid="stPopover"] > button svg,
    [data-testid="stPopover"] > button span{
        color:#000 !important; fill:#000 !important;
    }

    /* Popover container and body should be above the nav */
    div[data-testid="stPopover"]{
        z-index: calc(var(--popover-z) + 1) !important;
        position: relative !important;
    }
    div[data-testid="stPopoverBody"]{
        z-index: calc(var(--popover-z) + 2) !important;
        background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(250,250,250,0.96));
        color:#000;
        border-radius:12px;
        padding:12px !important;
        margin-top:8px !important;
        box-shadow: 0 12px 60px rgba(0,0,0,0.45), 0 0 30px rgba(0,243,255,0.12) !important;
        border:1px solid rgba(0,243,255,0.12) !important;
    }

    /* Neon glowing border for central chat box inside popover */
    div[data-testid="stPopoverBody"] .stChat,
    div[data-testid="stPopoverBody"] .stChatMessageBlock,
    div[data-testid="stPopoverBody"] div[data-testid="stChatMessageContent"]{
        border-radius:12px !important;
        box-shadow:
            0 2px 0 rgba(0,0,0,0.6) inset,
            0 8px 30px rgba(0,0,0,0.6),
            0 0 20px rgba(0,243,255,0.14),
            0 0 6px rgba(0,243,255,0.28);
        border:1px solid rgba(0,243,255,0.28) !important;
        background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(250,250,250,0.96)) !important;
    }
    div[data-testid="stPopoverBody"] div[data-testid="stChatMessageContent"] p{
        color:#001019 !important; font-weight:500 !important;
    }
    div[data-testid="stPopoverBody"] textarea:focus,
    div[data-testid="stPopoverBody"] input:focus{
        outline:none !important;
        box-shadow: 0 0 24px rgba(0,243,255,0.32) !important;
        border:1px solid rgba(0,243,255,0.4) !important;
    }

    /* Make sure the floating button when positioned uses pointer cursor */
    #nexabot-floating-btn {
        cursor: grab !important;
        touch-action: none; /* handle touches ourselves */
    }
    #nexabot-floating-btn.dragging { cursor: grabbing !important; }

    /* Small visual indicator when in "move" mode */
    #nexabot-floating-btn[data-move="true"] {
        box-shadow: 0 0 36px rgba(0,243,255,0.25) !important;
        transform: scale(1.02) !important;
        border-radius: 12px !important;
    }
    </style>

    <!-- JS: make NexaBot popover button movable via double-click/double-tap and drag -->
    <script>
    (function(){
        const SELECTORS = [
            'button[data-testid="stPopoverOpenButton"]',
            'button[aria-label*="NexaBot"]',
            'button[title*="NexaBot"]',
            '[data-testid="stPopover"] > button'
        ];

        const STORAGE_KEY = 'nexabot_position_v1';
        const MOVE_FLAG = 'nexabot_move_enabled_v1';
        const POLL_INTERVAL = 300;
        const DOUBLE_TAP_MS = 350;

        function findBtn(){
            for(const s of SELECTORS){
                const el = document.querySelector(s);
                if(el) return el;
            }
            return null;
        }

        function applyFloatingStyle(btn){
            btn.id = 'nexabot-floating-btn';
            // Make fixed so we can move it anywhere
            btn.style.position = 'fixed';
            btn.style.zIndex = (parseInt(getComputedStyle(document.documentElement).getPropertyValue('--popover-z')) || 2150) + 10;
            btn.style.right = '24px';
            btn.style.top = 'calc(var(--nav-offset) + 8px)';
            btn.style.transition = 'none';
            btn.setAttribute('data-move', 'false');
            // Ensure icons/text inside show our colors
            btn.querySelectorAll('svg, span').forEach(i => {
                try { i.style.color = '#000'; i.style.fill = '#000'; } catch(e){}
            });
        }

        function restorePosition(btn){
            try{
                const raw = localStorage.getItem(STORAGE_KEY);
                if(!raw) return;
                const pos = JSON.parse(raw);
                if(typeof pos.left === 'number' && typeof pos.top === 'number'){
                    btn.style.left = pos.left + 'px';
                    btn.style.top = pos.top + 'px';
                    btn.style.right = 'auto';
                }
            }catch(e){}
        }

        function savePosition(btn){
            try{
                const rect = btn.getBoundingClientRect();
                const pos = { left: rect.left, top: rect.top };
                localStorage.setItem(STORAGE_KEY, JSON.stringify(pos));
            }catch(e){}
        }

        function enableMoveHandling(btn){
            let dragging = false;
            let dragOffset = {x:0,y:0};
            let lastTap = 0;
            let moveEnabled = false;

            // Allow double-click / double-tap to toggle move mode.
            btn.addEventListener('click', (ev) => {
                const now = Date.now();
                if(now - lastTap < DOUBLE_TAP_MS){
                    // double tap/click detected
                    moveEnabled = !moveEnabled;
                    btn.setAttribute('data-move', moveEnabled ? 'true' : 'false');
                    // store flag
                    try { localStorage.setItem(MOVE_FLAG, moveEnabled ? '1' : '0'); } catch(e){}
                }
                lastTap = now;
            }, {passive:true});

            // pointer events for mouse & touch
            btn.addEventListener('pointerdown', (ev) => {
                // Only allow dragging when move mode enabled (to avoid accidental drags)
                const stored = localStorage.getItem(MOVE_FLAG);
                const storedFlag = stored === '1' ? true : false;
                if(!(storedFlag || btn.getAttribute('data-move') === 'true')) return;
                ev.preventDefault();
                btn.classList.add('dragging');
                dragging = true;
                btn.setPointerCapture(ev.pointerId);
                const rect = btn.getBoundingClientRect();
                dragOffset.x = ev.clientX - rect.left;
                dragOffset.y = ev.clientY - rect.top;
            });

            btn.addEventListener('pointermove', (ev) => {
                if(!dragging) return;
                ev.preventDefault();
                let left = ev.clientX - dragOffset.x;
                let top = ev.clientY - dragOffset.y;
                // keep onscreen boundaries
                const pad = 8;
                left = Math.max(pad, Math.min(left, window.innerWidth - btn.offsetWidth - pad));
                top = Math.max(pad, Math.min(top, window.innerHeight - btn.offsetHeight - pad));
                btn.style.left = left + 'px';
                btn.style.top = top + 'px';
                btn.style.right = 'auto';
            });

            btn.addEventListener('pointerup', (ev) => {
                if(!dragging) return;
                ev.preventDefault();
                dragging = false;
                btn.classList.remove('dragging');
                try{ btn.releasePointerCapture(ev.pointerId); }catch(e){}
                savePosition(btn);
            });

            // If user resizes window, keep button within bounds
            window.addEventListener('resize', () => {
                const rect = btn.getBoundingClientRect();
                const pad = 8;
                let left = rect.left;
                let top = rect.top;
                left = Math.max(pad, Math.min(left, window.innerWidth - btn.offsetWidth - pad));
                top = Math.max(pad, Math.min(top, window.innerHeight - btn.offsetHeight - pad));
                btn.style.left = left + 'px';
                btn.style.top = top + 'px';
                btn.style.right = 'auto';
                savePosition(btn);
            });
        }

        // Repeatedly attempt to find the button and apply handlers (handles Streamlit re-renders)
        let initialized = false;
        const observer = new MutationObserver(() => {
            const btn = findBtn();
            if(!btn) return;
            // If we already set up the ID and handlers on the same node, skip.
            if(btn.id === 'nexabot-floating-btn' && initialized) return;

            applyFloatingStyle(btn);
            restorePosition(btn);
            enableMoveHandling(btn);

            // Ensure the popover body is above the nav when opened (extra safety)
            const popBody = document.querySelector('div[data-testid="stPopoverBody"]');
            if(popBody){
                popBody.style.zIndex = (parseInt(getComputedStyle(document.documentElement).getPropertyValue('--popover-z')) || 2150) + 20;
                popBody.style.position = 'relative';
            }

            initialized = true;
        });

        // Start observing the app container for changes (Streamlit re-renders)
        const root = document.querySelector('#root') || document.body;
        observer.observe(root, { childList: true, subtree: true });

        // Also poll initially (in case MutationObserver missed initial render)
        setInterval(() => {
            const btn = findBtn();
            if(btn && btn.id !== 'nexabot-floating-btn'){
                applyFloatingStyle(btn);
                restorePosition(btn);
                enableMoveHandling(btn);
            }
        }, POLL_INTERVAL);

        // On load: read and set move mode from storage
        try {
            const stored = localStorage.getItem(MOVE_FLAG);
            if(stored === '1'){
                const existing = document.getElementById('nexabot-floating-btn');
                if(existing) existing.setAttribute('data-move', 'true');
            }
        } catch(e){}
    })();
    </script>
    """, unsafe_allow_html=True)

load_custom_css_and_js()

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
# 3. UI Components (unchanged behavior)
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

    c_nav, c_bot = st.columns([6, 1], gap="small")
    with c_nav:
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
        # Chatbot Button (Streamlit popover) - behavior unchanged.
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
