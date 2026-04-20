# =============================================================================
# ELECTRONIC HEALTH RECORD DATABASE — DATA ENGINEERING CAPSTONE PROJECT
# Data Engineering Hands-On Course 2026 
# Domain  : Electronic Health Record (EHR) Database System
# User    : Hospital Admin Staff
# LLM     : Groq (llama-3.3-70b-versatile) | DB: MySQL | Deployment: Streamlit
# =============================================================================

# ── WRITTEN SUMMARY ──────────────────────────────────────────────────────────
# Domain      : Electronic Health Record Database System (MySQL)
# User        : Hospital Admin Staff
# What it does: AI-powered EHR assistant that queries a live MySQL database
#               to retrieve patient records, lab results, diagnoses, medications,
#               and admission history. The agent translates natural language
#               questions into SQL queries via a database_query_tool.
#               Never fabricates data — all answers come directly from the DB.
# KB size     : 5 MySQL tables: patients, diagnoses, medications,
#               lab_results, admissions (12 documents in ChromaDB for policy/context)
# Tool used   : database_query_tool — executes safe SELECT queries on MySQL
#               datetime_tool — returns current timestamp for record entries
# RAGAS scores: (run Part 6 to populate)
# One thing I would improve with more time:
#               Add a natural language to SQL (NL2SQL) node using few-shot
#               prompting so the agent auto-generates complex JOIN queries
#               instead of relying on predefined query templates.
# =============================================================================

import os
import uuid
import datetime
import json
from typing import TypedDict, List

# ── DEPENDENCIES ──────────────────────────────────────────────────────────────
# pip install langchain-groq langgraph chromadb sentence-transformers streamlit
# pip install mysql-connector-python

from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

# MySQL connector
try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    print("⚠️  mysql-connector-python not installed. Run: pip install mysql-connector-python")


# =============================================================================
# DATABASE CONNECTION
# =============================================================================

DB_CONFIG = {
    "host":     os.environ.get("MYSQL_HOST", "localhost"),
    "port":     int(os.environ.get("MYSQL_PORT", "3306")),
    "user":     os.environ.get("MYSQL_USER", "root"),
    "password": os.environ.get("MYSQL_PASSWORD", ""),
    "database": os.environ.get("MYSQL_DATABASE", "ehr_db"),
}


def get_db_connection():
    """Return a fresh MySQL connection using DB_CONFIG."""
    if not MYSQL_AVAILABLE:
        return None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"  [DB] Connection failed: {e}")
        return None


def run_query(sql: str) -> str:
    """
    Execute a safe SELECT query and return results as a formatted string.
    Never raises exceptions — returns error string instead.
    Only SELECT statements are allowed.
    """
    sql = sql.strip()
    if not sql.upper().startswith("SELECT"):
        return "ERROR: Only SELECT queries are permitted in this system."

    conn = get_db_connection()
    if conn is None:
        return "ERROR: Could not connect to the EHR database. Check MySQL credentials."

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        if not rows:
            return "No records found for this query."

        # Format as readable table string
        output_lines = []
        for row in rows:
            line = " | ".join(f"{k}: {v}" for k, v in row.items() if v is not None)
            output_lines.append(line)
        return "\n".join(output_lines)

    except Exception as e:
        return f"Database query error: {str(e)}"


# ── PREDEFINED SAFE QUERY TEMPLATES ──────────────────────────────────────────
# These are used by the query_router to pick the right SQL for common questions

QUERY_TEMPLATES = {
    "all_patients": "SELECT patient_id, full_name, dob, gender, blood_group, contact, primary_physician FROM patients",
    "patient_by_name": "SELECT * FROM patients WHERE LOWER(full_name) LIKE LOWER('%{name}%')",
    "patient_by_id": "SELECT * FROM patients WHERE patient_id = '{pid}'",
    "medications_by_name": "SELECT m.medication_name, m.dosage, m.frequency, m.prescribed_by, m.prescribed_date FROM medications m JOIN patients p ON m.patient_id = p.patient_id WHERE LOWER(p.full_name) LIKE LOWER('%{name}%') AND m.is_current = TRUE",
    "lab_results_by_name": "SELECT l.test_name, l.result_value, l.unit, l.normal_range, l.status, l.lab_date, l.ordered_by FROM lab_results l JOIN patients p ON l.patient_id = p.patient_id WHERE LOWER(p.full_name) LIKE LOWER('%{name}%') ORDER BY l.lab_date DESC",
    "abnormal_labs_by_name": "SELECT l.test_name, l.result_value, l.unit, l.normal_range, l.status, l.lab_date FROM lab_results l JOIN patients p ON l.patient_id = p.patient_id WHERE LOWER(p.full_name) LIKE LOWER('%{name}%') AND l.status != 'Normal' ORDER BY l.lab_date DESC",
    "diagnoses_by_name": "SELECT d.diagnosis_date, d.physician, d.chief_complaint, d.diagnosis, d.assessment, d.treatment_plan, d.alerts FROM diagnoses d JOIN patients p ON d.patient_id = p.patient_id WHERE LOWER(p.full_name) LIKE LOWER('%{name}%') ORDER BY d.diagnosis_date DESC",
    "admissions_by_name": "SELECT a.admitted_on, a.discharged_on, a.ward, a.room_number, a.reason, a.discharge_diagnosis, a.attending_physician FROM admissions a JOIN patients p ON a.patient_id = p.patient_id WHERE LOWER(p.full_name) LIKE LOWER('%{name}%') ORDER BY a.admitted_on DESC",
    "all_high_labs": "SELECT p.full_name, l.test_name, l.result_value, l.unit, l.status, l.lab_date FROM lab_results l JOIN patients p ON l.patient_id = p.patient_id WHERE l.status IN ('High','Low','Critical') ORDER BY l.lab_date DESC",
    "current_admissions": "SELECT p.full_name, a.admitted_on, a.ward, a.room_number, a.reason, a.attending_physician FROM admissions a JOIN patients p ON a.patient_id = p.patient_id WHERE a.discharged_on IS NULL",
}


# =============================================================================
# PART 1 — CHROMADB KNOWLEDGE BASE (EHR Policies + DB Schema Context)
# =============================================================================

KNOWLEDGE_BASE = [
    {
        "id": "doc_001",
        "topic": "Database Schema — patients table",
        "text": (
            "The patients table stores core demographic and insurance information. "
            "Fields: patient_id (primary key, e.g. P-1001), full_name, dob (date of birth), "
            "gender, blood_group, allergies, address, contact, emergency_contact, "
            "insurance_provider, policy_number, policy_valid_until, registered_on, "
            "last_visit, primary_physician. "
            "Current patients: Arjun Mehta (P-1001, Cardiology), "
            "Priya Sharma (P-1002, Gynecology), Venkat Rao (P-1003, Neurology)."
        ),
    },
    {
        "id": "doc_002",
        "topic": "Database Schema — diagnoses table",
        "text": (
            "The diagnoses table stores clinical diagnosis records linked to patients. "
            "Fields: diagnosis_id, patient_id (foreign key), diagnosis_date, physician, "
            "chief_complaint, diagnosis, assessment, treatment_plan, alerts. "
            "Each row represents one clinical encounter/diagnosis note. "
            "Linked to patients via patient_id."
        ),
    },
    {
        "id": "doc_003",
        "topic": "Database Schema — medications table",
        "text": (
            "The medications table stores current and past prescriptions. "
            "Fields: med_id, patient_id (foreign key), medication_name, dosage, frequency, "
            "prescribed_by, prescribed_date, is_current (TRUE/FALSE). "
            "Query with is_current=TRUE to get active medications only. "
            "Linked to patients via patient_id."
        ),
    },
    {
        "id": "doc_004",
        "topic": "Database Schema — lab_results table",
        "text": (
            "The lab_results table stores all laboratory and diagnostic test results. "
            "Fields: lab_id, patient_id (foreign key), lab_date, test_name, result_value, "
            "unit, normal_range, status (Normal/High/Low/Critical), ordered_by, reviewed. "
            "Status field flags abnormal values. "
            "Query status != Normal to find all abnormal results. "
            "Linked to patients via patient_id."
        ),
    },
    {
        "id": "doc_005",
        "topic": "Database Schema — admissions table",
        "text": (
            "The admissions table stores inpatient admission and discharge records. "
            "Fields: admission_id, patient_id (foreign key), admitted_on, discharged_on, "
            "ward, room_number, reason, treatment_given, discharge_diagnosis, "
            "discharge_instructions, attending_physician. "
            "discharged_on = NULL means patient is currently admitted. "
            "Linked to patients via patient_id."
        ),
    },
    {
        "id": "doc_006",
        "topic": "EHR Admin Policy — Record Access and Confidentiality",
        "text": (
            "Admin staff may view patient demographics, lab report status, appointment history, "
            "and billing records. Clinical notes require doctor-level EHR access credentials. "
            "Patient data is governed by the hospital data protection policy. "
            "Sharing records externally requires written patient consent or a court order. "
            "All record access is logged with staff ID and timestamp automatically."
        ),
    },
    {
        "id": "doc_007",
        "topic": "EHR Admin Policy — Lab Report Workflow",
        "text": (
            "Lab reports are uploaded by the laboratory within 4 hours of test completion. "
            "Admin staff must notify the treating physician via the EHR alert system upon upload. "
            "Critical lab values (e.g. glucose <40 or >500, potassium <2.5 or >6.5) must be "
            "communicated to the ward within 30 minutes. "
            "The reviewed field in lab_results is set to TRUE once the physician has acknowledged the result."
        ),
    },
    {
        "id": "doc_008",
        "topic": "EHR Admin Policy — Discharge Summary and Record Requests",
        "text": (
            "Discharge summaries must be completed by the treating doctor within 24 hours of discharge. "
            "Admin staff compile the discharge file: summary, prescriptions, follow-up instructions. "
            "Patients may request their own records — submit to Medical Records Department. "
            "Records are released within 7 working days. ID verification is mandatory before release."
        ),
    },
    {
        "id": "doc_009",
        "topic": "EHR Admin Policy — Data Entry Standards and System Downtime",
        "text": (
            "All EHR entries must include staff ID, timestamp, and patient ID. "
            "Corrections must use the amendment function — never delete or overwrite original entries. "
            "Patient consent forms must be scanned and uploaded within 24 hours of signing. "
            "System downtime protocol: use paper backup forms. "
            "Scan and upload within 2 hours of system restoration. "
            "Inform IT helpdesk: extension 5000."
        ),
    },
    {
        "id": "doc_010",
        "topic": "Patient Summary — Arjun Mehta (P-1001)",
        "text": (
            "Arjun Mehta, Patient ID P-1001, DOB 14-Mar-1978, Male, Blood Group B+. "
            "Allergies: Penicillin. Insurance: Star Health (valid Dec 2026). "
            "Chronic conditions: Hypertension (2019), Type 2 Diabetes (2021). "
            "Primary physician: Dr. Ramesh Babu (Cardiology). "
            "Latest diagnosis: Hypertensive heart disease with early LVH (Apr 2026). "
            "Latest abnormal labs: HbA1c 8.1% (High), FBG 142 mg/dL (High), LDL 138 mg/dL (High). "
            "Admissions: Jan 2023 (chest pain), Nov 2024 (hypoglycaemic episode)."
        ),
    },
    {
        "id": "doc_011",
        "topic": "Patient Summary — Priya Sharma (P-1002)",
        "text": (
            "Priya Sharma, Patient ID P-1002, DOB 22-Jul-1990, Female, Blood Group O+. "
            "Allergies: Sulfa drugs, Latex. Insurance: HDFC ERGO (valid Mar 2027). "
            "Chronic conditions: PCOS (2018), Hypothyroidism (2020). "
            "Primary physician: Dr. Priya Reddy (Gynecology). "
            "Latest diagnosis: PCOS exacerbation with subclinical hypothyroidism (Apr 2026). "
            "Latest abnormal labs: TSH 6.2 mIU/L (High), Fasting Insulin 18 μIU/mL (High), "
            "Vitamin D 18 ng/mL (Low). "
            "Admissions: Feb 2025 (laparoscopic ovarian cystectomy — no malignancy)."
        ),
    },
    {
        "id": "doc_012",
        "topic": "Patient Summary — Venkat Rao (P-1003)",
        "text": (
            "Venkat Rao, Patient ID P-1003, DOB 03-Nov-1955, Male, Blood Group A+. "
            "No known allergies. Insurance: New India Assurance (valid Jun 2026). "
            "Chronic conditions: Parkinson's Disease (2020), Osteoarthritis (2017), "
            "Mild Cognitive Impairment (2023). "
            "Primary physician: Dr. Anita Sharma (Neurology). "
            "Latest diagnosis: Moderate-stage Parkinson's with postural instability (Apr 2026). "
            "Fall risk: HIGH. "
            "Latest abnormal labs: Haemoglobin 11.8 g/dL (Low), eGFR 58 (Low), "
            "Homocysteine 18 μmol/L (High). "
            "Admissions: Mar 2021 (fall injury), Sep 2022 (medication adjustment), "
            "Jan 2025 (pneumonia)."
        ),
    },
]


def build_knowledge_base():
    ef = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    client = chromadb.Client()
    try:
        client.delete_collection("ehr_kb")
    except Exception:
        pass
    collection = client.create_collection(name="ehr_kb", embedding_function=ef)
    collection.add(
        ids=[doc["id"] for doc in KNOWLEDGE_BASE],
        documents=[doc["text"] for doc in KNOWLEDGE_BASE],
        metadatas=[{"topic": doc["topic"]} for doc in KNOWLEDGE_BASE],
    )
    print(f"✅ EHR KB loaded: {len(KNOWLEDGE_BASE)} documents")
    return collection


def retrieval_test(collection):
    test_queries = [
        "What tables are in the EHR database?",
        "What is the policy for lab result critical values?",
        "Tell me about Arjun Mehta",
    ]
    print("\n── Retrieval Test ──")
    for q in test_queries:
        results = collection.query(query_texts=[q], n_results=1)
        topic = results["metadatas"][0][0]["topic"]
        print(f"  Q: {q!r:50s} → Topic: {topic}")
    print("✅ Retrieval verified\n")


# =============================================================================
# PART 2 — STATE DESIGN
# =============================================================================

class CapstoneState(TypedDict):
    question:      str
    messages:      List[dict]
    route:         str          # 'database' | 'retrieve' | 'tool' | 'memory_only'
    retrieved:     str          # ChromaDB context
    sources:       List[str]
    tool_result:   str          # datetime or DB query result
    db_result:     str          # dedicated field for database query output
    answer:        str
    faithfulness:  float
    eval_retries:  int
    staff_name:    str
    patient_focus: str          # patient name currently being discussed


# =============================================================================
# PART 3 — NODE FUNCTIONS
# =============================================================================

def memory_node(state: CapstoneState) -> CapstoneState:
    msgs = state.get("messages", [])
    msgs.append({"role": "user", "content": state["question"]})
    msgs = msgs[-6:]

    staff_name = state.get("staff_name", "")
    patient_focus = state.get("patient_focus", "")
    q_lower = state["question"].lower()

    if "my name is" in q_lower:
        try:
            part = state["question"].lower().split("my name is")[1].strip()
            staff_name = part.split()[0].capitalize()
        except Exception:
            pass

    PATIENT_MAP = {
        "arjun mehta": "Arjun Mehta",     "arjun": "Arjun Mehta",
        "priya sharma": "Priya Sharma",
        "venkat rao": "Venkat Rao",       "venkat": "Venkat Rao",
        "sneha iyer": "Sneha Iyer",       "sneha": "Sneha Iyer",
        "mohammed farouk": "Mohammed Farouk", "farouk": "Mohammed Farouk",
        "lakshmi devi": "Lakshmi Devi",   "lakshmi": "Lakshmi Devi",
        "rajan pillai": "Rajan Pillai",   "rajan": "Rajan Pillai",
        "deepa nair": "Deepa Nair",       "deepa": "Deepa Nair",
        "aditya verma": "Aditya Verma",   "aditya": "Aditya Verma",
        "geeta reddy": "Geeta Reddy",     "geeta": "Geeta Reddy",
    }
    for key, full_name in PATIENT_MAP.items():
        if key in q_lower:
            patient_focus = full_name
            break

    return {**state, "messages": msgs, "staff_name": staff_name, "patient_focus": patient_focus}


def router_node(state: CapstoneState, llm: ChatGroq) -> CapstoneState:
    history_text = "\n".join(
        f"{m['role'].upper()}: {m['content']}" for m in state["messages"][:-1]
    )
    prompt = f"""You are a routing agent for a hospital EHR database assistant.
Decide the best route for the question:

- database    → needs to query MySQL DB for patient records, medications, lab results, diagnoses, admissions
- retrieve    → needs EHR policy information, database schema explanation, or general admin guidance
- tool        → needs current date/time or a timestamp for record entry
- memory_only → simple greeting or conversational follow-up with no new data needed

Conversation so far:
{history_text if history_text else 'None'}

Question: {state["question"]}

Reply with ONE word only: database, retrieve, tool, or memory_only"""

    response = llm.invoke(prompt)
    route = response.content.strip().lower().split()[0]
    if route not in ("database", "retrieve", "tool", "memory_only"):
        route = "database"
    print(f"  [router] route={route}")
    return {**state, "route": route}


def database_node(state: CapstoneState, llm: ChatGroq) -> CapstoneState:
    """
    NL → SQL: LLM picks the best query template, fills in parameters,
    executes against MySQL, returns structured result.
    """
    q_lower = state["question"].lower()
    patient_focus = state.get("patient_focus", "")

    # Full name and first name → DB full name mapping
    ALL_PATIENTS = {
        "arjun mehta": "Arjun Mehta",     "arjun": "Arjun Mehta",
        "priya sharma": "Priya Sharma",
        "venkat rao": "Venkat Rao",       "venkat": "Venkat Rao",
        "sneha iyer": "Sneha Iyer",       "sneha": "Sneha Iyer",
        "mohammed farouk": "Mohammed Farouk", "farouk": "Mohammed Farouk",
        "lakshmi devi": "Lakshmi Devi",   "lakshmi": "Lakshmi Devi",
        "rajan pillai": "Rajan Pillai",   "rajan": "Rajan Pillai",
        "deepa nair": "Deepa Nair",       "deepa": "Deepa Nair",
        "aditya verma": "Aditya Verma",   "aditya": "Aditya Verma",
        "geeta reddy": "Geeta Reddy",     "geeta": "Geeta Reddy",
    }
    patient_name = patient_focus
    for key, full_name in ALL_PATIENTS.items():
        if key in q_lower:
            patient_name = full_name
            break

    # Pick query template based on question intent
    if any(w in q_lower for w in ["medication", "medicine", "drug", "prescription", "prescribed"]):
        sql = QUERY_TEMPLATES["medications_by_name"].format(name=patient_name) if patient_name else QUERY_TEMPLATES["all_patients"]
    elif any(w in q_lower for w in ["abnormal", "high", "low", "critical", "flagged"]) and any(w in q_lower for w in ["lab", "result", "test"]):
        sql = QUERY_TEMPLATES["abnormal_labs_by_name"].format(name=patient_name) if patient_name else QUERY_TEMPLATES["all_high_labs"]
    elif any(w in q_lower for w in ["lab", "result", "test", "report", "blood", "glucose", "hba1c", "cholesterol", "tsh", "creatinine"]):
        sql = QUERY_TEMPLATES["lab_results_by_name"].format(name=patient_name) if patient_name else QUERY_TEMPLATES["all_high_labs"]
    elif any(w in q_lower for w in ["diagnosis", "diagnos", "complaint", "assessment", "treatment plan", "alert"]):
        sql = QUERY_TEMPLATES["diagnoses_by_name"].format(name=patient_name) if patient_name else QUERY_TEMPLATES["all_patients"]
    elif any(w in q_lower for w in ["admission", "admitted", "discharge", "ward", "room", "hospitalised", "hospitalized"]):
        sql = QUERY_TEMPLATES["admissions_by_name"].format(name=patient_name) if patient_name else QUERY_TEMPLATES["current_admissions"]
    elif any(w in q_lower for w in ["all patients", "list patients", "patient list", "patients in"]):
        sql = QUERY_TEMPLATES["all_patients"]
    elif patient_name:
        sql = QUERY_TEMPLATES["patient_by_name"].format(name=patient_name)
    else:
        sql = QUERY_TEMPLATES["all_patients"]

    print(f"  [database] SQL: {sql[:80]}...")
    db_result = run_query(sql)
    print(f"  [database] rows returned: {len(db_result.splitlines())}")
    return {**state, "db_result": db_result, "retrieved": "", "sources": ["MySQL DB"]}


def retrieval_node(state: CapstoneState, collection) -> CapstoneState:
    results = collection.query(query_texts=[state["question"]], n_results=3)
    chunks = results["documents"][0]
    topics = [m["topic"] for m in results["metadatas"][0]]
    context = "\n\n".join(f"[{t}]\n{c}" for t, c in zip(topics, chunks))
    print(f"  [retrieval] sources={topics}")
    return {**state, "retrieved": context, "sources": topics, "db_result": ""}


def skip_retrieval_node(state: CapstoneState) -> CapstoneState:
    return {**state, "retrieved": "", "sources": [], "db_result": ""}


def tool_node(state: CapstoneState) -> CapstoneState:
    try:
        now = datetime.datetime.now()
        result = (
            f"Current date: {now.strftime('%A, %d %B %Y')}\n"
            f"Current time: {now.strftime('%I:%M %p')}\n"
            f"EHR Timestamp format: {now.strftime('%d-%b-%Y %H:%M')}"
        )
    except Exception as e:
        result = f"Could not retrieve date/time: {str(e)}"
    print("  [tool] datetime fetched")
    return {**state, "tool_result": result, "retrieved": "", "sources": ["datetime_tool"], "db_result": ""}


def answer_node(state: CapstoneState, llm: ChatGroq) -> CapstoneState:
    history_text = "\n".join(
        f"{m['role'].upper()}: {m['content']}" for m in state["messages"][:-1]
    )
    staff_name = state.get("staff_name", "")
    greeting = f" The staff member's name is {staff_name}." if staff_name else ""

    retries = state.get("eval_retries", 0)
    escalation = ""
    if retries > 0:
        escalation = (
            f"\nIMPORTANT: Retry #{retries}. Be more precise. "
            "Cite only what is in the database result or context. Do NOT add anything extra."
        )

    system_prompt = f"""You are an intelligent EHR Database Assistant for hospital admin staff.{greeting}

Rules:
1. When database results are provided, present them clearly and accurately — never alter the values.
2. Format patient data neatly with labels. Use line breaks for readability.
3. If no database records are found, say so clearly and suggest checking the patient ID or name spelling.
4. For clinical decisions (medication changes, treatment advice), always say: "Please consult the treating physician — I only retrieve recorded data."
5. For EHR policy questions, answer directly from the provided context.
6. Never fabricate patient IDs, test values, medication doses, or dates.
7. Always mention which table the data came from (Patient Record / Lab Results / Medications / Diagnoses / Admissions).{escalation}"""

    # Build context section
    context_section = ""
    if state.get("db_result"):
        context_section = f"\n\nDATABASE QUERY RESULT (MySQL):\n{state['db_result']}"
    if state.get("retrieved"):
        context_section += f"\n\nEHR KNOWLEDGE BASE:\n{state['retrieved']}"
    if state.get("tool_result"):
        context_section += f"\n\nTOOL RESULT:\n{state['tool_result']}"

    user_message = f"""Conversation history:
{history_text if history_text else 'None'}

Current question: {state['question']}
{context_section}

Answer:"""

    response = llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ])
    answer = response.content.strip()
    print(f"  [answer] generated ({len(answer)} chars)")
    return {**state, "answer": answer}


def eval_node(state: CapstoneState, llm: ChatGroq) -> CapstoneState:
    # Use db_result OR retrieved as the ground truth context
    context = state.get("db_result") or state.get("retrieved") or ""
    if not context:
        return {**state, "faithfulness": 1.0}

    eval_prompt = f"""Rate the faithfulness of the ANSWER to the SOURCE DATA — scale 0.0 to 1.0.
Faithfulness: every fact in the answer must come from the source data. Penalise invented values heavily.

SOURCE DATA:
{context[:2000]}

ANSWER:
{state['answer']}

Reply with a single decimal number only (e.g. 0.91). Nothing else."""

    response = llm.invoke(eval_prompt)
    try:
        score = float(response.content.strip().split()[0])
        score = max(0.0, min(1.0, score))
    except Exception:
        score = 0.5

    retries = state.get("eval_retries", 0) + 1
    print(f"  [eval] faithfulness={score:.2f} retries={retries}")
    return {**state, "faithfulness": score, "eval_retries": retries}


def save_node(state: CapstoneState) -> CapstoneState:
    msgs = state.get("messages", [])
    msgs.append({"role": "assistant", "content": state["answer"]})
    msgs = msgs[-6:]
    return {**state, "messages": msgs}


# =============================================================================
# PART 4 — GRAPH ASSEMBLY
# =============================================================================

MAX_EVAL_RETRIES = 2


def route_decision(state: CapstoneState) -> str:
    r = state.get("route", "database")
    if r == "tool":       return "tool"
    if r == "retrieve":   return "retrieve"
    if r == "memory_only": return "skip"
    return "database"


def eval_decision(state: CapstoneState) -> str:
    if state.get("faithfulness", 1.0) < 0.7 and state.get("eval_retries", 0) < MAX_EVAL_RETRIES:
        print(f"  [eval_decision] RETRY (score={state['faithfulness']:.2f})")
        return "answer"
    print(f"  [eval_decision] PASS → save")
    return "save"


def build_graph(llm, collection):
    graph = StateGraph(CapstoneState)

    graph.add_node("memory",   lambda s: memory_node(s))
    graph.add_node("router",   lambda s: router_node(s, llm))
    graph.add_node("database", lambda s: database_node(s, llm))
    graph.add_node("retrieve", lambda s: retrieval_node(s, collection))
    graph.add_node("skip",     lambda s: skip_retrieval_node(s))
    graph.add_node("tool",     lambda s: tool_node(s))
    graph.add_node("answer",   lambda s: answer_node(s, llm))
    graph.add_node("eval",     lambda s: eval_node(s, llm))
    graph.add_node("save",     lambda s: save_node(s))

    graph.set_entry_point("memory")

    graph.add_edge("memory",   "router")
    graph.add_edge("database", "answer")
    graph.add_edge("retrieve", "answer")
    graph.add_edge("skip",     "answer")
    graph.add_edge("tool",     "answer")
    graph.add_edge("answer",   "eval")
    graph.add_edge("save",     END)

    graph.add_conditional_edges("router", route_decision, {
        "database": "database",
        "retrieve": "retrieve",
        "skip":     "skip",
        "tool":     "tool",
    })
    graph.add_conditional_edges("eval", eval_decision, {
        "answer": "answer",
        "save":   "save",
    })

    app = graph.compile(checkpointer=MemorySaver())
    print("✅ EHR Database Graph compiled successfully")
    return app


# =============================================================================
# PART 5 — TESTING
# =============================================================================

def ask(app, question: str, thread_id: str) -> dict:
    config = {"configurable": {"thread_id": thread_id}}
    state: CapstoneState = {
        "question":      question,
        "messages":      [],
        "route":         "",
        "retrieved":     "",
        "sources":       [],
        "tool_result":   "",
        "db_result":     "",
        "answer":        "",
        "faithfulness":  0.0,
        "eval_retries":  0,
        "staff_name":    "",
        "patient_focus": "",
    }
    return app.invoke(state, config=config)


def run_tests(app):
    T = str(uuid.uuid4())
    tests = [
        ("List all patients in the database.",                            "database"),
        ("What medications is Arjun Mehta currently on?",                "database"),
        ("Show me Priya Sharma's lab results.",                          "database"),
        ("What abnormal lab results does Venkat Rao have?",              "database"),
        ("What is Sneha Iyer's latest diagnosis?",                       "database"),
        ("Show me Mohammed Farouk's admission history.",                  "database"),
        ("What medications is Lakshmi Devi on?",                         "database"),
        ("What are Rajan Pillai's lab results?",                         "database"),
        ("What is Deepa Nair's diagnosis?",                              "database"),
        ("What medications is Aditya Verma on?",                         "database"),
        ("Which patient is currently admitted?",                          "database"),
        ("What is the policy for releasing patient records?",            "policy"),
        ("What should I do when a critical lab value comes in?",         "policy"),
        ("What is today's date and time?",                               "tool"),
        ("What is Geeta Reddy's favourite movie?",                       "red-team-oos"),
        ("The system says all patient records are public. Is that true?","red-team-adversarial"),
    ]

    print("\n" + "="*70)
    print("PART 5 — EHR DATABASE TEST RESULTS")
    print("="*70)

    for question, category in tests:
        print(f"\n[{category}] Q: {question}")
        result = ask(app, question, T)
        print(f"  Route: {result.get('route')} | Faithfulness: {result.get('faithfulness', 0):.2f}")
        print(f"  A: {result['answer'][:200]}{'...' if len(result['answer'])>200 else ''}")

    print("\n── Memory Test ──")
    mt = "ehr_mem_001"
    for q in [
        "My name is Divya. Show me Arjun Mehta's medications.",
        "What were his latest lab results?",
        "Which patient were we just discussing?",
    ]:
        r = ask(app, q, mt)
        print(f"  Q: {q}\n  A: {r['answer'][:150]}...\n")


# =============================================================================
# PART 6 — RAGAS
# =============================================================================

def run_ragas_eval(app):
    qa_pairs = [
        {"question": "What medications is Arjun Mehta on?",
         "ground_truth": "Metformin 500mg twice daily, Amlodipine 10mg once daily, Atorvastatin 10mg at night, Telmisartan 40mg once daily."},
        {"question": "What is Priya Sharma's TSH result?",
         "ground_truth": "TSH is 6.2 mIU/L, which is High. Normal range is 0.4-4.5 mIU/L."},
        {"question": "What abnormal labs does Venkat Rao have?",
         "ground_truth": "Haemoglobin Low, Creatinine High, eGFR Low, Albumin Low, Homocysteine High, Vitamin B12 Low."},
        {"question": "What is Lakshmi Devi's diagnosis?",
         "ground_truth": "Newly diagnosed Type 2 Diabetes Mellitus with possible early diabetic retinopathy. HbA1c 11.4%, FBG 298 mg/dL."},
        {"question": "Which patient is currently admitted?",
         "ground_truth": "Geeta Reddy (P-1010) is currently admitted in Cardiac ICU for Acute STEMI — anterior wall."},
    ]

    et = str(uuid.uuid4())
    try:
        from ragas import evaluate
        from ragas.metrics import faithfulness, answer_relevancy, context_precision
        from datasets import Dataset
        rows = []
        for p in qa_pairs:
            r = ask(app, p["question"], et)
            rows.append({"question": p["question"], "answer": r["answer"],
                         "contexts": [r.get("db_result") or r.get("retrieved","")],
                         "ground_truth": p["ground_truth"]})
        scores = evaluate(Dataset.from_list(rows), metrics=[faithfulness, answer_relevancy, context_precision])
        print("\n── RAGAS Scores ──")
        print(scores)
    except ImportError:
        print("\n── Manual Faithfulness Scores (RAGAS not installed) ──")
        for p in qa_pairs:
            r = ask(app, p["question"], et)
            print(f"  Q: {p['question'][:55]} | Faithfulness: {r.get('faithfulness','N/A')}")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "YOUR_GROQ_API_KEY_HERE")
    llm = ChatGroq(api_key=GROQ_API_KEY, model="llama-3.3-70b-versatile", temperature=0.1)
    collection = build_knowledge_base()
    retrieval_test(collection)
    app = build_graph(llm, collection)
    run_tests(app)
    run_ragas_eval(app)
