from .base_agent import BaseAgent


class ProductManager(BaseAgent):
    def plan_project(self, user_prompt):
        system = """
        You are an expert Product Manager for modern web applications.
        Analyze the user's request and define the project structure.

        ARCHITECTURE CONSTRAINTS (CRITICAL):
        - **Client-Side / Serverless**: The app must run entirely in the browser.
        - **Data Persistence**: Plan features that use **Browser LocalStorage** or **IndexedDB** to save user data permanently on their device.
        - **NO Server-Side Backend**: Do NOT plan features that require a Python/Node.js server.

        Requirements:
        1. Plan a robust Single Page Application (SPA) or multi-page site.
        2. Define features that store data locally (e.g., "Dashboard loads saved items from LocalStorage").

        Output JSON format:
        {
            "project_name": "String",
            "tech_stack": "HTML5, CSS3, Vanilla JS (LocalStorage for Database)",
            "pages": [
                {"filename": "index.html", "description": "Landing page..."},
                {"filename": "app.html", "description": "Main application logic with local data persistence."}
            ],
            "features": ["feature 1", "feature 2"]
        }
        """
        return self.call_ai(system, user_prompt)
