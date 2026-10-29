"""Smart Purchase Planner & Unified Financial Decision Engine page."""

import streamlit as st
from frontend.components.ui import page_header


def render_purchase_planner():
    client = st.session_state.api_client
    token = st.session_state.token

    page_header(
        title="Smart Purchase Planner & Decision Engine",
        subtitle="Evaluate the true multi-pillar affordability of major purchases across cash flow, emergency buffers, debt service, and goal delays."
    )

    col_in, col_res = st.columns([1, 1])

    with col_in:
        st.markdown("### 🛍️ Purchase Details")
        with st.form("purchase_eval_form"):
            p_name = st.text_input("Item / Purchase Name", value="New Commuter Vehicle", placeholder="e.g. Car, Home Remodel, Luxury Watch, Vacation")
            p_cost = st.number_input("Total Purchase Cost ($)", min_value=100.0, value=28000.0, step=500.0)
            
            p_fin = st.radio("How will you pay?", ["loan", "cash"], horizontal=True, format_func=lambda x: "Finance / Loan" if x == "loan" else "Pay in Cash (Liquid Savings)")
            
            p_down = 0.0
            p_apr = 6.5
            p_tenure = 48
            if p_fin == "loan":
                c_d, c_a = st.columns(2)
                with c_d:
                    p_down = st.number_input("Down Payment ($)", min_value=0.0, value=4000.0, step=500.0)
                with c_a:
                    p_apr = st.number_input("Loan APR (%)", min_value=0.0, max_value=35.0, value=6.5, step=0.25)
                p_tenure = st.selectbox("Loan Tenure (Months)", [12, 24, 36, 48, 60, 72], index=3)

            submit_eval = st.form_submit_button("Run Unified Decision Analysis", type="primary", use_container_width=True)

    with col_res:
        st.markdown("### 🔍 Multi-Pillar Decision Verdict")
        if submit_eval:
            payload = {
                "decision_type": "expensive_purchase",
                "purchase": {
                    "name": p_name,
                    "cost": str(p_cost),
                    "financing_option": p_fin,
                    "down_payment": str(p_down),
                    "loan_interest_rate_pct": str(p_apr),
                    "loan_term_months": p_tenure
                }
            }
            try:
                res = client.evaluate_decision(token, payload)
                st.session_state["last_decision_eval"] = res
            except Exception as e:
                st.error(f"Decision evaluation failed: {e}")

        if "last_decision_eval" in st.session_state:
            d = st.session_state["last_decision_eval"]
            verdict = d["recommendation_verdict"]

            if verdict == "APPROVED_SAFE":
                st.success(f"### 🟢 {verdict}: Purchase Feasible")
            elif verdict == "PROCEED_WITH_CAUTION":
                st.warning(f"### 🟡 {verdict}: Tight Financial Margins")
            else:
                st.error(f"### 🔴 {verdict}: High Financial Strain")

            st.markdown(d["executive_summary"])

            # 4 Pillar Breakdown
            b = d["budget_impact"]
            ef = d["emergency_fund_impact"]
            debt = d["debt_impact"]

            st.markdown("---")
            st.markdown("#### 1. Cash Flow & Budget Surplus")
            m1, m2 = st.columns(2)
            m1.metric("Monthly Surplus Before", f"${float(b['monthly_surplus_before']):,.2f}")
            surplus_after = float(b['monthly_surplus_after'])
            delta_s = float(b['surplus_change'])
            m2.metric("Monthly Surplus After", f"${surplus_after:,.2f}", f"{delta_s:+,.2f}/mo")

            st.markdown("#### 2. Emergency Runway Buffer")
            ef1, ef2 = st.columns(2)
            ef1.metric("Reserves Before", f"{ef['months_before']:.1f} mos")
            ef2.metric("Reserves After", f"{ef['months_after']:.1f} mos", f"-{ef['months_depleted']:.1f} mos")
            if ef.get("rebuild_months"):
                st.info(f"⏳ Rebuilding depleted reserves will take **{ef['rebuild_months']} months** at current monthly surplus.")

            st.markdown("#### 3. Liabilities & Debt-to-Income (DTI)")
            dt1, dt2 = st.columns(2)
            dt1.metric("DTI Before", f"{debt['dti_pct_before']:.1f}%")
            dt2.metric("DTI After", f"{debt['dti_pct_after']:.1f}%", f"+{(debt['dti_pct_after'] - debt['dti_pct_before']):.1f}%")

            # Goals Delay
            goals_delayed = d.get("cross_goal_impacts", [])
            if goals_delayed:
                st.markdown("#### 4. Impact on Competing Savings Goals")
                for gi in goals_delayed:
                    st.warning(f"🎯 **{gi['goal_title']}**: Delayed by approx **{gi['projected_delay_months']} months** due to cash flow constraints.")

            st.markdown("---")
            st.markdown("#### 💡 Trade-Offs & Actionable Alternatives")
            for t in d.get("tradeoff_analysis", []):
                st.markdown(f"- {t}")
            for a in d.get("actionable_alternatives", []):
                st.markdown(f"👉 **Option:** {a}")
        else:
            st.info("Fill out the purchase details on the left and click 'Run Unified Decision Analysis' to inspect cross-module impacts.")
