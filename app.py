# ============================================
# REAL ESTATE WEB APP - Frontend
# File: app.py
# Streamlit interface with Ollama
# Complete India Coverage - 70+ Cities
# ============================================

import streamlit as st
from model import RealEstateModel
import base64
import os
import random

# -------------------------------------------------
# NORMALIZE MODEL OUTPUT (VERY IMPORTANT)
# -------------------------------------------------
def normalize_projects(projects):
    normalized = []
    for p in projects:
        normalized.append({
            "name": p.get("name", ""),
            "city": p.get("city", ""),
            "property_type": p.get("property_type") or p.get("type", ""),
            "price_min": p.get("price_min") or p.get("price", 0),
            "price_max": p.get("price_max") or p.get("price", 0),
            "location": p.get("location", ""),
            "bedrooms": p.get("bedrooms", ""),
            "developer": p.get("developer", ""),
            "amenities": p.get("amenities", ""),
            "possession_date": p.get("possession_date", ""),
            "description": p.get("description", "")
        })
    return normalized


# -------------------------------------------------
# FILTERING LOGIC (FIXED)
# -------------------------------------------------
def filter_projects_by_query(projects, query):
    if not projects:
        return []

    projects = normalize_projects(projects)
    q = query.lower()
    results = []

    for p in projects:
        city = p["city"].lower()
        ptype = p["property_type"].lower()
        price = p["price_min"] or 0

        match = True

        # City filter
        cities = [
            "mumbai","bangalore","hyderabad","delhi","goa","pune","chennai",
            "kolkata","ahmedabad","jaipur","kochi","vizag","vijayawada",
            "tirupati","warangal","guntur","nellore"
        ]
        for c in cities:
            if c in q and c not in city:
                match = False

        # Property type filter
        if "villa" in q and "villa" not in ptype:
            match = False
        if "apartment" in q and "apartment" not in ptype:
            match = False
        if "flat" in q and "apartment" not in ptype:
            match = False

        # Budget filter
        if "under" in q and "crore" in q:
            if price and price > 2:
                match = False

        if match:
            results.append(p)

    return results if results else projects[:5]


# -------------------------------------------------
# BOT RESPONSE
# -------------------------------------------------
def generate_bot_response(projects):
    if not projects:
        return "❌ No exact match found. Showing closest available properties."

    responses = [
        f"🏠 I found **{len(projects)} properties** for you. Check them on the right 👉",
        f"✨ Great choice! Showing **{len(projects)} matching properties**.",
        f"🎯 Here are **{len(projects)} properties** that match your search."
    ]
    return random.choice(responses)


# -------------------------------------------------
# BACKGROUND IMAGE
# -------------------------------------------------
def get_base64_image(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

bg_image = get_base64_image("background.jpg")

# -------------------------------------------------
# STREAMLIT CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="🏠 Real Estate India Chatbot",
    page_icon="🏠",
    layout="wide"
)

# -------------------------------------------------
# CSS
# -------------------------------------------------
if bg_image:
    st.markdown(f"""
    <style>
    .stApp {{
        background: url("data:image/jpg;base64,{bg_image}");
        background-size: cover;
    }}
    </style>
    """, unsafe_allow_html=True)

st.markdown("""
<style>
.user-message {
    background: #6a5acd;
    color: white;
    padding: 12px;
    border-radius: 15px;
    margin: 8px 0;
    text-align: right;
}
.bot-message {
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
        st.session_state.chat_history = []

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
    if not st.session_state.chat_history:
        st.markdown(
            "<div class='bot-message'>👋 Ask me about properties in any Indian city!</div>",
            unsafe_allow_html=True
        )

    for msg in st.session_state.chat_history:
        css = "user-message" if msg["type"] == "user" else "bot-message"
        st.markdown(f"<div class='{css}'>{msg['content']}</div>", unsafe_allow_html=True)

    user_input = st.text_input(
        "Ask about properties",
        placeholder="e.g., Apartments in Hyderabad",
        label_visibility="collapsed"
    )

    if st.button("🔍 Search") and user_input:
        st.session_state.chat_history.append({"type": "user", "content": user_input})

        with st.spinner("Searching..."):
            result = st.session_state.model.process_query(user_input)
            filtered = filter_projects_by_query(result["projects"], user_input)

            bot_reply = generate_bot_response(filtered)
            st.session_state.chat_history.append({"type": "bot", "content": bot_reply})
            st.session_state.last_results = filtered

        st.rerun()

# -------------------------------------------------
# RESULTS SECTION
# -------------------------------------------------
with right:
    st.subheader("🏢 Property Results")

    if "last_results" in st.session_state and st.session_state.last_results:
        for p in st.session_state.last_results:
            with st.expander(f"{p['name']} – {p['city']}"):
                st.write(f"**Type:** {p['property_type']}")
                st.write(f"**Location:** {p['location']}")
                st.write(f"**Bedrooms:** {p['bedrooms']}")
                st.write(f"**Developer:** {p['developer']}")
                st.write(f"**Amenities:** {p['amenities']}")
                st.write(f"**Possession:** {p['possession_date']}")
                st.write(f"**Description:** {p['description']}")
    else:
        st.info("💬 Ask a question to see properties here.")

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
            st.session_state.chat_history.append({"type": "user", "content": ex})
            result = st.session_state.model.process_query(ex)
            filtered = filter_projects_by_query(result["projects"], ex)
            st.session_state.chat_history.append({
                "type": "bot",
                "content": generate_bot_response(filtered)
            })
            st.session_state.last_results = filtered
            st.rerun()

    if st.button("🗑 Clear Chat"):
        st.session_state.chat_history = []
        st.session_state.pop("last_results", None)
        st.rerun()

    st.caption("🇮🇳 70+ Cities | AI Powered")
