# ============================================
# REAL ESTATE MODEL - Backend (FINAL)
# ============================================

import sqlite3
import pandas as pd

class RealEstateModel:
    def __init__(self):
        self.conn = sqlite3.connect("real_estate.db", check_same_thread=False)
        self.load_data()

    def load_data(self):
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
            (1,"Raheja Mindspace","Hyderabad","Madhapur",4e6,2.5e7,
             "Apartments","Office",
             "IT Park, Security","Raheja","2024","Tech park apartments"),
            (2,"Lodha World Towers","Mumbai","Mahalaxmi",2.5e7,5e7,
             "Apartments","3-5 BHK",
             "Pool, Gym","Lodha","2024","Luxury apartments"),
            (3,"Godrej Aqua","Mumbai","Vikhroli",1.8e7,4e7,
             "Apartments","2-4 BHK",
             "Garden, Club","Godrej","2024","Premium apartments"),
            (4,"Sobha Hartland","Bangalore","Whitefield",8e6,2.5e7,
             "Apartments","2-4 BHK",
             "Lake, School","Sobha","2024","Residential township"),
            (5,"DLF Villas","Goa","Panaji",3e7,6e7,
             "Villas","4-5 BHK",
             "Beach, Pool","DLF","2025","Luxury beach villas"),
        ]

        cur.executemany("INSERT INTO projects VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", projects)
        self.conn.commit()

        self.df = pd.read_sql("SELECT * FROM projects", self.conn)

    def process_query(self, query):
        q = query.lower()

        cities = ["hyderabad","mumbai","bangalore","goa"]
        types = ["apartment","villa"]

        city = next((c for c in cities if c in q), None)
        ptype = next((t for t in types if t in q), None)

        df = self.df.copy()
        df["city"] = df["city"].str.lower()
        df["property_type"] = df["property_type"].str.lower()

        if city:
            df = df[df["city"].str.contains(city)]

        if ptype:
            df = df[df["property_type"].str.contains(ptype)]

        return {
            "projects": df.to_dict(orient="records"),
            "count": len(df)
        }
