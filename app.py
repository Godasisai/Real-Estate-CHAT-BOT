# ============================================
# REAL ESTATE INDIA CHATBOT - FINAL WORKING
# ============================================

import streamlit as st
from model import RealEstateModel
import base64
import os
import random

# -------------------------------------------------
# NORMALIZE PROJECT DATA (CRITICAL FIX)
# -------------------------------------------------
def normalize_projects(projects):
    normalized = []
    for p in projects:
        normalized.append({
            "name": str(p.get("name", "Unknown Project")),
            "city": str(p.get("city", "")),
            "property_type": str(p.get("property_type", p.get("type", ""))),
            "price_min": p.get("price_min", p.get("price", 0)) or 0,
            "price_max": p.get("price_max", p.get("price", 0)) or 0,
            "location": str(p.get("location", "")),
            "bedrooms": str(p.get("bedrooms", "")),
            "developer": str(p.get("developer", "")),
            "amenities": str(p.get("amenities", "")),
            "possession_date": str(p.get("possession_date", "")),
            "description": str(p.get("description", ""))
        })
    return normalized


# -------------------------------------------------
# SMART FILTERING (SOFT MATCHING)
# -------------------------------------------------
def filter_projects_by_query(projects, query):
    if not projects:
        return []

    projects = normalize_projects(projects)
    q = query.lower()
    results = []

    cities = [
        "mumbai","bangalore","hyderabad","delhi","goa","pune",
        "chennai","kolkata","ahmedabad","jaipur","kochi",
        "vizag","vijayawada","tirupati","warangal","guntur","nellore"
    ]

    for p in projects:
        score = 0
        city = p["city"].lower()
        ptype = p["property_type"].lower()
        name = p["name"].lower()

        # City matching
        for c in cities:
            if c in q and c in city:
                score += 3

        # Property type
        if "villa" in q and "villa" in ptype:
            score += 2
        if "apartment" in q and ("apartment" in ptype or "flat" in ptype):
            score += 2
        if "house" in q and "house" in ptype:
            score += 2

        # Keyword relevance
        for word in q.split():
            if len(word) > 3 and (word in name or word in ptype):
                score += 1

        if score > 0:
            p["__score"] = score
            results.append(p)

    # Sort best matches first
    results = sorted(results, key=lambda x: x["__score"], reverse=True)

    # NEVER return empty
    return results if results else projects[:5]


# -------------------------------------------------
# BOT RESPONSE
# -------------------------------------------------
def generate_bot_response(projects, query):
    if not projects:
        return "❌ No exact match found. Showing best available properties."

    return f"🏠 Found **{len(projects)} properties** matching: *{query}*"


# -------------------------------------------------
# BACKGROUND IMAGE (OPTIONAL)
# -------------------------------------------------
def get_base64_image(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

bg = get_base64_image("background.jpg")

# -------------------------------------------------
# STREAMLIT CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="🏠 Real Estate India Chatbot",
    page_icon="🏠",
    layout="wide"
)

# -------------------------------------------------
# STYLES
# -------------------------------------------------
if bg:
    st.markdown(f"""
    <style>
    .stApp {{
        background: url("data:image/jpg;base64,{bg}");
        background-size: cover;
    }}
    </style>
    """, unsafe_allow_html=True)

st.markdown("""
<style>
.user-msg {
    background: #6a5acd;
    color: white;
    padding: 12px;
    border-radius: 15px;
    margin: 8px 0;
    text-align: right;
}
.bot-msg {
    background: white;
    padding: 12px;
    border-radius: 15px;
    margin: 8px 0;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# LOAD MODEL
# -------------------------------------------------
if "model" not in st.session_state:
    with st.spinner("Loading AI model..."):
        st.session_state.model = RealEstateModel()
        st.session_state.chat = []

# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.title("🏠 Real Estate India Chatbot")
st.caption("AI-Powered Property Search Across India")

left, right = st.columns(2)

# -------------------------------------------------
# CHAT SECTION
# -------------------------------------------------
with left:
    if not st.session_state.chat:
        st.markdown("<div class='bot-msg'>👋 Ask me about properties anywhere in India!</div>", unsafe_allow_html=True)

    for msg in st.session_state.chat:
        css = "user-msg" if msg["role"] == "user" else "bot-msg"
        st.markdown(f"<div class='{css}'>{msg['text']}</div>", unsafe_allow_html=True)

    user_query = st.text_input(
        "Ask something",
        placeholder="e.g., Apartments in Hyderabad",
        label_visibility="collapsed"
    )

    if st.button("🔍 Search") and user_query:
        st.session_state.chat.append({"role": "user", "text": user_query})

        with st.spinner("Searching properties..."):
            result = st.session_state.model.process_query(user_query)
            filtered = filter_projects_by_query(result["projects"], user_query)

            bot_reply = generate_bot_response(filtered, user_query)
            st.session_state.chat.append({"role": "bot", "text": bot_reply})
            st.session_state.results = filtered

        st.rerun()

# -------------------------------------------------
# RESULTS SECTION
# -------------------------------------------------
with right:
    st.subheader("🏢 Property Results")

    if "results" in st.session_state:
        for p in st.session_state.results:
            with st.expander(f"{p['name']} – {p['city']}"):
                st.write(f"**Type:** {p['property_type']}")
                st.write(f"**Location:** {p['location']}")
                st.write(f"**Bedrooms:** {p['bedrooms']}")
                st.write(f"**Developer:** {p['developer']}")
                st.write(f"**Amenities:** {p['amenities']}")
                st.write(f"**Possession:** {p['possession_date']}")
                st.write(f"**Description:** {p['description']}")
    else:
        st.info("💬 Ask a question to see property results.")

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
with st.sidebar:
    st.subheader("💡 Quick Queries")

    examples = [
        "Apartments in Hyderabad",
        "Villas in Bangalore",
        "Properties under 2 crores",
        "Luxury homes in Goa",
        "Properties in Mumbai"
    ]

    for ex in examples:
        if st.button(ex):
            st.session_state.chat.append({"role": "user", "text": ex})
            result = st.session_state.model.process_query(ex)
            filtered = filter_projects_by_query(result["projects"], ex)
            st.session_state.chat.append({
                "role": "bot",
                "text": generate_bot_response(filtered, ex)
            })
            st.session_state.results = filtered
            st.rerun()

    if st.button("🗑 Clear Chat"):
        st.session_state.chat = []
        st.session_state.pop("results", None)
        st.rerun()

    st.caption("🇮🇳 Pan-India | AI Powered")
