import streamlit as st
import time
from .product_manager import ProductManager
from .designer import Designer
from .developer import Developer


class ProjectManager:
    def __init__(self):
        self.pm = ProductManager()
        self.designer = Designer()
        self.developer = Developer()

    def _render_status(self, placeholder, role, action, color, icon):
        """Renders an animated card for the active agent."""
        html_code = f"""
        <style>
            @keyframes pulse-border {{
                0% {{ border-color: {color}; box-shadow: 0 0 0px {color}; }}
                50% {{ border-color: {color}; box-shadow: 0 0 20px {color}; }}
                100% {{ border-color: {color}; box-shadow: 0 0 0px {color}; }}
            }}
            @keyframes blink {{
                0% {{ opacity: 0.2; }}
                20% {{ opacity: 1; }}
                100% {{ opacity: 0.2; }}
            }}
            .agent-box {{
                padding: 20px;
                border-radius: 12px;
                border: 2px solid {color};
                background: linear-gradient(90deg, rgba(22, 27, 34, 0.9) 0%, rgba(22, 27, 34, 0.6) 100%);
                display: flex;
                align-items: center;
                gap: 20px;
                margin-bottom: 20px;
                animation: pulse-border 2s infinite ease-in-out;
            }}
            .agent-icon {{
                font-size: 2.5rem;
                background: rgba(255,255,255,0.05);
                padding: 10px;
                border-radius: 50%;
            }}
            .agent-role {{
                font-weight: bold;
                font-size: 1.2rem;
                color: {color};
                margin-bottom: 5px;
            }}
            .agent-action {{
                color: #c9d1d9;
                font-family: monospace;
            }}
            .dot {{ font-weight: bold; font-size: 1.2rem; animation: blink 1.4s infinite both; }}
            .d1 {{ animation-delay: 0s; }}
            .d2 {{ animation-delay: 0.2s; }}
            .d3 {{ animation-delay: 0.4s; }}
        </style>

        <div class="agent-box">
            <div class="agent-icon">{icon}</div>
            <div>
                <div class="agent-role">{role}</div>
                <div class="agent-action">
                    {action}
                    <span class="dot d1">.</span>
                    <span class="dot d2">.</span>
                    <span class="dot d3">.</span>
                </div>
            </div>
        </div>
        """
        placeholder.markdown(html_code, unsafe_allow_html=True)

    def create_website(self, prompt):
        status_box = st.empty()

        # Step 1: Plan (Cyan)
        self._render_status(status_box, "Product Manager", "Analyzing requirements & planning structure", "#00f3ff",
                            "👨‍💼")
        plan = self.pm.plan_project(prompt)
        if not plan:
            status_box.error("Planning failed. Please try again.")
            return None

        # Step 2: Design (Purple)
        self._render_status(status_box, "Lead Designer", "Crafting visual identity & design system", "#bc13fe", "🎨")
        design = self.designer.create_design_system(plan)

        # Step 3: Develop (Green)
        # Initial status while waiting for AI API response
        self._render_status(status_box, "Senior Developer", "Architecting solution & generating logic...", "#00ff99",
                            "👨‍💻")

        files = self.developer.write_code(plan, design)

        # --- Animated File Writing Effect ---
        if files:
            for filename in files:
                # Update the UI to show exactly which file is being "written"
                self._render_status(status_box, "Senior Developer", f"Writing {filename}...", "#00ff99", "👨‍💻")
                # Add a small delay so the user can see it happen
                time.sleep(0.7)

            # Final connection step
            self._render_status(status_box, "Senior Developer", "Connecting Universal Backend API...", "#00ff99", "🔌")
            time.sleep(0.8)

        # Clear the animation when done
        status_box.empty()

        return {
            "files": files,
            "plan": plan,
            "design": design
        }

    def edit_website(self, prompt, current_files):
        status_box = st.empty()
        # Edit Mode (Orange)
        self._render_status(status_box, "Senior Developer", "Reading code & applying changes", "#ffaa00", "🛠️")

        result = self.developer.modify_code(prompt, current_files)

        if result:
            # Simulate applying changes to specific files
            for filename in result:
                self._render_status(status_box, "Senior Developer", f"Updating {filename}...", "#ffaa00", "🛠️")
                time.sleep(0.5)

        status_box.empty()
        return result