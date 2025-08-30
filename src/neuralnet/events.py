"""Event sourcing system for the game world."""

import json
import sqlite3
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T", bound="Event")


class Event(BaseModel, ABC):
    """Base class for all events in the system."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    event_type: str = Field(init=False)
    
    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        cls.model_fields["event_type"].default = cls.__name__

    def model_post_init(self, __context: Any) -> None:
        if not hasattr(self, "event_type") or not self.event_type:
            self.event_type = self.__class__.__name__


class WorldInitialized(Event):
    """Event fired when the game world is first created."""
    season: int
    leagues: List[str]


class MatchScheduled(Event):
    """Event fired when a match is scheduled."""
    match_id: str
    home_team: str
    away_team: str
    league: str
    matchday: int
    season: int


class MatchStarted(Event):
    """Event fired when a match begins."""
    match_id: str
    seed: int


class MatchEvent(Event):
    """Base class for events that occur during a match."""
    match_id: str
    minute: int
    home_score: int
    away_score: int


class KickOff(MatchEvent):
    """Match kick-off event."""
    pass


class Goal(MatchEvent):
    """Goal scored event."""
    scorer: str
    team: str
    assist: Optional[str] = None


class YellowCard(MatchEvent):
    """Yellow card event."""
    player: str
    team: str
    reason: str


class RedCard(MatchEvent):
    """Red card event."""
    player: str
    team: str
    reason: str


class Substitution(MatchEvent):
    """Player substitution event."""
    team: str
    player_off: str
    player_on: str


class MatchEnded(Event):
    """Event fired when a match concludes."""
    match_id: str
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    duration_minutes: int


class SoftStateUpdated(Event):
    """Event fired when LLM-driven soft state is updated."""
    entity_type: str  # "player", "team", etc.
    entity_id: str
    updates: Dict[str, Any]


class EventStore:
    """SQLite-based event store for the game world."""
    
    def __init__(self, db_path: str = "game.db") -> None:
        self.db_path = Path(db_path)
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize the SQLite database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    data TEXT NOT NULL,
                    sequence_number INTEGER
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS snapshots (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    sequence_number INTEGER NOT NULL,
                    data TEXT NOT NULL
                )
            """)
            
            conn.execute("CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_events_sequence ON events(sequence_number)")
    
    def append_event(self, event: Event) -> None:
        """Append an event to the store."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get next sequence number
            cursor.execute("SELECT COALESCE(MAX(sequence_number), 0) + 1 FROM events")
            sequence_number = cursor.fetchone()[0]
            
            cursor.execute("""
                INSERT INTO events (id, timestamp, event_type, data, sequence_number)
                VALUES (?, ?, ?, ?, ?)
            """, (
                event.id,
                event.timestamp.isoformat(),
                event.event_type,
                event.model_dump_json(),
                sequence_number
            ))
    
    def get_events(
        self, 
        event_type: Optional[str] = None,
        after_sequence: Optional[int] = None,
        limit: Optional[int] = None
    ) -> List[Event]:
        """Retrieve events from the store."""
        with sqlite3.connect(self.db_path) as conn:
            query = "SELECT data, event_type FROM events WHERE 1=1"
            params = []
            
            if event_type:
                query += " AND event_type = ?"
                params.append(event_type)
            
            if after_sequence is not None:
                query += " AND sequence_number > ?"
                params.append(after_sequence)
            
            query += " ORDER BY sequence_number"
            
            if limit:
                query += " LIMIT ?"
                params.append(limit)
            
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            events = []
            for row in cursor.fetchall():
                data_json, event_type_name = row
                event_class = self._get_event_class(event_type_name)
                if event_class:
                    event_data = json.loads(data_json)
                    events.append(event_class.model_validate(event_data))
            
            return events
    
    def get_latest_sequence_number(self) -> int:
        """Get the latest sequence number in the store."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COALESCE(MAX(sequence_number), 0) FROM events")
            return cursor.fetchone()[0]
    
    def _get_event_class(self, event_type: str) -> Optional[Type[Event]]:
        """Get the event class for a given event type name."""
        # This is a simple registry - in a larger system you'd want a proper registry
        event_classes = {
            "WorldInitialized": WorldInitialized,
            "MatchScheduled": MatchScheduled,
            "MatchStarted": MatchStarted,
            "KickOff": KickOff,
            "Goal": Goal,
            "YellowCard": YellowCard,
            "RedCard": RedCard,
            "Substitution": Substitution,
            "MatchEnded": MatchEnded,
            "SoftStateUpdated": SoftStateUpdated,
        }
        return event_classes.get(event_type)