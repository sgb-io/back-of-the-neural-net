#!/usr/bin/env python3
"""Test script to reproduce the match reports issue."""

import asyncio
from src.neuralnet.orchestrator import GameOrchestrator
from src.neuralnet.events import EventStore

async def test_match_reports_before_simulation():
    """Test that no match reports exist before any matches are simulated."""
    print("🔍 Testing match reports issue...")
    
    # Create fresh orchestrator
    orchestrator = GameOrchestrator(EventStore(":memory:"))
    orchestrator.initialize_world()
    
    print(f"✓ World initialized with {len(orchestrator.world.teams)} teams")
    
    # Check for any MediaStoryPublished events before simulation
    all_events = orchestrator.event_store.get_events()
    media_events = [e for e in all_events if e.event_type == "MediaStoryPublished"]
    
    print(f"📊 Events in store before simulation: {len(all_events)}")
    print(f"📰 Media story events before simulation: {len(media_events)}")
    
    if media_events:
        print("❌ ISSUE FOUND: Media stories exist before any matches were simulated!")
        for event in media_events:
            print(f"   - {event.headline} (Type: {event.story_type})")
    else:
        print("✓ No media stories before simulation (as expected)")
    
    # Check current fixtures
    fixtures = orchestrator.get_current_matchday_fixtures()
    print(f"📅 Current matchday fixtures: {len(fixtures)}")
    
    completed_matches = orchestrator.get_completed_matches()
    print(f"⚽ Completed matches: {len(completed_matches)}")
    
    # Now simulate one matchday
    print("\n🎮 Simulating one matchday...")
    result = await orchestrator.advance_simulation()
    
    print(f"✓ Matchday completed: {result['matches_played']} matches played")
    
    # Check for media events after simulation
    all_events_after = orchestrator.event_store.get_events()
    media_events_after = [e for e in all_events_after if e.event_type == "MediaStoryPublished"]
    
    print(f"📊 Events after simulation: {len(all_events_after)}")
    print(f"📰 Media story events after simulation: {len(media_events_after)}")
    
    if media_events_after:
        print("✓ Media stories exist after simulation (expected for important matches)")
        for event in media_events_after:
            print(f"   - {event.headline} (Type: {event.story_type})")
    
    return len(media_events) == 0  # Should be True if no reports before simulation

if __name__ == "__main__":
    success = asyncio.run(test_match_reports_before_simulation())
    print(f"\n{'✅ TEST PASSED' if success else '❌ TEST FAILED'}")