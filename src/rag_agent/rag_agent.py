"""Conversational RAG Agent with Tools."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

from langchain_community.vectorstores import FAISS
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain.agents import create_tool_calling_agent, AgentExecutor

from .config import settings
from .embeddings import get_embeddings
from .llm import get_llm
from .tools import calculator, generate_plot, web_search


class RAGAgent:
    """Agent that can chat, calculate, plot, and search documents."""

    def __init__(self, vector_store: FAISS | None = None) -> None:
        settings.ensure_dirs()
        self.vector_store = vector_store or self._load_vector_store()
        self.llm = get_llm()
        self.agent_executor = self._build_agent()

    def _load_vector_store(self) -> FAISS:
        """Load vector store or create empty one if missing."""
        vector_path = Path(settings.vector_dir)
        embeddings = get_embeddings()
        
        if not vector_path.exists():
            # If missing, create an empty FAISS index so the agent doesn't crash
            # It will just return "I don't know" until data is ingested
            import faiss
            from langchain_community.docstore.in_memory import InMemoryDocstore
            index = faiss.IndexFlatL2(len(embeddings.embed_query("hello")))
            return FAISS(
                embedding_function=embeddings,
                index=index,
                docstore=InMemoryDocstore(),
                index_to_docstore_id={}
            )

        return FAISS.load_local(
            str(vector_path),
            embeddings=embeddings,
            index_name="echomindai",
            allow_dangerous_deserialization=True,
        )

    def _build_agent(self):
        # 1. Define Retrieval Tool
        @tool
        def search_knowledge_base(query: str) -> str:
            """
            Search the project's knowledge base (documents) for information.
            Use this for questions about specific projects, policies, or uploaded files.
            """
            docs = self.vector_store.similarity_search(query, k=4)
            if not docs:
                return "No relevant documents found."
            
            formatted = []
            for i, doc in enumerate(docs, 1):
                source = doc.metadata.get('source', 'Unknown')
                formatted.append(f"Source {i} ({source}):\n{doc.page_content}")
            return "\n\n---\n\n".join(formatted)

        # 2. Bind Tools
        tools = [search_knowledge_base, calculator, generate_plot, web_search]
        
        # 3. Create Prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are 'EchoMindAI', an expert AI Assistant specialized in Data Analysis and Research.\n"
                       "Your goal is to provide ACCURATE, DATA-DRIVEN answers.\n"
                       "\n"
                       "**TOOL USAGE PROTOCOL:**\n"
                       "1. **Plots**: Use `generate_plot` to create visualizations. DO NOT write `plt.savefig` or `path` in your code. The tool will return the image link automatically. You MUST include that link in your response.\n"
                       "2. **Math**: Use the `calculator` for all calculations. Do not guess.\n"
                       "3. **Search**: comprehensive answers with citations.\n"
                       "\n"
                       "**RESPONSE STYLE:**\n"
                       "- Professional, concise, and direct.\n"
                       "- Use Markdown tables for data.\n"
                       "- No fluff. Just the answer and the evidence.\n"
                       ),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        # 4. Create Agent
        agent = create_tool_calling_agent(self.llm, tools, prompt)
        
        # 5. Create Executor
        return AgentExecutor(agent=agent, tools=tools, verbose=True)

    @staticmethod
    def _coerce_history(messages: list[tuple[str, str]] | List[BaseMessage] | None) -> List[BaseMessage]:
        if not messages:
            return []
        if isinstance(messages[0], BaseMessage):
            return list(messages)  # type: ignore[return-value]
        coerced: List[BaseMessage] = []
        for role, content in messages:
            if role == "human" or role == "user":
                coerced.append(HumanMessage(content=content))
            else:
                coerced.append(AIMessage(content=content))
        return coerced

    def ask(self, question: str, chat_history: list | None = None) -> str:
        """Synchronous ask."""
        return self.ask_stream_sync(question, chat_history)

    def ask_stream_sync(self, question: str, chat_history: list | None = None) -> str:
        """
        Helper for sync calls, basically just invokes and returns 'output'.
        kept the name 'ask' compatible.
        """
        history = self._coerce_history(chat_history)
        result = self.agent_executor.invoke({"input": question, "chat_history": history})
        return result["output"]

    def ask_stream(self, question: str, chat_history: list | None = None):
        """
        Streaming generator that yields tokens.
        Note: The AgentExecutor streaming yields events (steps and output tokens).
        We filter specifically for the final answer tokens for the UI.
        """
        history = self._coerce_history(chat_history)
        
        # We use .stream() which yields chunks
        # We need to look for 'messages' in the output chunk usually, or just 'output' if available
        # But AgentExecutor.stream yields a dict of `{"output": "..."}` or `{"actions": ...}`
        
        # Simpler approach: Use the LLM's streaming if possible, but Tool use complicates it.
        # langchain .stream() on AgentExecutor usually yields Step dicts.
        
        # WORKAROUND: For this iteration, to keep the UI simple, we will stream the
        # *final answer* chunks if possible. If not, we fall back to yielding the final string.
        # But let's try to stream properly.
        
        for event in self.agent_executor.stream({"input": question, "chat_history": history}):
            # "output" key exists in the final response chunk
            if "output" in event:
                # This usually comes as a single block in standard executor stream...
                # To get token-by-token, we need .astream_events maybe?
                # For now, let's just yield the block.
                yield event["output"]


__all__ = ["RAGAgent"]

