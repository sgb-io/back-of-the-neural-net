#!/usr/bin/env python3
"""
Regression test for Issue #56: News 'recent reports' displays fictitious match reports when first launching game.

This test ensures that no match reports are generated or displayed before any matches have been simulated.
"""

import pytest
from src.neuralnet.orchestrator import GameOrchestrator
from src.neuralnet.events import EventStore
from src.neuralnet.llm import MockLLMProvider
from src.neuralnet.llm_mcp import ToolsLLMProvider
from src.neuralnet.game_tools import GameStateTools


class TestIssue56Regression:
    """Regression tests for Issue #56 to prevent fictitious match reports on game launch."""

    @pytest.mark.asyncio
    async def test_no_media_stories_on_fresh_world_initialization(self):
        """Test that no MediaStoryPublished events exist immediately after world initialization."""
        # Create fresh orchestrator with in-memory storage
        orchestrator = GameOrchestrator(EventStore(":memory:"))
        orchestrator.initialize_world()
        
        # Check that no MediaStoryPublished events exist in a fresh world
        all_events = orchestrator.event_store.get_events()
        media_events = [e for e in all_events if e.event_type == "MediaStoryPublished"]
        
        assert len(media_events) == 0, f"Found {len(media_events)} unexpected media stories on fresh world initialization"
        
        # Verify we have expected initialization events but no media
        event_types = [e.event_type for e in all_events]
        assert "WorldInitialized" in event_types, "World should have WorldInitialized event"
        assert "MatchScheduled" in event_types, "World should have MatchScheduled events for fixtures"
        assert "MediaStoryPublished" not in event_types, "World should NOT have MediaStoryPublished events before simulation"

    @pytest.mark.asyncio
    async def test_news_api_returns_empty_reports_before_simulation(self):
        """Test that the news API returns empty recent_reports before any matches are simulated."""
        # Create fresh orchestrator
        orchestrator = GameOrchestrator(EventStore(":memory:"))
        orchestrator.initialize_world()
        
        # Get recent match reports (simulating the /api/news endpoint behavior)
        all_events = orchestrator.event_store.get_events()
        media_events = [e for e in all_events if e.event_type == "MediaStoryPublished"]
        
        # Should be empty - no reports before simulation
        assert len(media_events) == 0, "News API should return empty recent_reports before simulation"
        
        # Verify fixtures exist but no completed matches
        fixtures = orchestrator.get_current_matchday_fixtures()
        completed_matches = orchestrator.get_completed_matches()
        
        assert len(fixtures) > 0, "Should have upcoming fixtures"
        assert len(completed_matches) == 0, "Should have no completed matches before simulation"

    @pytest.mark.asyncio
    async def test_mock_llm_provider_prevents_reports_for_unfinished_matches(self):
        """Test that MockLLMProvider never generates reports for matches without MatchEnded event."""
        mock_provider = MockLLMProvider()
        
        # Create mock events for an unfinished match (no MatchEnded event)
        unfinished_match_events = [
            type('MockEvent', (), {
                'event_type': 'KickOff',
                'match_id': 'test_match',
                'home_score': 0,
                'away_score': 0
            })(),
            type('MockEvent', (), {
                'event_type': 'Goal',
                'match_id': 'test_match',
                'home_score': 1,
                'away_score': 0,
                'scorer': 'Test Player',
                'minute': 45
            })()
        ]
        
        # Create minimal world for testing
        from src.neuralnet.data import create_sample_world
        world = create_sample_world()
        
        # Should return no reports for unfinished match regardless of importance
        for importance in ["derby", "title_race", "relegation", "high"]:
            reports = await mock_provider.generate_match_reports(
                unfinished_match_events, world, importance
            )
            assert len(reports) == 0, f"MockLLMProvider should not generate reports for unfinished {importance} matches"

    @pytest.mark.asyncio
    async def test_tools_llm_provider_prevents_reports_for_unfinished_matches(self):
        """Test that ToolsLLMProvider never generates reports for matches without MatchEnded event."""
        # Create minimal world and tools
        from src.neuralnet.data import create_sample_world
        world = create_sample_world()
        game_tools = GameStateTools(world)
        tools_provider = ToolsLLMProvider(game_tools)
        
        # Create mock events for an unfinished match (no MatchEnded event)
        unfinished_match_events = [
            type('MockEvent', (), {
                'event_type': 'KickOff',
                'match_id': 'test_match',
                'home_score': 0,
                'away_score': 0
            })(),
            type('MockEvent', (), {
                'event_type': 'Goal',
                'match_id': 'test_match',
                'home_score': 1,
                'away_score': 0,
                'scorer': 'Test Player',
                'minute': 45
            })()
        ]
        
        # Should return no reports for unfinished match regardless of importance
        for importance in ["derby", "title_race", "relegation", "high"]:
            reports = await tools_provider.generate_match_reports(
                unfinished_match_events, world, importance
            )
            assert len(reports) == 0, f"ToolsLLMProvider should not generate reports for unfinished {importance} matches"

    @pytest.mark.asyncio
    async def test_reports_only_generated_after_complete_simulation(self):
        """Test that match reports are only generated after a full match simulation with MatchEnded event."""
        # Create fresh orchestrator
        orchestrator = GameOrchestrator(EventStore(":memory:"))
        orchestrator.initialize_world()
        
        # Verify no reports before simulation
        all_events_before = orchestrator.event_store.get_events()
        media_events_before = [e for e in all_events_before if e.event_type == "MediaStoryPublished"]
        assert len(media_events_before) == 0, "Should have no media events before simulation"
        
        # Simulate one matchday (this should generate MatchEnded events and possibly media reports)
        result = await orchestrator.advance_simulation()
        
        # Verify matches were played
        assert result["matches_played"] > 0, "Simulation should have played matches"
        
        # Check events after simulation
        all_events_after = orchestrator.event_store.get_events()
        media_events_after = [e for e in all_events_after if e.event_type == "MediaStoryPublished"]
        match_ended_events = [e for e in all_events_after if e.event_type == "MatchEnded"]
        
        # Should have MatchEnded events
        assert len(match_ended_events) > 0, "Should have MatchEnded events after simulation"
        
        # Media events should only exist if matches were actually completed
        # (Reports may or may not be generated depending on match importance, but if they exist, 
        # they should only be for completed matches)
        if len(media_events_after) > 0:
            # If reports exist, verify they're legitimate (for completed matches)
            # This validates the fix is working correctly
            assert len(match_ended_events) >= len(media_events_after), \
                "Should not have more media reports than completed matches"

    @pytest.mark.asyncio 
    async def test_multiple_world_reinitializations_no_phantom_reports(self):
        """Test that reinitializing the world multiple times doesn't create phantom reports."""
        orchestrator = GameOrchestrator(EventStore(":memory:"))
        
        # Initialize and check multiple times
        for i in range(3):
            orchestrator.initialize_world()
            
            all_events = orchestrator.event_store.get_events()
            media_events = [e for e in all_events if e.event_type == "MediaStoryPublished"]
            
            assert len(media_events) == 0, f"Initialization #{i+1} should not create media events"
            
            # Reset for next iteration
            orchestrator.is_initialized = False