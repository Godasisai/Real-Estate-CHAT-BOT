# ============================================
# REAL ESTATE CHATBOT - FINAL UI
# ============================================

import streamlit as st
from model import RealEstateModel

st.set_page_config("Real Estate India Chatbot", "🏠", layout="wide")

# Load model
if "model" not in st.session_state:
    st.session_state.model = RealEstateModel()
    st.session_state.history = []
    st.session_state.results = []

# ---------------- HEADER ----------------
st.markdown("<h1 style='text-align:center;'>🏠 Real Estate India Chatbot</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>AI-Powered Property Search Across India</p>", unsafe_allow_html=True)

# ---------------- SUGGESTIONS ----------------
SUGGESTED_QUERIES = [
    "Apartments in Hyderabad",
    "Luxury apartments in Mumbai",
    "Apartments in Bangalore",
    "Villas in Goa",
    "Properties in Mumbai",
]

st.markdown("### 🔍 Suggested Queries")

cols = st.columns(len(SUGGESTED_QUERIES))
for i, q in enumerate(SUGGESTED_QUERIES):
    if cols[i].button(q):
        st.session_state.query = q

# ---------------- LAYOUT ----------------
left, right = st.columns(2)

# ---------------- CHAT ----------------
with left:
    for msg in st.session_state.history:
        role = "🧑 You" if msg["role"] == "user" else "🤖 Bot"
        st.markdown(f"**{role}:** {msg['text']}")

    query = st.text_input(
        "Ask about properties",
        value=st.session_state.get("query", ""),
        placeholder="Apartments in Hyderabad"
    )

    if st.button("Search") and query:
        st.session_state.history.append({"role":"user","text":query})
        result = st.session_state.model.process_query(query)

        if result["count"] == 0:
            reply = "❌ No results found. Try another city or property type."
        else:
            reply = f"✅ Found {result['count']} matching properties."

        st.session_state.history.append({"role":"bot","text":reply})
        st.session_state.results = result["projects"]
        st.session_state.query = query
        st.rerun()

# ---------------- RESULTS ----------------
with right:
    st.markdown("## 🏢 Property Results")

    if st.session_state.results:
        query_city = st.session_state.query.lower()

        for p in st.session_state.results:
            highlight = p["city"].lower() in query_city
            title = f"{p['name']} – {p['city']}"

            if highlight:
                title = f"⭐ {title} ⭐"

            with st.expander(title, expanded=highlight):
                st.write(f"📍 Location: {p['location']}")
                st.write(f"🏠 Type: {p['property_type']}")
                st.write(f"🛏 Bedrooms: {p['bedrooms']}")
                st.write(f"💰 Price: ₹{p['price_min']/1e7:.1f}Cr - ₹{p['price_max']/1e7:.1f}Cr")
                st.write(f"🏗 Developer: {p['developer']}")
                st.write(f"✨ Amenities: {p['amenities']}")
                st.write(f"📝 {p['description']}")
    else:
        st.info("Use suggested queries or type your own to see results")
