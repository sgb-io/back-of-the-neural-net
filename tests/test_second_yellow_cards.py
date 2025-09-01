"""Test that players get red cards when they receive a second yellow card."""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from neuralnet.data import create_sample_world
from neuralnet.entities import Match
from neuralnet.events import YellowCard, RedCard
from neuralnet.simulation import MatchSimulator
import uuid


def test_first_yellow_remains_yellow():
    """Test that the first yellow card for a player remains a yellow card."""
    world = create_sample_world()
    
    # Get first two teams
    team_ids = list(world.teams.keys())[:2]
    home_team = world.teams[team_ids[0]]
    away_team = world.teams[team_ids[1]]
    
    # Create a test match
    match = Match(
        id=str(uuid.uuid4()),
        home_team_id=team_ids[0],
        away_team_id=team_ids[1],
        league="premier_fantasy",
        matchday=1,
        season=2024
    )
    
    world.matches[match.id] = match
    
    # Create a simulator
    simulator = MatchSimulator(world, match, seed=42)
    
    test_player = home_team.players[0]
    initial_yellow_count = test_player.yellow_cards
    
    simulator.match.minute = 30
    
    # Temporarily override the random selection to always pick our test player
    original_choice = simulator.rng.choice
    def mock_choice(seq):
        if seq == [home_team, away_team]:
            return home_team
        elif seq == home_team.players:
            return test_player
        else:
            return original_choice(seq)
    
    simulator.rng.choice = mock_choice
    
    # Create a yellow card event
    event = simulator._create_yellow_card_event()
    
    # Restore original choice method
    simulator.rng.choice = original_choice
    
    # Should be a yellow card
    assert isinstance(event, YellowCard), f"Expected YellowCard, got {type(event)}"
    assert event.player == test_player.name
    assert test_player.yellow_cards == initial_yellow_count + 1
    assert simulator._match_yellow_cards[test_player.name] == 1


def test_second_yellow_becomes_red():
    """Test that a player receiving a second yellow card automatically gets a red card."""
    world = create_sample_world()
    
    # Get first two teams
    team_ids = list(world.teams.keys())[:2]
    home_team = world.teams[team_ids[0]]
    away_team = world.teams[team_ids[1]]
    
    # Create a test match
    match = Match(
        id=str(uuid.uuid4()),
        home_team_id=team_ids[0],
        away_team_id=team_ids[1],
        league="premier_fantasy",
        matchday=1,
        season=2024
    )
    
    world.matches[match.id] = match
    
    # Create a simulator
    simulator = MatchSimulator(world, match, seed=42)
    
    # Test the scenario: give a player a yellow card, then try to give them another
    test_player = home_team.players[0]
    initial_yellow_count = test_player.yellow_cards
    initial_red_count = test_player.red_cards
    
    # Manually set that this player has a yellow card in this match
    simulator._match_yellow_cards[test_player.name] = 1
    test_player.yellow_cards += 1  # Simulate they already got one
    
    simulator.match.minute = 45
    
    # Temporarily override the random selection to always pick our test player
    original_choice = simulator.rng.choice
    def mock_choice(seq):
        if seq == [home_team, away_team]:
            return home_team
        elif seq == home_team.players:
            return test_player
        else:
            return original_choice(seq)
    
    simulator.rng.choice = mock_choice
    
    # Now create a "yellow card" event - should become red card
    event = simulator._create_yellow_card_event()
    
    # Restore original choice method
    simulator.rng.choice = original_choice
    
    # Should be a red card with "Second yellow card" reason
    assert isinstance(event, RedCard), f"Expected RedCard, got {type(event)}"
    assert event.reason == "Second yellow card", f"Expected 'Second yellow card', got '{event.reason}'"
    assert event.player == test_player.name
    assert test_player.red_cards == initial_red_count + 1


def test_simulation_remains_deterministic():
    """Test that the full simulation remains deterministic with same seed."""
    world = create_sample_world()
    
    # Get first two teams
    team_ids = list(world.teams.keys())[:2]
    
    # Create a test match
    match1 = Match(
        id=str(uuid.uuid4()),
        home_team_id=team_ids[0],
        away_team_id=team_ids[1],
        league="premier_fantasy",
        matchday=1,
        season=2024
    )
    
    match2 = Match(
        id=str(uuid.uuid4()),
        home_team_id=team_ids[0],
        away_team_id=team_ids[1],
        league="premier_fantasy",
        matchday=1,
        season=2024
    )
    
    world.matches[match1.id] = match1
    world.matches[match2.id] = match2
    
    # Simulate the same match with the same seed twice
    simulator1 = MatchSimulator(world, match1, seed=12345)
    events1 = list(simulator1.simulate())
    
    simulator2 = MatchSimulator(world, match2, seed=12345)
    events2 = list(simulator2.simulate())
    
    # Should have the same number of events
    assert len(events1) == len(events2), "Simulations with same seed should produce same number of events"
    
    # Should have the same event types
    event_types1 = [e.event_type for e in events1]
    event_types2 = [e.event_type for e in events2]
    assert event_types1 == event_types2, "Simulations with same seed should produce same event types"


def test_different_players_independent_yellows():
    """Test that different players can each get yellow cards independently."""
    world = create_sample_world()
    
    # Get first two teams
    team_ids = list(world.teams.keys())[:2]
    home_team = world.teams[team_ids[0]]
    away_team = world.teams[team_ids[1]]
    
    # Create a test match
    match = Match(
        id=str(uuid.uuid4()),
        home_team_id=team_ids[0],
        away_team_id=team_ids[1],
        league="premier_fantasy",
        matchday=1,
        season=2024
    )
    
    world.matches[match.id] = match
    
    # Create a simulator
    simulator = MatchSimulator(world, match, seed=42)
    
    player1 = home_team.players[0]
    player2 = home_team.players[1]
    
    # Both players should be able to get their first yellow card without interference
    simulator.match.minute = 30
    
    # Give player1 a yellow card
    original_choice = simulator.rng.choice
    def mock_choice_player1(seq):
        if seq == [home_team, away_team]:
            return home_team
        elif seq == home_team.players:
            return player1
        else:
            return original_choice(seq)
    
    simulator.rng.choice = mock_choice_player1
    event1 = simulator._create_yellow_card_event()
    
    # Give player2 a yellow card
    def mock_choice_player2(seq):
        if seq == [home_team, away_team]:
            return home_team
        elif seq == home_team.players:
            return player2
        else:
            return original_choice(seq)
    
    simulator.rng.choice = mock_choice_player2
    event2 = simulator._create_yellow_card_event()
    
    # Restore original choice method
    simulator.rng.choice = original_choice
    
    # Both should be yellow cards
    assert isinstance(event1, YellowCard)
    assert isinstance(event2, YellowCard)
    assert event1.player == player1.name
    assert event2.player == player2.name
    
    # Both should be tracked
    assert simulator._match_yellow_cards[player1.name] == 1
    assert simulator._match_yellow_cards[player2.name] == 1