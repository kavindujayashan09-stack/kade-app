import streamlit as nn
import cv2
import pandas as pd
from pyzbar.pyzbar import decode

# පිටුවේ සැකසුම් (Page Layout)
st.set_page_config(page_title="Kade Management System", layout="wide")
st.title("🛒 කඩේ කළමනාකරණ පද්ධතිය (Auto-Billing)")

# 1. බඩු බාහිරාදියේ මිල ලැයිස්තුව (Product Database)
# ඔයාට ඕන බාර්කෝඩ් අංක සහ මිල ගණන් මෙතනට ඇතුළත් කරන්න
PRODUCTS = {
    "123456789": {"name": "සීනි 1kg", "price": 240.00},
    "987654321": {"name": "පරිප්පු 1kg", "price": 320.00},
    "694123456": {"name": "සබන් සබන්", "price": 150.00},
}

# 2. ඇප් එකේ මෙමරිය (Session State) සක්‍රීය කිරීම
if "bill_items" not in st.session_state:
    st.session_state.bill_items = []  # බිලට එකතු වන බඩු ලැයිස්තුව
if "last_scanned" not in st.session_state:
    st.session_state.last_scanned = None  # අන්තිමට ස්කෑන් කරපු බාර්කෝඩ් එක

# පිටුව කොටස් දෙකකට බෙදීම (කැමරාව සහ බිල)
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📷 Barcode Scanner (Live)")
    
    # කැමරාව ඔන් කිරීම (Streamlit Cloud එකේ වැඩ කිරීමට opencv-python-headless සමඟ)
    img_file_buffer = st.camera_input("බාර්කෝඩ් එක කැමරාවට අල්ලන්න")

    if img_file_buffer is not None:
        # පින්තූරය OpenCV ආකෘතියට හැරවීම
        bytes_data = img_file_buffer.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        
        # බාර්කෝඩ් කියවීම
        barcodes = decode(cv2_img)
        
        for barcode in barcodes:
            barcode_data = barcode.data.decode("utf-8")
            
            # බාර්කෝඩ් එක අහුවුණු ගමන් සහ ඒක කලින් පාර ස්කෑන් කරපු එකම නෙවෙයි නම්
            if barcode_data and barcode_data != st.session_state.last_scanned:
                st.session_state.last_scanned = barcode_data  # මෙමරිය අප්ඩේට් කිරීම
                
                # බඩු ලැයිස්තුවේ බාර්කෝඩ් එක තියෙනවාදැයි බැලීම
                if barcode_data in PRODUCTS:
                    product = PRODUCTS[barcode_data]
                    
                    # ඔටෝමැටිකලි බිලට එකතු කිරීම
                    st.session_state.bill_items.append({
                        "Barcode": barcode_data,
                        "Item Name": product["name"],
                        "Price (Rs.)": product["price"]
                    })
                    st.toast(f"✅ {product['name']} බිලට එකතු කළා!", icon="🛒")
                    
                    # කිසිම බටන් එකක් නොඔබා පිටුව ක්ෂණිකව රී-රන් කිරීම
                    st.rerun()
                else:
                    st.error(f"❌ බාර්කෝඩ් එක හඳුනාගත නොහැක: {barcode_data}")

    # මෙමරිය රීසෙට් කිරීමට බටන් එකක් (ඊළඟ පාරිභෝගිකයා සඳහා)
    if st.button("🔄 අලුත් බිලක් (Reset Scanner)"):
        st.session_state.bill_items = []
        st.session_state.last_scanned = None
        st.rerun()

with col2:
    st.subheader("🧾 පාරිභෝගික බිල (Current Bill)")
    
    if st.session_state.bill_items:
        # බිලේ තියෙන බඩු ටික Table එකක් විදිහට පෙන්වීම
        df = pd.DataFrame(st.session_state.bill_items)
        st.table(df)
        
        # මුළු මුදල ගණනය කිරීම
        total_amount = sum(item["Price (Rs.)"] for item in st.session_state.bill_items)
        st.markdown(f"## 💰 **මුළු මුදල: රු. {total_amount:,.2f}**")
    else:
        st.info("තවමත් බඩු කිසිවක් බිලට එකතු කර නැත.")import streamlit as nn
import cv2
import pandas as pd
from pyzbar.pyzbar import decode

# පිටුවේ සැකසුම් (Page Layout)
st.set_page_config(page_title="Kade Management System", layout="wide")
st.title("🛒 කඩේ කළමනාකරණ පද්ධතිය (Auto-Billing)")

# 1. බඩු බාහිරාදියේ මිල ලැයිස්තුව (Product Database)
# ඔයාට ඕන බාර්කෝඩ් අංක සහ මිල ගණන් මෙතනට ඇතුළත් කරන්න
PRODUCTS = {
    "123456789": {"name": "සීනි 1kg", "price": 240.00},
    "987654321": {"name": "පරිප්පු 1kg", "price": 320.00},
    "694123456": {"name": "සබන් සබන්", "price": 150.00},
}

# 2. ඇප් එකේ මෙමරිය (Session State) සක්‍රීය කිරීම
if "bill_items" not in st.session_state:
    st.session_state.bill_items = []  # බිලට එකතු වන බඩු ලැයිස්තුව
if "last_scanned" not in st.session_state:
    st.session_state.last_scanned = None  # අන්තිමට ස්කෑන් කරපු බාර්කෝඩ් එක

# පිටුව කොටස් දෙකකට බෙදීම (කැමරාව සහ බිල)
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📷 Barcode Scanner (Live)")
    
    # කැමරාව ඔන් කිරීම (Streamlit Cloud එකේ වැඩ කිරීමට opencv-python-headless සමඟ)
    img_file_buffer = st.camera_input("බාර්කෝඩ් එක කැමරාවට අල්ලන්න")

    if img_file_buffer is not None:
        # පින්තූරය OpenCV ආකෘතියට හැරවීම
        bytes_data = img_file_buffer.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        
        # බාර්කෝඩ් කියවීම
        barcodes = decode(cv2_img)
        
        for barcode in barcodes:
            barcode_data = barcode.data.decode("utf-8")
            
            # බාර්කෝඩ් එක අහුවුණු ගමන් සහ ඒක කලින් පාර ස්කෑන් කරපු එකම නෙවෙයි නම්
            if barcode_data and barcode_data != st.session_state.last_scanned:
                st.session_state.last_scanned = barcode_data  # මෙමරිය අප්ඩේට් කිරීම
                
                # බඩු ලැයිස්තුවේ බාර්කෝඩ් එක තියෙනවාදැයි බැලීම
                if barcode_data in PRODUCTS:
                    product = PRODUCTS[barcode_data]
                    
                    # ඔටෝමැටිකලි බිලට එකතු කිරීම
                    st.session_state.bill_items.append({
                        "Barcode": barcode_data,
                        "Item Name": product["name"],
                        "Price (Rs.)": product["price"]
                    })
                    st.toast(f"✅ {product['name']} බිලට එකතු කළා!", icon="🛒")
                    
                    # කිසිම බටන් එකක් නොඔබා පිටුව ක්ෂණිකව රී-රන් කිරීම
                    st.rerun()
                else:
                    st.error(f"❌ බාර්කෝඩ් එක හඳුනාගත නොහැක: {barcode_data}")

    # මෙමරිය රීසෙට් කිරීමට බටන් එකක් (ඊළඟ පාරිභෝගිකයා සඳහා)
    if st.button("🔄 අලුත් බිලක් (Reset Scanner)"):
        st.session_state.bill_items = []
        st.session_state.last_scanned = None
        st.rerun()

with col2:
    st.subheader("🧾 පාරිභෝගික බිල (Current Bill)")
    
    if st.session_state.bill_items:
        # බිලේ තියෙන බඩු ටික Table එකක් විදිහට පෙන්වීම
        df = pd.DataFrame(st.session_state.bill_items)
        st.table(df)
        
        # මුළු මුදල ගණනය කිරීම
        total_amount = sum(item["Price (Rs.)"] for item in st.session_state.bill_items)
        st.markdown(f"## 💰 **මුළු මුදල: රු. {total_amount:,.2f}**")
    else:
        st.info("තවමත් බඩු කිසිවක් බිලට එකතු කර නැත.")
