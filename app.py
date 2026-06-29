import streamlit as st
import pandas as pd
import numpy as np  # 🚨 Pandas wala np error eka hadanna meka thama hari kramaya
import cv2
from pyzbar.pyzbar import decode
import datetime

# Page Configuration
st.set_page_config(page_title="Kade Management System", layout="wide")
st.title("🏪 අපේ කඩේ - කළමනාකරණ පද්ධතිය")

# Dummy Product Data (QR code scan කරාම මිල ගණන් ගන්නා දත්ත පද්ධතිය)
PRODUCT_DB = {
    "12345": {"name": "සීනි 1kg", "price": 280.00},
    "67890": {"name": "හාල් 1kg", "price": 220.00},
    "55555": {"name": "තේ කොළ 100g", "price": 150.00},
}

# Session State දත්ත සුරැකීමට ඇති memory එක සකස් කිරීම
if 'bill_items' not in st.session_state:
    st.session_state.bill_items = []
if 'transactions' not in st.session_state:
    st.session_state.transactions = pd.DataFrame(columns=["Date", "Type", "Description", "Amount"])

# --- TABS සකස් කිරීම ---
tab1, tab2, tab3 = st.tabs(["🧾 บිල්පත් සකස් කිරීම (Billing)", "💸 වියදම් ඇතුළත් කිරීම", "📊 මාසික වාර්තා (Reports)"])

# --- TAB 1: BILLING & QR SCANNER ---
with tab1:
    st.subheader("QR කේතය ස්කෑන් කර බිල සාදන්න")
    
    # කැමරාවෙන් QR කියවීම
    img_file_buffer = st.camera_input("QR කේතය ස්කෑන් කිරීමට කැමරාව ක්‍රියාත්මක කරන්න")
    
    if img_file_buffer is not None:
        bytes_data = img_file_buffer.getvalue()
        # 🚨 මෙතන pd.np වෙනුවට np කියලා නිවැරදි කරලා තියෙන්නේ
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        
        detected_barcodes = decode(cv2_img)
        if detected_barcodes:
            for barcode in detected_barcodes:
                qr_data = barcode.data.decode('utf-8')
                if qr_data in PRODUCT_DB:
                    item = PRODUCT_DB[qr_data]
                    st.session_state.bill_items.append({
                        "භාණ්ඩය": item["name"],
                        "මිල (රු.)": item["price"]
                    })
                    st.success(f"✅ {item['name']} - රු.{item['price']} බිලට එකතු කලා!")
                else:
                    st.error("❌ මෙම QR කේතය පද්ධතියේ නැත.")
        else:
            st.warning("QR කේතයක් හඳුනාගත නොහැකි විය. කරුණාකර නැවත උත්සාහ කරන්න.")

    st.markdown("---")
    st.write("Manual භාණ්ඩ ඇතුළත් කිරීම:")
    
    # Form එකක් භාවිතා කර ඇති නිසා බටන් එක එබූ සැනින් කොටු සියල්ල auto හිස් වේ
    with st.form("manual_clear_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            manual_name = st.text_input("භාණ්ඩයේ නම")
        with col2:
            manual_price = st.number_input("මිල (රු.)", min_value=0.0, step=10.0)
            
        add_button = st.form_submit_button("බිලට එකතු කරන්න")
        
        if add_button:
            if manual_name and manual_price > 0:
                st.session_state.bill_items.append({"භාණ්ඩය": manual_name, "මිල (රු.)": manual_price})
                st.rerun()

    # වත්මන් බිල පෙන්වීම
    if st.session_state.bill_items:
        st.markdown("### වත්මන් බිල්පත")
        df_bill = pd.DataFrame(st.session_state.bill_items)
        st.table(df_bill)
        
        total_amount = df_bill["මිල (රු.)"].sum()
        st.markdown(f"### **මුළු එකතුව: රු. {total_amount:,.2f}**")
        
        if st.button("බිල තහවුරු කර සුරකින්න (Confirm Bill)"):
            new_row = pd.DataFrame([{
                "Date": datetime.date.today().strftime("%Y-%m"),
                "Type": "Income (ආදායම)",
                "Description": f"බිල්පත් අලෙවිය ({len(df_bill)} items)",
                "Amount": total_amount
            }])
            st.session_state.transactions = pd.concat([st.session_state.transactions, new_row], ignore_index=True)
            st.session_state.bill_items = [] 
            st.success("🎉 බිල සාර්ථකව සුරැකුණා!")
            st.rerun()
            
        if st.button("බිල හිස් කරන්න"):
            st.session_state.bill_items = []
            st.rerun()

# --- TAB 2: EXPENSES ---
with tab2:
    st.subheader("කඩේ මාසික වියදම් ඇතුළත් කරන්න")
    with st.form("expense_form", clear_on_submit=True):
        exp_desc = st.text_input("වියදම් විස්තරය (උදා: ලයිට් බිල, බඩු ගෙන ඒම)")
        exp_amount = st.number_input("වියදම් මුදල (රු.)", min_value=0.0, step=100.0)
        submitted = st.form_submit_button("වියදම ඇතුළත් කරන්න")
        
        if submitted and exp_desc and exp_amount > 0:
            new_exp = pd.DataFrame([{
                "Date": datetime.date.today().strftime("%Y-%m"),
                "Type": "Expense (වියදම)",
                "Description": exp_desc,
                "Amount": exp_amount
            }])
            st.session_state.transactions = pd.concat([st.session_state.transactions, new_exp], ignore_index=True)
            st.success("💰 වියදම ඇතුළත් කලා!")

# --- TAB 3: REPORTS & PRINT ---
with tab3:
    st.subheader("📊 මාසික ආදායම්, වියදම් සහ ලාභය")
    
    if not st.session_state.transactions.empty:
        months = st.session_state.transactions["Date"].unique()
        selected_month = st.selectbox("මාසය තෝරන්න", months)
        
        monthly_df = st.session_state.transactions[st.session_state.transactions["Date"] == selected_month]
        st.dataframe(monthly_df, use_container_width=True)
        
        total_inc = monthly_df[monthly_df["Type"] == "Income (ආදායම)"]["Amount"].sum()
        total_exp = monthly_df[monthly_df["Type"] == "Expense (වියදම)"]["Amount"].sum()
        profit = total_inc - total_exp
        
        c1, c2, c3 = st.columns(3)
        c1.metric("මුළු ආදායම", f"රු. {total_inc:,.2f}")
        c2.metric("මුළු වියදම", f"රු. {total_exp:,.2f}")
        c3.metric("ශුද්ධ ලාභය", f"රු. {profit:,.2f}", delta=float(profit))
        
        st.markdown("---")
        @st.cache_data
        def convert_df(df):
            return df.to_csv().encode('utf-8')
            
        csv = convert_df(monthly_df)
        st.download_button(
            label="📄 මෙම මාසික වාර්තාව (Print/Download) බාගත කරගන්න",
            data=csv,
            file_name=f'Kade_Report_{selected_month}.csv',
            mime='text/csv',
        )
    else:
        st.info("තවමත් කිසිදු ගනුදෙනුවක් සිදු කර නොමැත.")