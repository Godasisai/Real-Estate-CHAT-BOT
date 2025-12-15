# ============================================
# REAL ESTATE CHATBOT - STREAMLIT UI
# ============================================

import streamlit as st
from model import RealEstateModel

st.set_page_config(
    page_title="Real Estate India Chatbot",
    page_icon="🏠",
    layout="wide"
)

# Load model
if "model" not in st.session_state:
    st.session_state.model = RealEstateModel()
    st.session_state.history = []

st.markdown("<h1 style='text-align:center;'>🏠 Real Estate India Chatbot</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>AI-Powered Property Search Across India</p>", unsafe_allow_html=True)

left, right = st.columns(2)

# ---------------- CHAT ----------------
with left:
    for msg in st.session_state.history:
        if msg["role"] == "user":
            st.markdown(f"**🧑 You:** {msg['text']}")
        else:
            st.markdown(f"**🤖 Bot:** {msg['text']}")

    query = st.text_input("Ask about properties", placeholder="Apartments in Hyderabad")

    if st.button("Search") and query:
        st.session_state.history.append({"role":"user","text":query})

        result = st.session_state.model.process_query(query)
        projects = result["projects"]

        if not projects:
            reply = "❌ No exact match found. Try another city or property type."
        else:
            reply = f"✅ Found {len(projects)} matching properties."

        st.session_state.history.append({"role":"bot","text":reply})
        st.session_state.results = projects
        st.session_state.query = query
        st.rerun()

# ---------------- RESULTS ----------------
with right:
    st.markdown("## 🏢 Property Results")

    if "results" in st.session_state:
        query_city = st.session_state.query.lower()

        for p in st.session_state.results:
            is_match = p["city"].lower() in query_city

            title = f"{p['name']} – {p['city']}"
            if is_match:
                title = f"⭐ {title} ⭐"

            with st.expander(title, expanded=is_match):
                st.write(f"📍 Location: {p['location']}")
                st.write(f"🏠 Type: {p['property_type']}")
                st.write(f"🛏 Bedrooms: {p['bedrooms']}")
                st.write(f"💰 Price: ₹{p['price_min']/1e7:.1f}Cr - ₹{p['price_max']/1e7:.1f}Cr")
                st.write(f"🏗 Developer: {p['developer']}")
                st.write(f"✨ Amenities: {p['amenities']}")
                st.write(f"📝 {p['description']}")
    else:
        st.info("Ask a question to see results")
