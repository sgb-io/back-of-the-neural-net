"""Tests for financial system improvements (prize money, TV rights) and statistics tracking."""

import sys
import uuid
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from neuralnet.data import create_sample_world
from neuralnet.entities import Match
from neuralnet.simulation import MatchEngine


def test_clean_sheets_are_tracked():
    """Test that clean sheets are properly tracked."""
    world = create_sample_world()
    engine = MatchEngine(world)
    
    # Get first two teams
    team_ids = list(world.teams.keys())[:2]
    home_team = world.teams[team_ids[0]]
    away_team = world.teams[team_ids[1]]
    
    # Record initial clean sheets
    initial_home_cs = home_team.clean_sheets
    initial_away_cs = away_team.clean_sheets
    
    # Create a test match where home team wins 2-0 (away team gets clean sheet... wait no, home gets CS)
    match = Match(
        id=str(uuid.uuid4()),
        home_team_id=team_ids[0],
        away_team_id=team_ids[1],
        league="premier_fantasy",
        matchday=1,
        season=2025
    )
    world.matches[match.id] = match
    
    # Simulate match (using deterministic seed that should produce a clean sheet)
    # We'll check multiple seeds to find one with a clean sheet
    found_clean_sheet = False
    for seed in range(1, 100):
        # Reset teams
        home_team.clean_sheets = initial_home_cs
        away_team.clean_sheets = initial_away_cs
        
        events = engine.simulate_match(match.id, seed=seed)
        
        # Check if either team got a clean sheet
        if home_team.clean_sheets > initial_home_cs or away_team.clean_sheets > initial_away_cs:
            found_clean_sheet = True
            
            # Verify the clean sheet logic
            match_obj = world.matches[match.id]
            if match_obj.away_score == 0:
                assert home_team.clean_sheets == initial_home_cs + 1, "Home team should have clean sheet"
            if match_obj.home_score == 0:
                assert away_team.clean_sheets == initial_away_cs + 1, "Away team should have clean sheet"
            break
    
    assert found_clean_sheet, "Should find at least one clean sheet in 100 seeds"


def test_home_away_records_are_tracked():
    """Test that home and away records are properly tracked."""
    world = create_sample_world()
    engine = MatchEngine(world)
    
    # Get first two teams
    team_ids = list(world.teams.keys())[:2]
    home_team = world.teams[team_ids[0]]
    away_team = world.teams[team_ids[1]]
    
    # Record initial stats
    initial_home_wins = home_team.home_wins
    initial_away_wins = away_team.away_wins
    
    # Create and simulate a match
    match = Match(
        id=str(uuid.uuid4()),
        home_team_id=team_ids[0],
        away_team_id=team_ids[1],
        league="premier_fantasy",
        matchday=1,
        season=2025
    )
    world.matches[match.id] = match
    
    events = engine.simulate_match(match.id, seed=42)
    match_obj = world.matches[match.id]
    
    # Verify home/away statistics were updated correctly
    if match_obj.home_score > match_obj.away_score:
        # Home win
        assert home_team.home_wins == initial_home_wins + 1
        assert away_team.away_losses == 1  # Assuming it starts at 0
    elif match_obj.away_score > match_obj.home_score:
        # Away win
        assert away_team.away_wins == initial_away_wins + 1
        assert home_team.home_losses == 1
    else:
        # Draw
        assert home_team.home_draws == 1
        assert away_team.away_draws == 1
    
    # Verify overall stats match home + away stats
    assert home_team.wins == home_team.home_wins + home_team.away_wins
    assert home_team.draws == home_team.home_draws + home_team.away_draws
    assert home_team.losses == home_team.home_losses + home_team.away_losses


def test_home_away_points_properties():
    """Test that home and away points properties work correctly."""
    world = create_sample_world()
    team = list(world.teams.values())[0]
    
    # Set some stats manually
    team.home_wins = 3
    team.home_draws = 2
    team.home_losses = 1
    team.away_wins = 2
    team.away_draws = 1
    team.away_losses = 3
    
    # Calculate expected points
    expected_home_points = 3 * 3 + 2  # 11
    expected_away_points = 2 * 3 + 1  # 7
    
    assert team.home_points == expected_home_points
    assert team.away_points == expected_away_points
    
    # Also verify overall points matches
    team.wins = team.home_wins + team.away_wins
    team.draws = team.home_draws + team.away_draws
    assert team.points == expected_home_points + expected_away_points


def test_prize_money_calculation():
    """Test that prize money is calculated based on league position."""
    world = create_sample_world()
    team = list(world.teams.values())[0]
    
    # Test prize money for different positions
    # 1st place should get more than last place
    prize_1st = team.calculate_prize_money(league_position=1, total_teams=20)
    prize_10th = team.calculate_prize_money(league_position=10, total_teams=20)
    prize_20th = team.calculate_prize_money(league_position=20, total_teams=20)
    
    assert prize_1st > prize_10th > prize_20th
    assert prize_20th >= 100_000  # Minimum prize money
    
    # Higher reputation teams should have higher prize pools
    team.reputation = 90
    prize_high_rep = team.calculate_prize_money(league_position=1, total_teams=20)
    
    team.reputation = 30
    prize_low_rep = team.calculate_prize_money(league_position=1, total_teams=20)
    
    assert prize_high_rep > prize_low_rep


def test_tv_revenue_calculation():
    """Test that TV revenue is calculated based on league position and facilities."""
    world = create_sample_world()
    team = list(world.teams.values())[0]
    
    # Test TV revenue for different positions
    tv_1st = team.calculate_tv_revenue(league_position=1, total_teams=20)
    tv_10th = team.calculate_tv_revenue(league_position=10, total_teams=20)
    tv_20th = team.calculate_tv_revenue(league_position=20, total_teams=20)
    
    # Better positions get more TV revenue
    assert tv_1st > tv_10th > tv_20th
    
    # Larger stadiums should contribute to TV revenue
    small_stadium_capacity = team.stadium_capacity
    team.stadium_capacity = 80000
    tv_large_stadium = team.calculate_tv_revenue(league_position=1, total_teams=20)
    
    team.stadium_capacity = small_stadium_capacity
    tv_small_stadium = team.calculate_tv_revenue(league_position=1, total_teams=20)
    
    assert tv_large_stadium > tv_small_stadium


def test_seasonal_evolution_applies_financial_bonuses():
    """Test that end-of-season evolution applies prize money and TV revenue."""
    world = create_sample_world()
    
    # Simulate some matches to generate league standings
    engine = MatchEngine(world)
    team_ids = list(world.teams.keys())
    
    # Play a few matches
    for i in range(3):
        match = Match(
            id=str(uuid.uuid4()),
            home_team_id=team_ids[i * 2],
            away_team_id=team_ids[i * 2 + 1],
            league="premier_fantasy",
            matchday=1,
            season=2025
        )
        world.matches[match.id] = match
        engine.simulate_match(match.id, seed=1000 + i)
    
    # Get a team and record its initial balance
    team = world.teams[team_ids[0]]
    initial_balance = team.balance
    
    # Apply seasonal evolution (which includes financial bonuses)
    world.advance_seasonal_evolution()
    
    # Balance should have increased due to prize money and TV revenue
    assert team.balance > initial_balance
    
    # The increase should be substantial (at least £1M for end-of-season bonuses)
    balance_increase = team.balance - initial_balance
    assert balance_increase >= 1_000_000


def test_reputation_changes_with_league_position():
    """Test that team reputation changes based on league position at end of season."""
    world = create_sample_world()
    engine = MatchEngine(world)
    
    # Simulate matches to create clear winners and losers
    team_ids = list(world.teams.keys())[:4]
    
    # Make team 0 win a lot (should gain reputation)
    winning_team = world.teams[team_ids[0]]
    losing_team = world.teams[team_ids[1]]
    
    initial_winner_rep = winning_team.reputation
    initial_loser_rep = losing_team.reputation
    
    # Simulate several matches
    for i in range(5):
        match = Match(
            id=str(uuid.uuid4()),
            home_team_id=team_ids[0],
            away_team_id=team_ids[1],
            league="premier_fantasy",
            matchday=i + 1,
            season=2025
        )
        world.matches[match.id] = match
        
        # Use a seed that favors home team (team 0)
        engine.simulate_match(match.id, seed=100 + i)
    
    # Apply seasonal evolution
    world.advance_seasonal_evolution()
    
    # Check that reputation changed (could go up or down depending on results and randomness)
    # Just verify that the system is working - reputation should change
    assert winning_team.reputation != initial_winner_rep or losing_team.reputation != initial_loser_rep
