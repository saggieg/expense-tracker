import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Shared Expense Tracker", page_icon="💰")
st.title("💰 Our Shared Ledger")

# Create a connection object
conn = st.connection("gsheets", type=GSheetsConnection)

# Read existing data
df = conn.read(worksheet="Sheet1", ttl="0")
# --- INPUT FORM ---
with st.expander("➕ Add New Expense"):
    with st.form("expense_form", clear_on_submit=True):
        item = st.text_input("What did you buy?")
        amount = st.number_input("Amount ($)", min_value=0.0, step=0.01)
        paid_by = st.selectbox("Who paid?", ["Partner A", "Partner B"])
        submit = st.form_submit_button("Save to Google Sheets")
        
        if submit and item and amount > 0:
            # Create new row
            new_row = pd.DataFrame([{
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Item": item,
                "Amount": amount,
                "Paid By": paid_by,
                "Split": "50/50"
            }])
            
            # Add to existing data and update Google Sheet
            updated_df = pd.concat([df, new_row], ignore_index=True)
            conn.update(data=updated_df)
            st.success("Expense saved!")
            st.rerun()

# --- CALCULATIONS ---
if not df.empty:
    a_total = df[df["Paid By"] == "Partner A"]["Amount"].sum()
    b_total = df[df["Paid By"] == "Partner B"]["Amount"].sum()
    
    st.metric("Partner A Total", f"${a_total:.2f}")
    st.metric("Partner B Total", f"${b_total:.2f}")
    
    # Settle up logic
    diff = (a_total - b_total) / 2
    if diff > 0:
        st.info(f"Partner B owes Partner A: **${abs(diff):.2f}**")
    elif diff < 0:
        st.info(f"Partner A owes Partner B: **${abs(diff):.2f}**")

    st.subheader("Transaction History")
    st.dataframe(df.sort_index(ascending=False))
