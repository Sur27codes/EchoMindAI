"""Simple CLI for running the RAG agent."""
from __future__ import annotations

import argparse
import os

from .ingest import ingest_documents
from .rag_agent import RAGAgent

# Suppress tokenizers parallelism warning
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
# Suppress PyTorch warnings
import warnings
warnings.filterwarnings("ignore", message=".*torch.classes.*")
warnings.filterwarnings("ignore", category=UserWarning, module="torch")


def handle_ingest(_: argparse.Namespace) -> None:
    location = ingest_documents()
    print(f"Vector store saved under {location}")


def handle_chat(args: argparse.Namespace) -> None:
    agent = RAGAgent()
    
    # Debug: Check what's being retrieved
    if args.debug:
        docs = agent.vector_store.similarity_search(args.question, k=4)
        print("\n--- RETRIEVED DOCUMENTS ---")
        for i, doc in enumerate(docs, 1):
            print(f"\n[{i}] {doc.page_content[:200]}...")
            print(f"    Source: {doc.metadata.get('source', 'N/A')}")
        print()
    
    answer = agent.ask(args.question)
    print("\n--- ANSWER ---")
    print(answer)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="RAG agent utilities")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser("ingest", help="Ingest local docs into FAISS")
    ingest_parser.set_defaults(func=handle_ingest)

    chat_parser = subparsers.add_parser("chat", help="Ask a question against the index")
    chat_parser.add_argument("question", type=str, help="User question")
    chat_parser.add_argument("--debug", action="store_true", help="Show retrieved documents")
    chat_parser.set_defaults(func=handle_chat)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
