"""Life-Event Scenario Modeler page."""

import streamlit as st
from frontend.components.ui import page_header


def render_life_events():
    client = st.session_state.api_client
    token = st.session_state.token

    page_header(
        title="Life-Event Scenario Modeler",
        subtitle="Simulate career breaks, city relocation, medical emergencies, or home purchases before they occur."
    )

    col_form, col_report = st.columns([1, 1])

    with col_form:
        st.markdown("### 🧬 Configure Scenario")
        event_choice = st.selectbox(
            "Select Scenario Template",
            [
                "🏖️ Career Sabbatical / Unpaid Leave",
                "🏙️ Relocation to High Cost-of-Living City",
                "🏥 Unexpected Medical Shock Outflow",
                "🏡 Home Down Payment & Mortgage",
                "⚙️ Custom Scenario"
            ]
        )

        with st.form("scenario_form"):
            s_name = st.text_input("Scenario Name", value=event_choice.split(" ")[1])
            duration_months = st.slider("Duration (Months)", min_value=1, max_value=36, value=6)

            inc_delta = 0.0
            exp_delta = 0.0
            lump_sum = 0.0

            if "Sabbatical" in event_choice:
                inc_delta = -100.0 # 100% loss of income
                exp_delta = -10.0 # slight reduction in commute expenses
            elif "Relocation" in event_choice:
                inc_delta = 15.0 # 15% salary increase
                exp_delta = 35.0 # 35% higher rent/utilities
            elif "Medical" in event_choice:
                lump_sum = 8000.0 # $8,000 deductible/out-of-pocket
                exp_delta = 10.0 # recurring prescription costs
            elif "Home" in event_choice:
                lump_sum = 50000.0 # Down payment
                exp_delta = 800.0 # Additional housing cost vs previous rent

            c_inc, c_exp = st.columns(2)
            with c_inc:
                inc_pct = st.number_input("Monthly Income Change (%)", value=float(inc_delta), step=5.0)
            with c_exp:
                exp_pct = st.number_input("Monthly Living Expense Change (%)", value=float(exp_delta), step=5.0)

            lump = st.number_input("One-Time Upfront Outflow ($)", min_value=0.0, value=float(lump_sum), step=500.0)

            run_sim = st.form_submit_button("Simulate Scenario Impact", type="primary", use_container_width=True)

    with col_report:
        st.markdown("### 📊 Simulated Resilience Report")
        if run_sim:
            try:
                overview = client.get_overview(token)
                curr_inc = float(overview["monthly_income"])
                curr_exp = float(overview["monthly_expenses"])
                curr_ef = float(overview["emergency_fund_months"])

                # Simulated values
                sim_inc = max(0.0, curr_inc * (1.0 + (inc_pct / 100.0)))
                sim_exp = curr_exp * (1.0 + (exp_pct / 100.0))
                sim_surplus = sim_inc - sim_exp

                living_monthly = curr_exp if curr_exp > 0 else 2000.0
                curr_cash = curr_ef * living_monthly
                cash_after_lump = max(0.0, curr_cash - lump)
                sim_ef_months = round(cash_after_lump / (sim_exp if sim_exp > 0 else 1.0), 1)

                m1, m2 = st.columns(2)
                m1.metric("Simulated Monthly Surplus", f"${sim_surplus:,.2f}", f"${sim_surplus - float(overview['net_monthly_savings']):+,.2f}/mo")
                m2.metric("Simulated Emergency Runway", f"{sim_ef_months} mos", f"{sim_ef_months - curr_ef:+.1f} mos")

                st.markdown("---")
                if sim_surplus < 0:
                    monthly_drain = abs(sim_surplus)
                    total_drain = (monthly_drain * duration_months) + lump
                    st.error(f"⚠️ **Cash Flow Deficit:** This scenario drains **${monthly_drain:,.2f}/month**.")
                    st.markdown(f"**Total Capital Required for {duration_months} Months:** ${total_drain:,.2f}")
                    if cash_after_lump >= (monthly_drain * duration_months):
                        st.info("💡 Your existing liquid reserves can absorb this duration without taking on debt.")
                    else:
                        st.warning("🚨 **Shortfall Warning:** Existing reserves are insufficient to sustain this entire period. Secondary income or debt reduction required.")
                else:
                    st.success(f"✅ **Positive Cashflow Retained:** Even under this scenario, you generate a positive monthly surplus of **${sim_surplus:,.2f}**.")
            except Exception as e:
                st.error(f"Simulation failed: {e}")
        else:
            st.info("Select a template on the left and click 'Simulate Scenario Impact' to project financial resilience.")
