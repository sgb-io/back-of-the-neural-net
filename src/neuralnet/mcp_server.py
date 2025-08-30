"""MCP Server for providing game state query tools to LLMs."""

import random
from typing import Any, Dict, List, Optional, Tuple

from mcp.server import Server
from mcp.types import Tool, TextContent
from pydantic import BaseModel

from .entities import GameWorld, Team, Player, Match


class MCPGameServer:
    """MCP server that provides game state query tools for LLMs."""
    
    def __init__(self, world: GameWorld) -> None:
        self.world = world
        self.server = Server("football-game")
        self._register_tools()
    
    def _register_tools(self) -> None:
        """Register all available tools with the MCP server."""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List all available tools."""
            return [
                Tool(
                    name="get_match_predictions",
                    description="Get potential outcomes (win chance, score predictions) for a match",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "home_team_id": {"type": "string", "description": "ID of the home team"},
                            "away_team_id": {"type": "string", "description": "ID of the away team"}
                        },
                        "required": ["home_team_id", "away_team_id"]
                    }
                ),
                Tool(
                    name="get_reputation_info",
                    description="Get reputation information about a club/person in relation to another",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "entity_type": {"type": "string", "enum": ["team", "player", "club_owner", "staff_member", "player_agent"], "description": "Type of entity"},
                            "entity_id": {"type": "string", "description": "ID of the entity"},
                            "relation_type": {"type": "string", "enum": ["team", "player", "club_owner", "staff_member", "player_agent"], "description": "Type of related entity"},
                            "relation_id": {"type": "string", "description": "ID of the related entity"}
                        },
                        "required": ["entity_type", "entity_id", "relation_type", "relation_id"]
                    }
                ),
                Tool(
                    name="get_head_to_head",
                    description="Get recent head-to-head results between two teams",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "team1_id": {"type": "string", "description": "ID of the first team"},
                            "team2_id": {"type": "string", "description": "ID of the second team"},
                            "limit": {"type": "integer", "default": 5, "description": "Number of recent matches to return"}
                        },
                        "required": ["team1_id", "team2_id"]
                    }
                ),
                Tool(
                    name="get_media_views",
                    description="Get current media views about a person or club",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "entity_type": {"type": "string", "enum": ["team", "player", "club_owner", "staff_member"], "description": "Type of entity"},
                            "entity_id": {"type": "string", "description": "ID of the entity"}
                        },
                        "required": ["entity_type", "entity_id"]
                    }
                ),
                Tool(
                    name="generate_random",
                    description="Generate random values to help add randomness to outcomes",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "enum": ["float", "int", "choice", "boolean"], "description": "Type of random value"},
                            "min_val": {"type": "number", "description": "Minimum value for int/float"},
                            "max_val": {"type": "number", "description": "Maximum value for int/float"},
                            "choices": {"type": "array", "items": {"type": "string"}, "description": "Options for choice type"},
                            "seed": {"type": "integer", "description": "Optional seed for reproducibility"}
                        },
                        "required": ["type"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls."""
            if name == "get_match_predictions":
                return await self._get_match_predictions(arguments)
            elif name == "get_reputation_info":
                return await self._get_reputation_info(arguments)
            elif name == "get_head_to_head":
                return await self._get_head_to_head(arguments)
            elif name == "get_media_views":
                return await self._get_media_views(arguments)
            elif name == "generate_random":
                return await self._generate_random(arguments)
            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    async def _get_match_predictions(self, args: Dict[str, Any]) -> List[TextContent]:
        """Get match predictions based on team stats and current form."""
        home_team_id = args["home_team_id"]
        away_team_id = args["away_team_id"]
        
        home_team = self.world.get_team_by_id(home_team_id)
        away_team = self.world.get_team_by_id(away_team_id)
        
        if not home_team or not away_team:
            return [TextContent(type="text", text="One or both teams not found")]
        
        # Calculate basic predictions based on team stats
        home_strength = self._calculate_team_strength(home_team)
        away_strength = self._calculate_team_strength(away_team)
        
        # Home advantage
        home_strength *= 1.1
        
        total_strength = home_strength + away_strength
        home_win_chance = (home_strength / total_strength) * 100
        away_win_chance = (away_strength / total_strength) * 100
        draw_chance = 100 - home_win_chance - away_win_chance
        
        # Adjust for draw probability (football has significant draw chance)
        draw_factor = 0.25
        home_win_chance *= (1 - draw_factor)
        away_win_chance *= (1 - draw_factor)
        draw_chance = draw_factor * 100
        
        # Predict likely score ranges
        home_goals_avg = self._predict_goals(home_team, away_team, True)
        away_goals_avg = self._predict_goals(away_team, home_team, False)
        
        result = {
            "home_team": home_team.name,
            "away_team": away_team.name,
            "win_probabilities": {
                "home_win": round(home_win_chance, 1),
                "draw": round(draw_chance, 1),
                "away_win": round(away_win_chance, 1)
            },
            "predicted_score": {
                "home_goals": round(home_goals_avg, 1),
                "away_goals": round(away_goals_avg, 1)
            },
            "factors": {
                "home_strength": round(home_strength, 2),
                "away_strength": round(away_strength, 2),
                "home_form": home_team.team_morale,
                "away_form": away_team.team_morale
            }
        }
        
        return [TextContent(type="text", text=str(result))]
    
    async def _get_reputation_info(self, args: Dict[str, Any]) -> List[TextContent]:
        """Get reputation information between entities."""
        entity_type = args["entity_type"]
        entity_id = args["entity_id"]
        relation_type = args["relation_type"]
        relation_id = args["relation_id"]
        
        # Get the entities
        entity = self._get_entity(entity_type, entity_id)
        relation = self._get_entity(relation_type, relation_id)
        
        if not entity or not relation:
            return [TextContent(type="text", text="One or both entities not found")]
        
        reputation_info = {
            "entity": {"type": entity_type, "id": entity_id, "name": getattr(entity, "name", "Unknown")},
            "relation": {"type": relation_type, "id": relation_id, "name": getattr(relation, "name", "Unknown")},
            "reputation_factors": self._analyze_reputation(entity, relation, entity_type, relation_type)
        }
        
        return [TextContent(type="text", text=str(reputation_info))]
    
    async def _get_head_to_head(self, args: Dict[str, Any]) -> List[TextContent]:
        """Get recent head-to-head results between teams."""
        team1_id = args["team1_id"]
        team2_id = args["team2_id"]
        limit = args.get("limit", 5)
        
        team1 = self.world.get_team_by_id(team1_id)
        team2 = self.world.get_team_by_id(team2_id)
        
        if not team1 or not team2:
            return [TextContent(type="text", text="One or both teams not found")]
        
        # Find matches between these teams (in a real implementation, this would query a match history)
        h2h_matches = []
        for match in self.world.matches.values():
            if ((match.home_team_id == team1_id and match.away_team_id == team2_id) or
                (match.home_team_id == team2_id and match.away_team_id == team1_id)) and match.finished:
                h2h_matches.append(match)
        
        # Sort by most recent (this is simplified - in reality you'd sort by date)
        h2h_matches = h2h_matches[-limit:]
        
        results = []
        team1_wins = 0
        team2_wins = 0
        draws = 0
        
        for match in h2h_matches:
            home_team = self.world.get_team_by_id(match.home_team_id)
            away_team = self.world.get_team_by_id(match.away_team_id)
            
            result_info = {
                "home_team": home_team.name,
                "away_team": away_team.name,
                "score": f"{match.home_score}-{match.away_score}",
                "matchday": match.matchday
            }
            results.append(result_info)
            
            # Count wins for each team
            if match.home_score > match.away_score:
                if match.home_team_id == team1_id:
                    team1_wins += 1
                else:
                    team2_wins += 1
            elif match.away_score > match.home_score:
                if match.away_team_id == team1_id:
                    team1_wins += 1
                else:
                    team2_wins += 1
            else:
                draws += 1
        
        h2h_summary = {
            "team1": team1.name,
            "team2": team2.name,
            "recent_matches": results,
            "head_to_head_record": {
                f"{team1.name}_wins": team1_wins,
                f"{team2.name}_wins": team2_wins,
                "draws": draws,
                "total_matches": len(h2h_matches)
            }
        }
        
        return [TextContent(type="text", text=str(h2h_summary))]
    
    async def _get_media_views(self, args: Dict[str, Any]) -> List[TextContent]:
        """Get current media views about an entity."""
        entity_type = args["entity_type"]
        entity_id = args["entity_id"]
        
        entity = self._get_entity(entity_type, entity_id)
        if not entity:
            return [TextContent(type="text", text="Entity not found")]
        
        media_views = []
        
        for outlet in self.world.media_outlets.values():
            bias = 0
            if entity_type == "team" and entity_id in outlet.bias_towards_teams:
                bias = outlet.bias_towards_teams[entity_id]
            
            # Generate view based on outlet characteristics and bias
            view = {
                "outlet_name": outlet.name,
                "outlet_type": outlet.outlet_type,
                "reach": outlet.reach,
                "credibility": outlet.credibility,
                "bias": bias,
                "sensationalism": outlet.sensationalism,
                "current_narrative": self._generate_media_narrative(outlet, entity, bias)
            }
            media_views.append(view)
        
        media_summary = {
            "entity": {"type": entity_type, "name": getattr(entity, "name", "Unknown")},
            "media_coverage": media_views,
            "overall_sentiment": self._calculate_overall_sentiment(media_views)
        }
        
        return [TextContent(type="text", text=str(media_summary))]
    
    async def _generate_random(self, args: Dict[str, Any]) -> List[TextContent]:
        """Generate random values for LLM use."""
        random_type = args["type"]
        seed = args.get("seed")
        
        if seed is not None:
            random.seed(seed)
        
        result = None
        
        if random_type == "float":
            min_val = args.get("min_val", 0.0)
            max_val = args.get("max_val", 1.0)
            result = random.uniform(min_val, max_val)
        
        elif random_type == "int":
            min_val = args.get("min_val", 0)
            max_val = args.get("max_val", 100)
            result = random.randint(int(min_val), int(max_val))
        
        elif random_type == "choice":
            choices = args.get("choices", [])
            if choices:
                result = random.choice(choices)
            else:
                result = "No choices provided"
        
        elif random_type == "boolean":
            result = random.choice([True, False])
        
        else:
            result = f"Unknown random type: {random_type}"
        
        return [TextContent(type="text", text=str(result))]
    
    def _calculate_team_strength(self, team: Team) -> float:
        """Calculate overall team strength based on various factors."""
        # Base strength from player ratings
        if team.players:
            avg_player_rating = sum(p.overall_rating for p in team.players) / len(team.players)
        else:
            avg_player_rating = 70  # Default if no players
        
        # Factor in team morale and tactical familiarity
        morale_factor = team.team_morale / 100.0
        tactical_factor = team.tactical_familiarity / 100.0
        
        # Factor in recent form (based on recent results)
        form_factor = self._calculate_form(team)
        
        strength = avg_player_rating * morale_factor * tactical_factor * form_factor
        return max(strength, 10.0)  # Minimum strength floor
    
    def _predict_goals(self, attacking_team: Team, defending_team: Team, is_home: bool) -> float:
        """Predict likely goals for a team in a match."""
        attack_strength = self._calculate_team_strength(attacking_team)
        defense_strength = self._calculate_team_strength(defending_team)
        
        # Home advantage
        if is_home:
            attack_strength *= 1.1
        
        # Goals per game based on strength differential
        goal_base = 1.5  # Average goals per team per game
        strength_ratio = attack_strength / defense_strength
        
        predicted_goals = goal_base * strength_ratio
        return max(0.1, min(predicted_goals, 5.0))  # Cap between 0.1 and 5
    
    def _calculate_form(self, team: Team) -> float:
        """Calculate team form based on recent results."""
        if team.matches_played == 0:
            return 1.0
        
        # Simple form calculation based on win percentage
        win_rate = team.wins / team.matches_played if team.matches_played > 0 else 0.5
        form = 0.8 + (win_rate * 0.4)  # Scale between 0.8 and 1.2
        return form
    
    def _get_entity(self, entity_type: str, entity_id: str) -> Optional[Any]:
        """Get an entity by type and ID."""
        if entity_type == "team":
            return self.world.get_team_by_id(entity_id)
        elif entity_type == "player":
            return self.world.get_player_by_id(entity_id)
        elif entity_type == "club_owner":
            return self.world.get_club_owner_by_id(entity_id)
        elif entity_type == "staff_member":
            return self.world.get_staff_member_by_id(entity_id)
        elif entity_type == "player_agent":
            return self.world.get_player_agent_by_id(entity_id)
        return None
    
    def _analyze_reputation(self, entity: Any, relation: Any, entity_type: str, relation_type: str) -> Dict[str, Any]:
        """Analyze reputation factors between entities."""
        factors = {}
        
        # Basic reputation factors
        if hasattr(entity, "reputation"):
            factors["entity_reputation"] = entity.reputation
        if hasattr(relation, "reputation"):
            factors["relation_reputation"] = relation.reputation
        
        # Relationship-specific factors
        if entity_type == "player" and relation_type == "team":
            # Player-team relationship
            if hasattr(entity, "team_id") and entity.team_id == relation.id:
                factors["relationship"] = "current_teammate"
                factors["team_morale_impact"] = getattr(relation, "team_morale", 50)
            else:
                factors["relationship"] = "external"
        
        elif entity_type == "club_owner" and relation_type == "team":
            # Owner-team relationship
            if hasattr(entity, "team_id") and entity.team_id == relation.id:
                factors["relationship"] = "owns_team"
                factors["satisfaction"] = getattr(entity, "satisfaction", 50)
                factors["ambition"] = getattr(entity, "ambition", 50)
        
        return factors
    
    def _generate_media_narrative(self, outlet: Any, entity: Any, bias: int) -> str:
        """Generate a media narrative based on outlet characteristics and bias."""
        entity_name = getattr(entity, "name", "Unknown")
        
        if bias > 50:
            if outlet.sensationalism > 70:
                return f"Sensational positive coverage of {entity_name}"
            else:
                return f"Positive coverage of {entity_name}"
        elif bias < -50:
            if outlet.sensationalism > 70:
                return f"Sensational negative coverage of {entity_name}"
            else:
                return f"Critical coverage of {entity_name}"
        else:
            return f"Neutral coverage of {entity_name}"
    
    def _calculate_overall_sentiment(self, media_views: List[Dict[str, Any]]) -> str:
        """Calculate overall media sentiment."""
        if not media_views:
            return "neutral"
        
        total_bias = sum(view["bias"] * view["reach"] for view in media_views)
        total_reach = sum(view["reach"] for view in media_views)
        
        if total_reach == 0:
            return "neutral"
        
        weighted_bias = total_bias / total_reach
        
        if weighted_bias > 20:
            return "positive"
        elif weighted_bias < -20:
            return "negative"
        else:
            return "neutral"

    def get_server(self) -> Server:
        """Get the MCP server instance."""
        return self.server