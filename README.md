# ✨ EchoMindAI: Enterprise Intelligence

> **The Advanced RAG System with Vision, Voice, and Real-Time Agentic Capabilities.**

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Frontend](https://img.shields.io/badge/Frontend-Streamlit-red)
![Status](https://img.shields.io/badge/Status-Active-success)

![EchoMindAI Dashboard](assets/images/dashboard_preview.png)

---

## 📖 The Story

### 1. Context & Problem Statement
The goal of **EchoMindAI** was to bridge the gap between static document search and dynamic, agentic intelligence. Traditional RAG (Retrieval-Augmented Generation) systems are often limited to text-only retrieval and lack the ability to interact with the real world or present information visually.

**The Problem:**
Enterprises needed an assistant that could not only "read" internal documents (PDFs, CSVs) but also "see" images, "hear" voice commands, and "act" by searching the live web—all wrapped in a premium, consumer-grade user interface that feels far superior to standard internal tools.

### 2. The Solution (What We Built)

We built a multi-modal agentic system that seamlessly integrates internal knowledge with external tools.

#### **Product Features:**
*   **🧠 The Super-Brain**: A fail-safe RAG system that uses **FAISS** for internal document retrieval and automatically falls back to **DuckDuckGo** live search if internal data is insufficient.
*   **👁️ Visual Intelligence**: Users can upload images (e.g., a photo of a shoe or a chart). The system analyzes the image and triggers relevant agents—like a "Visual Shopper" finding products online.
*   **🎤 Voice-First**: Integrated **Groq Whisper** for near-instant multi-lingual speech-to-text and **OpenAI Audio** for life-like text-to-speech.
*   **🌐 Agentic Tools**: Real-time fetching of **Stock Prices**, **Global News**, **Weather**, and **Travel Bookings**.

#### **Creative Technical Solutions:**
*   **"React-like" UI on Streamlit**: The most creative aspect was pushing **Streamlit** beyond its limits. Since Streamlit is typically static, we implemented a custom **HTML/CSS/JS injection engine**.
    *   **CSS Injection**: Forced a "Glassmorphism" aesthetic with neon gradients.
    *   **The "HTML Parsing Bridge"**: A robust parser that intercepts the LLM's stream, strips Markdown code blocks, and forces the browser to render raw HTML for **Product Cards** and **Financial Tickers**.

### 3. Engineering Challenges & Solutions

| Challenge | Solution |
| :--- | :--- |
| **LLM Output Formatting** | The model frequently broke strict JSON schemas. We implemented a **Robust Error Handler** that attempts to "salvage" raw text from exceptions, often recovering the correct answer even if the format failed. |
| **Latency in Voice & Search** | Chaining multiple tools created lag. We utilized **Groq's LPU** for Whisper (STT) to reduce transcription time to near-zero and implemented an in-memory **response cache** for frequent queries. |
| **Streamlit's Re-run Cycle** | Streamlit re-runs the script on every interaction. We heavily utilized `st.session_state` to decouple Agent memory from the UI refresh cycle, ensuring persistent conversation history. |

### 4. Impact & Key Learnings

*   **Impact**: The project demonstrated that "Enterprise" software doesn't have to be boring. By combining powerful RAG capabilities with a premium UI, we significantly increased user engagement.
*   **Key Learning**: *User Experience is the differentiator.* The underlying RAG logic is standard, but the **"Magic"**—the instant voice response, the visual product cards, and the beautiful charts—is what makes the tool valuable. Investing time in "UI hacks" pays off disproportionately in perceived quality.

---

## 🎨 Minute Technical Details: The "UI Engine"

EchoMindAI uses a sophisticated set of "hacks" to trick Streamlit into behaving like a modern Single Page Application (SPA).

### The CSS/JS Injection
We use `st.markdown(..., unsafe_allow_html=True)` to inject a `<style>` block that redefines the entire CSS variable system of Streamlit, creating the **Dark/Neon Theme**.

### The HTML Stream Parser
LLMs often output code like this:
```markdown
Here is the product:
```html
<div class="card">...</div>
```
```
Our parser detects this pattern in real-time, strips the ```html wrapper, and renders the div directly into the DOM, allowing for rich, interactive components that Streamlit doesn't natively support.

---

## 🛠️ Technology Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Frontend** | Streamlit | The core web framework, heavily customized. |
| **LLM** | GPT-4o | The primary reasoning brain. |
| **Orchestration** | LangChain | Manages the agent loop and tool execution. |
| **Vector DB** | FAISS | Stores embeddings for internal document search. |
| **Voice** | Groq + OpenAI | Whisper (STT) and OpenAI TTS. |
| **Live Data** | DuckDuckGo, yFinance | APIs for web search and stock data. |

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
