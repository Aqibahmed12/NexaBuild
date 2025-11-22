from .base_agent import BaseAgent
import json


class Developer(BaseAgent):
    def write_code(self, project_plan, design_system):
        system = f"""
        You are a Senior Full-Stack Developer.
        Write the COMPLETE code for the website based on the Plan and Design.

        ARCHITECTURE RULES:
        - **Universal Backend**: You have a pre-built backend running at `/api/`.
        - **NO Python Files**: Do NOT write `app.py` or `main.py`. It is already provided by the system.
        - **Focus on JS**: Write robust JavaScript to fetch/save data using the API.

        API DOCUMENTATION (Use this for "Real" functionality):
        1. **Save Data**: `POST /api/{{collection_name}}` (Body: JSON object)
           Example: `await fetch('/api/todos', {{ method: 'POST', headers: {{'Content-Type': 'application/json'}}, body: JSON.stringify({{task: 'Buy milk'}}) }})`
        2. **Get Data**: `GET /api/{{collection_name}}`
           Example: `const res = await fetch('/api/todos'); const todos = await res.json();`
        3. **Delete**: `DELETE /api/{{collection_name}}/{{id}}`

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
            "script.js": "// Uses fetch('/api/...') for real data\\n..."
        }}
        """

        prompt = f"""
        Project Plan: {json.dumps(project_plan)}
        Design System: {json.dumps(design_system)}

        Generate the files. Build a fully functional, data-driven application.
        """
        return self.call_ai(system, prompt)

    def modify_code(self, user_msg, current_files):
        system = """
        You are a Senior Developer. Update the code based on the request.
        Keep using the Universal Backend (/api/ endpoints) for data. 
        Do NOT write python files.
        """
        prompt = f"""
        Request: {user_msg}
        Current Files: {json.dumps(current_files)}
        """
        return self.call_ai(system, prompt)