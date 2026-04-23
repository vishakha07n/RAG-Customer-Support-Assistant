import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
import tempfile 
import streamlit as st

from app.main import SupportAssistant
from app.config import settings
from app.utils.helpers import generate_session_id
from app.hitl.reviewer import ReviewerSimulator

# ----------------- SESSION STATE INIT -----------------
if "session_id" not in st.session_state:
    st.session_state.session_id = generate_session_id()

if "assistant" not in st.session_state:
    st.session_state.assistant = SupportAssistant(st.session_state.session_id)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "uploaded_files_hashes" not in st.session_state:
    st.session_state.uploaded_files_hashes = set()

if "escalation_ticket" not in st.session_state:
    st.session_state.escalation_ticket = None

# ----------------- UI LAYOUT -----------------
st.set_page_config(page_title="RAG Support Assistant", layout="wide")
st.title("🤖 RAG Customer Support Assistant")
st.caption(f"Session ID: {st.session_state.session_id}")

# Sidebar for PDF Upload & HITL Review
with st.sidebar:
    st.header("1. Upload Documents")
    uploaded_files = st.file_uploader("Upload PDFs", type=["pdf"], accept_multiple_files=True)
    
    if st.button("Process PDFs"):
        if uploaded_files:
            with st.spinner("Processing documents..."):
                temp_paths = []
                for file in uploaded_files:
                    # Save uploaded file to temp dir
                    fd, path = tempfile.mkstemp(suffix=".pdf")
                    with os.fdopen(fd, 'wb') as f:
                        f.write(file.getvalue())
                    temp_paths.append(path)
                
                # Ingest & Store
                st.session_state.assistant.process_pdfs(temp_paths)
                
                # Cleanup temp files
                for path in temp_paths:
                    os.remove(path)
                    
            st.success("Documents processed & indexed in ChromaDB successfully!")
        else:
            st.warning("Please upload files first.")
            
    st.divider()
    if st.button("Clear Session Data"):
        st.session_state.assistant.reset_session()
        st.session_state.chat_history = []
        st.session_state.escalation_ticket = None
        st.rerun()

    st.divider()
    st.header("Human-In-The-Loop (HITL)")
    if st.session_state.escalation_ticket:
        st.warning("Ticket pending review!")
        st.json(st.session_state.escalation_ticket)
        
        decision = st.radio("Reviewer Decision:", ["approve", "reject", "custom_reply"])
        custom_reply = ""
        if decision == "custom_reply":
            custom_reply = st.text_input("Custom Response:")
            
        if st.button("Submit Decision"):
            reviewer = ReviewerSimulator()
            reply = reviewer.process_decision(decision, custom_reply)
            
            # Add to chat history
            st.session_state.chat_history.append({"role": "agent", "content": f"**[Human Agent]** {reply}"})
            st.session_state.escalation_ticket = None # Clear ticket
            st.rerun()
    else:
        st.info("No pending escalations.")

# Main Chat Area
st.header("✨Chat")

# Display chat history
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "sources" in msg and msg["sources"]:
            with st.expander("Sources"):
                for src in msg["sources"]:
                    st.write(f"- {src['source']} (Page {src['page']})")

# Chat input
if query := st.chat_input("Ask a question based on the uploaded PDFs..."):
    if st.session_state.escalation_ticket:
        st.warning("Please wait for the human agent to review the pending ticket.")
    else:
        # Display user msg
        with st.chat_message("user"):
            st.markdown(query)
        st.session_state.chat_history.append({"role": "user", "content": query})

        # Process via LangGraph
        with st.spinner("Analyzing and thinking..."):
            final_state = st.session_state.assistant.ask(query)
            
            response = final_state["final_response"]
            sources = final_state.get("sources", [])
            route = final_state.get("route", "Unknown")
            
            # Display assistant msg
            with st.chat_message("assistant"):
                st.markdown(f"**[{route.upper()}]** {response}")
                if sources and route == "answer":
                    with st.expander("Sources"):
                        for src in sources:
                            st.write(f"- {src['source']} (Page {src['page']})")
            
            # Check for escalation
            if final_state.get("escalation_required"):
                st.session_state.escalation_ticket = final_state["escalation_ticket"]
                st.toast("Query escalated to human reviewer!", icon="🚨")
            
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"**[{route.upper()}]** {response}",
                "sources": sources if route == "answer" else []
            })
            
            if final_state.get("escalation_required"):
                st.rerun()
