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
    sharpness: int = Field(default=75, ge=1, le=100)  # Match sharpness/readiness
    reputation: int = Field(default=30, ge=1, le=100, description="Player reputation/fame level")
    
    # Metadata
    age: int = Field(ge=15, le=45)  # Extended range for youth development
    peak_age: int = Field(default=27, ge=20, le=35)  # Age when player peaks
    injured: bool = Field(default=False)
    injury_weeks_remaining: int = Field(default=0, ge=0)  # Weeks until recovery
    suspended: bool = Field(default=False)
    suspension_matches_remaining: int = Field(default=0, ge=0)  # Matches until suspension ends
    yellow_cards: int = Field(default=0, ge=0)
    red_cards: int = Field(default=0, ge=0)
    
    @property
    def base_attributes(self) -> Dict[str, int]:
        """Get base attributes before age modifiers."""
        return {
            "pace": self.pace,
            "shooting": self.shooting, 
            "passing": self.passing,
            "defending": self.defending,
            "physicality": self.physicality
        }
    
    @property
    def age_modified_attributes(self) -> Dict[str, int]:
        """Get attributes modified by age curve."""
        base_attrs = self.base_attributes
        age_modifier = self._calculate_age_modifier()
        
        modified = {}
        for attr, value in base_attrs.items():
            # Apply age modifier (can be positive or negative)
            modified_value = value + (value * age_modifier * 0.01)  # Age modifier as percentage
            modified[attr] = max(1, min(100, int(modified_value)))
        
        return modified
    
    def _calculate_age_modifier(self) -> float:
        """Calculate age modifier (-20 to +15) based on player's age curve."""
        age_diff = self.age - self.peak_age
        
        if age_diff <= 0:
            # Before peak: gradual improvement (0 to +15%)
            years_to_peak = self.peak_age - 15  # Career start at 15
            if years_to_peak <= 0:
                return 15.0  # Edge case
            progress = (self.age - 15) / years_to_peak
            return progress * 15.0  # Up to +15% at peak
        else:
            # After peak: gradual decline (0 to -20%)
            years_after_peak = age_diff
            decline_rate = min(years_after_peak * 2.5, 20.0)  # 2.5% per year, max -20%
            return -decline_rate
    
    @property
    def overall_rating(self) -> int:
        """Calculate overall player rating from attributes."""
        # Use age-modified attributes
        attrs = self.age_modified_attributes
        skills = [attrs["pace"], attrs["shooting"], attrs["passing"], attrs["defending"], attrs["physicality"]]
        base_rating = sum(skills) / len(skills)
        
        # Factor in form, fitness, and sharpness
        form_modifier = (self.form - 50) * 0.1  # -5 to +5 modifier
        fitness_modifier = (self.fitness - 100) * 0.05  # Penalty for low fitness
        sharpness_modifier = (self.sharpness - 75) * 0.05  # Penalty for low sharpness
        
        # Injury penalty
        injury_modifier = -10 if self.injured else 0
        
        overall = base_rating + form_modifier + fitness_modifier + sharpness_modifier + injury_modifier
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
    reputation: int = Field(default=40, ge=1, le=100, description="Club reputation/prestige level")
    
    # Financial system
    balance: int = Field(default=1000000, ge=0, description="Current club balance in currency units")
    initial_balance: int = Field(default=1000000, ge=0, description="Starting balance for the season")
    owner_investment: int = Field(default=0, ge=0, description="Owner investment for this season")
    monthly_wage_costs: int = Field(default=100000, ge=0, description="Monthly player and staff wage costs")
    monthly_stadium_costs: int = Field(default=50000, ge=0, description="Monthly stadium maintenance costs")
    monthly_facilities_costs: int = Field(default=25000, ge=0, description="Monthly training facilities costs")
    
    # Stadium details
    stadium_name: str = Field(default="Fantasy Stadium", description="Name of the team's stadium")
    stadium_capacity: int = Field(default=30000, ge=5000, le=100000, description="Stadium seating capacity")
    
    # Training facilities
    training_facilities_quality: int = Field(default=50, ge=1, le=100, description="Quality of training facilities")
    
    # Fanbase
    fanbase_size: int = Field(default=50000, ge=1000, description="Total supporter base size")
    season_ticket_holders: int = Field(default=15000, ge=100, description="Number of season ticket holders")
    
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
    
    @property
    def monthly_total_costs(self) -> int:
        """Calculate total monthly operating costs."""
        return self.monthly_wage_costs + self.monthly_stadium_costs + self.monthly_facilities_costs
    
    @property
    def season_ticket_revenue(self) -> int:
        """Calculate annual revenue from season tickets (rough estimate)."""
        # Average season ticket price varies by club reputation and capacity
        avg_price = 200 + (self.reputation * 5)  # £200-£700 range
        return self.season_ticket_holders * avg_price
    
    @property
    def matchday_revenue_per_game(self) -> int:
        """Calculate estimated revenue per home game."""
        # Assume 80% attendance for regular matches
        attendance = int(self.stadium_capacity * 0.8)
        # Ticket price varies by reputation
        avg_ticket_price = 20 + (self.reputation * 0.5)  # £20-£70 range
        return attendance * int(avg_ticket_price)
    
    def calculate_stadium_utilization(self) -> float:
        """Calculate stadium utilization based on fanbase and capacity."""
        # Larger fanbase relative to capacity means higher utilization
        if self.stadium_capacity == 0:
            return 0.0
        potential_attendance = min(self.fanbase_size * 0.3, self.stadium_capacity)
        return potential_attendance / self.stadium_capacity


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
    investment_tendency: int = Field(default=50, ge=1, le=100, description="Likelihood to invest money")
    
    # Soft attributes (LLM-driven)
    ambition: int = Field(default=50, ge=1, le=100, description="Sporting ambition")
    patience: int = Field(default=50, ge=1, le=100, description="Patience with results")
    public_approval: int = Field(default=50, ge=1, le=100, description="Fan approval rating")
    
    # Financial history
    total_invested: int = Field(default=0, ge=0, description="Total amount invested in the club")
    last_investment: int = Field(default=0, ge=0, description="Last investment amount")
    
    # Metadata
    years_at_club: int = Field(default=1, ge=0)
    
    def calculate_potential_investment(self, team_performance: float, financial_need: float) -> int:
        """Calculate potential investment based on owner characteristics and team situation."""
        # Base investment capacity based on wealth
        base_investment = self.wealth * 10000  # Wealth 100 = £1M capacity
        
        # Modify by investment tendency
        investment_willingness = self.investment_tendency / 100.0
        
        # Modify by ambition and patience
        ambition_factor = self.ambition / 100.0
        patience_factor = self.patience / 100.0
        
        # Performance factor: poor performance may trigger more investment if ambitious
        performance_factor = 1.0
        if team_performance < 0.5 and self.ambition > 60:
            performance_factor = 1.5  # Ambitious owners invest more when team struggles
        elif team_performance > 0.8:
            performance_factor = 0.7  # Less need to invest when doing well
        
        # Financial need factor
        need_factor = min(financial_need, 2.0)  # Cap at 2x multiplier
        
        potential = base_investment * investment_willingness * ambition_factor * performance_factor * need_factor
        return int(potential * 0.2)  # Only invest up to 20% of capacity per season


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


class Rivalry(BaseModel):
    """A rivalry between two teams."""
    id: str
    team1_id: str
    team2_id: str
    name: str = Field(description="Official name of the rivalry (e.g., 'Merseyside Derby')")
    intensity: int = Field(default=75, ge=1, le=100, description="Rivalry intensity level")
    description: str = Field(default="", description="Brief description of the rivalry")


class GameWorld(BaseModel):
    """The complete game world state."""
    season: int = Field(default=2025)
    current_date: str = Field(default="2025-08-01")  # Simple date representation
    
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
    rivalries: Dict[str, Rivalry] = Field(default_factory=dict)
    
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
    
    def get_rivalry_between_teams(self, team1_id: str, team2_id: str) -> Optional['Rivalry']:
        """Get rivalry between two teams if it exists."""
        for rivalry in self.rivalries.values():
            if ((rivalry.team1_id == team1_id and rivalry.team2_id == team2_id) or
                (rivalry.team1_id == team2_id and rivalry.team2_id == team1_id)):
                return rivalry
        return None
    
    def advance_weekly_progression(self) -> None:
        """Advance weekly progression for all players (fitness, injuries, suspensions)."""
        import random
        rng = random.Random(42)  # Use consistent seed for weekly progression
        
        for player in self.players.values():
            # Handle injury recovery
            if player.injured and player.injury_weeks_remaining > 0:
                player.injury_weeks_remaining -= 1
                if player.injury_weeks_remaining <= 0:
                    player.injured = False
                    player.injury_weeks_remaining = 0
            
            # Handle suspension countdown (per match, not weekly, but we can track here)
            # Note: Suspension countdown should happen per match, but we can reset here for testing
            
            # Fitness changes - natural recovery and training
            if not player.injured:
                # Training improves fitness gradually  
                fitness_change = rng.randint(1, 3)  # +1 to +3 fitness per week
                player.fitness = min(100, player.fitness + fitness_change)
                
                # Sharpness also improves with training
                sharpness_change = rng.randint(1, 2)  # +1 to +2 sharpness per week  
                player.sharpness = min(100, player.sharpness + sharpness_change)
            else:
                # Injured players lose fitness and sharpness
                fitness_loss = rng.randint(2, 4)  # -2 to -4 fitness per week when injured
                sharpness_loss = rng.randint(1, 3)  # -1 to -3 sharpness per week when injured
                
                player.fitness = max(1, player.fitness - fitness_loss)
                player.sharpness = max(1, player.sharpness - sharpness_loss)
    
    def advance_match_progression(self, match_events: list) -> None:
        """Advance match-based progression (suspensions, match fitness cost)."""
        import random
        rng = random.Random(42)
        
        # Get all players who participated in matches (had events)
        participating_players = set()
        
        for event in match_events:
            if hasattr(event, 'player'):
                participating_players.add(event.player)
            elif hasattr(event, 'scorer'):
                participating_players.add(event.scorer)
            elif hasattr(event, 'player_off'):
                participating_players.add(event.player_off)
            elif hasattr(event, 'player_on'):
                participating_players.add(event.player_on)
        
        # Apply match costs to participating players
        for player_name in participating_players:
            # Find the player object
            player = None
            for p in self.players.values():
                if p.name == player_name:
                    player = p
                    break
            
            if player and not player.injured:
                # Playing a match costs fitness and sharpness
                fitness_cost = rng.randint(3, 7)  # -3 to -7 fitness per match
                sharpness_cost = rng.randint(2, 5)  # -2 to -5 sharpness per match
                
                player.fitness = max(1, player.fitness - fitness_cost)
                player.sharpness = max(1, player.sharpness - sharpness_cost)
        
        # Handle suspension countdown for all players
        for player in self.players.values():
            if player.suspended and player.suspension_matches_remaining > 0:
                player.suspension_matches_remaining -= 1
                if player.suspension_matches_remaining <= 0:
                    player.suspended = False
                    player.suspension_matches_remaining = 0
    
    def advance_monthly_finances(self) -> None:
        """Advance monthly financial progression for all teams."""
        import random
        rng = random.Random(self.season * 12 + 42)  # Different seed each month
        
        for team in self.teams.values():
            # Apply monthly costs
            monthly_costs = team.monthly_total_costs
            team.balance = max(0, team.balance - monthly_costs)
            
            # Add matchday revenue (estimate 2 home games per month)
            matchday_income = team.matchday_revenue_per_game * 2
            team.balance += matchday_income
            
            # Potential owner investment based on team performance and financial situation
            owners = self.get_club_owners_for_team(team.id)
            if owners:
                owner = owners[0]  # Primary owner
                
                # Calculate team performance (simple metric)
                if team.matches_played > 0:
                    performance = (team.wins * 3 + team.draws) / (team.matches_played * 3)
                else:
                    performance = 0.5  # Neutral performance
                
                # Financial need factor
                financial_need = max(0, (monthly_costs * 3 - team.balance) / (monthly_costs * 3))
                
                # Random chance for investment
                if rng.random() < 0.3:  # 30% chance per month
                    potential_investment = owner.calculate_potential_investment(performance, financial_need)
                    if potential_investment > 10000:  # Minimum threshold
                        team.balance += potential_investment
                        team.owner_investment += potential_investment
                        owner.total_invested += potential_investment
                        owner.last_investment = potential_investment
    
    def advance_seasonal_evolution(self) -> None:
        """Advance seasonal evolution of club finances and reputation (max 20% change)."""
        import random
        rng = random.Random(self.season * 365 + 42)
        
        for team in self.teams.values():
            # Reputation evolution based on performance and random factors
            if team.matches_played > 0:
                performance = (team.wins * 3 + team.draws) / (team.matches_played * 3)
                league_position_factor = 1.0  # Could be enhanced with actual league position
                
                # Performance influence on reputation (max ±10 points)
                performance_change = int((performance - 0.5) * 20)  # -10 to +10
                performance_change = max(-10, min(10, performance_change))
                
                # Random factor (max ±5 points)
                random_change = rng.randint(-5, 5)
                
                # Total change (max ±15 points, which is 15% of 100)
                total_rep_change = performance_change + random_change
                new_reputation = team.reputation + total_rep_change
                team.reputation = max(1, min(100, new_reputation))
            
            # Financial evolution - initial balance for next season
            # Successful teams get better financial backing
            reputation_factor = team.reputation / 100.0
            performance_factor = 1.0
            if team.matches_played > 0:
                performance_factor = 0.8 + (team.wins / max(1, team.matches_played)) * 0.4
            
            # Owner wealth can also evolve
            owners = self.get_club_owners_for_team(team.id)
            if owners:
                owner = owners[0]
                # Owner wealth can change by up to 10% per season
                wealth_change = rng.randint(-10, 15)  # Slight positive bias
                new_wealth = owner.wealth + wealth_change
                owner.wealth = max(1, min(100, new_wealth))
                
                # Update team's financial situation for new season
                wealth_factor = owner.wealth / 100.0
                base_balance = 500000 + (team.reputation * 10000)  # £500k to £1.5M base
                team.initial_balance = int(base_balance * wealth_factor * performance_factor)
                team.balance = max(team.balance, team.initial_balance // 2)  # Don't drop below half
                team.owner_investment = 0  # Reset for new season