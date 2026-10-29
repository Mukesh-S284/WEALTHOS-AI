"""Dashboard & Unified Decision Hub page."""

import streamlit as st
import plotly.graph_objects as go
from frontend.components.ui import page_header, render_metric_card


def render_dashboard():
    client = st.session_state.api_client
    token = st.session_state.token
    currency = st.session_state.user.get("preferred_currency", "USD")

    try:
        overview = client.get_overview(token)
    except Exception as e:
        st.error(f"Failed to fetch overview: {e}")
        return

    page_header(
        title="Unified Financial Intelligence Hub",
        subtitle="Real-time multi-pillar status across cash flow, liquidity, liabilities, investments, and health.",
        badge=f"Score: {overview['health_score']}/100 ({overview['health_rating']})"
    )

    # Row 1: Cash Flow Metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card("Monthly Income", f"${float(overview['monthly_income']):,.2f}", "Total periodic inflows")
    with c2:
        render_metric_card("Living Expenses", f"${float(overview['monthly_expenses']):,.2f}", "Monthly burn rate")
    with c3:
        surplus = float(overview['net_monthly_savings'])
        sub_text = "Positive surplus" if surplus >= 0 else "Cash flow deficit!"
        render_metric_card("Net Monthly Savings", f"${surplus:,.2f}", sub_text)
    with c4:
        sr = overview['savings_rate_pct']
        render_metric_card("Savings Rate", f"{sr:.1f}%", "Target: >= 20%")

    # Row 2: Reserves, Liabilities, Wealth
    c5, c6, c7, c8 = st.columns(4)
    with c5:
        ef = overview['emergency_fund_months']
        render_metric_card("Emergency Liquidity", f"{ef:.1f} mos", "Buffer vs living expenses")
    with c6:
        dti = overview['debt_to_income_pct']
        render_metric_card("Debt-to-Income", f"{dti:.1f}%", "Ceiling: < 36%")
    with c7:
        pval = float(overview['total_portfolio_value'])
        render_metric_card("Portfolio Value", f"${pval:,.2f}", "Multi-asset holdings")
    with c8:
        score = overview['health_score']
        render_metric_card("Financial Health", f"{score} / 100", f"Rating: {overview['health_rating']}")

    st.markdown("### 📊 Cash Flow & Capital Allocation Breakdown")
    col_chart, col_summary = st.columns([3, 2])

    with col_chart:
        # Plotly Waterfall or Bar Chart
        fig = go.Figure(go.Waterfall(
            name="Cashflow",
            orientation="v",
            measure=["relative", "relative", "total"],
            x=["Income", "Expenses", "Net Savings"],
            textposition="outside",
            text=[f"+${float(overview['monthly_income']):,.0f}", f"-${float(overview['monthly_expenses']):,.0f}", f"${surplus:,.0f}"],
            y=[float(overview['monthly_income']), -float(overview['monthly_expenses']), surplus],
            connector={"line": {"color": "#94A3B8"}},
            decreasing={"marker": {"color": "#EF4444"}},
            increasing={"marker": {"color": "#10B981"}},
            totals={"marker": {"color": "#2563EB"}}
        ))
        fig.update_layout(
            title="Monthly Cash Flow Reconciliation",
            template="plotly_white",
            height=340,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_summary:
        st.markdown("#### Decision Engine Health Status")
        if overview['health_score'] >= 80:
            st.success("🟢 **Financially Resilient:** Your emergency liquidity and cashflow buffer provide solid protection against market volatility.")
        elif overview['health_score'] >= 60:
            st.info("🟡 **Stable with Growth Opportunities:** Moderate cash flow. Consider boosting your liquid emergency buffer toward 6 months.")
        else:
            st.warning("🔴 **Margin of Safety Tight:** High debt servicing or low liquid cash reserves. Review discretionary expenses and prioritize emergency buffer.")

        st.markdown(f"- **Active Savings Goals:** {overview['active_goals_count']}")
        st.markdown(f"- **Total Outstanding Liabilities:** ${float(overview['total_debt_balance']):,.2f}")
        st.markdown(f"- **Operating Currency:** {currency}")

    # Recent Activity snippet
    st.markdown("### 🕒 Recent Transaction Flow")
    try:
        txs = client.list_transactions(token, limit=5)
        if txs:
            st.dataframe(
                [
                    {
                        "Date": t["date"],
                        "Description": t["description"],
                        "Category": t["category"],
                        "Type": t["type"].upper(),
                        "Amount": f"${float(t['amount']):,.2f}"
                    }
                    for t in txs
                ],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No transactions recorded yet. Visit the Smart Money Manager to add transactions or import bank CSVs.")
    except Exception as e:
        st.warning(f"Unable to load transactions: {e}")
