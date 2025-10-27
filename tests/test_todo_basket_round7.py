"""Tests for TODO basket round 7 features.

This test suite covers:
1. Pitch conditions (6 types)
2. Team captains and vice-captains
3. Average player ratings tracking
4. Season records infrastructure
5. Enhanced form guide
"""

import pytest
from src.neuralnet.data import create_sample_world
from src.neuralnet.entities import (
    GameWorld,
    PitchCondition,
    Position,
    Team,
    Match,
    League,
)
from src.neuralnet.orchestrator import GameOrchestrator
from src.neuralnet.events import EventStore


class TestPitchConditions:
    """Test pitch condition tracking for matches."""

    def test_pitch_condition_enum_exists(self):
        """Test that PitchCondition enum has all expected values."""
        assert hasattr(PitchCondition, "EXCELLENT")
        assert hasattr(PitchCondition, "GOOD")
        assert hasattr(PitchCondition, "AVERAGE")
        assert hasattr(PitchCondition, "WORN")
        assert hasattr(PitchCondition, "POOR")
        assert hasattr(PitchCondition, "WATERLOGGED")
        
        # Verify there are 6 conditions
        assert len(PitchCondition) == 6

    def test_match_has_pitch_condition(self):
        """Test that matches have pitch_condition field."""
        match = Match(
            id="test_match",
            home_team_id="team1",
            away_team_id="team2",
            league="premier_fantasy",
            matchday=1,
            season=2025
        )
        
        # Should have default pitch condition
        assert hasattr(match, "pitch_condition")
        assert match.pitch_condition == PitchCondition.GOOD

    def test_pitch_condition_generated_for_matches(self):
        """Test that pitch conditions are generated during fixture scheduling."""
        world = create_sample_world()
        event_store = EventStore(":memory:")
        orchestrator = GameOrchestrator(event_store=event_store)
        orchestrator.world = world
        
        # Initialize world
        orchestrator.initialize_world()
        
        # Check that matches have pitch conditions
        matches = list(orchestrator.world.matches.values())
        assert len(matches) > 0
        
        for match in matches:
            assert hasattr(match, "pitch_condition")
            assert isinstance(match.pitch_condition, PitchCondition)

    def test_pitch_condition_variety(self):
        """Test that different matches get different pitch conditions."""
        world = create_sample_world()
        event_store = EventStore(":memory:")
        orchestrator = GameOrchestrator(event_store=event_store)
        orchestrator.world = world
        
        orchestrator.initialize_world()
        
        matches = list(orchestrator.world.matches.values())
        pitch_conditions = [m.pitch_condition for m in matches]
        
        # Should have at least 2 different conditions
        unique_conditions = set(pitch_conditions)
        assert len(unique_conditions) >= 2


class TestTeamCaptains:
    """Test captain and vice-captain functionality."""

    def test_team_has_captain_fields(self):
        """Test that teams have captain_id and vice_captain_id fields."""
        team = Team(
            id="test_team",
            name="Test United",
            league="premier_fantasy"
        )
        
        assert hasattr(team, "captain_id")
        assert hasattr(team, "vice_captain_id")
        # Default should be None
        assert team.captain_id is None
        assert team.vice_captain_id is None

    def test_captains_assigned_during_team_creation(self):
        """Test that captains are assigned when teams are created."""
        world = create_sample_world()
        
        for team in world.teams.values():
            # Teams should have captains assigned
            assert team.captain_id is not None
            
            # Captain should be a valid player ID
            captain = world.get_player_by_id(team.captain_id)
            assert captain is not None
            assert captain.id in [p.id for p in team.players]

    def test_vice_captain_assigned(self):
        """Test that vice-captains are assigned and are different from captains."""
        world = create_sample_world()
        
        for team in world.teams.values():
            # Most teams should have vice-captains
            if team.vice_captain_id:
                assert team.vice_captain_id != team.captain_id
                
                vice_captain = world.get_player_by_id(team.vice_captain_id)
                assert vice_captain is not None
                assert vice_captain.id in [p.id for p in team.players]

    def test_captains_are_experienced_players(self):
        """Test that captains tend to be more experienced/older players."""
        world = create_sample_world()
        
        for team in world.teams.values():
            if team.captain_id:
                captain = world.get_player_by_id(team.captain_id)
                # Captains should generally be 23 or older (though not guaranteed)
                # Check that captain is in midfield or defense positions typically
                assert captain.position in [
                    Position.CM, Position.CB, Position.CAM,
                    Position.LB, Position.RB, Position.LM, Position.RM
                ] or captain.age >= 25


class TestPlayerAverageRatings:
    """Test average rating calculation for players."""

    def test_player_has_match_ratings_field(self):
        """Test that players have match_ratings field for tracking."""
        world = create_sample_world()
        
        player = next(iter(world.players.values()))
        assert hasattr(player, "match_ratings")
        assert isinstance(player.match_ratings, list)

    def test_player_average_rating_property(self):
        """Test that players have average_rating property."""
        world = create_sample_world()
        
        player = next(iter(world.players.values()))
        assert hasattr(player, "average_rating")
        
        # Initially should be 0.0 (no ratings yet)
        assert player.average_rating == 0.0

    def test_average_rating_calculation(self):
        """Test that average rating is calculated correctly."""
        world = create_sample_world()
        player = next(iter(world.players.values()))
        
        # Add some ratings
        player.match_ratings = [6.5, 7.0, 7.5, 8.0]
        
        expected_avg = (6.5 + 7.0 + 7.5 + 8.0) / 4
        assert player.average_rating == expected_avg

    @pytest.mark.asyncio
    async def test_ratings_updated_after_match(self):
        """Test that player ratings are updated after matches."""
        event_store = EventStore(":memory:")
        orchestrator = GameOrchestrator(event_store=event_store)
        
        orchestrator.initialize_world()
        
        # Play a matchday
        await orchestrator.advance_simulation()
        
        # Check that some players have ratings
        players_with_ratings = [
            p for p in orchestrator.world.players.values()
            if len(p.match_ratings) > 0
        ]
        
        # At least some players should have played and gotten ratings
        assert len(players_with_ratings) > 0
        
        # Ratings should be in valid range (1-10)
        for player in players_with_ratings:
            for rating in player.match_ratings:
                assert 1.0 <= rating <= 10.0


class TestSeasonRecords:
    """Test season records infrastructure."""

    def test_league_has_season_records_field(self):
        """Test that leagues have season_records field."""
        league = League(
            id="test_league",
            name="Test League",
            season=2025
        )
        
        assert hasattr(league, "season_records")
        assert isinstance(league.season_records, dict)

    def test_season_records_structure(self):
        """Test that season_records can store various records."""
        world = create_sample_world()
        
        league = next(iter(world.leagues.values()))
        
        # Should be able to add records
        league.season_records[2025] = {
            "most_goals": {"player_id": "p1", "goals": 30, "team_id": "t1"},
            "best_defense": {"team_id": "t1", "goals_conceded": 15},
            "most_clean_sheets": {"team_id": "t2", "clean_sheets": 18}
        }
        
        assert league.season_records[2025]["most_goals"]["goals"] == 30


class TestFormGuide:
    """Test form guide tracking."""

    def test_team_has_recent_form_field(self):
        """Test that teams have recent_form field."""
        team = Team(
            id="test_team",
            name="Test United",
            league="premier_fantasy"
        )
        
        assert hasattr(team, "recent_form")
        assert isinstance(team.recent_form, list)

    @pytest.mark.asyncio
    async def test_form_guide_tracks_last_5_matches(self):
        """Test that form guide maintains last 5 match results."""
        world = create_sample_world()
        event_store = EventStore(":memory:")
        orchestrator = GameOrchestrator(event_store=event_store)
        orchestrator.world = world
        
        orchestrator.initialize_world()
        
        # Play multiple matchdays
        for _ in range(6):
            await orchestrator.advance_simulation()
        
        # Check teams have form guides
        for team in world.teams.values():
            # Should have up to 5 results
            assert len(team.recent_form) <= 5
            
            # All results should be W, D, or L
            for result in team.recent_form:
                assert result in ["W", "D", "L"]

    @pytest.mark.asyncio
    async def test_form_guide_only_keeps_last_5(self):
        """Test that form guide doesn't grow beyond 5 matches."""
        world = create_sample_world()
        event_store = EventStore(":memory:")
        orchestrator = GameOrchestrator(event_store=event_store)
        orchestrator.world = world
        
        orchestrator.initialize_world()
        
        # Play many matchdays
        for _ in range(10):
            await orchestrator.advance_simulation()
        
        # All teams should have exactly 5 results
        for team in world.teams.values():
            if team.matches_played >= 5:
                assert len(team.recent_form) == 5


class TestIntegrationAndCompatibility:
    """Test integration and backward compatibility."""

    @pytest.mark.asyncio
    async def test_all_features_work_together(self):
        """Test that all new features work together in a full simulation."""
        event_store = EventStore(":memory:")
        orchestrator = GameOrchestrator(event_store=event_store)
        
        orchestrator.initialize_world()
        
        # Play several matchdays
        for _ in range(3):
            await orchestrator.advance_simulation()
        
        # Verify all features are working
        # 1. Pitch conditions
        matches = [m for m in orchestrator.world.matches.values() if m.finished]
        assert all(hasattr(m, "pitch_condition") for m in matches)
        
        # 2. Captains
        assert all(team.captain_id is not None for team in orchestrator.world.teams.values())
        
        # 3. Player ratings
        players_with_ratings = [
            p for p in orchestrator.world.players.values()
            if len(p.match_ratings) > 0
        ]
        assert len(players_with_ratings) > 0
        
        # 4. Form guides
        assert all(
            len(team.recent_form) > 0
            for team in orchestrator.world.teams.values()
            if team.matches_played > 0
        )

    @pytest.mark.asyncio
    async def test_determinism_with_new_features(self):
        """Test that new features maintain determinism."""
        # Create two identical worlds
        event_store1 = EventStore(":memory:")
        orchestrator1 = GameOrchestrator(event_store=event_store1)
        world1 = create_sample_world()
        orchestrator1.world = world1
        orchestrator1.initialize_world()
        
        event_store2 = EventStore(":memory:")
        orchestrator2 = GameOrchestrator(event_store=event_store2)
        world2 = create_sample_world()
        orchestrator2.world = world2
        orchestrator2.initialize_world()
        
        # Play same matchday
        await orchestrator1.advance_simulation()
        await orchestrator2.advance_simulation()
        
        # Pitch conditions should be identical
        matches1 = sorted(
            [m for m in world1.matches.values() if m.matchday == 1],
            key=lambda m: m.id
        )
        matches2 = sorted(
            [m for m in world2.matches.values() if m.matchday == 1],
            key=lambda m: m.id
        )
        
        for m1, m2 in zip(matches1, matches2):
            assert m1.pitch_condition == m2.pitch_condition
        
        # Captains should have consistent properties (same player chosen based on position and rating)
        for team1 in world1.teams.values():
            team2 = world2.get_team_by_id(team1.id)
            
            # Both teams should have captains
            assert team1.captain_id is not None
            assert team2.captain_id is not None
            
            # Get the captain players
            captain1 = world1.get_player_by_id(team1.captain_id)
            captain2 = world2.get_player_by_id(team2.captain_id)
            
            # Captains should have same name, position, and attributes (deterministic selection)
            assert captain1.name == captain2.name
            assert captain1.position == captain2.position

    def test_backward_compatibility(self):
        """Test that old matches without pitch conditions still work."""
        # Create a match without pitch condition explicitly set
        match = Match(
            id="old_match",
            home_team_id="team1",
            away_team_id="team2",
            league="premier_fantasy",
            matchday=1,
            season=2024
        )
        
        # Should have default pitch condition
        assert match.pitch_condition == PitchCondition.GOOD
        
        # Should be serializable
        match_dict = match.model_dump()
        assert "pitch_condition" in match_dict
