# ============================================
# REAL ESTATE MODEL - Backend Service
# Streamlit Cloud Compatible (FAISS Removed)
# ============================================

import sqlite3
import pandas as pd
import numpy as np
import requests
import json

class RealEstateModel:
    """Real estate chatbot using lightweight keyword search"""

    def __init__(self):
        self.conn = None
        self.df = None
        self.project_texts = None
        self.ollama_url = "http://localhost:11434/api/generate"
        self.initialize()

    def initialize(self):
        """Initialize database and load projects"""
        self.create_database()
        self.load_projects()

    def create_database(self):
        """Create SQLite database with project data"""
        self.conn = sqlite3.connect('real_estate.db')
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
