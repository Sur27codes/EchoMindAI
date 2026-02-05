"""Conversational RAG Agent with Tools."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

from langchain_community.vectorstores import FAISS
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor

from .config import settings
from .embeddings import get_embeddings
from .llm import get_llm
from .llm import get_llm
from .tools import calculator, generate_plot, web_search, save_file, translate_content
from .tools_external import get_weather, get_global_news, find_hotels, search_products, get_map_location, find_relevant_links, get_images, generate_ai_image, get_stock_price
from .tools_visualization import create_chart
import queue
import threading
from langchain_core.callbacks import BaseCallbackHandler

class StreamHandler(BaseCallbackHandler):
    """Callback handler that streams LLM tokens to a queue."""
    def __init__(self, q: queue.Queue):
        self.q = q
        self.tokens_received = False

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.tokens_received = True
        self.q.put(token)

    def on_tool_end(self, output: str, **kwargs) -> None:
        pass


class RAGAgent:
    """Agent that can chat, calculate, plot, and search documents."""

    def __init__(self, vector_store: FAISS | None = None) -> None:
        settings.ensure_dirs()
        self.vector_store = vector_store or self._load_vector_store()
        self.llm = get_llm()
        self.agent_executor = self._build_agent()
        from langchain_core.chat_history import InMemoryChatMessageHistory
        self.history = InMemoryChatMessageHistory()

    def _load_vector_store(self) -> FAISS:
        """Load vector store or create empty one if missing."""
        vector_path = Path(settings.vector_dir)
        embeddings = get_embeddings()
        
        if not vector_path.exists():
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
        # Enhanced with World Knowledge + Generative Tools
        tools = [
            search_knowledge_base, 
            calculator, 
            generate_plot, 
            web_search,
            get_weather,
            get_global_news,
            search_products,
            get_map_location,
            get_stock_price,
            create_chart,
            find_relevant_links,
            get_images,
            generate_ai_image,
            save_file,
            translate_content
        ]
        

        
        # 3. Create Prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are 'EchoMindAI', an Advanced Enterprise Intelligence Agent.\n"
                       "Your mission is to provide **COMPLETELY DYNAMIC**, **ACCURATE**, and **VISUALLY STUNNING** responses.\n"
                       "\n"
                       "**CORE GENERATION PROTOCOLS (STRICT):**\n"
                       "1. **DEEP DETAIL & ACCURACY**: Never give surface-level answers. Dive deep. Explain the 'Why', 'How', and 'History'. IF unsure, state your confidence level clearly.\n"
                       "2. **DYNAMIC STRUCTURE**: Adapt your formatting to the question. Use bolding, headers, lists, and tables to make the content readable and engaging.\n"
                       "3. **VISUAL FIRST**: For ANY physical object, place, product, or person, you **MUST** embed an image using `get_images`.\n"
                       "   - Format: `![Alt Text](ImageURL)`\n"
                       "   - **NEVER** leave a visual query text-only.\n"
                       "\n"
                       "**TOOL USAGE & RENDERING RULES (STRICT FORMATS):**\n"
                       "- **Weather**: You MUST use the `get_weather` tool. It returns HTML. **OUTPUT IT EXACTLY AS IS**. Do not modify it. Do not wrap it in markdown.\n"
                       "- **Finance**: You MUST use the `get_stock_price` tool. It returns HTML. **OUTPUT IT EXACTLY AS IS** (start with `<div`). Do not wrap it in markdown code blocks.\n"
                       "- **Shopping/Hotels**: You MUST use the **GRID LAYOUT HTML** below. **NEVER** use a list or text table.\n"
                       "  ```html\n"
                       "  <section class=\"product-grid\">\n"
                       "    <div class=\"product-card\">\n"
                       "      <div class=\"product-card-img-container\"><img src=\"IMAGE_URL\"/></div>\n"
                       "      <div class=\"product-card-content\">\n"
                       "         <h3>Title</h3>\n"
                       "         <div class=\"rating\">⭐ 4.8</div>\n"
                       "         <div class=\"price\">$Price</div>\n"
                       "         <p class=\"description\">Detailed specs...</p>\n"
                       "         <a href=\"LINK\" class=\"action-btn\">View</a>\n"
                       "      </div>\n"
                       "    </div>\n"
                       "  </section>\n"
                       "  ```\n"
                       "\n"
                       "**CONSISTENCY PROTOCOL:**\n"
                       "- **NEVER** change the UI format on your own.\n"
                       "- **ALWAYS** use the schemas above for their respective topics.\n"
                       "- **ACCURACY**: Verify facts. If a price or rating is unknown, estimate reasonable values based on market data, but mark as 'Est.'.\n"
                       "\n"
                       "**MATH & STUDY PROTOCOL (USER FRIENDLY):**\n"
                       "**MATH & STUDY PROTOCOL (RENDERED):**\n"
                       "- **Equations**: You **MUST** use standard LaTeX math wrapped in `$$` delimiters for proper rendering.\n"
                       "- **Format**: `$$ \\int x^n dx = \\frac{{1}}{{n+1}} x^{{n+1}} + C $$` (This renders as a beautiful equation).\n"
                       "- **Structure**: \n"
                       "  1. **The Formula**: Show the core equation first using `$$` blocks.\n"
                       "  2. **The Example**: Provide a specific worked example (e.g., `n=5`).\n"
                       "  3. **Step-by-Step**: Explain the manipulation clearly.\n"
                       "  4. **Analogy/Concept**: Explain the intuition.\n"
                       "  4. **Example**: A concrete worked example or application.\n"
                       "- **Tone**: Encouraging, clear, and educational. Avoid dense walls of text. Use bullet points.\n"
                       "\n"
                       "**SOCIAL MEDIA & LINKS:**\n"
                       "- If asked for profiles (LinkedIn, Twitter, etc.), **ALWAYS** use `find_relevant_links` with the person's name + platform.\n"
                       "- Provide the actual clickable URLs in a neat list.\n"
                       "\n"
                       "**ERROR HANDLING PROTOCOL:**\n"
                       "- If a tool returns 'Search Failed' or 'Rate Limited', **DO NOT** make up information.\n"
                       "- Explicitly state: 'I am currently unable to search the live web due to high traffic/technical limits.'\n"
                       "- Offer to answer based on your internal knowledge or suggest the user tries again in a moment."
                       ),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        # 4. Create Agent
        agent = create_tool_calling_agent(self.llm, tools, prompt)
        
        # 5. Create Executor
        def _handle_error(error) -> str:
            # Robust Error Handler for "Parsing Failed" scenarios
            # This happens when the LLM answers directly (Good!) but the Agent expects a Tool (Bad parser).
            
            error_str = str(error)
            
            # Case 1: Standard LangChain "Could not parse"
            if "Could not parse LLM output:" in error_str:
                return error_str.split("Could not parse LLM output:")[-1].strip().strip('`')
                
            # Case 2: "Parsing failed" (New LangChain version)
            if "Parsing failed" in error_str:
                # Sometimes the raw output is buried in the exception
                # We try to salvage the text if possible, otherwise apologize
                # Often the *output* property of the exception holds the key
                if hasattr(error, "output"):
                    return str(error.output).strip().strip('`')
                if hasattr(error, "send_to_llm"): # Some exceptions allow re-sending
                     return "I have the answer but failed to format it structurally. Please check the raw logs."
                     
            # Case 3: Rate Limits or API Errors (Don't hide these!)
            if "429" in error_str or "Rate limit" in error_str:
                 return "**System Alert**: High Traffic. Please wait 10 seconds and try again. (Rate Limit)"

            # Fallback: Just return the raw error so the user isn't blind
            return f"**Agent System Info**: I generated a response, but the system parser caught an edge case.\n\nRaw context: {error_str[-200:]}"

        return AgentExecutor(
            agent=agent, 
            tools=tools, 
            verbose=False,  # Silent mode: Respond in UI, not Terminal
            handle_parsing_errors=_handle_error
        )

    def ask_stream(self, query: str):
        """Stream the agent's response."""
        q = queue.Queue()
        handler = StreamHandler(q)
        
        def run():
            try:
                # Use internal memory
                chat_history = self.history.messages
                res = self.agent_executor.invoke(
                    {"input": query, "chat_history": chat_history},
                    config={"callbacks": [handler]}
                )
                
                # Fallback: if no tokens streamed
                if not handler.tokens_received:
                   q.put(res.get("output", ""))
                   
                # Save to memory
                self.history.add_user_message(query)
                self.history.add_ai_message(res.get("output", ""))
                
            except Exception as e:
                q.put(f"Error: {e}")
            finally:
                q.put(None) # Sentinel

        thread = threading.Thread(target=run)
        thread.start()

        while True:
            token = q.get()
            if token is None:
                break
            yield token

    @staticmethod
    def _coerce_history(messages: list[tuple[str, str]] | List[BaseMessage] | None) -> List[BaseMessage]:
        """Helper to coerce chat history if passed explicitly (legacy support)."""
        if not messages:
            return []
        if isinstance(messages[0], BaseMessage):
            return list(messages)
        coerced: List[BaseMessage] = []
        for role, content in messages:
            if role == "human" or role == "user":
                coerced.append(HumanMessage(content=content))
            else:
                coerced.append(AIMessage(content=content))
        return coerced

    def ask(self, question: str, chat_history: list | None = None) -> str:
        """Synchronous ask with retry and caching."""
        # Check cache (simple in-memory)
        if not hasattr(self, "_response_cache"):
            self._response_cache = {}
        
        cache_key = f"{question}-{str(chat_history)}"
        cache_key = f"{question}-{str(chat_history)}"
        # if cache_key in self._response_cache:
        #     return self._response_cache[cache_key]

        from tenacity import retry, stop_after_attempt, wait_exponential
        
        @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
        def _invoke_with_retry(input_data):
            return self.agent_executor.invoke(input_data)

        # Simplified sync call using the same executor logic
        history = self.history.messages
        if chat_history:
             # If explicit history provided, use it (or merge it)
             history = self._coerce_history(chat_history)
             
        try:
            result = _invoke_with_retry({"input": question, "chat_history": history})
            output = result["output"]
            
            # Cache success
            self._response_cache[cache_key] = output
            # Limit cache size
            if len(self._response_cache) > 100:
                self._response_cache.pop(next(iter(self._response_cache)))
            
            # Update memory if we used the internal one
            if not chat_history:
                self.history.add_user_message(question)
                self.history.add_ai_message(output)
                
            return output
        except Exception as e:
            return f"Error: {str(e)} (after retries)"

__all__ = ["RAGAgent"]

