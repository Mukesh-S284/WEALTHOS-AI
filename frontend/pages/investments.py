"""Investment Intelligence: Asset classes, live quotes, and educational analytics."""

import streamlit as st
import plotly.graph_objects as go
from frontend.components.ui import page_header


def render_investments():
    client = st.session_state.api_client
    token = st.session_state.token

    page_header(
        title="Investment Intelligence & Multi-Asset Analytics",
        subtitle="Live market data, asset class risk-return profiles, and transparent instrument analysis."
    )

    tab_quote, tab_classes = st.tabs(["📈 Live Market Quote Lookup", "📚 Asset Class Directory"])

    with tab_quote:
        col_sym, col_btn = st.columns([3, 1])
        with col_sym:
            symbol = st.text_input("Enter Ticker Symbol", value="SPY", placeholder="e.g. SPY, VTI, AAPL, MSFT, BND, GLD, BTC-USD")
        with col_btn:
            st.write("")
            st.write("")
            lookup_btn = st.button("Fetch Live Data", type="primary", use_container_width=True)

        if symbol:
            try:
                quote = client.get_market_quote(token, symbol.strip().upper())
                
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Ticker / Instrument", f"{quote['symbol']}")
                c2.metric("Market Price", f"${float(quote['current_price']):,.2f}")
                c3.metric("Asset Class", f"{quote['asset_class'].upper()}")
                c4.metric("Data Provider", f"{quote['data_source']}")

                if quote.get("historical_prices") and len(quote["historical_prices"]) > 1:
                    hist = quote["historical_prices"]
                    dates = [p["date"] for p in hist]
                    closes = [float(p["close"]) for p in hist]

                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=dates, y=closes,
                        mode="lines",
                        line=dict(color="#2563EB", width=2),
                        name="Close Price"
                    ))
                    fig.update_layout(
                        title=f"{quote['symbol']} Historical Price Chart",
                        template="plotly_white",
                        height=350,
                        margin=dict(l=20, r=20, t=40, b=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Single snapshot quote retrieved.")

                # Provenance and metadata
                st.caption(f"Observation recorded: {quote['as_of_date']} | Status: Verified live feed via {quote['data_source']}")

            except Exception as e:
                st.error(f"Market data lookup failed for '{symbol}': {e}")

    with tab_classes:
        st.markdown("### Core Financial Products & Asset Classes")
        try:
            classes = client.get_asset_classes(token)
            for ac in classes:
                with st.expander(f"{ac['name']} — Risk: {ac['risk_level'].upper()} | Expected: {ac['expected_return_range']}"):
                    st.markdown(ac["description"])
                    st.markdown(f"**Best Suited For:** {ac['suitability']}")
                    st.markdown(f"**Typical Instruments:** {', '.join(ac['typical_instruments'])}")
        except Exception as e:
            st.error(f"Failed to fetch asset class directory: {e}")
