# =============================================================================
# capstone_streamlit.py — EHR Database Admin Assistant (Streamlit UI)
# Run: streamlit run capstone_streamlit.py
# =============================================================================

import os
import uuid
import streamlit as st

st.set_page_config(
    page_title="EHR Database Assistant",
    page_icon="🗄️",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource
def load_agent():
    from langchain_groq import ChatGroq
    from day13_capstone import build_knowledge_base, retrieval_test, build_graph

    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", st.secrets.get("GROQ_API_KEY", ""))
    if not GROQ_API_KEY:
        st.error("❌ GROQ_API_KEY not set. Add it to .streamlit/secrets.toml")
        st.stop()

    llm = ChatGroq(api_key=GROQ_API_KEY, model="llama-3.3-70b-versatile", temperature=0.1)
    collection = build_knowledge_base()
    retrieval_test(collection)
    app = build_graph(llm, collection)
    return app


def ask_agent(app, question, thread_id, history, staff_name):
    from day13_capstone import CapstoneState
    config = {"configurable": {"thread_id": thread_id}}
    state: CapstoneState = {
        "question":      question,
        "messages":      history.copy(),
        "route":         "",
        "retrieved":     "",
        "sources":       [],
        "tool_result":   "",
        "db_result":     "",
        "answer":        "",
        "faithfulness":  0.0,
        "eval_retries":  0,
        "staff_name":    staff_name,
        "patient_focus": "",
    }
    return app.invoke(state, config=config)


def init_session():
    defaults = {
        "thread_id":    str(uuid.uuid4()),
        "chat_history": [],
        "graph_history":[],
        "staff_name":   "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🗄️ EHR Database Assistant")
    st.markdown("*Electronic Health Record System*")
    st.divider()

    st.markdown("### 👤 Staff Login")
    name_input = st.text_input("Your Name", value=st.session_state.staff_name, placeholder="e.g. Divya")
    if name_input:
        st.session_state.staff_name = name_input.strip().capitalize()

    st.divider()
    st.markdown("### 🗃️ Database Tables")
    st.markdown("""
| Table | Contents |
|-------|---------|
| `patients` | Demographics, insurance |
| `diagnoses` | Clinical notes |
| `medications` | Prescriptions |
| `lab_results` | Test reports |
| `admissions` | Ward history |
    """)

    st.divider()
    st.markdown("### 👥 Patients in DB")
    st.info(
        "**P-1001** Arjun Mehta\n\n"
        "**P-1002** Priya Sharma\n\n"
        "**P-1003** Venkat Rao\n\n"
        "**P-1004** Sneha Iyer\n\n"
        "**P-1005** Mohammed Farouk\n\n"
        "**P-1006** Lakshmi Devi\n\n"
        "**P-1007** Rajan Pillai\n\n"
        "**P-1008** Deepa Nair\n\n"
        "**P-1009** Aditya Verma\n\n"
        "**P-1010** Geeta Reddy ⚠️ Admitted"
    )

    st.divider()
    st.markdown("### 💡 Try Asking")
    st.caption("• List all patients in the database")
    st.caption("• What medications is Arjun Mehta on?")
    st.caption("• Show Priya Sharma's abnormal lab results")
    st.caption("• What is Venkat Rao's diagnosis?")
    st.caption("• Show Sneha Iyer's lab results")
    st.caption("• What is Mohammed Farouk's treatment plan?")
    st.caption("• What medications is Lakshmi Devi on?")
    st.caption("• Show Rajan Pillai's admission history")
    st.caption("• What are Deepa Nair's lab results?")
    st.caption("• What is Aditya Verma's diagnosis?")
    st.caption("• Which patient is currently admitted?")
    st.caption("• What is the policy for critical lab values?")
    st.caption("• What is today's date for a record entry?")

    st.divider()
    if st.button("🔄 New Session", use_container_width=True):
        st.session_state.thread_id     = str(uuid.uuid4())
        st.session_state.chat_history  = []
        st.session_state.graph_history = []
        st.rerun()

    st.caption("⚠️ All patient data is synthetic mock data for educational purposes only.")

# ── MAIN ──────────────────────────────────────────────────────────────────────
st.markdown("""
<h2 style='color:#1a4f7a;'>🗄️ EHR Database Assistant</h2>
<p style='color:#555;'>Query patient records, lab results, medications, diagnoses, and admissions 
directly from the MySQL EHR database using natural language.<br>
<em>Data is retrieved live from the database — nothing is fabricated.</em></p>
""", unsafe_allow_html=True)

# DB connection status
from day13_capstone import get_db_connection, MYSQL_AVAILABLE
if not MYSQL_AVAILABLE:
    st.warning("⚠️ mysql-connector-python not installed. Run: `pip install mysql-connector-python`")
else:
    conn_test = get_db_connection()
    if conn_test:
        conn_test.close()
        st.success("✅ MySQL database connected — ehr_db")
    else:
        st.error("❌ MySQL connection failed. Check your credentials in `.streamlit/secrets.toml`")

st.divider()

# Chat history display
for msg in st.session_state.chat_history:
    role = msg["role"]
    with st.chat_message(role, avatar="👤" if role == "user" else "🗄️"):
        st.markdown(msg["content"])
        if role == "assistant" and "meta" in msg:
            meta = msg["meta"]
            c1, c2, c3 = st.columns(3)
            c1.caption(f"Route: `{meta.get('route','N/A')}`")
            c2.caption(f"Faithfulness: `{meta.get('faithfulness',0):.2f}`")
            if meta.get("sources"):
                c3.caption(f"Source: {', '.join(meta['sources'][:2])}")

# Load agent
app = load_agent()

# Chat input
if prompt := st.chat_input("Ask about patients, medications, lab results, diagnoses..."):
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🗄️"):
        with st.spinner("Querying EHR database..."):
            result = ask_agent(
                app, prompt,
                st.session_state.thread_id,
                st.session_state.graph_history,
                st.session_state.staff_name,
            )

        answer = result.get("answer", "Unable to process. Please try again.")
        st.markdown(answer)

        meta = {
            "route":       result.get("route", "N/A"),
            "faithfulness": result.get("faithfulness", 1.0),
            "sources":     result.get("sources", []),
        }
        c1, c2, c3 = st.columns(3)
        c1.caption(f"Route: `{meta['route']}`")
        c2.caption(f"Faithfulness: `{meta['faithfulness']:.2f}`")
        if meta["sources"]:
            c3.caption(f"Source: {', '.join(meta['sources'][:2])}")

    st.session_state.chat_history.append({
        "role": "assistant", "content": answer, "meta": meta
    })
    st.session_state.graph_history = result.get("messages", [])
    if result.get("staff_name"):
        st.session_state.staff_name = result["staff_name"]

st.divider()
st.caption("EHR Database System | MySQL Backend | Agentic AI Capstone 2026 | All data shown is synthetic mock data.")