# ============================================
# REAL ESTATE MODEL - FIXED & SMART SEARCH
# ============================================

import sqlite3
import pandas as pd
import re

class RealEstateModel:
    """Real estate chatbot using smart keyword filtering"""

    def __init__(self):
        self.conn = None
        self.df = None
        self.initialize()

    # --------------------------------------------------
    def initialize(self):
        self.create_database()
        self.load_projects()

    # --------------------------------------------------
    def create_database(self):
        self.conn = sqlite3.connect("real_estate.db", check_same_thread=False)
        cur = self.conn.cursor()

        cur.execute("DROP TABLE IF EXISTS projects")

        cur.execute("""
        CREATE TABLE projects (
            id INTEGER PRIMARY KEY,
            name TEXT,
            city TEXT,
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
        """)

        projects = [
            (1, 'Lodha World Towers', 'Mumbai', 'Mahalaxmi', 2.5e7, 5e7,
             'Apartments', '3-5 BHK',
             'Pool, Gym, Spa', 'Lodha Group', '2024', 'Luxury apartments'),

            (2, 'Godrej Aqua', 'Mumbai', 'Vikhroli', 1.8e7, 4e7,
             'Apartments', '2-4 BHK',
             'Garden, Club', 'Godrej', '2024', 'Premium apartments'),

            (3, 'Sobha Hartland', 'Bangalore', 'Whitefield', 8e6, 2.5e7,
             'Apartments', '2-4 BHK',
             'Lake, School', 'Sobha', '2024', 'Gated township'),

            (4, 'M3M Golf Estate', 'Gurgaon', 'Sector 65', 2e7, 4e7,
             'Villas', '3-5 BHK',
             'Golf, Club', 'M3M', '2024', 'Luxury villas'),

            (5, 'Raheja Mindspace', 'Hyderabad', 'Madhapur', 4e6, 2.5e7,
             'Apartments', '2-3 BHK',
             'Tech Park', 'Raheja', '2024', 'Modern living'),

            (6, 'Goa Bay Villas', 'Goa', 'Panaji', 1.2e7, 3e7,
             'Villas', '3-4 BHK',
             'Sea View, Pool', 'Bay Group', '2024', 'Luxury villas'),
        ]

        cur.executemany("""
        INSERT INTO projects VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """, projects)

        self.conn.commit()

    # --------------------------------------------------
    def load_projects(self):
        self.df = pd.read_sql("SELECT * FROM projects", self.conn)

    # --------------------------------------------------
    def extract_budget(self, query):
        match = re.search(r'(\d+(\.\d+)?)\s*(cr|crore)', query.lower())
        if match:
            return float(match.group(1)) * 1e7
        return None

    # --------------------------------------------------
    def search_projects(self, query, top_k=5):
        if not query:
            return self.df.head(top_k).to_dict(orient="records")

        q = query.lower()
        budget = self.extract_budget(q)

        results = []

        for _, row in self.df.iterrows():
            score = 0

            # City match
            if row.city.lower() in q:
                score += 3

            # Property type match
            if "apartment" in q and "apartment" in row.property_type.lower():
                score += 2
            if "villa" in q and "villa" in row.property_type.lower():
                score += 2

            # Budget match
            if budget:
                if row.price_min <= budget:
                    score += 2

            if score > 0:
                row_dict = row.to_dict()
                row_dict["score"] = score
                results.append(row_dict)

        if not results:
            results = self.df.head(top_k).to_dict(orient="records")

        results = sorted(results, key=lambda x: x.get("score", 0), reverse=True)
        return results[:top_k]

    # --------------------------------------------------
    def process_query(self, user_query):
        projects = self.search_projects(user_query)
        return {
            "query": user_query,
            "projects": projects,
            "count": len(projects),
            "response": f"Found {len(projects)} matching properties."
        }


if __name__ == "__main__":
    m = RealEstateModel()
    print("Model ready with", len(m.df), "projects")
