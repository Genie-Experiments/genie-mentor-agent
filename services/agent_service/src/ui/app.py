import json
import os
from typing import Any, Dict, List

import requests
import streamlit as st

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
    rows = [
        f"| {c['id']}      |    {c['sub_query']}   |        {c['source']}      |"
        for c in components
    ]
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
    user_query = st.text_input(
        "📨 Your question", placeholder="e.g. How does RLHF work?"
    )
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

    # Get all plan versions
    plan_versions = []
    if isinstance(planner, list):
        plan_versions = planner
    else:
        plan_versions = [planner]

    st.header("🗺️ Let's see what Planner planned")

    # Show original and refined plans in dropdowns
    for idx, version in enumerate(plan_versions, 1):
        version_plan = version.get("plan", {})
        if idx == 1:
            with st.expander("📋 Original Plan"):
                st.markdown("**Query Components:**")
                render_query_components(version_plan.get("query_components", []))
                st.markdown(
                    f"**Aggregation Strategy:** {version_plan.get('execution_order', {}).get('aggregation', 'N/A')}  \n\n"
                    f"**Query Intent:** {version_plan.get('query_intent', 'N/A')}"
                )
                st.markdown("**Thinking Process:**")
                think = version_plan.get("think", {})
                st.markdown(f"**Query Analysis:** {think.get('query_analysis', 'N/A')}")
                st.markdown(
                    f"**Sub-Query Reasoning:** {think.get('sub_query_reasoning', 'N/A')}"
                )
                st.markdown(
                    f"**Source Selection:** {think.get('source_selection', 'N/A')}"
                )
                st.markdown(
                    f"**Execution Strategy:** {think.get('execution_strategy', 'N/A')}"
                )
        else:
            with st.expander(f"📋 Refined Plan {idx-1}"):
                st.markdown("**Query Components:**")
                render_query_components(version_plan.get("query_components", []))
                st.markdown(
                    f"**Aggregation Strategy:** {version_plan.get('execution_order', {}).get('aggregation', 'N/A')}  \n\n"
                    f"**Query Intent:** {version_plan.get('query_intent', 'N/A')}"
                )
                st.markdown("**Thinking Process:**")
                think = version_plan.get("think", {})
                st.markdown(f"**Query Analysis:** {think.get('query_analysis', 'N/A')}")
                st.markdown(
                    f"**Sub-Query Reasoning:** {think.get('sub_query_reasoning', 'N/A')}"
                )
                st.markdown(
                    f"**Source Selection:** {think.get('source_selection', 'N/A')}"
                )
                st.markdown(
                    f"**Execution Strategy:** {think.get('execution_strategy', 'N/A')}"
                )

    # Show final plan (current display)
    st.subheader("📊 Final Plan")
    # Get the last plan version for the final display
    final_plan = plan_versions[-1].get("plan", {}) if plan_versions else {}

    # Sub-queries table
    render_query_components(final_plan.get("query_components", []))

    st.markdown(
        f"**Aggregation Strategy:** {final_plan.get('execution_order', {}).get('aggregation', 'N/A')}  \n\n"
        f"**Query Intent:** {final_plan.get('query_intent', 'N/A')}"
    )

    # Thinking process dropdown
    with st.expander("💭 Show Planner's thinking process"):
        think = final_plan.get("think", {})
        st.markdown("**Thinking Process:**")
        st.markdown(f"**Query Analysis:** {think.get('query_analysis', 'N/A')}")
        st.markdown(
            f"**Sub-Query Reasoning:** {think.get('sub_query_reasoning', 'N/A')}"
        )
        st.markdown(f"**Source Selection:** {think.get('source_selection', 'N/A')}")
        st.markdown(f"**Execution Strategy:** {think.get('execution_strategy', 'N/A')}")

    ############################################################################
    # Planner Refiner Section
    ############################################################################
    refiner = trace.get("planner_refiner_agent", {})
    if refiner:
        st.header("🛠️ Did Planner Pass Refiner Agent Test?")

        # Get all refinement attempts
        refinement_attempts = []
        if isinstance(refiner, list):
            refinement_attempts = refiner
        else:
            refinement_attempts = [refiner]

        for idx, attempt in enumerate(refinement_attempts, 1):
            with st.expander(f"🔍 Refinement Attempt {idx}"):
                st.markdown(
                    f"**Refinement Required:** {attempt.get('refinement_required', 'N/A')}"
                )
                st.markdown(
                    f"**Feedback Summary:** {attempt.get('feedback_summary', 'N/A')}"
                )

                # Handle feedback_reasoning whether it's a string or list
                reasoning = attempt.get("feedback_reasoning", [])
                if isinstance(reasoning, str):
                    reasoning = [reasoning]

                if reasoning:
                    st.markdown("**Feedback Reasoning:**")
                    for line in reasoning:
                        st.write(f"- {line}")

                if not reasoning:  # Explicitly check if reasoning is empty
                    st.info("No feedback reasoning provided")

                if attempt.get("error"):
                    st.error(attempt["error"])

                # Show execution time if available
                if "execution_time_ms" in attempt:
                    st.caption(f"Execution time: {attempt['execution_time_ms']}ms")

    ############################################################################
    # Executor Section
    ############################################################################
    executor = trace.get("executor_agent", {})
    st.header("🚀 Executor Executed Sub-Queries!")

    # Combined answer
    st.subheader("Source Agents Worked Together To Produce this Answer")
    st.write(executor.get("executor_answer", "No answer returned."))

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
    st.caption(
        f"Total time taken by our Agents: {trace.get('total_time', 'N/A')} seconds"
    )
