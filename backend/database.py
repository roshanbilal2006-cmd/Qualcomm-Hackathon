import sqlite3
from typing import List
from models import ObservationRequest, HeatmapPoint
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "landsense.db")

def init_db():
    """Initializes the SQLite database with necessary tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Table to store observations
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS observations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            latitude TEXT,
            longitude TEXT,
            timestamp TEXT,
            voice_query TEXT,
            device TEXT
        )
    ''')
    
    # Optionally, a table for storing heatmap data points directly, 
    # but for this hackathon we can just derive heatmap data from observations 
    # or keep a separate mock table. Let's create a mock table for heatmap.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS heatmap_points (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            latitude REAL,
            longitude REAL,
            activity_level TEXT
        )
    ''')
    
    conn.commit()
    
    # Seed some mock heatmap data if empty
    cursor.execute("SELECT COUNT(*) FROM heatmap_points")
    if cursor.fetchone()[0] == 0:
        seed_heatmap(conn)
        
    conn.close()

def seed_heatmap(conn):
    """Seed initial heatmap points (e.g., around a central location)."""
    cursor = conn.cursor()
    points = [
        (1.3521, 103.8198, "High"),
        (1.3600, 103.8100, "Medium"),
        (1.3400, 103.8300, "Low"),
    ]
    cursor.executemany("INSERT INTO heatmap_points (latitude, longitude, activity_level) VALUES (?, ?, ?)", points)
    conn.commit()

def save_observation(request: ObservationRequest) -> int:
    """Saves a new observation to the database and returns the generated ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # We are not storing the base64 images in SQLite to save space during the hackathon.
    # In a real app, they would go to S3 or a local file storage and we'd save the path.
    
    cursor.execute('''
        INSERT INTO observations (latitude, longitude, timestamp, voice_query, device)
        VALUES (?, ?, ?, ?, ?)
    ''', (request.latitude, request.longitude, request.timestamp, request.voice_query, request.device))
    
    obs_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return obs_id

def get_heatmap_points() -> List[HeatmapPoint]:
    """Retrieves all heatmap points."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT latitude, longitude, activity_level FROM heatmap_points")
    rows = cursor.fetchall()
    conn.close()
    
    points = []
    for row in rows:
        points.append(HeatmapPoint(
            latitude=row[0],
            longitude=row[1],
            activity_level=row[2]
        ))
    return points
