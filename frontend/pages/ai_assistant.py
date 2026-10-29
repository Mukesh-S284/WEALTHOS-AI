"""Grounded Financial AI Assistant page."""

import streamlit as st
from frontend.components.ui import page_header


def render_ai_assistant():
    client = st.session_state.api_client
    token = st.session_state.token

    page_header(
        title="Grounded Financial AI Assistant",
        subtitle="Ask questions about your budget, test affordability, or research investment strategies with verifiable tool execution."
    )

    if "assistant_session_id" not in st.session_state:
        st.session_state.assistant_session_id = None

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    # Sidebar / Top controls for sessions
    col_sess, col_new = st.columns([3, 1])
    with col_sess:
        try:
            sessions = client.list_assistant_sessions(token)
            sess_opts = {s["id"]: f"{s['title'][:40]} ({s['created_at'][:10]})" for s in sessions}
            if sess_opts:
                cur_id = st.session_state.assistant_session_id or list(sess_opts.keys())[0]
                sel = st.selectbox("Conversation History", options=list(sess_opts.keys()), format_func=lambda x: sess_opts[x], index=0)
                if sel != st.session_state.assistant_session_id:
                    st.session_state.assistant_session_id = sel
                    st.session_state.chat_messages = []
        except Exception:
            pass

    with col_new:
        if st.button("➕ New Chat Session", use_container_width=True):
            st.session_state.assistant_session_id = None
            st.session_state.chat_messages = []
            st.rerun()

    # Pre-built Prompt Chips
    st.markdown("**Suggested Financial Inquiries:**")
    prompt_cols = st.columns(3)
    preset_query = None
    with prompt_cols[0]:
        if st.button("📊 'What is my current spending & savings rate?'"):
            preset_query = "What is my current spending, income, and savings rate?"
    with prompt_cols[1]:
        if st.button("🚗 'Can I afford to buy a $35,000 car with $5k down?'"):
            preset_query = "Can I afford to buy a $35,000 car with $5,000 down payment?"
    with prompt_cols[2]:
        if st.button("🛡️ 'How does an emergency fund protect me?'"):
            preset_query = "How does an emergency fund protect my investments from forced selling?"

    st.markdown("---")

    # Render Chat History
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("tools"):
                with st.expander("🛠️ Deterministic Financial Tools Executed"):
                    for tc in msg["tools"]:
                        st.markdown(f"**Tool:** `{tc['name']}` | **Args:** `{tc['arguments']}`")
                        st.json(tc["result"])
            if msg.get("sources"):
                with st.expander("📚 Knowledge Base Citations"):
                    for s in msg["sources"]:
                        st.markdown(f"**Source:** {s['title']} ({s['category']})")
                        st.caption(s["snippet"])

    # Chat Input
    user_input = st.chat_input("Ask any financial question...") or preset_query
    if user_input:
        # Display user message
        st.session_state.chat_messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Call Assistant API
        with st.chat_message("assistant"):
            with st.spinner("Analyzing verified financial records & knowledge..."):
                try:
                    resp = client.assistant_chat(
                        token=token,
                        message=user_input,
                        session_id=st.session_state.assistant_session_id
                    )
                    st.session_state.assistant_session_id = resp["session_id"]
                    
                    st.markdown(resp["content"])
                    tools = resp.get("tool_calls", [])
                    sources = resp.get("knowledge_sources", [])

                    if tools:
                        with st.expander("🛠️ Deterministic Financial Tools Executed"):
                            for tc in tools:
                                st.markdown(f"**Tool:** `{tc['name']}` | **Args:** `{tc['arguments']}`")
                                st.json(tc["result"])

                    if sources:
                        with st.expander("📚 Knowledge Base Citations"):
                            for s in sources:
                                st.markdown(f"**Source:** {s['title']} ({s['category']})")
                                st.caption(s["snippet"])

                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": resp["content"],
                        "tools": tools,
                        "sources": sources
                    })
                except Exception as e:
                    st.error(f"Assistant error: {e}")
