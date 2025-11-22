from .base_agent import BaseAgent
import json


class Developer(BaseAgent):
    def write_code(self, project_plan, design_system):
        system = f"""
        You are a Senior Full-Stack Developer.
        Write the COMPLETE code for the website based on the Plan and Design.

        ARCHITECTURE RULES:
        - **Client-Side Logic Only**: There is NO external Python backend.
        - **Data Persistence**: You MUST implement a custom "backend" in JavaScript using `localStorage`.
        - **CRUD Operations**: Implement functions to Create, Read, Update, and Delete data directly in the browser.
        - **No External API Calls**: Do NOT fetch from `/api/` or `http://localhost`. All logic must run in the browser.

        IMPLEMENTATION DETAILS:
        - Create a helper class or functions (e.g., `DataManager`) to handle `localStorage`.
        - Example: `saveTask(task) {{ let tasks = JSON.parse(localStorage.getItem('tasks')||'[]'); tasks.push(task); localStorage.setItem('tasks', JSON.stringify(tasks)); }}`
        - Ensure the UI updates immediately after data changes.

        DESIGN RULES:
        - Colors: {json.dumps(design_system.get('color_palette'))}
        - Style: {design_system.get('ui_style')}
        - CSS: Use the `styles.css` file for all custom styling.

        OUTPUT FORMAT:
        Return a JSON object where keys are filenames.
        Example:
        {{
            "index.html": "...",
            "styles.css": "...",
            "script.js": "// Contains all logic and localStorage handling\\n..."
        }}
        """

        prompt = f"""
        Project Plan: {json.dumps(project_plan)}
        Design System: {json.dumps(design_system)}

        Generate the files. Build a fully functional, data-driven application using Client-Side Storage.
        """
        return self.call_ai(system, prompt)

    def modify_code(self, user_msg, current_files):
        system = """
        You are a Senior Developer. Update the code based on the request.
        Maintain the Client-Side architecture (LocalStorage).
        Do NOT add external API calls.
        """
        prompt = f"""
        Request: {user_msg}
        Current Files: {json.dumps(current_files)}
        """
        return self.call_ai(system, prompt)
