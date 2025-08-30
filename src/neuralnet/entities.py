"""Core game entities and domain models."""

from typing import Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field


class Position(str, Enum):
    """Player positions."""
    GK = "GK"  # Goalkeeper
    CB = "CB"  # Centre Back
    LB = "LB"  # Left Back
    RB = "RB"  # Right Back
    CM = "CM"  # Centre Midfield
    LM = "LM"  # Left Midfield
    RM = "RM"  # Right Midfield
    CAM = "CAM"  # Centre Attacking Midfield
    LW = "LW"  # Left Wing
    RW = "RW"  # Right Wing
    ST = "ST"  # Striker


class Player(BaseModel):
    """A football player."""
    id: str
    name: str
    position: Position
    
    # Hard attributes (deterministic)
    pace: int = Field(ge=1, le=100)
    shooting: int = Field(ge=1, le=100)
    passing: int = Field(ge=1, le=100)
    defending: int = Field(ge=1, le=100)
    physicality: int = Field(ge=1, le=100)
    
    # Soft attributes (LLM-driven)
    form: int = Field(default=50, ge=1, le=100)  # Current form
    morale: int = Field(default=50, ge=1, le=100)  # Player morale
    fitness: int = Field(default=100, ge=1, le=100)  # Physical fitness
    
    # Metadata
    age: int = Field(ge=16, le=45)
    injured: bool = Field(default=False)
    yellow_cards: int = Field(default=0, ge=0)
    red_cards: int = Field(default=0, ge=0)


class Team(BaseModel):
    """A football team."""
    id: str
    name: str
    league: str
    
    # Hard state
    players: List[Player] = Field(default_factory=list)
    
    # Soft state (LLM-driven)
    team_morale: int = Field(default=50, ge=1, le=100)
    tactical_familiarity: int = Field(default=50, ge=1, le=100)
    
    # Statistics
    matches_played: int = Field(default=0, ge=0)
    wins: int = Field(default=0, ge=0)
    draws: int = Field(default=0, ge=0)
    losses: int = Field(default=0, ge=0)
    goals_for: int = Field(default=0, ge=0)
    goals_against: int = Field(default=0, ge=0)
    
    @property
    def points(self) -> int:
        """Calculate current league points."""
        return self.wins * 3 + self.draws
    
    @property
    def goal_difference(self) -> int:
        """Calculate goal difference."""
        return self.goals_for - self.goals_against


class Match(BaseModel):
    """A football match."""
    id: str
    home_team_id: str
    away_team_id: str
    league: str
    matchday: int
    season: int
    
    # Match state
    home_score: int = Field(default=0, ge=0)
    away_score: int = Field(default=0, ge=0)
    minute: int = Field(default=0, ge=0, le=120)  # Including extra time
    finished: bool = Field(default=False)
    
    # Match metadata
    seed: Optional[int] = None  # For deterministic simulation


class League(BaseModel):
    """A football league."""
    id: str
    name: str
    teams: List[str] = Field(default_factory=list)  # Team IDs
    season: int
    current_matchday: int = Field(default=1, ge=1)
    total_matchdays: int = Field(default=38, ge=1)  # Standard league format
    
    def is_season_complete(self) -> bool:
        """Check if the current season is complete."""
        return self.current_matchday > self.total_matchdays


class GameWorld(BaseModel):
    """The complete game world state."""
    season: int = Field(default=2024)
    current_date: str = Field(default="2024-01-01")  # Simple date representation
    
    # Entities
    leagues: Dict[str, League] = Field(default_factory=dict)
    teams: Dict[str, Team] = Field(default_factory=dict)
    players: Dict[str, Player] = Field(default_factory=dict)
    matches: Dict[str, Match] = Field(default_factory=dict)
    
    # Simulation state
    paused: bool = Field(default=False)
    simulation_speed: int = Field(default=1, ge=1, le=10)
    
    def get_team_by_id(self, team_id: str) -> Optional[Team]:
        """Get a team by its ID."""
        return self.teams.get(team_id)
    
    def get_league_by_id(self, league_id: str) -> Optional[League]:
        """Get a league by its ID."""
        return self.leagues.get(league_id)
    
    def get_match_by_id(self, match_id: str) -> Optional[Match]:
        """Get a match by its ID."""
        return self.matches.get(match_id)
    
    def get_player_by_id(self, player_id: str) -> Optional[Player]:
        """Get a player by its ID."""
        return self.players.get(player_id)
    
    def get_league_table(self, league_id: str) -> List[Team]:
        """Get league table sorted by points, goal difference, then goals for."""
        league = self.leagues.get(league_id)
        if not league:
            return []
        
        teams = [self.teams[team_id] for team_id in league.teams if team_id in self.teams]
        return sorted(
            teams,
            key=lambda t: (t.points, t.goal_difference, t.goals_for),
            reverse=True
        )