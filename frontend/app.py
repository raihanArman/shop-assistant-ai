import streamlit as st
import requests

st.set_page_config(page_title="Shop Assistant", layout="wide")

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Sidebar chat ui
st.sidebar.title("Chat with Shop Assistant")
st.sidebar.markdown("Ask questions about products, prices and more!")

# display full chat history in sidebar
for msg in st.session_state.chat_history:
    if msg.startswith("User:"):
        st.sidebar.markdown(f"**{msg}**")
    else:
        st.sidebar.markdown(f"*{msg}*")

# user input
with st.sidebar:
    user_query=st.text_input("Type your message here...", key="user_query")
    if st.button("Send"):
        if user_query.strip():
            try:
                res=requests.post(
                    "http://127.0.0.1:8000/chat",
                    json={"query":user_query,"history":st.session_state.chat_history}
                )
                data=res.json()

                st.session_state.chat_history=data["history"]
                st.rerun()
            except Exception as e:
                st.error(f"Error {e}")    


# main page
st.title("Shop Assistant")
st.markdown("<hr>", unsafe_allow_html=True)

# fetch products from backend
try:
    response = requests.get("http://localhost:8000/products")
    products = response.json()

    if not products:
        st.warning("No products found.")
    else:
        # Get filter values
        brands = sorted(set(p["ProductBrand"] for p in products if p["ProductBrand"]))
        genders = sorted(set(p["Gender"] for p in products if p["Gender"]))

        st.subheader("🔍 Filter Products")
        col1, col2, col3 = st.columns(3)

        with col1:
            selected_brand = st.selectbox("Brand", ["All"] + brands)
        with col2:
            selected_gender = st.selectbox("Gender", ["All"] + genders)
        with col3:
            sort_order = st.selectbox("Sort by Price", ["Default", "Low to High", "High to Low"])

        # Apply filters
        filtered = products
        if selected_brand != "All":
            filtered = [p for p in filtered if p["ProductBrand"] == selected_brand]
        if selected_gender != "All":
            filtered = [p for p in filtered if p["Gender"] == selected_gender]

        # Apply sorting
        if sort_order == "Low to High":
            filtered = sorted(filtered, key=lambda x: float(x["Price"]))
        elif sort_order == "High to Low":
            filtered = sorted(filtered, key=lambda x: float(x["Price"]), reverse=True)

        # ---- Custom CSS for Styled Product Cards ----
        # ... [everything above remains the same]

        # ---- Custom CSS for Transparent Product Cards ----
        st.markdown("""
            <style>
            .product-card {
                background-color: rgba(255, 255, 255, 0.05);  /* semi-transparent */
                border: 1px solid #ccc;
                border-radius: 16px;
                padding: 20px;
                margin-bottom: 20px;
                backdrop-filter: blur(8px);  /* glass effect */
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                transition: 0.3s ease-in-out;
            }
            .product-card:hover {
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
                transform: scale(1.01);
            }
            .product-title {
                font-size: 20px;
                font-weight: bold;
                margin-bottom: 8px;
                color: #e0e0e0;
            }
            .product-meta {
                font-size: 14px;
                color: #b0bec5;
                margin-bottom: 4px;
            }
            .product-desc {
                font-size: 13px;
                color: #cfd8dc;
                margin-top: 10px;
            }
            </style>
        """, unsafe_allow_html=True)

        # Display products in two columns
        cols = st.columns(2)
        for idx, product in enumerate(filtered):
            with cols[idx % 2]:
                st.markdown(f"""
                    <div class="product-card">
                        <div class="product-title">{product['ProductName']}</div>
                        <div class="product-meta"><b>Brand:</b> {product['ProductBrand']} &nbsp; | &nbsp; <b>Gender:</b> {product['Gender']}</div>
                        <div class="product-meta"><b>Price:</b> ₹{product['Price']} &nbsp; | &nbsp; <b>Color:</b> {product['PrimaryColor']}</div>
                        <div class="product-desc">{product['Description']}</div>
                    </div>
                """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"⚠️ Could not fetch products: {e}")