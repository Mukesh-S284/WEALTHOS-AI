"""WealthOS AI — Main Streamlit Application Entrypoint.

Unified Financial Intelligence Platform:
Connects Money Management, Budgeting, Investment Analytics, Portfolio Risk,
Purchase Decision Engine, Simulations, RAG Assistant, and Financial Health Reporting.
"""

import streamlit as st
from frontend.services.api_client import APIClient
from frontend.components.ui import apply_custom_css, render_regulatory_disclaimer

st.set_page_config(
    page_title="WealthOS AI — Unified Wealth Platform",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply global styling
apply_custom_css()

# Initialize session state
if "api_client" not in st.session_state:
    st.session_state.api_client = APIClient()

if "token" not in st.session_state:
    st.session_state.token = None

if "user" not in st.session_state:
    st.session_state.user = None


def render_auth_view():
    """Render Login & Registration screen when unauthenticated."""
    col_l, col_center, col_r = st.columns([1, 2, 1])
    with col_center:
        st.markdown("<h1 style='text-align: center;'>💎 WealthOS AI</h1>", unsafe_allow_html=True)
        st.markdown(
            "<p style='text-align: center; color: #64748B; margin-bottom: 25px;'>Explainable AI-Powered Personal Finance & Investment Intelligence</p>",
            unsafe_allow_html=True
        )

        tab_login, tab_register = st.tabs(["Sign In", "Create Account"])

        with tab_login:
            with st.form("login_form"):
                email = st.text_input("Email Address", value="demo@wealthos.ai")
                password = st.text_input("Password", type="password", value="SecurePass123!")
                submit = st.form_submit_button("Sign In to WealthOS", use_container_width=True)

                if submit:
                    try:
                        res = st.session_state.api_client.login(email, password)
                        st.session_state.token = res["access_token"]
                        st.session_state.user = st.session_state.api_client.get_me(st.session_state.token)
                        st.success(f"Welcome back, {st.session_state.user.get('full_name')}!")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))

            st.markdown("<div style='text-align: center; margin-top: 10px;'><em>Tip: If demo account does not exist, use Create Account tab or register below.</em></div>", unsafe_allow_html=True)

        with tab_register:
            with st.form("register_form"):
                reg_name = st.text_input("Full Name", value="Alex Morgan")
                reg_email = st.text_input("Email Address", value="demo@wealthos.ai")
                reg_pass = st.text_input("Password", type="password", value="SecurePass123!")
                reg_curr = st.selectbox("Preferred Currency", ["USD", "EUR", "GBP", "INR", "CAD", "AUD"])
                reg_submit = st.form_submit_button("Create New Account", use_container_width=True)

                if reg_submit:
                    try:
                        res = st.session_state.api_client.register(
                            email=reg_email,
                            password=reg_pass,
                            full_name=reg_name,
                            preferred_currency=reg_curr
                        )
                        st.session_state.token = res["access_token"]
                        st.session_state.user = st.session_state.api_client.get_me(st.session_state.token)
                        st.success("Account created successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))


def main():
    if not st.session_state.token or not st.session_state.user:
        render_auth_view()
        render_regulatory_disclaimer()
        return

    # Sidebar: User profile badge and module navigation
    with st.sidebar:
        st.markdown(f"### 💎 WealthOS AI")
        st.markdown(f"**{st.session_state.user.get('full_name')}** ({st.session_state.user.get('preferred_currency')})")
        st.caption(st.session_state.user.get("email"))

        nav_choice = st.radio(
            "Navigate",
            [
                "🏠 Dashboard & Decision Hub",
                "💵 Smart Money Manager",
                "📊 Monthly Budgets",
                "🎯 Savings Goals & Liquidity",
                "📈 Investment Intelligence",
                "🛡️ Portfolio Risk & Drawdown",
                "🛍️ Smart Purchase Planner",
                "🚀 Wealth Simulator & Monte Carlo",
                "🧬 Life-Event Scenario Modeler",
                "🤖 AI Finance Assistant",
                "🎓 Financial Learning Coach",
                "🔍 Scam & Fraud Detector",
                "📋 Financial Health Reports",
                "⚙️ Settings & Data Privacy"
            ]
        )

        st.markdown("---")
        if st.button("Sign Out", use_container_width=True):
            st.session_state.token = None
            st.session_state.user = None
            st.rerun()

    # Dynamic page rendering
    if nav_choice == "🏠 Dashboard & Decision Hub":
        from frontend.pages.dashboard import render_dashboard
        render_dashboard()
    elif nav_choice == "💵 Smart Money Manager":
        from frontend.pages.money_manager import render_money_manager
        render_money_manager()
    elif nav_choice == "📊 Monthly Budgets":
        from frontend.pages.budgets import render_budgets
        render_budgets()
    elif nav_choice == "🎯 Savings Goals & Liquidity":
        from frontend.pages.savings_goals import render_savings_goals
        render_savings_goals()
    elif nav_choice == "📈 Investment Intelligence":
        from frontend.pages.investments import render_investments
        render_investments()
    elif nav_choice == "🛡️ Portfolio Risk & Drawdown":
        from frontend.pages.portfolio_risk import render_portfolio_risk
        render_portfolio_risk()
    elif nav_choice == "🛍️ Smart Purchase Planner":
        from frontend.pages.purchase_planner import render_purchase_planner
        render_purchase_planner()
    elif nav_choice == "🚀 Wealth Simulator & Monte Carlo":
        from frontend.pages.wealth_simulator import render_wealth_simulator
        render_wealth_simulator()
    elif nav_choice == "🧬 Life-Event Scenario Modeler":
        from frontend.pages.life_events import render_life_events
        render_life_events()
    elif nav_choice == "🤖 AI Finance Assistant":
        from frontend.pages.ai_assistant import render_ai_assistant
        render_ai_assistant()
    elif nav_choice == "🎓 Financial Learning Coach":
        from frontend.pages.learning_coach import render_learning_coach
        render_learning_coach()
    elif nav_choice == "🔍 Scam & Fraud Detector":
        from frontend.pages.scam_detector import render_scam_detector
        render_scam_detector()
    elif nav_choice == "📋 Financial Health Reports":
        from frontend.pages.health_reports import render_health_reports
        render_health_reports()
    elif nav_choice == "⚙️ Settings & Data Privacy":
        from frontend.pages.settings import render_settings
        render_settings()

    render_regulatory_disclaimer()


if __name__ == "__main__":
    main()
