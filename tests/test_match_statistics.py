"""Tests for match statistics tracking (possession, shots, corners)."""

import sys
import uuid
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from neuralnet.data import create_sample_world
from neuralnet.entities import Match
from neuralnet.simulation import MatchSimulator


def test_match_statistics_are_tracked():
    """Test that match statistics are properly tracked during simulation."""
    world = create_sample_world()
    
    # Get first two teams
    team_ids = list(world.teams.keys())[:2]
    
    # Create a test match
    match = Match(
        id=str(uuid.uuid4()),
        home_team_id=team_ids[0],
        away_team_id=team_ids[1],
        league="premier_fantasy",
        matchday=1,
        season=2025
    )
    world.matches[match.id] = match
    
    # Simulate match
    simulator = MatchSimulator(world, match, seed=12345)
    events = list(simulator.simulate())
    
    # Get the MatchEnded event (should be last)
    match_ended = events[-1]
    
    # Verify match statistics are present
    assert match_ended.event_type == "MatchEnded"
    assert match_ended.home_possession is not None
    assert match_ended.away_possession is not None
    assert match_ended.home_shots is not None
    assert match_ended.away_shots is not None
    assert match_ended.home_shots_on_target is not None
    assert match_ended.away_shots_on_target is not None
    assert match_ended.home_corners is not None
    assert match_ended.away_corners is not None
    
    # Verify possession adds up to 100%
    assert match_ended.home_possession + match_ended.away_possession == 100
    
    # Verify shots on target is less than or equal to total shots
    assert match_ended.home_shots_on_target <= match_ended.home_shots
    assert match_ended.away_shots_on_target <= match_ended.away_shots
    
    # Verify statistics are non-negative
    assert match_ended.home_possession >= 0
    assert match_ended.away_possession >= 0
    assert match_ended.home_shots >= 0
    assert match_ended.away_shots >= 0
    assert match_ended.home_shots_on_target >= 0
    assert match_ended.away_shots_on_target >= 0
    assert match_ended.home_corners >= 0
    assert match_ended.away_corners >= 0


def test_corner_kicks_are_generated():
    """Test that corner kick events are generated during matches."""
    world = create_sample_world()
    
    # Get first two teams
    team_ids = list(world.teams.keys())[:2]
    
    # Create a test match
    match = Match(
        id=str(uuid.uuid4()),
        home_team_id=team_ids[0],
        away_team_id=team_ids[1],
        league="premier_fantasy",
        matchday=1,
        season=2025
    )
    world.matches[match.id] = match
    
    # Simulate match
    simulator = MatchSimulator(world, match, seed=54321)
    events = list(simulator.simulate())
    
    # Check if any corner kicks occurred
    corner_events = [e for e in events if e.event_type == "CornerKick"]
    
    # At least one corner should have occurred in a 90 minute match
    assert len(corner_events) > 0
    
    # Verify corner events have correct structure
    for corner in corner_events:
        assert hasattr(corner, "team")
        assert hasattr(corner, "minute")
        assert hasattr(corner, "match_id")
        assert corner.minute >= 0
        assert corner.minute <= 90


def test_shots_include_goals():
    """Test that goals are counted as shots on target."""
    world = create_sample_world()
    
    # Get first two teams
    team_ids = list(world.teams.keys())[:2]
    
    # Create a test match
    match = Match(
        id=str(uuid.uuid4()),
        home_team_id=team_ids[0],
        away_team_id=team_ids[1],
        league="premier_fantasy",
        matchday=1,
        season=2025
    )
    world.matches[match.id] = match
    
    # Simulate match
    simulator = MatchSimulator(world, match, seed=99999)
    events = list(simulator.simulate())
    
    # Get goals and final stats
    goal_events = [e for e in events if e.event_type == "Goal"]
    match_ended = events[-1]
    
    home_goals = sum(1 for g in goal_events if g.team == match.home_team_id)
    away_goals = sum(1 for g in goal_events if g.team == match.away_team_id)
    
    # Shots on target must at least equal goals (since every goal is a shot on target)
    assert match_ended.home_shots_on_target >= home_goals
    assert match_ended.away_shots_on_target >= away_goals
    
    # Total shots must at least equal shots on target
    assert match_ended.home_shots >= match_ended.home_shots_on_target
    assert match_ended.away_shots >= match_ended.away_shots_on_target


def test_possession_distribution_is_realistic():
    """Test that possession distribution is realistic and deterministic."""
    world = create_sample_world()
    
    # Get first two teams
    team_ids = list(world.teams.keys())[:2]
    
    # Create a test match
    match = Match(
        id=str(uuid.uuid4()),
        home_team_id=team_ids[0],
        away_team_id=team_ids[1],
        league="premier_fantasy",
        matchday=1,
        season=2025
    )
    world.matches[match.id] = match
    
    # Simulate same match twice with same seed
    simulator1 = MatchSimulator(world, match, seed=42)
    events1 = list(simulator1.simulate())
    match_ended1 = events1[-1]
    
    # Reset match state
    match.home_score = 0
    match.away_score = 0
    match.finished = False
    
    simulator2 = MatchSimulator(world, match, seed=42)
    events2 = list(simulator2.simulate())
    match_ended2 = events2[-1]
    
    # With same seed, possession should be identical (deterministic)
    assert match_ended1.home_possession == match_ended2.home_possession
    assert match_ended1.away_possession == match_ended2.away_possession
    
    # Possession should be between 20% and 80% for each team (realistic range)
    assert 20 <= match_ended1.home_possession <= 80
    assert 20 <= match_ended1.away_possession <= 80


def test_statistics_vary_across_matches():
    """Test that statistics vary realistically across different matches."""
    world = create_sample_world()
    
    # Get multiple teams
    team_ids = list(world.teams.keys())
    
    match_stats = []
    for i in range(3):  # Test 3 different matches
        match = Match(
            id=str(uuid.uuid4()),
            home_team_id=team_ids[i * 2],
            away_team_id=team_ids[i * 2 + 1],
            league="premier_fantasy",
            matchday=1,
            season=2025
        )
        world.matches[match.id] = match
        
        simulator = MatchSimulator(world, match, seed=1000 + i)
        events = list(simulator.simulate())
        match_ended = events[-1]
        match_stats.append({
            "possession": match_ended.home_possession,
            "shots": match_ended.home_shots + match_ended.away_shots,
            "corners": match_ended.home_corners + match_ended.away_corners
        })
    
    # Not all matches should have identical statistics
    possessions = [s["possession"] for s in match_stats]
    shots_totals = [s["shots"] for s in match_stats]
    corners_totals = [s["corners"] for s in match_stats]
    
    # At least some variety in statistics
    assert len(set(possessions)) > 1 or len(set(shots_totals)) > 1 or len(set(corners_totals)) > 1
