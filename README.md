# ✨ EchoMindAI: Enterprise Intelligence

> **The Advanced RAG System with Vision, Voice, and Real-Time Agentic Capabilities.**

EchoMindAI is a next-generation AI assistant that goes beyond simple text. It combines **Retrieval-Augmented Generation (RAG)** with a powerful **Agentic Loop**, allowing it to see images, hear your voice, browse the live web, and render beautiful, interactive UIs.

![EchoMindAI Dashboard](assets/images/dashboard_preview.png)

---

## 🚀 Key Capabilities

### 🧠 1. The Super-Brain (RAG + Agents)
- **Smart Ingestion**: Drag & drop PDFs, Text, Markdown, or CSV files. The system "reads" them and builds a semantic vector index (FAISS).
- **Hybrid Search**: Combines your private document knowledge with live internet search.
- **Fail-Safe Intelligence**: If live search fails, the agent falls back to internal knowledge to generate answers.

![Feature Demo 1](assets/images/feature_demo_1.png)

### 👁️ 2. Visual Intelligence
- **Universal Vision**: Upload *any* image.
    - **Shopping**: Identifies products and builds a price comparison grid.
    - **Travel**: Recognizes landmarks and provides travel guides/hotels.
    - **Data**: Reads charts and graphs.
- **Lightbox UI**: All generated images support click-to-zoom interactivity.

### 🎤 3. Voice Intelligence
- **Hearing (STT)**: Uses **Groq Whisper** for extremely fast, multi-lingual voice transcription.
- **Speaking (TTS)**: Responds with high-quality, life-like AI voices using **OpenAI Audio**.

### 🌐 4. Live Agent Tools
The system is equipped with a suite of real-time tools:
- **Hotels & Flights**: Finds live booking options, prices, and ratings.
- **Shopping**: Scours the web for the best product deals.
- **News**: Fetches the latest global headlines with images.

![Feature Demo 2](assets/images/feature_demo_2.png)

---

## 🎨 The "React-Like" UI Engine

EchoMindAI pushes **Streamlit** to its absolute limit, tricking it into behaving like a modern React application.

### How it Works:
1.  **CSS Injection**: We inject a custom CSS engine (`styles.py`) that overrides default Streamlit styles with **Glassmorphism** and **Neon Gradients**.
2.  **JavaScript Bridge**: We inject vanilla JavaScript to handle client-side events like "Slide Up" animations.
3.  **HTML Wrapping Fix**: We patched the frontend to render raw HTML as interactive **Product Cards** and **Grids**.

---

## 🛠️ Technology Stack

- **Frontend**: Streamlit (Python) + Custom HTML/CSS/JS Injection.
- **LLM Orchestration**: LangChain + OpenAI GPT-4o.
- **Vector Database**: FAISS.
- **Search Engine**: DuckDuckGo.
- **Voice Stack**: Groq (STT) + OpenAI (TTS).
- **Server**: MCP Server implementation.

---

## 📖 Installation

1.  **Clone & Install**:
    ```bash
    git clone https://github.com/Sur27codes/EchoMindAI.git
    cd EchoMindAI
    pip install -r requirements.txt
    ```

2.  **Environment Secrets**:
    Create a `.env` file:
    ```env
    OPENAI_API_KEY=sk-...
    GROQ_API_KEY=gsk-...
    ```

3.  **Run**:
    ```bash
    streamlit run streamlit_app.py
    ```

---

## 📸 Gallery

| Data Visualization | Plotting Capabilities |
|:---:|:---:|
| ![Sine Wave](assets/images/sine_wave_example.png) | ![X/Y Plot](assets/images/plot_example.png) |
