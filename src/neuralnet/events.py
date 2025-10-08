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
    penalty: bool = False  # True if goal was from a penalty kick


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


class CornerKick(MatchEvent):
    """Corner kick event."""
    team: str


class Foul(MatchEvent):
    """Foul committed event."""
    player: str
    team: str
    foul_type: str  # "regular", "dangerous", "professional"


class PenaltyAwarded(MatchEvent):
    """Penalty kick awarded event."""
    team: str
    reason: str  # Description of why penalty was awarded


class Injury(MatchEvent):
    """Player injury event."""
    player: str
    team: str
    injury_type: str
    severity: str  # "minor", "moderate", "severe"
    weeks_out: int


class MatchEnded(Event):
    """Event fired when a match concludes."""
    match_id: str
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    duration_minutes: int
    # Match statistics
    home_possession: Optional[int] = None  # Percentage (0-100)
    away_possession: Optional[int] = None  # Percentage (0-100)
    home_shots: Optional[int] = None
    away_shots: Optional[int] = None
    home_shots_on_target: Optional[int] = None
    away_shots_on_target: Optional[int] = None
    home_corners: Optional[int] = None
    away_corners: Optional[int] = None
    home_fouls: Optional[int] = None
    away_fouls: Optional[int] = None
    home_penalties: Optional[int] = None  # Penalty kicks taken
    away_penalties: Optional[int] = None  # Penalty kicks taken


class SoftStateUpdated(Event):
    """Event fired when LLM-driven soft state is updated."""
    entity_type: str  # "player", "team", "club_owner", "media_outlet", "player_agent", "staff_member"
    entity_id: str
    updates: Dict[str, Any]


class MediaStoryPublished(Event):
    """Event fired when a media outlet publishes a story."""
    media_outlet_id: str
    headline: str
    story_type: str  # "transfer_rumor", "performance_analysis", "scandal", "injury_update", etc.
    entities_mentioned: List[str]  # IDs of players, teams, etc. mentioned
    sentiment: int = Field(ge=-100, le=100, description="Story sentiment (-100 negative, 100 positive)")


class OwnerStatement(Event):
    """Event fired when a club owner makes a public statement."""
    owner_id: str
    team_id: str
    statement_type: str  # "support", "pressure", "investment", "ambition", etc.
    message: str
    public_reaction: int = Field(ge=-100, le=100, description="Fan reaction to statement")


class AgentNegotiation(Event):
    """Event fired when a player agent enters negotiations or makes demands."""
    agent_id: str
    player_id: str
    team_id: str
    negotiation_type: str  # "contract_demand", "playing_time", "transfer_request", etc.
    outcome: str  # "successful", "ongoing", "failed", etc.


class EventStore:
    """SQLite-based event store for the game world."""
    
    def __init__(self, db_path: str = "game.db") -> None:
        # Handle in-memory database specially
        if db_path == ":memory:":
            self.db_path = ":memory:"
            # For in-memory databases, keep a persistent connection
            self._connection = sqlite3.connect(":memory:")
            self._init_db_with_connection(self._connection)
        else:
            self.db_path = Path(db_path)
            self._connection = None
            self._init_db()
    
    def reset_database(self) -> None:
        """Reset the database by dropping all tables and recreating them.
        
        This is useful for starting with a fresh game state.
        """
        if self.db_path == ":memory:":
            # For in-memory databases, just recreate the connection
            if self._connection:
                self._connection.close()
            self._connection = sqlite3.connect(":memory:")
            self._init_db_with_connection(self._connection)
        else:
            # For file databases, drop and recreate tables
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DROP TABLE IF EXISTS events")
                cursor.execute("DROP TABLE IF EXISTS snapshots")
                self._init_db_with_connection(conn)
    
    def _init_db(self) -> None:
        """Initialize the SQLite database schema for file-based databases."""
        with sqlite3.connect(self.db_path) as conn:
            self._init_db_with_connection(conn)
    
    def _init_db_with_connection(self, conn: sqlite3.Connection) -> None:
        """Initialize database schema with given connection."""
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                data TEXT NOT NULL,
                sequence_number INTEGER
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS snapshots (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                sequence_number INTEGER NOT NULL,
                data TEXT NOT NULL
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_sequence ON events(sequence_number)")
        conn.commit()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        if self._connection:
            return self._connection
        else:
            return sqlite3.connect(self.db_path)
    
    def append_event(self, event: Event) -> None:
        """Append an event to the store."""
        if self._connection:
            # For in-memory databases, use persistent connection
            cursor = self._connection.cursor()
            
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
            self._connection.commit()
        else:
            # For file-based databases, create new connection
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
        if self._connection:
            conn = self._connection
        else:
            conn = sqlite3.connect(self.db_path)
        
        try:
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
        finally:
            if not self._connection:
                conn.close()
    
    def get_latest_sequence_number(self) -> int:
        """Get the latest sequence number in the store."""
        if self._connection:
            cursor = self._connection.cursor()
            cursor.execute("SELECT COALESCE(MAX(sequence_number), 0) FROM events")
            return cursor.fetchone()[0]
        else:
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
            "CornerKick": CornerKick,
            "Injury": Injury,
            "MatchEnded": MatchEnded,
            "SoftStateUpdated": SoftStateUpdated,
            "MediaStoryPublished": MediaStoryPublished,
        }
        return event_classes.get(event_type)