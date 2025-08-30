"""Main game orchestrator that manages the simulation loop."""

import asyncio
import uuid
from typing import List, Optional

from .data import create_sample_world
from .entities import GameWorld, League, Match
from .events import EventStore, MatchEnded, MatchScheduled, MatchStarted, SoftStateUpdated, WorldInitialized
from .llm import BrainOrchestrator, MockLLMProvider
from .simulation import MatchEngine


class GameOrchestrator:
    """Main orchestrator for the football simulation game."""
    
    def __init__(self, event_store: Optional[EventStore] = None) -> None:
        self.event_store = event_store or EventStore()
        self.world = GameWorld()
        self.match_engine = MatchEngine(self.world)
        self.brain_orchestrator = BrainOrchestrator(MockLLMProvider())
        
        # State tracking
        self.is_initialized = False
        self.current_matches: List[Match] = []
    
    def initialize_world(self) -> None:
        """Initialize the game world with sample data."""
        if self.is_initialized:
            return
        
        # Create sample world
        self.world = create_sample_world()
        
        # Generate fixtures for both leagues
        self._generate_fixtures()
        
        # Log world initialization
        event = WorldInitialized(
            season=self.world.season,
            leagues=list(self.world.leagues.keys())
        )
        self.event_store.append_event(event)
        
        self.is_initialized = True
    
    def _generate_fixtures(self) -> None:
        """Generate fixture list for all leagues."""
        for league_id, league in self.world.leagues.items():
            self._generate_league_fixtures(league)
    
    def _generate_league_fixtures(self, league: League) -> None:
        """Generate fixtures for a single league using round-robin."""
        teams = league.teams.copy()
        num_teams = len(teams)
        
        if num_teams < 2:
            return
        
        # Simple round-robin algorithm
        for matchday in range(1, num_teams * 2 - 1):  # Double round-robin
            for match_idx in range(num_teams // 2):
                home_idx = match_idx
                away_idx = num_teams - 1 - match_idx
                
                # Determine home and away teams
                if matchday <= num_teams - 1:
                    # First half of season
                    home_team_id = teams[home_idx]
                    away_team_id = teams[away_idx]
                else:
                    # Second half - reverse fixtures
                    home_team_id = teams[away_idx]
                    away_team_id = teams[home_idx]
                
                # Create match
                match_id = str(uuid.uuid4())
                match = Match(
                    id=match_id,
                    home_team_id=home_team_id,
                    away_team_id=away_team_id,
                    league=league.id,
                    matchday=matchday,
                    season=league.season
                )
                
                self.world.matches[match_id] = match
                
                # Schedule event
                event = MatchScheduled(
                    match_id=match_id,
                    home_team=home_team_id,
                    away_team=away_team_id,
                    league=league.id,
                    matchday=matchday,
                    season=league.season
                )
                self.event_store.append_event(event)
            
            # Rotate teams for next matchday (except first team stays fixed)
            teams = [teams[0]] + [teams[-1]] + teams[1:-1]
    
    def get_current_matchday_fixtures(self) -> List[Match]:
        """Get fixtures for the current matchday across all leagues."""
        fixtures = []
        
        for league in self.world.leagues.values():
            league_fixtures = [
                match for match in self.world.matches.values()
                if (match.league == league.id and 
                    match.matchday == league.current_matchday and
                    not match.finished)
            ]
            fixtures.extend(league_fixtures)
        
        return fixtures
    
    async def advance_simulation(self) -> dict:
        """Advance the simulation by one step (matchday)."""
        if not self.is_initialized:
            self.initialize_world()
        
        # Get current matchday fixtures
        fixtures = self.get_current_matchday_fixtures()
        
        if not fixtures:
            # No more matches - advance to next matchday or season
            self._advance_matchday()
            return {
                "status": "matchday_advanced",
                "matches_played": 0,
                "events": []
            }
        
        # Simulate all matches in current matchday
        all_events = []
        for match in fixtures:
            match_events = await self._simulate_match(match)
            all_events.extend(match_events)
        
        # Process LLM updates for the completed matches
        soft_updates = await self.brain_orchestrator.process_match_events(all_events, self.world)
        
        # Log soft state updates
        for update in soft_updates:
            event = SoftStateUpdated(
                entity_type=update.entity_type,
                entity_id=update.entity_id,
                updates=update.updates
            )
            self.event_store.append_event(event)
        
        # Advance to next matchday
        self._advance_matchday()
        
        return {
            "status": "matches_completed",
            "matches_played": len(fixtures),
            "events": [event.model_dump() for event in all_events],
            "soft_updates": [update.model_dump() for update in soft_updates]
        }
    
    async def _simulate_match(self, match: Match) -> List:
        """Simulate a single match and log events."""
        # Start match
        start_event = MatchStarted(
            match_id=match.id,
            seed=42  # Fixed seed for now - could be made configurable
        )
        self.event_store.append_event(start_event)
        
        # Simulate match
        match_events = self.match_engine.simulate_match(match.id, seed=42)
        
        # Log all match events
        for event in match_events:
            self.event_store.append_event(event)
        
        return match_events
    
    def _advance_matchday(self) -> None:
        """Advance all leagues to the next matchday."""
        for league in self.world.leagues.values():
            if not league.is_season_complete():
                league.current_matchday += 1
    
    def get_world_state(self) -> dict:
        """Get the current world state for the API."""
        return {
            "season": self.world.season,
            "leagues": {
                league_id: {
                    "name": league.name,
                    "current_matchday": league.current_matchday,
                    "table": [
                        {
                            "position": i + 1,
                            "team": team.name,
                            "played": team.matches_played,
                            "won": team.wins,
                            "drawn": team.draws,
                            "lost": team.losses,
                            "goals_for": team.goals_for,
                            "goals_against": team.goals_against,
                            "goal_difference": team.goal_difference,
                            "points": team.points
                        }
                        for i, team in enumerate(self.world.get_league_table(league_id))
                    ]
                }
                for league_id, league in self.world.leagues.items()
            },
            "next_fixtures": [
                {
                    "id": match.id,
                    "home_team": self.world.get_team_by_id(match.home_team_id).name if self.world.get_team_by_id(match.home_team_id) else "Unknown",
                    "away_team": self.world.get_team_by_id(match.away_team_id).name if self.world.get_team_by_id(match.away_team_id) else "Unknown",
                    "league": match.league,
                    "matchday": match.matchday
                }
                for match in self.get_current_matchday_fixtures()[:10]  # Limit to 10 for display
            ]
        }