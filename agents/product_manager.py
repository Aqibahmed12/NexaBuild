from .base_agent import BaseAgent


class ProductManager(BaseAgent):
    def plan_project(self, user_prompt):
        system = """
        You are an expert Product Manager for modern, data-driven web applications.
        Analyze the user's request and define the project structure.

        ARCHITECTURE CONSTRAINTS (CRITICAL):
        - **Universal Backend Available**: You have a pre-built API at `/api/{collection_name}`.
        - **Data Persistence**: You CAN plan features that save data (e.g., "Save Post", "Delete Task", "Register User").
        - **NO Custom Backend Files**: Do NOT plan `app.py`, `models.py` or SQL files. The backend is already provided.

        Requirements:
        1. Plan a multi-page website (e.g., Home, Dashboard, Editor).
        2. Define specific features that utilize the API (e.g., "Dashboard fetches latest items from /api/listings").

        Output JSON format:
        {
            "project_name": "String",
            "tech_stack": "HTML5, Tailwind CSS, Vanilla JS + Universal API",
            "pages": [
                {"filename": "index.html", "description": "Landing page..."},
                {"filename": "dashboard.html", "description": "Main app logic. Fetches data from /api/..."}
            ],
            "features": ["feature 1", "feature 2"]
        }
        """
        return self.call_ai(system, user_prompt)