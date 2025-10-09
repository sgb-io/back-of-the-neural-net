"""Tests for TODO basket round 5 features."""

import pytest
from src.neuralnet.data import create_sample_world, create_fantasy_player
from src.neuralnet.entities import (
    Player, Position, PlayerTrait, PlayerSeasonStats, League
)
from src.neuralnet.events import SeasonEnded
from src.neuralnet.simulation import MatchSimulator


def test_skill_moves_rating_exists():
    """Test that skill_moves rating is added to players."""
    world = create_sample_world()
    
    # Check that all players have skill_moves attribute
    for team in world.teams.values():
        for player in team.players:
            assert hasattr(player, 'skill_moves')
            assert 1 <= player.skill_moves <= 5


def test_skill_moves_distribution():
    """Test that skill_moves are distributed appropriately by position."""
    world = create_sample_world()
    
    # Collect skill moves by position type
    attackers_skill_moves = []
    defenders_skill_moves = []
    
    for team in world.teams.values():
        for player in team.players:
            if player.position in [Position.ST, Position.LW, Position.RW, Position.CAM]:
                attackers_skill_moves.append(player.skill_moves)
            elif player.position in [Position.CB, Position.GK]:
                defenders_skill_moves.append(player.skill_moves)
    
    # Attackers should have higher average skill moves
    avg_attacker_skills = sum(attackers_skill_moves) / len(attackers_skill_moves)
    avg_defender_skills = sum(defenders_skill_moves) / len(defenders_skill_moves)
    
    assert avg_attacker_skills > avg_defender_skills


def test_player_traits_exist():
    """Test that player traits are added to players."""
    world = create_sample_world()
    
    # Check that players can have traits
    for team in world.teams.values():
        for player in team.players:
            assert hasattr(player, 'traits')
            assert isinstance(player.traits, list)


def test_player_traits_based_on_attributes():
    """Test that player traits are assigned based on attributes."""
    world = create_sample_world()
    
    # Find players with exceptional attributes
    speedsters = []
    clinical_finishers = []
    walls = []
    
    for team in world.teams.values():
        for player in team.players:
            if player.pace >= 85:
                speedsters.append(player)
            if player.shooting >= 85:
                clinical_finishers.append(player)
            if player.defending >= 85:
                walls.append(player)
    
    # Check that high pace players have Speedster trait
    for player in speedsters:
        assert PlayerTrait.SPEEDSTER in player.traits
    
    # Check that high shooting players have Clinical Finisher trait
    for player in clinical_finishers:
        assert PlayerTrait.CLINICAL_FINISHER in player.traits
    
    # Check that high defending players have Wall trait
    for player in walls:
        assert PlayerTrait.WALL in player.traits


def test_player_season_stats_structure():
    """Test that PlayerSeasonStats has correct structure."""
    stats = PlayerSeasonStats(season=2025)
    
    assert stats.season == 2025
    assert stats.appearances == 0
    assert stats.goals == 0
    assert stats.assists == 0
    assert stats.yellow_cards == 0
    assert stats.red_cards == 0
    assert stats.minutes_played == 0
    assert stats.average_rating == 0.0


def test_player_has_season_stats():
    """Test that players have season_stats dictionary."""
    world = create_sample_world()
    
    for team in world.teams.values():
        for player in team.players:
            assert hasattr(player, 'season_stats')
            assert isinstance(player.season_stats, dict)


def test_season_stats_can_be_added():
    """Test that season statistics can be added to players."""
    world = create_sample_world()
    player = list(world.players.values())[0]
    
    # Add season stats
    season_stats = PlayerSeasonStats(
        season=2025,
        appearances=10,
        goals=5,
        assists=3,
        yellow_cards=2,
        red_cards=0,
        minutes_played=900,
        average_rating=7.5
    )
    
    player.season_stats[2025] = season_stats
    
    assert 2025 in player.season_stats
    assert player.season_stats[2025].goals == 5
    assert player.season_stats[2025].assists == 3
    assert player.season_stats[2025].average_rating == 7.5


def test_league_has_historical_records():
    """Test that leagues have historical records fields."""
    world = create_sample_world()
    
    for league in world.leagues.values():
        assert hasattr(league, 'champions_by_season')
        assert hasattr(league, 'top_scorers_by_season')
        assert isinstance(league.champions_by_season, dict)
        assert isinstance(league.top_scorers_by_season, dict)


def test_league_champions_can_be_recorded():
    """Test that league champions can be recorded."""
    world = create_sample_world()
    league = world.leagues["premier_fantasy"]
    team = world.teams["man_red"]
    
    # Record a champion
    league.champions_by_season[2025] = team.id
    
    assert 2025 in league.champions_by_season
    assert league.champions_by_season[2025] == team.id


def test_league_top_scorers_can_be_recorded():
    """Test that league top scorers can be recorded."""
    world = create_sample_world()
    league = world.leagues["premier_fantasy"]
    team = world.teams["man_red"]
    player = team.players[0]
    
    # Record a top scorer
    league.top_scorers_by_season[2025] = {
        "player_id": player.id,
        "goals": 25,
        "team_id": team.id
    }
    
    assert 2025 in league.top_scorers_by_season
    assert league.top_scorers_by_season[2025]["player_id"] == player.id
    assert league.top_scorers_by_season[2025]["goals"] == 25


def test_season_ended_event_structure():
    """Test SeasonEnded event structure."""
    event = SeasonEnded(
        season=2025,
        league_id="premier_fantasy",
        champion_team_id="man_red",
        top_scorer_player_id="player_123",
        top_scorer_goals=25,
        top_assister_player_id="player_456",
        top_assister_assists=15,
        most_clean_sheets_team_id="west_london_blue",
        most_clean_sheets_count=18
    )
    
    assert event.season == 2025
    assert event.league_id == "premier_fantasy"
    assert event.champion_team_id == "man_red"
    assert event.top_scorer_goals == 25
    assert event.top_assister_assists == 15
    assert event.most_clean_sheets_count == 18


def test_traits_include_technical_for_high_skill_moves():
    """Test that high skill moves players get Technical trait."""
    world = create_sample_world()
    
    technical_players = []
    for team in world.teams.values():
        for player in team.players:
            if player.skill_moves >= 4:
                technical_players.append(player)
    
    # At least some high skill moves players should have Technical trait
    players_with_technical = [p for p in technical_players if PlayerTrait.TECHNICAL in p.traits]
    assert len(players_with_technical) > 0


def test_traits_include_engine_for_high_work_rate():
    """Test that high work rate players get Engine trait."""
    world = create_sample_world()
    
    from src.neuralnet.entities import WorkRate
    
    engine_candidates = []
    for team in world.teams.values():
        for player in team.players:
            if player.attacking_work_rate == WorkRate.HIGH and player.defensive_work_rate == WorkRate.HIGH:
                engine_candidates.append(player)
    
    # All players with high/high work rate should have Engine trait
    for player in engine_candidates:
        assert PlayerTrait.ENGINE in player.traits


def test_traits_include_leader_for_experienced_players():
    """Test that experienced, reputable players get Leader trait."""
    world = create_sample_world()
    
    leaders = []
    for team in world.teams.values():
        for player in team.players:
            if player.age >= 28 and player.reputation >= 60:
                leaders.append(player)
    
    # All experienced, reputable players should have Leader trait
    for player in leaders:
        assert PlayerTrait.LEADER in player.traits


def test_skill_moves_five_star_players_exist():
    """Test that 5-star skill moves players exist."""
    world = create_sample_world()
    
    five_star_players = []
    for team in world.teams.values():
        for player in team.players:
            if player.skill_moves == 5:
                five_star_players.append(player)
    
    # Should have at least some 5-star skill moves players
    assert len(five_star_players) > 0


def test_player_can_have_multiple_traits():
    """Test that a player can have multiple traits."""
    world = create_sample_world()
    
    players_with_multiple_traits = []
    for team in world.teams.values():
        for player in team.players:
            if len(player.traits) >= 2:
                players_with_multiple_traits.append(player)
    
    # Should have at least some players with multiple traits
    assert len(players_with_multiple_traits) > 0


def test_injury_prone_trait_exists():
    """Test that some players have Injury Prone trait."""
    world = create_sample_world()
    
    injury_prone_players = []
    for team in world.teams.values():
        for player in team.players:
            if PlayerTrait.INJURY_PRONE in player.traits:
                injury_prone_players.append(player)
    
    # Should have at least a few injury prone players (5% chance)
    # With 40 teams * ~29 players = ~1160 players, expect ~58 injury prone
    # Allow for randomness, just check there are some
    assert len(injury_prone_players) > 0


def test_flair_trait_for_skilled_players():
    """Test that highly skilled players with 5-star skills and 70+ average get Flair trait."""
    world = create_sample_world()
    
    # Find players with 5-star skill moves and calculate their base ability average
    flair_candidates = []
    for team in world.teams.values():
        for player in team.players:
            if player.skill_moves == 5:
                # Calculate base ability average (same way it's done in data.py)
                base_ability = (player.pace + player.shooting + player.passing + 
                               player.defending + player.physicality) / 5
                if base_ability >= 70:
                    flair_candidates.append(player)
    
    # These players should have Flair trait (if any exist)
    if len(flair_candidates) > 0:
        for player in flair_candidates:
            assert PlayerTrait.FLAIR in player.traits, f"Player {player.name} has skill_moves=5 and base_ability>=70 but no FLAIR trait"
    # else: it's okay if no players meet the strict criteria


def test_determinism_with_new_features():
    """Test that player generation with new features is still deterministic."""
    # Create two players with the same name and position
    player1 = create_fantasy_player("Test Player", Position.ST)
    player2 = create_fantasy_player("Test Player", Position.ST)
    
    # They should have identical attributes including new ones
    assert player1.skill_moves == player2.skill_moves
    assert player1.traits == player2.traits
    assert player1.preferred_foot == player2.preferred_foot
    assert player1.weak_foot == player2.weak_foot


def test_backward_compatibility_no_season_stats():
    """Test that players work without season stats."""
    world = create_sample_world()
    player = list(world.players.values())[0]
    
    # Should have empty season_stats dict by default
    assert len(player.season_stats) == 0
    
    # Should still work normally
    assert player.overall_rating > 0
    assert player.calculated_market_value > 0
