"""Tests for player season statistics fix (Issue #60)."""

import pytest
from neuralnet.orchestrator import GameOrchestrator
from neuralnet.events import EventStore
from neuralnet.server import calculate_player_season_stats
import neuralnet.server as server_module


class TestPlayerStatsFix:
    """Test that player statistics are only based on simulated matches."""

    def setup_method(self):
        """Set up test environment."""
        self.orchestrator = GameOrchestrator(EventStore(":memory:"))
        self.orchestrator.initialize_world()
        server_module.orchestrator = self.orchestrator
        
        # Get a test player
        self.first_team = list(self.orchestrator.world.teams.values())[0]
        self.test_player = self.first_team.players[0]

    def teardown_method(self):
        """Clean up test environment."""
        server_module.orchestrator = None

    def test_no_stats_before_simulation(self):
        """Test that player has no stats before any matches are simulated."""
        stats = calculate_player_season_stats(self.test_player.name)
        
        expected = {
            "goals": 0,
            "assists": 0,
            "yellow_cards": 0,
            "red_cards": 0,
            "matches_played": 0,
            "minutes_played": 0
        }
        
        assert stats == expected

    def test_non_existent_player(self):
        """Test that non-existent player returns empty stats."""
        stats = calculate_player_season_stats("Non Existent Player")
        
        expected = {
            "goals": 0,
            "assists": 0,
            "yellow_cards": 0,
            "red_cards": 0,
            "matches_played": 0,
            "minutes_played": 0
        }
        
        assert stats == expected

    def test_no_orchestrator(self):
        """Test that function handles missing orchestrator gracefully."""
        server_module.orchestrator = None
        
        stats = calculate_player_season_stats(self.test_player.name)
        
        expected = {
            "goals": 0,
            "assists": 0,
            "yellow_cards": 0,
            "red_cards": 0,
            "matches_played": 0,
            "minutes_played": 0
        }
        
        assert stats == expected

    @pytest.mark.asyncio
    async def test_stats_only_from_completed_matches(self):
        """Test that stats are only counted from matches with MatchEnded events."""
        # Simulate one matchday
        result = await self.orchestrator.advance_simulation()
        assert result["matches_played"] > 0, "Should have simulated matches"
        
        # Get player stats
        stats = calculate_player_season_stats(self.test_player.name)
        
        # Verify stats are reasonable
        assert stats["matches_played"] >= 0
        assert stats["matches_played"] <= 5, f"Too many matches played: {stats['matches_played']}"
        assert stats["minutes_played"] >= 0
        assert stats["goals"] >= 0
        assert stats["assists"] >= 0
        assert stats["yellow_cards"] >= 0
        assert stats["red_cards"] >= 0
        
        # If player played matches, minutes should be positive
        if stats["matches_played"] > 0:
            assert stats["minutes_played"] > 0

    @pytest.mark.asyncio
    async def test_stats_only_for_players_team(self):
        """Test that stats are only counted for the player's actual team."""
        # Simulate matches
        await self.orchestrator.advance_simulation()
        
        # Get player stats
        stats = calculate_player_season_stats(self.test_player.name)
        
        # Count how many teams have a player with the same name
        teams_with_same_name = 0
        for team in self.orchestrator.world.teams.values():
            if any(p.name == self.test_player.name for p in team.players):
                teams_with_same_name += 1
        
        # Even if there are duplicate names, stats should only reflect
        # matches for the first team found (the player's "actual" team)
        # This should be reasonable, not inflated by duplicates
        assert stats["matches_played"] <= 5, (
            f"Matches played ({stats['matches_played']}) seems inflated. "
            f"Player appears in {teams_with_same_name} teams."
        )

    @pytest.mark.asyncio
    async def test_stats_accumulate_across_simulations(self):
        """Test that stats accumulate correctly across multiple simulations."""
        # First simulation
        await self.orchestrator.advance_simulation()
        stats_1 = calculate_player_season_stats(self.test_player.name)
        
        # Second simulation
        await self.orchestrator.advance_simulation()
        stats_2 = calculate_player_season_stats(self.test_player.name)
        
        # Stats should increase or stay the same (never decrease)
        assert stats_2["matches_played"] >= stats_1["matches_played"]
        assert stats_2["minutes_played"] >= stats_1["minutes_played"]
        assert stats_2["goals"] >= stats_1["goals"]
        assert stats_2["assists"] >= stats_1["assists"]
        assert stats_2["yellow_cards"] >= stats_1["yellow_cards"]
        assert stats_2["red_cards"] >= stats_1["red_cards"]

    @pytest.mark.asyncio
    async def test_matches_played_equals_team_involvement(self):
        """Test that matches_played equals the number of completed matches the team was involved in."""
        # Simulate one matchday
        await self.orchestrator.advance_simulation()
        
        # Count completed matches involving the player's team
        all_events = self.orchestrator.event_store.get_events()
        match_ended_events = [e for e in all_events if e.event_type == "MatchEnded"]
        
        team_matches = 0
        for event in match_ended_events:
            match = self.orchestrator.world.get_match_by_id(event.match_id)
            if match and (match.home_team_id == self.first_team.id or match.away_team_id == self.first_team.id):
                team_matches += 1
        
        # Get player stats
        stats = calculate_player_season_stats(self.test_player.name)
        
        # Player's matches_played should equal team's match involvement
        assert stats["matches_played"] == team_matches, (
            f"Player matches_played ({stats['matches_played']}) != "
            f"team matches ({team_matches})"
        )