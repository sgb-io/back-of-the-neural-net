"""Main game orchestrator that manages the simulation loop."""

import asyncio
import uuid
from typing import List, Optional, Dict, Any

from .config import get_config, Config
from .data import create_sample_world
from .entities import GameWorld, League, Match
from .events import EventStore, MatchEnded, MatchScheduled, MatchStarted, SoftStateUpdated, WorldInitialized
from .llm import BrainOrchestrator, MockLLMProvider
from .llm_mcp import MockToolsLLMProvider, ToolsLLMProvider
from .llm_lmstudio import LMStudioProvider
from .game_tools import GameStateTools
from .simulation import MatchEngine


class GameOrchestrator:
    """Main orchestrator for the football simulation game."""
    
    def __init__(self, event_store: Optional[EventStore] = None, config: Optional[Config] = None) -> None:
        self.config = config or get_config()
        self.event_store = event_store or EventStore()
        self.world = GameWorld()
        self.match_engine = MatchEngine(self.world)
        
        # Initialize game state tools and LLM provider based on configuration
        self.use_tools = self.config.use_tools
        self.llm_provider = self._create_llm_provider()
        
        if self.use_tools:
            self.game_tools = GameStateTools(self.world)
        else:
            self.game_tools = None
        
        self.brain_orchestrator = BrainOrchestrator(self.llm_provider)
        
        # State tracking
        self.is_initialized = False
        self.current_matches: List[Match] = []
    
    def _create_llm_provider(self):
        """Create LLM provider based on configuration."""
        provider_type = self.config.llm.provider.lower()
        
        if provider_type == "lmstudio":
            return LMStudioProvider(self.config.llm)
        elif provider_type == "mock":
            if self.use_tools:
                # Will create tools later in initialize_world
                return None  # Placeholder, will be replaced
            else:
                return MockLLMProvider()
        else:
            # Default to mock for unknown providers
            print(f"Warning: Unknown LLM provider '{provider_type}', falling back to mock")
            return MockLLMProvider()
    
    def initialize_world(self) -> None:
        """Initialize the game world with sample data."""
        if self.is_initialized:
            return
        
        # Create sample world
        self.world = create_sample_world()
        
        # Re-initialize match engine with new world
        self.match_engine = MatchEngine(self.world)
        
        # Re-initialize game tools with new world and update LLM provider if needed
        if self.use_tools:
            self.game_tools = GameStateTools(self.world)
            if self.config.llm.provider.lower() == "mock":
                # For mock provider with tools, recreate the provider
                self.llm_provider = MockToolsLLMProvider(self.game_tools)
                self.brain_orchestrator = BrainOrchestrator(self.llm_provider)
        elif self.llm_provider is None:
            # Fallback if provider wasn't created in constructor
            self.llm_provider = MockLLMProvider()
            self.brain_orchestrator = BrainOrchestrator(self.llm_provider)
        
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
    
    def get_completed_matches(self, limit: Optional[int] = None) -> List[Match]:
        """Get completed matches, most recent first."""
        completed_matches = [
            match for match in self.world.matches.values()
            if match.finished
        ]
        
        # Sort by matchday and season (most recent first)
        completed_matches.sort(
            key=lambda m: (m.season, m.matchday),
            reverse=True
        )
        
        if limit:
            completed_matches = completed_matches[:limit]
        
        return completed_matches
    
    def get_match_events(self, match_id: str) -> List[Any]:
        """Get all events for a specific match."""
        # Get all events from the event store
        all_events = self.event_store.get_events()
        
        # Filter events that belong to this match
        match_events = []
        seen_event_ids = set()
        
        for event in all_events:
            # Skip duplicate events
            if event.id in seen_event_ids:
                continue
            
            # Check if event has match_id attribute and matches
            if hasattr(event, 'match_id') and event.match_id == match_id:
                match_events.append(event)
                seen_event_ids.add(event.id)
        
        # Sort by timestamp
        match_events.sort(key=lambda e: e.timestamp)
        
        return match_events
    
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
            ],
            "entities_summary": {
                "total_players": len(self.world.players),
                "total_club_owners": len(self.world.club_owners),
                "total_staff_members": len(self.world.staff_members),
                "total_player_agents": len(self.world.player_agents),
                "total_media_outlets": len(self.world.media_outlets)
            },
            "recent_narratives": self._get_recent_narratives()
        }
    
    def _get_recent_narratives(self) -> List[Dict[str, Any]]:
        """Get recent narratives from media outlets and other sources."""
        narratives = []
        
        # Sample some media stories and owner statements
        import random
        
        # Get a few media outlets
        sample_outlets = list(self.world.media_outlets.values())[:3]
        for outlet in sample_outlets:
            if outlet.active_stories:
                narratives.extend([
                    {
                        "type": "media_story",
                        "source": outlet.name,
                        "headline": story,
                        "outlet_type": outlet.outlet_type
                    }
                    for story in outlet.active_stories[:2]  # Limit to 2 per outlet
                ])
        
        # Add some club owner sentiment
        for owner in list(self.world.club_owners.values())[:5]:  # Sample 5 owners
            team = self.world.get_team_by_id(owner.team_id)
            if team:
                if owner.public_approval < 40:
                    narratives.append({
                        "type": "owner_sentiment",
                        "source": f"{owner.name} ({owner.role})",
                        "headline": f"Fan pressure mounting on {team.name} leadership",
                        "sentiment": "negative"
                    })
                elif owner.public_approval > 80:
                    narratives.append({
                        "type": "owner_sentiment", 
                        "source": f"{owner.name} ({owner.role})",
                        "headline": f"{team.name} ownership praised by supporters",
                        "sentiment": "positive"
                    })
        
        return narratives[:10]  # Limit total narratives
    
    async def query_game_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Query a game state tool directly for testing/debugging."""
        if not self.use_tools or not self.game_tools:
            return {"error": "Game tools not enabled"}
        
        try:
            if tool_name == "get_match_predictions":
                return await self.game_tools.get_match_predictions(kwargs["home_team_id"], kwargs["away_team_id"])
            elif tool_name == "get_reputation_info":
                return await self.game_tools.get_reputation_info(
                    kwargs["entity_type"], kwargs["entity_id"], 
                    kwargs["relation_type"], kwargs["relation_id"]
                )
            elif tool_name == "get_head_to_head":
                return await self.game_tools.get_head_to_head(
                    kwargs["team1_id"], kwargs["team2_id"], kwargs.get("limit", 5)
                )
            elif tool_name == "get_media_views":
                return await self.game_tools.get_media_views(kwargs["entity_type"], kwargs["entity_id"])
            elif tool_name == "generate_random":
                return await self.game_tools.generate_random(
                    kwargs["type"], kwargs.get("min_val"), kwargs.get("max_val"),
                    kwargs.get("choices"), kwargs.get("seed")
                )
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_available_game_tools(self) -> List[str]:
        """Get list of available game state tools."""
        if not self.use_tools or not self.game_tools:
            return []
        
        return [
            "get_match_predictions",
            "get_reputation_info", 
            "get_head_to_head",
            "get_media_views",
            "generate_random"
        ]