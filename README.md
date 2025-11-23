# ⚡ NexaBuild - Professional Agentic AI Website Builder

![NexaBuild Banner](images/logo.png)

> **Built for the HEC Generative AI Hackathon 2025** > *Turning text prompts into full-stack, deployable web applications in seconds.*

---

## 🚀 Overview

**NexaBuild** is an intelligent, multi-agent AI platform that democratizes software development. Unlike standard code generators that just output snippets, NexaBuild acts as a **complete virtual development team**. 

It takes a simple natural language prompt (e.g., *"Build a personal finance tracker"*) and orchestrates a team of AI agents to **Plan**, **Design**, and **Code** a fully functional, persistent web application—running entirely in the browser.

## 🏆 Hackathon Context
This project was developed specifically for the **HEC Generative AI Hackathon**.  
**Mission:** To solve the "Concept-to-Code" gap for students and non-technical founders by providing a tool that builds *and* deploys production-ready apps without vendor lock-in.

---

## ✨ Key Features

* **🤖 Multi-Agent AI Architecture:**
    * **Product Manager Agent:** Analyzes requirements and creates a comprehensive project plan.
    * **Designer Agent:** Crafts a custom design system (Color palettes, Typography, Glassmorphism UI).
    * **Developer Agent:** Writes robust, error-free HTML/CSS/JS code with client-side logic.

* **💾 Client-Side "Serverless" Architecture:** * Generated apps use **LocalStorage/IndexedDB** for data persistence. 
    * This means apps are **instant**, **crash-proof**, and require **no external backend** to save data.

* **🛠️ Live Developer Workspace:** * Real-time split-screen preview.
    * **NexaBot Assistant:** An embedded AI chat companion to help debug or iterate on the design.
    * Code editor for manual tweaks.

* **☁️ One-Click Deployment:** * Direct integration with **GitHub API**.
    * Instantly publishes the user's site to **GitHub Pages** (Live URL generation).
    * **Export to ZIP** for local ownership.

---

## 🏗️ System Architecture

NexaBuild utilizes a sequential chain of specialized AI agents powered by **Google Gemini 1.5 Flash**:

```mermaid
graph LR
    User[User Prompt] --> PM[Product Manager Agent]
    PM -->|Project Plan| Des[Designer Agent]
    Des -->|Design System| Dev[Developer Agent]
    Dev -->|HTML/CSS/JS| Preview[Live Preview]
    Dev -->|Files| Deploy[GitHub/Zip Export]
🛠️ Installation & Setup
Follow these steps to run NexaBuild locally:

Prerequisites
Python 3.10+

A Google Gemini API Key

1. Clone the Repository
Bash

git clone [https://github.com/your-username/nexabuild.git](https://github.com/your-username/nexabuild.git)
cd nexabuild
2. Install Dependencies
Bash

pip install -r requirements.txt
(Dependencies include: streamlit, google-generativeai, requests)

3. Configure API Key
Create a .streamlit/secrets.toml file (or use environment variables):

Ini, TOML

# .streamlit/secrets.toml
API_KEY = "YOUR_GEMINI_API_KEY"
4. Run the Application
Bash

streamlit run main.py
📖 How to Use
🚀 Create: Navigate to the Home tab. Enter your idea (e.g., "A To-Do list app with a dark neon theme"). Click Generate.

👀 Visualize: Watch as the agents (PM, Designer, Developer) communicate and build your app in real-time.

💬 Refine: Use the Workspace to chat with the team. Type "Change the background to blue" or "Add a delete button" to instantly modify the code.

🌍 Deploy: Go to the Deploy tab. Enter your GitHub token to publish your site to the web instantly, or download the Source Code as a ZIP.

👥 The Team
Aqib Ahmed - Lead Developer & AI Architect
Sanaullah - Frontend & UI/UX
Komal - Documentation & Research
Tahir - Support

This project is open-source and available under the MIT License.

<div align="center"> <sub>Made with ❤️ by the NexaBuild Team for the HEC Hackathon</sub> </div>
