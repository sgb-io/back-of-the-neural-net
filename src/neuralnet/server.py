"""HTTP API server for the game."""

import asyncio
import json
from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from sse_starlette.sse import EventSourceResponse

from .config import get_config, validate_llm_config
from .orchestrator import GameOrchestrator


# Global orchestrator instance - will be initialized in lifespan
orchestrator: GameOrchestrator = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    global orchestrator
    
    # Startup - validate configuration and initialize
    try:
        config = get_config()
        validate_llm_config(config)
        print(f"✓ LLM Provider: {config.llm.provider}")
        
        if config.llm.provider == "lmstudio":
            print(f"✓ LM Studio URL: {config.llm.lmstudio_base_url}")
            print(f"✓ LM Studio Model: {config.llm.lmstudio_model}")
        
        orchestrator = GameOrchestrator(config=config)
        orchestrator.initialize_world()
        print("✓ Game world initialized successfully")
        
    except Exception as e:
        print(f"❌ Server startup failed: {e}")
        print("\nConfiguration help:")
        print("For LM Studio, set these environment variables:")
        print("  LLM_PROVIDER=lmstudio")
        print("  LMSTUDIO_MODEL=<your-model-name>")
        print("  LMSTUDIO_BASE_URL=http://localhost:1234/v1  # (default)")
        print("\nFor mock/testing, set:")
        print("  LLM_PROVIDER=mock  # (default)")
        raise
    
    yield
    
    # Shutdown - cleanup if needed
    if orchestrator and hasattr(orchestrator, 'llm_provider'):
        if hasattr(orchestrator.llm_provider, '__aexit__'):
            await orchestrator.llm_provider.__aexit__(None, None, None)


# Create FastAPI app
app = FastAPI(
    title="Back of the Neural Net",
    description="Football management with artificial brains",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {"message": "Back of the Neural Net API", "version": "0.1.0"}


@app.get("/api/world")
async def get_world_state() -> dict:
    """Get the current world state."""
    try:
        return orchestrator.get_world_state()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/advance")
async def advance_simulation() -> dict:
    """Advance the simulation by one step."""
    try:
        result = await orchestrator.advance_simulation()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/events/stream")
async def event_stream() -> EventSourceResponse:
    """Server-sent events stream for live updates."""
    
    async def generate_events() -> AsyncGenerator[str, None]:
        """Generate server-sent events."""
        last_sequence = orchestrator.event_store.get_latest_sequence_number()
        
        while True:
            try:
                # Check for new events
                current_sequence = orchestrator.event_store.get_latest_sequence_number()
                
                if current_sequence > last_sequence:
                    # Get new events
                    new_events = orchestrator.event_store.get_events(
                        after_sequence=last_sequence,
                        limit=50
                    )
                    
                    for event in new_events:
                        event_data = {
                            "type": event.event_type,
                            "data": event.model_dump()
                        }
                        yield f"data: {json.dumps(event_data)}\\n\\n"
                    
                    last_sequence = current_sequence
                
                # Wait a bit before checking again
                await asyncio.sleep(1)
                
            except Exception as e:
                # Send error event
                error_data = {"type": "error", "message": str(e)}
                yield f"data: {json.dumps(error_data)}\\n\\n"
                break
    
    return EventSourceResponse(generate_events())


@app.get("/api/leagues/{league_id}/table")
async def get_league_table(league_id: str) -> dict:
    """Get the league table for a specific league."""
    try:
        league = orchestrator.world.get_league_by_id(league_id)
        if not league:
            raise HTTPException(status_code=404, detail="League not found")
        
        table = orchestrator.world.get_league_table(league_id)
        
        return {
            "league": league.name,
            "season": league.season,
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
                for i, team in enumerate(table)
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/fixtures")
async def get_fixtures(limit: int = 20) -> dict:
    """Get upcoming fixtures."""
    try:
        fixtures = orchestrator.get_current_matchday_fixtures()[:limit]
        
        return {
            "fixtures": [
                {
                    "id": match.id,
                    "home_team": orchestrator.world.get_team_by_id(match.home_team_id).name,
                    "away_team": orchestrator.world.get_team_by_id(match.away_team_id).name,
                    "league": match.league,
                    "matchday": match.matchday,
                    "home_score": match.home_score if match.finished else None,
                    "away_score": match.away_score if match.finished else None,
                    "finished": match.finished
                }
                for match in fixtures
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/fixtures/predictions")
async def get_fixtures_with_predictions(limit: int = 20) -> dict:
    """Get upcoming fixtures with match predictions."""
    try:
        fixtures = orchestrator.get_current_matchday_fixtures()[:limit]
        fixtures_with_predictions = []
        
        for match in fixtures:
            home_team = orchestrator.world.get_team_by_id(match.home_team_id)
            away_team = orchestrator.world.get_team_by_id(match.away_team_id)
            
            fixture_data = {
                "id": match.id,
                "home_team": home_team.name,
                "away_team": away_team.name,
                "home_team_id": match.home_team_id,
                "away_team_id": match.away_team_id,
                "league": match.league,
                "matchday": match.matchday,
                "home_score": match.home_score if match.finished else None,
                "away_score": match.away_score if match.finished else None,
                "finished": match.finished,
                "prediction": None,
                "importance": "normal",
                "media_preview": None
            }
            
            # Determine match importance
            importance_level = determine_match_importance(home_team, away_team, match.league, orchestrator.world)
            fixture_data["importance"] = importance_level
            
            # Get match prediction if tools are available and match not finished
            if not match.finished and orchestrator.game_tools:
                try:
                    prediction = await orchestrator.game_tools.get_match_predictions(
                        match.home_team_id, match.away_team_id
                    )
                    if "error" not in prediction:
                        fixture_data["prediction"] = prediction
                except Exception as e:
                    print(f"Failed to get prediction for {home_team.name} vs {away_team.name}: {e}")
            
            # Generate media preview for important matches
            if importance_level in ["high", "derby", "title_race"]:
                try:
                    media_preview = await generate_match_media_preview(
                        home_team, away_team, importance_level, orchestrator.game_tools
                    )
                    fixture_data["media_preview"] = media_preview
                except Exception as e:
                    print(f"Failed to get media preview for {home_team.name} vs {away_team.name}: {e}")
            
            fixtures_with_predictions.append(fixture_data)
        
        return {
            "fixtures": fixtures_with_predictions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def determine_match_importance(home_team, away_team, league: str, world) -> str:
    """Determine the importance level of a match."""
    # Get league table to check positions
    try:
        league_table = world.get_league_table(league)
        if not league_table:
            return "normal"
        
        # Find team positions in table
        home_position = None
        away_position = None
        
        for i, team in enumerate(league_table, 1):
            if team.id == home_team.id:
                home_position = i
            elif team.id == away_team.id:
                away_position = i
        
        if home_position is None or away_position is None:
            return "normal"
        
        # Top of table clash (both teams in top 3)
        if home_position <= 3 and away_position <= 3:
            return "title_race"
        
        # One team in top 3, other in top 6
        if (home_position <= 3 and away_position <= 6) or (away_position <= 3 and home_position <= 6):
            return "high"
        
        # Check for derby matches (same city/region - simple check based on name similarity)
        home_words = set(home_team.name.lower().split())
        away_words = set(away_team.name.lower().split())
        
        # Common words that might indicate same region
        if home_words & away_words:  # If they share any words
            return "derby"
        
        # Both teams in bottom 4 (relegation battle)
        total_teams = len(league_table)
        if home_position >= total_teams - 3 and away_position >= total_teams - 3:
            return "relegation"
        
        return "normal"
    except Exception as e:
        print(f"Error in determine_match_importance: {e}")
        return "normal"


async def generate_match_media_preview(home_team, away_team, importance_level: str, game_tools) -> dict:
    """Generate a media preview for an important match."""
    if not game_tools:
        return None
    
    try:
        # Generate preview based on importance level
        if importance_level == "title_race":
            headline = f"Title Race Heats Up: {home_team.name} vs {away_team.name}"
            preview = f"Two title contenders clash as {home_team.name} host {away_team.name} in what could be a season-defining encounter."
        elif importance_level == "derby":
            headline = f"Local Derby: {home_team.name} vs {away_team.name}"
            preview = f"Pride is at stake as local rivals {home_team.name} and {away_team.name} face off in this heated derby match."
        elif importance_level == "relegation":
            headline = f"Relegation Battle: {home_team.name} vs {away_team.name}"
            preview = f"Six-pointer alert! Both {home_team.name} and {away_team.name} desperately need points in this crucial relegation clash."
        else:  # high importance
            headline = f"Big Match: {home_team.name} vs {away_team.name}"
            preview = f"High-stakes encounter as {home_team.name} take on {away_team.name} in a match that could shape their season."
        
        # Get some media views for additional context
        home_media = await game_tools.get_media_views("team", home_team.id)
        away_media = await game_tools.get_media_views("team", away_team.id)
        
        # Pick a high-reach outlet for the preview
        home_outlets = home_media.get("media_coverage", [])
        if home_outlets:
            outlet = max(home_outlets, key=lambda x: x.get("reach", 0))
            source = outlet.get("outlet_name", "Media Source")
        else:
            source = "Football Press"
        
        return {
            "headline": headline,
            "preview": preview,
            "source": source,
            "importance": importance_level
        }
    
    except Exception as e:
        print(f"Error generating media preview: {e}")
        return None


@app.get("/api/matches")
async def get_completed_matches(limit: int = 50) -> dict:
    """Get completed matches."""
    try:
        matches = orchestrator.get_completed_matches(limit=limit)
        
        return {
            "matches": [
                {
                    "id": match.id,
                    "home_team": orchestrator.world.get_team_by_id(match.home_team_id).name,
                    "away_team": orchestrator.world.get_team_by_id(match.away_team_id).name,
                    "league": match.league,
                    "matchday": match.matchday,
                    "season": match.season,
                    "home_score": match.home_score,
                    "away_score": match.away_score,
                    "finished": match.finished
                }
                for match in matches
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/matches/{match_id}/events")
async def get_match_events(match_id: str) -> dict:
    """Get events for a specific match."""
    try:
        # Check if match exists
        match = orchestrator.world.get_match_by_id(match_id)
        if not match:
            raise HTTPException(status_code=404, detail="Match not found")
        
        events = orchestrator.get_match_events(match_id)
        
        return {
            "match_id": match_id,
            "match": {
                "id": match.id,
                "home_team": orchestrator.world.get_team_by_id(match.home_team_id).name,
                "away_team": orchestrator.world.get_team_by_id(match.away_team_id).name,
                "league": match.league,
                "matchday": match.matchday,
                "season": match.season,
                "home_score": match.home_score,
                "away_score": match.away_score,
                "finished": match.finished
            },
            "events": [
                {
                    "event_type": event.event_type,
                    "timestamp": event.timestamp.isoformat(),
                    "minute": getattr(event, 'minute', None),
                    "team": getattr(event, 'team', None),
                    "player": getattr(event, 'player', None),
                    "scorer": getattr(event, 'scorer', None),
                    "assist": getattr(event, 'assist', None),
                    "player_off": getattr(event, 'player_off', None),
                    "player_on": getattr(event, 'player_on', None),
                    "reason": getattr(event, 'reason', None),
                    "home_team": getattr(event, 'home_team', None),
                    "away_team": getattr(event, 'away_team', None),
                    "home_score": getattr(event, 'home_score', None),
                    "away_score": getattr(event, 'away_score', None),
                }
                for event in events
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/teams/{team_id}")
async def get_team_details(team_id: str) -> dict:
    """Get detailed information about a specific team."""
    try:
        team = orchestrator.world.get_team_by_id(team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        return {
            "id": team.id,
            "name": team.name,
            "league": team.league,
            "team_morale": team.team_morale,
            "tactical_familiarity": team.tactical_familiarity,
            "matches_played": team.matches_played,
            "wins": team.wins,
            "draws": team.draws,
            "losses": team.losses,
            "goals_for": team.goals_for,
            "goals_against": team.goals_against,
            "goal_difference": team.goal_difference,
            "points": team.points,
            "players": [
                {
                    "id": player.id,
                    "name": player.name,
                    "position": player.position.value,
                    "age": player.age,
                    "overall_rating": player.overall_rating,
                    "pace": player.pace,
                    "shooting": player.shooting,
                    "passing": player.passing,
                    "defending": player.defending,
                    "physicality": player.physicality,
                    "form": player.form,
                    "morale": player.morale,
                    "fitness": player.fitness,
                    "injured": player.injured,
                    "yellow_cards": player.yellow_cards,
                    "red_cards": player.red_cards
                }
                for player in team.players
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/teams/{team_id}/matches")
async def get_team_matches(team_id: str, limit: int = 10) -> dict:
    """Get recent matches for a specific team."""
    try:
        team = orchestrator.world.get_team_by_id(team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        # Get all completed matches and filter for this team
        all_matches = orchestrator.get_completed_matches(limit=100)  # Get more to filter
        team_matches = []
        
        for match in all_matches:
            home_team = orchestrator.world.get_team_by_id(match.home_team_id)
            away_team = orchestrator.world.get_team_by_id(match.away_team_id)
            
            if home_team and away_team and (match.home_team_id == team_id or match.away_team_id == team_id):
                team_matches.append({
                    "id": match.id,
                    "home_team": home_team.name,
                    "away_team": away_team.name,
                    "league": match.league,
                    "matchday": match.matchday,
                    "season": match.season,
                    "home_score": match.home_score,
                    "away_score": match.away_score,
                    "finished": match.finished,
                    "is_home": match.home_team_id == team_id
                })
                
                if len(team_matches) >= limit:
                    break
        
        return {
            "team_id": team_id,
            "team_name": team.name,
            "matches": team_matches
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/players/{player_id}")
async def get_player_details(player_id: str) -> dict:
    """Get detailed information about a specific player."""
    try:
        player = orchestrator.world.get_player_by_id(player_id)
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        
        # Find the player's current team
        current_team = None
        for team in orchestrator.world.teams.values():
            if any(p.id == player_id for p in team.players):
                current_team = team
                break
        
        if not current_team:
            raise HTTPException(status_code=404, detail="Player's team not found")
        
        # Calculate season stats (for now, just basic stats - can be enhanced later)
        # This is a placeholder for season-specific statistics
        season_stats = {
            "goals": 0,  # Would need to track from match events
            "assists": 0,  # Would need to track from match events
            "yellow_cards": player.yellow_cards,
            "red_cards": player.red_cards,
            "matches_played": 0,  # Would need to calculate from matches
            "minutes_played": 0   # Would need to track from match events
        }
        
        return {
            "id": player.id,
            "name": player.name,
            "position": player.position.value,
            "age": player.age,
            "overall_rating": player.overall_rating,
            "pace": player.pace,
            "shooting": player.shooting,
            "passing": player.passing,
            "defending": player.defending,
            "physicality": player.physicality,
            "form": player.form,
            "morale": player.morale,
            "fitness": player.fitness,
            "injured": player.injured,
            "yellow_cards": player.yellow_cards,
            "red_cards": player.red_cards,
            "current_team": {
                "id": current_team.id,
                "name": current_team.name,
                "league": current_team.league
            },
            "season_stats": season_stats
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/players/{player_id}/career-summary")
async def get_player_career_summary(player_id: str) -> dict:
    """Generate and return a career summary for a specific player using LLM."""
    try:
        player = orchestrator.world.get_player_by_id(player_id)
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        
        # Generate career summary using the LLM provider
        brain_orchestrator = orchestrator.brain_orchestrator
        if brain_orchestrator and brain_orchestrator.llm_provider:
            summary = await brain_orchestrator.llm_provider.generate_career_summary(
                player_id, orchestrator.world
            )
            
            return {
                "player_id": player_id,
                "player_name": player.name,
                "career_summary": summary,
                "generated_at": str(datetime.now())
            }
        else:
            # Fallback if no LLM provider available
            return {
                "player_id": player_id,
                "player_name": player.name,
                "career_summary": f"{player.name} is a {player.age}-year-old {player.position.value} with an overall rating of {player.overall_rating}.",
                "generated_at": str(datetime.now())
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/players/lookup/{player_name}")
async def lookup_player_by_name(player_name: str) -> dict:
    """Get player ID by player name."""
    try:
        # Find player by name
        for player_id, player in orchestrator.world.players.items():
            if player.name == player_name:
                return {
                    "player_id": player_id,
                    "player_name": player.name,
                    "position": player.position.value
                }
        
        raise HTTPException(status_code=404, detail="Player not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/teams/lookup/{team_name}")
async def lookup_team_by_name(team_name: str) -> dict:
    """Get team ID by team name."""
    try:
        # Search through all teams to find matching name
        for team_id, team in orchestrator.world.teams.items():
            if team.name.lower() == team_name.lower().replace('_', ' '):
                return {
                    "team_id": team_id,
                    "team_name": team.name,
                    "league": team.league
                }
        
        raise HTTPException(status_code=404, detail="Team not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Health check endpoint
@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/api/config")
async def get_config_info() -> dict:
    """Get current LLM configuration information."""
    try:
        config = get_config()
        return {
            "llm_provider": config.llm.provider,
            "use_tools": config.use_tools,
            "lmstudio_configured": config.llm.provider == "lmstudio" and config.llm.lmstudio_model is not None,
            "lmstudio_base_url": config.llm.lmstudio_base_url if config.llm.provider == "lmstudio" else None,
            "lmstudio_model": config.llm.lmstudio_model if config.llm.provider == "lmstudio" else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tools")
async def get_available_tools() -> dict:
    """Get list of available game state tools."""
    try:
        return {
            "tools": orchestrator.get_available_game_tools(),
            "tools_enabled": orchestrator.use_tools
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tools/{tool_name}")
async def call_game_tool(tool_name: str, arguments: dict) -> dict:
    """Call a game state tool with the provided arguments."""
    try:
        result = await orchestrator.query_game_tool(tool_name, **arguments)
        return {"tool": tool_name, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)