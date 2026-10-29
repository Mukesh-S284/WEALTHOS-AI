"""Savings Goals and Emergency Liquidity page."""

import streamlit as st
from datetime import date
from dateutil.relativedelta import relativedelta
import plotly.graph_objects as go
from frontend.components.ui import page_header


def render_savings_goals():
    client = st.session_state.api_client
    token = st.session_state.token

    page_header(
        title="Savings Goals & Emergency Reserves",
        subtitle="Track targeted capital accumulation, calculate compound contributions, and safeguard liquid survival cushions."
    )

    tab_ef, tab_goals, tab_new = st.tabs([
        "🛡️ Emergency Fund Health", "🎯 Active Savings Goals", "➕ Create New Goal"
    ])

    with tab_ef:
        st.markdown("### Emergency Fund Adequacy Analyzer")
        st.markdown("Your liquid emergency fund protects your investments from forced liquidation during life shocks.")

        col_t, _ = st.columns([1, 2])
        with col_t:
            target_months = st.slider("Target Safety Horizon (Months)", min_value=3, max_value=12, value=6)

        try:
            ef_data = client.get_emergency_fund(token, target_months=target_months)
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Monthly Essential Needs", f"${float(ef_data['monthly_essential_expenses']):,.2f}")
            c2.metric("Target Reserve Pool", f"${float(ef_data['target_amount']):,.2f}")
            c3.metric("Current Liquid Cash", f"${float(ef_data['current_savings']):,.2f}")
            c4.metric("Months Covered", f"{ef_data['months_covered']:.1f} mos", f"Target: {target_months} mos")

            # Gauge Chart
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=ef_data['months_covered'],
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Liquid Runway (Months of Living Expenses)"},
                gauge={
                    'axis': {'range': [0, 12]},
                    'bar': {'color': "#2563EB"},
                    'steps': [
                        {'range': [0, 3], 'color': "#FEE2E2"},
                        {'range': [3, 6], 'color': "#FEF3C7"},
                        {'range': [6, 12], 'color': "#DCFCE7"}
                    ],
                    'threshold': {
                        'line': {'color': "#166534", 'width': 4},
                        'thickness': 0.75,
                        'value': target_months
                    }
                }
            ))
            fig.update_layout(height=260, margin=dict(l=20, r=20, t=30, b=10))
            st.plotly_chart(fig, use_container_width=True)

            if ef_data['months_covered'] >= target_months:
                st.success(f"✅ **Fully Funded:** Your emergency buffer covers {ef_data['months_covered']:.1f} months, exceeding your {target_months}-month target.")
            elif ef_data['months_covered'] >= 3.0:
                st.info(f"🟡 **Adequate Baseline:** You have {ef_data['months_covered']:.1f} months covered. Close the ${float(ef_data['gap_amount']):,.2f} gap to reach your optimal target.")
            else:
                st.warning(f"🔴 **Vulnerable Buffer:** Current reserves cover only {ef_data['months_covered']:.1f} months. Prioritize building this reserve before aggressive speculative investing.")

        except Exception as e:
            st.error(f"Failed to calculate emergency fund status: {e}")

    with tab_goals:
        try:
            goals = client.list_savings_goals(token)
            if not goals:
                st.info("No savings goals established yet. Use the 'Create New Goal' tab to define your targets.")
            else:
                st.markdown(f"### You have {len(goals)} Active Goal{'s' if len(goals) > 1 else ''}")
                for g in goals:
                    target = float(g["target_amount"])
                    current = float(g["current_amount"])
                    monthly = float(g["monthly_contribution"])
                    pct = min(100.0, (current / target) * 100.0) if target > 0 else 0.0

                    with st.container():
                        col_info, col_pb, col_on_track = st.columns([3, 3, 2])
                        with col_info:
                            st.markdown(f"#### {g['title']}")
                            st.caption(f"Target: ${target:,.2f} | Deadline: {g['target_date']}")
                            st.write(f"**Saved:** ${current:,.2f} (${target - current:,.2f} remaining)")
                        with col_pb:
                            st.write(f"**Progress: {pct:.1f}%**")
                            st.progress(pct / 100.0)
                            st.caption(f"Monthly SIP: ${monthly:,.2f}/month")
                        with col_on_track:
                            if g.get("is_on_track"):
                                st.success("🟢 On Track")
                            else:
                                st.warning("⚠️ Off Track / Shortfall")
                            req_sip = g.get("required_monthly_savings")
                            if req_sip:
                                st.caption(f"Required SIP: ${float(req_sip):,.2f}/mo")
                        st.markdown("---")
        except Exception as e:
            st.error(f"Failed to list goals: {e}")

    with tab_new:
        st.markdown("### Define a Savings Goal")
        with st.form("new_goal_form"):
            c_title, c_cat = st.columns([2, 1])
            with c_title:
                g_title = st.text_input("Goal Title", placeholder="e.g. Home Down Payment, Wedding, New Car")
            with c_cat:
                g_cat = st.selectbox("Goal Category", ["general", "emergency_fund", "house", "car", "education", "retirement", "vacation"])

            c_target, c_curr, c_date = st.columns(3)
            with c_target:
                g_target = st.number_input("Target Amount ($)", min_value=100.0, value=20000.0, step=500.0)
            with c_curr:
                g_curr = st.number_input("Current Amount Saved ($)", min_value=0.0, value=2500.0, step=100.0)
            with c_date:
                default_target_date = date.today() + relativedelta(years=2)
                g_target_date = st.date_input("Target Date", value=default_target_date)

            c_sip, c_ret = st.columns(2)
            with c_sip:
                g_sip = st.number_input("Planned Monthly Contribution ($)", min_value=0.0, value=500.0, step=50.0)
            with c_ret:
                g_ret = st.number_input("Expected Annual Return (%)", min_value=0.0, max_value=25.0, value=5.0, step=0.5)

            if st.form_submit_button("Create Savings Goal", use_container_width=True):
                if not g_title:
                    st.error("Please enter a goal title.")
                else:
                    payload = {
                        "title": g_title,
                        "category": g_cat,
                        "target_amount": str(g_target),
                        "current_amount": str(g_curr),
                        "target_date": str(g_target_date),
                        "monthly_contribution": str(g_sip),
                        "expected_annual_return_pct": str(g_ret)
                    }
                    try:
                        client.create_savings_goal(token, payload)
                        st.success(f"Goal '{g_title}' successfully created!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error creating goal: {e}")
