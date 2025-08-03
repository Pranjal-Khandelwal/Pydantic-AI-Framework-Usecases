import os
import asyncio
import streamlit as st
from datetime import datetime
from pydantic import BaseModel
import ollama

#Ollama Setup
class OllamaChatModel:
    def __init__(self, model="llama3"):
        self.model = model

    async def chat(self, messages):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: ollama.chat(model=self.model, messages=messages)["message"]["content"])

for key, default in {
    "collected_facts": [],
    "research_started": False,
    "research_done": False,
    "report_result": None,
    "research_progress": 0,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

def save_important_fact(fact: str, source: str = None) -> str:
    for existing in st.session_state.collected_facts:
        if existing["fact"] == fact:
            return "⚠️ Fact already saved."

    st.session_state.collected_facts.append({
        "fact": fact,
        "source": source or "Not specified",
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })
    return f"✅ Fact saved: {fact}"

#Agent Setup
class SimpleAgent:
    def __init__(self, name, instructions, model):
        self.name = name
        self.instructions = instructions
        self.model = model

    async def run(self, user_input):
        return await self.model.chat([
            {"role": "system", "content": self.instructions},
            {"role": "user", "content": user_input}
        ])

query_agent = SimpleAgent(
    name="Query Agent",
    instructions="Generate 5–8 diverse and precise search queries on the topic.",
    model=OllamaChatModel("llama3")
)

research_agent = SimpleAgent(
    name="Research Agent",
    instructions="Provide bullet-point key facts on the topic. Keep it concise. Mention sources if known.",
    model=OllamaChatModel("llama3")
)

editor_agent = SimpleAgent(
    name="Editor Agent",
    instructions="Given the facts, compile a clean 300-500 word markdown report. Include an outline and list of sources.",
    model=OllamaChatModel("llama3")
)

st.set_page_config(page_title="AI Research Assistant", layout="wide")

st.title("Research Assistant")

with st.sidebar:
    st.header("🔍 Research Input")
    user_topic = st.text_input("Enter your topic:")
    start_btn = st.button("Start Research", disabled=not user_topic)

    st.markdown("---")
    st.progress(st.session_state.research_progress)

async def run_research(topic):
    st.session_state.research_started = True
    st.session_state.research_progress = 0
    st.session_state.collected_facts = []
    st.session_state.research_done = False

    st.markdown("## 🧠 Generating Queries")
    queries = await query_agent.run(topic)
    st.session_state.research_progress = 25
    st.code(queries)

    st.markdown("## 📚 Collecting Facts")
    facts = await research_agent.run(queries)
    st.session_state.research_progress = 50

    # Simulate fact-saving
    for line in facts.split("\n"):
        if line.strip():
            save_important_fact(line.strip())

    with st.expander("🧠 Saved Facts", expanded=True):
        for fact in st.session_state.collected_facts:
            st.markdown(f"🧠 **{fact['fact']}**  \n📌 Source: {fact['source']}  \n🕒 {fact['timestamp']}")

    st.markdown("## 📝 Compiling Report")
    combined_facts = "\n".join(f["fact"] for f in st.session_state.collected_facts)
    report = await editor_agent.run(combined_facts)
    st.session_state.research_progress = 100
    st.session_state.research_done = True
    st.session_state.report_result = report

if start_btn:
    with st.spinner("Researching..."):
        asyncio.run(run_research(user_topic))

if st.session_state.research_done and st.session_state.report_result:
    st.subheader("📖 Final Report")
    st.markdown(st.session_state.report_result)
    st.download_button(
        label="⬇️ Download Markdown",
        data=st.session_state.report_result,
        file_name="research_report.md",
        mime="text/markdown"
    )