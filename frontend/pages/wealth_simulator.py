"""Wealth Simulator & Monte Carlo Stochastic Projections page."""

import streamlit as st
import plotly.graph_objects as go
from frontend.components.ui import page_header


def render_wealth_simulator():
    client = st.session_state.api_client
    token = st.session_state.token

    page_header(
        title="Wealth Simulator & Monte Carlo Stochastic Engine",
        subtitle="Model compound capital growth, annual contribution step-ups, inflation purchasing power loss, and 1,000-path stochastic percentiles."
    )

    tab_proj, tab_mc = st.tabs(["📈 Compound Wealth Projection", "🎲 Monte Carlo Simulation"])

    with tab_proj:
        col_ctrl, col_chart = st.columns([1, 2])
        with col_ctrl:
            init_inv = st.number_input("Initial Starting Capital ($)", min_value=0.0, value=10000.0, step=1000.0)
            monthly_sip = st.number_input("Monthly Contribution ($)", min_value=0.0, value=800.0, step=50.0)
            years = st.slider("Investment Horizon (Years)", min_value=1, max_value=40, value=20)
            exp_ret = st.slider("Expected Annual Return (%)", min_value=1.0, max_value=20.0, value=8.0, step=0.5)
            step_up = st.slider("Annual Contribution Step-Up (%)", min_value=0.0, max_value=15.0, value=5.0, step=1.0)
            inflation = st.slider("Annual Inflation Rate (%)", min_value=0.0, max_value=10.0, value=3.0, step=0.5)

            run_proj = st.button("Calculate Projection", type="primary", use_container_width=True)

        with col_chart:
            if run_proj or "proj_cache" in st.session_state:
                if run_proj:
                    payload = {
                        "initial_capital": str(init_inv),
                        "monthly_contribution": str(monthly_sip),
                        "annual_return_pct": str(exp_ret),
                        "horizon_years": years,
                        "annual_step_up_pct": str(step_up),
                        "inflation_rate_pct": str(inflation)
                    }
                    try:
                        st.session_state["proj_cache"] = client.project_wealth(token, payload)
                    except Exception as e:
                        st.error(f"Projection calculation error: {e}")

                if "proj_cache" in st.session_state:
                    res = st.session_state["proj_cache"]
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Final Nominal Wealth", f"${float(res['final_nominal_wealth']):,.0f}")
                    c2.metric("Total Capital Invested", f"${float(res['total_principal_contributed']):,.0f}")
                    c3.metric("Inflation-Adjusted Value", f"${float(res['final_real_wealth']):,.0f}")

                    # Chart
                    schedule = res["schedule"]
                    yr_axis = [s["year"] for s in schedule]
                    nom_vals = [float(s["nominal_wealth"]) for s in schedule]
                    real_vals = [float(s["real_wealth"]) for s in schedule]
                    invested = [float(s["cumulative_invested"]) for s in schedule]

                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=yr_axis, y=nom_vals, mode="lines", name="Nominal Wealth", line=dict(color="#2563EB", width=3)))
                    fig.add_trace(go.Scatter(x=yr_axis, y=real_vals, mode="lines", name="Real Wealth (Purchasing Power)", line=dict(color="#10B981", width=2, dash="dash")))
                    fig.add_trace(go.Scatter(x=yr_axis, y=invested, mode="lines", name="Total Out-of-Pocket Invested", line=dict(color="#94A3B8", width=1)))

                    fig.update_layout(
                        title=f"{years}-Year Wealth Accumulation Schedule",
                        xaxis_title="Years",
                        yaxis_title="Portfolio Balance ($)",
                        template="plotly_white",
                        height=360,
                        margin=dict(l=20, r=20, t=30, b=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)

    with tab_mc:
        st.markdown("### Geometric Brownian Motion Monte Carlo Engine")
        st.markdown("Unlike deterministic projections, markets experience volatility and non-linear paths. Monte Carlo models 1,000 probable futures.")

        mc_c1, mc_c2 = st.columns([1, 2])
        with mc_c1:
            mc_init = st.number_input("Starting Capital ($)", min_value=100.0, value=25000.0, step=1000.0, key="mc_init")
            mc_monthly = st.number_input("Monthly Contribution ($)", min_value=0.0, value=600.0, step=50.0, key="mc_m")
            mc_years = st.slider("Simulation Horizon (Years)", min_value=1, max_value=30, value=15, key="mc_y")
            mc_ret = st.slider("Mean Expected Return (μ %)", min_value=1.0, max_value=15.0, value=8.0, step=0.5, key="mc_r")
            mc_vol = st.slider("Expected Annual Volatility (σ %)", min_value=5.0, max_value=35.0, value=16.0, step=1.0, key="mc_v")
            mc_target = st.number_input("Financial Goal Target ($)", min_value=1000.0, value=300000.0, step=10000.0, key="mc_tgt")

            run_mc = st.button("Run 1,000 Monte Carlo Paths", type="primary", use_container_width=True)

        with mc_c2:
            if run_mc or "mc_cache" in st.session_state:
                if run_mc:
                    payload = {
                        "initial_capital": str(mc_init),
                        "monthly_contribution": str(mc_monthly),
                        "mean_annual_return_pct": str(mc_ret),
                        "annual_volatility_pct": str(mc_vol),
                        "horizon_years": mc_years,
                        "target_goal_amount": str(mc_target),
                        "num_simulations": 1000,
                        "random_seed": 42
                    }
                    try:
                        st.session_state["mc_cache"] = client.run_monte_carlo(token, payload)
                    except Exception as e:
                        st.error(f"Monte Carlo execution error: {e}")

                if "mc_cache" in st.session_state:
                    res_mc = st.session_state["mc_cache"]
                    prob = float(res_mc["probability_of_reaching_target_pct"])

                    k1, k2, k3 = st.columns(3)
                    k1.metric("P50 Median Outcome", f"${float(res_mc['p50_median']):,.0f}")
                    k2.metric("Goal Attainment Probability", f"{prob:.1f}%")
                    k3.metric("P10 Bear Market Floor", f"${float(res_mc['p10_bear_case']):,.0f}")

                    # Percentile Distribution Chart
                    fig_mc = go.Figure()
                    fig_mc.add_trace(go.Bar(
                        x=["P10 (Severe Bear)", "P25 (Conservative)", "P50 (Median)", "P75 (Strong Growth)", "P90 (Bull Market)"],
                        y=[float(res_mc["p10_bear_case"]), float(res_mc["p25"]), float(res_mc["p50_median"]), float(res_mc["p75"]), float(res_mc["p90_bull_case"])],
                        marker_color=["#EF4444", "#F59E0B", "#2563EB", "#10B981", "#8B5CF6"]
                    ))
                    fig_mc.add_hline(y=float(mc_target), line_dash="dash", line_color="#0F172A", annotation_text=f"Target: ${float(mc_target):,.0f}")
                    fig_mc.update_layout(
                        title=f"Distribution of 1,000 Simulated Wealth Outcomes ({mc_years} Years)",
                        yaxis_title="Final Portfolio Value ($)",
                        template="plotly_white",
                        height=350,
                        margin=dict(l=20, r=20, t=35, b=20)
                    )
                    st.plotly_chart(fig_mc, use_container_width=True)
