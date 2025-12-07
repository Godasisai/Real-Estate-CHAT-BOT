# ============================================
# REAL ESTATE MODEL - Backend Service
# Streamlit Cloud Compatible (FAISS Removed)
# ============================================

import sqlite3
import pandas as pd
import requests

class RealEstateModel:
    """Real estate chatbot using lightweight keyword search"""

    def __init__(self):
        self.conn = None
        self.df = None
        self.ollama_url = "http://localhost:11434/api/generate"
        self.initialize()

    def initialize(self):
        """Initialize database and load projects"""
        self.create_database()
        self.load_projects()

    def create_database(self):
        """Create SQLite database with project data"""
        self.conn = sqlite3.connect('real_estate.db', check_same_thread=False)
        cursor = self.conn.cursor()

        cursor.execute('DROP TABLE IF EXISTS projects')

        cursor.execute('''
            CREATE TABLE projects (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                city TEXT NOT NULL,
                location TEXT,
                price_min REAL,
                price_max REAL,
                property_type TEXT,
                bedrooms TEXT,
                amenities TEXT,
                developer TEXT,
                possession_date TEXT,
                description TEXT
            )
        ''')

        projects_data = [
            (1, 'Lodha World Towers', 'Mumbai', 'Mahalaxmi', 2.5e7, 5e7,
             'Luxury Apartments', '3-5 BHK',
             'Pool, Gym, Spa, Concierge, Security', 'Lodha Group',
             '2024-06', 'Ultra-luxury residential project with world-class amenities'),

            (2, 'Godrej Aqua', 'Mumbai', 'Vikhroli', 1.8e7, 4e7,
             'Premium Apartments', '2-4 BHK',
             'Garden, Club, Parking, School', 'Godrej Properties',
             '2024-08', 'Premium residential with landscaped gardens'),

            (3, 'Sobha Hartland', 'Bangalore', 'Whitefield', 8e6, 2.5e7,
             'Residential Township', '2-4 BHK',
             'Lake, Golf Course, School, Hospital', 'Sobha Limited',
             '2024-12', 'Gated township with integrated amenities'),

            (4, 'DLF The Crest', 'Gurgaon', 'Sector 54', 1e7, 3e7,
             'Ultra Luxury', '3-5 BHK',
             'Private Club, Spa, Security, Parking', 'DLF Limited',
             '2024-09', 'Ultra-luxury apartments in prime Gurgaon'),

            (5, 'Puravankara Purva Westend', 'Bangalore', 'Whitefield',
             4.5e6, 1.5e7, 'Residential', '2-3 BHK',
             'Pool, Gym, Garden, Parking', 'Puravankara Limited',
             '2024-10', 'Mid-range residential with good amenities'),

            (6, 'M3M Golf Estate', 'Gurgaon', 'Sector 65',
             2e7, 4e7, 'Premium Villas', '3-5 BHK',
             'Golf Course, Club, Tennis, Security', 'M3M Development',
             '2024-07', 'Premium villas with golf course access'),

            (7, 'Prestige Central', 'Bangalore', 'MG Road',
             5e6, 3e7, 'Commercial Office', '1000-10000 sqft',
             'Parking, 24/7 Power, Security, WiFi', 'Prestige Group',
             '2024-05', 'Premium office with modern infrastructure'),

            (8, 'NESCO Business Park', 'Mumbai', 'Nesco Complex',
             7.5e6, 5e7, 'IT Office Space', '5000-50000 sqft',
             'Halls, Cafeteria, Transport, Parking', 'NESCO',
             '2024-03', 'IT business park with excellent connectivity'),

            (9, 'Raheja Mindspace', 'Hyderabad', 'Madhapur',
             4e6, 2.5e7, 'Tech Park', '2000-20000 sqft',
             'Security, Connectivity, Food Court, ATM', 'Raheja Group',
             '2024-04', 'Tech park with modern facilities'),
        ]

        cursor.executemany('''
            INSERT INTO projects 
            (id, name, city, location, price_min, price_max, property_type, bedrooms, amenities, developer, possession_date, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', projects_data)

        self.conn.commit()
        print("✓ Database created successfully")

    def load_projects(self):
        """Load projects from database"""
        query = "SELECT * FROM projects"
        self.df = pd.read_sql_query(query, self.conn)
        print(f"✓ Loaded {len(self.df)} projects")

    def search_projects(self, query, top_k=5):
        """Simple keyword-based search compatible with Streamlit Cloud"""
        if not query:
            return self.df.head(top_k).to_dict(orient='records')

        query = query.lower()

        def row_matches(row):
            text = " ".join([str(v).lower() for v in row.values])
            return query in text

        matched = self.df[self.df.apply(row_matches, axis=1)]
        return matched.head(top_k).to_dict(orient='records')

    def generate_response(self, user_query, search_results):
        """Generate response using Ollama (if available)"""
        context = "Here are the relevant real estate projects:\n\n"
        for i, project in enumerate(search_results, 1):
            price_str = f"₹{project['price_min']/1e7:.1f}Cr - ₹{project['price_max']/1e7:.1f}Cr"
            context += f"{i}. {project['name']} - {project['city']}\n"
            context += f"   Location: {project['location']}\n"
            context += f"   Type: {project['property_type']} | {project['bedrooms']}\n"
            context += f"   Price: {price_str}\n"
            context += f"   Developer: {project['developer']}\n"
            context += f"   Amenities: {project['amenities']}\n"
            context += f"   Possession: {project['possession_date']}\n\n"

        prompt = f"""
You are a helpful real estate assistant.

User Query: {user_query}

{context}

Provide a simple, friendly answer.
"""

        try:
            response = requests.post(
                self.ollama_url,
                json={'model': 'mistral', 'prompt': prompt, 'stream': False},
                timeout=10
            )
            if response.status_code == 200:
                return response.json().get('response', 'No response generated')
            return "⚠️ Unable to generate response from Ollama."

        except Exception:
            return "⚠️ Ollama is not available. Showing search results only."

    def process_query(self, user_query):
        """Main workflow"""
        projects = self.search_projects(user_query, top_k=5)
        response = self.generate_response(user_query, projects)
        return {
            "query": user_query,
            "response": response,
            "projects": projects,
            "count": len(projects)
        }


if __name__ == "__main__":
    print("Initializing Real Estate Model...")
    m = RealEstateModel()
    print("✓ Model Ready!")

