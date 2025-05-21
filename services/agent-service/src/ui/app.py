# frontend/app.py
# Standard library imports
import json
import os
import uuid
import time
from datetime import datetime
from pathlib import Path

# Third-party imports
import requests
import streamlit as st

# ╭ Configuration 
DB_FILE        = Path('db.json')
DEFAULT_BACKEND= os.getenv('BACKEND_URL', 'http://127.0.0.1:8001')

def format_timestamp(timestamp_str: str) -> str:
    """Format ISO timestamp string to a more readable format."""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime('%B %d, %Y at %I:%M:%S %p')
    except (ValueError, AttributeError):
        return timestamp_str

def format_trace_info(trace_info: dict) -> dict:
    """Format timestamps in trace information to be more readable."""
    formatted_trace = trace_info.copy()
    
    # Format main timestamp
    if 'timestamp' in formatted_trace:
        formatted_trace['timestamp'] = format_timestamp(formatted_trace['timestamp'])
    
    # Format user input timestamp
    if 'user_input' in formatted_trace and 'time' in formatted_trace['user_input']:
        formatted_trace['user_input']['time'] = format_timestamp(formatted_trace['user_input']['time'])
    
    # Format planner agent timestamps
    if 'planner_agent' in formatted_trace:
        if 'timestamp' in formatted_trace['planner_agent']:
            formatted_trace['planner_agent']['timestamp'] = format_timestamp(formatted_trace['planner_agent']['timestamp'])
    
    # Format query agent timestamps
    if 'query_agent' in formatted_trace:
        if 'timestamp' in formatted_trace['query_agent']:
            formatted_trace['query_agent']['timestamp'] = format_timestamp(formatted_trace['query_agent']['timestamp'])
    
    return formatted_trace

# ── helper: talk to backend 
def call_backend(query: str) -> str:
    """POST /planner/plan and return both planner and query results"""
    if not st.session_state.current_chat_id:
        return '❌ No active chat session'

    current_chat = st.session_state.chats[st.session_state.current_chat_id]
    session_id = current_chat['session_id']

    # Start timing the request
    start_time = time.time()
    
    # Call planner endpoint which now returns both planner and query results
    response = requests.post(
        f'{DEFAULT_BACKEND}/planner/plan',
        params={
            'query': query,
            'session_id': session_id
        },
        timeout=190
    )
    response.raise_for_status()
    result = response.json()
    
    # Calculate total time taken
    total_time = time.time() - start_time
    
    # Format the response - result is already parsed JSON
    planner_output = result['planner_output']
    query_output = result['query_output']
    trace_info = result.get('trace_info', {})
    
    # Initialize trace_history if it doesn't exist
    if 'trace_history' not in current_chat:
        current_chat['trace_history'] = []
    
    # Add trace block to chat history
    current_chat['trace_history'].append(trace_info)
    
    # Save updated chat history
    DB_FILE.write_text(
        json.dumps(st.session_state.chats, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )
    
    # Format the response with planner output as JSON and query output as chat
    try:
        if isinstance(query_output, str):
            # If query_output is a string, try to parse it as JSON
            query_output = json.loads(query_output)
        
        # Extract the actual response and confidence score from the query output
        if isinstance(query_output, dict):
            if 'aggregated_results' in query_output:
                query_response = query_output['aggregated_results']
                confidence_score = query_output.get('confidence_score', 'N/A')
            elif 'answer' in query_output:
                query_response = query_output['answer']
                confidence_score = query_output.get('confidence_score', 'N/A')
            else:
                query_response = str(query_output)
                confidence_score = 'N/A'
        else:
            query_response = str(query_output)
            confidence_score = 'N/A'
    except json.JSONDecodeError:
        # If parsing fails, return the raw output
        query_response = str(query_output)
        confidence_score = 'N/A'
    
    return f'''**Planner Agent Output**
```json
{json.dumps(planner_output, indent=2)}
```

**Query Agent Response**
{query_response}

**Confidence Score**: {confidence_score}'''

# ── session‑state bootstrap 
if 'chats' not in st.session_state:
    if DB_FILE.exists():
        try:
            data = json.loads(DB_FILE.read_text(encoding='utf-8'))
            if isinstance(data, dict) and 'chat_history' in data:
                new_chat_id = str(uuid.uuid4())
                st.session_state.chats = {
                    new_chat_id: {
                        'session_id': str(uuid.uuid4()),
                        'chat_history': data['chat_history'],
                        'trace_history': [],  # Initialize trace_history
                        'created_at': datetime.now().isoformat(),
                        'title': 'Chat 1'
                    }
                }
            else:
                # Convert existing chats to include trace_history
                st.session_state.chats = {
                    chat_id: {
                        **chat_data,
                        'trace_history': []  # Add trace_history to existing chats
                    }
                    for chat_id, chat_data in data.items()
                }
        except json.JSONDecodeError:
            st.session_state.chats = {}
    else:
        st.session_state.chats = {}

if 'current_chat_id' not in st.session_state:
    st.session_state.current_chat_id = None

if 'editing_chat_id' not in st.session_state:
    st.session_state.editing_chat_id = None

# ── sidebar 
st.sidebar.title('⚙️  Settings')
backend_url = st.sidebar.text_input('FastAPI URL', value=DEFAULT_BACKEND)

st.sidebar.markdown('### 💬 Chats')
if st.sidebar.button('➕ New Chat'):
    new_chat_id = str(uuid.uuid4())
    st.session_state.chats[new_chat_id] = {
        'session_id': str(uuid.uuid4()),
        'chat_history': [],
        'trace_history': [],  # Initialize trace_history
        'created_at': datetime.now().isoformat(),
        'title': f'Chat {len(st.session_state.chats) + 1}'
    }
    st.session_state.current_chat_id = new_chat_id
    st.rerun()

for chat_id, chat_data in st.session_state.chats.items():
    col1, col2, col3 = st.sidebar.columns([3, 1, 1])
    with col1:
        if st.session_state.editing_chat_id == chat_id:
            new_title = st.text_input(
                'Edit title',
                value=chat_data['title'],
                key=f'edit_input_{chat_id}',
                label_visibility='collapsed'
            )
            if new_title and new_title != chat_data['title']:
                st.session_state.chats[chat_id]['title'] = new_title
                st.session_state.editing_chat_id = None
                DB_FILE.write_text(
                    json.dumps(st.session_state.chats, indent=2, ensure_ascii=False),
                    encoding='utf-8'
                )
                st.rerun()
        else:
            if st.button(
                f'📝 {chat_data["title"]}', 
                key=f'chat_{chat_id}',
                use_container_width=True
            ):
                st.session_state.current_chat_id = chat_id
                st.rerun()

    with col2:
        if st.button('✏️', key=f'edit_btn_{chat_id}'):
            st.session_state.editing_chat_id = chat_id
            st.rerun()

    with col3:
        if st.button('🗑', key=f'delete_{chat_id}'):
            del st.session_state.chats[chat_id]
            if st.session_state.current_chat_id == chat_id:
                st.session_state.current_chat_id = next(iter(st.session_state.chats.keys())) if st.session_state.chats else None
            st.rerun()

st.sidebar.markdown('---')

st.sidebar.markdown('### 📄 Upload document')
uploaded = st.sidebar.file_uploader('Choose PDF, TXT, or DOCX', type=['pdf', 'txt', 'docx'])
if uploaded and st.sidebar.button('Upload to agent'):
    with st.spinner('Uploading…'):
        res = requests.post(
            f'{backend_url}/upload/doc',
            files={'file': (uploaded.name, uploaded.getvalue())},
            timeout=60,
        )
    if res.ok:
        st.sidebar.success('Uploaded!')
    else:
        st.sidebar.error(f'Error: {res.text}')

# ── main chat interface 
if not st.session_state.current_chat_id and st.session_state.chats:
    st.session_state.current_chat_id = next(iter(st.session_state.chats.keys()))

if st.session_state.current_chat_id:
    current_chat = st.session_state.chats[st.session_state.current_chat_id]
    st.title(f'💬 {current_chat["title"]}')

    # Display chat history
    for m in current_chat['chat_history']:
        with st.chat_message(m['role']):
            st.markdown(m['content'])

    if prompt := st.chat_input('Type your question …'):
        with st.chat_message('user'):
            st.markdown(prompt)
        current_chat['chat_history'].append({'role': 'user', 'content': prompt})

        with st.chat_message('assistant'):
            with st.spinner('Thinking…'):
                try:
                    answer = call_backend(prompt)
                    # Get the trace info from the response
                    response = requests.post(
                        f'{DEFAULT_BACKEND}/planner/plan',
                        params={
                            'query': prompt,
                            'session_id': current_chat['session_id']
                        },
                        timeout=190
                    ).json()
                    trace_info = response.get('trace_info', {})
                    # Format the trace information
                    formatted_trace = format_trace_info(trace_info)
                except requests.HTTPError as e:
                    detail = e.response.text if e.response is not None else ''
                    answer = f'❌ *backend error* ({e.response.status_code}): {detail}'
                    formatted_trace = {}

            st.markdown(answer)
            # Add trace information in an expander
            with st.expander("🔍 Trace Information"):
                st.json(formatted_trace)
                
        current_chat['chat_history'].append({'role': 'assistant', 'content': answer})

        DB_FILE.write_text(
            json.dumps(st.session_state.chats, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
else:
    st.info('👈 Create a new chat using the sidebar!')
