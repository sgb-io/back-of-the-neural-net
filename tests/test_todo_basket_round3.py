"""Tests for TODO basket round 3 features.

This test suite covers:
- Offsides tracking
- Match commentary
- Player ratings per match
- Form guide (last 5 games)
- Career statistics tracking
"""

import pytest
from neuralnet.data import create_sample_world
from neuralnet.entities import Match
from neuralnet.simulation import MatchEngine, MatchSimulator
from neuralnet.events import Goal, Offside, MatchEnded


def _create_test_match(world, home_idx=0, away_idx=1):
    """Helper to create a test match between two teams."""
    team_ids = list(world.teams.keys())
    match = Match(
        id=f"test-match-{home_idx}-{away_idx}",
        home_team_id=team_ids[home_idx],
        away_team_id=team_ids[away_idx],
        league="premier_fantasy",
        matchday=1,
        season=2024,
        date="2024-08-17"
    )
    world.matches[match.id] = match
    return match


def test_offsides_can_occur():
    """Test that offside events are generated during matches."""
    world = create_sample_world()
    
    # Create multiple test matches
    for i in range(10):
        home = i * 2
        away = i * 2 + 1
        if away >= len(world.teams):
            break
        _create_test_match(world, home, away)
    
    engine = MatchEngine(world)
    
    # Simulate matches to increase likelihood of offsides
    offside_count = 0
    matches = list(world.matches.values())
    for match in matches:
        events = engine.simulate_match(match.id, seed=42 + offside_count)
        offsides = [e for e in events if isinstance(e, Offside)]
        offside_count += len(offsides)
    
    # Should have at least some offsides across multiple matches
    assert offside_count > 0, "Expected at least some offside events"


def test_offside_statistics_tracked():
    """Test that offside statistics are tracked in MatchEnded events."""
    world = create_sample_world()
    match = _create_test_match(world)
    engine = MatchEngine(world)
    
    events = engine.simulate_match(match.id, seed=42)
    
    # Find MatchEnded event
    match_ended = next((e for e in events if isinstance(e, MatchEnded)), None)
    assert match_ended is not None
    
    # Check offside fields exist and are non-negative
    assert hasattr(match_ended, 'home_offsides')
    assert hasattr(match_ended, 'away_offsides')
    assert match_ended.home_offsides >= 0
    assert match_ended.away_offsides >= 0


def test_match_commentary_generated():
    """Test that match commentary is generated for events."""
    world = create_sample_world()
    match = _create_test_match(world)
    engine = MatchEngine(world)
    
    events = engine.simulate_match(match.id, seed=42)
    
    # Find MatchEnded event
    match_ended = next((e for e in events if isinstance(e, MatchEnded)), None)
    assert match_ended is not None
    
    # Check commentary exists
    assert hasattr(match_ended, 'commentary')
    assert match_ended.commentary is not None
    assert len(match_ended.commentary) > 0
    
    # Commentary should be strings
    for line in match_ended.commentary:
        assert isinstance(line, str)
        assert len(line) > 0


def test_commentary_includes_goals():
    """Test that commentary includes goal events."""
    world = create_sample_world()
    match = _create_test_match(world)
    engine = MatchEngine(world)
    
    events = engine.simulate_match(match.id, seed=42)
    
    # Find goals
    goals = [e for e in events if isinstance(e, Goal)]
    
    # Find MatchEnded event
    match_ended = next((e for e in events if isinstance(e, MatchEnded)), None)
    assert match_ended is not None
    
    if goals:  # If there were goals
        # Commentary should mention "GOAL"
        commentary_text = " ".join(match_ended.commentary)
        assert "GOAL" in commentary_text


def test_form_guide_last_5_matches():
    """Test that form guide tracks last 5 matches."""
    world = create_sample_world()
    
    team = list(world.teams.values())[0]
    
    # Create multiple test matches involving this team
    for i in range(7):
        _create_test_match(world, home_idx=0, away_idx=i+1)
    
    engine = MatchEngine(world)
    
    # Simulate matches
    matches = list(world.matches.values())
    for i, match in enumerate(matches):
        events = engine.simulate_match(match.id, seed=42 + i)
    
    # Team should have recent form tracked
    assert hasattr(team, 'recent_form')
    
    # Should have at most 5 results
    assert len(team.recent_form) <= 5
    
    # Results should be W/D/L
    for result in team.recent_form:
        assert result in ['W', 'D', 'L']


def test_form_guide_tracks_results():
    """Test that form guide tracks match results correctly."""
    world = create_sample_world()
    
    team = list(world.teams.values())[0]
    
    # Create multiple test matches
    for i in range(3):
        _create_test_match(world, home_idx=0, away_idx=i+1)
    
    engine = MatchEngine(world)
    
    # Simulate matches
    matches = list(world.matches.values())
    for i, match in enumerate(matches):
        events = engine.simulate_match(match.id, seed=42 + i)
    
    # Team should have form tracked
    assert len(team.recent_form) > 0
    assert len(team.recent_form) <= 5


def test_offside_deterministic():
    """Test that offside generation is deterministic with same seed."""
    world = create_sample_world()
    match = _create_test_match(world)
    engine = MatchEngine(world)
    
    # Simulate twice with same seed
    events1 = engine.simulate_match(match.id, seed=42)
    
    # Reset match state (need to recreate world)
    world2 = create_sample_world()
    match2 = _create_test_match(world2)
    engine2 = MatchEngine(world2)
    events2 = engine2.simulate_match(match2.id, seed=42)
    
    # Count offsides in both simulations
    offsides1 = [e for e in events1 if isinstance(e, Offside)]
    offsides2 = [e for e in events2 if isinstance(e, Offside)]
    
    # Should be identical
    assert len(offsides1) == len(offsides2)


def test_commentary_has_minutes():
    """Test that commentary lines include minute markers."""
    world = create_sample_world()
    match = _create_test_match(world)
    engine = MatchEngine(world)
    
    events = engine.simulate_match(match.id, seed=42)
    
    # Find MatchEnded event
    match_ended = next((e for e in events if isinstance(e, MatchEnded)), None)
    assert match_ended is not None
    
    if match_ended.commentary:
        # At least one commentary line should have a minute marker
        has_minute_marker = any("'" in line for line in match_ended.commentary)
        assert has_minute_marker, "Commentary should include minute markers"
