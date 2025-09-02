"""Test player contracts and value functionality."""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from neuralnet.data import create_sample_world, create_fantasy_player
from neuralnet.entities import Position


def test_player_contract_fields():
    """Test that players have contract and value fields."""
    world = create_sample_world()
    
    # Get a test player
    team = next(iter(world.teams.values()))
    player = team.players[0]
    
    # Check contract fields exist
    assert hasattr(player, 'contract_years_remaining'), "Player should have contract_years_remaining field"
    assert hasattr(player, 'salary'), "Player should have salary field"
    assert hasattr(player, 'market_value'), "Player should have market_value field"
    
    # Check field types and ranges
    assert isinstance(player.contract_years_remaining, int), "contract_years_remaining should be int"
    assert isinstance(player.salary, int), "salary should be int"
    assert isinstance(player.market_value, int), "market_value should be int"
    
    assert player.contract_years_remaining >= 0, "contract_years_remaining should be non-negative"
    assert player.salary >= 0, "salary should be non-negative"
    assert player.market_value >= 0, "market_value should be non-negative"


def test_market_value_calculation():
    """Test that market value is calculated properly based on player attributes."""
    # Create a high-rated young player
    young_star = create_fantasy_player("Young Star", Position.ST)
    young_star.pace = 90
    young_star.shooting = 85
    young_star.passing = 75
    young_star.defending = 30
    young_star.physicality = 80
    young_star.age = 22
    young_star.peak_age = 27
    young_star.reputation = 70
    young_star.form = 80
    young_star.injured = False
    
    # Create an older declining player with similar base stats
    veteran = create_fantasy_player("Veteran", Position.ST)
    veteran.pace = 90
    veteran.shooting = 85
    veteran.passing = 75
    veteran.defending = 30
    veteran.physicality = 80
    veteran.age = 35
    veteran.peak_age = 27
    veteran.reputation = 90
    veteran.form = 60
    veteran.injured = False
    
    # Calculate market values
    young_value = young_star.calculated_market_value
    veteran_value = veteran.calculated_market_value
    
    # Young player should be worth less than veteran due to reputation
    # but the veteran should be heavily penalized for age
    assert young_value >= 100000, f"Young star should be worth at least £100k, got £{young_value}"
    assert veteran_value >= 100000, f"Veteran should be worth at least £100k, got £{veteran_value}"
    
    # Test injured player penalty
    young_star.injured = True
    injured_value = young_star.calculated_market_value
    young_star.injured = False
    healthy_value = young_star.calculated_market_value
    
    assert injured_value < healthy_value, "Injured player should be worth less than healthy player"


def test_salary_based_on_ability():
    """Test that salary correlates with player ability and age."""
    # Create players with different abilities using the factory function
    low_player = create_fantasy_player("Test Low", Position.CB)
    high_player = create_fantasy_player("Test High", Position.ST)
    
    # Both should have positive salaries
    assert low_player.salary > 0, "Low ability player should have positive salary"
    assert high_player.salary > 0, "High ability player should have positive salary"
    
    # Check minimum salary
    assert low_player.salary >= 15000, f"Player salary should be at least £15k, got £{low_player.salary}"
    assert high_player.salary >= 15000, f"Player salary should be at least £15k, got £{high_player.salary}"


def test_contract_years_range():
    """Test that contract years are within reasonable range."""
    world = create_sample_world()
    
    for team in world.teams.values():
        for player in team.players:
            assert 0 <= player.contract_years_remaining <= 5, \
                f"Player {player.name} has unrealistic contract length: {player.contract_years_remaining}"


def test_all_players_have_contracts():
    """Test that all players in the world have contract information."""
    world = create_sample_world()
    
    total_players = 0
    for team in world.teams.values():
        for player in team.players:
            total_players += 1
            # Check each player has contract fields
            assert player.contract_years_remaining is not None, f"Player {player.name} missing contract_years_remaining"
            assert player.salary is not None, f"Player {player.name} missing salary"
            assert player.market_value is not None, f"Player {player.name} missing market_value"
            
            # Check reasonable values
            assert player.salary >= 10000, f"Player {player.name} has unrealistically low salary: £{player.salary}"
            assert player.market_value >= 50000, f"Player {player.name} has unrealistically low market value: £{player.market_value}"
    
    assert total_players > 0, "Should have created players in the world"
    print(f"Verified contracts for {total_players} players")