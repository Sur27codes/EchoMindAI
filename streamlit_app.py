"""Streamlit web interface for the RAG agent."""
from __future__ import annotations

import os
import sys
import re
import json
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
    """Initialize the RAG agent with visual feedback."""
    try:
        if st.session_state.agent is None:
            with st.spinner("🧠 Waking up EchoMindAI..."):
                st.session_state.agent = RAGAgent()
        return st.session_state.agent
    except Exception as e:
        st.error(f"System Boot Error: {e}")
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
            st.session_state.debug_mode = st.toggle("🐞 Debug Mode", value=False, help="Show raw agent steps and tool outputs.")
            
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
            error_msg = str(e)
            if "401" in error_msg or "Unauthorized" in error_msg:
                 st.error("Authentication Failed (401). Please check your OPENAI_API_KEY or GROQ_API_KEY in .env.")
            else:
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
    # 1. Hero Section
    welcome_html = """
    <div style="text-align: center; margin-top: 3rem; margin-bottom: 2rem;" class="animate-fade-in">
        <div class="typewriter" style="display: inline-block;">
            <h1 style="font-size: 4rem; margin-bottom: 0.5rem; font-weight: 800; letter-spacing: -2px;">
                <span class="gradient-text">EchoMindAI</span>
            </h1>
        </div>
        <p style="font-size: 1.3rem; color: #E0E0E0; max-width: 700px; margin: 0 auto; line-height: 1.6; font-weight: 400;">
            Your All-Knowing AI Companion. <br>
            <span style="opacity: 0.7; font-size: 1.1rem;">Capable of Real-Time Web Search, Deep Analysis, and Multimodal Creation.</span>
        </p>
    </div>
    """
    st.markdown(welcome_html, unsafe_allow_html=True)

    # 2. Quick Action Buttons
    cols = st.columns(5)
    features = [
        ("🎨 Create", "Generate a photo of a futuristic city"),
        ("🛍️ Shop", "Find top rated running shoes"),
        ("📰 News", "Latest AI news today"),
        ("⛅ Weather", "Weather in Tokyo"),
        ("✈️ Travel", "Find luxury hotels in Dubai")
    ]
    
    for col, (label, prompt) in zip(cols, features):
        with col:
            if st.button(label, use_container_width=True, type="secondary"):
                submit_query(prompt)

    # 3. Capabilities Matrix (Visual Guide)
    st.markdown("""
    <div style="margin-top: 3rem; padding: 2rem; background: rgba(255,255,255,0.03); border-radius: 20px; border: 1px solid rgba(255,255,255,0.1);">
        <h3 style="text-align: center; margin-bottom: 1.5rem; font-size: 1.2rem; color: #fff;">🚀 Core Capabilities</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem;">
            <div style="text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🌐</div>
                <strong style="color: #fff;">Live Web Search</strong>
                <p style="font-size: 0.9rem; color: #aaa; margin: 0;">Access real-time world data, not just training sets.</p>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">👁️</div>
                <strong style="color: #fff;">Visual Intelligence</strong>
                <p style="font-size: 0.9rem; color: #aaa; margin: 0;">Upload images to get analysis, shopping links, or code.</p>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🧠</div>
                <strong style="color: #fff;">RAG Memory</strong>
                <p style="font-size: 0.9rem; color: #aaa; margin: 0;">Chat with your PDFs, Docs, and Data instantly.</p>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🛠️</div>
                <strong style="color: #fff;">Deep Research</strong>
                <p style="font-size: 0.9rem; color: #aaa; margin: 0;">Autonomous agent that browses and compiles reports.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def submit_query(text):
    """Helper to submit a query programmatically."""
    st.session_state.messages.append({"role": "user", "content": text})
    st.rerun()


def extract_balanced_tag(text, start_match, tag_name):
    """
    Extracts a balanced tag (div/section) starting from the regex match.
    start_match: the re.Match object for the opening tag
    tag_name: "div" or "section"
    Returns: (content_string, end_index_absolute)
    """
    start_idx = start_match.start()
    
    balance = 0
    # Regex to find open/close tags of this specific type
    # e.g. <div... or </div>
    pattern = re.compile(f'(<{tag_name}\\b[^>]*>|</{tag_name}>)', re.IGNORECASE)
    
    for match in pattern.finditer(text, start_idx):
        tag = match.group(0).lower()
        if tag.startswith(f'<{tag_name}'):
            balance += 1
        else:
            balance -= 1
        
        if balance == 0:
            return text[start_idx:match.end()], match.end()
            
    return None, -1

def parse_mixed_content(text):
    """Splits text into text and HTML widget chunks using balanced parsing."""
    import re

    # PRE-PROCESSING: Global Stripper
    # If a financial card exists, remove ALL backticks to prevent code block rendering
    if 'class="financial-card"' in text:
        text = text.replace("```html", "").replace("```xml", "").replace("```", "")
        
    parts = []
    current_idx = 0
    
    # regex for the START of any supported widget
    # We find the *first* one, extract it balanced, then continue
    # UPDATED: Support both single and double quotes for class attributes
    start_pattern = re.compile(
        r'(<section\s+class=["\']weather-card["\']>|<section\s+class=["\']product-grid["\']>|<div\s+class=["\']product-card["\']>|<div\s+class=["\']financial-card["\'])', 
        re.IGNORECASE
    )
    
    while current_idx < len(text):
        subtext = text[current_idx:]
        match = start_pattern.search(subtext)
        
        if not match:
            # No more widgets
            if subtext:
                parts.append({"type": "text", "content": subtext})
            break
            
        rel_start = match.start()
        abs_start = current_idx + rel_start
        
        # Add preceding text
        if abs_start > current_idx:
            parts.append({"type": "text", "content": text[current_idx:abs_start]})
            
        # Determine tag type (div or section) from the match
        tag_str = match.group(0).lower()
        tag_type = "section" if tag_str.startswith("<section") else "div"
        
        # Extract balanced content
        widget_content, abs_end = extract_balanced_tag(text, match, tag_type) # match is relative to subtext?? 
        # Wait, extract_balanced_tag takes 'text' and 'start_match'. 
        # But 'match' was found in 'subtext'. 'match.start()' is relative.
        # We need a match object that is absolute, OR pass subtext.
        # Let's use subtext logic inside the loop.
        
        # FIX: Call extract on SUBTEXT, then adjust indices
        w_content, w_end_rel = extract_balanced_tag(subtext, match, tag_type)
        
        if w_content:
            parts.append({"type": "html", "content": w_content})
            current_idx += w_end_rel
        else:
            # Parsing failed (no closing tag?), treat start as text and forward 1 char to avoid infinite loop
            parts.append({"type": "text", "content": subtext[:rel_start+1]})
            current_idx += rel_start + 1
            
    return parts

def unindent_text(text):
    """Remove common leading whitespace from every line."""
    lines = text.splitlines()
    if not lines: return text
    
    # Find minimum indentation of non-empty lines
    min_indent = 1000
    for line in lines:
        if line.strip():
            indent = len(line) - len(line.lstrip())
            if indent < min_indent:
                min_indent = indent
                
    if min_indent == 1000 or min_indent == 0:
        return text
        
    return "\n".join([line[min_indent:] for line in lines])

def render_chat_message(role, content, sources=None):
    """Render a chat message with mixed content handling."""
    with st.chat_message(role):
        # 1. Parse Mixed Content (Text vs Widgets)
        chunks = parse_mixed_content(content)
        
        for chunk in chunks:
            if chunk["type"] == "text":
                # Render text normally
                text = chunk["content"]
                
                # CLEANUP: Dedent text to prevent Markdown Code Blocks
                text = unindent_text(text)
                
                # 4. Render Generic Visualization Tool Charts
                # Format: <!-- CHART_TOOL_JSON: {...} -->
                tool_chart_match = re.search(r'<!-- CHART_TOOL_JSON: (.*?) -->', text)
                if tool_chart_match:
                    try:
                        import plotly.express as px
                        import pandas as pd
                        
                        payload = json.loads(tool_chart_match.group(1))
                        # Remove comment from text so it doesn't clutter the markdown logic
                        text = text.replace(tool_chart_match.group(0), "")
                        
                        df = pd.DataFrame(payload['data'])
                        c_type = payload.get('type', 'line')
                        
                        # Render the text *before* the chart? Or after?
                        # If we modified 'text', we need to re-render it? 
                        # Chunk logic: 'if text.strip(): st.markdown(text)' happens BEFORE this block in the original code?
                        # No, check the order.
                        
                        # Current order in file:
                        # 1. Unindent
                        # 2. Check Chart Data (Stock Old)
                        # 3. Render Text -> st.markdown(text)
                        # 4. Render Stock Chart (if chart_data)
                        # 5. Render Chart Tool (if tool_chart_match)
                        
                        # Issue: standard 'text' is rendered at step 3. 
                        # We are modifying 'text' at step 5! Too late!
                        # The comment is already inside the rendered markdown (invisible).
                        
                        # To fix: move detection UP, before st.markdown.
                        pass # Placeholder for logic move
                    except:
                        pass
                
                # RESTRUCTURED LOGIC BELOW
                
                # 1. Detect & Strip Stock Chart Data (Old)
                chart_match = re.search(r'<!-- CHART_DATA_JSON: (.*?) -->', text)
                chart_data = None
                if chart_match:
                    try:
                         chart_data = json.loads(chart_match.group(1))
                         text = text.replace(chart_match.group(0), "")
                    except: pass

                # 2. Detect & Strip Tool Chart Data (New)
                tool_chart_match = re.search(r'<!-- CHART_TOOL_JSON: (.*?) -->', text)
                tool_payload = None
                if tool_chart_match:
                    try:
                        tool_payload = json.loads(tool_chart_match.group(1))
                        text = text.replace(tool_chart_match.group(0), "")
                    except: pass

                # 3. Render Text
                # Relaxed check for "financial-card"
                if "financial-card" in text and ("class=" in text or "class:" in text):
                     st.html(text)
                else:
                    if text.strip():
                        st.markdown(text, unsafe_allow_html=True)
                        
                # 4. Render Stock Chart (Old - Keep for compatibility)
                if chart_data:
                    st.caption("📉 Price History (1 Month)")
                    st.line_chart(chart_data, x="Date", y="Close", color="#4caf50")
                    
                # 5. Render Tool Chart (New - Plotly)
                if tool_payload:
                    try:
                        import plotly.express as px
                        import pandas as pd
                        
                        df = pd.DataFrame(tool_payload['data'])
                        c_type = tool_payload.get('type', 'line')
                        title = tool_payload.get('title', 'Chart')
                        
                        st.caption(f"📊 {title}")
                        
                        if c_type == 'bar':
                            fig = px.bar(df, x=tool_payload['x'], y=tool_payload['y'])
                        elif c_type == 'scatter':
                            fig = px.scatter(df, x=tool_payload['x'], y=tool_payload['y'])
                        elif c_type == 'pie':
                            fig = px.pie(df, names=tool_payload['x'], values=tool_payload['y'])
                        else:
                            fig = px.line(df, x=tool_payload['x'], y=tool_payload['y'])
                            
                        # Improve Plotly Layout
                        fig.update_layout(margin=dict(l=20, r=20, t=30, b=20), height=300)
                        st.plotly_chart(fig, use_container_width=True)
                        
                    except Exception as e:
                        st.error(f"Error rendering chart: {e}")
                    
            elif chunk["type"] == "html":
                # Render widgets cleanly
                st.html(chunk["content"])

        # Footer with metadata
        if role == "assistant":
            st.markdown(
                "<div style='margin-top: 8px; font-size: 0.75rem; color: rgba(255,255,255,0.4); display: flex; align-items: center; gap: 6px;'>"
                "<span>⚡ EchoMindAI</span>"
                "<span style='width: 3px; height: 3px; background: #555; border-radius: 50%;'></span>"
                "<span>GPT-4o</span>"
                "<span style='width: 3px; height: 3px; background: #555; border-radius: 50%;'></span>"
                f"<span>{time.strftime('%H:%M')}</span>"
                "</div>", 
                unsafe_allow_html=True
            )

        if sources and role == "assistant":
            # Styled Expander
            with st.expander(f"📚 View {len(sources)} Sources"):
                for i, source in enumerate(sources, 1):
                    src_name = source.get('metadata', {}).get('source', 'Unknown')
                    st.caption(f"**Source {i}: {src_name}**")
                    st.markdown(f"<div style='font-size: 0.85rem; color: #cbd5e1; border-left: 2px solid #475569; padding-left: 10px; margin-bottom: 10px;'>{source['content'][:300]}...</div>", unsafe_allow_html=True)
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
                        # 1. Thinking Status (Restored Clean UI)
                        if st.session_state.get("debug_mode", False):
                            with st.expander("🐞 Agent Trace (Debug)", expanded=True):
                                st.write("**Input:**", prompt)
                                st.caption("Streaming raw thoughts...")

                        with st.status("🧠 Analyzing...", expanded=False) as status:
                            st.write("Checking Knowledge Base & Tools...")
                            status.update(label="✅ Response Ready", state="complete", expanded=False)

                        # 2. Streaming Response & Image Detection
                        full_response = ""
                        response_container = st.empty()
                        stop_container = st.empty() # Container for stop button
                        stop_generating = False
                        
                        import re
                        
                        # Stop Button UI
                        with stop_container:
                            if st.button("⏹ Stop Generating", key="stop_gen_btn"):
                                stop_generating = True

                        for chunk in agent.ask_stream(prompt):
                            # Check for stop signal (session state or button)
                            # Note: Buttons in loops are tricky in Streamlit. 
                            # Ideally we check session state, but immediate button requires rerun.
                            # We use a placeholder approach.
                            
                            full_response += chunk
                            
                            # Debug: Show raw tokens if debug mode is on
                            if st.session_state.get("debug_mode", False):
                                # We can't easily stream to two places without buffering, 
                                # but we can log unique large chunks or tool calls if we had them intercepted.
                                # For now, we'll just show the final raw output in the expander at the end.
                                pass

                            # Helper to clean response
                            def clean_response(text):
                                pattern = re.compile(r'```html\s*(.*?)\s*```', re.DOTALL | re.IGNORECASE)
                                match = pattern.search(text)
                                if match:
                                    return match.group(1)
                                text = re.sub(r'```\w*\s*', '', text) 
                                text = re.sub(r'```', '', text)
                                
                                # --- MATH RENDERING FIXER ---
                                # Convert standard LaTeX delimiters to Streamlit's required $$ format
                                
                                # 1. Replace explicit LaTeX \[ ... \] with $$ ... $$
                                text = text.replace(r'\[', '$$').replace(r'\]', '$$')
                                
                                # 2. Replace explicit LaTeX \( ... \) with $ ... $
                                text = text.replace(r'\(', '$').replace(r'\)', '$')
                                
                                # 3. SMART Bracket Detection
                                # Only convert [ ... ] to $$ ... $$ if it looks like math and NOT a list/JSON
                                # We check for typical math symbols (=, +, -, \frac, ^) and ensure it's not just quoted strings
                                def smart_math_replacer(match):
                                    content = match.group(1)
                                    # Anti-match: if it looks like a list "['a', 'b']" or "{"a":1}", ignore it
                                    if re.search(r"^['\"]|['\"]$|,\s*['\"]", content.strip()): 
                                        return f"[{content}]"
                                        
                                    # Pro-match: indicators of math
                                    if any(x in content for x in ['=', '\\', '^', '_', '+', '-']) or len(content) > 3:
                                        return f"$${content}$$"
                                        
                                    return f"[{content}]"
                                
                                # Only target brackets appearing at start of lines or standalone for safety
                                text = re.sub(r'(?m)^\[(.*?)\]$', smart_math_replacer, text)
                                
                                # --- INDENTATION FIXER ---
                                # Un-indent HTML blocks that might be treated as code by Markdown
                                def unindent_block(match):
                                    block = match.group(0)
                                    return "\n".join([line.strip() for line in block.splitlines()])

                                # Fix indentation for our specific widgets if they appear indented
                                text = re.sub(r'((?:    )+<div class="financial-card".*?(?:<!-- END_FINANCIAL_CARD -->|</div>\s*</div>))', unindent_block, text, flags=re.DOTALL)
                                
                                return text

                            # Real-time sanitization
                            display_text = clean_response(full_response)
                            
                            # Safety Net: If regex missed it but it looks like a financial card, Force HTML rendering
                            # Fix: Ensure backticks are gone so it doesn't render as code block
                            if "class=\"financial-card\"" in display_text or "class='financial-card'" in display_text:
                                display_text = re.sub(r'```(?:html|xml)?', '', display_text)
                                display_text = display_text.replace('```', '')
                                # We let st.markdown render it, but now without backticks it will render as HTML because of unsafe_allow_html=True
                                pass 
                            
                            display_text = re.sub(r'!\[.*?\]\((?!http|https).*?\)', ' *(Generating chart...)* ', display_text)
                            response_container.markdown(display_text + "▌", unsafe_allow_html=True)
                        
                        # Clear Stop Button
                        stop_container.empty()
                        
                        # Final display
                        cleaned_text = clean_response(full_response)
                        cleaned_text = re.sub(r'!\[.*?\]\((?!http|https).*?\)', ' *(See chart below)* ', cleaned_text)
                        
                        # Parsing Mixed Content (Text + HTML Widgets)
                        # We explicitly use parse_mixed_content to ensure <section> tags render as HTML
                        # and text renders as Markdown.
                        parts = parse_mixed_content(cleaned_text)
                        
                        # Clear the streaming placeholder
                        response_container.empty()
                        
                        # Render parts sequentially
                        for part in parts:
                            if part["type"] == "text":
                                if part["content"].strip():
                                    st.markdown(part["content"])
                            else:
                                st.markdown(part["content"], unsafe_allow_html=True)

                        if st.session_state.get("debug_mode", False):
                            with st.expander("🐞 Raw Output (Debug)"):
                                st.code(full_response)
                        
                        # UI Feature: Copy Button (Bottom Right, Minimal)
                        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True) # Spacer
                        col_spacer, col_copy = st.columns([0.85, 0.15])
                        with col_copy:
                             # Using a popover for a cleaner "Copy" interaction (Streamlit 1.30+)
                             # Falls back to standard expader behavior if popover not robust in this version,
                             # but using a localized expander is safer. We make it "text only" label.
                             with st.popover("📋 Copy"):
                                 st.code(full_response, language=None)
                        
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
                                
                                audio_data = None
                                
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
                                        audio_bytes.seek(0)
                                        audio_data = audio_bytes
                                    except Exception as e:
                                        print(f"OpenAI TTS failed: {e}. Falling back to gTTS.")
                                        audio_data = None

                                if not audio_data:
                                    # Fallback to gTTS
                                    try:
                                        from gtts import gTTS
                                        tts = gTTS(text=clean_text, lang='en')
                                        audio_fp = io.BytesIO()
                                        tts.write_to_fp(audio_fp)
                                        audio_fp.seek(0)
                                        audio_data = audio_fp
                                    except Exception as gtts_error:
                                        print(f"gTTS failed: {gtts_error}")
                                        # Only show toast on error, don't crash or show ugly red box
                                        # st.toast("Voice output failed (Network/API)", icon="⚠️")
                                        audio_data = None
                                
                                if audio_data and audio_data.getbuffer().nbytes > 100:
                                    # Write valid WAV header if needed or ensure bytes are ready
                                    # Streamlit audio handles BytesIO well if format is specified
                                    # Use unique key to prevent duplicate widgets
                                    st.audio(audio_data, format="audio/mp3", autoplay=True, key=f"audio_{message_id}")
                                
                                # Only render if we have valid data
                                if audio_data and audio_data.getbuffer().nbytes > 100:
                                    st.audio(audio_data, format="audio/mp3")

                        except Exception:
                            pass

                        # Save history (We save the full response with the image link for continuity)
                        msg_data = {"role": "assistant", "content": full_response}
                        st.session_state.messages.append(msg_data)
                        
                    except Exception as e:
                        st.error(f"Something went wrong: {e}")

if __name__ == "__main__":
    main()
