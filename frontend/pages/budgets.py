"""Monthly Budgets page: Set limits, track actual spending, and alert overages."""

import streamlit as st
from datetime import date
import plotly.graph_objects as go
from frontend.components.ui import page_header


def render_budgets():
    client = st.session_state.api_client
    token = st.session_state.token

    page_header(
        title="Monthly Budgets & Spending Control",
        subtitle="Establish category spending thresholds, monitor burn rates, and receive early warning alerts."
    )

    today = date.today()
    default_period = f"{today.year}-{today.month:02d}"

    col_period, col_new = st.columns([1, 2])
    with col_period:
        period = st.text_input("Reporting Period (YYYY-MM)", value=default_period)

    try:
        overview = client.get_budgets_overview(token, period=period)
    except Exception as e:
        st.error(f"Failed to fetch budget overview: {e}")
        return

    # Add / Update Budget Form
    with st.expander("➕ Set or Update Category Budget Limit"):
        with st.form("set_budget_form"):
            c_cat, c_limit = st.columns([2, 1])
            with c_cat:
                cat_choice = st.selectbox(
                    "Category",
                    ["Groceries", "Dining Out", "Housing", "Utilities", "Transportation", "Entertainment", "Shopping", "Healthcare", "Travel", "Subscriptions"]
                )
            with c_limit:
                limit_val = st.number_input("Monthly Limit ($)", min_value=10.0, value=500.0, step=50.0)

            if st.form_submit_button("Save Budget Limit"):
                try:
                    client.set_budget(token, category=cat_choice, limit_amount=limit_val, period=period)
                    st.success(f"Budget for '{cat_choice}' set to ${limit_val:,.2f}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error saving budget: {e}")

    # Display Metrics Summary
    tot_budget = float(overview.get("total_budgeted", 0.0))
    tot_spent = float(overview.get("total_spent", 0.0))
    remaining = float(overview.get("total_remaining", 0.0))
    pct_used = float(overview.get("overall_utilization_pct", 0.0))

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Budgeted", f"${tot_budget:,.2f}")
    m2.metric("Total Spent", f"${tot_spent:,.2f}")
    m3.metric("Remaining Pool", f"${remaining:,.2f}")
    m4.metric("Budget Utilization", f"{pct_used:.1f}%")

    st.markdown("---")
    items = overview.get("items", [])
    if not items:
        st.info("No budget categories established for this period yet. Click 'Set or Update Category Budget Limit' above to start.")
        return

    st.markdown("### 🎯 Category Utilization")
    for item in items:
        spent = float(item["actual_spent"])
        limit = float(item["budget_limit"])
        pct = float(item["percentage_used"])
        is_over = item["is_over_budget"]
        is_alert = item["is_near_limit"]

        col_title, col_prog, col_stat = st.columns([2, 4, 2])
        with col_title:
            st.markdown(f"**{item['category']}**")
            st.caption(f"${spent:,.2f} of ${limit:,.2f}")
        with col_prog:
            prog_val = min(1.0, max(0.0, pct / 100.0))
            st.progress(prog_val)
        with col_stat:
            if is_over:
                st.error(f"⚠️ Over by ${spent - limit:,.2f} ({pct:.0f}%)")
            elif is_alert:
                st.warning(f"Near Limit: {pct:.0f}%")
            else:
                st.success(f"${limit - spent:,.2f} left ({pct:.0f}%)")
