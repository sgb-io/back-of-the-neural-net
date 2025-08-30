"""LM Studio LLM provider for local inference."""

import json
import asyncio
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel, ValidationError

from .config import LLMConfig
from .entities import GameWorld
from .events import MatchEvent
from .llm import LLMProvider, SoftStateUpdate


class LMStudioProvider(LLMProvider):
    """LLM provider that uses local LM Studio server for inference."""

    def __init__(self, config: LLMConfig) -> None:
        self.config = config
        self.client = httpx.AsyncClient(
            base_url=config.lmstudio_base_url,
            timeout=config.timeout
        )

    async def analyze_match_events(
        self, 
        match_events: List[MatchEvent], 
        world: GameWorld
    ) -> List[SoftStateUpdate]:
        """Analyze match events using LM Studio and propose soft state updates."""
        
        # Build context about the match events
        events_summary = self._summarize_match_events(match_events)
        if not events_summary:
            return []
        
        # Get team information for context
        teams_context = self._get_teams_context(match_events, world)
        
        prompt = self._build_match_analysis_prompt(events_summary, teams_context)
        
        try:
            response = await self._make_llm_request(prompt)
            return self._parse_soft_state_updates(response)
        except Exception as e:
            print(f"Warning: LM Studio analysis failed: {e}")
            return []

    async def analyze_season_progress(
        self, 
        world: GameWorld
    ) -> List[SoftStateUpdate]:
        """Analyze overall season progress using LM Studio."""
        
        # Build season context
        season_context = self._get_season_context(world)
        prompt = self._build_season_analysis_prompt(season_context)
        
        try:
            response = await self._make_llm_request(prompt)
            return self._parse_soft_state_updates(response)
        except Exception as e:
            print(f"Warning: LM Studio season analysis failed: {e}")
            return []

    def _summarize_match_events(self, match_events: List[MatchEvent]) -> str:
        """Create a text summary of match events."""
        if not match_events:
            return ""
        
        summary_parts = []
        
        for event in match_events:
            event_type = event.__class__.__name__
            
            if hasattr(event, 'minute'):
                minute_info = f"[{event.minute}']"
            else:
                minute_info = ""
            
            if hasattr(event, 'scorer') and event.scorer:
                summary_parts.append(f"{minute_info} GOAL: {event.scorer}")
            elif hasattr(event, 'player') and hasattr(event, 'reason'):
                card_type = "RED CARD" if "Red" in event_type else "YELLOW CARD"
                summary_parts.append(f"{minute_info} {card_type}: {event.player} ({event.reason})")
            elif hasattr(event, 'player_in') and hasattr(event, 'player_out'):
                summary_parts.append(f"{minute_info} SUBSTITUTION: {event.player_out} → {event.player_in}")
        
        return "\n".join(summary_parts)

    def _get_teams_context(self, match_events: List[MatchEvent], world: GameWorld) -> str:
        """Get context about the teams involved in the match."""
        if not match_events:
            return ""
        
        # Extract team info from first event that has match_id
        match_id = None
        for event in match_events:
            if hasattr(event, 'match_id'):
                match_id = event.match_id
                break
        
        if not match_id or match_id not in world.matches:
            return ""
        
        match = world.matches[match_id]
        home_team = world.teams.get(match.home_team_id)
        away_team = world.teams.get(match.away_team_id)
        
        if not home_team or not away_team:
            return ""
        
        context = f"Match: {home_team.name} vs {away_team.name}\n"
        context += f"Home team form: {getattr(home_team, 'form', 50)}/100\n"
        context += f"Away team form: {getattr(away_team, 'form', 50)}/100\n"
        
        return context

    def _get_season_context(self, world: GameWorld) -> str:
        """Get context about the current season state."""
        context_parts = []
        
        # League standings context
        for league_id, league in world.leagues.items():
            context_parts.append(f"League: {league.name}")
            context_parts.append(f"Current matchday: {league.current_matchday}")
            
            # Get some team standings
            teams_data = []
            for team_id in league.teams:
                if team_id in world.teams:
                    team = world.teams[team_id]
                    teams_data.append({
                        'name': team.name,
                        'form': getattr(team, 'form', 50)
                    })
            
            if teams_data:
                context_parts.append("Top teams by form:")
                sorted_teams = sorted(teams_data, key=lambda x: x['form'], reverse=True)[:3]
                for i, team in enumerate(sorted_teams, 1):
                    context_parts.append(f"  {i}. {team['name']} (Form: {team['form']})")
        
        return "\n".join(context_parts)

    def _build_match_analysis_prompt(self, events_summary: str, teams_context: str) -> str:
        """Build prompt for match event analysis."""
        prompt = f"""You are analyzing a football match to determine how events should affect player and team psychology.

{teams_context}

Match Events:
{events_summary}

Based on these events, suggest soft state updates for players and teams. Consider:
- Goal scorers should get form boosts
- Players receiving cards (especially red cards) should lose form and morale
- Winning/losing teams should have morale adjustments
- Individual player performances affect their psychological state

Respond with a JSON array of updates. Each update should have:
- entity_type: "player" or "team"  
- entity_id: the player/team name
- updates: object with attributes like {{"form": 85, "morale": 75}}
- reasoning: explanation for the changes

Keep form and morale values between 1-100. Be conservative with changes (typically 5-15 point adjustments).

Example response:
[
  {{
    "entity_type": "player",
    "entity_id": "John Smith",
    "updates": {{"form": 85}},
    "reasoning": "Form boost for scoring the winning goal"
  }}
]

Response:"""
        
        return prompt

    def _build_season_analysis_prompt(self, season_context: str) -> str:
        """Build prompt for season progress analysis."""
        prompt = f"""You are analyzing the overall season progress to update team and player psychology.

Season Context:
{season_context}

Based on the current season state, suggest soft state updates. Consider:
- Teams performing above/below expectations
- Form trends affecting team morale
- Pressure on underperforming teams
- Confidence boosts for successful teams

Respond with a JSON array of updates focusing on team-level adjustments:
- entity_type: "team"
- entity_id: team name
- updates: object with attributes like {{"form": 70, "morale": 80}}
- reasoning: explanation for the changes

Keep values between 1-100. Make small, realistic adjustments (2-8 points typically).

Example response:
[
  {{
    "entity_type": "team", 
    "entity_id": "Arsenal United",
    "updates": {{"morale": 72}},
    "reasoning": "Steady mid-table performance maintaining confidence"
  }}
]

Response:"""
        
        return prompt

    async def _make_llm_request(self, prompt: str) -> str:
        """Make a request to LM Studio API."""
        payload = {
            "model": self.config.lmstudio_model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "stream": False
        }
        
        try:
            response = await self.client.post("/chat/completions", json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except httpx.HTTPStatusError as e:
            raise Exception(f"LM Studio HTTP error: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            raise Exception(f"LM Studio connection error: {e}")
        except (KeyError, IndexError) as e:
            raise Exception(f"Invalid LM Studio response format: {e}")

    def _parse_soft_state_updates(self, llm_response: str) -> List[SoftStateUpdate]:
        """Parse LLM response into SoftStateUpdate objects."""
        try:
            # Extract JSON from response (in case there's extra text)
            response_text = llm_response.strip()
            
            # Find JSON array in the response
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']') + 1
            
            if start_idx == -1 or end_idx == 0:
                print(f"Warning: No JSON array found in LLM response: {response_text}")
                return []
            
            json_text = response_text[start_idx:end_idx]
            updates_data = json.loads(json_text)
            
            updates = []
            for update_data in updates_data:
                try:
                    update = SoftStateUpdate(
                        entity_type=update_data["entity_type"],
                        entity_id=update_data["entity_id"],
                        updates=update_data["updates"],
                        reasoning=update_data.get("reasoning", "LM Studio analysis")
                    )
                    updates.append(update)
                except (KeyError, ValidationError) as e:
                    print(f"Warning: Invalid update format: {update_data}, error: {e}")
                    continue
            
            return updates
            
        except json.JSONDecodeError as e:
            print(f"Warning: Failed to parse LLM response as JSON: {e}")
            print(f"Response was: {llm_response}")
            return []
        except Exception as e:
            print(f"Warning: Unexpected error parsing LLM response: {e}")
            return []

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.aclose()