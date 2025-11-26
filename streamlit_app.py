"""Streamlit web interface for the RAG agent."""
from __future__ import annotations

import os
import sys
from pathlib import Path

import streamlit as st

# Add src to path so we can import rag_agent
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Suppress tokenizers warning
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
# Suppress PyTorch warnings
import warnings
warnings.filterwarnings("ignore", message=".*torch.classes.*")
warnings.filterwarnings("ignore", category=UserWarning, module="torch")

from rag_agent.config import settings
from rag_agent.ingest import ingest_documents
from rag_agent.rag_agent import RAGAgent

# Page config
st.set_page_config(
    page_title="RAG Agent - Project X",
    page_icon="🤖",
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


def initialize_agent():
    """Initialize the RAG agent."""
    try:
        if st.session_state.agent is None:
            with st.spinner("Loading RAG agent..."):
                st.session_state.agent = RAGAgent()
        return st.session_state.agent
    except FileNotFoundError as e:
        st.error(f"Vector store not found. Please run ingestion first. Error: {e}")
        return None
    except Exception as e:
        st.error(f"Error initializing agent: {e}")
        return None


def main():
    st.title("🤖 RAG Agent - Project X")
    st.markdown("Ask questions about your documents using Retrieval-Augmented Generation")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Show current settings
        st.subheader("Current Settings")
        st.text(f"Embedding: {settings.embedding_provider}")
        st.text(f"Chat Model: {settings.chat_provider}")
        st.text(f"Chat Model Name: {settings.chat_model}")
        
        # Check API key status
        import os
        if settings.chat_provider == "groq":
            api_key = os.getenv("GROQ_API_KEY", "")
            if api_key and api_key != "gsk-your-groq-key":
                st.success("✓ Groq API key configured")
            else:
                st.error("❌ Groq API key not set")
                st.info("Set GROQ_API_KEY in your .env file")
        
        st.divider()
        
        # Ingestion section
        st.subheader("📚 Document Ingestion")
        
        if st.session_state.vector_store_exists:
            st.success("✓ Vector store exists")
        else:
            st.warning("⚠️ Vector store not found")
        
        if st.button("🔄 Re-ingest Documents", use_container_width=True):
            with st.spinner("Ingesting documents..."):
                try:
                    location = ingest_documents()
                    st.success(f"✓ Documents ingested! Vector store saved to {location}")
                    st.session_state.vector_store_exists = True
                    st.session_state.agent = None  # Reset agent to reload vector store
                    st.rerun()
                except Exception as e:
                    st.error(f"Error during ingestion: {e}")
        
        st.divider()
        
        # Document upload (optional)
        st.subheader("📄 Upload Documents")
        uploaded_files = st.file_uploader(
            "Upload documents (Text, Markdown, PDF, Image)",
            type=["md", "txt", "pdf", "png", "jpg", "jpeg"],
            accept_multiple_files=True,
        )
        
        if uploaded_files and st.button("💾 Save Uploaded Files", use_container_width=True):
            saved_count = 0
            for uploaded_file in uploaded_files:
                file_path = settings.data_dir / uploaded_file.name
                try:
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    saved_count += 1
                except Exception as e:
                    st.error(f"Error saving {uploaded_file.name}: {e}")
            
            if saved_count > 0:
                st.success(f"✓ Saved {saved_count} file(s) to {settings.data_dir}")
                st.info("Click 'Re-ingest Documents' to update the vector store")
        
        st.divider()
        
        # Debug mode
        st.subheader("🔍 Debug")
        show_sources = st.checkbox("Show retrieved sources", value=False)
        st.session_state.show_sources = show_sources

    # Main chat interface
    if not st.session_state.vector_store_exists:
        st.warning(
            "⚠️ No vector store found. Please ingest documents first using the sidebar."
        )
        st.info(
            f"Add documents to `{settings.data_dir}` or upload them in the sidebar, "
            "then click 'Re-ingest Documents'."
        )
        return

    # Initialize agent
    agent = initialize_agent()
    if agent is None:
        return

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show sources if enabled and available
            if message["role"] == "assistant" and "sources" in message:
                with st.expander("📚 Sources"):
                    for i, source in enumerate(message["sources"], 1):
                        st.markdown(f"**[{i}]** {source['content'][:200]}...")
                        st.caption(f"Source: {source.get('metadata', {}).get('source', 'N/A')}")

    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Get retrieved documents if debug mode
                    sources = []
                    if st.session_state.get("show_sources", False):
                        docs = agent.vector_store.similarity_search(prompt, k=4)
                        sources = [
                            {
                                "content": doc.page_content,
                                "metadata": doc.metadata,
                            }
                            for doc in docs
                        ]
                    
                    # Get answer
                    answer = agent.ask(prompt)
                    st.markdown(answer)
                    
                    # Add assistant message with sources
                    message_data = {"role": "assistant", "content": answer}
                    if sources:
                        message_data["sources"] = sources
                    st.session_state.messages.append(message_data)
                    
                except Exception as e:
                    error_msg = f"Error: {e}"
                    st.error(error_msg)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": error_msg}
                    )

    # Clear chat button
    if st.session_state.messages:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()


if __name__ == "__main__":
    main()

