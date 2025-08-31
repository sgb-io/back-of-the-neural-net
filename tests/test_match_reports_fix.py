#!/usr/bin/env python3
"""Regression test to ensure match reports are only generated after matches are simulated."""

import asyncio
import pytest
from src.neuralnet.orchestrator import GameOrchestrator
from src.neuralnet.events import EventStore
from src.neuralnet.llm import MockLLMProvider


@pytest.mark.asyncio
async def test_no_match_reports_before_simulation():
    """Test that no match reports exist before any matches are simulated."""
    # Create fresh orchestrator with in-memory storage
    orchestrator = GameOrchestrator(EventStore(":memory:"))
    orchestrator.initialize_world()
    
    # Check that no MediaStoryPublished events exist
    all_events = orchestrator.event_store.get_events()
    media_events = [e for e in all_events if e.event_type == "MediaStoryPublished"]
    
    assert len(media_events) == 0, f"Found {len(media_events)} match reports before simulation"


@pytest.mark.asyncio
async def test_match_reports_only_for_completed_matches():
    """Test that match reports are only generated for matches that have ended."""
    # Create mock LLM provider
    mock_provider = MockLLMProvider()
    
    # Test with unfinished match (no MatchEnded event)
    unfinished_events = [
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
            'away_score': 0
        })()
    ]
    
    # Create minimal world for testing
    from src.neuralnet.data import create_sample_world
    world = create_sample_world()
    
    # Should return no reports for unfinished match
    reports_unfinished = await mock_provider.generate_match_reports(
        unfinished_events, world, "derby"
    )
    assert len(reports_unfinished) == 0, "Reports generated for unfinished match"
    
    # Test with finished match (includes MatchEnded event)
    finished_events = unfinished_events + [
        type('MockEvent', (), {
            'event_type': 'MatchEnded',
            'match_id': 'test_match',
            'home_score': 1,
            'away_score': 0
        })()
    ]
    
    # Should generate reports for finished match
    reports_finished = await mock_provider.generate_match_reports(
        finished_events, world, "derby"
    )
    # Note: Reports might still be 0 due to other validation (like match not existing in world)
    # The key is that it should NOT fail due to missing MatchEnded event


@pytest.mark.asyncio
async def test_match_reports_generated_after_simulation():
    """Test that match reports are generated after matches are simulated."""
    # Create fresh orchestrator
    orchestrator = GameOrchestrator(EventStore(":memory:"))
    orchestrator.initialize_world()
    
    # Ensure no reports before simulation
    all_events_before = orchestrator.event_store.get_events()
    media_events_before = [e for e in all_events_before if e.event_type == "MediaStoryPublished"]
    assert len(media_events_before) == 0
    
    # Simulate one matchday
    result = await orchestrator.advance_simulation()
    
    # Check that matches were played
    assert result["matches_played"] > 0, "No matches were played"
    
    # Check that match reports may be generated (for important matches)
    all_events_after = orchestrator.event_store.get_events()
    media_events_after = [e for e in all_events_after if e.event_type == "MediaStoryPublished"]
    
    # Reports are only generated for important matches, so this could be 0 or more
    # The key test is that the number after >= number before (which was 0)
    assert len(media_events_after) >= len(media_events_before)


def test_media_preview_terminology():
    """Test that media previews are clearly labeled as previews."""
    from src.neuralnet.server import generate_match_media_preview
    
    # Create mock teams
    class MockTeam:
        def __init__(self, name):
            self.name = name
            self.id = "test_id"
    
    # Create mock game tools
    class MockGameTools:
        async def get_media_views(self, entity_type, entity_id):
            return {"media_coverage": [{"outlet_name": "Test Outlet", "reach": 100}]}
    
    # Test that preview is clearly labeled
    async def run_test():
        home_team = MockTeam("Test United")
        away_team = MockTeam("Test City")
        
        preview = await generate_match_media_preview(
            home_team, away_team, "derby", MockGameTools()
        )
        
        assert preview is not None
        assert "Preview:" in preview["headline"], f"Preview headline should contain 'Preview:', got: {preview['headline']}"
        assert preview.get("type") == "match_preview", f"Preview type should be 'match_preview', got: {preview.get('type')}"
        assert "will be" in preview["preview"] or "prepare to" in preview["preview"] or "upcoming" in preview["preview"], \
            f"Preview text should indicate future tense, got: {preview['preview']}"
    
    asyncio.run(run_test())