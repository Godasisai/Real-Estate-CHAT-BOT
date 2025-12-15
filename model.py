# ============================================
# REAL ESTATE MODEL - Backend Service
# STRICT CITY + PROPERTY FILTERING
# ============================================

import sqlite3
import pandas as pd

class RealEstateModel:
    def __init__(self):
        self.conn = None
        self.df = None
        self.initialize()

    def initialize(self):
        self.create_database()
        self.load_projects()

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

        data = [
            (1,"Lodha World Towers","Mumbai","Mahalaxmi",2.5e7,5e7,"Apartments","3-5 BHK",
             "Pool, Gym","Lodha","2024","Luxury homes"),
            (2,"Godrej Aqua","Mumbai","Vikhroli",1.8e7,4e7,"Apartments","2-4 BHK",
             "Garden, Club","Godrej","2024","Premium flats"),
            (3,"Sobha Hartland","Bangalore","Whitefield",8e6,2.5e7,"Apartments","2-4 BHK",
             "Lake, School","Sobha","2024","Residential township"),
            (4,"Raheja Mindspace","Hyderabad","Madhapur",4e6,2.5e7,"Apartments","Office Space",
             "IT Park","Raheja","2024","Tech park Hyderabad"),
            (5,"DLF Villas","Goa","Panaji",3e7,6e7,"Villas","4-5 BHK",
             "Beach, Pool","DLF","2025","Luxury villas")
        ]

        cur.executemany("""
        INSERT INTO projects VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """, data)

        self.conn.commit()

    def load_projects(self):
        self.df = pd.read_sql("SELECT * FROM projects", self.conn)

    # ✅ FIXED SEARCH
    def search_projects(self, query, top_k=5):
        query = query.lower()

        cities = [
            "mumbai","bangalore","bengaluru","hyderabad",
            "delhi","goa","pune","chennai","kolkata"
        ]
        property_types = ["apartment","villa","flat","office","commercial"]

        city = None
        ptype = None

        for c in cities:
            if c in query:
                city = c
                break

        for p in property_types:
            if p in query:
                ptype = p
                break

        df = self.df.copy()
        df["city"] = df["city"].str.lower()
        df["property_type"] = df["property_type"].str.lower()

        if city:
            df = df[df["city"].str.contains(city)]

        if ptype:
            df = df[df["property_type"].str.contains(ptype)]

        return df.head(top_k).to_dict(orient="records")

    def process_query(self, query):
        projects = self.search_projects(query)
        return {
            "projects": projects,
            "count": len(projects)
        }
