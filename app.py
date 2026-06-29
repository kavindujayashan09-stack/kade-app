import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# පිටුවේ සැකසුම්
st.set_page_config(page_title="Kade Complete System", layout="wide")
st.title("🏪 කඩේ කළමනාකරණ මහා පද්ධතිය (Live Phone Scanner)")

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

# --- URL එකෙන් එන බාර්කෝඩ් එක කියවා බිලට එකතු කිරීම ---
query_params = st.query_params
if "scanned_code" in query_params:
    code = query_params["scanned_code"]
    # ආයේ ආයේ ඇඩ් වීම වැළැක්වීමට URL එක ක්ලියර් කිරීම
    st.query_params.clear()
    
    if code in st.session_state.products:
        product = st.session_state.products[code]
        st.session_state.bill_items.append({
            "Barcode": code,
            "Item Name": product["name"],
            "Price (Rs.)": product["price"]
        })
        st.toast(f"✅ {product['name']} බිලට එකතු කළා!", icon="🛒")
        st.rerun()
    else:
        st.error(f"❌ නොදන්නා බාර්කෝඩ් එකකි: {code}")

# --- 2. Tabs මඟින් පිටු වෙන් කිරීම ---
tab1, tab2, tab3 = st.tabs(["🛒 Auto Billing (කැමරා ස්කෑනර් බිල)", "📦 Add Products (මිල ගණන් ඇතුළත් කිරීම)", "💰 Finance (ආදායම් / වියදම්)"])

# =========================================================
# TAB 1: ෆෝන් කැමරා ඔටෝ ස්කෑනරය
# =========================================================
with tab1:
    st.header("📷 Phone Camera Barcode Scanner")
    col1, col2 = col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("ලයිව් ස්කෑනරය")
        st.info("💡 පහත කැමරාවට බාර්කෝඩ් එක කෙලින් අල්ලන්න. එය ඉබේම (Auto Capture) කියවා ගනීවි.")
        
        # 🌐 HTML5 සහ HTML5-QRCode Library එක මඟින් බ්‍රවුසර් එක ඇතුළෙන්ම ලයිව් ස්කෑන් කරන කෑල්ල
        scanner_html = """
        <div id="reader" style="width:100%; max-width:500px; background:white; border-radius:10px;"></div>
        <script src="https://unpkg.com/html5-qrcode"></script>
        <script>
            function onScanSuccess(decodedText, decodedResult) {
                // බාර්කෝඩ් එකක් අහුවුණු ගමන් Streamlit එකේ URL එකට ඒක යවනවා
                window.parent.postMessage({
                    type: "streamlit:set_query_params",
                    queryParams: {scanned_code: decodedText}
                }, "*");
                
                // පිටුව රීෆ්‍රෙෂ් කරනවා ඩේටා ටික ගන්න
                setTimeout(() => {
                    window.parent.location.reload();
                }, 300);
            }
            
            let html5QrcodeScanner = new Html5QrcodeScanner(
                "reader", { fps: 15, qrbox: {width: 250, height: 150} }
            );
            html5QrcodeScanner.render(onScanSuccess);
        </script>
        """
        # HTML කෝඩ් එක ඇප් එක ඇතුළට දැමීම
        components.html(scanner_html, height=420)
        
        if st.button("🔄 අලුත් බිලක් (Reset Scanner)", key="reset_b"):
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
            st.info("තවමත් බඩු කිසිවක් බිලට එකතු කර නැත. බාර්කෝඩ් එක කැමරාවට අල්ලන්න.")

# =========================================================
# TAB 2: මිල ගණන් ඇතුළත් කිරීම
# =========================================================
with tab2:
    st.header("📦 නව බඩු පද්ධතියට ඇතුළත් කිරීම")
    
    with st.form("product_form", clear_on_submit=True):
        new_barcode = st.text_input("බාර්කෝඩ් අංකය (Barcode Number)")
        new_name = st.text_input("බඩුවේ නම (Product Name)")
        new_price = st.number_input("විකුණුම් මිල (Price Rs.)", min_value=0.0, step=5.0)
        
        submit_product = st.form_submit_button("💾 බඩුව පද්ධතියට සේව් කරන්න")
        
        if submit_product:
            if new_barcode and new_name and new_price > 0:
                st.session_state.products[new_barcode] = {"name": new_name, "price": new_price}
                st.success(f"🎉 {new_name} (Rs. {new_price}) සාර්ථකව ඇතුළත් කළා!")
                st.rerun()
            else:
                st.error("⚠️ කරුණාකර සියලුම විස්තර නිවැරදිව පුරවන්න!")

    st.subheader("📋 පද්ධතියේ ඇති බඩු ලැයිස්තුව")
    prod_list = []
    for code, info in st.session_state.products.items():
        prod_list.append({"Barcode": code, "Product Name": info["name"], "Price (Rs.)": info["price"]})
    st.dataframe(pd.DataFrame(prod_list), use_container_width=True)

# =========================================================
# TAB 3: ආදායම් සහ වියදම් සේව් කරන තැන
# =========================================================
with tab3:
    st.header("💰 මාසික ආදායම් සහ වියදම් කළමනාකරණය")
    
    col_f1, col_f2 = st.columns([1, 2])
    
    with col_f1:
        st.subheader("📝 අලුත් ගණුදෙනුවක් ඇතුළත් කරන්න")
        rec_type = st.selectbox("වර්ගය", ["ආදායම (Income)", "වියදම (Expense)"])
        rec_desc = st.text_input("විස්තරය (උදා: කඩකුලී, විදුලි බිල)")
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
