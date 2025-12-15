# ============================================
# REAL ESTATE CHATBOT - FINAL UI WITH BACKGROUND
# ============================================

import streamlit as st
from model import RealEstateModel

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Real Estate India Chatbot",
    page_icon="🏠",
    layout="wide"
)

# ---------------- BACKGROUND + CSS ----------------
st.markdown("""
<style>
.stApp {
    background-image: url("https://images.unsplash.com/photo-1560518883-ce09059eeffa");
    background-size: cover;
    background-attachment: fixed;
}

.main-overlay {
    background: rgba(0,0,0,0.6);
    padding: 20px;
    border-radius: 15px;
}

.chat-box {
    background: rgba(255,255,255,0.95);
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 10px;
}

.result-box {
    background: rgba(255,255,255,0.97);
    border-radius: 12px;
    padding: 10px;
}

.highlight {
    border-left: 6px solid #2ecc71;
    background: #eafff2;
}

button {
    border-radius: 20px !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOAD MODEL ----------------
if "model" not in st.session_state:
    st.session_state.model = RealEstateModel()
    st.session_state.history = []
    st.session_state.results = []
    st.session_state.query = ""

# ---------------- HEADER ----------------
st.markdown("""
<div class="main-overlay">
<h1 style="text-align:center;color:white;">🏠 Real Estate India Chatbot</h1>
<p style="text-align:center;color:#ddd;">AI-Powered Property Search Across India</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------- SUGGESTED QUERIES ----------------
SUGGESTED_QUERIES = [
    "Apartments in Hyderabad",
    "Luxury apartments in Mumbai",
    "Apartments in Bangalore",
    "Villas in Goa",
    "Properties in Mumbai"
]

st.markdown("<div class='main-overlay'>", unsafe_allow_html=True)
st.markdown("### 🔍 Suggested Queries", unsafe_allow_html=True)
cols = st.columns(len(SUGGESTED_QUERIES))
for i, q in enumerate(SUGGESTED_QUERIES):
    if cols[i].button(q):
        st.session_state.query = q
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------- LAYOUT ----------------
left, right = st.columns(2)

# ---------------- CHAT SECTION ----------------
with left:
    st.markdown("<div class='main-overlay'>", unsafe_allow_html=True)
    st.markdown("### 💬 Chat")

    for msg in st.session_state.history:
        st.markdown(
            f"<div class='chat-box'><b>{'🧑 You' if msg['role']=='user' else '🤖 Bot'}:</b> {msg['text']}</div>",
            unsafe_allow_html=True
        )

    query = st.text_input(
        "Ask about properties",
        value=st.session_state.query,
        placeholder="Apartments in Hyderabad"
    )

    if st.button("🔍 Search") and query:
        st.session_state.history.append({"role": "user", "text": query})

        result = st.session_state.model.process_query(query)
        count = result["count"]

        if count == 0:
            reply = "❌ No matching properties found."
        else:
            reply = f"✅ Found {count} matching properties."

        st.session_state.history.append({"role": "bot", "text": reply})
        st.session_state.results = result["projects"]
        st.session_state.query = query
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- RESULTS SECTION ----------------
with right:
    st.markdown("<div class='main-overlay'>", unsafe_allow_html=True)
    st.markdown("### 🏢 Property Results")

    if st.session_state.results:
        q_city = st.session_state.query.lower()

        for p in st.session_state.results:
            is_match = p["city"].lower() in q_city
            box_class = "result-box highlight" if is_match else "result-box"

            st.markdown(f"<div class='{box_class}'>", unsafe_allow_html=True)
            st.markdown(f"### {p['name']} – {p['city']}")
            st.write(f"📍 Location: {p['location']}")
            st.write(f"🏠 Type: {p['property_type']}")
            st.write(f"🛏 Bedrooms: {p['bedrooms']}")
            st.write(f"💰 Price: ₹{p['price_min']/1e7:.1f}Cr – ₹{p['price_max']/1e7:.1f}Cr")
            st.write(f"🏗 Developer: {p['developer']}")
            st.write(f"✨ Amenities: {p['amenities']}")
            st.write(p["description"])
            st.markdown("</div><br>", unsafe_allow_html=True)

    else:
        st.info("Use suggested queries or search to see results")

    st.markdown("</div>", unsafe_allow_html=True)
