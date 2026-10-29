"""Scam & Fraud Awareness detector page."""

import streamlit as st
from frontend.components.ui import page_header


def render_scam_detector():
    client = st.session_state.api_client
    token = st.session_state.token

    page_header(
        title="Scam & Fraud Awareness Analyzer",
        subtitle="Detect red flags, manufactured urgency, guaranteed-return claims, and credential harvesting in investment offers."
    )

    col_in, col_res = st.columns([1, 1])

    with col_in:
        st.markdown("### 🔍 Test Investment Pitch or Message")
        st.caption("Paste the exact text of any suspicious message, email, social media pitch, or broker claim.")

        # Preset Samples
        st.markdown("**Try Example Scams or Safe Claims:**")
        sample_choice = st.selectbox(
            "Load Sample Claim",
            [
                "-- Select a sample --",
                "🚨 Guaranteed Returns & Double Money",
                "🚨 Credential & OTP Phishing Alert",
                "🚨 Multi-Level Pyramid / Ponzi Recruitment",
                "✅ Legitimate Registered Index Fund Prospectus"
            ]
        )

        default_text = ""
        if "Guaranteed" in sample_choice:
            default_text = "Join our exclusive crypto VIP trading club! 100% risk-free guaranteed returns of 35% weekly profit. Double your money in 7 days! You can't lose!"
        elif "Credential" in sample_choice:
            default_text = "WealthOS Security Notice: Unauthorized login detected from overseas IP. Please send your OTP and password immediately to prevent account suspension."
        elif "Pyramid" in sample_choice:
            default_text = "Act now before the window closes! Only 3 spots left! Recruit 5 people to earn passive income from your downline commission matrix."
        elif "Legitimate" in sample_choice:
            default_text = "Vanguard Total Stock Market Index Fund (VTI) tracks the CRSP US Total Market Index. The expense ratio is 0.03%. Past performance does not guarantee future results."

        with st.form("scam_detector_form"):
            pitch_text = st.text_area("Investment Text to Analyze", value=default_text, height=180, placeholder="Paste suspicious claim, email, or offer here...")
            submit_btn = st.form_submit_button("Analyze Threat Level", type="primary", use_container_width=True)

    with col_res:
        st.markdown("### 🛡️ Threat Assessment")
        if submit_btn and pitch_text.strip():
            try:
                res = client.analyze_scam(token, pitch_text.strip())
                st.session_state["scam_eval_cache"] = res
            except Exception as e:
                st.error(f"Analysis failed: {e}")

        if "scam_eval_cache" in st.session_state:
            d = st.session_state["scam_eval_cache"]
            score = d["threat_score"]
            level = d["risk_level"]

            if level in ("CRITICAL_SCAM", "HIGH_RISK"):
                st.error(f"### 🚨 {level}: Dangerous Offer (Threat Score: {score}/100)")
            elif level == "MEDIUM_RISK":
                st.warning(f"### ⚠️ {level}: Exercise Extreme Skepticism (Threat Score: {score}/100)")
            else:
                st.success(f"### 🟢 {level}: Low Risk Detected (Threat Score: {score}/100)")

            st.markdown(f"**Recommendation:** {d['recommendation']}")

            flags = d.get("detected_red_flags", [])
            if flags:
                st.markdown("#### 🚩 Specific Warning Signs Detected:")
                for f in flags:
                    st.markdown(f"- **{f['category'].replace('_', ' ').title()}** (`'{f['phrase_matched']}'`): {f['explanation']}")
            else:
                st.info("No standard high-risk scam phrases, credential phishing keywords, or Ponzi buzzwords detected.")

            st.markdown("---")
            st.markdown("#### 🏛️ Official Verification Checklist:")
            for step in d.get("official_verification_steps", []):
                st.markdown(f"- {step}")

            st.caption(d["disclaimer"])
        else:
            st.info("Paste a message or select a sample on the left to inspect red flags.")
