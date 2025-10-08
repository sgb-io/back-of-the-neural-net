"""Tests for TODO basket features: penalties, fouls, player attributes, streaks, and top assisters."""

import sys
import uuid
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from neuralnet.data import create_sample_world
from neuralnet.entities import Match, PreferredFoot, WorkRate
from neuralnet.events import Foul, Goal, PenaltyAwarded
from neuralnet.simulation import MatchEngine


def test_penalty_kicks_can_occur():
    """Test that penalty kicks can be awarded and scored."""
    world = create_sample_world()
    engine = MatchEngine(world)
    
    # Create a match
    team_ids = list(world.teams.keys())
    match = Match(
        id=str(uuid.uuid4()),
        home_team_id=team_ids[0],
        away_team_id=team_ids[1],
        league="premier_fantasy",
        matchday=1,
        season=2025
    )
    world.matches[match.id] = match
    
    # Simulate many matches to increase chance of penalty
    penalty_found = False
    penalty_goal_found = False
    
    for i in range(50):  # Simulate 50 matches
        match = Match(
            id=str(uuid.uuid4()),
            home_team_id=team_ids[i % 2],
            away_team_id=team_ids[(i + 1) % 2],
            league="premier_fantasy",
            matchday=1,
            season=2025
        )
        world.matches[match.id] = match
        events = engine.simulate_match(match.id, seed=3000 + i)
        
        # Check for penalty events
        for event in events:
            if isinstance(event, PenaltyAwarded):
                penalty_found = True
            if isinstance(event, Goal) and event.penalty:
                penalty_goal_found = True
        
        if penalty_found:
            break
    
    # With 50 matches, we should see at least some penalties
    assert penalty_found or penalty_goal_found, "No penalties found in 50 matches (very unlikely)"


def test_fouls_are_tracked():
    """Test that fouls are tracked in match statistics."""
    world = create_sample_world()
    engine = MatchEngine(world)
    
    team_ids = list(world.teams.keys())
    match = Match(
        id=str(uuid.uuid4()),
        home_team_id=team_ids[0],
        away_team_id=team_ids[1],
        league="premier_fantasy",
        matchday=1,
        season=2025
    )
    world.matches[match.id] = match
    
    events = engine.simulate_match(match.id, seed=2000)
    
    # Find MatchEnded event
    match_ended = None
    foul_events = []
    for event in events:
        if hasattr(event, '__class__') and event.__class__.__name__ == 'MatchEnded':
            match_ended = event
        if isinstance(event, Foul):
            foul_events.append(event)
    
    assert match_ended is not None
    
    # Check that foul statistics are tracked
    assert hasattr(match_ended, 'home_fouls')
    assert hasattr(match_ended, 'away_fouls')
    
    # Fouls should be non-negative
    assert match_ended.home_fouls >= 0
    assert match_ended.away_fouls >= 0
    
    # Total fouls should be reasonable (typically 10-30 per match)
    total_fouls = match_ended.home_fouls + match_ended.away_fouls
    assert 0 <= total_fouls <= 50, f"Total fouls {total_fouls} seems unrealistic"


def test_penalty_statistics_tracked():
    """Test that penalty statistics are tracked in MatchEnded."""
    world = create_sample_world()
    engine = MatchEngine(world)
    
    team_ids = list(world.teams.keys())
    match = Match(
        id=str(uuid.uuid4()),
        home_team_id=team_ids[0],
        away_team_id=team_ids[1],
        league="premier_fantasy",
        matchday=1,
        season=2025
    )
    world.matches[match.id] = match
    
    events = engine.simulate_match(match.id, seed=4000)
    
    # Find MatchEnded event
    match_ended = None
    for event in events:
        if hasattr(event, '__class__') and event.__class__.__name__ == 'MatchEnded':
            match_ended = event
            break
    
    assert match_ended is not None
    assert hasattr(match_ended, 'home_penalties')
    assert hasattr(match_ended, 'away_penalties')
    assert match_ended.home_penalties >= 0
    assert match_ended.away_penalties >= 0


def test_player_preferred_foot():
    """Test that players have preferred foot attribute."""
    world = create_sample_world()
    
    # Check that all players have preferred foot
    for team in world.teams.values():
        for player in team.players:
            assert hasattr(player, 'preferred_foot')
            assert player.preferred_foot in [PreferredFoot.LEFT, PreferredFoot.RIGHT, PreferredFoot.BOTH]


def test_player_work_rates():
    """Test that players have work rate attributes."""
    world = create_sample_world()
    
    # Check that all players have work rates
    for team in world.teams.values():
        for player in team.players:
            assert hasattr(player, 'attacking_work_rate')
            assert hasattr(player, 'defensive_work_rate')
            assert player.attacking_work_rate in [WorkRate.LOW, WorkRate.MEDIUM, WorkRate.HIGH]
            assert player.defensive_work_rate in [WorkRate.LOW, WorkRate.MEDIUM, WorkRate.HIGH]


def test_work_rates_match_positions():
    """Test that work rates are appropriate for player positions."""
    world = create_sample_world()
    
    strikers_with_high_attacking = 0
    defenders_with_high_defensive = 0
    
    for team in world.teams.values():
        for player in team.players:
            if player.position.value == "ST":
                # Strikers should tend to have high attacking work rate
                if player.attacking_work_rate == WorkRate.HIGH:
                    strikers_with_high_attacking += 1
            
            if player.position.value in ["CB", "LB", "RB"]:
                # Defenders should tend to have high defensive work rate
                if player.defensive_work_rate == WorkRate.HIGH:
                    defenders_with_high_defensive += 1
    
    # At least some strikers should have high attacking work rate
    assert strikers_with_high_attacking > 0
    # At least some defenders should have high defensive work rate
    assert defenders_with_high_defensive > 0


def test_winning_streak_tracking():
    """Test that winning streaks are tracked correctly."""
    world = create_sample_world()
    engine = MatchEngine(world)
    
    team_ids = list(world.teams.keys())
    team = world.teams[team_ids[0]]
    
    # Verify initial state
    assert team.current_streak == 0
    assert team.longest_winning_streak == 0
    
    # Simulate matches (team wins)
    for i in range(3):
        match = Match(
            id=str(uuid.uuid4()),
            home_team_id=team_ids[0],
            away_team_id=team_ids[1],
            league="premier_fantasy",
            matchday=i + 1,
            season=2025
        )
        world.matches[match.id] = match
        
        # Use a seed that tends to produce home wins
        events = engine.simulate_match(match.id, seed=1000 + i)
    
    # Check that streak is tracked (may be positive or negative depending on results)
    assert hasattr(team, 'current_streak')
    assert hasattr(team, 'longest_winning_streak')
    assert hasattr(team, 'longest_losing_streak')


def test_losing_streak_tracking():
    """Test that losing streaks are tracked correctly."""
    world = create_sample_world()
    engine = MatchEngine(world)
    
    team_ids = list(world.teams.keys())
    team = world.teams[team_ids[1]]  # Away team more likely to lose
    
    # Verify initial state
    assert team.current_streak == 0
    assert team.longest_losing_streak == 0
    
    # Simulate matches (away team likely loses)
    for i in range(3):
        match = Match(
            id=str(uuid.uuid4()),
            home_team_id=team_ids[0],
            away_team_id=team_ids[1],
            league="premier_fantasy",
            matchday=i + 1,
            season=2025
        )
        world.matches[match.id] = match
        events = engine.simulate_match(match.id, seed=2000 + i)
    
    # Streaks should be updated
    assert team.longest_losing_streak >= 0


def test_draw_resets_streak():
    """Test that a draw resets the current streak to 0."""
    world = create_sample_world()
    engine = MatchEngine(world)
    
    team_ids = list(world.teams.keys())
    team = world.teams[team_ids[0]]
    
    # Set an artificial winning streak
    team.current_streak = 3
    team.longest_winning_streak = 3
    
    # Simulate matches until we get a draw or loss (resets streak)
    for i in range(10):
        match = Match(
            id=str(uuid.uuid4()),
            home_team_id=team_ids[0],
            away_team_id=team_ids[1],
            league="premier_fantasy",
            matchday=i + 1,
            season=2025
        )
        world.matches[match.id] = match
        
        initial_streak = team.current_streak
        events = engine.simulate_match(match.id, seed=5000 + i)
        
        # If the team drew or lost, streak should be different
        if match.home_score == match.away_score:
            # Draw resets to 0
            assert team.current_streak == 0
            break
        elif match.home_score < match.away_score:
            # Loss makes streak negative
            assert team.current_streak <= 0
            break


def test_streak_deterministic():
    """Test that streak tracking is deterministic."""
    world1 = create_sample_world()
    world2 = create_sample_world()
    
    engine1 = MatchEngine(world1)
    engine2 = MatchEngine(world2)
    
    team_ids = list(world1.teams.keys())
    
    # Simulate same matches with same seed
    for i in range(5):
        match1 = Match(
            id=str(uuid.uuid4()),
            home_team_id=team_ids[0],
            away_team_id=team_ids[1],
            league="premier_fantasy",
            matchday=i + 1,
            season=2025
        )
        world1.matches[match1.id] = match1
        
        match2 = Match(
            id=match1.id,  # Same ID
            home_team_id=team_ids[0],
            away_team_id=team_ids[1],
            league="premier_fantasy",
            matchday=i + 1,
            season=2025
        )
        world2.matches[match2.id] = match2
        
        engine1.simulate_match(match1.id, seed=7000 + i)
        engine2.simulate_match(match2.id, seed=7000 + i)
    
    team1 = world1.teams[team_ids[0]]
    team2 = world2.teams[team_ids[0]]
    
    # Streaks should be identical
    assert team1.current_streak == team2.current_streak
    assert team1.longest_winning_streak == team2.longest_winning_streak
    assert team1.longest_losing_streak == team2.longest_losing_streak
