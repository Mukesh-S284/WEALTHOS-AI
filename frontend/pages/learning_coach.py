"""Financial Learning Coach page with curriculum, lesson text, and interactive quizzes."""

import streamlit as st
from frontend.components.ui import page_header


def render_learning_coach():
    client = st.session_state.api_client
    token = st.session_state.token

    page_header(
        title="Financial Learning Coach",
        subtitle="Interactive, objective curriculum on personal finance, investment principles, and financial literacy."
    )

    try:
        topics = client.list_learning_topics(token)
    except Exception as e:
        st.error(f"Failed to fetch learning topics: {e}")
        return

    # Top progress summary
    completed_count = sum(1 for t in topics if t.get("completed"))
    pct_complete = int((completed_count / len(topics)) * 100) if topics else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Curriculum Topics", len(topics))
    c2.metric("Topics Mastered", f"{completed_count} / {len(topics)}")
    c3.metric("Curriculum Completion", f"{pct_complete}%")
    st.progress(pct_complete / 100.0)

    st.markdown("---")

    col_menu, col_content = st.columns([1, 2])

    with col_menu:
        st.markdown("### Modules & Topics")
        topic_map = {t["topic_id"]: t for t in topics}

        def format_topic_label(tid: str) -> str:
            t = topic_map[tid]
            icon = "✅ " if t.get("completed") else "📖 "
            score_str = f" ({t['quiz_score']}%)" if t.get("quiz_score") is not None else ""
            return f"{icon}{t['title']}{score_str}"
        
        selected_id = st.radio(
            "Select Topic",
            options=list(topic_map.keys()),
            format_func=format_topic_label
        )

    with col_content:
        if selected_id:
            try:
                topic_data = client.get_learning_topic(token, selected_id)
                st.markdown(f"## {topic_data['title']}")
                st.caption(f"Category: {topic_data['category']} | Estimated Read Time: {topic_data['read_time_minutes']} mins")
                st.info(topic_data["summary"])

                # Lesson Content
                st.markdown(topic_data["content"])

                st.markdown("---")
                st.markdown("### 📝 Interactive Knowledge Check")
                st.caption("Pass with >= 66% to earn topic mastery credit.")

                quiz = topic_data.get("quiz", [])
                with st.form(f"quiz_form_{selected_id}"):
                    user_answers = {}
                    for q in quiz:
                        st.markdown(f"**{q['question']}**")
                        choice = st.radio(
                            "Select Answer:",
                            options=list(range(len(q["options"]))),
                            format_func=lambda idx, opts=q["options"]: opts[idx],
                            key=f"q_{q['id']}"
                        )
                        user_answers[q["id"]] = choice
                        st.write("")

                    submit_quiz = st.form_submit_button("Submit Quiz Answers", type="primary", use_container_width=True)

                if submit_quiz:
                    try:
                        res = client.submit_quiz(token, selected_id, user_answers)
                        if res["passed"]:
                            st.success(f"🎉 **Congratulations!** You passed with **{res['score_percentage']}%** ({res['correct_count']} of {res['total_questions']} correct)!")
                        else:
                            st.warning(f"Score: **{res['score_percentage']}%** ({res['correct_count']} of {res['total_questions']}). Review the explanations below and try again!")

                        # Show Question Results and Explanations
                        st.markdown("#### Answer Explanations:")
                        for qr in res.get("question_results", []):
                            status_icon = "✅" if qr["is_correct"] else "❌"
                            with st.expander(f"{status_icon} {qr['question']}"):
                                st.markdown(f"**Explanation:** {qr['explanation']}")
                        
                        st.rerun()
                    except Exception as e:
                        st.error(f"Quiz submission error: {e}")

            except Exception as e:
                st.error(f"Failed to load topic details: {e}")
