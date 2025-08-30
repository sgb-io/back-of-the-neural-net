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

from .orchestrator import GameOrchestrator


# Global orchestrator instance
orchestrator = GameOrchestrator()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    orchestrator.initialize_world()
    yield
    # Shutdown - cleanup if needed


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


# Health check endpoint
@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)