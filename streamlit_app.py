"""Streamlit web interface for the RAG agent."""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path
import warnings
from dotenv import load_dotenv

# Load environment variables (Critical for Keys)
load_dotenv()

import streamlit as st

# Add src to path so we can import rag_agent
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Suppress warnings
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
warnings.filterwarnings("ignore")

# Suppress noisy warnings
warnings.filterwarnings("ignore", message=".*Examining the path of torch.classes.*")
warnings.filterwarnings("ignore", category=UserWarning, module="torch")

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
            <div style="padding: 2rem 0; text-align: center;">
                <h1 class="gradient-text" style="font-size: 2rem; margin:0; font-weight: 700;">✨ EchoMindAI</h1>
                <p style="color: var(--text-secondary); font-size: 0.9rem; margin-top: 5px;">Enterprise Intelligence</p>
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

        st.divider()

        # Tabs for Compact Layout
        tab_brain, tab_vision, tab_settings = st.tabs(["🧠 Brain", "👁️ Vision", "⚙️ Config"])

        with tab_brain:
            st.caption("Knowledge Base")
            uploaded_files = st.file_uploader(
                "Add Documents",
                accept_multiple_files=True,
                label_visibility="collapsed",
                key="brain_upload",
                help="PDF, TXT, MD, CSV"
            )
            if uploaded_files:
                if st.button("⚡ Process Files", use_container_width=True, type="primary"):
                    handle_upload_and_ingest(uploaded_files)
            
            st.divider()
            st.caption("Data Analysis")
            user_data_files = st.file_uploader(
                "Upload Data", 
                accept_multiple_files=True, 
                type=["csv", "xlsx"],
                key="data_upload",
                label_visibility="collapsed"
            )
            if user_data_files:
                handle_user_data_upload(user_data_files) # Helper to keep logic clean

        with tab_vision:
            st.caption("Visual Intelligence")
            shopping_image = st.file_uploader(
                "Upload Image", 
                type=["jpg", "png", "jpeg"],
                key="shop_upload",
                label_visibility="collapsed"
            )
            if shopping_image:
                if st.button("🔍 Analyze", use_container_width=True, type="primary"):
                    handle_visual_shop(shopping_image)

        with tab_settings:
            st.caption("Modes")
            st.session_state.deep_research_mode = st.toggle("Deep Research Agent", value=False)
            
            st.caption("Voice")
            # Using st.audio_input (handled in handle_voice_input call below or inline)
            # handle_voice_input() renders the recorder widget
            handle_voice_input()
            
            st.session_state.voice_selection = st.selectbox(
                "Voice Persona",
                ["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
                index=4
            )
            
            st.divider()
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.messages = []
                st.rerun()
            if st.button("🔄 Rebuild Index", use_container_width=True):
                handle_reingest()
                        
            # Export Chat
            chat_str = "\\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])
            st.download_button("📥 Export Chat", chat_str, "chat.txt", "text/plain", use_container_width=True)
            
    # Helper for data upload (since we moved it inside tab)
    def handle_user_data_upload(files):
        user_upload_dir = Path("data/user_uploads")
        user_upload_dir.mkdir(parents=True, exist_ok=True)
        for data_file in files:
            save_path = user_upload_dir / data_file.name
            with open(save_path, "wb") as f:
                f.write(data_file.getbuffer())
        st.success(f"Uploaded {len(files)} files.")


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


def handle_visual_shop(uploaded_file):
    """Process an uploaded image for shopping."""
    st.session_state.processing = True
    
    try:
        # 1. Save Image
        imgs_dir = settings.data_dir / "user_images"
        imgs_dir.mkdir(parents=True, exist_ok=True)
        img_path = imgs_dir / uploaded_file.name
        
        with open(img_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        # 2. Display
        st.sidebar.image(uploaded_file, caption="Identifying...", use_column_width=True)
        
        # 3. Analyze (Captioning)
        with st.status("👁️ Analyzing Image...", expanded=True) as status:
            from rag_agent.tools_vision import describe_image
            st.write("Loading vision models...")
            caption = describe_image(str(img_path))
            
            if "Error" in caption:
                st.error(caption)
                status.update(label="❌ Vision Failed", state="error")
                return
                
            st.write(f"identified: **{caption}**")
            status.update(label="✅ Item Identified", state="complete", expanded=False)
            
        # 4. Trigger Universal Visual Agent
        query = (f"I have uploaded an image. Visual analysis result: '{caption}'. "
                 "Please identify this. "
                 "If it is a commercial product, provide a shopping table with links/prices. "
                 "If it is a place/landmark, provide details, location, and travel info. "
                 "If it is data, analyze it.")
        submit_query(query)
        
    except Exception as e:
        st.error(f"Visual Shop Error: {e}")
    finally:
        st.session_state.processing = False


def handle_voice_input():
    """Record and transcribe voice input using Groq Whisper (Multi-lingual)."""
    import speech_recognition as sr
    import os
    from groq import Groq
    
    # Check API Key (Prioritize OpenAI, Fallback to Groq)
    openai_key = os.getenv("OPENAI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    
    if not openai_key and not groq_key:
        st.error("Missing API Key. Please set OPENAI_API_KEY or GROQ_API_KEY in .env")
        return

    # Use Streamlit Native Audio Input (Streamlit >= 1.40)
    audio_value = st.audio_input("Record Voice (Any Language)")
    
    if audio_value:
        # Status Indicator
        status = st.status("🎙️ Processing Audio...", expanded=True)
        try:
             text = ""
             
             # OPTION A: OpenAI Whisper (Preferred by User)
             if openai_key:
                 from openai import OpenAI
                 status.write("Transcribing with OpenAI Whisper...")
                 client = OpenAI(api_key=openai_key)
                 transcription = client.audio.transcriptions.create(
                    file=("audio.wav", audio_value), 
                    model="whisper-1",
                    response_format="json"
                 )
                 text = transcription.text
                 
             # OPTION B: Groq Whisper (Fallback)
             elif groq_key:
                 from groq import Groq
                 status.write("Transcribing with Groq Whisper...")
                 client = Groq(api_key=groq_key)
                 transcription = client.audio.transcriptions.create(
                    file=("audio.wav", audio_value), 
                    model="whisper-large-v3",
                    response_format="json",
                    temperature=0.0
                 )
                 text = transcription.text
             
             status.update(label=f"🗣️ Heard: '{text}'", state="complete", expanded=False)
             
             # Typing Effect
             if text and text.strip():
                typing_placeholder = st.empty()
                typed_text = ""
                for char in f"🗣️ User: {text}":
                    typed_text += char
                    typing_placeholder.markdown(f"**{typed_text}**▌")
                    time.sleep(0.01) # Fast typing
                typing_placeholder.empty()
                
                # Prevent auto-submission loop (simple debounce)
                if "last_voice_text" not in st.session_state or st.session_state.last_voice_text != text:
                    st.session_state.last_voice_text = text
                    time.sleep(0.5)
                    submit_query(text)
                    
        except Exception as e:
            status.update(label="❌ Voice Error", state="error")
            st.error(f"Error: {e}")



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
    """Render the premium zero-state welcome screen."""
    welcome_html = """
    <div style="text-align: center; margin-top: 3rem; margin-bottom: 3rem;" class="animate-fade-in">
        <h1 style="font-size: 3.5rem; margin-bottom: 1rem; font-weight: 800; letter-spacing: -1px;">
            <span>EchoMindAI</span>
        </h1>
        <p style="font-size: 1.2rem; color: rgba(255,255,255,0.7); max-width: 600px; margin: 0 auto; line-height: 1.6;">
            Enterprise Intelligence with Vision & Voice
        </p>
    </div>
    """
    st.markdown(welcome_html, unsafe_allow_html=True)

    # Feature Suggestion Cards (5 items)
    # Using 'secondary' kind to trigger our glassmorphism CSS
    cols = st.columns(5)
    
    features = [
        ("🎨 Images", "Generate a photo of a futuristic city"),
        ("🛍️ Shopping", "Find top rated running shoes"),
        ("📰 News", "Latest AI news today"),
        ("xk Weather", "Weather in New York"), # User requested "xk" styled weather? Kept simple.
        ("✈️ Bookings", "Find luxury hotels in Dubai")
    ]
    
    # Correction: User likely meant "Weather" but used "xk". I will use standard weather icon.
    features = [
        ("🎨 Images", "Generate a photo of a futuristic city"),
        ("🛍️ Shopping", "Find top rated running shoes"),
        ("📰 News", "Latest AI news today"),
        ("⛅ Weather", "Weather in Tokyo"),
        ("✈️ Bookings", "Find luxury hotels in Dubai")
    ]

    for col, (label, prompt) in zip(cols, features):
        with col:
            # We use a trick: Button label is the Icon+Name
            if st.button(label, use_container_width=True, type="secondary"):
                submit_query(prompt)


def submit_query(text):
    """Helper to submit a query programmatically."""
    st.session_state.messages.append({"role": "user", "content": text})
    st.rerun()


def render_chat_message(role, content, sources=None):
    """Render a chat message with the new glass styling."""
    with st.chat_message(role):
        # Strip code blocks if it's HTML content to allow rendering
        if "div class=" in content or "product-grid" in content:
            content = content.replace("```html", "").replace("```", "")
        st.markdown(content, unsafe_allow_html=True)
        
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
        render_welcome_screen() # Call our centralized, updated UI logic

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
        print(f"DEBUG: Input received: {prompt}")
        st.session_state.messages.append({"role": "user", "content": prompt})
        render_chat_message("user", prompt)

    # Response Logic (Runs if last message is from user)
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        print("DEBUG: Entering Response Logic Block")
        prompt = st.session_state.messages[-1]["content"]
        print(f"DEBUG: Processing prompt: {prompt}")
        
        if not agent:
             print("DEBUG: Agent is NONE!")
             st.error("Agent not ready. Please check configuration.")
             return
        
        print("DEBUG: Agent is ready. Starting generation...")

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
                            # Real-time sanitization: Only hide LOCAL images (charts), allow external URLs (http/https) to show
                            # Regex matches ![alt](path) where path DOES NOT start with http or https
                            # Also strip ```html wrapper if present
                            display_text = full_response
                            display_text = re.sub(r'```html\s*', '', display_text)
                            display_text = re.sub(r'```', '', display_text) # Cleaning trailing
                            display_text = re.sub(r'!\[.*?\]\((?!http|https).*?\)', ' *(Generating chart...)* ', display_text)
                            response_container.markdown(display_text + "▌", unsafe_allow_html=True)
                        
                        # Final clean display: Only hide LOCAL images
                        display_text = full_response
                        display_text = re.sub(r'```html\s*', '', display_text)
                        display_text = re.sub(r'```', '', display_text)
                        display_text = re.sub(r'!\[.*?\]\((?!http|https).*?\)', ' *(See chart below)* ', display_text)
                        response_container.markdown(display_text, unsafe_allow_html=True)
                        
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
                                         # 4. Specific fix for 'app/static' which might be just 'static' locally
                                         if "app/static" in image_path_str:
                                             local_static = Path("static") / image_path.name
                                             if local_static.exists():
                                                 st.image(str(local_static))
                                                 pass

                        
                        # 4. Voice Output (TTS) with OpenAI (High Quality) or gTTS (Fallback)
                        try:
                            # Clean markdown for speech
                            clean_text = re.sub(r'!\[.*?\]\(.*?\)', '', full_response) 
                            clean_text = re.sub(r'[*_`]', '', clean_text)
                            clean_text = clean_text[:800] # Limit to avoid long processing

                            if clean_text.strip():
                                import os
                                from openai import OpenAI
                                
                                # Try OpenAI TTS first
                                openai_key = os.getenv("OPENAI_API_KEY")
                                voice_model = st.session_state.get("voice_selection", "nova")
                                
                                if openai_key:
                                    try:
                                        client = OpenAI(api_key=openai_key)
                                        response = client.audio.speech.create(
                                            model="tts-1",
                                            voice=voice_model,
                                            input=clean_text
                                        )
                                        # Stream audio directly
                                        import io
                                        audio_bytes = io.BytesIO()
                                        for chunk in response.iter_bytes():
                                            audio_bytes.write(chunk)
                                        
                                        audio_bytes.seek(0) # CRITICAL FIX: Reset pointer
                                        st.audio(audio_bytes, format="audio/mp3")
                                    except Exception as e:
                                        # Fallback to gTTS if OpenAI fails (e.g. quota)
                                        print(f"OpenAI TTS failed: {e}. Falling back to gTTS.")
                                        from gtts import gTTS
                                        tts = gTTS(text=clean_text, lang='en')
                                        audio_fp = io.BytesIO()
                                        tts.write_to_fp(audio_fp)
                                        audio_fp.seek(0)
                                        st.audio(audio_fp, format='audio/mp3')
                                else:
                                    # Default to gTTS if no key
                                    from gtts import gTTS
                                    tts = gTTS(text=clean_text, lang='en')
                                    audio_fp = io.BytesIO()
                                    tts.write_to_fp(audio_fp)
                                    audio_fp.seek(0)
                                    st.audio(audio_fp, format='audio/mp3')

                        except Exception as vocal_error:
                            pass

                        # Save history (We save the full response with the image link for continuity)
                        msg_data = {"role": "assistant", "content": full_response}
                        st.session_state.messages.append(msg_data)
                        
                    except Exception as e:
                        st.error(f"Something went wrong: {e}")

if __name__ == "__main__":
    main()
