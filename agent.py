# agent.py — EHR Database Agent wrapper
# Usage:
#   from agent import EHRAgent
#   agent = EHRAgent()
#   print(agent.chat("What medications is Arjun Mehta on?"))

import os
import uuid
from day13_capstone import build_knowledge_base, build_graph, CapstoneState
from langchain_groq import ChatGroq


class EHRAgent:
    def __init__(self, groq_api_key: str = None):
        api_key = groq_api_key or os.environ.get("GROQ_API_KEY", "")
        if not api_key:
            raise ValueError("GROQ_API_KEY must be set or passed explicitly.")
        self.llm        = ChatGroq(api_key=api_key, model="llama-3.3-70b-versatile", temperature=0.1)
        self.collection = build_knowledge_base()
        self.app        = build_graph(self.llm, self.collection)
        self._sessions  = {}

    def chat(self, question: str, thread_id: str = None) -> str:
        if thread_id is None:
            thread_id = str(uuid.uuid4())
        history = self._sessions.get(thread_id, [])
        config  = {"configurable": {"thread_id": thread_id}}
        state: CapstoneState = {
            "question": question, "messages": history.copy(),
            "route": "", "retrieved": "", "sources": [],
            "tool_result": "", "db_result": "", "answer": "",
            "faithfulness": 0.0, "eval_retries": 0,
            "staff_name": "", "patient_focus": "",
        }
        result = self.app.invoke(state, config=config)
        self._sessions[thread_id] = result.get("messages", [])
        return result["answer"]

    def new_session(self) -> str:
        tid = str(uuid.uuid4())
        self._sessions[tid] = []
        return tid
