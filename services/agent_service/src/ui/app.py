import os
import json
import requests
import streamlit as st
from typing import Any, Dict, List

###############################################################################
# Configuration
###############################################################################
DEFAULT_BACKEND = "http://127.0.0.1:8000"

###############################################################################
# Helpers
###############################################################################

def call_backend(query: str, session_id: str) -> Dict[str, Any]:
    """Send the user query to the backend and return its JSON payload."""
    endpoint = f"{DEFAULT_BACKEND}/1/agent_service"
    

    try:
        resp = requests.post(
            endpoint,
            params={"query": query, "session_id": session_id},
            timeout=190,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:
        st.error(f"❌ Backend request failed — {exc}")
        return {}


def render_query_components(components: List[Dict[str, Any]]):
    """Pretty-print planner sub-queries in a compact table."""
    if not components:
        st.info("Planner did not return any query components.")
        return

    # Build a small markdown table manually for clarity
    header = "| Sub-Query ID   |      Sub-Query        |     Source |\n|---|---|---|"
    rows = [f"| {c['id']}      |    {c['sub_query']}   |        {c['source']}      |" for c in components]
    st.markdown("\n".join([header, *rows]))


def render_metadata_by_source(metadata_map: Dict[str, List[Dict[str, Any]]]):
    """Show per-source metadata; keys differ per source, so render dynamically."""
    if not metadata_map:
        st.write("No metadata available.")
        return

    for source, entries in metadata_map.items():
        st.subheader(f"📄 Metadata — {source}")
        for idx, meta in enumerate(entries, 1):
            with st.expander(f"Item {idx}"):
                pretty_json = json.dumps(meta, indent=2, ensure_ascii=False)
                st.code(pretty_json, language="json")


def render_evaluation_history(evals: List[Dict[str, Any]]):
    if not evals:
        st.write("Evaluation stage skipped or returned no data.")
        return

    for e in evals:
        attempt_no = e.get("attempt")
        hist = e.get("evaluation_history", {})
        with st.expander(f"Evaluation Attempt {attempt_no}"):
            st.markdown(f"**Score:** {hist.get('score', 'N/A')}")
            reasoning = hist.get("reasoning", "")
            if reasoning:
                st.markdown("**Reasoning:**")
                st.code(reasoning, language="json")
            if hist.get("error"):
                st.error(hist["error"])


def render_editor_history(edits: List[Dict[str, Any]]):
    if not edits:
        st.write("Editor stage skipped or returned no data.")
        return

    for e in edits:
        attempt_no = e.get("attempt")
        hist = e.get("editor_history", {})
        with st.expander(f"Editor Attempt {attempt_no}"):
            st.markdown("**Revised Answer:**")
            st.write(hist.get("answer", ""))
            if hist.get("error"):
                st.error(hist["error"])

###############################################################################
# Streamlit UI
###############################################################################

st.set_page_config(
    page_title="Genie Mentor Agent Flow Inspector",
    page_icon="🧞",
    layout="centered",
)

st.title("🧞 Genie Mentor Agent Flow Inspector")

st.markdown(
    """Ask a question and explore how each agent (Planner, Refiner, Executor,\
    Evaluator, Editor) processed your user query under the hood."""
)

###############################################################################
# User Input
###############################################################################

with st.form(key="user_query_form"):
    user_query = st.text_input("📨 Your question", placeholder="e.g. How does RLHF work?")
    session_id = st.text_input("🆔 Session ID", value="123")
    submit_btn = st.form_submit_button("Run")

if submit_btn and user_query.strip():
    with st.spinner("Our Agents are working to get you best Answer to your Query..."):
        response = call_backend(user_query, session_id)

    if not response:
        st.stop()

    trace = response.get("trace_info", {})

    ############################################################################
    # Planner Section
    ############################################################################
    planner = trace.get("planner_agent", {})
    plan = planner.get("plan", {})

    st.header("🗺️ Let's see what Planner planned")

    # Sub-queries table
    render_query_components(plan.get("query_components", []))

    st.markdown(
        f"**Aggregation Strategy:** {plan.get('execution_order', {}).get('aggregation', 'N/A')}  \n\n"
        f"**Query Intent:** {plan.get('query_intent', 'N/A')}"
    )


    # Thinking process dropdown
    with st.expander("💭 Show Planner's thinking process"):
        pretty_think = json.dumps(plan.get("think", {}), indent=2, ensure_ascii=False)
        st.code(pretty_think, language="json")

    ############################################################################
    # Planner Refiner Section
    ############################################################################
    refiner = trace.get("planner_refiner_agent", {})
    if refiner:
        st.header("🛠️ Did Planner Pass Refiner Agent Test?")
        with st.expander("🔍 View refiner details"):
            st.markdown(f"**Refinement Required:** {refiner.get('refinement_required', 'N/A')}")
            st.markdown(f"**Feedback Summary:** {refiner.get('feedback_summary', 'N/A')}")
            reasoning = refiner.get("feedback_reasoning", [])
            if reasoning:
                st.markdown("**Feedback Reasoning:**")
                for line in reasoning:
                    st.write(f"- {line}")
            if refiner.get("error"):
                st.error(refiner["error"])

    ############################################################################
    # Executor Section
    ############################################################################
    executor = trace.get("executor_agent", {})
    st.header("🚀 Executor Executed Sub-Queries!")

    # Combined answer
    st.subheader("Source Agents Worked Together To Produce this Answer")
    st.write(executor.get("combined_answer_of_sources", "No answer returned."))

    # Per-source metadata
    metadata_map = executor.get("metadata_by_source", {})
    render_metadata_by_source(metadata_map)

    ############################################################################
    # Evaluation Section
    ############################################################################
    st.header("📊 How Evaluator Agent Evaluated Cooked Answer")
    render_evaluation_history(trace.get("evaluation_agent", []))

    ############################################################################
    # Editor Section
    ############################################################################
    st.header("✍️ Editor Edited for You!")
    render_editor_history(trace.get("editor_agent", []))

    ############################################################################
    # Final Answer
    ############################################################################
    st.header("🏁 Here is Your Answer")
    st.success(trace.get("final_answer", "No final answer provided."))

    ############################################################################
    # Runtime / Misc
    ############################################################################
    st.caption(f"Total time taken by our Agents: {trace.get('total_time', 'N/A')} seconds")
