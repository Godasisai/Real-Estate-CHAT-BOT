# ============================================
# REAL ESTATE WEB APP - Frontend
# File: app.py
# Streamlit interface with Ollama
# Complete India Coverage - 70+ Cities
# ============================================

from altair import Align
import streamlit as st
from model import RealEstateModel
import base64
import os

# -------------------------------------------------
# HELPER FUNCTIONS FOR FILTERING
# -------------------------------------------------
def filter_projects_by_query(projects, query):
    """Filter projects based on user query - STRICT FILTERING with ALL INDIA COVERAGE"""
    if not projects:
        return projects
    
    query_lower = query.lower()
    filtered = []
    
    # Extract city names from query - ALL MAJOR INDIAN CITIES
    cities_map = {
        # Metro Cities
        'mumbai': ['mumbai', 'bombay', 'navi mumbai', 'thane'],
        'bangalore': ['bangalore', 'bengaluru', 'whitefield', 'electronic city'],
        'delhi': ['delhi', 'new delhi', 'ncr'],
        'kolkata': ['kolkata', 'calcutta'],
        'chennai': ['chennai', 'madras'],
        'hyderabad': ['hyderabad', 'secunderabad', 'cyberabad'],
        
        # Tier 1 Cities
        'pune': ['pune', 'pimpri', 'chinchwad'],
        'ahmedabad': ['ahmedabad', 'amdavad'],
        'gurgaon': ['gurgaon', 'gurugram', 'dlf'],
        'noida': ['noida', 'greater noida'],
        'ghaziabad': ['ghaziabad'],
        'faridabad': ['faridabad'],
        'surat': ['surat'],
        'jaipur': ['jaipur', 'pink city'],
        'lucknow': ['lucknow'],
        'kanpur': ['kanpur'],
        'nagpur': ['nagpur'],
        'indore': ['indore'],
        'bhopal': ['bhopal'],
        'visakhapatnam': ['visakhapatnam', 'vizag', 'vishakhapatnam'],
        'vadodara': ['vadodara', 'baroda'],
        'ludhiana': ['ludhiana'],
        'agra': ['agra'],
        'nashik': ['nashik'],
        'kochi': ['kochi', 'cochin', 'ernakulam'],
        'coimbatore': ['coimbatore'],
        'chandigarh': ['chandigarh', 'mohali', 'panchkula'],
        
        # Tier 2 Cities
        'patna': ['patna'],
        'thiruvananthapuram': ['thiruvananthapuram', 'trivandrum'],
        'mysore': ['mysore', 'mysuru'],
        'mangalore': ['mangalore', 'mangaluru'],
        'madurai': ['madurai'],
        'rajkot': ['rajkot'],
        'varanasi': ['varanasi', 'banaras', 'kashi'],
        'aurangabad': ['aurangabad'],
        'amritsar': ['amritsar'],
        'allahabad': ['allahabad', 'prayagraj'],
        'ranchi': ['ranchi'],
        'jodhpur': ['jodhpur'],
        'guwahati': ['guwahati', 'gauhati'],
        'raipur': ['raipur'],
        'kota': ['kota'],
        'dehradun': ['dehradun'],
        'bhubaneswar': ['bhubaneswar', 'bbsr'],
        'jabalpur': ['jabalpur'],
        'vijayawada': ['vijayawada'],
        'gwalior': ['gwalior'],
        'jammu': ['jammu'],
        'srinagar': ['srinagar'],
        'tiruchirappalli': ['tiruchirappalli', 'trichy', 'tiruchi'],
        'salem': ['salem'],
        'jalandhar': ['jalandhar'],
        'meerut': ['meerut'],
        'kolhapur': ['kolhapur'],
        'tirupati': ['tirupati'],
        'udaipur': ['udaipur'],
        'shimla': ['shimla'],
        'panaji': ['panaji', 'panjim', 'goa'],
        'calicut': ['calicut', 'kozhikode'],
        'thrissur': ['thrissur', 'trichur'],
        'nellore': ['nellore'],
        'guntur': ['guntur'],
        'warangal': ['warangal'],
        'imphal': ['imphal'],
        'kohima': ['kohima'],
        'silchar': ['silchar'],
        'agartala': ['agartala'],
        'aizawl': ['aizawl'],
        'shillong': ['shillong']
    }
    
    # Find which city is mentioned in query
    query_cities = []
    for city, aliases in cities_map.items():
        if any(alias in query_lower for alias in aliases):
            query_cities.append(city)
    
    # Extract property types from query
    property_types = ['apartment', 'villa', 'office', 'commercial', 'residential', 'park', 'space', 'tower', 'house']
    query_types = [ptype for ptype in property_types if ptype in query_lower]
    
    # Filter logic
    for project in projects:
        project_city_lower = project.get('city', '').lower()
        project_type_lower = project.get('property_type', '').lower()
        project_name_lower = project.get('name', '').lower()
        
        match = False
        
        # PRIORITY 1: If city is mentioned, MUST match city
        if query_cities:
            for city in query_cities:
                if city in project_city_lower:
                    match = True
                    break
        else:
            # PRIORITY 2: If no city, match by property type
            if query_types:
                for ptype in query_types:
                    if ptype in project_type_lower:
                        match = True
                        break
            else:
                # PRIORITY 3: Match by project name keywords
                query_words = [w for w in query_lower.split() if len(w) > 3]
                if query_words:
                    matching_words = sum(1 for word in query_words if word in project_name_lower)
                    if matching_words >= 1:
                        match = True
        
        if match:
            filtered.append(project)
    
    # If no matches and city was specified, return empty
    if not filtered and query_cities:
        return []
    
    # If still no matches, return all (fallback)
    return filtered if filtered else projects[:5]


def generate_bot_response(projects, query):
    """Generate conversational bot response"""
    if not projects:
        return "I couldn't find any properties matching your criteria. Could you try rephrasing or specify a different city?"
    
    count = len(projects)
    query_lower = query.lower()
    
    # Extract city from query
    city_mentioned = None
    for word in query.split():
        if len(word) > 4:
            city_mentioned = word.title()
            break
    
    responses = [
        f"Great! I found {count} properties for you. Check out the results on the right! 🏠",
        f"Perfect! I discovered {count} amazing properties that match your search. Take a look! ✨",
        f"Awesome! Here are {count} properties I found for you. Browse them on the right side! 🎯",
        f"Found {count} excellent options! Explore the details in the results panel. 🏡",
        f"Success! I've got {count} properties that fit your requirements. Check them out! 🌟"
    ]
    
    import random
    return random.choice(responses)


# -------------------------------------------------
# Load Background Image Safely
# -------------------------------------------------
def get_base64_image(image_path):
    """Safely load base64 image"""
    try:
        if os.path.exists(image_path):
            with open(image_path, "rb") as img:
                return base64.b64encode(img.read()).decode()
    except:
        pass
    return None

bg_image_base64 = get_base64_image("background.jpg")

# Streamlit Config
st.set_page_config(
    page_title="Real Estate Chatbot - India",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------
# CSS Styling with Base64 Background
# -------------------------------------------------
if bg_image_base64:
    st.markdown(f"""
    <style>
        /* Background Image */
        .stApp {{
            background: url("data:image/jpg;base64,{bg_image_base64}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        
        [data-testid="stAppViewContainer"] {{
            background: url("data:image/jpg;base64,{bg_image_base64}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        
        /* Overlay */
        [data-testid="stAppViewContainer"]::before {{
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.3);
            pointer-events: none;
            z-index: 1;
        }}
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
    </style>
    """, unsafe_allow_html=True)

st.markdown("""
<style>
    /* Sidebar background */
    [data-testid="stSidebar"] {
        background: rgba(0, 0, 0, 0.7) !important;
    }

    [data-testid="stSidebar"] * {
        color: white !important;
    }

    /* Title */
    .main-title {
        text-align: center; 
        color: white;
        font-size: 2.5em;
        font-weight: bold;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.5);
    }

    /* User Message */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; 
        padding: 12px 16px;
        border-radius: 18px 18px 4px 18px;
        margin: 8px 0;
        margin-left: 50px;
        word-wrap: break-word;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.4);
        display: inline-block;
        max-width: 80%;
        z-index: 2;
        position: relative;
    }

    /* Bot Message */
    .bot-message {
        background-color: rgba(255, 255, 255, 0.95);
        color: #333;
        padding: 12px 16px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px 0;
        margin-right: 50px;
        word-wrap: break-word;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        display: inline-block;
        max-width: 80%;
        z-index: 2;
        position: relative;
    }

    .stTextInput > div > div > input {
        border-radius: 25px;
        border: 2px solid white;
        padding: 12px 20px;
        background: rgba(255, 255, 255, 0.95);
        font-size: 16px;
    }

    .stButton > button {
        border-radius: 25px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none;
        padding: 12px 30px;
        font-weight: bold;
        font-size: 16px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.4);
    }

    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }

    .stInfo {
        background: rgba(255,255,255,0.9) !important;
        border-left: 4px solid #667eea !important;
    }

    h1, h2, h3 {
        color: white !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Load ML Model
# -------------------------------------------------
if 'model' not in st.session_state:
    with st.spinner("Loading model... (First time may take 2-3 minutes)"):
        try:
            st.session_state.model = RealEstateModel()
            st.session_state.chat_history = []
        except Exception as e:
            st.error(f"❌ Error loading model: {str(e)}")
            st.stop()

# Header
st.markdown("<h1 class='main-title'>🏠 Real Estate India Chatbot</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: white; font-size: 1.1em;'>AI-Powered Property Search Across India</p>", unsafe_allow_html=True)

# Layout
left_col, right_col = st.columns([1, 1], gap="medium")

# -------------------------------------------------
# CHAT SECTION
# -------------------------------------------------
with left_col:
    # Display chat history
    if not st.session_state.chat_history:
        st.markdown("<div class='bot-message'>👋 Hi! I'm your Real Estate Assistant. Ask me about properties in any city across India!</div>", unsafe_allow_html=True)
    
    for message in st.session_state.chat_history:
        if message['type'] == 'user':
            st.markdown(f"<div class='user-message'>{message['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='bot-message'>{message['content']}</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    user_input = st.text_input(
        "Ask about properties...",
        placeholder="E.g., Show me luxury apartments in Mumbai...",
        label_visibility="collapsed"
    )

    _, col_btn, _ = st.columns([1, 1, 1])
    with col_btn:
        search_btn = st.button("🔍 Search", use_container_width=True)

    if search_btn and user_input:
        st.session_state.chat_history.append({'type': 'user', 'content': user_input})

        with st.spinner("Searching properties..."):
            try:
                result = st.session_state.model.process_query(user_input)
                # APPLY FILTERING HERE
                filtered_results = filter_projects_by_query(result['projects'], user_input)
                
                # Generate bot response
                bot_response = generate_bot_response(filtered_results, user_input)
                st.session_state.chat_history.append({'type': 'bot', 'content': bot_response})
                
                st.session_state.last_results = filtered_results
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.session_state.chat_history.append({
                    'type': 'bot',
                    'content': f"Sorry, I encountered an error. Please try again! 🙏"
                })

        st.rerun()

# -------------------------------------------------
# RESULTS SECTION
# -------------------------------------------------
with right_col:
    st.markdown('<div class="results-container">', unsafe_allow_html=True)
    st.markdown("### 🏢 Property Results")

    if 'last_results' in st.session_state and st.session_state.last_results:
        projects = st.session_state.last_results
        st.info(f"✅ Found {len(projects)} properties")

        for project in projects:
            with st.expander(f"📍 {project['name']} - {project['city']}"):
                try:
                    price_min = project['price_min'] / 1e7
                    price_max = project['price_max'] / 1e7
                    st.metric("💰 Price", f"₹{price_min:.1f}Cr - ₹{price_max:.1f}Cr")
                except:
                    st.metric("💰 Price", "N/A")

                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Location:** {project.get('location', 'N/A')}")
                    st.write(f"**Type:** {project.get('property_type', 'N/A')}")
                with col2:
                    st.write(f"**Bedrooms:** {project.get('bedrooms', 'N/A')}")
                    st.write(f"**Developer:** {project.get('developer', 'N/A')}")

                st.write(f"**Amenities:** {project.get('amenities', 'N/A')}")
                st.write(f"**Possession:** {project.get('possession_date', 'N/A')}")
                st.write(f"**Details:** {project.get('description', 'N/A')}")

    else:
        st.info("💬 Ask me about properties and I'll show you the best matches!")
        st.markdown("""
        **Try asking:**
        - "Show me apartments in Bangalore"
        - "Luxury villas in Goa"
        - "Commercial properties under 5 crores"
        - "3 BHK flats in Pune"
        """)

    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
with st.sidebar:
    st.markdown("### 💬 Quick Queries")
    st.markdown("Click any question below:")

    examples = [
        "What properties do you have in Mumbai?",
        "Show me villas in Bangalore",
        "Any apartments under 2 crores?",
        "Properties in Delhi NCR",
        "Luxury homes in Goa"
    ]

    for example in examples:
        if st.button(example, use_container_width=True, key=example):
            st.session_state.chat_history.append({'type': 'user', 'content': example})

            with st.spinner("Processing..."):
                try:
                    result = st.session_state.model.process_query(example)
                    # APPLY FILTERING HERE
                    filtered_results = filter_projects_by_query(result['projects'], example)
                    
                    # Generate bot response
                    bot_response = generate_bot_response(filtered_results, example)
                    st.session_state.chat_history.append({'type': 'bot', 'content': bot_response})
                    
                    st.session_state.last_results = filtered_results
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

            st.rerun()

    st.markdown("---")
    st.markdown("### 📊 Database Stats")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Properties", len(st.session_state.model.df) if hasattr(st.session_state.model, 'df') else 0)
    with col2:
        st.metric("Cities", st.session_state.model.df['city'].nunique() if hasattr(st.session_state.model, 'df') else 0)

    st.metric("Chat Messages", len([m for m in st.session_state.chat_history if m['type'] == 'user']))

    st.markdown("---")
    st.markdown("### 🇮🇳 All India Coverage")
    st.caption("✅ 70+ Cities Covered")
    st.caption("🏙️ Metro & Tier 1 Cities")
    st.caption("🌆 Major Tier 2 Cities")
    st.caption("🗺️ Pan India Availability")

    st.markdown("---")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        if 'last_results' in st.session_state:
            del st.session_state.last_results
        st.rerun()

    st.caption("🚀 Powered by AI | Real Estate India")