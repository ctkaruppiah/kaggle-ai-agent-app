# ⚡ Antigravity Chat

A sleek, premium, and fully responsive Python chatbot interface built with **Streamlit** and the new **Google GenAI SDK**, featuring real-time streaming, chat history, custom configurations, and adaptive dark/light themes.

---

## ✨ Features

- **Modern & Premium Design**: Custom CSS overrides for a beautiful, glassmorphic layout matching a zinc/shadcn-inspired palette.
- **Multilingual & Multi-Turn Chats**: Built-in support for continuous conversations with model history retention.
- **Live Streamed Responses**: Messages stream token-by-token using Gemini's streaming capabilities.
- **Configurable Settings**: 
  - Choose between `gemini-2.5-flash` and `gemini-2.5-pro`.
  - Adjust creativity with a **Temperature** slider.
  - Set custom **Max Output Tokens** and **System Instructions** on the fly.
- **Responsive Layout**: Adapts gracefully to all screen sizes.
- **Visual Theme Toggles**: Clean one-click toggle between Dark and Light mode.

---

## 🛠️ Setup & Installation

### 1. Clone or Open the Directory
Make sure you are in the application root directory:
```bash
cd c:/kaggle-ai-agent-app
```

### 2. Configure the Virtual Environment
Create and activate a virtual environment:
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🚀 Running the App

1. Set your **Gemini API Key** as an environment variable (optional, you can also enter it in the app UI):
   ```bash
   # Windows (CMD)
   set GEMINI_API_KEY=your_api_key_here

   # Windows (PowerShell)
   $env:GEMINI_API_KEY="your_api_key_here"

   # macOS / Linux
   export GEMINI_API_KEY="your_api_key_here"
   ```

2. Start the Streamlit application:
   ```bash
   streamlit run app.py
   ```

3. The application will automatically open in your web browser, typically at [http://localhost:8501](http://localhost:8501).

---

## 📂 Project Structure

```text
├── .venv/                 # Python Virtual Environment (ignored)
├── .gitignore             # Standard Git ignore configurations
├── requirements.txt       # Streamlit & Google GenAI SDK dependencies
├── app.py                 # Core Streamlit application & custom UI design
└── README.md              # Documentation
```
