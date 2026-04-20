# Electronic Health Record Database — Agentic AI Capstone

**Domain:** Electronic Health Record (EHR) Database System  
**User:** Hospital Admin Staff  
**LLM:** Groq (llama3-8b-8192) | **Database:** MySQL | **UI:** Streamlit

---

## Project Structure

```
electronic-health-record/
├── ehr_schema.sql          ← MySQL schema + seed data (run this first)
├── day13_capstone.py       ← Core: DB connection, KB, State, Nodes, Graph, Tests
├── capstone_streamlit.py   ← Streamlit UI
├── agent.py                ← Clean EHRAgent class
├── requirements.txt
├── .streamlit/
│   └── secrets.toml        ← API key + DB credentials
└── README.md
```

---

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up MySQL database
```bash
mysql -u root -p < ehr_schema.sql
```
This creates the `ehr_db` database with 5 tables and seeds all patient data.

### 3. Configure secrets
Edit `.streamlit/secrets.toml`:
```toml
GROQ_API_KEY   = "gsk_your_key_here"
MYSQL_HOST     = "localhost"
MYSQL_PORT     = "3306"
MYSQL_USER     = "root"
MYSQL_PASSWORD = "your_mysql_password"
MYSQL_DATABASE = "ehr_db"
```

### 4. Run
```bash
streamlit run capstone_streamlit.py
```

---

## Architecture

```
User question
      ↓
[memory_node]    → sliding window (last 6), extract staff name + patient focus
      ↓
[router_node]    → database / retrieve / tool / memory_only
      ↓
[database_node]  → NL→SQL template → MySQL query → structured result
[retrieval_node] → ChromaDB → EHR policy / schema context
[tool_node]      → datetime for record timestamps
[skip_node]      → memory-only path
      ↓
[answer_node]    → Groq LLM formats DB result into clean natural language
      ↓
[eval_node]      → faithfulness check 0.0-1.0, retry if <0.7
      ↓
[save_node]      → append to messages → END
```

---

## Database Tables

| Table | Description |
|-------|-------------|
| `patients` | Demographics, blood group, allergies, insurance |
| `diagnoses` | Clinical notes, treatment plans, alerts |
| `medications` | Current and past prescriptions |
| `lab_results` | Test results with Normal/High/Low/Critical flags |
| `admissions` | Ward admissions and discharge summaries |

---

## Six Mandatory Capabilities

| # | Capability | Implementation |
|---|-----------|---------------|
| 1 | LangGraph StateGraph (3+ nodes) | 9 nodes: memory, router, database, retrieve, skip, tool, answer, eval, save |
| 2 | ChromaDB RAG (10+ docs) | 12 docs: DB schema, EHR policies, patient summaries |
| 3 | MemorySaver + thread_id | Sliding window msgs[-6:], tracks patient_focus across turns |
| 4 | Self-reflection eval node | Faithfulness 0.0-1.0, retries if <0.7, MAX_EVAL_RETRIES=2 |
| 5 | Tool use beyond retrieval | `database_query_tool` (MySQL SELECT) + `datetime_tool` |
| 6 | Streamlit deployment | @st.cache_resource, st.session_state, DB connection status indicator |

---

## Sample Questions to Ask

- "What medications is Arjun Mehta currently on?"
- "Show me all abnormal lab results for Venkat Rao"
- "What is Priya Sharma's latest diagnosis?"
- "List all admissions for Arjun Mehta"
- "What is the policy for releasing patient records?"
- "What is today's date for a record entry?"
- "List all patients in the database"
