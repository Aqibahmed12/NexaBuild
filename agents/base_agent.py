import os
import json
import re
import google.generativeai as genai
import streamlit as st


class BaseAgent:
    def __init__(self, model_name="gemini-2.0-flash"):
        
        # Safe API Key Fallback
        api_key = None
        try:
            if "API_KEY" in st.secrets:
                api_key = st.secrets["API_KEY"]
        except Exception:
            pass
        if not api_key:
            api_key = os.environ.get("API_KEY", "")
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def call_ai(self, system_instruction, user_prompt, output_format="json"):
        formating_instruction = "Return ONLY valid JSON."
        if output_format == "xml":
            formating_instruction = 'Output each file wrapped in XML-like tags, for example:\n<file name="index.html">\n...\n</file>'

        full_prompt = f"""
        SYSTEM INSTRUCTION:
        {system_instruction}

        USER REQUEST:
        {user_prompt}
        
        {formating_instruction}
        """
        try:
            response = self.model.generate_content(full_prompt)
            if output_format == "xml":
                return self._extract_xml_files(response.text)
            return self._clean_json(response.text)
        except Exception as e:
            print(f"AI Error: {e}")
            return {}

    def _clean_json(self, text):
        text = text.strip()
        if text.startswith("```json"):
            text = text.replace("```json", "").replace("```", "")
        elif text.startswith("```"):
            text = text.replace("```", "")

        try:
            return json.loads(text)
        except:
            # Simple manual extraction if JSON is messy
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end != -1:
                try:
                    return json.loads(text[start:end])
                except:
                    pass
            return {}

    def _extract_xml_files(self, text):
        files = {}
        # Regex to capture <file name="something">content</file>
        pattern = re.compile(r'<file\s+name="([^"]+)">\s*(.*?)\s*</file>', re.DOTALL | re.IGNORECASE)
        matches = pattern.finditer(text)
        for match in matches:
            filename = match.group(1).strip()
            content = match.group(2).strip()
            files[filename] = content
        return files