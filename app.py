import streamlit as st
import pandas as pd
from rag_core import process_multiple_pdfs, answer_question
from mongo_utils import delete_documents_by_source, get_distinct_sources, count_documents


st.set_page_config(
    page_title="🚀 IAcine HR Power Tool – CV RAG Analyzer",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.title("🚀 IAcine HR Power Tool – CV RAG Analyzer")


st.sidebar.header("📂 CV Library Management")

sources = get_distinct_sources()
if sources:
    to_delete = st.sidebar.selectbox("🗑️ Delete a CV", sources)
    if st.sidebar.button("Delete CV"):
        deleted = delete_documents_by_source(to_delete)
        st.sidebar.success(f"✅ Removed {deleted} chunks from {to_delete}")
else:
    st.sidebar.info("ℹ️ No CVs indexed yet.")

st.sidebar.markdown(f"**💾 Total indexed chunks:** `{count_documents()}`")

uploaded = st.sidebar.file_uploader(
    "📄 Upload one CV (PDF)",
    type="pdf",
    accept_multiple_files=False,
    key="cv_uploader"
)
if uploaded:
    with st.spinner("🔍 Indexing CV…"):
        n = process_multiple_pdfs([uploaded])
    st.sidebar.success(f"✅ Indexed {n} chunks from the CV")


active_cv = None
if sources:
    active_cv = st.sidebar.selectbox("🎯 Select CV to analyze", sources)
    st.sidebar.info(f"Analyzing: **{active_cv}**")
else:
    st.sidebar.info("Upload and index a CV to begin")


fields = {
    "Name":           "What is the candidate’s name?",
    "Title":          "What is the candidate’s current title?",
    "Certifications": "Which certifications does the candidate hold?",
    "Passion":        "Provide the candidate’s personal summary/passion statement.",
    "Education":      "What is the candidate’s academic background?",
    "Experience":     "What professional experiences does the candidate have?",
    "Skills & Tools": "List key skills and tools mentioned.",
    "Languages":      "Which languages does the candidate speak?",
    "Contact":        "How can we contact the candidate?",
    "Location":       "Where is the candidate based?"
}

for key in fields:
    if key not in st.session_state:
        st.session_state[key] = ""

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []




def generate_full_profile():
    if not active_cv:
        st.warning("Please select a CV first.")
        return

    for label, question in fields.items():
        if label == "Experience":
            prompt = "Please answer concisely and list *all* professional experiences mentioned in the CV."
            ans = answer_question(prompt, k=10)
        else:
            prompt = f"Please answer concisely: {question}"
            ans = answer_question(prompt)

        if "Aucun contenu pertinent" in ans or "not specified" in ans:
            ans = "❌ Not specified in the CV."

        st.session_state[label] = ans




col_profile, col_chat = st.columns([2, 1])

with col_profile:
    st.header("🎯 Candidate Profile Snapshot")
    st.button("🤖 Generate Full Profile", on_click=generate_full_profile)
    data = {label: st.session_state[label] or "–" for label in fields}
    df = pd.DataFrame.from_dict(data, orient="index", columns=["Value"])
    st.table(df)

with col_chat:
    st.header("💬 Freeform RAG Chat")
    for role, msg in st.session_state["chat_history"]:
        st.chat_message(role).write(msg)

    user_input = st.chat_input("Ask anything about the CV…")
    if user_input:
        st.chat_message("user").write(user_input)
        with st.spinner("🔍 Searching & Generating…"):
            reply = answer_question(f"Please answer concisely: {user_input}")
            if "Aucun contenu pertinent" in reply or "not specified" in reply:
                reply = "❌ Not specified in the CV."
        st.chat_message("assistant").write(reply)
        st.session_state["chat_history"].append(("user", user_input))
        st.session_state["chat_history"].append(("assistant", reply))
