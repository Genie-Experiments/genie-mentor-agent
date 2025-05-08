# frontend/app.py
import streamlit as st, requests, uuid, json, os
from pathlib import Path
from datetime import datetime

# ╭─ Configuration ────────────────────────────────────────────────────────────╮
DB_FILE        = Path("db.json")
DEFAULT_BACKEND= os.getenv("BACKEND_URL", "http://127.0.0.1:8001")
# ╰────────────────────────────────────────────────────────────────────────────╯

# ── helper: talk to backend ────────────────────────────────────────────────
def call_backend(query: str) -> str:
    """POST /ask and return the model's reply text.  
       Also prints debug info to the terminal."""
    if not st.session_state.current_chat_id:
        return "❌ No active chat session"
        
    current_chat = st.session_state.chats[st.session_state.current_chat_id]
    params = {
        "query": query,
        "session_id": current_chat["session_id"],
    }

    body = {
        "history": [
            (h["content"] if h["role"] == "user"      else "",
             h["content"] if h["role"] == "assistant" else "")
            for h in current_chat["chat_history"]
        ]
    }

    print("\n───📨  REQUEST ─────────────────────────────────────")
    print("URL   :", f"{backend_url}/ask")
    print("PARAMS:", params)
    print("BODY  :", json.dumps(body, indent=2, ensure_ascii=False))

    r = requests.post(f"{backend_url}/onboarding/chat", params=params, json=body, timeout=190)

    print("───📩  RESPONSE ────────────────────────────────────")
    print("status:", r.status_code)
    print("headers:", r.headers.get("content-type"))
    print("text   :", r.text[:400] + ("…" if len(r.text) > 400 else ""))
    print("────────────────────────────────────────────────────\n")

    r.raise_for_status()

    if r.headers.get("content-type", "").startswith("application/json"):
        return r.json().get("response", r.text)
    return r.text

# ── session‑state bootstrap ───────────────────────────────────────────────────
if "chats" not in st.session_state:
    if DB_FILE.exists():
        try:
            data = json.loads(DB_FILE.read_text(encoding="utf-8"))
            # Migration: Convert old format to new format
            if isinstance(data, dict) and "chat_history" in data:
                # Old format detected, migrate to new format
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
                # Already in new format
                st.session_state.chats = data
        except json.JSONDecodeError:
            st.session_state.chats = {}
    else:
        st.session_state.chats = {}

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

if "editing_chat_id" not in st.session_state:
    st.session_state.editing_chat_id = None

# ── sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("⚙️  Settings")
backend_url = st.sidebar.text_input("FastAPI URL", value=DEFAULT_BACKEND)

# Chat management in sidebar
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

# Display existing chats
for chat_id, chat_data in st.session_state.chats.items():
    col1, col2, col3 = st.sidebar.columns([3, 1, 1])
    
    with col1:
        if st.session_state.editing_chat_id == chat_id:
            # Show text input for editing
            new_title = st.text_input(
                "Edit title",
                value=chat_data["title"],
                key=f"edit_{chat_id}",
                label_visibility="collapsed"
            )
            if new_title and new_title != chat_data["title"]:
                st.session_state.chats[chat_id]["title"] = new_title
                st.session_state.editing_chat_id = None
                # Save changes
                DB_FILE.write_text(
                    json.dumps(st.session_state.chats, indent=2, ensure_ascii=False),
                    encoding="utf-8"
                )
                st.rerun()
        else:
            # Show chat button
            if st.button(
                f"📝 {chat_data['title']}", 
                key=f"chat_{chat_id}",
                use_container_width=True
            ):
                st.session_state.current_chat_id = chat_id
                st.rerun()
    
    with col2:
        if st.button("✏️", key=f"edit_{chat_id}"):
            st.session_state.editing_chat_id = chat_id
            st.rerun()
    
    with col3:
        if st.button("🗑", key=f"delete_{chat_id}"):
            del st.session_state.chats[chat_id]
            if st.session_state.current_chat_id == chat_id:
                st.session_state.current_chat_id = next(iter(st.session_state.chats.keys())) if st.session_state.chats else None
            st.rerun()

st.sidebar.markdown("---")

# ── main chat interface ─────────────────────────────────────────────────────────
if not st.session_state.current_chat_id and st.session_state.chats:
    st.session_state.current_chat_id = next(iter(st.session_state.chats.keys()))

if st.session_state.current_chat_id:
    current_chat = st.session_state.chats[st.session_state.current_chat_id]
    st.title(f"💬 {current_chat['title']}")
    
    # Display chat history
    for m in current_chat["chat_history"]:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your question …"):
        # user bubble
        with st.chat_message("user"):
            st.markdown(prompt)
        current_chat["chat_history"].append({"role": "user", "content": prompt})

        # assistant bubble
        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                try:
                    answer = call_backend(prompt)
                except requests.HTTPError as e:
                    detail = e.response.text if e.response is not None else ""
                    answer = f"❌ *backend error* ({e.response.status_code}): {detail}"

            st.markdown(answer)
        current_chat["chat_history"].append({"role": "assistant", "content": answer})

        # persist changes
        DB_FILE.write_text(
            json.dumps(st.session_state.chats, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
else:
    st.info("👈 Create a new chat using the sidebar!")

