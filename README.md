# ✨ EchoMindAI: Enterprise Intelligence

> **The Advanced RAG System with Vision, Voice, and Real-Time Agentic Capabilities.**

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)
![Status](https://img.shields.io/badge/Status-Active-success)

![EchoMindAI Dashboard](assets/images/dashboard_preview.png)

---

## 🧐 The Context & Problem

Traditional Retrieval-Augmented Generation (RAG) systems are powerful but often **limited** and **boring**. They typically only "read" text and output text, lacking the ability to interact with the real world or present information in an engaging way.

**The Goal:** To build an **"Enterprise Intelligence"** assistant that could not only "read" internal documents but also **"see"** images, **"hear"** voice commands, and **"act"** by searching the live web—all wrapped in a premium, consumer-grade user interface that feels far superior to standard internal tools.

---

## 💡 The Solution: A Multi-Modal Agent

We built a system that seamlessly integrates internal knowledge with external tools, creating a "Super-Brain" for enterprise users.

### 1. 🧠 The Super-Brain (Hybrid RAG)
A fail-safe intelligence engine. It utilizes **FAISS** for high-speed internal document retrieval. Crucially, if internal data is insufficient, it **automatically falls back** to **DuckDuckGo** live search, ensuring the user never hits a dead end.

### 2. 👁️ Visual Intelligence
Users can upload *any* image. The system uses vision models to analyze the image and triggers relevant agents:
- **Shopping Agent**: Identifies a shoe in a photo and finds the best prices online.
- **Travel Agent**: Recognizes a landmark and generates a travel itinerary.
- **Data Analyst**: Reads complex charts and graphs and summarizes the insights.

![Visual Intelligence Demo](assets/images/feature_demo_1.png)

### 3. 🎤 Voice-First Interaction
A complete hands-free experience. We integrated **Groq Whisper** for near-instant multi-lingual speech-to-text and **OpenAI Audio** for hyper-realistic text-to-speech.

---

## 🛠️ Creative Technical Engineering (The "Magic")

The most challenging—and rewarding—part of this project was pushing **Streamlit** beyond its static limits to create a dynamic, "React-like" experience.

### 🎨 1. The "HTML Parsing Bridge"
**The Challenge:** LLMs often output HTML wrapped in Markdown code blocks (e.g., ` ```html <div>...</div> `), which renders as raw code in Streamlit.
**The Solution:** We wrote a robust **Stream Parser** that acts as a middleware. It intercepts the LLM's token stream, identifies these wrappers, checks for potential security issues, and strips them on-the-fly. This forces the browser to render the **Raw HTML**, allowing us to display rich **Product Cards**, **Financial Tickers**, and **Grids** directly in the chat.

### 🧪 2. CSS Injection Engine
Streamlit is notoriously difficult to style. We built a custom `styles.py` module that injects CSS to override the shadow DOM, implementing a **Glassmorphism** aesthetic with neon gradients and 60FPS particle backgrounds.

### 📊 3. Dynamic Data Visualization Protocol
To enable the agent to create charts, we defined a hidden protocol. The agent outputs a specific JSON signature (`<!-- CHART_TOOL_JSON: ... -->`). The frontend's background loop detects this signature and instantly renders interactive **Plotly** charts.

---

## 🧗 Challenges & How We Overcame Them

| Challenge | The Solution |
| :--- | :--- |
| **LLM Hallucinations (JSON)** | The model would frequently break JSON schemas. We implemented a **"Salvaging" Error Handler** that catches parsing exceptions and uses regex heuristics to extract valid data from the broken JSON, preventing crashes. |
| **Voice Latency** | Chaining Audio -> STT -> Agent -> TTS was too slow. We migrated STT to **Groq's LPU** (Language Processing Unit), reducing transcription time to milliseconds. |
| **State Management** | Streamlit re-runs the entire script on every interaction. We heavily utilized `st.session_state` to decouple the Agent's memory from the UI refresh cycle, ensuring persistence. |

---

## 🚀 Impact & Key Learnings

> *"Enterprise software doesn't have to look boring."*

This project demonstrated that **User Experience** is a massive differentiator. The underlying RAG logic is standard, but the "Magic"—the instant voice response, the visual product cards, and the beautiful charts—is what builds trust. We learned that investing time in "UI hacks" pays off disproportionately in perceived product quality.

---

## 🧱 Technology Stack

| Domain | Technology Used |
| :--- | :--- |
| **Frontend** | Streamlit, HTML5, CSS3, Vanilla JS |
| **AI Brain** | LangChain, OpenAI GPT-4o |
| **Voice** | Groq (Whisper), OpenAI (Audio) |
| **Data** | FAISS (Vector DB), DuckDuckGo (Search) |
| **Deployment** | Docker, MCP Server |

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
    Create a `.env` file within the root directory:
    ```env
    OPENAI_API_KEY=sk-...
    GROQ_API_KEY=gsk-...
    ```

4.  **Run the Application**:
    ```bash
    streamlit run streamlit_app.py
    ```

---

![Live Tools Demo](assets/images/feature_demo_2.png)
