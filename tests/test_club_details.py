"""Tests for enhanced club features including finances, stadiums, facilities, and fanbase."""

import pytest
from src.neuralnet.data import create_sample_world
from src.neuralnet.entities import GameWorld


def test_team_financial_attributes():
    """Test that teams have comprehensive financial attributes."""
    world = create_sample_world()
    
    for team_id, team in world.teams.items():
        # Check all financial attributes exist and are reasonable
        assert hasattr(team, 'balance'), f"Team {team.name} missing balance"
        assert hasattr(team, 'initial_balance'), f"Team {team.name} missing initial_balance"
        assert hasattr(team, 'owner_investment'), f"Team {team.name} missing owner_investment"
        assert hasattr(team, 'monthly_wage_costs'), f"Team {team.name} missing monthly_wage_costs"
        assert hasattr(team, 'monthly_stadium_costs'), f"Team {team.name} missing monthly_stadium_costs"
        assert hasattr(team, 'monthly_facilities_costs'), f"Team {team.name} missing monthly_facilities_costs"
        
        # Check reasonable value ranges
        assert team.balance >= 0, f"Team {team.name} has negative balance"
        assert team.initial_balance >= 100000, f"Team {team.name} initial balance too low"
        assert team.monthly_wage_costs > 0, f"Team {team.name} has zero wage costs"
        assert team.monthly_stadium_costs > 0, f"Team {team.name} has zero stadium costs"
        assert team.monthly_facilities_costs > 0, f"Team {team.name} has zero facilities costs"


def test_team_stadium_attributes():
    """Test that teams have realistic stadium attributes."""
    world = create_sample_world()
    
    for team_id, team in world.teams.items():
        # Check stadium attributes exist
        assert hasattr(team, 'stadium_name'), f"Team {team.name} missing stadium_name"
        assert hasattr(team, 'stadium_capacity'), f"Team {team.name} missing stadium_capacity"
        
        # Check reasonable values
        assert isinstance(team.stadium_name, str), f"Team {team.name} stadium name not string"
        assert len(team.stadium_name) > 0, f"Team {team.name} has empty stadium name"
        assert 5000 <= team.stadium_capacity <= 100000, f"Team {team.name} stadium capacity {team.stadium_capacity} out of realistic range"


def test_team_facilities_and_fanbase():
    """Test that teams have training facilities and fanbase attributes."""
    world = create_sample_world()
    
    for team_id, team in world.teams.items():
        # Check training facilities
        assert hasattr(team, 'training_facilities_quality'), f"Team {team.name} missing training_facilities_quality"
        assert 1 <= team.training_facilities_quality <= 100, f"Team {team.name} training quality out of range"
        
        # Check fanbase attributes
        assert hasattr(team, 'fanbase_size'), f"Team {team.name} missing fanbase_size"
        assert hasattr(team, 'season_ticket_holders'), f"Team {team.name} missing season_ticket_holders"
        
        assert team.fanbase_size >= 1000, f"Team {team.name} fanbase too small"
        assert team.season_ticket_holders >= 100, f"Team {team.name} season tickets too few"
        assert team.season_ticket_holders <= team.stadium_capacity, f"Team {team.name} more season tickets than capacity"


def test_reputation_influences_financial_setup():
    """Test that higher reputation teams have better financial setups."""
    world = create_sample_world()
    
    high_rep_teams = [team for team in world.teams.values() if team.reputation > 70]
    low_rep_teams = [team for team in world.teams.values() if team.reputation < 40]
    
    assert len(high_rep_teams) > 0, "No high reputation teams found"
    assert len(low_rep_teams) > 0, "No low reputation teams found"
    
    # High reputation teams should generally have larger stadiums
    avg_high_capacity = sum(team.stadium_capacity for team in high_rep_teams) / len(high_rep_teams)
    avg_low_capacity = sum(team.stadium_capacity for team in low_rep_teams) / len(low_rep_teams)
    assert avg_high_capacity > avg_low_capacity, "High reputation teams don't have larger average stadiums"
    
    # High reputation teams should have larger fanbases
    avg_high_fanbase = sum(team.fanbase_size for team in high_rep_teams) / len(high_rep_teams)
    avg_low_fanbase = sum(team.fanbase_size for team in low_rep_teams) / len(low_rep_teams)
    assert avg_high_fanbase > avg_low_fanbase, "High reputation teams don't have larger average fanbases"


def test_enhanced_club_owners():
    """Test that club owners have enhanced attributes and investment behavior."""
    world = create_sample_world()
    
    for owner_id, owner in world.club_owners.items():
        # Check new attributes
        assert hasattr(owner, 'investment_tendency'), f"Owner {owner.name} missing investment_tendency"
        assert hasattr(owner, 'total_invested'), f"Owner {owner.name} missing total_invested"
        assert hasattr(owner, 'last_investment'), f"Owner {owner.name} missing last_investment"
        
        # Check value ranges
        assert 1 <= owner.investment_tendency <= 100, f"Owner {owner.name} investment tendency out of range"
        assert owner.total_invested >= 0, f"Owner {owner.name} has negative total investment"
        assert owner.last_investment >= 0, f"Owner {owner.name} has negative last investment"
        
        # Test investment calculation method
        potential_investment = owner.calculate_potential_investment(0.5, 0.5)
        assert isinstance(potential_investment, int), "Investment calculation should return integer"
        assert potential_investment >= 0, "Investment calculation should not be negative"


def test_owner_wealth_correlates_with_team_reputation():
    """Test that owners of high reputation teams tend to be wealthier."""
    world = create_sample_world()
    
    team_owner_pairs = []
    for team_id, team in world.teams.items():
        owners = world.get_club_owners_for_team(team_id)
        if owners:
            team_owner_pairs.append((team, owners[0]))
    
    assert len(team_owner_pairs) > 0, "No team-owner pairs found"
    
    high_rep_owners = [owner for team, owner in team_owner_pairs if team.reputation > 70]
    low_rep_owners = [owner for team, owner in team_owner_pairs if team.reputation < 40]
    
    if high_rep_owners and low_rep_owners:
        avg_high_wealth = sum(owner.wealth for owner in high_rep_owners) / len(high_rep_owners)
        avg_low_wealth = sum(owner.wealth for owner in low_rep_owners) / len(low_rep_owners)
        assert avg_high_wealth > avg_low_wealth, "High reputation team owners should be wealthier on average"


def test_financial_calculations():
    """Test team financial calculation methods."""
    world = create_sample_world()
    
    team = next(iter(world.teams.values()))
    
    # Test monthly costs calculation
    monthly_costs = team.monthly_total_costs
    expected_costs = team.monthly_wage_costs + team.monthly_stadium_costs + team.monthly_facilities_costs
    assert monthly_costs == expected_costs, "Monthly costs calculation incorrect"
    
    # Test season ticket revenue calculation
    st_revenue = team.season_ticket_revenue
    assert st_revenue > 0, "Season ticket revenue should be positive"
    assert isinstance(st_revenue, int), "Season ticket revenue should be integer"
    
    # Test matchday revenue calculation
    matchday_revenue = team.matchday_revenue_per_game
    assert matchday_revenue > 0, "Matchday revenue should be positive"
    assert isinstance(matchday_revenue, int), "Matchday revenue should be integer"
    
    # Test stadium utilization calculation
    utilization = team.calculate_stadium_utilization()
    assert 0 <= utilization <= 1, "Stadium utilization should be between 0 and 1"


def test_financial_evolution_system():
    """Test that financial evolution system works correctly."""
    world = create_sample_world()
    
    # Get initial state
    team = next(iter(world.teams.values()))
    initial_balance = team.balance
    initial_reputation = team.reputation
    
    # Test monthly financial progression
    world.advance_monthly_finances()
    
    # Balance should have changed (costs deducted, revenue added)
    # Note: Balance could go up or down depending on income vs costs
    assert isinstance(team.balance, int), "Balance should remain integer after monthly progression"
    assert team.balance >= 0, "Balance should not go negative"
    
    # Test seasonal evolution
    # Simulate some matches for performance calculation
    team.matches_played = 10
    team.wins = 5
    team.draws = 3
    team.losses = 2
    
    world.advance_seasonal_evolution()
    
    # Reputation might have changed based on performance
    reputation_change = abs(team.reputation - initial_reputation)
    assert reputation_change <= 20, "Reputation should not change more than 20 points per season"


def test_big_club_patterns():
    """Test that recognized big club patterns get appropriate treatment."""
    world = create_sample_world()
    
    # Find teams that should be "big clubs" based on name patterns
    big_club_patterns = ["madrid", "barcelona", "man_", "merseyside", "north_london", "west_london_blue"]
    big_clubs = []
    regular_clubs = []
    
    for team in world.teams.values():
        is_big_club = any(pattern in team.id.lower() for pattern in big_club_patterns)
        if is_big_club:
            big_clubs.append(team)
        else:
            regular_clubs.append(team)
    
    if big_clubs and regular_clubs:
        # Big clubs should generally have higher reputation
        avg_big_rep = sum(team.reputation for team in big_clubs) / len(big_clubs)
        avg_regular_rep = sum(team.reputation for team in regular_clubs) / len(regular_clubs)
        assert avg_big_rep > avg_regular_rep, "Big clubs should have higher average reputation"
        
        # Big clubs should have larger stadiums
        avg_big_capacity = sum(team.stadium_capacity for team in big_clubs) / len(big_clubs)
        avg_regular_capacity = sum(team.stadium_capacity for team in regular_clubs) / len(regular_clubs)
        assert avg_big_capacity > avg_regular_capacity, "Big clubs should have larger average stadiums"


def test_stadium_naming_system():
    """Test that stadium names are generated appropriately."""
    world = create_sample_world()
    
    for team in world.teams.values():
        assert team.stadium_name, f"Team {team.name} has empty stadium name"
        assert len(team.stadium_name.split()) >= 2, f"Stadium name '{team.stadium_name}' seems too short"
        
        # Check that stadium names contain appropriate keywords OR are special fantasy names
        stadium_keywords = ["stadium", "park", "arena", "ground", "field", "fantasy"]
        name_lower = team.stadium_name.lower()
        has_keyword = any(keyword in name_lower for keyword in stadium_keywords)
        assert has_keyword, f"Stadium name '{team.stadium_name}' doesn't contain expected keywords"


def test_team_financial_data_consistency():
    """Test that financial data is internally consistent."""
    world = create_sample_world()
    
    for team in world.teams.items():
        team = team[1]  # Get team object
        
        # Season ticket holders should not exceed stadium capacity
        assert team.season_ticket_holders <= team.stadium_capacity, \
            f"Team {team.name} has more season tickets ({team.season_ticket_holders}) than capacity ({team.stadium_capacity})"
        
        # Stadium capacity should influence costs appropriately
        if team.stadium_capacity > 50000:
            assert team.monthly_stadium_costs > 30000, \
                f"Large stadium team {team.name} has unrealistically low stadium costs"
        
        # Higher reputation should generally mean higher costs
        if team.reputation > 80:
            assert team.monthly_wage_costs > 100000, \
                f"High reputation team {team.name} has unrealistically low wage costs"


def test_orchestrator_integration():
    """Test that the orchestrator properly integrates with financial evolution."""
    from src.neuralnet.orchestrator import GameOrchestrator
    
    # Create orchestrator with a temporary database
    orchestrator = GameOrchestrator()
    orchestrator.initialize_world()
    
    # Check that teams have financial data
    team = next(iter(orchestrator.world.teams.values()))
    initial_balance = team.balance
    initial_reputation = team.reputation
    
    # Test that evolution methods are accessible
    assert hasattr(orchestrator.world, 'advance_monthly_finances'), "World missing monthly finances method"
    assert hasattr(orchestrator.world, 'advance_seasonal_evolution'), "World missing seasonal evolution method" 
    assert hasattr(orchestrator.world, 'advance_match_progression'), "World missing match progression method"
    
    # Test that the methods can be called without errors
    orchestrator.world.advance_monthly_finances()
    
    # Simulate some performance data
    team.matches_played = 5
    team.wins = 3
    team.draws = 1
    team.losses = 1
    
    orchestrator.world.advance_seasonal_evolution()
    
    # Check that values are still reasonable after evolution
    assert team.balance >= 0, "Balance became negative after evolution"
    assert 1 <= team.reputation <= 100, "Reputation out of bounds after evolution"
    
    print(f"✓ Orchestrator integration test passed")
    print(f"  Balance: £{initial_balance:,} → £{team.balance:,}")
    print(f"  Reputation: {initial_reputation} → {team.reputation}")