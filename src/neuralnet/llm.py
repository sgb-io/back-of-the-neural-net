"""LLM integration for soft state management."""

import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .entities import GameWorld, Player, Team, ClubOwner, MediaOutlet, PlayerAgent, StaffMember
from .events import Event, MatchEvent


class SoftStateUpdate(BaseModel):
    """Represents an update to soft state from LLM analysis."""
    entity_type: str  # "player", "team", "club_owner", "media_outlet", "player_agent", "staff_member"
    entity_id: str
    updates: Dict[str, Any]
    reasoning: str = Field(description="LLM's reasoning for the changes")


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    async def analyze_match_events(
        self, 
        match_events: List[MatchEvent], 
        world: GameWorld
    ) -> List[SoftStateUpdate]:
        """Analyze match events and propose soft state updates."""
        pass
    
    @abstractmethod
    async def analyze_season_progress(
        self, 
        world: GameWorld
    ) -> List[SoftStateUpdate]:
        """Analyze overall season progress and propose updates."""
        pass


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing and development."""
    
    async def analyze_match_events(
        self, 
        match_events: List[MatchEvent], 
        world: GameWorld
    ) -> List[SoftStateUpdate]:
        """Mock analysis that makes simple changes based on match events."""
        updates = []
        
        # Track goals and cards for each player
        player_stats = {}
        
        for event in match_events:
            if hasattr(event, 'scorer') and event.scorer:
                # Goal scorer gets form boost
                player_id = self._find_player_by_name(event.scorer, world)
                if player_id:
                    updates.append(SoftStateUpdate(
                        entity_type="player",
                        entity_id=player_id,
                        updates={"form": min(100, self._get_player_form(player_id, world) + 5)},
                        reasoning=f"Form boost for scoring a goal in minute {event.minute}"
                    ))
            
            if hasattr(event, 'player') and hasattr(event, 'reason'):
                # Player with card gets morale/form decrease
                player_id = self._find_player_by_name(event.player, world)
                if player_id and "Red" in event.__class__.__name__:
                    updates.append(SoftStateUpdate(
                        entity_type="player",
                        entity_id=player_id,
                        updates={
                            "form": max(1, self._get_player_form(player_id, world) - 10),
                            "morale": max(1, self._get_player_morale(player_id, world) - 15)
                        },
                        reasoning=f"Form and morale decrease for receiving red card: {event.reason}"
                    ))
        
        return updates
    
    async def analyze_season_progress(
        self, 
        world: GameWorld
    ) -> List[SoftStateUpdate]:
        """Mock season analysis that adjusts team morale based on league position."""
        updates = []
        
        for league_id, league in world.leagues.items():
            table = world.get_league_table(league_id)
            
            for position, team in enumerate(table, 1):
                # Top teams get morale boost, bottom teams get decrease
                current_morale = team.team_morale
                
                if position <= 3:  # Top 3
                    new_morale = min(100, current_morale + 2)
                    reasoning = f"Morale boost for being in top 3 (position {position})"
                elif position >= len(table) - 2:  # Bottom 3
                    new_morale = max(1, current_morale - 3)
                    reasoning = f"Morale decrease for being in bottom 3 (position {position})"
                else:
                    continue  # Mid-table teams unchanged
                
                updates.append(SoftStateUpdate(
                    entity_type="team",
                    entity_id=team.id,
                    updates={"team_morale": new_morale},
                    reasoning=reasoning
                ))
                
                # Update club owners based on team performance
                owners = world.get_club_owners_for_team(team.id)
                for owner in owners:
                    if position <= 3:  # Good performance
                        new_patience = min(100, owner.patience + 1)
                        new_approval = min(100, owner.public_approval + 3)
                        updates.append(SoftStateUpdate(
                            entity_type="club_owner",
                            entity_id=owner.id,
                            updates={"patience": new_patience, "public_approval": new_approval},
                            reasoning=f"Owner satisfaction from team's good performance (position {position})"
                        ))
                    elif position >= len(table) - 2:  # Poor performance
                        new_patience = max(1, owner.patience - 2)
                        new_approval = max(1, owner.public_approval - 5)
                        updates.append(SoftStateUpdate(
                            entity_type="club_owner",
                            entity_id=owner.id,
                            updates={"patience": new_patience, "public_approval": new_approval},
                            reasoning=f"Owner frustration from team's poor performance (position {position})"
                        ))
                
                # Update staff morale based on team performance
                staff = world.get_staff_for_team(team.id)
                for staff_member in staff:
                    if position <= 5:  # Good performance
                        new_morale = min(100, staff_member.morale + 1)
                        new_rapport = min(100, staff_member.team_rapport + 1)
                        updates.append(SoftStateUpdate(
                            entity_type="staff_member",
                            entity_id=staff_member.id,
                            updates={"morale": new_morale, "team_rapport": new_rapport},
                            reasoning=f"Staff satisfaction from team's good performance"
                        ))
                    elif position >= len(table) - 3:  # Poor performance
                        new_morale = max(1, staff_member.morale - 2)
                        updates.append(SoftStateUpdate(
                            entity_type="staff_member",
                            entity_id=staff_member.id,
                            updates={"morale": new_morale},
                            reasoning=f"Staff concern from team's poor performance"
                        ))
        
        # Update media narratives based on interesting stories
        for outlet in world.media_outlets.values():
            # Occasionally generate new stories or update sensationalism
            import random
            if random.random() < 0.3:  # 30% chance to update
                new_sensationalism = max(1, min(100, outlet.sensationalism + random.randint(-5, 5)))
                updates.append(SoftStateUpdate(
                    entity_type="media_outlet",
                    entity_id=outlet.id,
                    updates={"sensationalism": new_sensationalism},
                    reasoning="Media outlet adjusting editorial stance based on market response"
                ))
        
        # Update player agents' reputation based on client performance
        for agent in world.player_agents.values():
            if agent.clients:
                total_form = 0
                client_count = 0
                for client_id in agent.clients:
                    player = world.get_player_by_id(client_id)
                    if player:
                        total_form += player.form
                        client_count += 1
                
                if client_count > 0:
                    avg_form = total_form / client_count
                    if avg_form > 70:  # Clients performing well
                        new_reputation = min(100, agent.reputation + 1)
                        updates.append(SoftStateUpdate(
                            entity_type="player_agent",
                            entity_id=agent.id,
                            updates={"reputation": new_reputation},
                            reasoning="Agent reputation boost from client success"
                        ))
                    elif avg_form < 40:  # Clients struggling
                        new_reputation = max(1, agent.reputation - 1)
                        updates.append(SoftStateUpdate(
                            entity_type="player_agent",
                            entity_id=agent.id,
                            updates={"reputation": new_reputation},
                            reasoning="Agent reputation decline from client struggles"
                        ))
        
        return updates
    
    def _find_player_by_name(self, name: str, world: GameWorld) -> Optional[str]:
        """Find a player ID by name."""
        for player_id, player in world.players.items():
            if player.name == name:
                return player_id
        return None
    
    def _get_player_form(self, player_id: str, world: GameWorld) -> int:
        """Get current player form."""
        player = world.get_player_by_id(player_id)
        return player.form if player else 50
    
    def _get_player_morale(self, player_id: str, world: GameWorld) -> int:
        """Get current player morale."""
        player = world.get_player_by_id(player_id)
        return player.morale if player else 50


class SoftStateValidator:
    """Validates and clamps LLM-proposed soft state updates."""
    
    def validate_update(self, update: SoftStateUpdate, world: GameWorld) -> bool:
        """Validate that an update is valid and safe to apply."""
        if update.entity_type == "player":
            return self._validate_player_update(update, world)
        elif update.entity_type == "team":
            return self._validate_team_update(update, world)
        elif update.entity_type == "club_owner":
            return self._validate_club_owner_update(update, world)
        elif update.entity_type == "media_outlet":
            return self._validate_media_outlet_update(update, world)
        elif update.entity_type == "player_agent":
            return self._validate_player_agent_update(update, world)
        elif update.entity_type == "staff_member":
            return self._validate_staff_member_update(update, world)
        return False
    
    def _validate_player_update(self, update: SoftStateUpdate, world: GameWorld) -> bool:
        """Validate a player update."""
        player = world.get_player_by_id(update.entity_id)
        if not player:
            return False
        
        # Clamp all values to valid ranges
        for key, value in update.updates.items():
            if key in ["form", "morale", "fitness"]:
                if not isinstance(value, (int, float)) or value < 1 or value > 100:
                    return False
        
        return True
    
    def _validate_team_update(self, update: SoftStateUpdate, world: GameWorld) -> bool:
        """Validate a team update."""
        team = world.get_team_by_id(update.entity_id)
        if not team:
            return False
        
        # Clamp all values to valid ranges
        for key, value in update.updates.items():
            if key in ["team_morale", "tactical_familiarity"]:
                if not isinstance(value, (int, float)) or value < 1 or value > 100:
                    return False
        
        return True
    
    def _validate_club_owner_update(self, update: SoftStateUpdate, world: GameWorld) -> bool:
        """Validate a club owner update."""
        owner = world.get_club_owner_by_id(update.entity_id)
        if not owner:
            return False
        
        # Clamp all values to valid ranges
        for key, value in update.updates.items():
            if key in ["ambition", "patience", "public_approval"]:
                if not isinstance(value, (int, float)) or value < 1 or value > 100:
                    return False
        
        return True
    
    def _validate_media_outlet_update(self, update: SoftStateUpdate, world: GameWorld) -> bool:
        """Validate a media outlet update."""
        outlet = world.get_media_outlet_by_id(update.entity_id)
        if not outlet:
            return False
        
        # Clamp all values to valid ranges
        for key, value in update.updates.items():
            if key == "sensationalism":
                if not isinstance(value, (int, float)) or value < 1 or value > 100:
                    return False
            elif key == "bias_towards_teams":
                if not isinstance(value, dict):
                    return False
                for team_id, bias in value.items():
                    if not isinstance(bias, (int, float)) or bias < -100 or bias > 100:
                        return False
            elif key == "active_stories":
                if not isinstance(value, list):
                    return False
        
        return True
    
    def _validate_player_agent_update(self, update: SoftStateUpdate, world: GameWorld) -> bool:
        """Validate a player agent update."""
        agent = world.get_player_agent_by_id(update.entity_id)
        if not agent:
            return False
        
        # Clamp all values to valid ranges
        for key, value in update.updates.items():
            if key in ["reputation", "aggressiveness"]:
                if not isinstance(value, (int, float)) or value < 1 or value > 100:
                    return False
            elif key == "clients":
                if not isinstance(value, list):
                    return False
        
        return True
    
    def _validate_staff_member_update(self, update: SoftStateUpdate, world: GameWorld) -> bool:
        """Validate a staff member update."""
        staff = world.get_staff_member_by_id(update.entity_id)
        if not staff:
            return False
        
        # Clamp all values to valid ranges
        for key, value in update.updates.items():
            if key in ["morale", "team_rapport"]:
                if not isinstance(value, (int, float)) or value < 1 or value > 100:
                    return False
        
        return True
    
    def apply_update(self, update: SoftStateUpdate, world: GameWorld) -> bool:
        """Apply a validated update to the world state."""
        if not self.validate_update(update, world):
            return False
        
        if update.entity_type == "player":
            player = world.get_player_by_id(update.entity_id)
            if player:
                for key, value in update.updates.items():
                    if hasattr(player, key):
                        setattr(player, key, value)
                return True
        
        elif update.entity_type == "team":
            team = world.get_team_by_id(update.entity_id)
            if team:
                for key, value in update.updates.items():
                    if hasattr(team, key):
                        setattr(team, key, value)
                return True
        
        elif update.entity_type == "club_owner":
            owner = world.get_club_owner_by_id(update.entity_id)
            if owner:
                for key, value in update.updates.items():
                    if hasattr(owner, key):
                        setattr(owner, key, value)
                return True
        
        elif update.entity_type == "media_outlet":
            outlet = world.get_media_outlet_by_id(update.entity_id)
            if outlet:
                for key, value in update.updates.items():
                    if hasattr(outlet, key):
                        setattr(outlet, key, value)
                return True
        
        elif update.entity_type == "player_agent":
            agent = world.get_player_agent_by_id(update.entity_id)
            if agent:
                for key, value in update.updates.items():
                    if hasattr(agent, key):
                        setattr(agent, key, value)
                return True
        
        elif update.entity_type == "staff_member":
            staff = world.get_staff_member_by_id(update.entity_id)
            if staff:
                for key, value in update.updates.items():
                    if hasattr(staff, key):
                        setattr(staff, key, value)
                return True
        
        return False


class BrainOrchestrator:
    """Orchestrates LLM analysis and soft state updates."""
    
    def __init__(self, llm_provider: LLMProvider, validator: Optional[SoftStateValidator] = None) -> None:
        self.llm_provider = llm_provider
        self.validator = validator or SoftStateValidator()
    
    async def process_match_events(
        self, 
        match_events: List[MatchEvent], 
        world: GameWorld
    ) -> List[SoftStateUpdate]:
        """Process match events through LLM and apply valid updates."""
        proposed_updates = await self.llm_provider.analyze_match_events(match_events, world)
        
        applied_updates = []
        for update in proposed_updates:
            if self.validator.apply_update(update, world):
                applied_updates.append(update)
        
        return applied_updates
    
    async def process_season_progress(self, world: GameWorld) -> List[SoftStateUpdate]:
        """Process season progress through LLM and apply valid updates."""
        proposed_updates = await self.llm_provider.analyze_season_progress(world)
        
        applied_updates = []
        for update in proposed_updates:
            if self.validator.apply_update(update, world):
                applied_updates.append(update)
        
        return applied_updates