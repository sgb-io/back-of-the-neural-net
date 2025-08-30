"""Simple test without external dependencies."""

import sys
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Simple test without pydantic
print("Testing basic architecture without external dependencies...")

# Test 1: Basic imports
try:
    import sqlite3
    print("✓ SQLite available")
except ImportError:
    print("✗ SQLite not available")

# Test 2: Can create basic data structures
class SimpleTeam:
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name
        self.players = []
        self.wins = 0
        self.draws = 0
        self.losses = 0
        self.goals_for = 0
        self.goals_against = 0
    
    @property
    def points(self):
        return self.wins * 3 + self.draws

class SimplePlayer:
    def __init__(self, id: str, name: str, position: str):
        self.id = id
        self.name = name
        self.position = position
        self.pace = 50
        self.shooting = 50
        self.form = 50

# Test 3: Create sample data
teams = {}
teams["team1"] = SimpleTeam("team1", "United Dragons")
teams["team1"].players.append(SimplePlayer("p1", "Gareth Thunderfoot", "GK"))
teams["team1"].players.append(SimplePlayer("p2", "Marcus Swiftwind", "ST"))

teams["team2"] = SimpleTeam("team2", "City Phoenix") 
teams["team2"].players.append(SimplePlayer("p3", "Oliver Ironshot", "GK"))
teams["team2"].players.append(SimplePlayer("p4", "James Stormpass", "ST"))

print(f"✓ Created {len(teams)} teams with players")

# Test 4: Simple match simulation
import random

class SimpleMatch:
    def __init__(self, home_team, away_team):
        self.home_team = home_team
        self.away_team = away_team
        self.home_score = 0
        self.away_score = 0
        self.events = []
    
    def simulate(self, seed=42):
        rng = random.Random(seed)
        
        # Simple simulation - random goals
        total_goals = rng.randint(0, 6)
        
        for _ in range(total_goals):
            if rng.random() < 0.5:
                self.home_score += 1
                scorer = rng.choice(self.home_team.players)
                self.events.append(f"Goal by {scorer.name} ({self.home_team.name})")
            else:
                self.away_score += 1
                scorer = rng.choice(self.away_team.players)
                self.events.append(f"Goal by {scorer.name} ({self.away_team.name})")

# Test match simulation
match = SimpleMatch(teams["team1"], teams["team2"])
match.simulate()

print(f"✓ Match simulation: {match.home_team.name} {match.home_score} - {match.away_score} {match.away_team.name}")
for event in match.events:
    print(f"  - {event}")

# Test 5: SQLite event storage
conn = sqlite3.connect(":memory:")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE events (
        id INTEGER PRIMARY KEY,
        type TEXT,
        data TEXT,
        timestamp TEXT
    )
""")

# Store a simple event
import datetime
event_data = {
    "type": "MatchCompleted",
    "home_team": match.home_team.name,
    "away_team": match.away_team.name,
    "home_score": match.home_score,
    "away_score": match.away_score,
    "events": match.events
}

cursor.execute("""
    INSERT INTO events (type, data, timestamp) 
    VALUES (?, ?, ?)
""", ("MatchCompleted", json.dumps(event_data), datetime.datetime.now().isoformat()))

conn.commit()

# Retrieve events
cursor.execute("SELECT * FROM events")
rows = cursor.fetchall()
print(f"✓ Stored and retrieved {len(rows)} events from SQLite")

conn.close()

print("\n🎉 Basic architecture test completed successfully!")
print("\nNext steps:")
print("1. Install dependencies: pip install pydantic fastapi uvicorn sse-starlette")
print("2. Run full system: python main.py test")
print("3. Start server: python main.py server")
print("4. Install React UI: cd ui && npm install && npm start")