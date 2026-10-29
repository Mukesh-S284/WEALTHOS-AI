"""Portfolio Risk, Asset Allocation, and Stress Testing page."""

import streamlit as st
import plotly.graph_objects as go
from frontend.components.ui import page_header


def render_portfolio_risk():
    client = st.session_state.api_client
    token = st.session_state.token

    page_header(
        title="Portfolio Risk & Stress Testing",
        subtitle="Analyze asset allocation, concentration risk (HHI), volatility, maximum drawdown, and macroeconomic crisis stress tests."
    )

    try:
        portfolios = client.list_portfolios(token)
    except Exception as e:
        st.error(f"Failed to fetch portfolios: {e}")
        return

    if not portfolios:
        st.info("You haven't created a portfolio yet. Create your first portfolio below.")
        with st.form("create_portfolio_form"):
            p_name = st.text_input("Portfolio Name", value="Core Wealth Portfolio")
            p_desc = st.text_input("Description", value="Long-term diversified multi-asset account")
            if st.form_submit_button("Create Portfolio"):
                try:
                    client.create_portfolio(token, name=p_name, description=p_desc)
                    st.success("Portfolio created!")
                    st.rerun()
                except Exception as ex:
                    st.error(str(ex))
        return

    selected_portfolio = portfolios[0]
    p_id = selected_portfolio["id"]

    tab_holdings, tab_alloc, tab_stress, tab_add = st.tabs([
        "📊 Current Holdings", "🥧 Asset Allocation & Risk", "⚡ Stress Test Scenarios", "➕ Add Holding"
    ])

    with tab_holdings:
        tot_val = float(selected_portfolio.get("total_value", 0.0))
        tot_gain = float(selected_portfolio.get("total_unrealized_gain", 0.0))
        tot_gain_pct = float(selected_portfolio.get("total_unrealized_gain_pct", 0.0))

        c1, c2, c3 = st.columns(3)
        c1.metric("Total Portfolio Value", f"${tot_val:,.2f}")
        c2.metric("Total Unrealized Gain", f"${tot_gain:,.2f}", f"{tot_gain_pct:+.2f}%")
        c3.metric("Number of Holdings", len(selected_portfolio.get("holdings", [])))

        st.markdown("---")
        holdings = selected_portfolio.get("holdings", [])
        if not holdings:
            st.info("No holdings in this portfolio yet. Use the 'Add Holding' tab to enter positions.")
        else:
            st.dataframe(
                [
                    {
                        "Symbol": h["symbol"],
                        "Name": h["name"],
                        "Asset Class": h["asset_class"].upper(),
                        "Quantity": float(h["quantity"]),
                        "Avg Price": f"${float(h['average_buy_price']):,.2f}",
                        "Current Price": f"${float(h['current_price']):,.2f}",
                        "Current Value": f"${float(h['current_value']):,.2f}",
                        "Weight": f"{float(h['weight_pct']):.1f}%",
                        "Gain/Loss": f"${float(h['unrealized_gain']):+,.2f} ({float(h['unrealized_gain_pct']):+.1f}%)"
                    }
                    for h in holdings
                ],
                use_container_width=True,
                hide_index=True
            )

    with tab_alloc:
        alloc = selected_portfolio.get("asset_class_allocation_pct", {})
        if alloc:
            col_pie, col_risk = st.columns([1, 1])
            with col_pie:
                fig = go.Figure(go.Pie(
                    labels=list(alloc.keys()),
                    values=list(alloc.values()),
                    hole=0.45,
                    marker=dict(colors=["#2563EB", "#10B981", "#F59E0B", "#8B5CF6", "#EF4444"])
                ))
                fig.update_layout(title="Asset Class Distribution", height=320, margin=dict(l=10, r=10, t=30, b=10))
                st.plotly_chart(fig, use_container_width=True)

            with col_risk:
                st.markdown("#### Risk & Volatility Metrics")
                try:
                    risk_rep = client.get_risk_report(token, p_id)
                    st.metric("Herfindahl-Hirschman Index (HHI)", f"{risk_rep['hhi_concentration']:.3f}", f"Concentration: {risk_rep['concentration_rating']}")
                    st.metric("Annualized Volatility (σ)", f"{risk_rep['annualized_volatility_pct']:.1f}%")
                    st.metric("Maximum Historical Drawdown", f"{risk_rep['maximum_drawdown_pct']:.1f}%")
                    st.metric("Sharpe Ratio (Rf=4.0%)", f"{risk_rep['sharpe_ratio']:.2f}")
                except Exception as ex:
                    st.info(f"Risk metrics calculation: {ex}")
        else:
            st.info("Add holdings to calculate asset allocation breakdown.")

    with tab_stress:
        st.markdown("### Macroeconomic Crisis Stress Testing")
        st.markdown("Evaluate how your actual portfolio would perform during severe historical market dislocations.")
        try:
            risk_rep = client.get_risk_report(token, p_id)
            scenarios = risk_rep.get("stress_test_results", [])
            for s in scenarios:
                loss_val = float(s["projected_portfolio_loss"])
                pct_loss = float(s["projected_portfolio_loss_pct"])
                with st.expander(f"⚠️ {s['scenario_name']} — Projected Impact: {pct_loss:+.1f}% (${loss_val:,.2f})"):
                    st.markdown(s["description"])
                    st.markdown(f"**Value After Shock:** ${float(s['projected_value_after']):,.2f}")
        except Exception as ex:
            st.info(f"Stress test simulation: {ex}")

    with tab_add:
        st.markdown("### Add Holding to Portfolio")
        with st.form("add_holding_form"):
            c_sym, c_name = st.columns(2)
            with c_sym:
                h_sym = st.text_input("Ticker Symbol", placeholder="e.g. VTI, AAPL, BND, GLD, BTC-USD")
            with c_name:
                h_name = st.text_input("Holding Name", placeholder="e.g. Vanguard Total Stock Market ETF")

            c_ac, c_qty = st.columns(2)
            with c_ac:
                h_ac = st.selectbox("Asset Class", ["equity", "fixed_income", "cash", "commodities", "crypto", "real_estate"])
            with c_qty:
                h_qty = st.number_input("Shares / Units", min_value=0.0001, value=10.0, step=1.0)

            c_buy, c_curr = st.columns(2)
            with c_buy:
                h_buy = st.number_input("Average Buy Price ($)", min_value=0.01, value=220.0, step=5.0)
            with c_curr:
                h_curr = st.number_input("Current Market Price ($)", min_value=0.01, value=235.0, step=5.0)

            if st.form_submit_button("Add Position to Portfolio"):
                if not h_sym:
                    st.error("Please enter a ticker symbol.")
                else:
                    payload = {
                        "symbol": h_sym.strip().upper(),
                        "name": h_name or h_sym.strip().upper(),
                        "asset_class": h_ac,
                        "quantity": str(h_qty),
                        "average_buy_price": str(h_buy),
                        "current_price": str(h_curr)
                    }
                    try:
                        client.add_holding(token, p_id, payload)
                        st.success(f"Added {h_sym.upper()} to portfolio!")
                        st.rerun()
                    except Exception as ex:
                        st.error(f"Error adding holding: {ex}")
