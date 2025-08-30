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
    
    @property
    def overall_rating(self) -> int:
        """Calculate overall player rating from attributes."""
        # Simple average of all skill attributes
        skills = [self.pace, self.shooting, self.passing, self.defending, self.physicality]
        base_rating = sum(skills) / len(skills)
        
        # Factor in form and fitness
        form_modifier = (self.form - 50) * 0.1  # -5 to +5 modifier
        fitness_modifier = (self.fitness - 100) * 0.05  # Penalty for low fitness
        
        overall = base_rating + form_modifier + fitness_modifier
        return max(1, min(100, int(overall)))


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


class ClubOwner(BaseModel):
    """A club owner/director/chairperson."""
    id: str
    name: str
    team_id: str
    role: str = Field(description="Owner, Director, Chairman, etc.")
    
    # Hard attributes
    wealth: int = Field(ge=1, le=100, description="Financial resources")
    business_acumen: int = Field(ge=1, le=100, description="Business skills")
    
    # Soft attributes (LLM-driven)
    ambition: int = Field(default=50, ge=1, le=100, description="Sporting ambition")
    patience: int = Field(default=50, ge=1, le=100, description="Patience with results")
    public_approval: int = Field(default=50, ge=1, le=100, description="Fan approval rating")
    
    # Metadata
    years_at_club: int = Field(default=1, ge=0)


class MediaOutlet(BaseModel):
    """A press/media outlet."""
    id: str
    name: str
    outlet_type: str = Field(description="Newspaper, TV, Radio, Online, etc.")
    
    # Hard attributes
    reach: int = Field(ge=1, le=100, description="Audience reach")
    credibility: int = Field(ge=1, le=100, description="Journalistic credibility")
    
    # Soft attributes (LLM-driven)
    bias_towards_teams: Dict[str, int] = Field(default_factory=dict, description="Team bias ratings (-100 to 100)")
    sensationalism: int = Field(default=50, ge=1, le=100, description="Tendency toward sensational stories")
    
    # Current narratives
    active_stories: List[str] = Field(default_factory=list, description="Currently running story topics")


class PlayerAgent(BaseModel):
    """A player agent."""
    id: str
    name: str
    agency_name: str
    
    # Hard attributes
    negotiation_skill: int = Field(ge=1, le=100, description="Contract negotiation ability")
    network_reach: int = Field(ge=1, le=100, description="Industry connections")
    
    # Soft attributes (LLM-driven)
    reputation: int = Field(default=50, ge=1, le=100, description="Industry reputation")
    aggressiveness: int = Field(default=50, ge=1, le=100, description="How pushy in negotiations")
    
    # Client relationships
    clients: List[str] = Field(default_factory=list, description="Player IDs represented")


class StaffMember(BaseModel):
    """A staff member (coach, medical, scout, etc.)."""
    id: str
    name: str
    team_id: str
    role: str = Field(description="Head Coach, Assistant Coach, Physio, Scout, etc.")
    
    # Hard attributes
    experience: int = Field(ge=1, le=100, description="Years of experience")
    specialization: int = Field(ge=1, le=100, description="Skill in their specialization")
    
    # Soft attributes (LLM-driven)
    morale: int = Field(default=50, ge=1, le=100, description="Staff member morale")
    team_rapport: int = Field(default=50, ge=1, le=100, description="Relationship with team")
    
    # Metadata
    contract_years_remaining: int = Field(default=1, ge=0)
    salary: int = Field(default=50000, ge=0, description="Annual salary")


class GameWorld(BaseModel):
    """The complete game world state."""
    season: int = Field(default=2024)
    current_date: str = Field(default="2024-01-01")  # Simple date representation
    
    # Entities
    leagues: Dict[str, League] = Field(default_factory=dict)
    teams: Dict[str, Team] = Field(default_factory=dict)
    players: Dict[str, Player] = Field(default_factory=dict)
    matches: Dict[str, Match] = Field(default_factory=dict)
    
    # New entities
    club_owners: Dict[str, ClubOwner] = Field(default_factory=dict)
    media_outlets: Dict[str, MediaOutlet] = Field(default_factory=dict)
    player_agents: Dict[str, PlayerAgent] = Field(default_factory=dict)
    staff_members: Dict[str, StaffMember] = Field(default_factory=dict)
    
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
    
    def get_club_owner_by_id(self, owner_id: str) -> Optional[ClubOwner]:
        """Get a club owner by its ID."""
        return self.club_owners.get(owner_id)
    
    def get_media_outlet_by_id(self, outlet_id: str) -> Optional[MediaOutlet]:
        """Get a media outlet by its ID."""
        return self.media_outlets.get(outlet_id)
    
    def get_player_agent_by_id(self, agent_id: str) -> Optional[PlayerAgent]:
        """Get a player agent by its ID."""
        return self.player_agents.get(agent_id)
    
    def get_staff_member_by_id(self, staff_id: str) -> Optional[StaffMember]:
        """Get a staff member by its ID."""
        return self.staff_members.get(staff_id)
    
    def get_club_owners_for_team(self, team_id: str) -> List[ClubOwner]:
        """Get all club owners for a specific team."""
        return [owner for owner in self.club_owners.values() if owner.team_id == team_id]
    
    def get_staff_for_team(self, team_id: str) -> List[StaffMember]:
        """Get all staff members for a specific team."""
        return [staff for staff in self.staff_members.values() if staff.team_id == team_id]
    
    def get_agent_for_player(self, player_id: str) -> Optional[PlayerAgent]:
        """Get the agent for a specific player."""
        for agent in self.player_agents.values():
            if player_id in agent.clients:
                return agent
        return None
    
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