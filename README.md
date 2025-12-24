# Gemini Project Coder - AI Assistant (v10.0)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Gemini API](https://img.shields.io/badge/Google-Gemini%20API-orange)
![License](https://img.shields.io/badge/License-MIT-green)

**Gemini Project Coder** is a powerful, local GUI desktop application designed to assist developers (optimized for Minecraft/Spigot/Paper, but usable for any code) by integrating Google's Gemini models directly with your local project files.

It allows you to "chat" with your entire codebase, send screenshots of errors, and switch AI models on the fly.

## 🚀 Key Features

*   **📂 Full Project Scanning:** Recursively scans your folder and loads code files (`.java`, `.yml`, `.json`, etc.) into the AI's context.
*   **🧠 Context Caching Support:** Automatically manages Google's Context Caching for large projects (>32k tokens) to save costs and improve performance.
*   **🔄 Hot-Swap Models:** Switch between `Gemini 1.5 Flash`, `Pro`, or `Exp` models instantly during a conversation without losing context.
*   **🖼️ Multimodal Support:** Paste images directly from your clipboard (CTRL+V) to analyze screenshots or errors.
*   **💾 Session Manager:** Automatically saves your chat history. Resume conversations days later with full context restoration.
*   **🌍 Internationalization:** Instant UI language switching (English / Polish).
*   **✨ UX Enhancements:** Syntax highlighting, code copying, text selection (right-click menu), and auto-scroll control.

## 🛠️ Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/gemini-project-coder.git
    cd gemini-project-coder
    ```

2.  **Install dependencies:**
    ```bash
    pip install customtkinter google-generativeai Pillow
    ```

3.  **Run the application:**
    ```bash
    python main.py
    ```
    *(Replace `main.py` with the actual filename if different)*

## 📖 Usage Guide

1.  **API Key:** Paste your Google Gemini API Key in the settings panel (Get one at [Google AI Studio](https://aistudio.google.com/)).
2.  **Select Folder:** Click **"Project Folder"** and select the root directory of your code.
3.  **Scan:** Click **"1. 📂 Scan Project"**. The app will read your files and prepare the AI context.
    *   *Note: If the project is large (>32k tokens), enable "Use Context Caching" to save API costs.*
4.  **Chat:** Type your query or paste an image (CTRL+V) and hit Send.
5.  **Context Menu:** You can right-click on the chat text to Copy/Select All.

## ⚙️ Requirements

*   Python 3.10 or higher
*   Google AI Studio API Key (Free tier available)
*   Active internet connection

## 📸 Screenshots

*(Add your screenshots here)*

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## 📜 License

[MIT](https://choosealicense.com/licenses/mit/)
