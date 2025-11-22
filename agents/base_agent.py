import os
import json
import google.generativeai as genai
import streamlit as st


class BaseAgent:
    def __init__(self, model_name="gemini-2.5-flash"):

        api_key = st.secrets["API_KEY"]
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def call_ai(self, system_instruction, user_prompt):
        full_prompt = f"""
        SYSTEM INSTRUCTION:
        {system_instruction}

        USER REQUEST:
        {user_prompt}

        Return ONLY valid JSON.
        """
        try:
            response = self.model.generate_content(full_prompt)
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