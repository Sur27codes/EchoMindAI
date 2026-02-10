# ✨ EchoMindAI: Enterprise Intelligence

> **The Advanced RAG System with Vision, Voice, and Real-Time Agentic Capabilities.**

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)
![Status](https://img.shields.io/badge/Status-Active-success)

![EchoMindAI Dashboard](assets/images/dashboard_preview.png)

## 💡 What is EchoMindAI?

**EchoMindAI** bridges the gap between static document search and dynamic, agentic intelligence. Traditional RAG systems are often limited to text-only retrieval. We built an **"Enterprise Intelligence"** assistant that can:

- **Read** internal documents (PDFs, CSVs).
- **See** images and real-world objects.
- **Hear** complex voice commands.
- **Act** by searching the live web for real-time data.

All wrapped in a premium, consumer-grade user interface that feels far superior to standard internal tools.

---

## 🚀 Key Capabilities

| Feature | Description |
| :--- | :--- |
| **🧠 The Super-Brain** | A hybrid **RAG + Web Search** engine. It uses **FAISS** for internal docs and automatically falls back to **DuckDuckGo** for live queries, ensuring you never hit a dead end. |
| **👁️ Visual Intelligence** | Upload *any* image. The agent identifies products for shopping, recognizes landmarks for travel guides, or interprets complex data charts. |
| **🎤 Voice-First** | Powered by **Groq Whisper** for near-instant speech-to-text and **OpenAI Audio** for life-like responses. Completely hands-free. |
| **🌐 Live Agent Tools** | Real-time fetching of **Stock Prices**, **Global News**, **Weather**, and **Travel Bookings**. |

---

## 🎨 The "React-Like" UI Engine

EchoMindAI pushes **Streamlit** to its absolute limit, tricking it into behaving like a modern React application.

### The "Magic" Behind the Interface:

1.  **CSS Injection & Glassmorphism**:
    We inject a custom CSS engine (`styles.py`) that overrides default Streamlit styles with **Neon Gradients** and **Glassmorphism**, creating a premium feel.

2.  **The HTML Parsing Bridge**:
    LLMs often wrap HTML in Markdown code blocks. We wrote a robust **Stream Parser** that intercepts the LLM's output, strips the wrappers, and forces the browser to render raw HTML. This allows for rich **Product Cards** and **Financial Tickers** directly in the chat stream.

3.  **Dynamic Data Visualization**:
    The agent outputs a hidden JSON signature (`<!-- CHART_TOOL_JSON: ... -->`). The frontend detects this and instantly renders interactive **Plotly** charts.

---

## 🛠️ Technology Stack

| Component | Technology |
| :--- | :--- |
| **Frontend** | Streamlit + Custom HTML/CSS/JS Injection |
| **LLM Orchestration** | LangChain + OpenAI GPT-4o |
| **Vector DB** | FAISS (Facebook AI Similarity Search) |
| **Voice Stack** | Groq (STT) + OpenAI (TTS) |
| **Server** | MCP (Model Context Protocol) Implementation |

---

## 📸 Gallery

### Visual Intelligence & Data Analysis
![Visual Intelligence](assets/images/feature_demo_1.png)

### Live Agent Tools (News & Search)
![Live Tools](assets/images/feature_demo_2.png)

---

## 📖 Installation

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/Sur27codes/EchoMindAI.git
    cd EchoMindAI
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set Up Environment Secrets**:
    Create a `.env` file in the root directory:
    ```env
    OPENAI_API_KEY=sk-...
    GROQ_API_KEY=gsk-...
    ```

4.  **Run the Application**:
    ```bash
    streamlit run streamlit_app.py
    ```
