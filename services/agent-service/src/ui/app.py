# frontend/app.py
import streamlit as st, requests, uuid, json, os
from pathlib import Path
from datetime import datetime

# ╭ Configuration 
DB_FILE        = Path("db.json")
DEFAULT_BACKEND= os.getenv("BACKEND_URL", "http://127.0.0.1:8001")

# ── helper: talk to backend 
def call_backend(query: str) -> str:
    """POST /planner/plan and return both planner and query results"""
    if not st.session_state.current_chat_id:
        return "❌ No active chat session"

    current_chat = st.session_state.chats[st.session_state.current_chat_id]
    session_id = current_chat["session_id"]

    # Call planner endpoint which now returns both planner and query results
    response = requests.post(f"{DEFAULT_BACKEND}/planner/plan", params={"query": query}, timeout=190)
    response.raise_for_status()
    result = response.json()
    
    # Format the response - result is already parsed JSON
    planner_output = result["planner_output"]
    query_output = result["query_output"]
    
    return f"""**Planner Agent Output**
```json
{json.dumps(planner_output, indent=2)}
```

**Query Agent Output**
```json
{json.dumps(query_output, indent=2)}
```"""

# ── session‑state bootstrap 
if "chats" not in st.session_state:
    if DB_FILE.exists():
        try:
            data = json.loads(DB_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict) and "chat_history" in data:
                new_chat_id = str(uuid.uuid4())
                st.session_state.chats = {
                    new_chat_id: {
                        "session_id": str(uuid.uuid4()),
                        "chat_history": data["chat_history"],
                        "created_at": datetime.now().isoformat(),
                        "title": "Chat 1"
                    }
                }
            else:
                st.session_state.chats = data
        except json.JSONDecodeError:
            st.session_state.chats = {}
    else:
        st.session_state.chats = {}

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

if "editing_chat_id" not in st.session_state:
    st.session_state.editing_chat_id = None

# ── sidebar 
st.sidebar.title("⚙️  Settings")
backend_url = st.sidebar.text_input("FastAPI URL", value=DEFAULT_BACKEND)

st.sidebar.markdown("### 💬 Chats")
if st.sidebar.button("➕ New Chat"):
    new_chat_id = str(uuid.uuid4())
    st.session_state.chats[new_chat_id] = {
        "session_id": str(uuid.uuid4()),
        "chat_history": [],
        "created_at": datetime.now().isoformat(),
        "title": f"Chat {len(st.session_state.chats) + 1}"
    }
    st.session_state.current_chat_id = new_chat_id
    st.rerun()

for chat_id, chat_data in st.session_state.chats.items():
    col1, col2, col3 = st.sidebar.columns([3, 1, 1])
    with col1:
        if st.session_state.editing_chat_id == chat_id:
            new_title = st.text_input(
                "Edit title",
                value=chat_data["title"],
                key=f"edit_input_{chat_id}",
                label_visibility="collapsed"
            )
            if new_title and new_title != chat_data["title"]:
                st.session_state.chats[chat_id]["title"] = new_title
                st.session_state.editing_chat_id = None
                DB_FILE.write_text(
                    json.dumps(st.session_state.chats, indent=2, ensure_ascii=False),
                    encoding="utf-8"
                )
                st.rerun()
        else:
            if st.button(
                f"📝 {chat_data['title']}", 
                key=f"chat_{chat_id}",
                use_container_width=True
            ):
                st.session_state.current_chat_id = chat_id
                st.rerun()

    with col2:
        if st.button("✏️", key=f"edit_btn_{chat_id}"):
            st.session_state.editing_chat_id = chat_id
            st.rerun()

    with col3:
        if st.button("🗑", key=f"delete_{chat_id}"):
            del st.session_state.chats[chat_id]
            if st.session_state.current_chat_id == chat_id:
                st.session_state.current_chat_id = next(iter(st.session_state.chats.keys())) if st.session_state.chats else None
            st.rerun()

st.sidebar.markdown("---")

st.sidebar.markdown("### 📄 Upload document")
uploaded = st.sidebar.file_uploader("Choose PDF, TXT, or DOCX", type=["pdf", "txt", "docx"])
if uploaded and st.sidebar.button("Upload to agent"):
    with st.spinner("Uploading…"):
        res = requests.post(
            f"{backend_url}/upload/doc",
            files={"file": (uploaded.name, uploaded.getvalue())},
            timeout=60,
        )
    if res.ok:
        st.sidebar.success("Uploaded!")
    else:
        st.sidebar.error(f"Error: {res.text}")

# ── main chat interface 
if not st.session_state.current_chat_id and st.session_state.chats:
    st.session_state.current_chat_id = next(iter(st.session_state.chats.keys()))

if st.session_state.current_chat_id:
    current_chat = st.session_state.chats[st.session_state.current_chat_id]
    st.title(f"💬 {current_chat['title']}")

    for m in current_chat["chat_history"]:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if prompt := st.chat_input("Type your question …"):
        with st.chat_message("user"):
            st.markdown(prompt)
        current_chat["chat_history"].append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                try:
                    answer = call_backend(prompt)
                except requests.HTTPError as e:
                    detail = e.response.text if e.response is not None else ""
                    answer = f"❌ *backend error* ({e.response.status_code}): {detail}"

            st.markdown(answer)
        current_chat["chat_history"].append({"role": "assistant", "content": answer})

        DB_FILE.write_text(
            json.dumps(st.session_state.chats, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
else:
    st.info("👈 Create a new chat using the sidebar!")
