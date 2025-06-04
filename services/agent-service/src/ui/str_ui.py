import json
import os
import uuid
import time
from datetime import datetime
from pathlib import Path
import asyncio
import aiohttp
import streamlit as st
from typing import Dict, Any, Optional

# Configuration
DB_FILE = Path('db.json')
DEFAULT_BACKEND = os.getenv('BACKEND_URL', 'http://127.0.0.1:8001')

def format_timestamp(timestamp_str: str) -> str:
    """Format ISO timestamp string to a more readable format."""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime('%B %d, %Y at %I:%M:%S %p')
    except (ValueError, AttributeError):
        return timestamp_str

def create_agent_container(agent_name: str, icon: str) -> tuple:
    """Create a container for an agent's output with a collapsible section."""
    container = st.empty()
    with container.container():
        with st.expander(f"{icon} {agent_name}", expanded=True):
            content = st.empty()
    return container, content

async def stream_response(query: str, session_id: str) -> None:
    """Stream the response from the backend in real-time."""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f'{DEFAULT_BACKEND}/planner/plan',
            params={'query': query, 'session_id': session_id},
            timeout=190
        ) as response:
            if response.status != 200:
                st.error(f"Error: {await response.text()}")
                return

            # Create containers for each agent's output
            planner_container, planner_content = create_agent_container("Planner Agent", "🤖")
            refiner_container, refiner_content = create_agent_container("Refiner Agent", "🔄")
            query_container, query_content = create_agent_container("Query Agent", "🔍")
            evaluation_container, evaluation_content = create_agent_container("Evaluation Agent", "📊")

            # Stream the response
            async for chunk in response.content:
                try:
                    data = json.loads(chunk)
                    print("DEBUG: Received data:", json.dumps(data, indent=2))
                    
                    # Extract data from planner_output
                    if 'planner_output' in data:
                        plan_dict = data['planner_output']
                        
                        # Update planner output - show original plan
                        planner_content.markdown(f"""
                        **Original Plan:**
                        ```json
                        {json.dumps({
                            'user_query': plan_dict.get('user_query', ''),
                            'query_intent': plan_dict.get('query_intent', ''),
                            'data_sources': plan_dict.get('data_sources', []),
                            'query_components': plan_dict.get('query_components', []),
                            'execution_order': plan_dict.get('execution_order', {})
                        }, indent=2)}
                        ```
                        """)
                        
                        # Update refiner output - show refined plan and metadata
                        if 'refiner_metadata' in plan_dict:
                            refiner_data = plan_dict['refiner_metadata']
                            refiner_content.markdown(f"""
                            **Refined Plan:**
                            ```json
                            {json.dumps(json.loads(refiner_data.get('refined_plan', '{}')), indent=2)}
                            ```
                            
                            **Feedback:**
                            {refiner_data.get('feedback', 'No feedback provided')}
                            
                            **Changes Made:**
                            {chr(10).join(f"- {change}" for change in refiner_data.get('changes_made', ['No changes made']))}
                            """)
                        
                        # Update query output - show execution results
                        if 'query_results' in plan_dict:
                            query_data = plan_dict['query_results']
                            query_content.markdown(f"""
                            **Answer:**
                            {query_data.get('answer', '')}
                            
                            **Confidence Score:** {query_data.get('confidence_score', 'N/A')}%
                            """)
                        
                        # Update evaluation output - show evaluation data
                        if 'evaluation_results' in plan_dict:
                            eval_data = plan_dict['evaluation_results']
                            
                            # Format attempts history
                            attempts_text = ""
                            for attempt in eval_data.get('attempts', []):
                                attempts_text += f"""
                                **Attempt {len(attempts_text.split('Attempt'))}:**
                                - Answer: {attempt.get('answer', '')}
                                - Score: {attempt.get('score', 'N/A')}
                                - Delta: {attempt.get('delta', 'N/A')}
                                """
                            
                            evaluation_content.markdown(f"""
                            **Final Answer:**
                            {eval_data.get('final_answer', '')}
                            
                            **Evaluation Score:** {eval_data.get('evaluation_score', 0):.2f}
                            **Corrections Made:** {eval_data.get('corrections_made', 0)}
                            
                            **Attempts History:**
                            {attempts_text}
                            """)

                except json.JSONDecodeError as e:
                    print(f"DEBUG: JSON Decode Error: {e}")
                    continue
                except Exception as e:
                    print(f"DEBUG: Unexpected Error: {e}")
                    continue

def initialize_session_state():
    """Initialize session state variables."""
    if 'chats' not in st.session_state:
        if DB_FILE.exists():
            try:
                data = json.loads(DB_FILE.read_text(encoding='utf-8'))
                st.session_state.chats = {
                    chat_id: {
                        **chat_data,
                        'trace_history': []
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

def render_sidebar():
    """Render the sidebar with chat history and settings."""
    st.sidebar.title('⚙️ Settings')
    backend_url = st.sidebar.text_input('FastAPI URL', value=DEFAULT_BACKEND)

    st.sidebar.markdown('### 💬 Chats')
    if st.sidebar.button('➕ New Chat'):
        new_chat_id = str(uuid.uuid4())
        st.session_state.chats[new_chat_id] = {
            'session_id': str(uuid.uuid4()),
            'chat_history': [],
            'trace_history': [],
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

def main():
    """Main Streamlit app."""
    st.set_page_config(
        page_title="AI Chat Assistant",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better UI
    st.markdown("""
        <style>
        .stExpander {
            border: 1px solid #e0e0e0;
            border-radius: 5px;
            margin: 10px 0;
        }
        .stExpander:hover {
            border-color: #2196F3;
        }
        .css-1d391kg {
            padding: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    initialize_session_state()
    render_sidebar()

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
                asyncio.run(stream_response(prompt, current_chat['session_id']))

            # Save chat history
            DB_FILE.write_text(
                json.dumps(st.session_state.chats, indent=2, ensure_ascii=False),
                encoding='utf-8'
            )
    else:
        st.info('👈 Create a new chat using the sidebar!')

if __name__ == '__main__':
    main()