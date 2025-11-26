"""Conversational RAG agent built on LangChain."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

from langchain_core.messages import BaseMessage
from langchain_community.vectorstores import FAISS
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda, RunnableParallel
from .config import settings
from .embeddings import get_embeddings
from .llm import get_llm


def _format_docs(docs: Iterable) -> str:
    formatted = []
    for idx, doc in enumerate(docs, start=1):
        # Clean up the content and make it more readable
        content = doc.page_content.strip()
        source = doc.metadata.get('source', 'Unknown')
        formatted.append(f"Document {idx} (from {source}):\n{content}")
    if not formatted:
        return "No relevant documents found."
    return "\n\n---\n\n".join(formatted)


class RAGAgent:
    """Thin wrapper that wires retrieval with a chat model."""

    def __init__(self, vector_store: FAISS | None = None) -> None:
        settings.ensure_dirs()
        self.vector_store = vector_store or self._load_vector_store()
        self.llm = get_llm()
        self.chain = self._build_chain()

    def _load_vector_store(self) -> FAISS:
        vector_path = Path(settings.vector_dir)
        if not vector_path.exists():
            raise FileNotFoundError(
                f"Vector store missing at {vector_path}. Run ingest_documents() first."
            )
        embeddings = get_embeddings()
        return FAISS.load_local(
            str(vector_path),
            embeddings=embeddings,
            index_name="projectx",
            allow_dangerous_deserialization=True,
        )

    def _build_chain(self):
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 4})
        
        # Create prompt template with proper variable substitution
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a helpful assistant. Answer questions using the context provided. The context contains relevant information from documents. Use it to answer the question."),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "Context:\n{context}\n\nQuestion: {question}\n\nAnswer the question using the context provided above."),
            ]
        )

        # Build chain with RunnableParallel
        # The output dict from RunnableParallel will be passed to ChatPromptTemplate
        retrieval_chain = (
            RunnableLambda(lambda x: x["question"])
            | retriever
            | RunnableLambda(_format_docs)
        )
        
        chain = (
            RunnableParallel(
                context=retrieval_chain,
                question=RunnableLambda(lambda x: x["question"]),
                chat_history=RunnableLambda(lambda x: x.get("chat_history", [])),
            )
            | prompt
            | self.llm
            | StrOutputParser()
        )
        return chain

    @staticmethod
    def _coerce_history(messages: list[tuple[str, str]] | List[BaseMessage] | None) -> List[BaseMessage]:
        if not messages:
            return []
        if isinstance(messages[0], BaseMessage):
            return list(messages)  # type: ignore[return-value]
        coerced: List[BaseMessage] = []
        for role, content in messages:
            if role == "human":
                coerced.append(HumanMessage(content=content))
            else:
                coerced.append(AIMessage(content=content))
        return coerced

    def ask(
        self,
        question: str,
        chat_history: list[tuple[str, str]] | List[BaseMessage] | None = None,
        return_context: bool = False,
    ) -> str | tuple[str, str]:
        """Ask a question and optionally return the context used."""
        history = self._coerce_history(chat_history)
        
        # Get context separately for debugging
        docs = self.vector_store.similarity_search(question, k=4)
        context = _format_docs(docs)
        
        result = self.chain.invoke({"question": question, "chat_history": history})
        
        if return_context:
            return result, context
        return result


__all__ = ["RAGAgent"]
