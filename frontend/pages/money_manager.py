"""Smart Money Manager page: Transactions, Categories, CSV Import/Export."""

import streamlit as st
from datetime import date
from frontend.components.ui import page_header


def render_money_manager():
    client = st.session_state.api_client
    token = st.session_state.token

    page_header(
        title="Smart Money Manager",
        subtitle="Record income and expenses, auto-categorize with machine learning, and manage bank CSV imports."
    )

    tab_txs, tab_new, tab_import, tab_export = st.tabs([
        "All Transactions", "Add Transaction", "Import CSV", "Export Data"
    ])

    with tab_txs:
        col_f1, col_f2 = st.columns([1, 3])
        with col_f1:
            filter_type = st.selectbox("Filter Type", ["All", "income", "expense"])
        
        try:
            tx_type = None if filter_type == "All" else filter_type
            transactions = client.list_transactions(token, limit=100, tx_type=tx_type)
            
            if transactions:
                # Summary header
                incomes = sum(float(t["amount"]) for t in transactions if t["type"] == "income")
                expenses = sum(float(t["amount"]) for t in transactions if t["type"] == "expense")
                m1, m2, m3 = st.columns(3)
                m1.metric("Filtered Income", f"${incomes:,.2f}")
                m2.metric("Filtered Expenses", f"${expenses:,.2f}")
                m3.metric("Net Flow", f"${(incomes - expenses):,.2f}")

                st.markdown("---")
                # Table view
                for t in transactions[:30]:
                    col1, col2, col3, col4, col5 = st.columns([2, 4, 3, 2, 1])
                    with col1:
                        st.write(t["date"])
                    with col2:
                        st.markdown(f"**{t['description']}**")
                    with col3:
                        badge = "🟢" if t["type"] == "income" else "🔴"
                        st.caption(f"{badge} {t['category']}")
                    with col4:
                        prefix = "+" if t["type"] == "income" else "-"
                        st.markdown(f"**{prefix}${float(t['amount']):,.2f}**")
                    with col5:
                        if st.button("🗑️", key=f"del_{t['id']}"):
                            try:
                                client.delete_transaction(token, t["id"])
                                st.success("Deleted")
                                st.rerun()
                            except Exception as ex:
                                st.error(str(ex))
            else:
                st.info("No transactions match the selected filter.")
        except Exception as e:
            st.error(f"Failed to fetch transactions: {e}")

    with tab_new:
        st.markdown("### Record Transaction")
        with st.form("new_transaction_form"):
            c_desc, c_amt = st.columns([3, 1])
            with c_desc:
                desc = st.text_input("Description / Merchant", placeholder="e.g. Whole Foods Market, Apple Store, Monthly Salary")
            with c_amt:
                amt = st.number_input("Amount ($)", min_value=0.01, value=50.00, step=1.0)

            c_date, c_type, c_cat = st.columns(3)
            with c_date:
                tx_date = st.date_input("Date", value=date.today())
            with c_type:
                t_type = st.selectbox("Transaction Type", ["expense", "income"])
            with c_cat:
                cat = st.text_input("Category (leave blank for ML Auto-categorization)", placeholder="Optional")

            c_notes, c_rec = st.columns([3, 1])
            with c_notes:
                notes = st.text_input("Notes / Reference", placeholder="Optional")
            with c_rec:
                is_recurring = st.checkbox("Recurring Bill / Income")

            submit_btn = st.form_submit_button("Save Transaction", use_container_width=True)

            if submit_btn:
                if not desc:
                    st.error("Please enter a description.")
                else:
                    payload = {
                        "date": str(tx_date),
                        "description": desc,
                        "amount": str(amt),
                        "type": t_type,
                        "is_recurring": is_recurring,
                        "notes": notes
                    }
                    if cat:
                        payload["category"] = cat
                    try:
                        res = client.create_transaction(token, payload)
                        st.success(f"Transaction recorded! Categorized as: **{res.get('category')}**")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

    with tab_import:
        st.markdown("### Bank CSV Statement Import")
        st.markdown("WealthOS automatically previews, cleans, validates formats, detects duplicates, and predicts categories.")
        
        uploaded_file = st.file_uploader("Upload CSV Statement", type=["csv"])
        csv_text_input = st.text_area("Or Paste Raw CSV Lines", height=120, placeholder="date,description,amount,type\n2026-10-01,Salary Paycheck,4000.00,income\n2026-10-02,Trader Joes,85.20,expense")

        content_to_preview = None
        if uploaded_file is not None:
            content_to_preview = uploaded_file.getvalue().decode("utf-8")
        elif csv_text_input.strip():
            content_to_preview = csv_text_input.strip()

        if content_to_preview:
            if st.button("Preview Import & Validate", key="preview_btn"):
                try:
                    preview_data = client.preview_csv_import(token, content_to_preview)
                    st.session_state["csv_preview_cache"] = preview_data
                except Exception as e:
                    st.error(f"Preview failed: {e}")

        if "csv_preview_cache" in st.session_state:
            p = st.session_state["csv_preview_cache"]
            st.markdown(f"**Found {p['total_rows_found']} rows:** {len(p['valid_transactions'])} valid, {len(p['duplicate_transactions'])} duplicate flags, {len(p['invalid_rows'])} invalid.")
            
            if p["valid_transactions"]:
                st.markdown("#### Preview of Valid Rows Ready to Import")
                st.dataframe(
                    [
                        {
                            "Date": r["date"],
                            "Description": r["description"],
                            "Amount": f"${float(r['amount']):,.2f}",
                            "Predicted Category": r.get("category", "General"),
                            "Type": r["type"].upper()
                        }
                        for r in p["valid_transactions"]
                    ],
                    use_container_width=True
                )

                if st.button("Commit & Import Valid Transactions", type="primary"):
                    try:
                        commit_res = client.commit_csv_import(token, p["valid_transactions"])
                        st.success(f"Successfully imported {commit_res['committed_count']} transactions!")
                        del st.session_state["csv_preview_cache"]
                        st.rerun()
                    except Exception as e:
                        st.error(f"Commit failed: {e}")

    with tab_export:
        st.markdown("### Export Financial Data")
        st.markdown("Download your complete personal transaction ledger in standardized CSV format for external backup or spreadsheet analysis.")
        
        if st.button("Generate CSV Export"):
            try:
                csv_data = client.export_csv(token)
                st.download_button(
                    label="Download CSV Ledger",
                    data=csv_data,
                    file_name=f"wealthos_transactions_{date.today().isoformat()}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Export failed: {e}")
