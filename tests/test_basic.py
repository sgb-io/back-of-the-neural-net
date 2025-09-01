"""Test the basic game architecture."""

import asyncio
import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from neuralnet.data import create_sample_world
from neuralnet.entities import GameWorld, Position
from neuralnet.events import EventStore
from neuralnet.orchestrator import GameOrchestrator
from neuralnet.simulation import MatchEngine


def test_sample_world_creation():
    """Test creating a sample world with fantasy data."""
    world = create_sample_world()
    
    # Check leagues
    assert len(world.leagues) == 2
    assert "premier_fantasy" in world.leagues
    assert "la_fantasy" in world.leagues
    
    # Check teams
    assert len(world.teams) == 40  # 20 teams per league
    
    # Check players
    assert len(world.players) > 0
    
    # Verify each team has players
    for team in world.teams.values():
        assert len(team.players) > 0
        assert team.players[0].position == Position.GK  # First player should be goalkeeper


def test_event_store():
    """Test the event store functionality."""
    from neuralnet.events import WorldInitialized
    
    # Use in-memory database for testing
    store = EventStore(":memory:")
    
    # Create and store an event
    event = WorldInitialized(season=2024, leagues=["test_league"])
    store.append_event(event)
    
    # Retrieve events
    events = store.get_events()
    assert len(events) == 1
    assert events[0].season == 2024
    assert events[0].leagues == ["test_league"]


def test_match_simulation():
    """Test basic match simulation."""
    world = create_sample_world()
    engine = MatchEngine(world)
    
    # Get first two teams
    team_ids = list(world.teams.keys())[:2]
    
    # Create a test match
    from neuralnet.entities import Match
    import uuid
    
    match = Match(
        id=str(uuid.uuid4()),
        home_team_id=team_ids[0],
        away_team_id=team_ids[1],
        league="premier_fantasy",
        matchday=1,
        season=2024
    )
    
    world.matches[match.id] = match
    
    # Simulate the match
    events = engine.simulate_match(match.id, seed=42)
    
    # Check that we got events
    assert len(events) > 0
    
    # Should start with kick off and end with match ended
    assert events[0].event_type == "KickOff"
    assert events[-1].event_type == "MatchEnded"
    
    # Match should be marked as finished
    assert match.finished


@pytest.mark.asyncio
async def test_game_orchestrator():
    """Test the game orchestrator."""
    orchestrator = GameOrchestrator(EventStore(":memory:"))
    orchestrator.initialize_world()
    
    # Check initialization
    assert orchestrator.is_initialized
    assert len(orchestrator.world.leagues) == 2
    assert len(orchestrator.world.matches) > 0
    
    # Test advancing simulation
    result = await orchestrator.advance_simulation()
    assert "status" in result
    assert "matches_played" in result


if __name__ == "__main__":
    # Run tests manually if pytest is not available
    print("Running basic tests...")
    
    print("Testing sample world creation...")
    test_sample_world_creation()
    print("✓ Sample world creation test passed")
    
    print("Testing event store...")
    test_event_store()
    print("✓ Event store test passed")
    
    print("Testing match simulation...")
    test_match_simulation()
    print("✓ Match simulation test passed")
    
    print("Testing game orchestrator...")
    asyncio.run(test_game_orchestrator())
    print("✓ Game orchestrator test passed")
    
    print("\nAll tests passed! 🎉")