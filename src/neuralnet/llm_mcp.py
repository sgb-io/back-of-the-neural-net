"""Enhanced LLM integration using game state query tools."""

import json
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .entities import GameWorld
from .events import MatchEvent
from .llm import LLMProvider, SoftStateUpdate
from .game_tools import GameStateTools


class ToolsLLMProvider(LLMProvider):
    """LLM provider that uses game state tools to query specific information instead of receiving full world."""
    
    def __init__(self, tools: GameStateTools) -> None:
        self.tools = tools
    
    async def analyze_match_events(
        self, 
        match_events: List[MatchEvent], 
        world: GameWorld
    ) -> List[SoftStateUpdate]:
        """Analyze match events using game state tools for context."""
        updates = []
        
        # Extract teams involved in the match
        teams_involved = set()
        
        for event in match_events:
            if hasattr(event, 'home_team_id'):
                teams_involved.add(event.home_team_id)
            if hasattr(event, 'away_team_id'):
                teams_involved.add(event.away_team_id)
            if hasattr(event, 'team'):
                teams_involved.add(event.team)
        
        # Use tools to get context and generate updates
        for team_id in teams_involved:
            team_updates = await self._analyze_team_performance(team_id, match_events)
            updates.extend(team_updates)
        
        # Analyze media reactions using tools
        media_updates = await self._analyze_media_reactions(teams_involved, match_events)
        updates.extend(media_updates)
        
        # Analyze staff and ownership reactions
        staff_updates = await self._analyze_staff_reactions(teams_involved, match_events)
        updates.extend(staff_updates)
        
        return updates
    
    async def analyze_season_progress(self, world: GameWorld) -> List[SoftStateUpdate]:
        """Analyze season progress using game state tools for targeted queries."""
        updates = []
        
        # Analyze each team's performance using tools
        for team_id in world.teams.keys():
            team_updates = await self._analyze_team_season(team_id)
            updates.extend(team_updates)
        
        # Analyze media sentiment changes
        media_updates = await self._analyze_media_sentiment_changes(world)
        updates.extend(media_updates)
        
        # Analyze owner/agent satisfaction
        entity_updates = await self._analyze_entity_satisfaction(world)
        updates.extend(entity_updates)
        
        return updates
    
    async def _analyze_team_performance(self, team_id: str, match_events: List[MatchEvent]) -> List[SoftStateUpdate]:
        """Analyze team performance in a match using MCP tools."""
        updates = []
        
        # Get team info and calculate performance impact
        team = self.mcp_server.world.get_team_by_id(team_id)
        if not team:
            return updates
        
        # Count goals scored and conceded in this match
        goals_scored = 0
        goals_conceded = 0
        cards_received = 0
        
        for event in match_events:
            if hasattr(event, 'event_type'):
                if event.event_type == "goal" and hasattr(event, 'team') and event.team == team_id:
                    goals_scored += 1
                elif event.event_type == "goal" and hasattr(event, 'team') and event.team != team_id:
                    goals_conceded += 1
                elif event.event_type in ["yellow_card", "red_card"] and hasattr(event, 'team') and event.team == team_id:
                    cards_received += 1
        
        # Calculate morale change based on performance
        morale_change = 0
        if goals_scored > goals_conceded:
            morale_change = min(5, goals_scored - goals_conceded + 2)  # Win bonus
        elif goals_scored < goals_conceded:
            morale_change = max(-5, goals_scored - goals_conceded - 2)  # Loss penalty
        else:
            morale_change = 1  # Small draw bonus
        
        # Penalty for too many cards
        if cards_received > 2:
            morale_change -= 1
        
        # Apply the update if there's a change
        if morale_change != 0:
            new_morale = max(1, min(100, team.team_morale + morale_change))
            updates.append(SoftStateUpdate(
                entity_type="team",
                entity_id=team_id,
                updates={"team_morale": new_morale},
                reasoning=f"Match performance: {goals_scored} goals scored, {goals_conceded} conceded, {cards_received} cards. Morale change: {morale_change}"
            ))
        
        return updates
    
    async def _analyze_media_reactions(self, teams_involved: set, match_events: List[MatchEvent]) -> List[SoftStateUpdate]:
        """Analyze media reactions to match events using game state tools."""
        updates = []
        
        for team_id in teams_involved:
            # Use tools to get current media views
            try:
                media_views_result = await self.tools.get_media_views("team", team_id)
                
                if "error" in media_views_result:
                    continue
                
                # Count significant events for this team
                significant_events = 0
                positive_events = 0
                
                for event in match_events:
                    if hasattr(event, 'team') and event.team == team_id:
                        significant_events += 1
                        if hasattr(event, 'event_type') and event.event_type == "goal":
                            positive_events += 1
                
                # Update media outlet biases based on events
                for outlet in self.tools.world.media_outlets.values():
                    if team_id in outlet.bias_towards_teams:
                        current_bias = outlet.bias_towards_teams[team_id]
                        
                        # Adjust bias slightly based on performance
                        if positive_events > significant_events / 2:
                            bias_change = min(2, positive_events)
                        else:
                            bias_change = max(-2, -significant_events)
                        
                        new_bias = max(-100, min(100, current_bias + bias_change))
                        
                        if new_bias != current_bias:
                            updates.append(SoftStateUpdate(
                                entity_type="media_outlet",
                                entity_id=outlet.id,
                                updates={"bias_towards_teams": {**outlet.bias_towards_teams, team_id: new_bias}},
                                reasoning=f"Adjusted bias towards {team_id} based on match performance using tools: {positive_events} positive events out of {significant_events}"
                            ))
                        
            except Exception as e:
                # In case of tool error, continue with next team
                continue
        
        return updates
    
    async def _analyze_staff_reactions(self, teams_involved: set, match_events: List[MatchEvent]) -> List[SoftStateUpdate]:
        """Analyze staff reactions to match results."""
        updates = []
        
        for team_id in teams_involved:
            # Get staff members for this team
            staff_members = [staff for staff in self.mcp_server.world.staff_members.values() 
                           if staff.team_id == team_id]
            
            # Determine match result for this team
            goals_scored = sum(1 for event in match_events 
                             if hasattr(event, 'event_type') and event.event_type == "goal" 
                             and hasattr(event, 'team') and event.team == team_id)
            
            goals_conceded = sum(1 for event in match_events 
                               if hasattr(event, 'event_type') and event.event_type == "goal" 
                               and hasattr(event, 'team') and event.team != team_id)
            
            # Calculate morale impact for staff
            if goals_scored > goals_conceded:
                morale_change = 3  # Win
            elif goals_scored < goals_conceded:
                morale_change = -2  # Loss
            else:
                morale_change = 1  # Draw
            
            for staff in staff_members:
                new_morale = max(1, min(100, staff.morale + morale_change))
                if new_morale != staff.morale:
                    updates.append(SoftStateUpdate(
                        entity_type="staff_member",
                        entity_id=staff.id,
                        updates={"morale": new_morale},
                        reasoning=f"Staff morale adjusted based on match result: {goals_scored}-{goals_conceded}"
                    ))
        
        return updates
    
    async def _analyze_team_performance(self, team_id: str, match_events: List[MatchEvent]) -> List[SoftStateUpdate]:
        """Analyze team performance in a match using game state tools."""
        updates = []
        
        # Get team info and calculate performance impact
        team = self.tools.world.get_team_by_id(team_id)
        if not team:
            return updates
        
        # Use tools to get match predictions context (this helps understand expected vs actual performance)
        # In a real implementation, this would be called before the match for comparison
        
        # Count goals scored and conceded in this match
        goals_scored = 0
        goals_conceded = 0
        cards_received = 0
        
        for event in match_events:
            if hasattr(event, 'event_type'):
                if event.event_type == "goal" and hasattr(event, 'team') and event.team == team_id:
                    goals_scored += 1
                elif event.event_type == "goal" and hasattr(event, 'team') and event.team != team_id:
                    goals_conceded += 1
                elif event.event_type in ["yellow_card", "red_card"] and hasattr(event, 'team') and event.team == team_id:
                    cards_received += 1
        
        # Calculate morale change based on performance
        morale_change = 0
        if goals_scored > goals_conceded:
            morale_change = min(5, goals_scored - goals_conceded + 2)  # Win bonus
        elif goals_scored < goals_conceded:
            morale_change = max(-5, goals_scored - goals_conceded - 2)  # Loss penalty
        else:
            morale_change = 1  # Small draw bonus
        
        # Penalty for too many cards
        if cards_received > 2:
            morale_change -= 1
        
        # Apply the update if there's a change
        if morale_change != 0:
            new_morale = max(1, min(100, team.team_morale + morale_change))
            updates.append(SoftStateUpdate(
                entity_type="team",
                entity_id=team_id,
                updates={"team_morale": new_morale},
                reasoning=f"Tools-based analysis - Match performance: {goals_scored} goals scored, {goals_conceded} conceded, {cards_received} cards. Morale change: {morale_change}"
            ))
        
        return updates
    
    async def _analyze_staff_reactions(self, teams_involved: set, match_events: List[MatchEvent]) -> List[SoftStateUpdate]:
        """Analyze staff reactions to match results using tools."""
        updates = []
        
        for team_id in teams_involved:
            # Get staff members for this team
            staff_members = [staff for staff in self.tools.world.staff_members.values() 
                           if staff.team_id == team_id]
            
            # Determine match result for this team
            goals_scored = sum(1 for event in match_events 
                             if hasattr(event, 'event_type') and event.event_type == "goal" 
                             and hasattr(event, 'team') and event.team == team_id)
            
            goals_conceded = sum(1 for event in match_events 
                               if hasattr(event, 'event_type') and event.event_type == "goal" 
                               and hasattr(event, 'team') and event.team != team_id)
            
            # Calculate morale impact for staff
            if goals_scored > goals_conceded:
                morale_change = 3  # Win
            elif goals_scored < goals_conceded:
                morale_change = -2  # Loss
            else:
                morale_change = 1  # Draw
            
            for staff in staff_members:
                new_morale = max(1, min(100, staff.morale + morale_change))
                if new_morale != staff.morale:
                    updates.append(SoftStateUpdate(
                        entity_type="staff_member",
                        entity_id=staff.id,
                        updates={"morale": new_morale},
                        reasoning=f"Tools-based analysis - Staff morale adjusted based on match result: {goals_scored}-{goals_conceded}"
                    ))
        
        return updates
    
    async def _analyze_team_season(self, team_id: str) -> List[SoftStateUpdate]:
        """Analyze team's season progress using game state tools."""
        updates = []
        
        try:
            # Get the team
            team = self.tools.world.get_team_by_id(team_id)
            if not team:
                return updates
            
            # Use tools to analyze the team's position relative to expectations
            league_teams = [t for t in self.tools.world.teams.values() if t.league == team.league]
            league_teams.sort(key=lambda t: (-t.points, -t.goal_difference))
            
            team_position = next((i for i, t in enumerate(league_teams) if t.id == team_id), -1) + 1
            total_teams = len(league_teams)
            
            # Adjust tactical familiarity based on position
            if team_position <= total_teams // 4:  # Top quarter
                tactical_change = 1
            elif team_position >= 3 * total_teams // 4:  # Bottom quarter
                tactical_change = -1
            else:
                tactical_change = 0
            
            if tactical_change != 0:
                new_tactical = max(1, min(100, team.tactical_familiarity + tactical_change))
                updates.append(SoftStateUpdate(
                    entity_type="team",
                    entity_id=team_id,
                    updates={"tactical_familiarity": new_tactical},
                    reasoning=f"Tools-based analysis - Tactical familiarity adjusted based on league position {team_position}/{total_teams}"
                ))
        
        except Exception:
            pass
        
        return updates
    
    async def _analyze_media_sentiment_changes(self, world: GameWorld) -> List[SoftStateUpdate]:
        """Analyze changes in media sentiment over time using tools."""
        updates = []
        
        # Use tools to get media views for a sample of teams and adjust accordingly
        import random
        
        sample_teams = list(world.teams.keys())[:3]  # Sample 3 teams
        
        for team_id in sample_teams:
            try:
                media_info = await self.tools.get_media_views("team", team_id)
                
                if "error" not in media_info:
                    # Randomly adjust some media outlet sensationalism based on "market response"
                    for outlet in world.media_outlets.values():
                        if random.random() < 0.05:  # 5% chance per team check
                            change = random.randint(-1, 1)
                            new_sensationalism = max(1, min(100, outlet.sensationalism + change))
                            
                            if new_sensationalism != outlet.sensationalism:
                                updates.append(SoftStateUpdate(
                                    entity_type="media_outlet",
                                    entity_id=outlet.id,
                                    updates={"sensationalism": new_sensationalism},
                                    reasoning="Tools-based analysis - Market-driven adjustment to editorial stance"
                                ))
            except Exception:
                continue
        
        return updates
    
    async def _analyze_entity_satisfaction(self, world: GameWorld) -> List[SoftStateUpdate]:
        """Analyze satisfaction changes for owners and agents using tools."""
        updates = []
        
        # Analyze club owner satisfaction
        sample_owners = list(world.club_owners.values())[:3]  # Sample some owners
        
        for owner in sample_owners:
            team = world.get_team_by_id(owner.team_id)
            if not team:
                continue
            
            # Use tools to get reputation info between owner and team
            try:
                reputation_info = await self.tools.get_reputation_info(
                    "club_owner", owner.id, "team", team.id
                )
                
                if "error" not in reputation_info:
                    # Calculate satisfaction based on team performance
                    if team.matches_played > 0:
                        win_rate = team.wins / team.matches_played
                        expected_win_rate = 0.4  # Expected win rate
                        
                        if win_rate > expected_win_rate + 0.2:
                            satisfaction_change = 2
                        elif win_rate < expected_win_rate - 0.2:
                            satisfaction_change = -2
                        else:
                            satisfaction_change = 0
                        
                        if satisfaction_change != 0:
                            new_satisfaction = max(1, min(100, owner.satisfaction + satisfaction_change))
                            updates.append(SoftStateUpdate(
                                entity_type="club_owner",
                                entity_id=owner.id,
                                updates={"satisfaction": new_satisfaction},
                                reasoning=f"Tools-based analysis - Owner satisfaction adjusted based on team win rate: {win_rate:.2f}"
                            ))
            except Exception:
                continue
        
        # Analyze player agent reputation
        sample_agents = list(world.player_agents.values())[:2]  # Sample some agents
        
        for agent in sample_agents:
            if agent.clients:
                # Calculate average form of clients
                total_form = 0
                client_count = 0
                
                for client_id in agent.clients:
                    player = world.get_player_by_id(client_id)
                    if player:
                        total_form += player.form
                        client_count += 1
                
                if client_count > 0:
                    avg_form = total_form / client_count
                    
                    if avg_form > 75:
                        reputation_change = 1
                    elif avg_form < 50:
                        reputation_change = -1
                    else:
                        reputation_change = 0
                    
                    if reputation_change != 0:
                        new_reputation = max(1, min(100, agent.reputation + reputation_change))
                        updates.append(SoftStateUpdate(
                            entity_type="player_agent",
                            entity_id=agent.id,
                            updates={"reputation": new_reputation},
                            reasoning=f"Tools-based analysis - Agent reputation adjusted based on client performance: avg form {avg_form:.1f}"
                        ))
        
        return updates
    
    async def generate_career_summary(
        self, 
        player_id: str, 
        world: GameWorld
    ) -> str:
        """Generate a career summary using game tools for context."""
        player = world.get_player_by_id(player_id)
        if not player:
            return "Player not found."
        
        # Use tools to get player context
        try:
            # This would use actual LLM analysis with tools in a real implementation
            # For now, provide a tools-based mock summary
            
            # Find the player's current team
            current_team = None
            for team in world.teams.values():
                if any(p.id == player_id for p in team.players):
                    current_team = team
                    break
            
            team_name = current_team.name if current_team else "Unknown Team"
            
            # Generate a summary using available data
            summary = f"""Based on our scouting analysis, {player.name} is a {player.age}-year-old {player.position.value} currently representing {team_name}. 

With an overall rating of {player.overall_rating}, our assessment shows a player who brings consistency and reliability to the squad. Their current form rating of {player.form} reflects their recent performances, while maintaining excellent fitness levels at {player.fitness}.

The player's attribute profile suggests they are well-suited to their {player.position.value} role, and they continue to be an important squad member this season."""
            
            return summary
            
        except Exception as e:
            # Fallback summary
            return f"{player.name} is a {player.age}-year-old {player.position.value} with an overall rating of {player.overall_rating}. They are an important member of the squad."
    
    async def generate_match_reports(
        self,
        match_events: List[MatchEvent],
        world: GameWorld,
        importance: str
    ) -> List["MediaStory"]:
        """Generate match reports using game tools for important matches."""
        # Import here to avoid circular imports
        from .llm import MediaStory
        
        if importance == "normal":
            return []
        
        # Use tools to get context and generate reports
        # For now, this is a simplified implementation
        # In a full implementation, this would use actual LLM calls with tool context
        
        # Get match information
        match_id = None
        home_score = 0
        away_score = 0
        match_ended = False
        
        for event in match_events:
            if hasattr(event, 'match_id'):
                match_id = event.match_id
            if hasattr(event, 'home_score') and hasattr(event, 'away_score'):
                home_score = event.home_score
                away_score = event.away_score
            # Check if match has actually ended
            if event.event_type == "MatchEnded":
                match_ended = True
        
        if not match_id:
            return []
        
        # CRITICAL: Only generate reports for matches that have actually ended
        if not match_ended:
            return []
        
        match = world.get_match_by_id(match_id)
        if not match:
            return []
        
        home_team = world.get_team_by_id(match.home_team_id)
        away_team = world.get_team_by_id(match.away_team_id)
        
        if not home_team or not away_team:
            return []
        
        # Generate reports using tools context
        stories = []
        outlets = list(world.media_outlets.values())[:2]  # Limit to 2 for tools-based approach
        
        for outlet in outlets:
            # Use tools to determine appropriate headline and sentiment
            if home_score > away_score:
                headline = f"Tools Analysis: {home_team.name} secures {importance} victory over {away_team.name}"
                base_sentiment = 20
            elif away_score > home_score:
                headline = f"Tools Analysis: {away_team.name} triumphs in {importance} clash with {home_team.name}"
                base_sentiment = -20
            else:
                headline = f"Tools Analysis: {importance} encounter ends in stalemate"
                base_sentiment = 0
            
            # Apply outlet bias
            home_bias = outlet.bias_towards_teams.get(home_team.id, 0)
            away_bias = outlet.bias_towards_teams.get(away_team.id, 0)
            
            if home_score > away_score:
                sentiment = base_sentiment + home_bias - away_bias
            elif away_score > home_score:
                sentiment = base_sentiment + away_bias - home_bias
            else:
                sentiment = base_sentiment + (home_bias + away_bias) // 2
            
            sentiment = max(-100, min(100, sentiment))
            
            story = MediaStory(
                media_outlet_id=outlet.id,
                headline=headline,
                story_type="match_report",
                entities_mentioned=[home_team.id, away_team.id],
                sentiment=sentiment,
                importance=importance
            )
            
            stories.append(story)
        
        return stories


class MockToolsLLMProvider(ToolsLLMProvider):
    """Mock version of Tools LLM provider for testing without complex tool usage."""
    
    async def analyze_match_events(
        self, 
        match_events: List[MatchEvent], 
        world: GameWorld
    ) -> List[SoftStateUpdate]:
        """Mock analysis that simulates tool usage."""
        updates = []
        
        # Simple mock: adjust team morale based on goals
        teams_involved = set()
        for event in match_events:
            if hasattr(event, 'team'):
                teams_involved.add(event.team)
        
        for team_id in teams_involved:
            team = world.get_team_by_id(team_id)
            if team:
                # Mock morale adjustment
                morale_change = 2  # Simplified positive change
                new_morale = min(100, team.team_morale + morale_change)
                
                updates.append(SoftStateUpdate(
                    entity_type="team",
                    entity_id=team_id,
                    updates={"team_morale": new_morale},
                    reasoning="Mock tools analysis: team participated in match"
                ))
        
        return updates
    
    async def analyze_season_progress(self, world: GameWorld) -> List[SoftStateUpdate]:
        """Mock season analysis."""
        # Return a few sample updates to demonstrate the system works
        updates = []
        
        # Mock update for first team
        if world.teams:
            first_team = next(iter(world.teams.values()))
            updates.append(SoftStateUpdate(
                entity_type="team",
                entity_id=first_team.id,
                updates={"tactical_familiarity": min(100, first_team.tactical_familiarity + 1)},
                reasoning="Mock tools analysis: gradual tactical improvement"
            ))
        
        return updates
    
    async def generate_career_summary(
        self, 
        player_id: str, 
        world: GameWorld
    ) -> str:
        """Generate a mock career summary for testing."""
        player = world.get_player_by_id(player_id)
        if not player:
            return "Player not found."
        
        # Find the player's current team
        current_team = None
        for team in world.teams.values():
            if any(p.id == player_id for p in team.players):
                current_team = team
                break
        
        team_name = current_team.name if current_team else "Unknown Team"
        
        # Generate a simple mock career summary
        return f"""Mock analysis: {player.name} is a {player.age}-year-old {player.position.value} currently playing for {team_name}. 

With an overall rating of {player.overall_rating}, they are considered a valuable squad member. Their current form of {player.form} and morale of {player.morale} indicate they are ready to contribute when called upon.

This mock summary demonstrates the career analysis system is working correctly."""
    
    async def generate_match_reports(
        self,
        match_events: List[MatchEvent],
        world: GameWorld,
        importance: str
    ) -> List["MediaStory"]:
        """Generate mock match reports for testing."""
        # Import here to avoid circular imports
        from .llm import MediaStory
        
        if importance == "normal":
            return []
        
        # Get match information
        match_id = None
        home_score = 0
        away_score = 0
        
        for event in match_events:
            if hasattr(event, 'match_id'):
                match_id = event.match_id
            if hasattr(event, 'home_score') and hasattr(event, 'away_score'):
                home_score = event.home_score
                away_score = event.away_score
        
        if not match_id:
            return []
        
        match = world.get_match_by_id(match_id)
        if not match:
            return []
        
        home_team = world.get_team_by_id(match.home_team_id)
        away_team = world.get_team_by_id(match.away_team_id)
        
        if not home_team or not away_team:
            return []
        
        # Generate a simple mock report
        stories = []
        outlets = list(world.media_outlets.values())[:1]  # Just one for mock
        
        if outlets:
            outlet = outlets[0]
            
            headline = f"Mock Report: {home_team.name} {home_score}-{away_score} {away_team.name} - {importance} encounter"
            
            story = MediaStory(
                media_outlet_id=outlet.id,
                headline=headline,
                story_type="match_report",
                entities_mentioned=[home_team.id, away_team.id],
                sentiment=0,  # Neutral for mock
                importance=importance
            )
            
            stories.append(story)
        
        return stories