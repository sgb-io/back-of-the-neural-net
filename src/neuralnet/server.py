"""HTTP API server for the game."""

import asyncio
import json
from contextlib import asynccontextmanager
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