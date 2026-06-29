import streamlit as st
import cv2
import pandas as pd
import numpy as np
from pyzbar.pyzbar import decode

# පිටුවේ සැකසුම් (Wide Layout එකක් දමා ලස්සන කිරීම)
st.set_page_config(page_title="Kade Complete System", layout="wide")
st.title("🏪 කඩේ කළමනාකරණ මහා පද්ධතිය (Auto-Capture Live)")

# --- 1. ඇප් එකේ මෙමරිය (Session State) සක්‍රීය කිරීම ---
if "products" not in st.session_state:
    st.session_state.products = {
        "123456789": {"name": "සීනි 1kg", "price": 240.00},
        "987654321": {"name": "පරිප්පු 1kg", "price": 320.00},
        "694123456": {"name": "සබන්", "price": 150.00},
    }

if "bill_items" not in st.session_state:
    st.session_state.bill_items = []
if "last_scanned" not in st.session_state:
    st.session_state.last_scanned = None
if "finance_records" not in st.session_state:
    st.session_state.finance_records = []

# --- 2. Tabs මඟින් පිටු වෙන් කිරීම ---
tab1, tab2, tab3 = st.tabs(["🛒 Auto Billing (ලයිව් ස්කෑනර් බිල)", "📦 Add Products (මිල ගණන් ඇතුළත් කිරීම)", "💰 Finance (ආදායම් / වියදම්)"])

# =========================================================
# TAB 1: ලයිව් වීඩියෝ බාර්කෝඩ් ස්කෑනර් එක සහ ඔටෝ බිල (Auto Capture)
# =========================================================
with tab1:
    st.header("📷 Live Video Barcode Scanner")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("කැමරා දර්ශනය (Live View)")
        
        # ලයිව් වීඩියෝ එකක් පෙන්වීමට හිස් Frame එකක් සකස් කිරීම
        FRAME_WINDOW = st.image([])
        
        # ෆෝන් එකේ හෝ ලැප් එකේ කැමරාව සක්‍රීය කිරීම
        # ලැප් එකේ නම් 0, සමහර ෆෝන් වල පසුපස කැමරාව සඳහා 1 හෝ 2 දීමට සිදුවේ
        cam = cv2.VideoCapture(0)
        
        # කැමරාව ඔන් වී ඇති තාක් ලූප් එකක් මඟින් ලයිව් වීඩියෝව ස්කෑන් කිරීම
        while cam.isOpened():
            ret, frame = cam.read()
            if not ret:
                st.write("කැමරාව සම්බන්ධ කරගත නොහැක.")
                break
                
            # වීඩියෝ Frame එක ස්ට්‍රීම් එකක් විදිහට ඇප් එකේ පෙන්වීම
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            FRAME_WINDOW.image(frame_rgb)
            
            # පින්තූරය ඇතුළේ බාර්කෝඩ් තියෙනවාදැයි ක්ෂණිකව පරික්ෂා කිරීම (Auto Capture)
            barcodes = decode(frame)
            
            scanned_this_frame = False
            for barcode in barcodes:
                barcode_data = barcode.data.decode("utf-8")
                
                # බාර්කෝඩ් එකක් හමු වී එය කලින් ස්කෑන් කළ එකම නොවේ නම්
                if barcode_data and barcode_data != st.session_state.last_scanned:
                    st.session_state.last_scanned = barcode_data
                    
                    # බඩු ලැයිස්තුවේ (Database) තිබේදැයි බැලීම
                    if barcode_data in st.session_state.products:
                        product = st.session_state.products[barcode_data]
                        st.session_state.bill_items.append({
                            "Barcode": barcode_data,
                            "Item Name": product["name"],
                            "Price (Rs.)": product["price"]
                        })
                        st.toast(f"✅ {product['name']} බිලට එකතු කළා!", icon="🛒")
                        scanned_this_frame = True
                    else:
                        st.sidebar.error(f"❌ නොදන්නා බාර්කෝඩ් අංකයකි: {barcode_data}")
            
            # අලුත් බඩුවක් ඇඩ් වුණොත් ලූප් එක නවතා පිටුව රීෆ්‍රෙෂ් (Rerun) කිරීම
            if scanned_this_frame:
                cam.release()
                st.rerun()
                break

        # ස්කෑනරය සහ බිල මුල සිට ආරම්භ කිරීමට බටන් එක
        if st.button("🔄 අලුත් බිලක් (Reset Scanner)", key="reset_b"):
            st.session_state.bill_items = []
            st.session_state.last_scanned = None
            st.rerun()

    with col2:
        st.subheader("🧾 වත්මන් බිල (Current Bill)")
        if st.session_state.bill_items:
            df_bill = pd.DataFrame(st.session_state.bill_items)
            st.table(df_bill)
            
            total_amount = sum(item["Price (Rs.)"] for item in st.session_state.bill_items)
            st.markdown(f"## 💰 **මුළු මුදල: රු. {total_amount:,.2f}**")
            
            # බිල අවසන් කර ආදායමට ඔටෝ එකතු කිරීම
            if st.button("💵 බිල අවසන් කර ආදායමට එකතු කරන්න", key="finish_b"):
                st.session_state.finance_records.append({
                    "Type": "ආදායම (Income)",
                    "Description": f"Barcode Bill - {len(st.session_state.bill_items)} items",
                    "Amount": total_amount
                })
                st.success("✅ බිලේ මුළු මුදල ආදායම් ගිණුමට එකතු කළා!")
                st.session_state.bill_items = []
                st.session_state.last_scanned = None
                st.rerun()
        else:
            st.info("තවමත් බඩු කිසිවක් බිලට එකතු කර නැත. බාර්කෝඩ් එක කැමරාවට කෙලින් අල්ලන්න.")

# =========================================================
# TAB 2: කඩේ බඩු වල බාර්කෝඩ් සහ මිල ගණන් ඇතුළත් කිරීම
# =========================================================
with tab2:
    st.header("📦 නව බඩු සහ මිල ගණන් පද්ධතියට ඇතුළත් කිරීම")
    
    with st.form("product_form", clear_on_submit=True):
        new_barcode = st.text_input("බාර්කෝඩ් අංකය (Barcode Number)")
        new_name = st.text_input("බඩුවේ නම (Product Name)")
        new_price = st.number_input("විකුණුම් මිල (Price Rs.)", min_value=0.0, step=5.0)
        
        submit_product = st.form_submit_with_button("💾 බඩුව පද්ධතියට සේဝ် කරන්න")
        
        if submit_product:
            if new_barcode and new_name and new_price > 0:
                st.session_state.products[new_barcode] = {"name": new_name, "price": new_price}
                st.success(f"🎉 {new_name} (Rs. {new_price}) සාර්ථකව පද්ධතියට ඇතුළත් කළා!")
                st.rerun()
            else:
                st.error("⚠️ කරුණාකර සියලුම විස්තර නිවැරදිව පුරවන්න!")

    # දැනට පද්ධතියේ ඇති බඩු ලැයිස්තුව
    st.subheader("📋 දැනට පද්ධතියේ ඇති බඩු ලැයිස්තුව")
    prod_list = []
    for code, info in st.session_state.products.items():
        prod_list.append({"Barcode": code, "Product Name": info["name"], "Price (Rs.)": info["price"]})
    st.dataframe(pd.DataFrame(prod_list), use_container_width=True)

# =========================================================
# TAB 3: මාසේ ආදායම් සහ වියදම් සේව් කරන තැන
# =========================================================
with tab3:
    st.header("💰 මාසික ආදායම් සහ වියදම් කළමනාකරණය")
    
    col_f1, col_f2 = st.columns([1, 2])
    
    with col_f1:
        st.subheader("📝 අලුත් ගණුදෙනුවක් ඇතුළත් කරන්න")
        rec_type = st.selectbox("වර්ගය", ["ආදායම (Income)", "වියදම (Expense)"])
        rec_desc = st.text_input("විස්තරය (උදා: කඩකුලී, විදුලි බිල, අත්පිට මුදල්)")
        rec_amount = st.number_input("මුදල (Amount Rs.)", min_value=0.0, step=10.0, key="finance_amt")
        
        if st.button("➕ ගිණුමට එකතු කරන්න"):
            if rec_desc and rec_amount > 0:
                st.session_state.finance_records.append({
                    "Type": rec_type,
                    "Description": rec_desc,
                    "Amount": rec_amount
                })
                st.success("✅ වාර්තාව සාර්ථකව සේව් වුණා!")
                st.rerun()
            else:
                st.error("⚠️ විස්තරය සහ මුදල නිවැරදිව ඇතුළත් කරන්න!")

    with col_f2:
        st.subheader("📊 මේ මාසයේ ගිණුම් වාර්තාව")
        if st.session_state.finance_records:
            df_finance = pd.DataFrame(st.session_state.finance_records)
            st.dataframe(df_finance, use_container_width=True)
            
            total_income = df_finance[df_finance["Type"] == "ආදායම (Income)"]["Amount"].sum()
            total_expense = df_finance[df_finance["Type"] == "වියදම (Expense)"]["Amount"].sum()
            net_profit = total_income - total_expense
            
            c1, c2, c3 = st.columns(3)
            c1.metric("🟢 මුළු ආදායම", f"රු. {total_income:,.2f}")
            c2.metric("🔴 මුළු වියදම", f"රු. {total_expense:,.2f}")
            if net_profit >= 0:
                c3.metric("📈 ශුද්ධ ලාභය", f"රු. {net_profit:,.2f}")
            else:
                c3.metric("📉 ශුද්ධ අලාභය", f"රු. {abs(net_profit):,.2f}")
        else:
            st.info("තවමත් කිසිදු ගණුදෙනුවක් ඇතුළත් කර නැත.")
