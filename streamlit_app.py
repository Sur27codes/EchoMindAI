"""Streamlit web interface for the RAG agent."""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path
import warnings

import streamlit as st

# Add src to path so we can import rag_agent
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Suppress warnings
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
warnings.filterwarnings("ignore")

from rag_agent.config import settings
from rag_agent.ingest import ingest_documents
from rag_agent.rag_agent import RAGAgent
from rag_agent.styles import get_custom_css

# Page config
st.set_page_config(
    page_title="EchoMindAI Intelligence",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent" not in st.session_state:
    st.session_state.agent = None
if "vector_store_exists" not in st.session_state:
    st.session_state.vector_store_exists = settings.vector_dir.exists()
if "processing" not in st.session_state:
    st.session_state.processing = False


def initialize_agent():
    """Initialize the RAG agent."""
    try:
        if st.session_state.agent is None:
            # Silent loading for better UX
            st.session_state.agent = RAGAgent()
        return st.session_state.agent
    except FileNotFoundError:
        return None
    except Exception as e:
        st.error(f"Error initializing agent: {e}")
        return None


def render_sidebar():
    """Render the simplified, premium sidebar."""
    import textwrap
    with st.sidebar:
        # App Title/Logo Area
        logo_html = textwrap.dedent("""
            <div style="padding: 1rem 0; text-align: center;">
                <h1 style="font-size: 1.5rem; margin:0; font-weight: 700;">✨ EchoMindAI</h1>
                <p style="color: #8E8E93; font-size: 0.8rem; margin:0;">Enterprise Intelligence</p>
            </div>
        """)
        st.markdown(logo_html, unsafe_allow_html=True)
        
        st.divider()

        # 1. System Status
        st.subheader("System Status")
        col1, col2, col3 = st.columns(3)
        with col1:
             st.caption("API")
             st.markdown("🟢" if os.getenv("GROQ_API_KEY") else "🔴")
        with col2:
             st.caption("Brain")
             st.markdown("🟢" if st.session_state.agent else "🔴")
        with col3:
             st.caption("Voice")
             try:
                 import gtts
                 st.markdown("🟢")
             except ImportError:
                 st.markdown("⚪")
        
        # Check Web Search
        try:
            from langchain_community.tools import DuckDuckGoSearchRun
        except ImportError:
            st.warning("Web Search unavailable. Install `duckduckgo-search`.")

        st.divider()

        # 2. Add Knowledge
        st.subheader("📚 Add Knowledge")
        uploaded_files = st.file_uploader(
            "Drop documents here",
            accept_multiple_files=True,
            label_visibility="collapsed",
            help="Supported: PDF, TXT, MD, CSV"
        )
        
        if uploaded_files:
            if st.button("⚡ Process & Add to Brain", use_container_width=True, type="primary"):
                handle_upload_and_ingest(uploaded_files)

        # 3. Data Analyst Mode (User Uploads)
        st.divider()
        st.subheader("📈 Data Analyst Mode")
        user_data_files = st.file_uploader(
            "Upload Data for Analysis", 
            accept_multiple_files=True, 
            type=["csv", "xlsx"],
            key="user_data_upload",
            help="Upload your own CSV/Excel files here. The agent can then analyze and plot them."
        )
        if user_data_files:
            user_upload_dir = Path("data/user_uploads")
            user_upload_dir.mkdir(parents=True, exist_ok=True)
            for data_file in user_data_files:
                save_path = user_upload_dir / data_file.name
                with open(save_path, "wb") as f:
                    f.write(data_file.getbuffer())
            st.success(f"Uploaded {len(user_data_files)} files.")

        st.divider()
        
        # 4. Mode Selection
        st.subheader("🧠 Intelligence Mode")
        st.session_state.deep_research_mode = st.toggle(
            "Deep Research Agent", 
            value=False,
            help="Enable autonomous multi-step research. Slower but deeper."
        )

        # 5. Settings (Bottom)
        st.markdown("<div style='flex-grow: 1;'></div>", unsafe_allow_html=True) # Spacer
        with st.expander("🛠️ Settings"):
            st.session_state.show_sources = st.toggle("Show citations", value=True)
            if st.button("🗑️ Reset Conversation", use_container_width=True):
                st.session_state.messages = []
                st.rerun()
            if st.button("🔄 Rebuild Index", use_container_width=True):
                handle_reingest()
            
            # Export Chat
            chat_str = "\\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])
            st.download_button(
                label="📥 Download Chat",
                data=chat_str,
                file_name="echomindai_chat.txt",
                mime="text/plain",
                use_container_width=True
            )


def handle_upload_and_ingest(uploaded_files):
    """Handle upload and auto-trigger ingestion."""
    st.session_state.processing = True
    progress_bar = st.progress(0, text="Starting upload...")
    
    try:
        # 1. Save Files
        saved_count = 0
        import zipfile
        
        for i, file in enumerate(uploaded_files):
            progress = (i / len(uploaded_files)) * 0.5
            progress_bar.progress(progress, text=f"Uploading {file.name}...")
            
            if file.name.lower().endswith(".zip"):
                with zipfile.ZipFile(file) as z:
                    extract_path = settings.data_dir / file.name.rsplit('.', 1)[0]
                    z.extractall(extract_path)
            else:
                file_path = settings.data_dir / file.name
                with open(file_path, "wb") as f:
                    f.write(file.getbuffer())
            saved_count += 1
        
        # 2. Ingest
        progress_bar.progress(0.6, text="🧠 Digesting information...")
        ingest_documents()
        
        progress_bar.progress(1.0, text="✅ Done!")
        time.sleep(0.5)
        
        st.session_state.vector_store_exists = True
        st.session_state.agent = None # Force reload
        st.toast(f"Successfully added {saved_count} documents!", icon="🎉")
        st.rerun()
        
    except Exception as e:
        st.error(f"Error: {e}")
    finally:
        st.session_state.processing = False


def handle_reingest():
    """Manual trigger for re-ingestion."""
    try:
        with st.spinner("Rebuilding knowledge base..."):
            ingest_documents()
            st.session_state.vector_store_exists = True
            st.session_state.agent = None
            st.success("Index rebuilt successfully!")
            st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")


def load_demo_data():
    """Create sample data to demo the agent."""
    demo_content = """# EchoMindAI: User Manual


## What is EchoMindAI?
EchoMindAI is an advanced Retrieval-Augmented Generation (RAG) system designed to help enterprises analyze their documents intelligently.

## Features
- **Smart Ingestion**: Automatically processes PDFs, Text files, and Markdown.
- **Glassmorphism UI**: A premium, modern interface.
- **Fast Vector Search**: Uses FAISS for sub-millisecond retrieval.

## Getting Started
1. Upload your documents in the sidebar.
2. Wait for the green status light.
3. Ask questions like "How do I upload?" or "What is EchoMindAI?".
"""
    try:
        settings.data_dir.mkdir(parents=True, exist_ok=True)
        with open(settings.data_dir / "echomindai_manual.md", "w") as f:
            f.write(demo_content)
        
        # Auto ingest
        with st.status("🚀 Loading Demo Data...", expanded=True) as status:
            st.write("Creating manual...")
            time.sleep(0.5)
            st.write("Indexing content...")
            ingest_documents()
            st.write("Done!")
            status.update(label="✅ Demo Loaded!", state="complete", expanded=False)
            
        st.session_state.vector_store_exists = True
        st.session_state.agent = None
        st.rerun()
        
    except Exception as e:
        st.error(f"Failed to load demo: {e}")


def render_welcome_screen():
    """Render the zero-state welcome screen."""
    welcome_html = """
    <div style="text-align: center; margin-top: 5rem; margin-bottom: 3rem;" class="animate-fade-in">
        <h1 style="font-size: 3rem; margin-bottom: 1rem;">
            Hello, Human
        </h1>
        <p style="font-size: 1.2rem; color: var(--text-secondary); max-width: 600px; margin: 0 auto;">
            I am ready to help you analyze your documents. Upload your files in the sidebar or try one of the examples below.
        </p>
    </div>
    """
    st.markdown(welcome_html, unsafe_allow_html=True)

    # Suggestion Cards
    col1, col2, col3 = st.columns(3)
    suggestions = [
        "Summarize the key points",
        "What are the main risks?",
        "Explain the technical details"
    ]
    
    for col, text in zip([col1, col2, col3], suggestions):
        with col:
            if st.button(text, use_container_width=True):
                submit_query(text)


def submit_query(text):
    """Helper to submit a query programmatically."""
    st.session_state.messages.append({"role": "user", "content": text})
    st.rerun()


def render_chat_message(role, content, sources=None):
    """Render a chat message with the new glass styling."""
    with st.chat_message(role):
        st.markdown(content)
        
        if sources and role == "assistant":
            with st.expander(f"📚 {len(sources)} References"):
                for i, source in enumerate(sources, 1):
                    src_name = source.get('metadata', {}).get('source', 'Unknown')
                    st.caption(f"**Source {i}: {src_name}**")
                    st.markdown(f"<div style='font-size: 0.85rem; color: #cbd5e1; border-left: 2px solid #475569; padding-left: 10px;'>{source['content'][:250]}...</div>", unsafe_allow_html=True)
                    if i < len(sources):
                        st.divider()


def main():
    # Inject CSS
    st.markdown(get_custom_css(), unsafe_allow_html=True)
    
    # Initialize agent early for sidebar status
    agent = initialize_agent()
    st.session_state.agent = agent # Store agent in session state

    render_sidebar()

    # Chat Interface
    # Note: We removed the global st.title to prevent redundancy with the Hero card.
    
    # Initialize messages
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # LOGIC: Show Hero Screen if chat is empty, otherwise show Chat History
    if not st.session_state.messages:
        # --- HERO START SCREEN ---
        import textwrap
        hero_html = textwrap.dedent("""
            <div class="hero-animate" style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 5rem 0;">
                <div style="text-align: center; max-width: 800px;">
                    <h1 style="font-size: 4.5rem; margin-bottom: 0.5rem; letter-spacing: -0.04em;">
                        EchoMindAI
                    </h1>
                    <p style="font-size: 1.5rem; color: #94A3B8; margin-bottom: 3rem;">
                        Enterprise Intelligence with Vision & Voice
                    </p>
                </div>
            </div>
        """)
        st.markdown(hero_html, unsafe_allow_html=True)
        
        # Action Buttons (Centered Grid)
        col1, col2, col3 = st.columns([1,1,1])
        prompts = [
            "📈 Analyze Q3 financials",
            "🌍 Latest AI News",
            "⚛️ Explain Project Omega"
        ]
        
        # Use a secondary container for button alignment
        with st.container():
            for col, txt in zip([col1, col2, col3], prompts):
                with col:
                    if st.button(txt, use_container_width=True):
                        st.session_state.messages.append({"role": "user", "content": txt})
                        st.rerun()

    else:
        # --- CHAT HISTORY VIEW ---
        # Show a discreet header when not in hero mode
        if len(st.session_state.messages) > 0:
            st.markdown("""
            <div style="padding: 1rem 0; margin-bottom: 2rem; border-bottom: 1px solid rgba(255,255,255,0.05); display: flex; align-items: center; justify-content: space-between;">
                <h3 style="margin: 0; font-size: 1.2rem;">✨ Conversation</h3>
                <span style="font-size: 0.8rem; color: var(--text-muted);">EchoMindAI Live</span>
            </div>
            """, unsafe_allow_html=True)

        for message in st.session_state.messages:
            render_chat_message(message["role"], message["content"], message.get("sources"))


    # Chat Input
    if prompt := st.chat_input("Ask anything..."):
        if not agent:
             st.error("Agent not ready. Please check configuration.")
             return

        # User Message
        st.session_state.messages.append({"role": "user", "content": prompt})
        render_chat_message("user", prompt)

        # Assistant Message
        with st.chat_message("assistant"):
            # --- DEEP RESEARCH MODE ---
            if st.session_state.get("deep_research_mode", False):
                from rag_agent.researcher import ResearchAgent
                import io

                status_container = st.status("🕵️‍♂️ Deep Research in progress...", expanded=True)
                response_placeholder = st.empty()
                
                try:
                    researcher = ResearchAgent()
                    # Execute generator
                    gen = researcher.execute_research(prompt)
                    final_report = ""
                    
                    for update in gen:
                        if isinstance(update, dict):
                            status_container.write(update.get("message", ""))
                            if "plan" in update:
                                status_container.markdown(f"**Plan:** {', '.join(update['plan'])}")
                        elif isinstance(update, str):
                            final_report = update
                            
                    status_container.update(label="✅ Research Complete", state="complete", expanded=False)
                    response_placeholder.markdown(final_report)
                    st.session_state.messages.append({"role": "assistant", "content": final_report})
                    
                    # Voice for Research
                    try:
                        import gtts
                        tts = gtts.gTTS("Research complete. Report generated.", lang='en')
                        width_buf = io.BytesIO()
                        tts.write_to_fp(width_buf)
                        st.audio(width_buf, format='audio/mp3')
                    except:
                        pass

                except Exception as e:
                    status_container.update(label="❌ Research Failed", state="error")
                    st.error(f"Research Error: {e}")

            # --- STANDARD MODE ---
            else:
                try:
                    # 1. Thinking Status
                    with st.status("🧠 Analyzing...", expanded=False) as status:
                        st.write("Checking Knowledge Base & Tools...")
                        status.update(label="✅ Response Ready", state="complete", expanded=False)

                    # 2. Streaming Response & Image Detection
                    full_response = ""
                    response_container = st.empty()
                    import re
                    
                    for chunk in agent.ask_stream(prompt):
                        full_response += chunk
                        # Real-time sanitization: Don't show the broken image link in the text stream
                        # We use a temporary display string that hides the image markdown
                        display_text = re.sub(r'!\[.*?\]\(.*?\)', ' *(See chart below)* ', full_response)
                        response_container.markdown(display_text + "▌")
                    
                    # Final clean display
                    display_text = re.sub(r'!\[.*?\]\(.*?\)', ' *(See chart below)* ', full_response)
                    response_container.markdown(display_text)
                    
                    # 3. Chart Rendering (The real image)
                    # 3. Chart Rendering (The real image)
                    image_matches = re.finditer(r'!\[.*?\]\((.*?)\)', full_response)
                    for match in image_matches:
                        image_path_str = match.group(1).strip()
                        # Clean up path
                        image_path = Path(image_path_str)
                        
                        # 1. Try absolute/direct path
                        if image_path.exists():
                            st.image(str(image_path))
                        else:
                            # 2. Try looking in the charts directory by filename
                            filename = image_path.name
                            chart_path = settings.data_dir / "charts" / filename
                            
                            if chart_path.exists():
                                st.image(str(chart_path))
                            else:
                                # 3. Fallback: Check if it's relative to CWD
                                cwd_path = Path.cwd() / image_path_str
                                if cwd_path.exists():
                                     st.image(str(cwd_path))
                                else:
                                     # Debug info (Only shows if really missing)
                                     # st.warning(f"Chart not found: {filename}") 
                                     pass
                    
                    # 4. Voice Output (TTS)
                    from gtts import gTTS
                    import io
                    try:
                        # Clean markdown for speech
                        # Remove images: ![alt](url)
                        clean_text = re.sub(r'!\[.*?\]\(.*?\)', '', full_response) 
                        # Remove bold/italic: *text* or _text_
                        clean_text = re.sub(r'[*_`]', '', clean_text) 
                        
                        if clean_text.strip():
                            tts = gTTS(text=clean_text[:500], lang='en') 
                            audio_fp = io.BytesIO()
                            tts.write_to_fp(audio_fp)
                            audio_fp.seek(0)
                            # Only display player if we have bytes
                            if audio_fp.getbuffer().nbytes > 0:
                                st.audio(audio_fp, format='audio/mp3')
                    except Exception as vocal_error:
                        # Silently fail for voice errors to avoid UI clutter
                        pass

                    # Save history (We save the full response with the image link for continuity)
                    msg_data = {"role": "assistant", "content": full_response}
                    st.session_state.messages.append(msg_data)
                    
                except Exception as e:
                    st.error(f"Something went wrong: {e}")

if __name__ == "__main__":
    main()
