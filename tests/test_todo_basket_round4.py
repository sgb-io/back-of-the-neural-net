"""Tests for TODO basket round 4 features.

This module tests the new features implemented in round 4:
- Weak foot rating (1-5 stars)
- Player ratings per match (1-10 scale)
- Free kicks (direct/indirect)
- Head-to-head records
"""

import pytest

from neuralnet.orchestrator import GameOrchestrator
from neuralnet.events import FreeKick, MatchEnded


@pytest.fixture
def orchestrator():
    """Create a fresh orchestrator for testing."""
    orch = GameOrchestrator()
    orch.initialize_world()
    return orch


def test_weak_foot_rating_exists(orchestrator):
    """Test that all players have a weak foot rating between 1-5."""
    world = orchestrator.world
    
    for team in world.teams.values():
        for player in team.players:
            assert hasattr(player, "weak_foot"), f"Player {player.name} missing weak_foot attribute"
            assert 1 <= player.weak_foot <= 5, f"Player {player.name} has invalid weak_foot: {player.weak_foot}"


def test_weak_foot_distribution(orchestrator):
    """Test that weak foot ratings follow expected distribution."""
    world = orchestrator.world
    
    weak_foot_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    
    for team in world.teams.values():
        for player in team.players:
            weak_foot_counts[player.weak_foot] += 1
    
    # Most players should have 3-star weak foot (most common)
    assert weak_foot_counts[3] > weak_foot_counts[1]
    assert weak_foot_counts[3] > weak_foot_counts[5]
    
    # All ratings should be represented
    for rating in range(1, 6):
        assert weak_foot_counts[rating] > 0


def test_both_footed_players_have_better_weak_foot(orchestrator):
    """Test that two-footed players tend to have better weak foot ratings."""
    world = orchestrator.world
    
    both_footed_ratings = []
    single_footed_ratings = []
    
    for team in world.teams.values():
        for player in team.players:
            if player.preferred_foot.value == "Both":
                both_footed_ratings.append(player.weak_foot)
            else:
                single_footed_ratings.append(player.weak_foot)
    
    # Two-footed players should have higher average weak foot rating
    if both_footed_ratings and single_footed_ratings:
        avg_both = sum(both_footed_ratings) / len(both_footed_ratings)
        avg_single = sum(single_footed_ratings) / len(single_footed_ratings)
        assert avg_both > avg_single


@pytest.mark.asyncio
async def test_free_kicks_can_occur(orchestrator):
    """Test that free kick events are generated during matches."""
    # Run multiple simulations to ensure we get free kicks
    free_kicks_found = False
    
    for _ in range(5):
        await orchestrator.advance_simulation()
    
    all_events = orchestrator.event_store.get_events()
    free_kicks = [e for e in all_events if isinstance(e, FreeKick)]
    
    assert len(free_kicks) > 0, "No free kick events found after 5 matchdays"
    free_kicks_found = True
    
    # Check free kick attributes
    for fk in free_kicks[:5]:  # Check first 5
        assert fk.team in [t.id for t in orchestrator.world.teams.values()]
        assert fk.free_kick_type in ["direct", "indirect"]
        assert fk.location in ["dangerous", "safe"]


@pytest.mark.asyncio
async def test_free_kick_statistics_tracked(orchestrator):
    """Test that free kick statistics are tracked in MatchEnded events."""
    await orchestrator.advance_simulation()
    
    all_events = orchestrator.event_store.get_events()
    match_ended_events = [e for e in all_events if isinstance(e, MatchEnded)]
    
    assert len(match_ended_events) > 0
    
    # Check that free kick stats exist
    for match_ended in match_ended_events:
        assert hasattr(match_ended, "home_free_kicks")
        assert hasattr(match_ended, "away_free_kicks")
        assert match_ended.home_free_kicks is not None
        assert match_ended.away_free_kicks is not None
        assert match_ended.home_free_kicks >= 0
        assert match_ended.away_free_kicks >= 0


@pytest.mark.asyncio
async def test_free_kick_types_distribution(orchestrator):
    """Test that free kicks have reasonable type distribution."""
    # Simulate multiple matchdays
    for _ in range(5):
        await orchestrator.advance_simulation()
    
    all_events = orchestrator.event_store.get_events()
    free_kicks = [e for e in all_events if isinstance(e, FreeKick)]
    
    if len(free_kicks) > 10:  # Need enough samples
        direct_count = sum(1 for fk in free_kicks if fk.free_kick_type == "direct")
        indirect_count = sum(1 for fk in free_kicks if fk.free_kick_type == "indirect")
        
        # Direct free kicks should be more common (~80%)
        assert direct_count > indirect_count


@pytest.mark.asyncio
async def test_player_ratings_calculated(orchestrator):
    """Test that player ratings are calculated for each match."""
    await orchestrator.advance_simulation()
    
    all_events = orchestrator.event_store.get_events()
    match_ended_events = [e for e in all_events if isinstance(e, MatchEnded)]
    
    assert len(match_ended_events) > 0
    
    for match_ended in match_ended_events:
        assert hasattr(match_ended, "player_ratings")
        assert match_ended.player_ratings is not None
        assert isinstance(match_ended.player_ratings, dict)
        
        # Should have ratings for starting 11 of both teams (22 players)
        assert len(match_ended.player_ratings) == 22
        
        # All ratings should be between 1.0 and 10.0
        for player_id, rating in match_ended.player_ratings.items():
            assert 1.0 <= rating <= 10.0, f"Invalid rating {rating} for player {player_id}"
            assert isinstance(rating, float)


@pytest.mark.asyncio
async def test_player_ratings_vary(orchestrator):
    """Test that player ratings vary across matches."""
    # Simulate several matches
    for _ in range(3):
        await orchestrator.advance_simulation()
    
    all_events = orchestrator.event_store.get_events()
    match_ended_events = [e for e in all_events if isinstance(e, MatchEnded)]
    
    # Collect all unique ratings
    all_ratings = set()
    for match_ended in match_ended_events:
        if match_ended.player_ratings:
            all_ratings.update(match_ended.player_ratings.values())
    
    # Should have variety of ratings (more than just base 6.0)
    assert len(all_ratings) > 5


@pytest.mark.asyncio
async def test_head_to_head_tracking(orchestrator):
    """Test that head-to-head records are tracked between teams."""
    world = orchestrator.world
    
    # Get two teams
    teams = list(world.teams.values())[:2]
    team1, team2 = teams[0], teams[1]
    
    # Initially, head-to-head should be empty or have zero records
    initial_h2h = team1.head_to_head.get(team2.id, {"W": 0, "D": 0, "L": 0})
    
    # Simulate multiple matchdays
    for _ in range(5):
        await orchestrator.advance_simulation()
    
    # After simulation, check if head-to-head records exist
    assert hasattr(team1, "head_to_head")
    assert isinstance(team1.head_to_head, dict)
    
    # Check if records were updated (teams should have played each other)
    if team2.id in team1.head_to_head:
        h2h = team1.head_to_head[team2.id]
        assert "W" in h2h
        assert "D" in h2h
        assert "L" in h2h
        
        # Total matches should be consistent
        total_matches = h2h["W"] + h2h["D"] + h2h["L"]
        assert total_matches > 0


@pytest.mark.asyncio
async def test_head_to_head_symmetry(orchestrator):
    """Test that head-to-head records are symmetric (team1 vs team2 = team2 vs team1)."""
    # Simulate matches
    for _ in range(5):
        await orchestrator.advance_simulation()
    
    world = orchestrator.world
    teams = list(world.teams.values())
    
    # Check symmetry for any pair that has played
    for team1 in teams:
        for opponent_id, h2h in team1.head_to_head.items():
            team2 = world.get_team_by_id(opponent_id)
            if team2 and team1.id in team2.head_to_head:
                team1_vs_team2 = team1.head_to_head[opponent_id]
                team2_vs_team1 = team2.head_to_head[team1.id]
                
                # team1's wins = team2's losses
                assert team1_vs_team2["W"] == team2_vs_team1["L"]
                # team1's losses = team2's wins
                assert team1_vs_team2["L"] == team2_vs_team1["W"]
                # Draws should be equal
                assert team1_vs_team2["D"] == team2_vs_team1["D"]


@pytest.mark.asyncio
async def test_free_kick_commentary(orchestrator):
    """Test that free kicks are included in match commentary."""
    # Simulate matches
    for _ in range(5):
        await orchestrator.advance_simulation()
    
    all_events = orchestrator.event_store.get_events()
    free_kicks = [e for e in all_events if isinstance(e, FreeKick)]
    
    if len(free_kicks) > 0:
        # Check that commentary exists and mentions free kicks
        match_ended_events = [e for e in all_events if isinstance(e, MatchEnded)]
        
        free_kick_in_commentary = False
        for match_ended in match_ended_events:
            if match_ended.commentary:
                for comment in match_ended.commentary:
                    if "free kick" in comment.lower():
                        free_kick_in_commentary = True
                        break
            if free_kick_in_commentary:
                break
        
        assert free_kick_in_commentary, "Free kicks should appear in match commentary"


@pytest.mark.asyncio
async def test_determinism_with_new_features(orchestrator):
    """Test that all new features maintain deterministic behavior."""
    # Create two orchestrators with same seed
    orch1 = GameOrchestrator()
    orch1.initialize_world()
    
    orch2 = GameOrchestrator()
    orch2.initialize_world()
    
    # Simulate with same seed
    await orch1.advance_simulation()
    await orch2.advance_simulation()
    
    events1 = orch1.event_store.get_events()
    events2 = orch2.event_store.get_events()
    
    # Should have same number of events
    assert len(events1) == len(events2)
    
    # Check free kicks are deterministic
    fks1 = [e for e in events1 if isinstance(e, FreeKick)]
    fks2 = [e for e in events2 if isinstance(e, FreeKick)]
    
    assert len(fks1) == len(fks2)
    
    # Check player ratings are deterministic
    matches1 = [e for e in events1 if isinstance(e, MatchEnded)]
    matches2 = [e for e in events2 if isinstance(e, MatchEnded)]
    
    for m1, m2 in zip(matches1, matches2):
        if m1.player_ratings and m2.player_ratings:
            assert m1.player_ratings == m2.player_ratings
