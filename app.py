import streamlit as st
import pandas as pd
from streamlit_embedcode import github_embed # මේක නැතත් කමක් නැහැ, අපි සරලවම input එක ගමු

# පිටුවේ සැකසුම්
st.set_page_config(page_title="Kade Complete System", layout="wide")
st.title("🏪 කඩේ කළමනාකරණ මහා පද්ධතිය")

# --- 1. ඇප් එකේ මෙමරිය (Session State) ---
if "products" not in st.session_state:
    st.session_state.products = {
        "123456789": {"name": "සීනි 1kg", "price": 240.00},
        "987654321": {"name": "පරිප්පු 1kg", "price": 320.00},
        "694123456": {"name": "සබන්", "price": 150.00},
    }

if "bill_items" not in st.session_state:
    st.session_state.bill_items = []
if "finance_records" not in st.session_state:
    st.session_state.finance_records = []

# --- 2. Tabs මඟින් පිටු වෙන් කිරීම ---
tab1, tab2, tab3 = st.tabs(["🛒 Auto Billing (ස්කෑනර් බිල)", "📦 Add Products (මිල ගණන් ඇතුළත් කිරීම)", "💰 Finance (ආදායම් / වියදම්)"])

# =========================================================
# TAB 1: බාර්කෝඩ් ස්කෑනර් එක සහ ඔටෝ බිල
# =========================================================
with tab1:
    st.header("🛒 Barcode Billing")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("බාර්කෝඩ් ඇතුළත් කිරීම")
        
        # 💡 ෆෝන් එකෙන් කරද්දී කැමරා ඇප් එකකින් බාර්කෝඩ් එක ස්කෑන් කරපු ගමන් 
        # හෝ බාර්කෝඩ් ස්කෑනර් ගන් එකකින් ගත්ත ගමන් ඔටෝ බිලට ඇඩ් වෙන සුපිරිම ක්‍රමය:
        def process_barcode():
            code = st.session_state.barcode_scanner_input.strip()
            if code:
                if code in st.session_state.products:
                    product = st.session_state.products[code]
                    st.session_state.bill_items.append({
                        "Barcode": code,
                        "Item Name": product["name"],
                        "Price (Rs.)": product["price"]
                    })
                    st.toast(f"✅ {product['name']} බිලට එකතු කළා!", icon="🛒")
                else:
                    st.error(f"❌ මේ බාර්කෝඩ් එක ඇතුළත් කර නැත: {code}")
                # ඊළඟ ස්කෑන් එකට බොක්ස් එක හිස් කිරීම
                st.session_state.barcode_scanner_input = ""

        st.text_input(
            "බාර්කෝඩ් අංකය මෙතනට ස්කෑන් කරන්න / ටයිප් කරන්න:", 
            key="barcode_scanner_input", 
            on_change=process_barcode
        )
        
        st.write("---")
        
        # 📸 කැමරාවෙන් කෙලින්ම ෆොටෝ එකක් අරන් ස්කෑන් කරන්න ඕනෙ නම් ඒකටත් විකල්පයක්:
        st.caption("📸 කැමරාවෙන් ස්කෑන් කිරීමට (ෆොටෝ එකක් ගන්න):")
        img_file_buffer = st.camera_input("Take a photo of barcode", key="cam_backup")
        
        if img_file_buffer is not None:
            import cv2
            import numpy as np
            from pyzbar.pyzbar import decode
            
            bytes_data = img_file_buffer.getvalue()
            cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
            barcodes = decode(cv2_img)
            
            if barcodes:
                for barcode in barcodes:
                    b_data = barcode.data.decode("utf-8")
                    if b_data in st.session_state.products:
                        product = st.session_state.products[b_data]
                        st.session_state.bill_items.append({
                            "Barcode": b_data,
                            "Item Name": product["name"],
                            "Price (Rs.)": product["price"]
                        })
                        st.toast(f"✅ {product['name']} බිලට එකතු කළා!", icon="🛒")
                        st.rerun()
                    else:
                        st.error(f"❌ නොදන්නා බාර්කෝඩ් එකකි: {b_data}")

        if st.button("🔄 අලුත් බිලක් (Reset)", key="reset_b"):
            st.session_state.bill_items = []
            st.rerun()

    with col2:
        st.subheader("🧾 වත්මන් බිල")
        if st.session_state.bill_items:
            df_bill = pd.DataFrame(st.session_state.bill_items)
            st.table(df_bill)
            
            total_amount = sum(item["Price (Rs.)"] for item in st.session_state.bill_items)
            st.markdown(f"## 💰 **මුළු මුදල: රු. {total_amount:,.2f}**")
            
            if st.button("💵 බිල අවසන් කර ආදායමට එකතු කරන්න", key="finish_b"):
                st.session_state.finance_records.append({
                    "Type": "ආදායම (Income)",
                    "Description": f"Barcode Bill - {len(st.session_state.bill_items)} items",
                    "Amount": total_amount
                })
                st.success("✅ බිලේ මුළු මුදල ආදායම් ගිණුමට එකතු කළා!")
                st.session_state.bill_items = []
                st.rerun()
        else:
            st.info("තවමත් බඩු කිසිවක් බිලට එකතු කර නැත.")

# =========================================================
# TAB 2: කඩේ බඩු වල බාර්කෝඩ් සහ මිල ගණන් ඇතුළත් කිරීම
# =========================================================
with tab2:
    st.header("📦 නව බඩු සහ මිල ගණන් පද්ධතියට ඇතුළත් කිරීම")
    
    with st.form("product_form", clear_on_submit=True):
        new_barcode = st.text_input("බාර්කෝඩ් අංකය (Barcode Number)")
        new_name = st.text_input("බඩුවේ නම (Product Name)")
        new_price = st.number_input("විකුණුම් මිල (Price Rs.)", min_value=0.0, step=5.0)
        
        submit_product = st.form_submit_button("💾 බඩුව පද්ධතියට සේව් කරන්න")
        
        if submit_product:
            if new_barcode and new_name and new_price > 0:
                st.session_state.products[new_barcode] = {"name": new_name, "price": new_price}
                st.success(f"🎉 {new_name} (Rs. {new_price}) සාර්ථකව පද්ධතියට ඇතුළත් කළා!")
                st.rerun()
            else:
                st.error("⚠️ කරුණාකර සියලුම විස්තර නිවැරදිව පුරවන්න!")

    st.subheader("📋 පද්ධතියේ ඇති බඩු ලැයිස්තුව")
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
        rec_desc = st.text_input("විස්තරය (උදා: කඩකුලී, විදුලි බිල, බඩු බෑග්)")
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
            st.info("තවමත් කිසිදු ගණුදෙනුවක් ඇතුළත් කර නැත.")import streamlit as st
import pandas as pd
from streamlit_embedcode import github_embed # මේක නැතත් කමක් නැහැ, අපි සරලවම input එක ගමු

# පිටුවේ සැකසුම්
st.set_page_config(page_title="Kade Complete System", layout="wide")
st.title("🏪 කඩේ කළමනාකරණ මහා පද්ධතිය")

# --- 1. ඇප් එකේ මෙමරිය (Session State) ---
if "products" not in st.session_state:
    st.session_state.products = {
        "123456789": {"name": "සීනි 1kg", "price": 240.00},
        "987654321": {"name": "පරිප්පු 1kg", "price": 320.00},
        "694123456": {"name": "සබන්", "price": 150.00},
    }

if "bill_items" not in st.session_state:
    st.session_state.bill_items = []
if "finance_records" not in st.session_state:
    st.session_state.finance_records = []

# --- 2. Tabs මඟින් පිටු වෙන් කිරීම ---
tab1, tab2, tab3 = st.tabs(["🛒 Auto Billing (ස්කෑනර් බිල)", "📦 Add Products (මිල ගණන් ඇතුළත් කිරීම)", "💰 Finance (ආදායම් / වියදම්)"])

# =========================================================
# TAB 1: බාර්කෝඩ් ස්කෑනර් එක සහ ඔටෝ බිල
# =========================================================
with tab1:
    st.header("🛒 Barcode Billing")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("බාර්කෝඩ් ඇතුළත් කිරීම")
        
        # 💡 ෆෝන් එකෙන් කරද්දී කැමරා ඇප් එකකින් බාර්කෝඩ් එක ස්කෑන් කරපු ගමන් 
        # හෝ බාර්කෝඩ් ස්කෑනර් ගන් එකකින් ගත්ත ගමන් ඔටෝ බිලට ඇඩ් වෙන සුපිරිම ක්‍රමය:
        def process_barcode():
            code = st.session_state.barcode_scanner_input.strip()
            if code:
                if code in st.session_state.products:
                    product = st.session_state.products[code]
                    st.session_state.bill_items.append({
                        "Barcode": code,
                        "Item Name": product["name"],
                        "Price (Rs.)": product["price"]
                    })
                    st.toast(f"✅ {product['name']} බිලට එකතු කළා!", icon="🛒")
                else:
                    st.error(f"❌ මේ බාර්කෝඩ් එක ඇතුළත් කර නැත: {code}")
                # ඊළඟ ස්කෑන් එකට බොක්ස් එක හිස් කිරීම
                st.session_state.barcode_scanner_input = ""

        st.text_input(
            "බාර්කෝඩ් අංකය මෙතනට ස්කෑන් කරන්න / ටයිප් කරන්න:", 
            key="barcode_scanner_input", 
            on_change=process_barcode
        )
        
        st.write("---")
        
        # 📸 කැමරාවෙන් කෙලින්ම ෆොටෝ එකක් අරන් ස්කෑන් කරන්න ඕනෙ නම් ඒකටත් විකල්පයක්:
        st.caption("📸 කැමරාවෙන් ස්කෑන් කිරීමට (ෆොටෝ එකක් ගන්න):")
        img_file_buffer = st.camera_input("Take a photo of barcode", key="cam_backup")
        
        if img_file_buffer is not None:
            import cv2
            import numpy as np
            from pyzbar.pyzbar import decode
            
            bytes_data = img_file_buffer.getvalue()
            cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
            barcodes = decode(cv2_img)
            
            if barcodes:
                for barcode in barcodes:
                    b_data = barcode.data.decode("utf-8")
                    if b_data in st.session_state.products:
                        product = st.session_state.products[b_data]
                        st.session_state.bill_items.append({
                            "Barcode": b_data,
                            "Item Name": product["name"],
                            "Price (Rs.)": product["price"]
                        })
                        st.toast(f"✅ {product['name']} බිලට එකතු කළා!", icon="🛒")
                        st.rerun()
                    else:
                        st.error(f"❌ නොදන්නා බාර්කෝඩ් එකකි: {b_data}")

        if st.button("🔄 අලුත් බිලක් (Reset)", key="reset_b"):
            st.session_state.bill_items = []
            st.rerun()

    with col2:
        st.subheader("🧾 වත්මන් බිල")
        if st.session_state.bill_items:
            df_bill = pd.DataFrame(st.session_state.bill_items)
            st.table(df_bill)
            
            total_amount = sum(item["Price (Rs.)"] for item in st.session_state.bill_items)
            st.markdown(f"## 💰 **මුළු මුදල: රු. {total_amount:,.2f}**")
            
            if st.button("💵 බිල අවසන් කර ආදායමට එකතු කරන්න", key="finish_b"):
                st.session_state.finance_records.append({
                    "Type": "ආදායම (Income)",
                    "Description": f"Barcode Bill - {len(st.session_state.bill_items)} items",
                    "Amount": total_amount
                })
                st.success("✅ බිලේ මුළු මුදල ආදායම් ගිණුමට එකතු කළා!")
                st.session_state.bill_items = []
                st.rerun()
        else:
            st.info("තවමත් බඩු කිසිවක් බිලට එකතු කර නැත.")

# =========================================================
# TAB 2: කඩේ බඩු වල බාර්කෝඩ් සහ මිල ගණන් ඇතුළත් කිරීම
# =========================================================
with tab2:
    st.header("📦 නව බඩු සහ මිල ගණන් පද්ධතියට ඇතුළත් කිරීම")
    
    with st.form("product_form", clear_on_submit=True):
        new_barcode = st.text_input("බාර්කෝඩ් අංකය (Barcode Number)")
        new_name = st.text_input("බඩුවේ නම (Product Name)")
        new_price = st.number_input("විකුණුම් මිල (Price Rs.)", min_value=0.0, step=5.0)
        
        submit_product = st.form_submit_button("💾 බඩුව පද්ධතියට සේව් කරන්න")
        
        if submit_product:
            if new_barcode and new_name and new_price > 0:
                st.session_state.products[new_barcode] = {"name": new_name, "price": new_price}
                st.success(f"🎉 {new_name} (Rs. {new_price}) සාර්ථකව පද්ධතියට ඇතුළත් කළා!")
                st.rerun()
            else:
                st.error("⚠️ කරුණාකර සියලුම විස්තර නිවැරදිව පුරවන්න!")

    st.subheader("📋 පද්ධතියේ ඇති බඩු ලැයිස්තුව")
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
        rec_desc = st.text_input("විස්තරය (උදා: කඩකුලී, විදුලි බිල, බඩු බෑග්)")
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
