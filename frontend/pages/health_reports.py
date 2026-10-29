"""Financial Health Reports page with 7-factor transparent score."""

import streamlit as st
from datetime import date
import plotly.graph_objects as go
from frontend.components.ui import page_header


def render_health_reports():
    client = st.session_state.api_client
    token = st.session_state.token

    page_header(
        title="Comprehensive Financial Health Reports",
        subtitle="Objective 7-factor diagnostic scorecard evaluating cash flow, resilience, liabilities, and investment structure."
    )

    today = date.today()
    default_period = f"{today.year}-{today.month:02d}"

    col_p, col_btn = st.columns([2, 1])
    with col_p:
        period = st.text_input("Report Period (YYYY-MM)", value=default_period)

    try:
        report = client.get_health_report(token, period=period)
    except Exception as e:
        st.error(f"Failed to generate health report: {e}")
        return

    # Top Health Score Banner
    score = report["overall_health_score"]
    rating = report["rating"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Overall Health Score", f"{score} / 100")
    c2.metric("Rating Classification", rating)
    c3.metric("Savings Rate", f"{report['savings_rate_pct']:.1f}%")
    c4.metric("Net Monthly Savings", f"${float(report['net_savings']):,.2f}")

    st.markdown("---")
    st.markdown("### 🧭 Seven Core Health Indicators")

    indicators = report.get("indicators", [])

    col_chart, col_list = st.columns([1, 1])

    with col_chart:
        # Radar chart of scores
        ind_names = [i["name"] for i in indicators]
        ind_pcts = [(i["score"] / i["max_score"]) * 100.0 for i in indicators]

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=ind_pcts + [ind_pcts[0]],
            theta=ind_names + [ind_names[0]],
            fill='toself',
            fillcolor='rgba(37, 99, 235, 0.2)',
            line=dict(color='#2563EB', width=2),
            name="Health Profile"
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False,
            height=360,
            margin=dict(l=40, r=40, t=20, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_list:
        for ind in indicators:
            with st.container():
                st.markdown(f"**{ind['name']}** ({ind['category']}) — **{ind['score']} / {ind['max_score']} pts**")
                st.caption(f"Metric: `{ind['metric_value']}` | Benchmark: `{ind['target_benchmark']}`")
                st.write(ind["explanation"])
                st.markdown("---")

    # Strengths and Improvements
    st.markdown("### 💡 Diagnostic Analysis")
    col_str, col_imp = st.columns(2)
    with col_str:
        st.markdown("#### 🟢 Key Strengths:")
        for s in report.get("strengths", []):
            st.markdown(f"- **{s}**")
    with col_imp:
        st.markdown("#### 🟡 Areas for Improvement:")
        for imp in report.get("areas_for_improvement", []):
            st.markdown(f"- **{imp}**")

    st.markdown("---")
    st.caption(report["disclaimer"])
