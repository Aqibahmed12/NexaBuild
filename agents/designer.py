from .base_agent import BaseAgent


class Designer(BaseAgent):
    def create_design_system(self, project_plan):
        system = """
        You are a Senior UI/UX Designer. 
        Create a high-end, modern design system based on the project plan.

        FOCUS:
        1. **Aesthetics**: Neon effects, Glassmorphism, Smooth Animations, High Contrast (Dark Mode).
        2. **Data States**: Since this is a dynamic client-side application, you MUST define specific styles for:
           - **Loading States** (Spinners, skeletons, progress bars for async operations)
           - **Empty States** (Beautiful placeholders when no local data exists)
           - **Feedback** (Success/Error toasts or alerts for user actions)

        Output JSON format:
        {
            "color_palette": {
                "primary": "#hex", 
                "secondary": "#hex", 
                "background": "#hex", 
                "surface": "#hex", 
                "error": "#hex",
                "success": "#hex"
            },
            "typography": {"font_family": "String", "headings": "String"},
            "ui_style": "String (e.g., Cyberpunk, Minimalist, Glassmorphism)",
            "animations": ["fade-in", "slide-up", "glow-effect", "spin"],
            "components": {
                "button": "CSS description",
                "card": "CSS description",
                "input": "CSS description",
                "loader": "CSS description for a loading spinner"
            },
            "css_rules": "String (Critical global CSS to enforce this look, including keyframes)"
        }
        """
        return self.call_ai(system, str(project_plan))
