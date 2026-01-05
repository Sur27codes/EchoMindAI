"""
Deep Research Module for EchoMindAI.
Reference: "Deep Research" pattern (Plan -> Execute -> Synthesize).
"""
import json
from typing import List, Dict, Generator
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
import os

class ResearchAgent:
    def __init__(self):
        # Initialize LLM (fast model for planning, smart model for synthesis if available)
        # We use strict JSON mode for planning
        self.llm = ChatGroq(
            model_name="llama-3.1-70b-versatile",
            temperature=0.4,
            api_key=os.getenv("GROQ_API_KEY")
        )
        self.search_tool = DuckDuckGoSearchRun()

    def plan_research(self, topic: str) -> List[str]:
        """
        Generates a list of search queries to investigate the topic thoroughly.
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a Research Lead. Break down the user's topic into 3-5 distinct, specific web search queries that would collectively provide a comprehensive answer. Return ONLY a JSON list of strings."),
            ("user", f"Topic: {topic}")
        ])
        
        chain = prompt | self.llm
        try:
            response = chain.invoke({})
            # Naive JSON parsing of the content
            content = response.content.replace("```json", "").replace("```", "").strip()
            queries = json.loads(content)
            if isinstance(queries, list):
                return queries[:5] # Limit to 5
            return [topic]
        except Exception as e:
            print(f"Planning Error: {e}")
            return [topic, f"{topic} analysis", f"{topic} latest news"]

    def execute_research(self, topic: str) -> Generator[Dict, None, str]:
        """
        Generator that yields progress updates and finally returns the synthesized report.
        """
        yield {"status": "planning", "message": "🧠 Analyzing topic and generating research plan..."}
        
        queries = self.plan_research(topic)
        yield {"status": "plan_ready", "plan": queries}
        
        results = []
        for i, query in enumerate(queries):
            yield {"status": "searching", "message": f"🔎 Searching: {query}...", "progress": (i+1)/len(queries)}
            try:
                # Use the tool
                content = self.search_tool.run(query)
                results.append(f"### Source: {query}\n{content}\n")
            except Exception as e:
                yield {"status": "error", "message": f"Failed search: {query}"}
        
        # Synthesis
        yield {"status": "synthesizing", "message": "✍️ Reading sources and writing report..."}
        
        context_block = "\n".join(results)
        final_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a Senior Editor at a top-tier tech magazine (like Wired or The Verge). "
                       "Write a synthesized report based on the provided research notes.\n\n"
                       "**Writing Style Rules:**\n"
                       "- **Clear & Engaging**: Use active voice. Avoid academic jargon.\n"
                       "- **Structured**: Use clear H2 and H3 headers.\n"
                       "- **Key Insights Box**: Start with a 'TL;DR' or 'Executive Summary' block.\n"
                       "- **Citations**: Inline links are preferred over footnotes.\n"
                       "- **Formatting**: Use bolding for key terms to make it skimmable.\n"),
            ("user", f"Original Topic: {topic}\n\nResearch Notes:\n{context_block}")
        ])
        
        chain = final_prompt | self.llm
        report = chain.invoke({})
        
        yield {"status": "complete", "message": "Done."}
        # Yield the final report as a string so consumers can iterate to get it
        yield report.content
