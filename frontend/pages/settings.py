"""Settings, User Preferences, and Data Privacy page."""

import json
import streamlit as st
from frontend.components.ui import page_header


def render_settings():
    client = st.session_state.api_client
    token = st.session_state.token
    user = st.session_state.user

    page_header(
        title="Settings & Data Privacy",
        subtitle="Manage personal financial preferences, currency formats, full data exports, and privacy controls."
    )

    tab_profile, tab_export, tab_privacy = st.tabs([
        "👤 Financial Profile", "📦 Data Export (GDPR / CCPA)", "🔒 Account Privacy & Security"
    ])

    with tab_profile:
        st.markdown("### Profile & Preferences")
        with st.form("settings_profile_form"):
            name = st.text_input("Full Name", value=user.get("full_name", ""))
            curr = st.selectbox(
                "Preferred Currency",
                ["USD", "EUR", "GBP", "INR", "CAD", "AUD", "JPY"],
                index=["USD", "EUR", "GBP", "INR", "CAD", "AUD", "JPY"].index(user.get("preferred_currency", "USD"))
            )
            monthly_inc = st.number_input("Declared Monthly Income ($)", min_value=0.0, value=float(user.get("monthly_income", 0.0) or 0.0), step=100.0)
            timezone_val = st.text_input("Timezone", value=user.get("timezone", "UTC"))

            if st.form_submit_button("Update Settings", type="primary"):
                try:
                    payload = {
                        "full_name": name,
                        "preferred_currency": curr,
                        "monthly_income": str(monthly_inc),
                        "timezone": timezone_val
                    }
                    updated_user = client.update_profile(token, payload)
                    st.session_state.user = updated_user
                    st.success("Profile preferences updated successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Update failed: {e}")

    with tab_export:
        st.markdown("### Export Account Data")
        st.markdown("Download a complete machine-readable JSON archive of all your personal records, transactions, budgets, goals, and portfolio holdings.")

        if st.button("Generate Complete JSON Data Export"):
            try:
                export_data = client.export_user_data(token)
                json_str = json.dumps(export_data, indent=2, default=str)
                st.download_button(
                    label="Download Complete Archive (.json)",
                    data=json_str,
                    file_name=f"wealthos_data_export_{user.get('id')}.json",
                    mime="application/json",
                    use_container_width=True
                )
                st.success("Archive generated successfully!")
            except Exception as e:
                st.error(f"Data export error: {e}")

    with tab_privacy:
        st.markdown("### Danger Zone: Account Deletion")
        st.warning("Account deletion is permanent and irreversible. All personal transactions, goals, portfolios, conversations, and audit logs will be permanently expunged from the database.")
        
        del_confirm = st.text_input("Type 'DELETE MY ACCOUNT' to confirm:", placeholder="DELETE MY ACCOUNT")
        if st.button("Permanently Delete My Account", type="primary"):
            if del_confirm == "DELETE MY ACCOUNT":
                try:
                    # Execute account deletion
                    headers = {"Authorization": f"Bearer {token}"}
                    import requests
                    r = requests.delete(f"{client.base_url}/users/me", headers=headers)
                    if r.ok:
                        st.session_state.token = None
                        st.session_state.user = None
                        st.success("Your account and all associated data have been permanently deleted.")
                        st.rerun()
                    else:
                        st.error(f"Failed to delete account: {r.text}")
                except Exception as ex:
                    st.error(str(ex))
            else:
                st.error("Please enter the exact confirmation phrase 'DELETE MY ACCOUNT'.")
