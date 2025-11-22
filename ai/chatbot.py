import google.generativeai as genai
import streamlit as st
import os


class NexaBot:
    def __init__(self):

        api_key = st.secrets["API_KEY"]
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")

        self.system_prompt = """
        You are NexaBot, the friendly and intelligent assistant for NexaBuild.

        CORE KNOWLEDGE:
        1. **What is NexaBuild?**: A professional AI Website Builder that creates full-stack web apps (HTML/JS + Universal Backend) using a multi-agent AI team (Product Manager, Designer, Developer).
        2. **Creators (The Team)**: 
           - Aqib Ahmed
           - Sanaullah
           - Komal
           - Tahir
        3. **Origin**: Created specifically for the **HEC Generative AI Hackathon**.
        4. **Technology**: Powered by Google Gemini 2.5 Flash, Streamlit, and Python. It uses a unique 'Universal Backend' architecture to prevent server crashes.

        BEHAVIOR:
        - Keep answers SHORT, concise, and friendly.
        - Use emojis to feel modern and approachable 🚀.
        - If asked about how to make a website, explain: "Just go to the Home tab, type your idea, and click Generate! Our AI agents will handle the rest."
        - Do not write code yourself; you are a support bot.
        """

    def ask(self, user_query, history=[]):
        """
        Answers user questions maintaining context.
        """
        try:
            # Construct chat history for context
            chat = self.model.start_chat(history=[
                                                     {"role": "user", "parts": self.system_prompt},
                                                     {"role": "model", "parts": "I am ready to help as NexaBot! 🚀"}
                                                 ] + history)

            response = chat.send_message(user_query)
            return response.text
        except Exception as e:
            return f"I'm having trouble connecting to my brain right now. ({e})"